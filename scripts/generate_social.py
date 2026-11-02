"""Generate assets/social-preview.png (1280x640 GitHub social card), Pillow-only.

GitHub/Twitter do not render SVG social cards, so this rasterizes the Atlas
brand lockup: gradient field, dot grid, kicker, title, rule, tagline, chips,
fold mark, footer URL. Run: python scripts/generate_social.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "social-preview.png")


def _font(size: int, bold: bool = False):
    from PIL import ImageFont
    names = ["arialbd.ttf" if bold else "arial.ttf",
             "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    bases = [r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu",
             "/usr/share/fonts/dejavu", "/System/Library/Fonts/Supplemental"]
    for base in bases:
        for name in names:
            path = os.path.join(base, name)
            if os.path.isfile(path):
                try:
                    return ImageFont.truetype(path, size)
                except OSError:
                    continue
    return ImageFont.load_default(size=size)


def _gradient(w, h, top, bottom):
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(round(a + (b - a) * t) for a, b in zip(top, bottom))
    return base.resize((w, h))


def main() -> str:
    img = _gradient(W, H, (16, 28, 58), (10, 15, 30))
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(0, H, 26):
        for x in range(0, W, 26):
            d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255, 14))
    d.rectangle([0, 0, W, 5], fill=(125, 211, 252))
    d.rounded_rectangle([10, 14, W - 10, H - 14], radius=18, outline=(248, 250, 252, 26), width=2)
    # Fold mark, right side.
    cx, cy, s = 1030, 300, 2.35
    pts_top = [(-52, -34), (8, -54), (52, -22), (-8, -2)]
    pts_leg = [(-52, -34), (-52, 22), (-8, 50), (52, 20), (52, -22)]
    top = [(cx + x * s, cy + y * s) for x, y in pts_top]
    d.polygon(top, fill=(125, 211, 252, 52), outline=(125, 211, 252))
    inner = [(cx + x * s * 0.55, cy + y * s * 0.55 - 6) for x, y in pts_top]
    d.polygon(inner, fill=(125, 211, 252, 26))
    leg = [(cx + x * s, cy + y * s) for x, y in pts_leg]
    d.line(leg, fill=(125, 211, 252), width=7, joint="curve")
    spine = [(cx - 8 * s, cy - 2 * s), (cx - 8 * s, cy + 50 * s)]
    d.line(spine, fill=(125, 211, 252), width=5, joint="curve")
    nx, ny = cx, cy  # group origin, as in the approved SVG mark
    d.ellipse([nx - 28, ny - 28, nx + 28, ny + 28], outline=(139, 92, 246, 140), width=3)
    d.ellipse([nx - 16, ny - 16, nx + 16, ny + 16], fill=(139, 92, 246))
    # Editorial column.
    f_title = _font(76, bold=True)
    f_kick = _font(20)
    f_tag = _font(29)
    f_chip = _font(15)
    f_foot = _font(19)
    d.text((76, 170), "Atlas", font=f_title, fill=(248, 250, 252))
    d.line([(78, 270), (690, 270)], fill=(125, 211, 252), width=3)
    d.text((78, 292), "AEGEANWORKS  ·  KNOWLEDGE PLATFORM", font=f_kick, fill=(125, 211, 252))
    d.text((80, 352), "An interactive visual knowledge platform for", font=f_tag, fill=(248, 250, 252, 189))
    d.text((80, 392), "scientific figures.", font=f_tag, fill=(248, 250, 252, 189))
    for i, label in enumerate(["figures", "entities", "pathways"]):
        x0 = 80 + i * 170
        d.rounded_rectangle([x0, 500, x0 + 150, 538], radius=19, fill=(11, 18, 32, 140),
                            outline=(148, 163, 184, 90), width=1)
        d.text((x0 + 75, 508), label, font=f_chip, fill=(248, 250, 252, 210), anchor="ma")
    d.text((76, 576), "AEGEANWORKS", font=f_foot, fill=(248, 250, 252, 128))
    url = "github.com/AegeanWorks/Atlas"
    d.text((W - 76, 576), url, font=f_foot, fill=(248, 250, 252, 140), anchor="ra")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    return OUT


if __name__ == "__main__":
    print(main())
