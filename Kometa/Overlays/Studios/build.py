#!/usr/bin/env python3
"""Make the studio logo overlays from the originals in each Source/ folder.

Every image is Kometa's poster size, 1000x1500, with the logo centred at the
bottom like the studio logos on MediUX posters: its middle at 500,1418, under
the title. Movies and shows use the same images. Per studio:

  Source/<Name>.svg or .png    the logo, or its parts, white parts white (colours are kept)
  Label/<File>_White.png       the logo
  Label/<File>_Black.png       its white parts black, for light posters (Dark label)

White parts inside a coloured shape stay white in both, like MARVEL in its
red box. Logos are only ever scaled down: svgs are drawn 4x bigger first,
pngs are used at the size they come in.

Some logos are put together from parts (PARTS): each part sits where it does
on a picture of the real logo, given as its left, top and height in that
picture's pixels (its width follows from its own shape). A part is a file in
Source/ or "rule", a bar, with its width last. The parts that aren't a whole
original logo:
  DC Studios/Source/STUDIOS.svg       the STUDIOS letters of the DC Studios print logo
  Marvel */Source/MARVEL.png          the red box of Marvel Studios' logo
  Marvel */Source/ANIMATION.png       the words, taken off the X-Men '97 and
  Marvel */Source/TELEVISION.png      Daredevil: Born Again posters

usage: python3 build.py [studio ...]        needs Pillow, numpy and cairosvg
"""
import io
import math
import os
import sys

import cairosvg
import numpy as np
from PIL import Image, ImageDraw

VERSION = "1.2.0"

HERE = os.path.dirname(os.path.abspath(__file__))
CX, CY = 500, 1418               # the logo's middle on the poster
CANVAS = (1000, 1500)
SS = 4                           # svgs are drawn this many times bigger, then scaled down
WHITE, BLACK = (255, 255, 255), (0, 0, 0)

# studio folder: file name, then the logo's width (w) or height (h) in px on the
# poster (sizes from MediUX posters: MARVEL STUDIOS 161 wide, MARVEL ANIMATION and
# MARVEL TELEVISION as high, DC STUDIOS 176, the DC roundel 54, Disney · PIXAR 182,
# LUCASFILM 102)
LOGOS = {
    "DC":                            dict(file="DC", h=54),
    "DC Studios":                    dict(file="DCStudios", w=176),
    "Lucasfilm":                     dict(file="Lucasfilm", w=102),
    "Marvel Animation":              dict(file="MarvelAnimation", h=36),
    "Marvel Studios":                dict(file="MarvelStudios", w=161),
    "Marvel Television":             dict(file="MarvelTelevision", h=36),
    "Pixar":                         dict(file="DisneyPixar", w=182),
    "Walt Disney Animation Studios": dict(file="Disney", h=50),
}

# logos put together from parts: (part, left, top, height[, width])
PARTS = {
    # on a 600x600 picture of the DC STUDIOS logo
    "DCStudios": [("DC", 61, 227, 146), ("STUDIOS", 222, 271, 56),
                  ("rule", 224, 249.5, 5, 314), ("rule", 224, 342.5, 5, 314)],
    # on the X-Men '97 and Daredevil: Born Again posters, 1500x2250
    "MarvelAnimation": [("MARVEL", 606, 2100, 54), ("ANIMATION", 733, 2100, 54)],
    "MarvelTelevision": [("MARVEL", 605, 2100, 54), ("TELEVISION", 733, 2100, 54)],
}


def crop(im):
    im = im.convert("RGBA")
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 2 else 0).getbbox())


def source(folder, name):
    for ext in (".svg", ".png"):
        path = os.path.join(HERE, folder, "Source", name + ext)
        if os.path.exists(path):
            return path
    raise SystemExit(f"{folder}: no Source/{name}.svg or .png")


def svg_png(svg, page_height):
    return crop(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg, output_height=page_height))))


def render(path, height):
    """The source as an image; an svg is drawn so the logo itself is height px tall."""
    if not path.endswith(".svg"):
        return crop(Image.open(path))
    svg = open(path, "rb").read()
    im = svg_png(svg, height * 3)            # most svgs have room round the logo
    if abs(height / im.height - 1) > 0.02:
        im = svg_png(svg, round(height * 3 * height / im.height))
    return im


def recolor(im, rgb):
    """The white and grey parts in rgb, except those inside a coloured shape."""
    a = np.asarray(im.convert("RGBA")).copy()
    c = a[..., :3].astype(int)
    neutral = (c.max(axis=2) - c.min(axis=2)) < 60
    coloured = ~neutral & (a[..., 3] > 128)
    # flood everything that isn't coloured from outside the logo
    walls = Image.fromarray(np.where(coloured, 0, 255).astype(np.uint8))
    framed = Image.new("L", (walls.width + 2, walls.height + 2), 255)
    framed.paste(walls, (1, 1))
    ImageDraw.floodfill(framed, (0, 0), 128)
    outside = np.asarray(framed)[1:-1, 1:-1] == 128
    a[neutral & outside, :3] = rgb
    return Image.fromarray(a, "RGBA")


def shrink(im, size):
    """Premultiplied, so the transparent pixels don't darken the edges."""
    return im.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")


def lockup(folder, spec):
    """A logo put together from its PARTS: the big image and its size on the poster."""
    parts = []
    for name, x, y, h, *w in PARTS[spec["file"]]:
        path = None if name == "rule" else source(folder, name)
        if path:
            probe = render(path, 200)
            w = [h * probe.width / probe.height]
        parts.append((name, path, x, y, w[0], h))
    x0, y0 = min(p[2] for p in parts), min(p[3] for p in parts)
    x1, y1 = max(p[2] + p[4] for p in parts), max(p[3] + p[5] for p in parts)
    fit = spec["h"] / (y1 - y0) if "h" in spec else spec["w"] / (x1 - x0)   # poster px per picture px
    k = fit * SS
    for name, path, x, y, w, h in parts:
        if path and path.endswith(".png"):   # never draw a png bigger than it comes
            k = min(k, crop(Image.open(path)).height / h)
    big = Image.new("RGBA", (math.ceil((x1 - x0) * k) + 2, math.ceil((y1 - y0) * k) + 2), (0, 0, 0, 0))
    for name, path, x, y, w, h in parts:
        X, Y, W, H = (x - x0) * k, (y - y0) * k, w * k, h * k
        if name == "rule":
            ImageDraw.Draw(big).rectangle((X, Y, X + W - 1, Y + H - 1), fill=WHITE + (255,))
        else:
            im = render(path, round(H))
            big.alpha_composite(shrink(im, (round(W), round(H))), (round(X), round(Y)))
    big = crop(big)
    return big, (round(big.width * fit / k), round(big.height * fit / k))


def master(folder, spec):
    """The logo drawn big, and its size on the poster."""
    if spec["file"] in PARTS:
        return lockup(folder, spec)
    path = source(folder, spec["file"])
    if "h" in spec:
        big = render(path, spec["h"] * SS)
        return big, (round(spec["h"] * big.width / big.height), spec["h"])
    probe = render(path, 100)                # by width: draw it tall enough for that width
    big = render(path, round(spec["w"] * SS * probe.height / probe.width))
    return big, (spec["w"], round(spec["w"] * big.height / big.width))


def save(logo, folder, name):
    os.makedirs(os.path.join(HERE, folder, "Label"), exist_ok=True)
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas.alpha_composite(logo, (round(CX - logo.width / 2), round(CY - logo.height / 2)))
    canvas.save(os.path.join(HERE, folder, "Label", name), optimize=True)


def build(folder, spec):
    f = spec["file"]
    big, (w, h) = master(folder, spec)
    if big.height < h:
        print(f"  warning: {folder}'s source is only {big.height}px high, drawn at {h}")
    save(shrink(recolor(big, WHITE), (w, h)), folder, f"{f}_White.png")
    save(shrink(recolor(big, BLACK), (w, h)), folder, f"{f}_Black.png")
    print(f"{folder:<30} {w}x{h}")


if __name__ == "__main__":
    names = sys.argv[1:] or list(LOGOS)
    unknown = [n for n in names if n not in LOGOS]
    if unknown:
        raise SystemExit(f"unknown studio: {', '.join(unknown)}")
    for name in names:
        build(name, LOGOS[name])
