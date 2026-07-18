import type { MobileVideo } from "@/src/types/analysis";

export const MAX_UPLOAD_BYTES = 100 * 1024 * 1024;
const SUPPORTED_EXTENSIONS = new Set(["mp4", "mov", "avi", "mkv", "webm"]);

export function validateSelectedVideo(video: MobileVideo): string | null {
  const extension = video.name.split(".").pop()?.toLowerCase();
  if (!extension || !SUPPORTED_EXTENSIONS.has(extension)) return "Choose an MP4, MOV, AVI, MKV, or WEBM video.";
  if (video.size === 0) return "The selected video is empty. Choose another recording.";
  if (video.size && video.size > MAX_UPLOAD_BYTES) return "This video is larger than 100 MB. Record or select a shorter video.";
  return null;
}

export const canSubmitUpload = (video: MobileVideo | null, busy: boolean) => Boolean(video) && !busy;

export function createUploadSubmissionGuard() {
  let active = false;
  return {
    tryStart() {
      if (active) return false;
      active = true;
      return true;
    },
    finish() { active = false; },
  };
}
