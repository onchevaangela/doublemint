"""Generate the Doublemint Detailing logo files.

Requires: pip install fonttools, plus Inter / Inter Display (OFL, fonts.google.com/specimen/Inter).
Text is converted to outlines so the SVGs render identically everywhere.
Run: python3 build.py   (writes ../logo/svg/*.svg)
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONT_DIR = os.environ.get("INTER_DIR", "/usr/share/fonts/opentype/inter")
DISPLAY_BLACK = f"{FONT_DIR}/InterDisplay-Black.otf"
TEXT_SEMIBOLD = f"{FONT_DIR}/Inter-SemiBold.otf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo", "svg")

# Brand palette
SPEARMINT = "#A3E05A"   # primary accent
PEPPERMINT = "#4CAF50"  # second leaf on dark
EVERGREEN = "#2F7D4F"   # deep green, accent on light
LIME_LEAF = "#7CC23A"   # first leaf on light
GLOSS = "#0E1210"       # near-black
STEEL = "#9AA59E"
SLATE = "#5B655F"
WHITE = "#FFFFFF"

THEMES = {
    # name: (leaf1, leaf2, sparkle, word1, word2, tagline)
    "dark": (SPEARMINT, PEPPERMINT, SPEARMINT, WHITE, SPEARMINT, STEEL),
    "light": (LIME_LEAF, EVERGREEN, EVERGREEN, GLOSS, EVERGREEN, SLATE),
    "white": (WHITE,) * 6,
    "black": (GLOSS,) * 6,
}

# ---------------------------------------------------------------- mark
# A wheel: tire, rim lip, five mint-leaf spokes, hub, and a sparkle glinting on the tire.
CX = CY = 50
R_OUT, R_IN = 46, 35          # tire ring
HUB = 8                         # hub radius
SPOKES = 5
L, W = 28.5, 17                 # leaf spoke length, width
SP_X, SP_Y, SP_R = 83.5, 16.5, 11.5   # sparkle on the rim (upper right)


def _leaf():
    return (f"M0,0 C{0.62*W:.2f},{-0.16*L:.2f} {0.42*W:.2f},{-0.70*L:.2f} 0,{-L:.2f} "
            f"C{-0.42*W:.2f},{-0.70*L:.2f} {-0.62*W:.2f},{-0.16*L:.2f} 0,0Z")


def _rib():
    return f"M0,{-0.16*L:.2f} L0,{-0.74*L:.2f}"


def _sparkle(cx, cy, r):
    k = r * 0.18
    return (f"M{cx},{cy-r} C{cx+k},{cy-k} {cx+k},{cy-k} {cx+r},{cy} "
            f"C{cx+k},{cy+k} {cx+k},{cy+k} {cx},{cy+r} "
            f"C{cx-k},{cy+k} {cx-k},{cy+k} {cx-r},{cy} "
            f"C{cx-k},{cy-k} {cx-k},{cy-k} {cx},{cy-r}Z")


def _ring():
    def circ(r):
        return (f"M{CX - r},{CY} a{r},{r} 0 1,0 {2*r},0 a{r},{r} 0 1,0 {-2*r},0Z")
    return circ(R_OUT) + circ(R_IN)


def _spoke(i):
    return f"translate({CX} {CY}) rotate({i * 360 / SPOKES}) translate(0 {-(HUB + 1.8)})"


MARK_BOX = (3.5, 3.5, 93, 93)  # x, y, w, h of the mark's visible bounds


def mark(theme, uid, x=0, y=0, scale=1.0):
    """Wheel with mint-leaf spokes and a rim sparkle."""
    c1, c2, sp = THEMES[theme][:3]
    leaf, rib = _leaf(), _rib()
    ribs = "".join(f'<path d="{rib}" transform="{_spoke(i)}" fill="none" stroke="#000" '
                   f'stroke-width="1.7" stroke-linecap="round"/>' for i in range(SPOKES))
    leaves = "".join(f'<path d="{leaf}" transform="{_spoke(i)}"/>' for i in range(SPOKES))
    return f'''<g transform="translate({x} {y}) scale({scale}) translate({-MARK_BOX[0]} {-MARK_BOX[1]})">
<mask id="{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">
<rect width="100" height="100" fill="#fff"/>{ribs}
<path d="{_sparkle(SP_X, SP_Y, SP_R + 3.2)}" fill="#000"/>
<circle cx="{CX}" cy="{CY}" r="2.6" fill="#000"/>
</mask>
<g mask="url(#{uid})">
<path d="{_ring()}" fill-rule="evenodd" fill="{c2}"/>
<circle cx="{CX}" cy="{CY}" r="{R_IN - 3.6}" fill="none" stroke="{c1}" stroke-width="1.8"/>
<g fill="{c1}">{leaves}<circle cx="{CX}" cy="{CY}" r="{HUB}"/></g>
</g>
<path d="{_sparkle(SP_X, SP_Y, SP_R)}" fill="{sp}"/>
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


def wordmark(theme, x, y, word_size):
    """DOUBLE|MINT over spaced DETAILING. (x, y) = top-left of caps."""
    _, _, _, w1, w2, tag = THEMES[theme]
    tr = 0.01
    cap = cap_height(DISPLAY_BLACK, word_size)
    base = y + cap
    d1, wd1 = text("DOUBLE", DISPLAY_BLACK, word_size, x, base, tr)
    d2, wd2 = text("MINT", DISPLAY_BLACK, word_size, x + wd1 + tr * word_size, base, tr)
    total = wd1 + tr * word_size + wd2
    # tagline: fit DETAILING to the wordmark width via tracking
    tsize = word_size * 0.34
    _, raw = text("DETAILING", TEXT_SEMIBOLD, tsize, 0, 0, 0)
    ttrack = (total - raw) / (8 * tsize)
    tcap = cap_height(TEXT_SEMIBOLD, tsize)
    tbase = base + word_size * 0.30 + tcap
    d3, _ = text("DETAILING", TEXT_SEMIBOLD, tsize, x, tbase, ttrack)
    svg = (f'<path d="{d1}" fill="{w1}"/><path d="{d2}" fill="{w2}"/>'
           f'<path d="{d3}" fill="{tag}"/>')
    return svg, total, tbase - y


def write(name, w, h, body, bg=None):
    rect = f'<rect width="{w:.1f}" height="{h:.1f}" fill="{bg}"/>' if bg else ""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" '
           f'width="{w:.0f}" height="{h:.0f}">'
           f'<title>Doublemint Detailing</title>{rect}{body}</svg>\n')
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(svg)


def build():
    os.makedirs(OUT, exist_ok=True)
    pad = 24
    for theme in THEMES:
        # horizontal lockup: mark height == wordmark block height
        ws = 64
        wm, ww, wh = wordmark(theme, 0, 0, ws)
        ms = wh / MARK_BOX[3] * 1.22
        mw, mh = MARK_BOX[2] * ms, MARK_BOX[3] * ms
        gap = mw * 0.30
        tx = pad + mw + gap
        ty = pad + (mh - wh) / 2
        wm, _, _ = wordmark(theme, tx, ty, ws)
        write(f"doublemint-horizontal-{theme}.svg", tx + ww + pad, mh + 2 * pad,
              mark(theme, f"m-h-{theme}", pad, pad, ms) + wm)

        # stacked lockup
        ws = 64
        _, ww, wh = wordmark(theme, 0, 0, ws)
        ms = ww * 0.36 / MARK_BOX[2]
        mw, mh = MARK_BOX[2] * ms, MARK_BOX[3] * ms
        W_ = ww + 2 * pad
        wm, _, _ = wordmark(theme, pad, pad + mh + ws * 0.42, ws)
        write(f"doublemint-stacked-{theme}.svg", W_, pad + mh + ws * 0.42 + wh + pad,
              mark(theme, f"m-s-{theme}", (W_ - mw) / 2, pad, ms) + wm)

        # mark only
        ms = 3.2
        write(f"doublemint-mark-{theme}.svg", MARK_BOX[2] * ms + 2 * pad, MARK_BOX[3] * ms + 2 * pad,
              mark(theme, f"m-m-{theme}", pad, pad, ms))

    # app / social icon: mark on gloss black rounded square
    S = 512
    ms = S * 0.66 / MARK_BOX[2]
    mw, mh = MARK_BOX[2] * ms, MARK_BOX[3] * ms
    body = (f'<rect width="{S}" height="{S}" rx="112" fill="{GLOSS}"/>'
            + mark("dark", "m-icon", (S - mw) / 2, (S - mh) / 2, ms))
    write("doublemint-app-icon.svg", S, S, body)


if __name__ == "__main__":
    build()
