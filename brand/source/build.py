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
# Marks live in marks.py. MARK picks the one used for the main logo files;
# every option is also exported to ../logo/options/ for comparison.
from marks import MARKS
MARK = os.environ.get("DM_MARK", "wheel")
MARK_BOX = (2, 2, 96, 96)


def mark(theme, uid, x=0, y=0, scale=1.0, kind=None):
    t = THEMES[theme]
    draw = MARKS[kind or MARK]
    return (f'<g transform="translate({x} {y}) scale({scale}) translate({-MARK_BOX[0]} {-MARK_BOX[1]})">'
            f'{draw(t["body"], t["accent"], uid)}</g>')

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


def stacked(theme, kind=None, tag=""):
    pad, ws = 28, 64
    _, ww, wh = wordmark(theme, "x", 0, 0, ws)
    ms = ww * 0.40 / MARK_BOX[2]
    mw, mh = MARK_BOX[2] * ms, MARK_BOX[3] * ms
    W_ = ww + 2 * pad + ws * 0.15
    gap = ws * 0.28
    wm, _, _ = wordmark(theme, f"w-s-{theme}{tag}", pad, pad + mh + gap, ws)
    return W_, pad + mh + gap + wh + pad, mark(theme, f"m-s-{theme}{tag}", (W_ - mw) / 2, pad, ms, kind) + wm


def build():
    os.makedirs(OUT, exist_ok=True)
    pad, ws = 28, 64
    for theme in THEMES:
        _, ww, wh = wordmark(theme, "x", 0, 0, ws)

        # stacked (primary): mark over the wordmark
        w, h, body = stacked(theme)
        write(f"doublemint-stacked-{theme}.svg", w, h, body)

        # horizontal: mark left, wordmark right
        ms = wh * 1.35 / MARK_BOX[3]
        mw, mh = MARK_BOX[2] * ms, MARK_BOX[3] * ms
        tx = pad + mw + ws * 0.30
        H = max(mh, wh) + 2 * pad
        wm, _, _ = wordmark(theme, f"w-h-{theme}", tx, (H - wh) / 2, ws)
        write(f"doublemint-horizontal-{theme}.svg", tx + ww + pad + ws * 0.1, H,
              mark(theme, f"m-h-{theme}", pad, (H - mh) / 2, ms) + wm)

        # mark only
        ms = 3
        write(f"doublemint-mark-{theme}.svg", MARK_BOX[2] * ms + 2 * pad, MARK_BOX[3] * ms + 2 * pad,
              mark(theme, f"m-m-{theme}", pad, pad, ms))

    # app / social icon: mark on gloss black rounded square
    S = 512
    ms = S * 0.70 / MARK_BOX[2]
    mw = MARK_BOX[2] * ms
    write("doublemint-app-icon.svg", S, S,
          f'<rect width="{S}" height="{S}" rx="112" fill="{GLOSS}"/>'
          + mark("dark", "m-icon", (S - mw) / 2, (S - mw) / 2, ms))

    # options: every mark as a stacked logo, for choosing
    opt = os.path.join(OUT, "..", "options")
    os.makedirs(opt, exist_ok=True)
    for kind in MARKS:
        for theme in ("dark", "light"):
            w, h, body = stacked(theme, kind, f"-{kind}")
            rect = f'<rect width="{w:.1f}" height="{h:.1f}" fill="{GLOSS if theme == "dark" else "#F3F7F0"}"/>'
            with open(os.path.join(opt, f"option-{kind}-{theme}.svg"), "w") as fh:
                fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" '
                         f'width="{w:.0f}" height="{h:.0f}">{rect}{body}</svg>\n')


if __name__ == "__main__":
    build()
