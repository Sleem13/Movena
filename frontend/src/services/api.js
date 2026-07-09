import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

export async function analyzeSquatVideo(videoFile) {
  const formData = new FormData();
  formData.append("video", videoFile);

  const response = await api.post("/api/v1/analyze/squat", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}

export default api;
