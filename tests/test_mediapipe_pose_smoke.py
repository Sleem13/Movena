"""Dependency smoke test for the MediaPipe API used by the application."""


def test_mediapipe_pose_initializes():
    import mediapipe as mp

    pose = mp.solutions.pose.Pose()
    try:
        assert pose is not None
    finally:
        pose.close()
