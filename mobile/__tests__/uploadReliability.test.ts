import { canSubmitUpload, validateSelectedVideo } from "@/src/utils/uploadValidation";

const video = { uri: "file:///movement.mp4", name: "movement.mp4", type: "video/mp4", size: 1024 };

describe("upload reliability", () => {
  it("prevents double submit while an upload is active", () => expect(canSubmitUpload(video, true)).toBe(false));
  it("requires a selected video", () => expect(canSubmitUpload(null, false)).toBe(false));
  it("allows retry with the retained valid video", () => expect(canSubmitUpload(video, false)).toBe(true));
  it("rejects unsupported and oversized files before upload", () => {
    expect(validateSelectedVideo({ ...video, name: "movement.txt" })).toMatch(/MP4/i);
    expect(validateSelectedVideo({ ...video, size: 101 * 1024 * 1024 })).toMatch(/100 MB/i);
  });
});
