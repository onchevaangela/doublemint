"""Generate the Doublemint Detailing logo files.

Requires: pip install fonttools, plus Inter / Inter Display (OFL, fonts.google.com/specimen/Inter).
Text is converted to outlines so the SVGs render identically everywhere.
Run: python3 build.py   (writes ../logo/svg/*.svg)
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = os.environ.get("INTER_DIR", "/usr/share/fonts/opentype/inter")
BLACK_ITALIC = f"{FONT_DIR}/InterDisplay-BlackItalic.otf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo", "svg")

# Brand palette
SPEARMINT = "#A3E05A"   # primary accent
EVERGREEN = "#2F7D4F"   # accent on light
GLOSS = "#0E1210"       # near-black
WHITE = "#FFFFFF"

THEMES = {
    # name: car body, accent (hubs, decal, speed lines), DOUBLE, MINT, bar
    "dark": dict(body=WHITE, accent=SPEARMINT, w1=WHITE, w2=SPEARMINT, bar=SPEARMINT),
    "light": dict(body=GLOSS, accent=EVERGREEN, w1=GLOSS, w2=EVERGREEN, bar=EVERGREEN),
    "white": dict(body=WHITE, accent=WHITE, w1=WHITE, w2=WHITE, bar=WHITE),
    "black": dict(body=GLOSS, accent=GLOSS, w1=GLOSS, w2=GLOSS, bar=GLOSS),
}
SKEW = -8   # extra forward lean on the type, degrees

# ---------------------------------------------------------------- mark
# A low sports coupe, side view, driving right, with speed lines behind it
# and a mint-leaf decal on the door.
BODY = ("M8,46 L6,37 L9,31 L13,28 L30,27.5 "
        "C46,26 58,20 70,13.5 C84,7 100,6 113,9.5 "
        "C123,14.5 131,19 141,24.5 "
        "C160,27 178,29.5 190,32.5 C196,34.5 198.5,39 197.5,43.5 L195,47 "
        "L172,47 A16,16 0 0 0 140,47 L60,47 A16,16 0 0 0 28,47 Z")
WINDOW = "M58,28.5 C73,17 90,11.5 106,12 C117,12.5 126,17.5 135,25.8 Z"
WHEELS = (44, 156)
WHEEL_Y = 47
SPEED = ((-30, 20, -1), (-22, 28, -5), (-36, 36, -9))   # x1, y, x2
MARK_BOX = (-37.6, 6.5, 237, 54.5)   # x, y, w, h of the visible bounds


def _leaf(cx, cy, length, width, ang):
    h = length / 2
    return (f'<path transform="translate({cx} {cy}) rotate({ang})" d="M0,{h} '
            f'C{0.62*width:.2f},{h-0.22*length:.2f} {0.40*width:.2f},{-h+0.20*length:.2f} 0,{-h} '
            f'C{-0.40*width:.2f},{-h+0.20*length:.2f} {-0.62*width:.2f},{h-0.22*length:.2f} 0,{h}Z"/>')


DECAL = (100, 36.5, 15, 8.5, 62)   # door leaf: cx, cy, length, width, angle


def _ring(cx, cy, r1, r2):
    def circ(r):
        return f"M{cx - r},{cy} a{r},{r} 0 1,0 {2*r},0 a{r},{r} 0 1,0 {-2*r},0Z"
    return circ(r1) + circ(r2)


def mark(theme, uid, x=0, y=0, scale=1.0):
    """Sports car with speed lines. Every gap is a mask, so it works on any background."""
    body, accent = THEMES[theme]["body"], THEMES[theme]["accent"]
    cx, cy, ln, wd, ang = DECAL
    halo = _leaf(cx, cy, ln + 4.5, wd + 4, ang).replace("/>", ' fill="#000"/>')
    arches = "".join(f'<circle cx="{wx}" cy="{WHEEL_Y}" r="16" fill="#000"/>' for wx in WHEELS)
    tires = "".join(f'<path d="{_ring(wx, WHEEL_Y, 13.5, 9)}" fill-rule="evenodd"/>' for wx in WHEELS)
    hubs = "".join(f'<circle cx="{wx}" cy="{WHEEL_Y}" r="6.5"/>' for wx in WHEELS)
    lines = "".join(f'<path d="M{x1},{ly} L{x2},{ly}"/>' for x1, ly, x2 in SPEED)
    return f'''<g transform="translate({x} {y}) scale({scale}) translate({-MARK_BOX[0]} {-MARK_BOX[1]})">
<mask id="{uid}" maskUnits="userSpaceOnUse" x="-30" y="0" width="240" height="70">
<rect x="-30" width="240" height="70" fill="#fff"/>
<path d="{WINDOW}" fill="#000"/>{arches}{halo}
</mask>
<path d="{BODY}" fill="{body}" mask="url(#{uid})"/>
<g fill="{body}">{tires}</g>
<g fill="{accent}">{hubs}{_leaf(cx, cy, ln, wd, ang)}</g>
<g stroke="{accent}" stroke-width="3.2" stroke-linecap="round">{lines}</g>
</g>'''

# ---------------------------------------------------------------- type
_fonts = {}


def text(s, font, size, x, y, tracking=0.0):
    """Outline text. Returns (path d, width, cap-top offset)."""
    f = _fonts.setdefault(font, TTFont(font))
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    k = size / upm
    pen, cx = SVGPathPen(gs), 0.0
    for i, ch in enumerate(s):
        g = gs[cmap[ord(ch)]]
        g.draw(TransformPen(pen, (k, 0, 0, -k, x + cx, y)))
        cx += g.width * k + (tracking * size if i < len(s) - 1 else 0)
    return pen.getCommands(), cx


def cap_height(font, size):
    f = _fonts.setdefault(font, TTFont(font))
    return f["OS/2"].sCapHeight * size / f["head"].unitsPerEm


def wordmark(theme, uid, x, y, size):
    """Slanted DOUBLEMINT over a racing-stripe bar with DETAILING cut out of it.
    (x, y) = top-left of the caps. Returns (svg, width, height)."""
    t = THEMES[theme]
    tr = -0.005
    cap = cap_height(BLACK_ITALIC, size)
    d1, wd1 = text("DOUBLE", BLACK_ITALIC, size, 0, cap, tr)
    d2, wd2 = text("MINT", BLACK_ITALIC, size, wd1 + tr * size, cap, tr)
    total = wd1 + tr * size + wd2
    # bar
    by, bh = cap + size * 0.16, size * 0.42
    lean = bh * 0.35
    bar = f"M{lean},{by} L{total + lean * 0.4},{by} L{total - lean * 0.6},{by + bh} L{-lean},{by + bh}Z"
    tsize = bh * 0.62
    _, raw = text("DETAILING", BLACK_ITALIC, tsize, 0, 0, 0)
    track = 0.32
    tw = raw + 8 * track * tsize
    tcap = cap_height(BLACK_ITALIC, tsize)
    d3, _ = text("DETAILING", BLACK_ITALIC, tsize, (total - tw) / 2, by + (bh + tcap) / 2, track)
    h = by + bh
    svg = f'''<g transform="translate({x} {y}) skewX({SKEW}) translate({h * 0.07} 0)">
<mask id="{uid}" maskUnits="userSpaceOnUse" x="{-size}" y="{-size}" width="{total + 2 * size}" height="{h + 2 * size}">
<rect x="{-size}" y="{-size}" width="{total + 2 * size}" height="{h + 2 * size}" fill="#fff"/><path d="{d3}" fill="#000"/></mask>
<path d="{d1}" fill="{t["w1"]}"/><path d="{d2}" fill="{t["w2"]}"/>
<path d="{bar}" fill="{t["bar"]}" mask="url(#{uid})"/>
</g>'''
    return svg, total, h


def write(name, w, h, body, bg=None):
    rect = f'<rect width="{w:.1f}" height="{h:.1f}" fill="{bg}"/>' if bg else ""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" '
           f'width="{w:.0f}" height="{h:.0f}">'
           f'<title>Doublemint Detailing</title>{rect}{body}</svg>\n')
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(svg)


def build():
    os.makedirs(OUT, exist_ok=True)
    pad = 28
    ws = 64
    for theme in THEMES:
        _, ww, wh = wordmark(theme, "x", 0, 0, ws)

        # stacked (primary): car over the wordmark
        ms = ww * 0.92 / MARK_BOX[2]
        mw, mh = MARK_BOX[2] * ms, MARK_BOX[3] * ms
        W_ = ww + 2 * pad
        gap = ws * 0.30
        wm, _, _ = wordmark(theme, f"w-s-{theme}", pad, pad + mh + gap, ws)
        write(f"doublemint-stacked-{theme}.svg", W_, pad + mh + gap + wh + pad,
              mark(theme, f"m-s-{theme}", (W_ - mw) / 2 + ww * 0.02, pad, ms) + wm)

        # horizontal: car left, wordmark right
        ms = wh * 1.05 / MARK_BOX[3]
        mw, mh = MARK_BOX[2] * ms, MARK_BOX[3] * ms
        tx = pad + mw + ws * 0.45
        H = max(mh, wh) + 2 * pad
        wm, _, _ = wordmark(theme, f"w-h-{theme}", tx, (H - wh) / 2, ws)
        write(f"doublemint-horizontal-{theme}.svg", tx + ww + pad + ws * 0.1, H,
              mark(theme, f"m-h-{theme}", pad, (H - mh) / 2, ms) + wm)

        # car only
        ms = 3
        write(f"doublemint-mark-{theme}.svg", MARK_BOX[2] * ms + 2 * pad, MARK_BOX[3] * ms + 2 * pad,
              mark(theme, f"m-m-{theme}", pad, pad, ms))

    # app / social icon: car on gloss black rounded square
    S = 512
    ms = S * 0.94 / MARK_BOX[2]
    mw, mh = MARK_BOX[2] * ms, MARK_BOX[3] * ms
    stripe = (f'<path d="M{S*0.20},{S*0.645} L{S*0.92},{S*0.645} L{S*0.885},{S*0.69} '
              f'L{S*0.165},{S*0.69}Z" fill="{SPEARMINT}"/>')
    body = (f'<rect width="{S}" height="{S}" rx="112" fill="{GLOSS}"/>'
            + mark("dark", "m-icon", (S - mw) / 2 - S * 0.01, S * 0.605 - mh, ms) + stripe)
    write("doublemint-app-icon.svg", S, S, body)


if __name__ == "__main__":
    build()
