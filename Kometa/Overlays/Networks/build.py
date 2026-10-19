#!/usr/bin/env python3
"""Make the network logo overlays from the originals in each Source/ folder.

Every image is Kometa's poster size, 1000x1500, with the logo's top-left
corner at 43,43 like the network logos on MediUX posters. Per network:

  Source/<File>.svg or .png        the logo, white (Netflix keeps its red N)
  Source/<File>_Color.svg or .png  the colour logo, if it has one
  Source/<File>_<show>.svg         a show tint with its own fill (the HBO ones)

  Label/<File>_White.png           the logo
  Label/<File>_Black.png           white parts black               Dark label
  Label/<File>_Color.png           the colour logo                  Color label
  Label/<File>_ColorDark.png       colour logo, white parts black   Color + Dark labels
  Tinted/<File>_<show>.png         one show's logo in its own colour

Logos are only ever scaled down: svgs are drawn 4x bigger first, pngs are
used at the size they come in.

usage: python3 build.py [network ...]        needs Pillow, numpy and cairosvg
"""
import io
import os
import sys

import cairosvg
import numpy as np
from PIL import Image

VERSION = "1.0.0"

HERE = os.path.dirname(os.path.abspath(__file__))
X0, Y0 = 43, 43                  # the logo's top-left corner on the poster
CANVAS = (1000, 1500)
SS = 4                           # svgs are drawn this many times bigger, then scaled down
WHITE, BLACK = (255, 255, 255), (0, 0, 0)

# network folder: file name, then the logo's height (h) or width (w) in px on
# the poster (sizes from MediUX posters: HBO 45 high, hulu 33, square logos 58)
#   color:      True = Source/<file>_Color.*, "#hex" = the logo in that colour
#   color_dark: also make _ColorDark, for colour logos with white text
#   tints:      {show: "#hex"}, or {show: "svg"} for Source/<file>_<show>.svg
LOGOS = {
    "Acorn TV":         dict(file="AcornTV", h=30),
    "Adult Swim":       dict(file="AdultSwim", h=45),
    "AMC":              dict(file="AMC", h=47),
    "Apple TV":         dict(file="AppleTV", h=45),
    "BBC":              dict(file="BBC", h=32),
    "BBC Earth":        dict(file="BBCEarth", h=52),
    "BritBox":          dict(file="BritBox", h=33),
    "C More":           dict(file="CMore", h=31),
    "Cartoon Network":  dict(file="CartoonNetwork", h=45),
    "Crave":            dict(file="Crave", h=30),
    "Crunchyroll":      dict(file="Crunchyroll", h=58, color=True),
    "Curiosity Stream": dict(file="CuriosityStream", h=40),
    "DAZN":             dict(file="DAZN", h=58),
    "discovery+":       dict(file="discoveryPlus", h=32),
    "Disney Plus":      dict(file="DisneyPlus", w=140),
    "FX":               dict(file="FX", h=44, tints={"thebear": "#fcf6c9"}),
    "fubo":             dict(file="fubo", h=36, color="#eb3401"),
    "HBO":              dict(file="HBO", h=45, tints={s: "svg" for s in ["chernobyl", "euphoria", "succession", "thelastofus"]}),
    "HBO Max":          dict(file="HBOMax", w=93, tints={"peacemaker": "#fcde15"}),
    "Hulu":             dict(file="Hulu", h=33, color=True),
    "ITVX":             dict(file="ITVX", h=34),
    "MGM+":             dict(file="MGMPlus", h=46),
    "Netflix":          dict(file="NSeries", h=47),
    "Nickelodeon":      dict(file="Nickelodeon", h=26),
    "Paramount Plus":   dict(file="ParamountPlus", h=58, color=True),
    "Peacock":          dict(file="Peacock", h=50, color=True, color_dark=True),
    "Prime Video":      dict(file="PrimeVideo", h=53, color=True, color_dark=True),
    "Rakuten TV":       dict(file="RakutenTV", h=58, color="#842ecb"),
    "Showtime":         dict(file="Showtime", h=48),
    "Shudder":          dict(file="Shudder", h=28),
    "SkyShowtime":      dict(file="SkyShowtime", h=38),
    "Stan":             dict(file="Stan", h=36),
    "Starz":            dict(file="Starz", h=30),
    "SVT1":             dict(file="SVT1", h=42),
    "TV4":              dict(file="TV4", h=58),
    "Viaplay":          dict(file="Viaplay", h=58, color=True),
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


def neutral(im, rgb):
    """White and grey parts in rgb; colours (Netflix's red N, the dots) are kept."""
    a = np.asarray(im.convert("RGBA")).copy()
    c = a[..., :3].astype(int)
    a[(c.max(axis=2) - c.min(axis=2)) < 60, :3] = rgb
    return Image.fromarray(a, "RGBA")


def fill(im, rgb):
    out = Image.new("RGBA", im.size, rgb + (0,))
    out.putalpha(im.getchannel("A"))
    return out


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shrink(im, size):
    """Premultiplied, so the transparent pixels don't darken the edges."""
    return im.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")


def svg_fill(path, logo):
    """A tint svg's colours on the logo's own crisp shape."""
    tint = shrink(render(path, logo.height * SS), logo.size)
    a = np.asarray(tint).copy()
    a[..., 3] = np.asarray(logo)[..., 3]
    return Image.fromarray(a, "RGBA")


def save(logo, folder, sub, name):
    os.makedirs(os.path.join(HERE, folder, sub), exist_ok=True)
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas.alpha_composite(logo, (X0, Y0))
    canvas.save(os.path.join(HERE, folder, sub, name), optimize=True)


def build(folder, spec):
    f = spec["file"]
    master = render(source(folder, f), (spec.get("h") or round(spec["w"] / 2)) * SS)
    aspect = master.width / master.height
    w, h = (spec["w"], round(spec["w"] / aspect)) if "w" in spec else (round(spec["h"] * aspect), spec["h"])
    if master.height < h:
        print(f"  warning: {folder}'s source is only {master.height}px high, drawn at {h}")

    label = {"White": shrink(neutral(master, WHITE), (w, h)), "Black": shrink(neutral(master, BLACK), (w, h))}
    color = spec.get("color")
    if color is True:
        c = render(source(folder, f + "_Color"), h * SS)
        label["Color"] = shrink(c, (w, h))
        if spec.get("color_dark"):
            label["ColorDark"] = shrink(neutral(c, BLACK), (w, h))
    elif color:
        label["Color"] = fill(label["White"], hexrgb(color))
    for name, im in label.items():
        save(im, folder, "Label", f"{f}_{name}.png")

    for show, how in spec.get("tints", {}).items():
        if how == "svg":
            tint = svg_fill(source(folder, f"{f}_{show}"), label["White"])
        else:
            tint = fill(label["White"], hexrgb(how))
        save(tint, folder, "Tinted", f"{f}_{show}.png")

    tints = f", tints: {', '.join(spec['tints'])}" if spec.get("tints") else ""
    print(f"{folder:<17} {w}x{h:<4} {', '.join(label)}{tints}")


if __name__ == "__main__":
    names = sys.argv[1:] or list(LOGOS)
    unknown = [n for n in names if n not in LOGOS]
    if unknown:
        raise SystemExit(f"unknown network: {', '.join(unknown)}")
    for name in names:
        build(name, LOGOS[name])
