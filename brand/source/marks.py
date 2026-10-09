"""Logo marks: each is drawn in a 100x100 box and uses masks for every gap,
so it works on any background. mark_<name>(body, accent, uid) -> svg string."""
import math


def circ(cx, cy, r):
    return f"M{cx - r:.2f},{cy} a{r},{r} 0 1,0 {2*r},0 a{r},{r} 0 1,0 {-2*r},0Z"


def ring(cx, cy, r1, r2):
    return circ(cx, cy, r1) + circ(cx, cy, r2)


def sparkle(cx, cy, r):
    k = r * 0.18
    return (f"M{cx},{cy-r} C{cx+k},{cy-k} {cx+k},{cy-k} {cx+r},{cy} "
            f"C{cx+k},{cy+k} {cx+k},{cy+k} {cx},{cy+r} "
            f"C{cx-k},{cy+k} {cx-k},{cy+k} {cx-r},{cy} "
            f"C{cx-k},{cy-k} {cx-k},{cy-k} {cx},{cy-r}Z")


def leaf(cx, cy, length, width, ang):
    h = length / 2
    return (f'<path transform="translate({cx} {cy}) rotate({ang})" d="M0,{h} '
            f'C{0.62*width:.2f},{h-0.22*length:.2f} {0.40*width:.2f},{-h+0.20*length:.2f} 0,{-h} '
            f'C{-0.40*width:.2f},{-h+0.20*length:.2f} {-0.62*width:.2f},{h-0.22*length:.2f} 0,{h}Z"/>')


def _mask(uid, inner):
    return (f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="-10" y="-10" width="120" height="120">'
            f'<rect x="-10" y="-10" width="120" height="120" fill="#fff"/>{inner}</mask>')


def _glint(x, y, r, accent):
    """Sparkle that cuts a halo into whatever is under it."""
    return sparkle(x, y, r + 3.2), f'<path d="{sparkle(x, y, r)}" fill="{accent}"/>'


# ------------------------------------------------------------------ wheel
def mark_wheel(body, accent, uid):
    """Tire with tread notches, five-spoke alloy rim, mint-leaf centre cap."""
    C = 50
    spokes = []
    for i in range(5):
        a = i * 72
        # tapered spoke: narrow at hub, wide at rim
        spokes.append(f'<path transform="rotate({a} {C} {C})" d="M{C-3.2},{C-10} L{C-6.5},{C-30} '
                      f'L{C+6.5},{C-30} L{C+3.2},{C-10}Z"/>')
        # slot down the middle makes it a split spoke
        spokes.append(f'<path transform="rotate({a} {C} {C})" d="M{C},{C-13} L{C},{C-28}" '
                      f'stroke="#000" stroke-width="2.2" stroke-linecap="round"/>')
    glint_cut, glint = _glint(82, 17, 10, accent)
    cap_leaf = leaf(C, C, 11, 7, 35)
    return (_mask(uid, f'<path d="{glint_cut}" fill="#000"/>')
            + _mask(uid + "r", "".join(s for s in spokes if "stroke" in s)
                    + f'<g fill="#000">{cap_leaf}</g>')
            + f'<g mask="url(#{uid})"><path d="{ring(C, C, 47, 35)}" fill-rule="evenodd" fill="{body}"/></g>'
            + f'<g mask="url(#{uid}r)" fill="{body}"><path d="{ring(C, C, 32, 28.5)}" fill-rule="evenodd"/>'
            + "".join(s for s in spokes if "stroke" not in s)
            + f'<circle cx="{C}" cy="{C}" r="11"/></g>'
            + (f'<g fill="{accent}">{cap_leaf}</g>' if accent != body else "") + glint)


# ------------------------------------------------------------------ windshield
def mark_windshield(body, accent, uid):
    """Windshield with a wiper that has just swept a clean arc."""
    glass = "M18,28 C19,22 22,20 28,20 L72,20 C78,20 81,22 82,28 L90,72 C91,78 88,80 82,80 L18,80 C12,80 9,78 10,72Z"
    inner = "M24,27 L76,27 C77,27 77.5,27.5 77.7,28.5 L84,71 C84.2,72.5 83.5,73 82,73 L18,73 C16.5,73 15.8,72.5 16,71 L22.3,28.5 C22.5,27.5 23,27 24,27Z"
    px, py, R = 50, 73, 40
    a0, a1 = math.radians(200), math.radians(320)
    x0, y0 = px + R * math.cos(a0), py + R * math.sin(a0)
    x1, y1 = px + R * math.cos(a1), py + R * math.sin(a1)
    r2 = 8
    ix0, iy0 = px + r2 * math.cos(a1), py + r2 * math.sin(a1)
    ix1, iy1 = px + r2 * math.cos(a0), py + r2 * math.sin(a0)
    swept = (f"M{x0:.2f},{y0:.2f} A{R},{R} 0 0 1 {x1:.2f},{y1:.2f} "
             f"L{ix0:.2f},{iy0:.2f} A{r2},{r2} 0 0 0 {ix1:.2f},{iy1:.2f}Z")
    clip = f'<clipPath id="{uid}c"><path d="{inner}"/></clipPath>'
    bx, by = px + (R + 2) * math.cos(a1), py + (R + 2) * math.sin(a1)
    glint_cut, glint = _glint(36, 47, 7.5, body)
    return (f'<g transform="translate(50 50) scale(1.3) translate(-50 -50)"><defs>{clip}</defs>'
            + _mask(uid, f'<path d="{inner}" fill="#000"/>')
            + _mask(uid + "s", f'<path d="M{px},{py} L{bx:.2f},{by:.2f}" stroke="#000" stroke-width="7" stroke-linecap="round"/>'
                    + f'<path d="{glint_cut}" fill="#000"/>')
            + f'<path d="{glass}" fill="{body}" mask="url(#{uid})"/>'
            + f'<g clip-path="url(#{uid}c)" mask="url(#{uid}s)"><path d="{swept}" fill="{accent}"/></g>'
            + f'<path d="M{px},{py} L{bx:.2f},{by:.2f}" stroke="{body}" stroke-width="3.2" stroke-linecap="round"/>'
            + f'<circle cx="{px}" cy="{py}" r="4" fill="{body}"/>' + glint + '</g>')


# ------------------------------------------------------------------ steering wheel
def mark_steering(body, accent, uid):
    """Sport steering wheel: thick rim with grips, three spokes, mint-leaf horn badge."""
    C = 50
    grips = "".join(
        f'<rect x="{C - 1}" y="{C - 47.5}" width="2" height="5" rx="1" fill="#000" '
        f'transform="rotate({a} {C} {C})"/>' for a in (-62, -54, -46, 46, 54, 62))
    spokes = (f'<path d="M{C-14},{C-3} L{C-37},{C-6} L{C-37},{C+8} L{C-14},{C+8}Z"/>'
              f'<path d="M{C+14},{C-3} L{C+37},{C-6} L{C+37},{C+8} L{C+14},{C+8}Z"/>'
              f'<path d="M{C-6},{C+12} L{C-9},{C+38} L{C+9},{C+38} L{C+6},{C+12}Z"/>')
    hub = f"M{C-15},{C-8} C{C-15},{C-13} {C-11},{C-15} {C-6},{C-15} L{C+6},{C-15} C{C+11},{C-15} {C+15},{C-13} {C+15},{C-8} L{C+13},{C+10} C{C+12},{C+15} {C+8},{C+18} {C},{C+18} C{C-8},{C+18} {C-12},{C+15} {C-13},{C+10}Z"
    badge = leaf(C, C + 1.5, 15, 9, 35)
    marker = f'<rect x="{C-2.5}" y="{C-47}" width="5" height="9.5" rx="1" fill="{accent}"/>'
    return (_mask(uid, grips + f'<rect x="{C-4.5}" y="{C-49}" width="9" height="13.5" rx="1.5" fill="#000"/>'
                  + f'<path d="{hub}" transform="translate({C} {C}) scale(1.18) translate({-C} {-C})" fill="#000"/>')
            + f'<g mask="url(#{uid})" fill="{body}"><path d="{ring(C, C, 47, 38)}" fill-rule="evenodd"/>{spokes}</g>'
            + _mask(uid + "h", f'<g fill="#000">{badge}</g>')
            + f'<path d="{hub}" fill="{body}" mask="url(#{uid}h)"/>'
            + (f'<g fill="{accent}">{badge}</g>' if accent != body else "") + marker)


MARKS = {"wheel": mark_wheel, "windshield": mark_windshield, "steering": mark_steering}
