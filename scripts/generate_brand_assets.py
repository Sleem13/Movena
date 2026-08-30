"""Generate exact, optimized web brand derivatives from the approved wordmark.

This is a deterministic crop/resize pipeline. It never redraws or generatively
alters the approved PhysioVision artwork.
"""

from pathlib import Path

from PIL import Image


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


def resize_contain(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def main() -> None:
    ICON_ROOT.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE).convert("RGBA") as wordmark:
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
