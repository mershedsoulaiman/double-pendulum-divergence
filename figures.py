"""Write every figure as SVG into figures/svg/. Then `python render.py` makes PNGs.

    python figures.py                 # book figures at 120°, point masses
    python figures.py --start 150     # another starting angle
    python figures.py --model rods    # the rods model

Book figures (book-*): the starting geometry and snapshots of the two pendulums.
Appendix figures (appendix-*): the measured quantities behind the text.
"""
import argparse
import math
from pathlib import Path

from pendulum.model import MODELS, T0, DEFAULT_STEP, SITE_EULER_STEP, euler, rk4, released, tip
from pendulum.runs import gap, pair, record

SVG = Path(__file__).parent / "figures" / "svg"
INK, INK2, MUTED, GRID, PAPER = "#0b0b0b", "#52514e", "#8a8984", "#e5e4df", "#ffffff"
BLUE, RED = "#2a78d6", "#d0342c"          # the two pendulums, as the book names them
S1, S2 = "#2a78d6", "#eb6834"             # chart series (validated pair)
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}"><rect width="{w}" height="{h}" fill="{PAPER}"/>{body}</svg>\n')


def text(x, y, s, size=13, fill=INK2, anchor="start", weight="normal", italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{st}>{s}</text>')


def write(name, content):
    SVG.mkdir(parents=True, exist_ok=True)
    (SVG / name).write_text(content, encoding="utf-8")
    print("wrote", SVG / name)


def sup(e):
    return str(e).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))


# -- Pendulum drawing ----------------------------------------------------------
def joints(s, cx, cy, L):
    t1, t2 = s[0], s[1]
    x1, y1 = cx + L * math.sin(t1), cy + L * math.cos(t1)
    return (x1, y1), (x1 + L * math.sin(t2), y1 + L * math.cos(t2))


def pendulum(s, cx, cy, L, colour, wide):
    """Blue is drawn wide underneath, red narrow on top: when the two coincide,
    a blue edge around the red shows that there are two."""
    (x1, y1), (x2, y2) = joints(s, cx, cy, L)
    w, r = (7, 10) if wide else (3, 6)
    return (f'<polyline points="{cx:.1f},{cy:.1f} {x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}" fill="none" '
            f'stroke="{colour}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{r}" fill="{colour}"/>'
            f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="{r}" fill="{colour}"/>')


def trail(points, colour):
    if len(points) < 2:
        return ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="1.6" '
            f'stroke-opacity="0.45" stroke-linejoin="round"/>')


def pivot(cx, cy):
    return (f'<line x1="{cx - 22}" y1="{cy}" x2="{cx + 22}" y2="{cy}" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="4" fill="{INK}"/>')


def geometry(start):
    """The starting position, with the reference verticals and both angles."""
    W = H = 600
    L = 120
    s = released(start, start)
    # centre the drawing on its own extent: pivot, joint, tip and the dashed verticals
    (jx, jy), (tx, ty) = joints(s, 0, 0, L)
    xs, ys = [0, jx, tx], [-30, 150, jy - 30, jy + 150, ty]
    cx = W / 2 - (min(xs) + max(xs)) / 2
    cy = (H - 60) / 2 - (min(ys) + max(ys)) / 2
    (x1, y1), _ = joints(s, cx, cy, L)
    th = math.radians(start)

    def arc(px, py, r, label):
        ex, ey = px + r * math.sin(th), py + r * math.cos(th)
        large = 1 if start > 180 else 0
        lx = px + (r + 20) * math.sin(th / 2)
        ly = py + (r + 20) * math.cos(th / 2)
        return (f'<path d="M {px:.1f} {py + r:.1f} A {r} {r} 0 {large} 0 {ex:.1f} {ey:.1f}" '
                f'fill="none" stroke="{INK2}" stroke-width="1.5"/>'
                + f'<text x="{lx:.1f}" y="{ly + 7:.1f}" font-size="20" fill="{INK}" text-anchor="middle" '
                f'font-style="italic">θ<tspan font-size="13" dy="5">{label}</tspan></text>')

    dash = f'stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="6 6"'
    body = (f'<line x1="{cx}" y1="{cy - 30}" x2="{cx}" y2="{cy + 150}" {dash}/>'
            f'<line x1="{x1:.1f}" y1="{y1 - 30:.1f}" x2="{x1:.1f}" y2="{y1 + 150:.1f}" {dash}/>'
            + arc(cx, cy, 46, "1") + arc(x1, y1, 46, "2")
            + pendulum(s, cx, cy, L, RED, False) + pivot(cx, cy)
            + text(W / 2, H - 40, f"Released from rest at θ₁ = θ₂ = {start:g}°, "
                   "each angle measured from its own vertical", 13, INK2, "middle"))
    return svg(W, H, body)


def snapshot(start, diff, t_target, states, label=True):
    """Both pendulums at time t_target (swings), with the last swing of each tip's path."""
    W = H = 600
    cx, cy, L = 300, 300, 120
    window = [x for x in states if t_target - 1.0 <= x[0] <= t_target + 1e-9]
    _, a, b = window[-1]
    tb = [(cx + L * tip(s)[0], cy + L * tip(s)[1]) for _, s, _ in window]
    tr = [(cx + L * tip(s)[0], cy + L * tip(s)[1]) for _, _, s in window]
    body = trail(tb, BLUE) + trail(tr, RED)
    body += pendulum(a, cx, cy, L, BLUE, True) + pendulum(b, cx, cy, L, RED, False) + pivot(cx, cy)
    if label:
        body += text(24, H - 24, f"after {t_target:.1f} swings", 14, INK2)
        body += (f'<circle cx="{W - 262}" cy="{H - 29}" r="5" fill="{BLUE}"/>'
                 + text(W - 252, H - 24, f"blue {start:.6f}°", 13, INK2)
                 + f'<circle cx="{W - 132}" cy="{H - 29}" r="5" fill="{RED}"/>'
                 + text(W - 122, H - 24, f"red {start + diff:.6f}°", 13, INK2))
    return svg(W, H, body), body


def pick_times(states):
    """Snapshot times chosen by how far apart the tips are, in arm lengths:
    the start, still together, just visibly apart, well apart, fully apart."""
    def tipgap(a, b):
        (ax, ay), (bx, by) = tip(a), tip(b)
        return math.hypot(ax - bx, ay - by)
    times = [0.0, 2.0]
    for thr in (0.03, 0.3):
        times.append(next(t for t, a, b in states if t > times[-1] and tipgap(a, b) >= thr))
    apart = next(t for t, a, b in states if gap(a, b) >= 1.0)
    times.append(round(max(apart + 1.0, times[-1] + 0.5), 2))
    return times


# -- Charts --------------------------------------------------------------------
class Axes:
    def __init__(self, W, H, x0, x1, y0, y1, ylog=False, xlog=False, m=(56, 40, 56, 70)):
        self.W, self.H = W, H
        self.t, self.r, self.b, self.l = m[0], W - m[1], H - m[2], m[3]
        self.x0, self.x1, self.y0, self.y1, self.ylog, self.xlog = x0, x1, y0, y1, ylog, xlog

    def _f(self, v, lo, hi, log):
        if log:
            return (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        return (v - lo) / (hi - lo)

    def X(self, x):
        return self.l + self._f(x, self.x0, self.x1, self.xlog) * (self.r - self.l)

    def Y(self, y):
        return self.b - self._f(y, self.y0, self.y1, self.ylog) * (self.b - self.t)

    def frame(self, xticks, yticks, xlabel, ylabel):
        out = ""
        for v, lab in yticks:
            y = self.Y(v)
            out += f'<line x1="{self.l}" y1="{y:.1f}" x2="{self.r}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>'
            out += text(self.l - 8, y + 4, lab, 12, INK2, "end")
        for v, lab in xticks:
            out += text(self.X(v), self.b + 18, lab, 12, INK2, "middle")
        out += f'<line x1="{self.l}" y1="{self.b}" x2="{self.r}" y2="{self.b}" stroke="{MUTED}" stroke-width="1"/>'
        out += text((self.l + self.r) / 2, self.H - 12, xlabel, 13, INK2, "middle")
        out += text(self.l - 8, self.t - 18, ylabel, 13, INK2, "start")
        return out

    def line(self, pts, colour, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts)
        return f'<polyline points="{p}" fill="none" stroke="{colour}" stroke-width="2" stroke-linejoin="round"{d}/>'


def chart_gap(model, starts, diff, swings):
    W, H = 720, 440
    ax = Axes(W, H, 0, swings, 1e-9, 10, ylog=True)
    body = ax.frame([(v, f"{v:g}") for v in range(0, int(swings) + 1, 2)],
                    [(10 ** e, "1" if e == 0 else f"10{sup(e)}") for e in range(-9, 2, 2)],
                    "time (swings)", "gap between the two pendulums (radians, log scale)")
    y1 = ax.Y(1.0)
    body += (f'<line x1="{ax.l}" y1="{y1:.1f}" x2="{ax.r}" y2="{y1:.1f}" stroke="{INK2}" '
             f'stroke-width="1" stroke-dasharray="4 4"/>'
             + text(ax.l + 6, y1 - 6, "one radian: apart", 12, INK2, "start"))
    for start, colour, dash in starts:
        pts = []
        for t, a, b in pair(model, start, diff, swings, every=0.02):
            g = max(gap(a, b), 1e-9)
            pts.append((t, min(g, 3.0)))
            if g >= 3.0:          # well apart: beyond here the gap counts whole turns, not divergence
                break
        body += ax.line(pts, colour, dash)
        lx, ly = pts[-1]
        if ly >= 3.0:
            body += text(ax.X(lx) + 8, ax.Y(ly) + 5, f"from {start:g}°", 13, INK, "start", "bold")
        else:
            body += text(ax.X(lx) - 4, ax.Y(max(y for _, y in pts)) - 14, f"from {start:g}°", 13, INK, "end", "bold")
    return svg(W, H, body)


def chart_precision(model, starts):
    W, H = 720, 440
    diffs = [1e-3, 1e-6, 1e-9, 1e-12]
    ax = Axes(W, H, 1e-1, 1e-13, 0, 14, xlog=True, m=(56, 96, 56, 70))
    body = ax.frame([(d, f"10{sup(round(math.log10(d)))}°") for d in diffs],
                    [(v, str(v)) for v in range(0, 15, 2)],
                    "starting difference in the first arm's angle (log scale, more precise to the right)",
                    "swings until one radian apart")
    series = [(start, colour, [(d, record(model, start, d)[0]) for d in diffs]) for start, colour in starts]
    for start, colour, pts in series:
        body += ax.line(pts, colour)
    for start, colour, pts in series:
        for i, (x, y) in enumerate(pts):
            others = [p[i][1] for _, _, p in series if p is not pts]
            above = all(y >= o for o in others)
            body += (f'<circle cx="{ax.X(x):.1f}" cy="{ax.Y(y):.1f}" r="5" fill="{colour}" '
                     f'stroke="{PAPER}" stroke-width="2"/>')
            body += text(ax.X(x), ax.Y(y) + (-12 if above else 22), f"{y:.1f}", 12, INK, "middle")
    for start, colour, pts in series:
        body += text(ax.X(pts[-1][0]) + 14, ax.Y(pts[-1][1]) + 5, f"from {start:g}°", 13, INK, "start", "bold")
    return svg(W, H, body)


def chart_energy(swings=15):
    W, H = 720, 440
    f, E = MODELS["rods-site"]

    def series(method, h):
        s = released(60, 60)
        E0 = E(s)
        out = [(0.0, 0.0)]
        k = max(1, int(0.05 * T0 / h))
        for i in range(1, int(swings * T0 / h) + 1):
            s = method(f, s, h)
            if i % k == 0:
                out.append((i * h / T0, 100 * (E(s) - E0) / 2.0))
        return out

    eu, rk = series(euler, SITE_EULER_STEP), series(rk4, DEFAULT_STEP)
    ymax = 50 * math.ceil(max(y for _, y in eu) / 50)
    ax = Axes(W, H, 0, swings, -10, ymax)
    body = ax.frame([(v, f"{v:g}") for v in range(0, swings + 1, 3)],
                    [(v, f"+{v}%" if v else "0") for v in range(0, ymax + 1, 50)],
                    "time (swings), rods released from rest at 60°/60°",
                    "change in total energy (% of the pendulum's depth)")
    body += ax.line(eu, S2) + ax.line(rk, S1)
    body += text(ax.X(0.4), ax.Y(0.85 * ymax), "forward Euler, as the site", 13, INK, "start", "bold")
    body += text(ax.r - 4, ax.Y(0) - 10, "accurate (RK4): no change", 13, INK, "end", "bold")
    return svg(W, H, body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=float, default=120.0)
    ap.add_argument("--model", default="masses", choices=["masses", "rods"])
    ap.add_argument("--diff", type=float, default=1e-6)
    a = ap.parse_args()

    write("book-01-geometry.svg", geometry(a.start))
    states = list(pair(a.model, a.start, a.diff, swings=20, every=0.002))
    times = pick_times(states)
    strip = ""
    for i, t in enumerate(times):
        full, _ = snapshot(a.start, a.diff, t, states)
        write(f"book-{i + 2:02d}-after-{t:.1f}-swings.svg", full)
        _, inner = snapshot(a.start, a.diff, t, states, label=False)
        strip += f'<g transform="translate({i * 300},0) scale(0.5)">{inner}</g>'
        strip += text(i * 300 + 150, 318, f"{t:.1f} swings", 13, INK2, "middle")
    write("book-07-strip.svg", svg(300 * len(times), 330, strip))

    write("appendix-1-gap-over-time.svg",
          chart_gap(a.model, [(a.start, S1, None), (60, S2, "6 4")], a.diff, 20))
    write("appendix-2-precision.svg", chart_precision(a.model, [(120, S1), (150, S2)]))
    write("appendix-3-site-method-energy.svg", chart_energy())


if __name__ == "__main__":
    main()
