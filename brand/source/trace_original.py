"""Trace the original lettering and car into clean vector outlines.

Keeps the exact shapes of the original logo (DOUBLE MINT brush type and
DETAILING) while smoothing away JPEG noise and brush grain. The car outline and
swooshes follow the original's path but are rebuilt as smooth tapered strokes.

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


# ------------------------------------------------------------- car strokes
# The car is rebuilt as smooth tapered strokes rather than traced outright:
# each stroke's centreline and thickness are measured column by column from
# the original, then fitted with polynomials, so the path matches the
# original but the edges are perfectly smooth.

# rough guide curve (cubic Bezier) and search half-height for each stroke,
# plus how far (as a fraction of length) each end tapers to a point
STROKES = {
    "roof":  ("white", [(404, 113), (498, 60), (704, 50), (808, 119)], 12, (0.08, 0.12)),
    "sill":  ("white", [(808, 119), (722, 145), (566, 137), (438, 115)], 9, (0.08, 0.12)),
    "acc1":  ("green", [(572, 80), (624, 78), (690, 92), (724, 110)], 6, (0.15, 0.12)),
    "acc2":  ("green", [(724, 110), (700, 118), (672, 122), (630, 123)], 5, (0.12, 0.2)),
    "left":  ("green", [(228, 163), (312, 127), (476, 116), (664, 150)], 13, (0.08, 0.08)),
    "right": ("green", [(660, 159), (744, 122), (868, 117), (946, 167)], 13, (0.08, 0.08)),
}
NOSE_STROKES = ("roof", "sill")   # these two meet at the nose tip


def bezier(p, n=400):
    t = np.linspace(0, 1, n)[:, None]
    p = np.array(p, float)
    return (1 - t)**3 * p[0] + 3 * (1 - t)**2 * t * p[1] + 3 * (1 - t) * t**2 * p[2] + t**3 * p[3]


def measure(mask, gx, gy, band):
    """Top and bottom of the ink near the guide, per original-pixel column."""
    order = np.argsort(gx)
    gx, gy = np.asarray(gx)[order], np.asarray(gy)[order]
    out = []
    for x in range(int(gx.min()) - 15, int(gx.max()) + 16):
        y = np.interp(x, gx, gy, left=np.nan, right=np.nan)
        if np.isnan(y):
            continue
        c = int((x - X0) * SCALE + SCALE / 2)
        y0, y1 = int((y - band - Y0) * SCALE), int((y + band - Y0) * SCALE)
        ys = np.nonzero(mask[max(y0, 0):y1, c])[0]
        if len(ys) >= SCALE * 0.8:
            out.append((x, (ys.min() + y0) / SCALE + Y0, (ys.max() + 1 + y0) / SCALE + Y0))
    return np.array(out).T


def fit_stroke(mask, guide, band, tip=None, deg=6):
    """Fit centreline and width polynomials (in u = 0..1 along x) to one stroke.

    Columns where it merges with a neighbouring stroke are left out; with
    `tip` the centreline is pinned to that point (the nose)."""
    p = bezier(guide)
    gx, gy = p[:, 0], p[:, 1]
    for _ in range(2):   # second pass re-measures around the fitted centreline
        x, top, bot = measure(mask, gx, gy, band)
        wid = bot - top
        ok = wid < 1.5 * np.median(wid)
        if tip is not None:
            ok &= x < tip[0] - 30
            x = np.r_[x, tip[0]]
            top, bot, wid, ok = np.r_[top, tip[1]], np.r_[bot, tip[1]], np.r_[wid, 0], np.r_[ok, False]
        u = (x - x.min()) / (x.max() - x.min())
        uu, yy, w = u[ok], ((top + bot) / 2)[ok], np.ones(ok.sum())
        if tip is not None:
            uu, yy, w = np.r_[uu, 1.0], np.r_[yy, tip[1]], np.r_[w, 60]
        cc = np.polyfit(uu, yy, deg, w=w)
        gx, gy = x, np.polyval(cc, u)
        band = wid[ok].max() / 2 + 3
    wc = np.polyfit(u[ok], wid[ok], 4)
    return x.min(), x.max(), cc, wc


def stroke_path(x0, x1, cc, wc, taper, n=160):
    u = np.linspace(0, 1, n)
    xs, ys = x0 + u * (x1 - x0), np.polyval(cc, u)
    a, b = taper
    env = np.minimum(np.clip(u / a, 0, 1), np.clip((1 - u) / b, 0, 1))
    ws = np.clip(np.polyval(wc, u), 0.6, None) * np.sin(env * np.pi / 2) ** 0.8
    dx, dy = np.gradient(xs), np.gradient(ys)
    ln = np.hypot(dx, dy)
    nx, ny = -dy / ln, dx / ln
    ring = np.r_[np.c_[xs + nx * ws / 2, ys + ny * ws / 2],
                 np.c_[xs - nx * ws / 2, ys - ny * ws / 2][::-1]]
    return "M" + "L".join(f"{px:.2f} {py:.2f}" for px, py in ring) + "Z"


def car(white, green):
    """Smooth strokes for the car; returns (white path d, green path d)."""
    masks = {"white": ndimage.gaussian_filter(white, 0.6 * SCALE) > 0.5,
             "green": ndimage.gaussian_filter(green, 0.6 * SCALE) > 0.5}
    # nose tip: rightmost white ink in a window around the car's nose
    wy0, wy1 = int((105 - Y0) * SCALE), int((135 - Y0) * SCALE)
    wx0, wx1 = int((770 - X0) * SCALE), int((830 - X0) * SCALE)
    ys, xs = np.nonzero(masks["white"][wy0:wy1, wx0:wx1])
    ys, xs = ys + wy0, xs + wx0
    nose = (xs.max() / SCALE + X0 - 1, ys[xs >= xs.max() - SCALE].mean() / SCALE + Y0)
    paths = {"white": "", "green": ""}
    for name, (colour, guide, band, taper) in STROKES.items():
        tip = nose if name in NOSE_STROKES else None
        paths[colour] += stroke_path(*fit_stroke(masks[colour], guide, band, tip), taper)
    return paths["white"], paths["green"]


if __name__ == "__main__":
    white, green = load()
    big = lambda y0, y1, x0, x1: y1 > 200 and y0 < 300   # wordmark, not car
    small = lambda y0, y1, x0, x1: y0 > 300 and 340 < x0 and x1 < 880
    rule = lambda y0, y1, x0, x1: y0 > 300 and (x1 < 345 or x0 > 870)

    double = keep(solid(white, 1.2 * SCALE, 2 * SCALE), big)
    mint = keep(solid(green, 1.2 * SCALE, 2 * SCALE), big)
    detailing = keep(solid(white, 0.35 * SCALE, 0), small)
    rules = keep(solid(green, 0.5 * SCALE, 0), rule)
    car_white, car_green = car(white, green)

    lab, _ = ndimage.label(rules)
    rule_boxes = sorted(bounds(lab == i) for i in range(1, lab.max() + 1))
    data = {
        "car_white": car_white,
        "car_green": car_green,
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
