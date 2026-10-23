"""Generate the classic Double Mint Detailing logo (car swoosh + brush wordmark).

A clean vector redraw of the original artwork. The car outline, swooshes and
lettering are traced from original.jpg (see trace_original.py), so they keep the
original shapes and font; sparkles and divider rules are redrawn crisply.

Requires: pip install cairosvg
Run: python3 classic.py   (writes ../logo/classic/*.svg and *.png)
"""
import math
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT = os.path.join(HERE, "traced.json")  # from trace_original.py
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


def sparkle(cx, cy, rx, ry, k=0.14):
    """Four-point star with concave sides."""
    qx, qy = rx * k, ry * k
    return (f"M{f(cx)} {f(cy - ry)}"
            f"Q{f(cx + qx)} {f(cy - qy)} {f(cx + rx)} {f(cy)}"
            f"Q{f(cx + qx)} {f(cy + qy)} {f(cx)} {f(cy + ry)}"
            f"Q{f(cx - qx)} {f(cy + qy)} {f(cx - rx)} {f(cy)}"
            f"Q{f(cx - qx)} {f(cy - qy)} {f(cx)} {f(cy - ry)}Z")


def car():
    """Return (white_paths, green_paths) for the car and sparkles."""
    with open(TEXT) as fh:
        t = json.load(fh)
    # car outline and swooshes traced from the original (trace_original.py)
    white = [t["car_white"]]
    green = [
        t["car_green"],
        # sparkles
        sparkle(812, 70, 23, 31),
        sparkle(853, 96, 11, 14),
        sparkle(782, 59, 7.5, 10),
        sparkle(768, 82, 6.5, 8.5),
    ]
    return white, green


# ------------------------------------------------------------------- text
def wordmark():
    """Original lettering (traced) plus clean divider rules."""
    with open(TEXT) as fh:
        t = json.load(fh)
    db, mb, tb = t["double_box"], t["mint_box"], t["detailing_box"]
    # rules at the original's position, redrawn with crisp tapered outer ends
    rules = [(r[0], r[2], (r[1] + r[3]) / 2) for r in t["rules"]]
    rule_paths = [tapered((a, y), (a + (b - a) / 3, y), (b - (b - a) / 3, y), (b, y),
                          (lambda u: 5 * min(1, u / 0.06)) if i == 0
                          else (lambda u: 5 * min(1, (1 - u) / 0.06)), n=24)
                  for i, (a, b, y) in enumerate(rules)]
    box = (min(db[0], rules[0][0]), max(mb[2], rules[1][1]), tb[3])
    return t["double"], t["mint"], t["detailing"], rule_paths, box


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
