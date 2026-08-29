"""Generate Expo raster assets from the established PhysioVision pulse mark."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "images"
BLUE = (37, 99, 235)
TEAL = (15, 143, 131)
WHITE = (255, 255, 255)


def gradient(size: int) -> Image.Image:
    image = Image.new("RGB", (size, size))
    pixels = image.load()
    for y in range(size):
        for x in range(size):
            ratio = (x + y) / (2 * (size - 1))
            pixels[x, y] = tuple(round(BLUE[i] * (1 - ratio) + TEAL[i] * ratio) for i in range(3))
    return image


def draw_mark(image: Image.Image, *, inset: int = 0, rounded_tile: bool = False) -> Image.Image:
    size = image.width
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    if rounded_tile:
        tile = gradient(size - inset * 2).convert("RGBA")
        mask = Image.new("L", tile.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, tile.width - 1, tile.height - 1), radius=tile.width // 4, fill=255)
        layer.paste(tile, (inset, inset), mask)
    scale = size / 64
    pulse = [(12, 47), (22, 47), (25, 40), (30, 51), (35, 36), (39, 44), (52, 44)]
    pulse_xy = [(round(x * scale), round(y * scale)) for x, y in pulse]
    movement_segments = [
        [(18, 31), (24, 26), (31.5, 23.5), (38, 25), (43.3, 29.1)],
        [(29.5, 24), (33.7, 34.2), (42.5, 40.5)],
        [(31.7, 29.4), (23.5, 39.2), (16.3, 41.6)],
    ]
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    for segment in movement_segments:
        shadow_draw.line([(round(x * scale), round(y * scale)) for x, y in segment], fill=(16, 36, 62, 85), width=max(5, round(4.8 * scale)), joint="curve")
    head_box = tuple(round(value * scale) for value in (20.4, 12.4, 29.6, 21.6))
    shadow_draw.ellipse(head_box, fill=(16, 36, 62, 85))
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(1, size // 128)))
    layer.alpha_composite(shadow)
    draw = ImageDraw.Draw(layer)
    draw.line(pulse_xy, fill=(255, 255, 255, 225), width=max(3, round(3.4 * scale)), joint="curve")
    for segment in movement_segments:
        draw.line([(round(x * scale), round(y * scale)) for x, y in segment], fill=WHITE, width=max(5, round(4.4 * scale)), joint="curve")
    draw.ellipse(head_box, fill=WHITE)
    return Image.alpha_composite(image.convert("RGBA"), layer)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    icon = draw_mark(gradient(1024))
    icon.convert("RGB").save(OUTPUT / "icon.png", optimize=True)

    adaptive = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    adaptive = draw_mark(adaptive)
    adaptive.save(OUTPUT / "adaptive-icon.png", optimize=True)

    splash = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    splash = draw_mark(splash, inset=190, rounded_tile=True)
    splash.save(OUTPUT / "splash-icon.png", optimize=True)

    icon.resize((64, 64), Image.Resampling.LANCZOS).convert("RGB").save(OUTPUT / "favicon.png", optimize=True)


if __name__ == "__main__":
    main()
