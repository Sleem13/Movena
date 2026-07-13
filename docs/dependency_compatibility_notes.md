# Dependency Compatibility Notes

## Validated Python environment

The PhysioVision AI core application is validated with Python 3.12.10 in a project-local `.venv`.

## MediaPipe and protobuf

The current pose pipeline uses the legacy `mp.solutions.pose.Pose` API. That API is available in `mediapipe==0.10.21` but was removed from MediaPipe releases starting with 0.10.30. MediaPipe 0.10.35 therefore cannot be used without migrating application logic to the newer Tasks Pose Landmarker API.

The compatible core pins are:

```text
mediapipe==0.10.21
protobuf==4.25.3
```

The protobuf pin prevents incompatible generated-protobuf/runtime combinations, including errors such as:

```text
ImportError: cannot import name 'runtime_version' from 'google.protobuf'
```

After dependency changes, validate both versions and initialize the pose runtime:

```powershell
python -c "import mediapipe as mp; import google.protobuf; print(mp.__version__); print(google.protobuf.__version__); pose = mp.solutions.pose.Pose(); pose.close()"
python -m pip check
python -m pytest
```

## TensorFlow exclusion

TensorFlow, Keras, and TensorBoard are excluded from the core requirements. The current application uses MediaPipe for pose estimation, explicit biomechanics rules for its primary analysis, and scikit-learn for an optional experimental second opinion; it does not require TensorFlow.

TensorFlow 2.21 requires a newer protobuf line than this legacy MediaPipe environment. Installing both into the core `.venv` can upgrade protobuf and break the current pose pipeline.

To reset an environment that contains the conflicting stack:

```powershell
python -m pip uninstall -y tensorflow tensorflow-intel keras tensorboard
python -m pip install --upgrade --force-reinstall -r requirements-dev.txt
python -m pip check
```

## Future MoveNet evaluation

MoveNet Lightning and Thunder should be evaluated later in a separate optional virtual environment with independently pinned TensorFlow/TensorFlow Lite dependencies. Benchmark outputs can be compared offline, but the optional environment must not modify the production core lock set or silently replace the MediaPipe backend.

Migrating the production application from legacy MediaPipe Solutions to MediaPipe Tasks is a separate application change and requires pose-contract, artifact, performance, and regression testing.
