import { canSubmitUpload, createUploadSubmissionGuard, MISSING_VIDEO_MESSAGE, validateSelectedVideo } from "@/src/utils/uploadValidation";

const video = { uri: "file:///movement.mp4", name: "movement.mp4", type: "video/mp4", size: 1024 };

describe("upload reliability", () => {
  it("prevents double submit while an upload is active", () => expect(canSubmitUpload(video, true)).toBe(false));
  it("prevents same-tick duplicate submission before React state updates", () => {
    const guard = createUploadSubmissionGuard();
    expect(guard.tryStart()).toBe(true);
    expect(guard.tryStart()).toBe(false);
    guard.finish();
    expect(guard.tryStart()).toBe(true);
  });
  it("requires a selected video and provides an upload-only warning", () => {
    expect(canSubmitUpload(null, false)).toBe(false);
    expect(MISSING_VIDEO_MESSAGE).toBe("Select a video before starting analysis.");
  });
  it("allows retry with the retained valid video", () => expect(canSubmitUpload(video, false)).toBe(true));
  it("rejects unsupported and oversized files before upload", () => {
    expect(validateSelectedVideo({ ...video, name: "movement.txt" })).toMatch(/MP4/i);
    expect(validateSelectedVideo({ ...video, size: 101 * 1024 * 1024 })).toMatch(/100 MB/i);
  });
});
