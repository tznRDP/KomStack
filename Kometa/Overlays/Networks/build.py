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
  Tinted/<File>_<show>.png         one show's logo in its own colour (TINTS below)

Logos are only ever scaled down: svgs are drawn 4x bigger first, pngs are
used at the size they come in. Tint effects are drawn at that size too.

usage: python3 build.py [network ...]        needs Pillow, numpy and cairosvg
"""
import io
import os
import sys
import zlib

import cairosvg
import numpy as np
from PIL import Image, ImageDraw

VERSION = "1.2.0"

HERE = os.path.dirname(os.path.abspath(__file__))
X0, Y0 = 43, 43                  # the logo's top-left corner on the poster
CANVAS = (1000, 1500)
SS = 4                           # svgs are drawn this many times bigger, then scaled down
WHITE, BLACK = (255, 255, 255), (0, 0, 0)

# network folder: file name, then the logo's height (h) or width (w) in px on
# the poster (sizes from MediUX posters: HBO 45 high, hulu 33, square logos 58)
#   color:      True = Source/<file>_Color.*, "#hex" = the logo in that colour
#   color_dark: also make _ColorDark, for colour logos with white text
LOGOS = {
    "ABC":              dict(file="ABC", h=58),
    "Acorn TV":         dict(file="AcornTV", h=30),
    "Adult Swim":       dict(file="AdultSwim", h=45),
    "AMC":              dict(file="AMC", h=47),
    "Apple TV":         dict(file="AppleTV", h=45),
    "BBC":              dict(file="BBC", h=32),
    "BBC Earth":        dict(file="BBCEarth", h=52),
    "BritBox":          dict(file="BritBox", h=33),
    "C More":           dict(file="CMore", h=31),
    "Cartoon Network":  dict(file="CartoonNetwork", h=45),
    "CBS":              dict(file="CBS", h=32),
    "Comedy Central":   dict(file="ComedyCentral", h=38, color=True, color_dark=True),
    "Crave":            dict(file="Crave", h=30),
    "Crunchyroll":      dict(file="Crunchyroll", h=58, color=True),
    "Curiosity Stream": dict(file="CuriosityStream", h=40),
    "DAZN":             dict(file="DAZN", h=58),
    "discovery+":       dict(file="discoveryPlus", h=32),
    "Disney Plus":      dict(file="DisneyPlus", w=140),
    "FOX":              dict(file="FOX", h=37),
    "Freeform":         dict(file="Freeform", h=30, color=True),
    "FX":               dict(file="FX", h=44),
    "fubo":             dict(file="fubo", h=36, color="#eb3401"),
    "HBO":              dict(file="HBO", h=45),
    "HBO Max":          dict(file="HBOMax", w=93),
    "Hulu":             dict(file="Hulu", h=33, color=True),
    "ITVX":             dict(file="ITVX", h=34),
    "MGM+":             dict(file="MGMPlus", h=46),
    "NBC":              dict(file="NBC", h=34, color=True, color_dark=True),
    "Netflix":          dict(file="NSeries", h=47),
    "Nickelodeon":      dict(file="Nickelodeon", h=26),
    "Paramount Plus":   dict(file="ParamountPlus", h=58, color=True),
    "Peacock":          dict(file="Peacock", h=50, color=True, color_dark=True),
    "Prime Video":      dict(file="PrimeVideo", h=53, color=True, color_dark=True),
    "Quibi":            dict(file="Quibi", h=38, color=True),
    "Rakuten TV":       dict(file="RakutenTV", h=58, color="#842ecb"),
    "Showtime":         dict(file="Showtime", h=48),
    "Shudder":          dict(file="Shudder", h=28),
    "SkyShowtime":      dict(file="SkyShowtime", h=38),
    "Stan":             dict(file="Stan", h=36),
    "Starz":            dict(file="Starz", h=30),
    "SVT1":             dict(file="SVT1", h=42),
    "The CW":           dict(file="TheCW", h=39, color=True),
    "TV4":              dict(file="TV4", h=58),
    "TVING":            dict(file="TVING", h=31, color=True),
    "Viaplay":          dict(file="Viaplay", h=58, color=True),
    "Youku":            dict(file="Youku", h=31, color=True),
}

# One show's logo in its own colours, usually its poster title's. Per network,
# show: how, saved as Tinted/<file>_<show>.png. How is one of:
#   "#hex"                      the logo in that colour
#   "svg"                       the fill of Source/<file>_<show>.svg (the HBO ones)
#   dict(...)                   one of fill, gradient or mottle, plus any effects:
#     fill="#hex"                 one colour
#     gradient=["#hex", ...]      colours spread evenly across the logo, along
#     angle=45                      0 left to right, 90 top to bottom, 45 top-left to bottom-right
#     mottle=["#hex", ...]        dark to light, in random blotches (gold leaf, metal)
#     keep_color=True             from the colour logo: only its white parts get the fill
#     tile=True                   the logo's box filled in, the letters in it white
#     bevel=["#hex", "#hex"]      edges facing the top-left in the second colour, the
#                                 others in the first, like lit metal
#     outline="#hex"              a thin rim round the edge
#     brush=True                  dry-brush streaks and frayed edges (paint)
#     chalk=True                  worn, speckled edges (chalk, dry brush)
#     cracks=[(x, y, r), ...]     thin cuts along circles: centre and radius in logo
#                                 heights, from the logo's top-left corner
# The random parts (mottle, brush, chalk) come out the same on every run.
TINTS = {
    "AMC": {
        "breakingbad": dict(gradient=["#105036", "#06612b"], angle=45, tile=True, outline="#062a0c"),
    },
    "Apple TV": {
        "widowsbay": "#9b1200",
    },
    "BritBox": {
        "whydidnttheyaskevans": dict(gradient=["#cd6502", "#dc8402", "#f6be15", "#fad322", "#fbd423"], angle=45),
    },
    "FX": {
        "thebear": "#fcf6c9",
        "fargo": "#bd1f1c",
        "grotesquerie": dict(fill="#af92fe", chalk=True),
    },
    "HBO": {
        "chernobyl": "svg",
        "euphoria": "svg",
        "succession": "svg",
        "thelastofus": "svg",
        "houseofthedragon": dict(mottle=["#5e2a12", "#8f4c2b", "#b8703f"], bevel=["#1e0d04", "#ffe0c4"], outline="#1e0d04"),
    },
    "HBO Max": {
        "peacemaker": "#fcde15",
        "fullcircle": dict(fill="#ffeb2c", cracks=[(2.2, 2.4, 2.6), (-1.5, 2.0, 2.3), (1.3, -1.2, 1.9)]),
    },
    "Hulu": {
        "shogun": dict(mottle=["#bc933c", "#d8b059", "#e6bf68", "#f2cb75", "#ffdf95"], brush=True),
    },
    "Paramount Plus": {
        "yellowjackets": "#f0d838",
    },
    "Peacock": {
        "crystallake": dict(fill="#d71e00", keep_color=True),
    },
    "Showtime": {
        "dexter": "#a61e22",
    },
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


# ---------- tint effects, on float arrays: colour h x w x 3 and alpha h x w, 0..1 ----------

def box(a, r, axis):
    """Mean over 2r+1 pixels along one axis, edges clamped."""
    r = int(round(r))
    if r < 1:
        return a
    pad = [(0, 0), (0, 0)]
    pad[axis] = (r + 1, r)
    c = np.pad(a, pad, mode="edge").cumsum(axis)
    n = a.shape[axis]
    return (np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis) - np.take(c, np.arange(n), axis)) / (2 * r + 1)


def blur(a, rx, ry=None):
    """Close to a Gaussian blur (three box blurs); ry for a different height."""
    ry = rx if ry is None else ry
    for _ in range(3):
        a = box(box(a, rx, 1), ry, 0)
    return a


def noise(shape, seed, rx, ry=None):
    """Random blotches about rx (wide) by ry (high) pixels, 0..1."""
    n = blur(np.random.default_rng(seed).random(shape), rx, ry)
    lo, hi = np.percentile(n, (2, 98))
    return np.clip((n - lo) / max(hi - lo, 1e-9), 0, 1)


def ramp(t, stops):
    """t (0..1) through the colours, spread evenly."""
    cols = np.array([hexrgb(s) for s in stops], np.float64) / 255
    pos = np.linspace(0, 1, len(cols))
    return np.stack([np.interp(t, pos, cols[:, i]) for i in range(3)], -1)


def gradient(shape, stops, angle):
    """The colours along angle, from one side of the logo to the other."""
    h, w = shape
    rad = np.radians(angle)
    yy, xx = np.mgrid[0:h, 0:w]
    p = xx * np.cos(rad) + yy * np.sin(rad)
    return ramp((p - p.min()) / max(p.max() - p.min(), 1e-9), stops)


def mottle(shape, stops, seed, k):
    """Big and small blotches, through the colours."""
    t = 0.55 * noise(shape, seed, 1.6 * k) + 0.45 * noise(shape, seed + 1, 0.5 * k)
    lo, hi = np.percentile(t, (3, 97))
    return ramp(np.clip((t - lo) / (hi - lo), 0, 1), stops)


def tile(rgb, a):
    """AMC's frame filled in: the whole box gets the colour, what's inside the frame is white."""
    empty = Image.fromarray(np.where(a > 0.5, 0, 255).astype(np.uint8))
    framed = Image.new("L", (empty.width + 2, empty.height + 2), 255)
    framed.paste(empty, (1, 1))
    ImageDraw.floodfill(framed, (0, 0), 128)                 # everything round the outside
    outside = np.asarray(framed)[1:-1, 1:-1] == 128
    ys, xs = np.nonzero(~outside & (a <= 0.5))             # the space inside the frame
    if not len(ys):
        raise SystemExit("tile: the logo has no frame round it, like AMC's")
    m = 3                                                  # keep the frame's own inner edge out
    inner = np.zeros_like(a)
    inner[ys.min() + m:ys.max() - m + 1, xs.min() + m:xs.max() - m + 1] = 1
    letters = a * inner
    rgb = rgb + (1 - rgb) * letters[..., None]
    return rgb, np.maximum(a, (~outside).astype(a.dtype))


def bevel(rgb, a, k, dark, light):
    """Edges facing the top-left lit, the others in shadow, about 2 poster px wide."""
    hgt = blur(a, k)
    gy, gx = np.gradient(hgt)
    s = np.clip((gx + gy) * 3.2 * k, -1, 1)[..., None]
    return np.where(s > 0, rgb + (light - rgb) * s, rgb + (dark - rgb) * -s)


def outline(rgb, a, k, col):
    """A rim about 1 poster px wide in col."""
    w = np.clip((1 - blur(a, 0.5 * k)) * 2, 0, 1)[..., None]
    return rgb + (col - rgb) * w


def brush(rgb, a, k, seed):
    """Dry brush: faint streaks down the paint and slightly frayed edges."""
    streak = noise(a.shape, seed, 0.3 * k, 3 * k)
    rgb = rgb * (0.92 + 0.16 * streak)[..., None]
    depth = blur(a, 0.5 * k)
    keep = np.clip((depth - 0.5 + (streak - 0.5) * 0.4) * 8, 0, 1)
    return rgb, a * np.where(depth > 0.9, 1, keep)


def chalk(a, k, seed):
    """Worn, scratchy edges and a few scratches through the middle."""
    scratch = noise(a.shape, seed, 0.25 * k, 2.5 * k)
    wear = 0.5 * noise(a.shape, seed + 1, 0.3 * k) + 0.5 * scratch
    depth = blur(a, 1.2 * k)
    gone = np.clip((0.22 + 0.6 * (1 - depth) - wear) * 8, 0, 1)
    return a * (1 - gone)


def cracks(a, arcs, k):
    """Thin cuts along circles, about 1 poster px wide."""
    h = a.shape[0]
    im = Image.new("L", (a.shape[1], h), 0)
    draw = ImageDraw.Draw(im)
    for x, y, r in arcs:
        cx, cy, rr = x * h, y * h, r * h
        draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=255, width=max(1, round(k)))
    return a * (1 - np.asarray(im, np.float64) / 255)


def tint(how, master, color_master, size, seed):
    """The logo in one show's colours and effects, scaled down to size."""
    base = color_master if how.get("keep_color") else master
    arr = np.asarray(base.convert("RGBA"), np.float64) / 255
    a = arr[..., 3]
    k = a.shape[0] / size[1]                 # pixels in the drawing per poster pixel
    if how.get("keep_color"):
        rgb = np.asarray(neutral(base, hexrgb(how["fill"])), np.float64)[..., :3] / 255
    elif "gradient" in how:
        rgb = gradient(a.shape, how["gradient"], how.get("angle", 0))
    elif "mottle" in how:
        rgb = mottle(a.shape, how["mottle"], seed, k)
    else:
        rgb = np.ones(a.shape + (3,)) * np.array(hexrgb(how["fill"])) / 255
    if how.get("tile"):
        rgb, a = tile(rgb, a)
    if "bevel" in how:
        rgb = bevel(rgb, a, k, *(np.array(hexrgb(c)) / 255 for c in how["bevel"]))
    if "outline" in how:
        rgb = outline(rgb, a, k, np.array(hexrgb(how["outline"])) / 255)
    if how.get("brush"):
        rgb, a = brush(rgb, a, k, seed)
    if how.get("chalk"):
        a = chalk(a, k, seed)
    if "cracks" in how:
        a = cracks(a, how["cracks"], k)
    out = np.dstack([np.clip(rgb, 0, 1), np.clip(a, 0, 1)])
    return shrink(Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA"), size)


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
    c = None
    if color is True:
        c = render(source(folder, f + "_Color"), h * SS)
        label["Color"] = shrink(c, (w, h))
        if spec.get("color_dark"):
            label["ColorDark"] = shrink(neutral(c, BLACK), (w, h))
    elif color:
        label["Color"] = fill(label["White"], hexrgb(color))
    for name, im in label.items():
        save(im, folder, "Label", f"{f}_{name}.png")

    tints = TINTS.get(folder, {})
    for show, how in tints.items():
        if how == "svg":
            im = svg_fill(source(folder, f"{f}_{show}"), label["White"])
        elif isinstance(how, dict):
            if how.get("keep_color") and c is None:
                raise SystemExit(f"{folder}: keep_color needs Source/{f}_Color")
            im = tint(how, master, c, (w, h), zlib.crc32(show.encode()))
        else:
            im = fill(label["White"], hexrgb(how))
        save(im, folder, "Tinted", f"{f}_{show}.png")

    tinted = f", tints: {', '.join(tints)}" if tints else ""
    print(f"{folder:<17} {w}x{h:<4} {', '.join(label)}{tinted}")


if __name__ == "__main__":
    names = sys.argv[1:] or list(LOGOS)
    unknown = [n for n in names if n not in LOGOS]
    if unknown:
        raise SystemExit(f"unknown network: {', '.join(unknown)}")
    for name in names:
        build(name, LOGOS[name])
