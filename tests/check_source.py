"""The point-mass equations of motion, checked against a published source.

Jiménez-López, J. & García-Garrido, V. J. (2024). Chaos and regularity in the double
pendulum with Lagrangian descriptors. International Journal of Bifurcation and Chaos
34(16). doi:10.1142/S0218127424502018. Open preprint: arXiv:2403.07000, eqs. (8), (15).

Their kinetic and potential energy, with m1 = m2 = l1 = l2 = g = 1:
    L = w1^2 + w2^2/2 + w1 w2 cos(d) + 2 cos(t1) + cos(t2),   d = t1 - t2
The Euler-Lagrange equations of that L are solved here by hand for the two
accelerations and compared with pendulum.model.masses at random states.

    python tests/check_source.py
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pendulum.model import masses  # noqa: E402


def from_source(s):
    t1, t2, w1, w2 = s
    d = t1 - t2
    c, sn = math.cos(d), math.sin(d)
    # d/dt(dL/dw1) - dL/dt1 = 0  ->  2 a1 + c a2 = -w2^2 sin d - 2 sin t1
    # d/dt(dL/dw2) - dL/dt2 = 0  ->  c a1 + a2   =  w1^2 sin d - sin t2
    b1 = -w2 * w2 * sn - 2 * math.sin(t1)
    b2 = w1 * w1 * sn - math.sin(t2)
    det = 2 - c * c
    return (b1 - c * b2) / det, (2 * b2 - c * b1) / det


def main():
    random.seed(1)
    worst = 0.0
    for _ in range(100_000):
        s = (random.uniform(-math.pi, math.pi), random.uniform(-math.pi, math.pi),
             random.uniform(-5, 5), random.uniform(-5, 5))
        _, _, a1, a2 = masses(s)
        p1, p2 = from_source(s)
        worst = max(worst, abs(a1 - p1), abs(a2 - p2))
    print(f"largest difference over 100,000 random states: {worst:.1e}")
    return 0 if worst < 1e-10 else 1


if __name__ == "__main__":
    raise SystemExit(main())
