"""The experiments behind every number in the tables and figures."""
import math
from .model import DEPTH, MODELS, T0, DEFAULT_STEP, rk4, released, tip


def gap(a, b):
    """Separation of two pendulums in angle space, radians."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def pair(model, start_deg, diff_deg=1e-6, swings=20.0, step=DEFAULT_STEP,
         method=rk4, every=None, stop_at=None):
    """Blue at start/start, red at (start + diff)/start, both from rest.

    Yields (time in swings, blue state, red state) every `every` swings
    (or every step if None). Stops early once the gap reaches `stop_at`.
    """
    f, _ = MODELS[model]
    a = released(start_deg, start_deg)
    b = released(start_deg + diff_deg, start_deg)
    n = int(round(swings * T0 / step))
    k = 1 if every is None else max(1, int(round(every * T0 / step)))
    yield 0.0, a, b
    for i in range(1, n + 1):
        a = method(f, a, step)
        b = method(f, b, step)
        if i % k == 0:
            yield i * step / T0, a, b
        if stop_at is not None and gap(a, b) >= stop_at:
            yield i * step / T0, a, b
            return


def swings_until(model, start_deg, diff_deg, threshold=1.0, max_swings=100.0,
                 step=DEFAULT_STEP, method=rk4):
    """Swings until the two pendulums are `threshold` radians apart, or None."""
    for t, a, b in pair(model, start_deg, diff_deg, max_swings, step, method,
                        stop_at=threshold):
        if gap(a, b) >= threshold:
            return t
    return None


def energy_drift(model, start_deg, swings, step, method):
    """Largest change in total energy over the run, as a fraction of the
    starting potential-energy depth below the pivot (always nonzero)."""
    f, E = MODELS[model]
    s = released(start_deg, start_deg)
    E0 = E(s)
    scale = DEPTH[model]
    worst = 0.0
    for _ in range(int(round(swings * T0 / step))):
        s = method(f, s, step)
        worst = max(worst, abs(E(s) - E0) / scale)
    return worst


def record(model, start_deg, diff_deg=1e-6, max_swings=100.0, step=DEFAULT_STEP,
           method=rk4, threshold=1.0):
    """One pass: swings until `threshold` rad apart (or None), the largest gap
    seen, and the blue pendulum's worst energy change (fraction of the depth)."""
    f, E = MODELS[model]
    a = released(start_deg, start_deg)
    b = released(start_deg + diff_deg, start_deg)
    E0 = E(a)
    scale = DEPTH[model]
    worst_gap = worst_dE = 0.0
    for i in range(1, int(round(max_swings * T0 / step)) + 1):
        a = method(f, a, step)
        b = method(f, b, step)
        g = gap(a, b)
        worst_gap = max(worst_gap, g)
        if i % 50 == 0:
            worst_dE = max(worst_dE, abs(E(a) - E0) / scale)
        if g >= threshold:
            return i * step / T0, worst_gap, worst_dE
    return None, worst_gap, worst_dE
