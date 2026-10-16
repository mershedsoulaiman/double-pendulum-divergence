"""Two double-pendulum models, in dimensionless form (g = l = m = 1).

Both angles are measured from the downward vertical, so the second angle is
absolute, not relative to the first arm. Time is in units of sqrt(l/g); the
figures and tables report it in swings, T0 = 2*pi*sqrt(l/g), the period of a
simple pendulum of the same length at small amplitude.

state = (theta1, theta2, omega1, omega2)
"""
import math

T0 = 2 * math.pi  # one swing, in units of sqrt(l/g)


# -- Point masses: two equal bobs on light rods of equal length ---------------
# The classic double pendulum, and the one the book's figure describes
# ("the pendulum arms and masses").
def masses(s):
    t1, t2, w1, w2 = s
    d = t1 - t2
    den = 3 - math.cos(2 * d)
    a1 = (-3 * math.sin(t1) - math.sin(t1 - 2 * t2)
          - 2 * math.sin(d) * (w2 * w2 + w1 * w1 * math.cos(d))) / den
    a2 = (2 * math.sin(d) * (2 * w1 * w1 + 2 * math.cos(t1)
                             + w2 * w2 * math.cos(d))) / den
    return (w1, w2, a1, a2)


def masses_energy(s):
    t1, t2, w1, w2 = s
    T = w1 * w1 + 0.5 * w2 * w2 + w1 * w2 * math.cos(t1 - t2)
    V = -2 * math.cos(t1) - math.cos(t2)
    return T + V


# -- Uniform rods: two equal rods, mass spread along each ----------------------
# The model visualize-it.github.io/double_pendulum uses (its drawn circles are
# markers, not masses). Lagrangian form; mass matrix [[8, 3c], [3c, 2]] / 6.
def rods(s):
    t1, t2, w1, w2 = s
    d = t1 - t2
    cd, sd = math.cos(d), math.sin(d)
    r1 = -3 * w2 * w2 * sd - 9 * math.sin(t1)
    r2 = 3 * w1 * w1 * sd - 3 * math.sin(t2)
    det = 16 - 9 * cd * cd
    return (w1, w2, (2 * r1 - 3 * cd * r2) / det, (8 * r2 - 3 * cd * r1) / det)


def rods_energy(s):
    t1, t2, w1, w2 = s
    T = (w2 * w2 + 4 * w1 * w1 + 3 * w1 * w2 * math.cos(t1 - t2)) / 6
    V = -0.5 * (3 * math.cos(t1) + math.cos(t2))
    return T + V


# -- The same rods, written as visualize-it writes them -------------------------
# Hamiltonian form, state = (theta1, theta2, p1, p2), momenta in units of
# m * l**2 * sqrt(g/l). Physically identical to `rods`; it matters only for a
# crude integrator, because forward Euler gives different errors depending on
# which variables it steps. Use this one to reproduce the site.
def rods_hamiltonian(s):
    t1, t2, p1, p2 = s
    d = t1 - t2
    cd = math.cos(d)
    den = 16 - 9 * cd * cd
    w1 = 6 * (2 * p1 - 3 * cd * p2) / den
    w2 = 6 * (8 * p2 - 3 * cd * p1) / den
    q1 = -0.5 * (w1 * w2 * math.sin(d) + 3 * math.sin(t1))
    q2 = -0.5 * (-w1 * w2 * math.sin(d) + math.sin(t2))
    return (w1, w2, q1, q2)


def rods_hamiltonian_energy(s):
    t1, t2, p1, p2 = s
    w1, w2, _, _ = rods_hamiltonian(s)
    return 0.5 * (w1 * p1 + w2 * p2) - 0.5 * (3 * math.cos(t1) + math.cos(t2))


MODELS = {
    "masses": (masses, masses_energy),
    "rods": (rods, rods_energy),
    "rods-site": (rods_hamiltonian, rods_hamiltonian_energy),
}

# Potential-energy depth below the pivot with both arms hanging: the scale for
# reporting energy errors as a fraction.
DEPTH = {"masses": 3.0, "rods": 2.0, "rods-site": 2.0}


# -- Integrators ---------------------------------------------------------------
def rk4(f, s, h):
    """Classical fourth-order Runge-Kutta step."""
    k1 = f(s)
    k2 = f(tuple(x + h / 2 * k for x, k in zip(s, k1)))
    k3 = f(tuple(x + h / 2 * k for x, k in zip(s, k2)))
    k4 = f(tuple(x + h * k for x, k in zip(s, k3)))
    return tuple(x + h / 6 * (a + 2 * b + 2 * c + d)
                 for x, a, b, c, d in zip(s, k1, k2, k3, k4))


def euler(f, s, h):
    """Forward Euler: every derivative from the old state, then one step.
    This is what visualize-it.github.io/double_pendulum does each frame."""
    return tuple(x + h * k for x, k in zip(s, f(s)))


# visualize-it uses dt = 0.1 with g/l = 9.81 / (0.2 * 0.45 * screen width).
# On a 1366 px screen that is 0.1 * sqrt(9.81 / 122.94) = 0.0282 in our units.
SITE_EULER_STEP = 0.1 * math.sqrt(9.81 / (0.2 * 0.45 * 1366))

DEFAULT_STEP = 0.002  # RK4 step; halved in reproduce.py to show convergence


def released(theta1_deg, theta2_deg):
    """Released from rest at the given angles, in degrees."""
    return (math.radians(theta1_deg), math.radians(theta2_deg), 0.0, 0.0)


def tip(s):
    """Position of the second bob or rod end; y points down."""
    t1, t2 = s[0], s[1]
    return (math.sin(t1) + math.sin(t2), math.cos(t1) + math.cos(t2))
