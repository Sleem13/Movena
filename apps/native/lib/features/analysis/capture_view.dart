import 'dart:async';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import '../../core/preferences.dart';

/// Movement recordings deliberately disable microphone capture.
class CaptureView extends StatefulWidget {
  final Preferences preferences;
  const CaptureView({super.key, required this.preferences});
  @override
  State<CaptureView> createState() => _CaptureViewState();
}

class _CaptureViewState extends State<CaptureView> with WidgetsBindingObserver {
  CameraController? camera;
  String? error;
  bool working = false;
  Timer? limit;
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    initialize();
  }

  Future<void> initialize() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) throw Exception(widget.preferences.t('unavailable'));
      final lens =
          cameras
              .where((c) => c.lensDirection == CameraLensDirection.back)
              .firstOrNull ??
          cameras.first;
      final controller = CameraController(
        lens,
        ResolutionPreset.medium,
        enableAudio: false,
      );
      await controller.initialize();
      if (!mounted) {
        await controller.dispose();
        return;
      }
      setState(() {
        camera = controller;
        error = null;
      });
    } catch (e) {
      if (mounted) {
        setState(() {
          error = e.toString();
        });
      }
    }
  }

  Future<void> toggle() async {
    if (working || camera == null) return;
    setState(() {
      working = true;
    });
    try {
      if (camera!.value.isRecordingVideo) {
        limit?.cancel();
        final file = await camera!.stopVideoRecording();
        if (mounted) Navigator.pop(context, file);
      } else {
        await camera!.startVideoRecording();
        limit = Timer(const Duration(seconds: 60), toggle);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          error = e.toString();
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          working = false;
        });
      }
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.inactive) {
      limit?.cancel();
      final controller = camera;
      camera = null;
      controller?.dispose();
    } else if (state == AppLifecycleState.resumed && camera == null) {
      initialize();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    limit?.cancel();
    camera?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(widget.preferences.t('video'))),
    body: SafeArea(
      child: Column(
        children: [
          Expanded(
            child: error != null
                ? Center(child: Text(error!))
                : camera == null
                ? const Center(child: CircularProgressIndicator())
                : Center(child: CameraPreview(camera!)),
          ),
          Padding(
            padding: const EdgeInsets.all(24),
            child: FilledButton.icon(
              onPressed: camera == null || working ? null : toggle,
              icon: Icon(
                camera?.value.isRecordingVideo == true
                    ? Icons.stop
                    : Icons.fiber_manual_record,
              ),
              label: Text(
                widget.preferences.t(
                  camera?.value.isRecordingVideo == true ? 'done' : 'start',
                ),
              ),
            ),
          ),
        ],
      ),
    ),
  );
}
