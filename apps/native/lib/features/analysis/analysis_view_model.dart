import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:uuid/uuid.dart';

import '../../core/api_client.dart';

class AnalysisViewModel extends ChangeNotifier {
  final ApiClient api;
  final String? patientId;
  String exercise;
  XFile? video;
  Map<String, dynamic>? job;
  bool uploading = false;
  String? error;
  String requestKey = const Uuid().v4();
  Timer? timer;
  http.Client? uploadClient;
  bool disposed = false;
  AnalysisViewModel(this.api, {this.exercise = '', this.patientId});
  bool get running =>
      uploading || ['queued', 'running'].contains(job?['status']);

  Future<void> restoreActive() async {
    if (job != null || uploading || patientId != null) return;
    try {
      final rows = rowsOf(await api.request('analysis-jobs'));
      final candidates = exercise.isEmpty
          ? rows
          : rows.where((row) => row['exercise_id'] == exercise).toList();
      if (candidates.isNotEmpty && !disposed) {
        job = candidates.first;
        if (exercise.isEmpty) exercise = job!['exercise_id']?.toString() ?? '';
        schedulePoll();
        update();
      }
    } catch (_) {
      // A recovery lookup must not prevent a new analysis.
    }
  }

  void update() {
    if (!disposed) notifyListeners();
  }

  void select(XFile file) {
    if (running) return;
    video = file;
    job = null;
    error = null;
    requestKey = const Uuid().v4();
    update();
  }

  void selectExercise(String value) {
    if (running) return;
    exercise = value;
    job = null;
    requestKey = const Uuid().v4();
    update();
  }

  Future<void> upload() async {
    if (video == null || exercise.isEmpty || running) return;
    if (await video!.length() > 100 * 1024 * 1024) {
      error = 'Maximum video size is 100 MB.';
      update();
      return;
    }
    if (['failed', 'cancelled'].contains(job?['status'])) {
      requestKey = const Uuid().v4();
    }
    uploading = true;
    error = null;
    update();
    final client = http.Client();
    uploadClient = client;
    try {
      final query = Uri(
        queryParameters: {
          'save_session': 'true',
          if (patientId != null) 'patient_id': patientId,
        },
      ).query;
      final request = http.MultipartRequest(
        'POST',
        api.uri('analysis-jobs/${Uri.encodeComponent(exercise)}?$query'),
      );
      request.followRedirects = false;
      final token = await api.tokens.read();
      if (token != null) request.headers['Authorization'] = 'Bearer $token';
      request.headers['Idempotency-Key'] = requestKey;
      request.files.add(
        await http.MultipartFile.fromPath('video', video!.path),
      );
      final response = await http.Response.fromStream(
        await client.send(request),
      ).timeout(const Duration(minutes: 5));
      job = objectOf(await api.decode(response));
      schedulePoll();
    } catch (e) {
      error = e.toString();
    } finally {
      client.close();
      uploadClient = null;
      uploading = false;
      update();
    }
  }

  void schedulePoll() {
    timer?.cancel();
    if (!disposed && ['queued', 'running'].contains(job?['status'])) {
      timer = Timer(const Duration(seconds: 2), poll);
    }
  }

  Future<void> poll() async {
    if (job == null || disposed) return;
    try {
      job = objectOf(
        await api.request(
          'analysis-jobs/${Uri.encodeComponent(job!['job_id'])}',
        ),
      );
      error = null;
      schedulePoll();
    } catch (e) {
      error = e.toString();
    }
    update();
  }

  Future<void> cancel() async {
    if (uploading) {
      uploadClient?.close();
      error = 'Upload interrupted. Retry to recover the submitted job.';
      update();
      return;
    }
    if (job == null) return;
    try {
      await api.request(
        'analysis-jobs/${Uri.encodeComponent(job!['job_id'])}/cancel',
        method: 'POST',
      );
      await poll();
    } catch (e) {
      error = e.toString();
      update();
    }
  }

  @override
  void dispose() {
    disposed = true;
    timer?.cancel();
    uploadClient?.close();
    super.dispose();
  }
}
