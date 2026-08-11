import { appendVideoToFormData, toMobileVideo } from "@/src/utils/mobileVideo";

describe("mobile video multipart handling", () => {
  it("preserves the browser File returned by Expo ImagePicker", () => {
    const file = { name: "squat.mp4", type: "video/mp4" } as File;
    const video = toMobileVideo({
      assetId: null,
      uri: "blob:http://localhost:8081/video",
      width: 1280,
      height: 720,
      type: "video",
      fileName: "squat.mp4",
      fileSize: 1024,
      mimeType: "video/mp4",
      duration: 1000,
      file,
    });

    expect(video.file).toBe(file);
  });

  it("appends the real browser File instead of a native URI descriptor", () => {
    const file = { name: "squat.mp4", type: "video/mp4" } as File;
    const append = jest.fn();
    appendVideoToFormData({ append } as unknown as FormData, {
      uri: "blob:http://localhost:8081/video",
      name: "squat.mp4",
      type: "video/mp4",
      file,
    });

    expect(append).toHaveBeenCalledWith("video", file, "squat.mp4");
  });

  it("keeps the React Native URI descriptor fallback", () => {
    const append = jest.fn();
    appendVideoToFormData({ append } as unknown as FormData, {
      uri: "file:///movement.mp4",
      name: "movement.mp4",
      type: "video/mp4",
    });

    expect(append).toHaveBeenCalledWith("video", {
      uri: "file:///movement.mp4",
      name: "movement.mp4",
      type: "video/mp4",
    });
  });
});
