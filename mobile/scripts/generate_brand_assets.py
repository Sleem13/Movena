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


def draw_pulse(image: Image.Image, *, inset: int = 0, rounded_tile: bool = False) -> Image.Image:
    size = image.width
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    if rounded_tile:
        tile = gradient(size - inset * 2).convert("RGBA")
        mask = Image.new("L", tile.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, tile.width - 1, tile.height - 1), radius=tile.width // 4, fill=255)
        layer.paste(tile, (inset, inset), mask)
    radius = int(size * 0.31)
    draw.ellipse((size // 2 - radius, size // 2 - radius, size // 2 + radius, size // 2 + radius), outline=(255, 255, 255, 55), width=max(3, size // 32))
    points = [(0.20, 0.53), (0.34, 0.53), (0.40, 0.36), (0.51, 0.70), (0.59, 0.48), (0.64, 0.59), (0.80, 0.59)]
    xy = [(round(x * size), round(y * size)) for x, y in points]
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).line(xy, fill=(16, 36, 62, 85), width=max(5, size // 19), joint="curve")
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(1, size // 128)))
    layer.alpha_composite(shadow)
    ImageDraw.Draw(layer).line(xy, fill=WHITE, width=max(5, size // 22), joint="curve")
    return Image.alpha_composite(image.convert("RGBA"), layer)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    icon = draw_pulse(gradient(1024))
    icon.convert("RGB").save(OUTPUT / "icon.png", optimize=True)

    adaptive = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    adaptive = draw_pulse(adaptive)
    adaptive.save(OUTPUT / "adaptive-icon.png", optimize=True)

    splash = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    splash = draw_pulse(splash, inset=190, rounded_tile=True)
    splash.save(OUTPUT / "splash-icon.png", optimize=True)

    icon.resize((64, 64), Image.Resampling.LANCZOS).convert("RGB").save(OUTPUT / "favicon.png", optimize=True)


if __name__ == "__main__":
    main()
