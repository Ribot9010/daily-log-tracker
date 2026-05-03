"""One-shot helper that produces icon-192.png and icon-512.png next to itself.

Re-run this whenever you want to tweak the icon look. Pillow is the only dep.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BG = (15, 23, 42)        # slate-900 — matches the form background
FG = (56, 189, 248)      # sky-400  — matches the accent in index.html
HERE = Path(__file__).parent


def find_bold_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\seguibl.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_icon(size: int, out: Path) -> None:
    img = Image.new("RGB", (size, size), BG)
    draw = ImageDraw.Draw(img)

    # Rounded square border for a hint of icon shape on legacy launchers.
    radius = size // 8
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=BG)

    text = "DL"
    font = find_bold_font(int(size * 0.55))
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pos = ((size - tw) // 2 - bbox[0], (size - th) // 2 - bbox[1])
    draw.text(pos, text, fill=FG, font=font)

    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({size}x{size})")


if __name__ == "__main__":
    draw_icon(192, HERE / "icon-192.png")
    draw_icon(512, HERE / "icon-512.png")
