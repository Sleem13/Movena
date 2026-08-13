import { API_BASE_URL } from "./api.js";

const TOKEN_KEY = "physiovision_access_token";

export function coachingWebSocketUrl(baseUrl = API_BASE_URL) {
  const url = new URL("/api/v1/coaching/stream", baseUrl);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
}

export function connectRealtimeCoaching(exerciseId, handlers = {}) {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) throw new Error("AUTH_REQUIRED");
  const socket = new WebSocket(coachingWebSocketUrl());
  socket.addEventListener("open", () => {
    socket.send(JSON.stringify({ type: "authenticate", token, exercise_id: exerciseId }));
  });
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    handlers.onMessage?.(message);
  });
  socket.addEventListener("error", () => handlers.onError?.(new Error("STREAM_UNAVAILABLE")));
  socket.addEventListener("close", (event) => handlers.onClose?.(event));
  return {
    sendLandmarks(payload) {
      if (socket.readyState !== WebSocket.OPEN) return false;
      socket.send(JSON.stringify({ type: "landmarks", ...payload }));
      return true;
    },
    stop() {
      if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: "stop" }));
      else socket.close();
    },
    close() { socket.close(); },
  };
}
