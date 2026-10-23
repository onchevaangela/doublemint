"""Generate the classic Double Mint Detailing logo (car swoosh + brush wordmark).

A clean vector redraw of the original artwork: same layout, car silhouette,
sparkles and text, with smooth tapered strokes and solid fills.

Requires: pip install fonttools cairosvg
Fonts (OFL) are in ./fonts: Knewave (wordmark), Montserrat Bold (DETAILING).
Text is converted to outlines so the SVGs render identically everywhere.
Run: python3 classic.py   (writes ../logo/classic/*.svg and *.png)
"""
import math
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
BRUSH = os.path.join(HERE, "fonts", "knewave-latin-400-normal.woff")
SANS = os.path.join(HERE, "fonts", "montserrat-latin-700-normal.woff")
OUT = os.path.join(HERE, "..", "logo", "classic")

MINT = "#2EEB78"        # main green, sampled from the original
MINT_HI = "#6BF7A0"     # top of the green gradient
MINT_LO = "#16C95E"     # bottom of the green gradient
FOREST = "#14924A"      # green on light backgrounds
INK = "#0B0F0D"         # near-black
WHITE = "#FFFFFF"

THEMES = {
    # name: background, white parts, green parts (None = mint gradient)
    "dark": dict(bg=INK, fg=WHITE, accent=None),
    "transparent": dict(bg=None, fg=WHITE, accent=None),
    "light": dict(bg=None, fg=INK, accent=FOREST),
    "white": dict(bg=None, fg=WHITE, accent=WHITE),
    "black": dict(bg=None, fg=INK, accent=INK),
}


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- strokes
def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def tapered(p0, p1, p2, p3, profile, n=90):
    """Filled brush stroke along a cubic, width given by profile(t)."""
    pts = [bezier(p0, p1, p2, p3, i / n) for i in range(n + 1)]
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = profile(i / n) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    ring = left + right[::-1]
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in ring) + "Z"


def swell(peak, at=0.5, start=0.0, end=0.0, power=1.0):
    """Width profile rising from `start` to `peak` at t=`at`, falling to `end`."""
    def p(t):
        if t <= at:
            s = math.sin(t / at * math.pi / 2) ** power
            return start + (peak - start) * s
        s = math.sin((1 - t) / (1 - at) * math.pi / 2) ** power
        return end + (peak - end) * s
    return p


def sparkle(cx, cy, rx, ry, k=0.14):
    """Four-point star with concave sides."""
    qx, qy = rx * k, ry * k
    return (f"M{f(cx)} {f(cy - ry)}"
            f"Q{f(cx + qx)} {f(cy - qy)} {f(cx + rx)} {f(cy)}"
            f"Q{f(cx + qx)} {f(cy + qy)} {f(cx)} {f(cy + ry)}"
            f"Q{f(cx - qx)} {f(cy + qy)} {f(cx - rx)} {f(cy)}"
            f"Q{f(cx - qx)} {f(cy - qy)} {f(cx)} {f(cy - ry)}Z")


def car():
    """Return (white_paths, green_paths) for the car silhouette and sparkles."""
    white = [
        # roof: thin tail at the back, full in the middle, fine at the nose
        tapered((404, 113), (498, 60), (704, 50), (808, 119),
                swell(13, at=0.42, start=1.5, end=4, power=0.8)),
        # sill / window line back from the nose
        tapered((808, 119), (722, 145), (566, 137), (438, 115),
                swell(11, at=0.45, start=4, end=1, power=0.8)),
    ]
    green = [
        # window accent (chevron pointing to the nose)
        tapered((572, 80), (624, 78), (690, 92), (724, 110),
                swell(7, at=0.85, start=0.6, end=5.5)),
        tapered((724, 110), (700, 118), (672, 122), (630, 123),
                swell(5.5, at=0.15, start=5.5, end=0.6)),
        # body swoosh, rear to door
        tapered((228, 163), (312, 127), (476, 116), (664, 150),
                swell(20, at=0.38, start=0.4, end=0.8, power=0.9)),
        # fine streak under the body swoosh
        tapered((470, 141), (540, 148), (606, 152), (654, 153),
                swell(4, at=0.5, start=0.3, end=0.3)),
        # body swoosh, door to front wheel arch
        tapered((660, 159), (744, 122), (868, 117), (946, 167),
                swell(17, at=0.45, start=0.6, end=0.4, power=0.9)),
        # sparkles
        sparkle(812, 70, 23, 31),
        sparkle(853, 96, 11, 14),
        sparkle(782, 59, 7.5, 10),
        sparkle(768, 82, 6.5, 8.5),
    ]
    return white, green


# ------------------------------------------------------------------- text
class Font:
    def __init__(self, path):
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet()
        self.cmap = self.tt.getBestCmap()
        self.upm = self.tt["head"].unitsPerEm

    def glyph(self, ch):
        return self.gs[self.cmap[ord(ch)]]

    def run(self, text, sx, sy, x, y, tracking=0.0):
        """Outline `text` at (x, baseline y); returns (path d, bounds)."""
        pen, bp, cx = SVGPathPen(self.gs), BoundsPen(self.gs), 0.0
        for ch in text:
            g = self.glyph(ch)
            m = (sx, 0, 0, -sy, x + cx, y)
            g.draw(TransformPen(pen, m))
            g.draw(TransformPen(bp, m))
            cx += g.width * sx + tracking
        return pen.getCommands(), bp.bounds

    def cap_height(self):
        b = BoundsPen(self.gs)
        self.glyph("H").draw(b)
        return b.bounds[3]


def wordmark():
    """DOUBLE / MINT fitted to the original's box, plus DETAILING and rules."""
    brush = Font(BRUSH)
    left, right, base, cap = 192, 1048, 300, 116  # original placement
    sy = cap / brush.cap_height()
    gap = 34
    # measure at unit x-scale, then stretch horizontally to fill the box
    _, b1 = brush.run("DOUBLE", 1, sy, 0, base)
    _, b2 = brush.run("MINT", 1, sy, 0, base)
    sx = (right - left - gap) / ((b1[2] - b1[0]) + (b2[2] - b2[0]))
    sx = min(sx, sy * 1.12)  # keep letter shapes close to the font's own
    w1 = (b1[2] - b1[0]) * sx
    w2 = (b2[2] - b2[0]) * sx
    total = w1 + gap + w2
    x0 = (left + right - total) / 2
    double, db = brush.run("DOUBLE", sx, sy, x0 - b1[0] * sx, base)
    mint, mb = brush.run("MINT", sx, sy, x0 + w1 + gap - b2[0] * sx, base)

    sans = Font(SANS)
    dcap = 30
    ds = dcap / sans.cap_height()
    track = 15.5
    _, tb = sans.run("DETAILING", ds, ds, 0, 0, track)
    tw = tb[2] - tb[0]
    mid = (db[0] + mb[2]) / 2
    tx = mid - tw / 2 - tb[0]
    tbase = 344
    detailing, tbb = sans.run("DETAILING", ds, ds, tx, tbase, track)

    ry, pad = tbase - dcap / 2, 26
    rules = [(db[0] - 6, tbb[0] - pad), (tbb[2] + pad, mb[2] + 2)]
    rule_paths = [tapered((a, ry), (a + (b - a) / 3, ry), (b - (b - a) / 3, ry), (b, ry),
                          (lambda t: 4.2 * min(1, t / 0.06)) if i == 0
                          else (lambda t: 4.2 * min(1, (1 - t) / 0.06)), n=24)
                  for i, (a, b) in enumerate(rules)]
    box = (min(db[0], rules[0][0]), max(mb[2], rules[1][1]), tbb[3])
    return double, mint, detailing, rule_paths, box


# -------------------------------------------------------------------- svg
def build(theme):
    t = THEMES[theme]
    white, green = car()
    double, mint, detailing, rules, (x_min, x_max, y_max) = wordmark()
    pad = 40
    vx, vy = x_min - pad, 50 - pad - 12
    vw, vh = x_max - x_min + 2 * pad, y_max - vy + pad
    accent = t["accent"] or "url(#mint)"

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(vx)} {f(vy)} {f(vw)} {f(vh)}" '
           f'width="{round(vw)}" height="{round(vh)}">',
           "<title>Double Mint Detailing</title>"]
    if t["accent"] is None:
        out.append(
            f'<defs><linearGradient id="mint" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="310">'
            f'<stop offset="0" stop-color="{MINT_HI}"/><stop offset=".45" stop-color="{MINT}"/>'
            f'<stop offset="1" stop-color="{MINT_LO}"/></linearGradient></defs>')
    if t["bg"]:
        out.append(f'<rect x="{f(vx)}" y="{f(vy)}" width="{f(vw)}" height="{f(vh)}" fill="{t["bg"]}"/>')
    out.append(f'<g fill="{t["fg"]}">' + "".join(f'<path d="{d}"/>' for d in white) + "</g>")
    out.append(f'<g fill="{accent}">' + "".join(f'<path d="{d}"/>' for d in green) + "</g>")
    out.append(f'<path fill="{t["fg"]}" d="{double}"/>')
    out.append(f'<path fill="{accent}" d="{mint}"/>')
    out.append(f'<g fill="{accent}">' + "".join(f'<path d="{d}"/>' for d in rules) + "</g>")
    out.append(f'<path fill="{t["fg"]}" d="{detailing}"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n", vw


if __name__ == "__main__":
    import cairosvg
    os.makedirs(OUT, exist_ok=True)
    for name in THEMES:
        svg, vw = build(name)
        base = os.path.join(OUT, f"doublemint-classic-{name}")
        with open(base + ".svg", "w") as fh:
            fh.write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=base + ".png", output_width=3000)
        print("wrote", base + ".svg/.png")
