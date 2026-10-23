"""Trace the original lettering and car into clean vector outlines.

Keeps the exact shapes of the original logo (car outline and swooshes, DOUBLE
MINT brush type and DETAILING) while smoothing away JPEG noise and brush grain.

Requires: pip install numpy pillow scipy potracer
Run: python3 trace_original.py   (reads original.jpg, writes traced.json)
"""
import json
import os
import numpy as np
import potrace
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "original.jpg")
OUT = os.path.join(HERE, "traced.json")

X0, Y0, X1, Y1 = 140, 40, 1080, 360   # logo area in original pixels
SCALE = 8                             # trace at 8x for smooth curves


def load():
    im = Image.open(SRC).convert("RGB").crop((X0, Y0, X1, Y1))
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
    a = np.asarray(im).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    white = np.clip((np.minimum(np.minimum(r, g), b) - 60) / 140, 0, 1)
    green = np.clip((g - np.maximum(r, b) - 40) / 100, 0, 1)
    return white, green


def solid(score, blur, close):
    """Soft colour score -> clean filled mask (fills brush streaks and specks)."""
    m = ndimage.gaussian_filter(score, blur) > 0.5
    if close:
        m = ndimage.binary_closing(m, iterations=close)
        holes, _ = ndimage.label(~m)
        sizes = np.bincount(holes.ravel())
        small = sizes < (12 * SCALE) ** 2   # streaks, not letter counters
        small[0] = False
        m |= small[holes]
    return m


def keep(mask, test):
    """Keep connected components whose bounding box passes test(y0, y1, x0, x1)."""
    lab, n = ndimage.label(mask)
    out = np.zeros_like(mask)
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        y0, y1 = (sl[0].start / SCALE + Y0, sl[0].stop / SCALE + Y0)
        x0, x1 = (sl[1].start / SCALE + X0, sl[1].stop / SCALE + X0)
        if test(y0, y1, x0, x1):
            out[sl] |= lab[sl] == i
    return out


def trace(mask, alphamax):
    # potracer treats False as ink, hence ~mask
    curves = potrace.Bitmap(~mask).trace(turdsize=40 * SCALE, alphamax=alphamax,
                                         opttolerance=0.4)
    k = 1 / SCALE

    def p(pt):
        return f"{pt.x * k + X0:.2f} {pt.y * k + Y0:.2f}"

    d = []
    for c in curves:
        d.append(f"M{p(c.start_point)}")
        for s in c.segments:
            if s.is_corner:
                d.append(f"L{p(s.c)}L{p(s.end_point)}")
            else:
                d.append(f"C{p(s.c1)} {p(s.c2)} {p(s.end_point)}")
        d.append("Z")
    return "".join(d)


def bounds(mask):
    ys, xs = np.nonzero(mask)
    return [xs.min() / SCALE + X0, ys.min() / SCALE + Y0,
            (xs.max() + 1) / SCALE + X0, (ys.max() + 1) / SCALE + Y0]


if __name__ == "__main__":
    white, green = load()
    big = lambda y0, y1, x0, x1: y1 > 200 and y0 < 300   # wordmark, not car
    small = lambda y0, y1, x0, x1: y0 > 300 and 340 < x0 and x1 < 880
    rule = lambda y0, y1, x0, x1: y0 > 300 and (x1 < 345 or x0 > 870)
    # car: above the wordmark, right of the ceiling light, minus the sparkles
    body = lambda y0, y1, x0, x1: y1 < 180 and x0 > 215 and not (x0 > 750 and y1 < 112)

    double = keep(solid(white, 1.2 * SCALE, 2 * SCALE), big)
    mint = keep(solid(green, 1.2 * SCALE, 2 * SCALE), big)
    detailing = keep(solid(white, 0.35 * SCALE, 0), small)
    rules = keep(solid(green, 0.5 * SCALE, 0), rule)
    car_white = keep(solid(white, 0.7 * SCALE, SCALE), body)
    car_green = keep(solid(green, 0.7 * SCALE, SCALE), body)

    lab, _ = ndimage.label(rules)
    rule_boxes = sorted(bounds(lab == i) for i in range(1, lab.max() + 1))
    data = {
        "car_white": trace(car_white, 1.1),
        "car_green": trace(car_green, 1.1),
        "double": trace(double, 1.0),
        "mint": trace(mint, 1.0),
        "detailing": trace(detailing, 0.55),
        "double_box": bounds(double),
        "mint_box": bounds(mint),
        "detailing_box": bounds(detailing),
        "rules": rule_boxes,
    }
    with open(OUT, "w") as fh:
        json.dump(data, fh)
    print("wrote", OUT, {k: v for k, v in data.items() if "box" in k or k == "rules"})
