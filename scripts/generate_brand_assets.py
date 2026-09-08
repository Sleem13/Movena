"""Generate deterministic Movena web brand assets."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = REPOSITORY_ROOT / "frontend" / "public"
SOURCE = PUBLIC_ROOT / "brand-wordmark.png"
ICON_ROOT = PUBLIC_ROOT / "icons"
MARK_CROP = (45, 65, 555, 575)
ICON_SIZES = {
    "favicon-16.png": 16,
    "favicon-32.png": 32,
    "apple-touch-icon.png": 180,
    "icon-192.png": 192,
    "icon-512.png": 512,
}
CANVAS_SIZE = (1600, 640)
TEXT_X = 588
NAME_Y = 166
TAGLINE_Y = 414
NAME = "Movena"
TAGLINE = "Move Better, Recover Together."
INK = "#071B4A"
TEAL = "#0F8F83"
FONT_ROOT = Path("C:/Windows/Fonts")


def resize_contain(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_ROOT / name), size)


def build_master_wordmark(source: Image.Image) -> Image.Image:
    mark = source.crop(MARK_CROP)
    wordmark = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    wordmark.alpha_composite(mark, (MARK_CROP[0], MARK_CROP[1]))

    draw = ImageDraw.Draw(wordmark)
    draw.text((TEXT_X, NAME_Y), NAME, fill=INK, font=font("arialbd.ttf", 178))
    draw.text((TEXT_X + 4, TAGLINE_Y), TAGLINE, fill=TEAL, font=font("arial.ttf", 62))
    return wordmark


def main() -> None:
    ICON_ROOT.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE).convert("RGBA") as source:
        wordmark = build_master_wordmark(source)
        wordmark.save(SOURCE, format="PNG", optimize=True)
        mark = wordmark.crop(MARK_CROP)
        for filename, size in ICON_SIZES.items():
            mark.resize((size, size), Image.Resampling.LANCZOS).save(
                ICON_ROOT / filename,
                format="PNG",
                optimize=True,
            )

        for width in (420, 840):
            optimized = resize_contain(wordmark, width)
            optimized.save(
                PUBLIC_ROOT / f"brand-wordmark-{width}.webp",
                format="WEBP",
                quality=88,
                method=6,
            )
            optimized.save(
                PUBLIC_ROOT / f"brand-wordmark-{width}.png",
                format="PNG",
                optimize=True,
            )


if __name__ == "__main__":
    main()
