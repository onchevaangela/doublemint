"""Vector recreation of the new Double Mint Detailing logo (brush wordmark + car swoosh).

Requires: pip install fonttools, plus Permanent Marker (Apache 2.0, fonts.google.com/specimen/Permanent+Marker)
and Inter. Text is converted to outlines so the SVGs render identically everywhere.
Run: python3 build_new_logo.py   (writes ../new-logo/*.svg)
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

MARKER = os.environ.get("MARKER_TTF", "PermanentMarker.ttf")
INTER_BOLD = os.environ.get("INTER_BOLD", "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "new-logo")

MINT = "#3BEA6B"     # bright mint from the new logo
WHITE = "#FFFFFF"
INK = "#0A0D0B"      # brush backing / black

THEMES = {
    # name: DOUBLE, MINT, car roof, car body, DETAILING, brush backing (None = no backing)
    "full":  dict(w1=WHITE, w2=MINT, roof=WHITE, body=MINT, sub=WHITE, ink=INK),
    "dark":  dict(w1=WHITE, w2=MINT, roof=WHITE, body=MINT, sub=WHITE, ink=None),
    "light": dict(w1=INK, w2="#17B54A", roof=INK, body="#17B54A", sub=INK, ink=None),
    "white": dict(w1=WHITE, w2=WHITE, roof=WHITE, body=WHITE, sub=WHITE, ink=None),
    "black": dict(w1=INK, w2=INK, roof=INK, body=INK, sub=INK, ink=None),
}

_fonts = {}


def text(s, font, size, x, y, tracking=0.0):
    f = _fonts.setdefault(font, TTFont(font))
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    k = size / upm
    pen, cx = SVGPathPen(gs), 0.0
    for i, ch in enumerate(s):
        g = gs[cmap[ord(ch)]]
        g.draw(TransformPen(pen, (k, 0, 0, -k, x + cx, y)))
        cx += g.width * k + (tracking * size if i < len(s) - 1 else 0)
    return pen.getCommands(), cx


def width(s, font, size, tracking=0.0):
    return text(s, font, size, 0, 0, tracking)[1]


def sparkle(cx, cy, r, fill):
    k = r * 0.22
    return (f'<path d="M{cx} {cy-r} Q{cx+k} {cy-k} {cx+r} {cy} Q{cx+k} {cy+k} {cx} {cy+r} '
            f'Q{cx-k} {cy+k} {cx-r} {cy} Q{cx-k} {cy-k} {cx} {cy-r}Z" fill="{fill}"/>')


def logo(theme):
    t = THEMES[theme]
    W, H = 1200, 450
    size = 150
    gap = 30
    w_double = width("DOUBLE", MARKER, size)
    w_mint = width("MINT", MARKER, size)
    total = w_double + gap + w_mint
    x0 = (W - total) / 2 + 10
    base = 332
    d1, _ = text("DOUBLE", MARKER, size, x0, base)
    d2, _ = text("MINT", MARKER, size, x0 + w_double + gap, base)
    sub_size, sub_track = 44, 0.5
    w_sub = width("DETAILING", INTER_BOLD, sub_size, sub_track)
    d3, _ = text("DETAILING", INTER_BOLD, sub_size, (W - w_sub) / 2, 418, sub_track)

    parts = []
    if t["ink"]:
        # rough brush backing behind the wordmark
        parts.append(
            f'<path fill="{t["ink"]}" d="M96 206 C300 186 560 180 780 184 C940 187 1050 194 1118 204 '
            f'L1140 222 L1104 240 L1136 262 L1100 284 L1128 312 L1090 334 L1110 360 '
            f'C900 372 620 372 330 366 L260 384 L180 380 L120 364 '
            f'L84 350 L106 326 L66 302 L100 278 L60 252 L94 232 Z"/>')
    # car silhouette: roof arc (white) + body sweep (mint), both tapered strokes
    parts.append(
        f'<path fill="{t["roof"]}" d="M360 140 C470 70 640 48 760 70 C820 82 880 108 930 140 '
        f'C880 120 820 100 760 92 C650 78 500 96 380 146 Z"/>')
    parts.append(
        f'<path fill="{t["roof"]}" d="M720 112 L905 132 L915 142 L760 130 Z"/>')
    parts.append(
        f'<path fill="{t["body"]}" d="M120 205 C300 168 520 150 700 156 C860 160 1000 176 1130 205 '
        f'C990 190 860 180 700 178 C520 176 320 190 120 205 Z"/>')
    parts.append(
        f'<path fill="{t["body"]}" d="M440 178 C560 160 700 150 860 158 C760 160 620 168 470 186 Z"/>')
    parts.append(sparkle(965, 66, 40, t["body"]))
    parts.append(sparkle(916, 98, 18, t["body"]))
    parts.append(sparkle(1012, 120, 14, t["body"]))
    # wordmark, leaned forward
    parts.append(f'<g transform="skewX(-6) translate(30 0)">'
                 f'<path fill="{t["w1"]}" d="{d1}"/><path fill="{t["w2"]}" d="{d2}"/></g>')
    parts.append(f'<path fill="{t["sub"]}" d="{d3}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Double Mint Detailing">{"".join(parts)}</svg>\n')


def icon():
    """Square profile icon: sparkle-car + DM monogram on black."""
    d, w = text("DM", MARKER, 240, 0, 0)
    x = (512 - w) / 2
    dm, _ = text("D", MARKER, 240, x - 12, 380)
    mm, _ = text("M", MARKER, 240, x - 12 + width("D", MARKER, 240), 380)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Double Mint Detailing">'
            f'<rect width="512" height="512" rx="96" fill="{INK}"/>'
            f'<path fill="{WHITE}" d="M96 150 C170 100 290 90 380 120 C330 110 230 112 110 160 Z"/>'
            f'<path fill="{MINT}" d="M60 196 C180 160 330 156 452 190 C330 176 190 178 60 196 Z"/>'
            f'{sparkle(410, 92, 30, MINT)}'
            f'<g transform="skewX(-6) translate(24 0)"><path fill="{WHITE}" d="{dm}"/><path fill="{MINT}" d="{mm}"/></g>'
            f'</svg>\n')


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name in THEMES:
        with open(os.path.join(OUT, f"doublemint-logo-{name}.svg"), "w") as fh:
            fh.write(logo(name))
    with open(os.path.join(OUT, "doublemint-icon.svg"), "w") as fh:
        fh.write(icon())
    print("wrote", OUT)
