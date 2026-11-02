#!/usr/bin/env python3
"""Make the overlay labels: a coloured pill with the word in letter-spaced
capitals, Montserrat ExtraBold (Source/, under the SIL Open Font License in
Source/OFL.txt). One folder per size, in percent of the first pill, which was
32px high with 15px capitals on a poster:

  150/<Name>.png    the pill 48px high with 22.5px capitals
  160/<Name>.png    a bit bigger, the most that fits under a studio logo

Posters are 1000x1500. Their labels (LABELS) sit centred at the bottom with
the pill's middle at y 1472, halfway between the bottom of the tallest studio
logo (y 1445) and the poster's edge, so they never cover a logo. TOP, with a
flame after the word, sits in the top left corner, 43px in, like the network
logos on shows. The flame is Source/fire.svg from Bootstrap Icons (MIT
licence in Source/LICENSE-fire.txt). Episode title cards are 1920x1080 and
their badges (EPISODES) sit centred at the bottom, everything 1.92x bigger so
they look the same size as on a poster.

White letters have a soft shadow under them so they stand out from the pill,
and the pill has one so it stands out from the poster. Each label is drawn
4x bigger and then scaled down.

usage: python3 build.py [size ...]          needs Pillow and cairosvg
"""
import io
import math
import os
import sys

import cairosvg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

VERSION = "1.2.0"

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "Source", "Montserrat[wght].ttf")
FLAME = os.path.join(HERE, "Source", "fire.svg")
WEIGHT = 800                     # ExtraBold
SS = 4                           # drawn this many times bigger, then scaled down
SIZES = (150, 160)
WHITE = (255, 255, 255)

POSTER = (1000, 1500)
POSTER_MID = 1472                # the bottom pill's middle
CORNER = 43                      # the top left pill's corner
CARD = (1920, 1080)
CARD_SCALE = CARD[0] / POSTER[0]  # a title card is 1.92x a poster's width
CARD_MID = CARD[1] - (POSTER[1] - POSTER_MID) * CARD_SCALE

# file name: word, pill colour (the colours Entree3k's labels used)
LABELS = {
    "NewSeason":     ("NEW SEASON",     (237, 4, 10)),
    "RecentlyAdded": ("RECENTLY ADDED", (237, 4, 10)),
    "Airing":        ("AIRING",         (37, 99, 255)),
    "Returning":     ("RETURNING",      (0, 136, 16)),
    "Ended":         ("ENDED",          (96, 96, 96)),
    "Canceled":      ("CANCELED",       (237, 4, 10)),
}
# the top left one, with the flame: file name, word, pill colour (the old TOP
# badge's yellow), letter colour (dark, white is hard to read on yellow)
TOP = ("Trending", "TOP", (255, 187, 16), (24, 24, 24))
EPISODES = {
    "SeriesPremiere":  ("SERIES PREMIERE",   (37, 99, 255)),
    "SeasonPremiere":  ("SEASON PREMIERE",   (22, 163, 74)),
    "MidSeasonFinale": ("MID-SEASON FINALE", (234, 115, 22)),
    "SeasonFinale":    ("SEASON FINALE",     (237, 4, 10)),
    "SeriesFinale":    ("SERIES FINALE",     (147, 51, 234)),
}

# at 100% on a poster, in px
HEIGHT, CAP, PAD, TRACK = 32, 15, 22, 0.14      # pill height, capital height, side padding, spacing (x CAP)
FLAME_HEIGHT, FLAME_GAP = 1.45, 0.45             # the flame's height and its gap after the word (x CAP)
BLUR, DROP, SHADE = 6, 2, 0.55                   # the pill's shadow: blur, offset down, darkness
TEXT_BLUR, TEXT_DROP, TEXT_SHADE = 1.2, 1.2, 0.7  # the shadow under white letters


def font(cap):
    """Montserrat ExtraBold at the size that makes its capitals cap px high."""
    f = ImageFont.truetype(FONT, 400)
    f.set_variation_by_axes([WEIGHT])
    box = f.getbbox("H")
    f = ImageFont.truetype(FONT, round(400 * cap / (box[3] - box[1])))
    f.set_variation_by_axes([WEIGHT])
    return f


def word_image(word, cap):
    """The word, letter-spaced, as a mask cropped to its ink."""
    f = font(cap)
    gap = TRACK * cap
    width = sum(f.getlength(c) for c in word) + gap * (len(word) - 1)
    im = Image.new("L", (int(width) + 80, int(cap * 4)), 0)
    draw = ImageDraw.Draw(im)
    x = 40.0
    for c in word:
        draw.text((x, cap * 1.5), c, font=f, fill=255)
        x += f.getlength(c) + gap
    return im.crop(im.getbbox())


def flame_image(height):
    """The flame as a mask, height px high."""
    svg = open(FLAME, "rb").read()
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg, output_height=round(height * 2)))).getchannel("A")
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * height / im.height), round(height)), Image.LANCZOS)


def content(word, cap, flame):
    """The word, with the flame after it centred on the capitals, as one mask."""
    text = word_image(word, cap)
    if not flame:
        return text
    fire = flame_image(FLAME_HEIGHT * cap)
    gap = round(FLAME_GAP * cap)
    h = max(text.height, fire.height)
    im = Image.new("L", (text.width + gap + fire.width, h), 0)
    im.paste(text, (0, (h - text.height) // 2))
    im.paste(fire, (text.width + gap, (h - fire.height) // 2))
    return im


def soft(mask, size, offset, blur, shade):
    """A black shadow of mask, blurred and moved down."""
    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    spot = Image.new("L", size, 0)
    spot.paste(mask, (offset[0], offset[1]))
    shadow.putalpha(spot.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: round(v * shade)))
    return shadow


def pill(word, fill, ink, scale, flame=False):
    """The pill with its shadows, in a box with room for the shadow all round.
    Returns the image and the pill's size and top left corner inside it, in px."""
    text = content(word, CAP * scale * SS, flame)
    ph, pad = round(HEIGHT * scale * SS), round(PAD * scale * SS)
    pw = text.width + 2 * pad
    room = math.ceil((3 * BLUR + DROP) * scale) * SS
    W, H = math.ceil(pw / SS) * SS + 2 * room, math.ceil(ph / SS) * SS + 2 * room
    x0, y0 = room, room
    shape = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shape).rounded_rectangle((x0, y0, x0 + pw - 1, y0 + ph - 1), radius=ph // 2, fill=255)
    big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    big.alpha_composite(soft(shape, (W, H), (0, 0), BLUR * scale * SS, SHADE), (0, round(DROP * scale * SS)))
    body = Image.new("RGBA", (W, H), fill + (255,))
    body.putalpha(shape)
    big.alpha_composite(body)
    tx, ty = x0 + (pw - text.width) // 2, y0 + (ph - text.height) // 2
    if ink == WHITE:             # dark letters don't need one
        big.alpha_composite(soft(text, (W, H), (tx, ty), TEXT_BLUR * scale * SS, TEXT_SHADE), (0, round(TEXT_DROP * scale * SS)))
    letters = Image.new("RGBA", text.size, ink + (255,))
    letters.putalpha(text)
    big.alpha_composite(letters, (tx, ty))
    small = big.convert("RGBa").resize((W // SS, H // SS), Image.LANCZOS).convert("RGBA")
    return small, (pw / SS, ph / SS), (room // SS, room // SS)


def overlay(canvas, word, fill, ink, scale, where, flame=False):
    """A full-size overlay with the pill centred on (x, y), or with its corner at
    (x, y) when where[0] is "corner"."""
    im, (pw, ph), (ox, oy) = pill(word, fill, ink, scale, flame)
    if where[0] == "corner":
        x, y = where[1], where[2]
    else:
        x, y = where[1] - pw / 2, where[2] - ph / 2
    out = Image.new("RGBA", canvas, (0, 0, 0, 0))
    out.alpha_composite(im, (round(x - ox), round(y - oy)))
    return out


def build(size):
    folder = os.path.join(HERE, str(size))
    os.makedirs(folder, exist_ok=True)
    k = size / 100
    made = {}
    for name, (word, fill) in LABELS.items():
        made[name] = overlay(POSTER, word, fill, WHITE, k, ("middle", POSTER[0] / 2, POSTER_MID))
    name, word, fill, ink = TOP
    made[name] = overlay(POSTER, word, fill, ink, k, ("corner", CORNER, CORNER), flame=True)
    for name, (word, fill) in EPISODES.items():
        made[name] = overlay(CARD, word, fill, WHITE, k * CARD_SCALE, ("middle", CARD[0] / 2, CARD_MID))
    for name, im in made.items():
        im.save(os.path.join(folder, name + ".png"), optimize=True)
        box = im.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox()
        print(f"{size}/{name:<16} {im.size[0]}x{im.size[1]}  pill {box[2] - box[0]}x{box[3] - box[1]} at {box[0]},{box[1]}")


if __name__ == "__main__":
    for size in [int(s) for s in sys.argv[1:]] or list(SIZES):
        build(size)
