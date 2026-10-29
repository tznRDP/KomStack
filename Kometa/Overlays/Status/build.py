#!/usr/bin/env python3
"""Make the status labels: a coloured pill with the word in white, centred at the
bottom of the poster, under the studio logo.

Every image is Kometa's poster size, 1000x1500, with the pill's middle at y 1472,
halfway between the bottom of the tallest studio logo (y 1445) and the poster's
edge, so a label never covers a logo. One folder per size:

  100/<Name>.png    a 32px high pill with 15px capitals
  115/<Name>.png    the same 15% bigger
  130/<Name>.png    and 30% bigger

The word is Montserrat ExtraBold in letter-spaced capitals (Source/, under the
SIL Open Font License in Source/OFL.txt), drawn 4x bigger and then scaled down.
The colours are the ones Entree3k's labels used.

usage: python3 build.py [size ...]          needs Pillow
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

VERSION = "1.0.0"

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "Source", "Montserrat[wght].ttf")
WEIGHT = 800                     # ExtraBold
CANVAS = (1000, 1500)
SS = 4                           # drawn this many times bigger, then scaled down
MID = 1472                       # the pill's middle
SIZES = (100, 115, 130)

# file name: the word and the pill's colour
LABELS = {
    "NewSeason":     ("NEW SEASON",     (237, 4, 10)),
    "RecentlyAdded": ("RECENTLY ADDED", (237, 4, 10)),
    "Airing":        ("AIRING",         (37, 99, 255)),
    "Returning":     ("RETURNING",      (0, 136, 16)),
    "Ended":         ("ENDED",          (96, 96, 96)),
    "Canceled":      ("CANCELED",       (237, 4, 10)),
}

# at 100%, in poster px
HEIGHT, CAP, PAD, TRACK = 32, 15, 22, 0.14      # pill height, capital height, side padding, spacing (x CAP)
BLUR, DROP, SHADE = 6, 2, 0.55                   # shadow: blur, offset down, darkness


def font(cap):
    """Montserrat ExtraBold at the size that makes its capitals cap px high."""
    f = ImageFont.truetype(FONT, 400)
    f.set_variation_by_axes([WEIGHT])
    box = f.getbbox("H")
    f = ImageFont.truetype(FONT, round(400 * cap / (box[3] - box[1])))
    f.set_variation_by_axes([WEIGHT])
    return f


def word_image(word, cap):
    """The word in white, letter-spaced, cropped to its ink."""
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


def label(word, rgb, scale):
    """The full-size overlay: the pill with its shadow and the word."""
    top = 1400                                   # only the bottom 100px are drawn
    W, H = CANVAS[0] * SS, (CANVAS[1] - top) * SS
    text = word_image(word, CAP * scale * SS)
    ph, pad = round(HEIGHT * scale * SS), round(PAD * scale * SS)
    pw = text.width + 2 * pad
    x0, y0 = (W - pw) // 2, round((MID - top) * SS - ph / 2)
    shape = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shape).rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=ph // 2, fill=255)
    strip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(shape.filter(ImageFilter.GaussianBlur(BLUR * scale * SS)).point(lambda v: round(v * SHADE)))
    strip.alpha_composite(shadow, (0, round(DROP * scale * SS)))
    pill = Image.new("RGBA", (W, H), rgb + (255,))
    pill.putalpha(shape)
    strip.alpha_composite(pill)
    white = Image.new("RGBA", text.size, (255, 255, 255, 255))
    white.putalpha(text)
    strip.alpha_composite(white, ((W - text.width) // 2, y0 + (ph - text.height) // 2))
    strip = strip.convert("RGBa").resize((CANVAS[0], CANVAS[1] - top), Image.LANCZOS).convert("RGBA")
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    out.alpha_composite(strip, (0, top))
    return out


def build(size):
    os.makedirs(os.path.join(HERE, str(size)), exist_ok=True)
    for name, (word, rgb) in LABELS.items():
        im = label(word, rgb, size / 100)
        im.save(os.path.join(HERE, str(size), name + ".png"), optimize=True)
        box = im.getchannel("A").point(lambda v: 255 if v > 64 else 0).getbbox()
        print(f"{size}/{name:<14} pill {box[2] - box[0]}x{box[3] - box[1]} at y {box[1]}")


if __name__ == "__main__":
    sizes = [int(s) for s in sys.argv[1:]] or list(SIZES)
    for size in sizes:
        build(size)
