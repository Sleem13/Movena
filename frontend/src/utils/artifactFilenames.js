export function exerciseArtifactSlug(exerciseId) {
  return String(exerciseId || "movement")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "movement";
}

export function artifactFilename(exerciseId, kind) {
  const extension = kind === "report" ? "pdf" : "mp4";
  return `physiovision-${exerciseArtifactSlug(exerciseId)}-${kind}.${extension}`;
}
