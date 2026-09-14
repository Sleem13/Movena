import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import '../../core/api_client.dart';
import '../../generated/client.dart';
import '../../generated/models.dart';

class PlansRepository {
  final ApiClient api;
  PlansRepository(this.api);
  CoreApi get client => CoreApi(api.request);
  Future<List<ExercisePlanDetail>> list(String id) => client.getPlans(id);
  Future<ExercisePlanDetail> create(
    String id,
    Map<String, dynamic> values,
    String key,
  ) => client.createPlan(id, ExercisePlanCreate.fromJson(values), key);
  Future<void> status(String patient, String plan, String status) async {
    await client.updatePlanStatus(
      patient,
      plan,
      ExercisePlanStatusUpdate.fromJson({'status': status}),
    );
  }
}

class PlanEditorModel extends ChangeNotifier {
  final PlansRepository repository;
  final String patientId;
  bool busy = false, done = false, _disposed = false;
  String? error, _body, _key;
  PlanEditorModel(this.repository, this.patientId);
  void notify() {
    if (!_disposed) notifyListeners();
  }

  Future<void> save(Map<String, dynamic> values) async {
    if (busy || done) return;
    final body = jsonEncode(values);
    if (body != _body) {
      _body = body;
      _key = const Uuid().v4();
    }
    busy = true;
    error = null;
    notify();
    try {
      await repository.create(patientId, values, _key!);
      done = true;
    } catch (e) {
      error = e.toString();
    } finally {
      busy = false;
      notify();
    }
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}
