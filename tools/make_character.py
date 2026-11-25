#!/usr/bin/env python3
"""Turns one photo of your pet (or anyone) into the little character that delivers each door.

    python3 tools/make_character.py character/pet.jpg [--face=0.5,0.25,0.5]

Needs:  pip install rembg onnxruntime pillow opencv-python-headless numpy
Writes: site/character/{face,sit,deliver}.webp  and  tools/cards/base.webp
Tip: a photo of the whole animal, sitting or standing, against a plain background, works best.
With no photo the build uses a paper envelope with a wax seal instead (see default_character()).
"""
import os, sys
from PIL import Image, ImageOps, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "character")
CARD = os.path.join(HERE, "cards")


def painterly(img):
    """Soften noise and keep edges, so a phone photo sits well among paper-cut shapes."""
    import numpy as np, cv2
    a = np.array(img.convert("RGBA"))
    rgb = cv2.cvtColor(a[:, :, :3], cv2.COLOR_RGB2BGR)
    soft = cv2.bilateralFilter(rgb, 9, 38, 9)
    crisp = cv2.detailEnhance(soft, sigma_s=6, sigma_r=0.07)
    rgb = cv2.addWeighted(soft, 0.45, crisp, 0.55, 0)           # gentle, so fur does not turn gritty
    a[:, :, :3] = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
    return Image.fromarray(a, "RGBA")


def save(img, name, height=None, folder=OUT):
    os.makedirs(folder, exist_ok=True)
    if height:
        w = round(img.width * height / img.height)
        img = img.resize((w, height), Image.LANCZOS)
    img.save(os.path.join(folder, name), "WEBP", quality=90, method=6)


def from_photo(path, face_box=None):
    from rembg import remove, new_session
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im.thumbnail((1600, 1600))
    cut = remove(im, session=new_session("isnet-general-use"), post_process_mask=True)
    alpha = cut.getchannel("A")
    box = alpha.point(lambda v: 255 if v > 40 else 0).getbbox()
    if not box:
        sys.exit("Could not find the animal in that photo. Try one with a plainer background.")
    cut = painterly(cut.crop(box))
    # a thin pale edge helps the cutout read against dark walls and coloured cards
    a = cut.getchannel("A")
    halo = a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    edge = Image.new("RGBA", cut.size, (250, 244, 232, 0)); edge.putalpha(halo)
    cut = Image.alpha_composite(edge, cut)
    # face stamp: a square crop. Default is the top-centre of the animal; pass --face cx,cy,size
    # (fractions of the cutout, e.g. 0.75,0.3,0.5 for a head on the right) when the head is elsewhere.
    w, h = cut.size
    if face_box:
        cx, cy, sz = face_box
        side = max(40, int(sz * max(w, h)))
        left = int(cx * w - side / 2); top = int(cy * h - side / 2)
    else:
        side = min(w, int(h * 0.62)); left = (w - side) // 2; top = 0
    left = max(0, min(left, w - side)) if side <= w else 0
    top = max(0, min(top, h - side)) if side <= h else 0
    face = cut.crop((left, top, left + side, top + side))
    bg = Image.new("RGBA", face.size, (238, 226, 205, 255)); bg.alpha_composite(face)
    return cut, bg.convert("RGB")


def default_character():
    """A paper envelope with a wax seal, drawn here so no photo is needed."""
    S = 4                                           # draw big, shrink for smooth edges
    W, H = 420 * S, 520 * S
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ex0, ey0, ex1, ey1 = 30 * S, 150 * S, 390 * S, 470 * S
    d.rounded_rectangle((ex0, ey0, ex1, ey1), 14 * S, fill=(246, 238, 222, 255), outline=(201, 170, 120, 255), width=3 * S)
    d.polygon([(ex0 + 3 * S, ey0 + 3 * S), (ex1 - 3 * S, ey0 + 3 * S), ((ex0 + ex1) // 2, (ey0 + ey1) // 2 + 10 * S)], fill=(236, 224, 202, 255), outline=(201, 170, 120, 255))
    d.polygon([(ex0 + 3 * S, ey1 - 3 * S), ((ex0 + ex1) // 2 - 10 * S, (ey0 + ey1) // 2 + 30 * S), ((ex0 + ex1) // 2 + 10 * S, (ey0 + ey1) // 2 + 30 * S), (ex1 - 3 * S, ey1 - 3 * S)], fill=(240, 230, 212, 255))
    cx, cy = (ex0 + ex1) // 2, (ey0 + ey1) // 2 + 6 * S
    d.ellipse((cx - 46 * S, cy - 46 * S, cx + 46 * S, cy + 46 * S), fill=(168, 44, 48, 255), outline=(120, 28, 34, 255), width=3 * S)
    d.ellipse((cx - 34 * S, cy - 34 * S, cx + 34 * S, cy + 34 * S), outline=(205, 90, 90, 255), width=2 * S)
    hc = (238, 196, 120, 255)
    d.ellipse((cx - 24 * S, cy - 20 * S, cx, cy + 4 * S), fill=hc); d.ellipse((cx, cy - 20 * S, cx + 24 * S, cy + 4 * S), fill=hc)
    d.polygon([(cx - 23 * S, cy - 4 * S), (cx + 23 * S, cy - 4 * S), (cx, cy + 24 * S)], fill=hc)
    # a gold star on top, so it reads as a delivery
    pts = []
    import math
    for i in range(10):
        r = 62 * S if i % 2 == 0 else 26 * S
        ang = -math.pi / 2 + i * math.pi / 5
        pts.append((210 * S + r * math.cos(ang), 112 * S + r * math.sin(ang)))
    d.polygon(pts, fill=(226, 184, 96, 255), outline=(170, 128, 52, 255))
    im = im.resize((W // S, H // S), Image.LANCZOS)
    face = Image.new("RGBA", (240, 240), (238, 226, 205, 255))
    seal = im.crop((cx // S - 70, cy // S - 70, cx // S + 70, cy // S + 70)).resize((200, 200), Image.LANCZOS)
    face.alpha_composite(seal, (20, 20))
    return im, face.convert("RGB")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = args[0] if args else None
    fb = None
    for a in sys.argv[1:]:
        if a.startswith("--face"):
            v = a.split("=", 1)[1] if "=" in a else sys.argv[sys.argv.index(a) + 1]
            fb = tuple(float(x) for x in v.split(","))
    if src:
        cut, face = from_photo(src, fb); pet = True
    else:
        cut, face = default_character(); pet = False
    save(face.resize((240, 240), Image.LANCZOS), "face.webp")
    save(cut, "sit.webp", 700)
    save(cut, "deliver.webp", 700)
    save(cut, "base.webp", 700, folder=CARD)
    # the paw-lift animation needs a hand-split leg; remove any leftover from an earlier run
    leg = os.path.join(CARD, "leg.webp")
    if os.path.exists(leg): os.remove(leg)
    print("character ready:", "from your photo" if pet else "paper envelope (no photo given)")


if __name__ == "__main__":
    main()
