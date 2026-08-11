import type { ImagePickerAsset } from "expo-image-picker";

import type { MobileVideo } from "@/src/types/analysis";

export function toMobileVideo(asset: ImagePickerAsset): MobileVideo {
  const extension = asset.fileName?.split(".").pop()?.toLowerCase() || "mp4";
  return {
    uri: asset.uri,
    name: asset.fileName || `movement-${Date.now()}.${extension}`,
    type: asset.mimeType || (extension === "mov" ? "video/quicktime" : "video/mp4"),
    size: asset.fileSize,
    duration: asset.duration ?? undefined,
    file: asset.file ?? undefined,
  };
}

export function appendVideoToFormData(form: FormData, video: MobileVideo): void {
  if (video.file) {
    form.append("video", video.file, video.name);
    return;
  }
  form.append("video", { uri: video.uri, name: video.name, type: video.type } as unknown as Blob);
}
