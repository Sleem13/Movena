import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:video_player/video_player.dart';

import '../../core/api_client.dart';
import '../../core/preferences.dart';
import '../../core/resource_view.dart';
import 'analysis_view_model.dart';
import 'capture_view.dart';

class AnalyzeView extends StatefulWidget {
  final ApiClient api;
  final Preferences preferences;
  final String exercise;
  final String? patientId;
  final bool returnResult;
  const AnalyzeView({
    super.key,
    required this.api,
    required this.preferences,
    this.exercise = '',
    this.patientId,
    this.returnResult = false,
  });
  @override
  State<AnalyzeView> createState() => _AnalyzeViewState();
}

class _AnalyzeViewState extends State<AnalyzeView> with WidgetsBindingObserver {
  late final AnalysisViewModel model;
  final picker = ImagePicker();
  VideoPlayerController? preview;
  String? mediaError;
  @override
  void initState() {
    super.initState();
    model = AnalysisViewModel(
      widget.api,
      exercise: widget.exercise,
      patientId: widget.patientId,
    );
    WidgetsBinding.instance.addObserver(this);
    model.restoreActive();
    recoverMedia();
  }

  Future<void> recoverMedia() async {
    if (!Platform.isAndroid) return;
    try {
      final lost = await picker.retrieveLostData();
      if (mounted && lost.files?.isNotEmpty == true) {
        await select(lost.files!.first);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          mediaError = e.toString();
        });
      }
    }
  }

  Future<void> select(XFile file) async {
    model.select(file);
    final old = preview;
    preview = null;
    await old?.dispose();
    final next = VideoPlayerController.file(File(file.path));
    try {
      await next.initialize();
      if (!mounted) {
        await next.dispose();
        return;
      }
      setState(() {
        preview = next;
        mediaError = null;
      });
    } catch (e) {
      await next.dispose();
      if (mounted) {
        setState(() {
          mediaError = e.toString();
        });
      }
    }
  }

  Future<void> pick(ImageSource source) async {
    try {
      final video = source == ImageSource.camera
          ? await Navigator.push<XFile>(
              context,
              MaterialPageRoute(
                builder: (_) => CaptureView(preferences: widget.preferences),
              ),
            )
          : await picker.pickVideo(source: source);
      if (video != null && mounted) await select(video);
    } catch (e) {
      if (mounted) {
        setState(() {
          mediaError = e.toString();
        });
      }
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      model.poll();
    } else {
      preview?.pause();
      model.timer?.cancel();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    model.dispose();
    preview?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.preferences;
    return Scaffold(
      appBar: AppBar(title: Text(p.t('analyze'))),
      body: SafeArea(
        child: ResourceView(
          api: widget.api,
          path: 'exercises',
          preferences: p,
          builder: (data, refresh) {
            final exercises = rowsOf(data)
                .where(
                  (v) =>
                      v['supported_in_app'] == true &&
                      v['endpoint_path'] != null,
                )
                .toList();
            return ListenableBuilder(
              listenable: model,
              builder: (context, _) => ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  Text(p.t('analyzeHint')),
                  const SizedBox(height: 24),
                  DropdownButtonFormField<String>(
                    initialValue:
                        exercises.any((e) => e['exercise_id'] == model.exercise)
                        ? model.exercise
                        : null,
                    decoration: InputDecoration(labelText: p.t('exercise')),
                    isExpanded: true,
                    items: exercises
                        .map(
                          (e) => DropdownMenuItem<String>(
                            value: e['exercise_id'],
                            child: Text(
                              p.exerciseName(e['exercise_id']),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        )
                        .toList(),
                    onChanged: model.running || widget.returnResult
                        ? null
                        : (v) => v == null ? null : model.selectExercise(v),
                  ),
                  const SizedBox(height: 20),
                  for (final exercise in exercises.where(
                    (e) => e['exercise_id'] == model.exercise,
                  )) ...[
                    Text(exercise['recommended_camera_view'] ?? ''),
                    const SizedBox(height: 8),
                    Text(exercise['safety_notes'] ?? ''),
                    const SizedBox(height: 20),
                  ],
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: model.running
                              ? null
                              : () => pick(ImageSource.camera),
                          icon: const Icon(Icons.videocam_outlined),
                          label: Text(p.t('analyze')),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: model.running
                              ? null
                              : () => pick(ImageSource.gallery),
                          icon: const Icon(Icons.video_library_outlined),
                          label: Text(p.t('video')),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  if (preview != null) ...[
                    AspectRatio(
                      aspectRatio: preview!.value.aspectRatio,
                      child: VideoPlayer(preview!),
                    ),
                    IconButton(
                      tooltip: preview!.value.isPlaying
                          ? p.t('cancel')
                          : p.t('next'),
                      icon: Icon(
                        preview!.value.isPlaying
                            ? Icons.pause
                            : Icons.play_arrow,
                      ),
                      onPressed: () => setState(() {
                        preview!.value.isPlaying
                            ? preview!.pause()
                            : preview!.play();
                      }),
                    ),
                  ],
                  if (mediaError != null) Text(mediaError!),
                  if (model.error != null) ...[
                    Text(
                      model.error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                    if (model.job != null)
                      OutlinedButton(
                        onPressed: model.poll,
                        child: Text(p.t('retry')),
                      ),
                  ],
                  const SizedBox(height: 16),
                  if (!model.running && model.job?['status'] != 'completed')
                    FilledButton(
                      onPressed: model.video == null || model.exercise.isEmpty
                          ? null
                          : model.upload,
                      child: Text(p.t('upload')),
                    ),
                  if (model.running) ...[
                    LinearProgressIndicator(
                      value: model.uploading
                          ? null
                          : (model.job?['progress'] as num? ?? 0).toDouble() /
                                100,
                    ),
                    const SizedBox(height: 16),
                    Text(p.t('loading')),
                    OutlinedButton(
                      onPressed: model.cancel,
                      child: Text(p.t('cancel')),
                    ),
                  ],
                  if (model.job?['status'] == 'cancelled')
                    Text(p.t('cancelled')),
                  if (model.job?['status'] == 'failed')
                    Text(model.job?['message'] ?? p.t('unavailable')),
                  if (model.job?['result'] is Map) ...[
                    ResultPanel(
                      result: objectOf(model.job!['result']),
                      preferences: p,
                    ),
                    if (widget.returnResult &&
                        model.job!['result']['status'] == 'success')
                      FilledButton(
                        onPressed: () => Navigator.pop(
                          context,
                          objectOf(model.job!['result']),
                        ),
                        child: Text(p.t('next')),
                      ),
                  ],
                  const SizedBox(height: 24),
                  Text(
                    p.t('analysisDisclaimer'),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

class ResultPanel extends StatelessWidget {
  final Map<String, dynamic> result;
  final Preferences preferences;
  const ResultPanel({
    super.key,
    required this.result,
    required this.preferences,
  });
  @override
  Widget build(BuildContext context) {
    final p = preferences;
    final valid = result['status'] == 'success';
    return Panel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(p.t('results'), style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 20),
          if (!valid)
            Text(
              result['message'] ??
                  p.t(
                    result['status'] == 'error' ? 'analysisError' : 'rejected',
                  ),
            ),
          if (valid) ...[
            Text(
              '${p.t('reps')}: ${result['total_reps'] ?? p.t('unavailable')}',
            ),
            Text(
              '${p.t('score')}: ${result['movement_score'] ?? p.t('unavailable')}',
            ),
          ],
          const SizedBox(height: 16),
          Text(
            '${p.t('confidence')}: ${result['analysis_confidence_level'] ?? (result['analysis_confidence'] is Map ? result['analysis_confidence']['level'] : null) ?? p.t('unavailable')}',
          ),
          const SizedBox(height: 16),
          for (final feedback in (result['feedback'] as List? ?? []))
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(feedback.toString()),
            ),
          Text(
            p.t('analysisDisclaimer'),
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}
