export type RecognitionModel = {
  model_id: string;
  model_name: string;
  artifact_format: string;
  status: string;
  active?: boolean;
  integrity_status?: string;
};

export type RecognitionModelsResponse = {
  status: string;
  models: RecognitionModel[];
  limitations?: string[];
};

export type RecognitionPrediction = { exercise_id: string; confidence: number };

export type RecognitionResult = {
  status: string;
  suggested_exercise_id?: string;
  confidence?: number;
  confidence_threshold?: number;
  analyzer_available?: boolean;
  recognition_event_id?: string;
  top_predictions?: RecognitionPrediction[];
  error_code?: string;
  message?: string;
  details?: string[];
};
