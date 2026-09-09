import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { BRAND } from "./brand.js";

const luminance = (hex) => {
  const rgb = hex.match(/[\da-f]{2}/gi).map((part) => {
    const channel = parseInt(part, 16) / 255;
    return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
};
const contrast = (a, b) => {
  const values = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (values[0] + 0.05) / (values[1] + 0.05);
};
const css = readFileSync("src/styles.css", "utf8");
const tokens = (block) => Object.fromEntries([...block.matchAll(/--([\w-]+):\s*(#[\da-f]{6});/gi)].map((m) => [m[1], m[2]]));

describe("Movena brand", () => {
  it("keeps install metadata aligned with the identity", () => {
    const manifest = JSON.parse(readFileSync("public/manifest.webmanifest", "utf8"));
    expect(manifest.theme_color).toBe(BRAND.colors.blue);
    expect(manifest.background_color).toBe(BRAND.colors.canvas);
    expect(manifest.description).toBe(BRAND.description);
    const html = readFileSync("index.html", "utf8");
    expect(html).toContain(`content="${BRAND.colors.blue}"`);
    expect(html).toContain(BRAND.tagline);
  });
  it.each(["light", "dark"])("provides readable core text and semantic colours in %s mode", (theme) => {
    const root = tokens(css.match(/:root\s*\{([^}]+)\}/)[1]);
    const palette = theme === "dark" ? { ...root, ...tokens(css.match(/\[data-theme="dark"\]\s*\{([^}]+)\}/)[1]) } : root;
    for (const [foreground, background] of [["text", "surface"], ["text-body", "surface-soft"], ["text-muted", "surface-muted"], ["action-text", "action"], ["action-text", "action-hover"], ["selection-text", "selection"], ["positive", "positive-soft"], ["warning", "warning-soft"], ["danger", "danger-soft"]]) {
      expect(contrast(palette[foreground], palette[background]), `${foreground} on ${background}`).toBeGreaterThanOrEqual(4.5);
    }
  });
  it("keeps shared light theme colours consistent", () => {
    const root = tokens(css.match(/:root\s*\{([^}]+)\}/)[1]);
    expect(root["brand-ink"]).toBe(BRAND.colors.ink);
    expect(root["brand-blue"]).toBe(BRAND.colors.blue);
    expect(root["brand-teal"]).toBe(BRAND.colors.teal);
  });
});
