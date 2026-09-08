"""Generate Expo assets from the approved Movena source artwork.

This deterministic crop/resize pipeline keeps web and mobile artwork aligned.
It does not redraw or generatively alter the approved mark.
"""

from pathlib import Path

from PIL import Image


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPOSITORY_ROOT / "frontend" / "public" / "brand-wordmark.png"
OUTPUT = REPOSITORY_ROOT / "mobile" / "assets" / "images"
MARK_CROP = (45, 65, 555, 575)


def centered_mark(mark: Image.Image, canvas_size: int, mark_size: int) -> Image.Image:
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    resized = mark.resize((mark_size, mark_size), Image.Resampling.LANCZOS)
    offset = (canvas_size - mark_size) // 2
    canvas.alpha_composite(resized, (offset, offset))
    return canvas


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE).convert("RGBA") as wordmark:
        mark = wordmark.crop(MARK_CROP)
        mark.resize((1024, 1024), Image.Resampling.LANCZOS).save(
            OUTPUT / "icon.png", format="PNG", optimize=True,
        )
        centered_mark(mark, 1024, 640).save(
            OUTPUT / "adaptive-icon.png", format="PNG", optimize=True,
        )
        centered_mark(mark, 1024, 720).save(
            OUTPUT / "splash-icon.png", format="PNG", optimize=True,
        )
        mark.resize((64, 64), Image.Resampling.LANCZOS).save(
            OUTPUT / "favicon.png", format="PNG", optimize=True,
        )
        mobile_width = 840
        mobile_height = round(wordmark.height * mobile_width / wordmark.width)
        wordmark.resize((mobile_width, mobile_height), Image.Resampling.LANCZOS).save(
            OUTPUT / "brand-wordmark.png", format="PNG", optimize=True,
        )


if __name__ == "__main__":
    main()
