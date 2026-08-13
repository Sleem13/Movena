const MEDIAPIPE_VERSION = "0.10.35";
const WASM_URL = `https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@${MEDIAPIPE_VERSION}/wasm`;
const MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task";
const HAND_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";

let extractorPromise;

async function createPoseLandmarker(delegate) {
  const { FilesetResolver, PoseLandmarker } = await import("@mediapipe/tasks-vision");
  const vision = await FilesetResolver.forVisionTasks(WASM_URL);
  return PoseLandmarker.createFromOptions(vision, {
    baseOptions: { modelAssetPath: MODEL_URL, delegate },
    runningMode: "VIDEO",
    numPoses: 1,
    minPoseDetectionConfidence: 0.5,
    minPosePresenceConfidence: 0.5,
    minTrackingConfidence: 0.5,
    outputSegmentationMasks: false,
  });
}

async function createExtractor() {
  const { FilesetResolver, HandLandmarker } = await import("@mediapipe/tasks-vision");
  let landmarker;
  try {
    landmarker = await createPoseLandmarker("GPU");
  } catch {
    landmarker = await createPoseLandmarker("CPU");
  }
  const vision = await FilesetResolver.forVisionTasks(WASM_URL);
  const handLandmarker = await HandLandmarker.createFromOptions(vision, {
    baseOptions: { modelAssetPath: HAND_MODEL_URL, delegate: "GPU" },
    runningMode: "VIDEO",
    numHands: 2,
    minHandDetectionConfidence: 0.5,
    minHandPresenceConfidence: 0.5,
    minTrackingConfidence: 0.5,
  });

  let lastTimestamp = 0;
  return {
    estimate(videoElement) {
      const timestamp = Math.max(performance.now(), lastTimestamp + 0.001);
      lastTimestamp = timestamp;
      const result = landmarker.detectForVideo(videoElement, timestamp);
      const handResult = handLandmarker.detectForVideo(videoElement, timestamp);
      const hands = (handResult.landmarks ?? []).map((landmarks, index) => ({
        landmarks,
        handedness: handResult.handedness?.[index]?.[0]?.categoryName ?? null,
      }));
      return { landmarks: result.landmarks?.[0] ?? [], hands };
    },
    close() {
      landmarker.close();
      handLandmarker.close();
    },
  };
}

export function getLocalPoseLandmarkExtractor() {
  if (!extractorPromise) {
    extractorPromise = createExtractor().catch((error) => {
      extractorPromise = undefined;
      throw error;
    });
  }
  return extractorPromise;
}
