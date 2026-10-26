#!/usr/bin/env python3
"""Make the Oscars Best Picture badges, one per ceremony year, from the parts in Source/.

The badge is the gold Academy triangle with the Oscar cut out of it, and under it
the year, a thin divider and BEST PICTURE / WINNER, as on the Best Picture posters
the parts were taken from. Every image is Kometa's poster size, 1000x1500, with the
badge at the top in the middle.

  Source/triangle.png, rule.png, text.png, digit_0-9.png   the parts' shapes (alpha)
  Source/layout.json                                        their places and colours

  BestPicture/<year>_Gold.png   gold year and text, for most posters
  BestPicture/<year>_Dark.png   darker gold year and text, for light posters

The divider always sits under the middle of the triangle, with the year to its left
and BEST PICTURE / WINNER to its right. (The posters centre the whole line instead,
so their divider moves with the year's width.) The year is the ceremony's, usually
the year after the film's. Years the posters show keep those posters' exact digit
spacing; others are spaced from them.

usage: python3 build.py [year ...]        no years = 1929 to 2035; needs Pillow and numpy
"""
import json
import os
import sys

import numpy as np
from PIL import Image

VERSION = "1.1.0"

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
OUT = os.path.join(HERE, "BestPicture")
BIG = (1500, 2250)                        # the posters' size, where the parts were measured
CANVAS = (1000, 1500)                     # Kometa's poster size
YEARS = range(1929, 2036)

LAY = json.load(open(os.path.join(SRC, "layout.json")))
part = lambda name: np.asarray(Image.open(os.path.join(SRC, name + ".png")), np.float64) / 255


def centre(al):
    """Where a shape's middle is, across, in its own pixels (pixel i spans i to i+1)."""
    w = al.sum(0)
    return (w * (np.arange(len(w)) + 0.5)).sum() / w.sum()


AXIS = LAY["triangle"]["x"] + centre(part("triangle"))     # the triangle's middle, 750.5
DIV = int(AXIS - 0.5)                                         # the divider's place for the year and text


def positions(year):
    """Core-left x of each digit, the divider's x and the text's x, at the posters' size.

    The divider is always at DIV, under the triangle; the year ends the same distance
    before it as on the posters, and the text starts the same distance after it."""
    y = str(year)
    if y in LAY["seen"]:                  # a year on the posters: its digits spaced exactly as there
        s = LAY["seen"][y]
        xs, div = s["digits"], s["divider"]
    else:
        xs = [0.0]
        for i in range(3):
            k = y[i] + y[i + 1]
            xs.append(xs[-1] + LAY["pairs"].get(k, LAY["A"][y[i]] + LAY["L"][y[i + 1]]))
        div = xs[3] + LAY["core_width"][y[3]] + LAY["last_digit_to_divider"][y[3]]
    shift = DIV - div
    return [round(v + shift) for v in xs], DIV, DIV + LAY["divider_to_text"]


def badge(year, gold):
    """The badge as RGBA at the posters' size."""
    rgb = np.zeros((BIG[1], BIG[0], 3))
    alpha = np.zeros((BIG[1], BIG[0]))

    def paste(al, x, y, colour):
        h, w = al.shape
        alpha[y:y + h, x:x + w] = np.maximum(alpha[y:y + h, x:x + w], al)
        rgb[y:y + h, x:x + w] = np.where(al[..., None] > 0, colour, rgb[y:y + h, x:x + w])

    t = LAY["triangle"]
    tri = part("triangle")
    rows = np.arange(tri.shape[0])[:, None, None]
    colour = np.array(t["colour_top"]) + rows * np.array(t["colour_per_row"])   # lighter at the top
    paste(tri, t["x"], t["y"], np.broadcast_to(colour, tri.shape + (3,)))

    g = np.array(LAY["gold"][gold], np.float64)
    xs, div, text = positions(year)
    for d, x in zip(str(year), xs):
        paste(part(f"digit_{d}"), x - LAY["digit_core_offset"], LAY["digit_y"], g)
    rule = part("rule")                   # moved by a part of a pixel so its middle is on the triangle's
    x = AXIS - centre(rule)
    frac = x - np.floor(x)
    moved = rule * (1 - frac)
    moved[:, 1:] += rule[:, :-1] * frac
    paste(moved, int(np.floor(x)), LAY["rule_y"], g)
    paste(part("text"), text + LAY["text_offset"], LAY["text_y"], g)
    return np.dstack([rgb, alpha * 255])


def save(year, gold):
    im = Image.fromarray(np.clip(badge(year, gold) + 0.5, 0, 255).astype(np.uint8), "RGBA")
    im = im.convert("RGBa").resize(CANVAS, Image.LANCZOS).convert("RGBA")   # premultiplied, clean edges
    im.save(os.path.join(OUT, f"{year}_{gold}.png"), optimize=True)


if __name__ == "__main__":
    years = [int(y) for y in sys.argv[1:]] or list(YEARS)
    os.makedirs(OUT, exist_ok=True)
    for year in years:
        for gold in LAY["gold"]:
            save(year, gold)
    print(f"{len(years)} years, {len(years) * len(LAY['gold'])} images in {OUT}")
