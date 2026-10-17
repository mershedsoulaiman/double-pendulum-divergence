# Double pendulum divergence

Companion to the *Chaos Theory* passage of *Neuroplastogenics*, Volume Two of *The Trilogy of
Mind* (Soulaiman Bassam Mershed). It produces the figures for that passage and every number
behind them, so a specialist reader can check the mathematics. The book's appendix, *The
Mathematics Behind the Double Pendulum*, is built on it.

**Licences:** the code is MIT (`LICENSE`); the figures and results are CC BY 4.0
(`figures/LICENSE.md`).

## The claim, and what checking it found

The passage shows two double pendulums released from rest, identical except for a tiny
difference in one starting angle, and says their paths part: lawful motion, yet unpredictable
in practice.

- From **60°/60°**, the starting angle the first figures used, a real double pendulum does
  **not** diverge: it moves regularly for at least 100 swings. The divergence those figures show
  came from the simulation that drew them, whose arithmetic adds energy no real pendulum can
  gain (`site-check/`).
- From **90°, 120° or 150°**, it does: a millionth of a degree grows to a full radian in 7 to
  12 swings.
- **Precision buys little time.** Making the starting difference a billion times smaller
  (10⁻³° to 10⁻¹²°) delays the parting by only about 7 to 9 swings. The time to divergence grows
  with the logarithm of the precision: this is what "practically unpredictable" means.

All numbers: [`results/results.md`](results/results.md).

## What is here

```
pendulum/model.py     the two models, their energies, RK4 and forward Euler
pendulum/runs.py      the experiments: a pair of pendulums, swings until apart, energy drift
reproduce.py          writes results/results.md (pure Python, about 3 minutes)
figures.py            writes figures/svg/ (book-* for the book, appendix-* for the appendix)
render.py             figures/svg/ -> figures/png/ at 3x, with headless Chrome
sim/index.html        interactive simulation; open it in a browser, no server needed
tests/check_page.js   checks the page's physics against results.md
site-check/           runs visualize-it's own code to show what it computes
```

## Run it

```sh
python reproduce.py           # numbers -> results/results.md
python figures.py             # figures at 120°, point masses (try --start 150, --model rods)
python render.py              # PNGs for Google Docs
node tests/check_page.js      # the browser page agrees with the Python
```

Python 3.8+ with no packages; Node for the page check; Chrome for the PNGs.

## The models

Two equal arms of length $l$, equal masses $m$, gravity $g$. Both angles are measured from the
downward vertical, so $\theta_2$ is the second arm's own angle, not its angle relative to the
first. Write $\Delta = \theta_1 - \theta_2$. Time is reported in **swings**,
$T_0 = 2\pi\sqrt{l/g}$, the small-amplitude period of a simple pendulum of length $l$.

### Point masses on light rods (default; the pendulum the book describes)

$$\ddot\theta_1 = \frac{-3\frac{g}{l}\sin\theta_1 - \frac{g}{l}\sin(\theta_1 - 2\theta_2) - 2\sin\Delta\left(\dot\theta_2^2 + \dot\theta_1^2\cos\Delta\right)}{3 - \cos 2\Delta}$$

$$\ddot\theta_2 = \frac{2\sin\Delta\left(2\dot\theta_1^2 + 2\frac{g}{l}\cos\theta_1 + \dot\theta_2^2\cos\Delta\right)}{3 - \cos 2\Delta}$$

$$\frac{E}{ml^2} = \dot\theta_1^2 + \tfrac12\dot\theta_2^2 + \dot\theta_1\dot\theta_2\cos\Delta - \frac{g}{l}\left(2\cos\theta_1 + \cos\theta_2\right)$$

### Uniform rods (the model visualize-it uses)

$$8\ddot\theta_1 + 3\cos\Delta\,\ddot\theta_2 = -3\dot\theta_2^2\sin\Delta - 9\frac{g}{l}\sin\theta_1$$

$$3\cos\Delta\,\ddot\theta_1 + 2\ddot\theta_2 = 3\dot\theta_1^2\sin\Delta - 3\frac{g}{l}\sin\theta_2$$

$$\frac{E}{ml^2} = \frac{4\dot\theta_1^2 + \dot\theta_2^2 + 3\dot\theta_1\dot\theta_2\cos\Delta}{6} - \frac{g}{2l}\left(3\cos\theta_1 + \cos\theta_2\right)$$

`rods-site` is the same system in Hamiltonian form, with momenta $p_1, p_2$, exactly as the
site writes it. It is physically identical to `rods`, and kept separately because forward Euler
gives different errors depending on which variables it steps.

### Neither can go over the top from 60°/60°

Released from rest, the second arm can reach the top only if the energy allows it:
$2\cos\theta_1 + \cos\theta_2 < 1$ for the point masses, $3\cos\theta_1 + \cos\theta_2 < 2$
for the rods. At 60°/60° these give 1.5 (short of the bar) and exactly 2 (on it).

## How the numbers are computed

Classical fourth-order Runge–Kutta with a fixed step of $0.002\sqrt{l/g}$. Two checks on every
run: total energy is conserved to between 10⁻¹³ and 10⁻⁹ of the pendulum's depth, and the key
runs repeated at half the step give the same answer to the reported precision. The two rod
forms (Lagrangian and Hamiltonian) agree with each other. *Apart* means the two pendulums
are one radian apart in angle space, $\sqrt{(\Delta\theta_1)^2 + (\Delta\theta_2)^2} \ge 1$.

## Figures

| File | For |
|---|---|
| `book-01-geometry` | the starting position, with both angles and their reference verticals |
| `book-02` to `book-06` | snapshots: together, still together, just parting, well apart, fully apart (times picked by the measured gap) |
| `book-07-strip` | the five snapshots in a row |
| `appendix-1-gap-over-time` | the gap on a log scale: straight-line growth from 120°, flat from 60° |
| `appendix-2-precision` | swings until apart against the starting difference |
| `appendix-3-site-method-energy` | the energy the site's method adds, against an accurate run |

Colours: blue `#2a78d6` and red `#d0342c` for the two pendulums, as the book names them;
checked for colour-blind separation. Where the two pendulums coincide, blue is drawn wider
underneath red, so both stay visible.

## Source for the equations

The point-mass model is checked against Jiménez-López & García-Garrido (2024), *International
Journal of Bifurcation and Chaos* 34(16), doi:10.1142/S0218127424502018 (open preprint
arXiv:2403.07000, eqs. 8 and 15). Their kinetic and potential energy reduce to ours with equal
masses and arms, and the equations of motion derived from them agree with `pendulum/model.py`
to 1e-14 at 100,000 random states: `python tests/check_source.py`. The over-the-top condition
follows from their potential energy. Checked 2026-10-17.

Also cited for the double pendulum, not read (paywalled): Shinbrot et al. (1992), *Am. J.
Phys.* 60, 491–499, doi:10.1119/1.16860; Levien & Tan (1993), *Am. J. Phys.* 61, 1038,
doi:10.1119/1.17335.

## Still to do

- The appendix text itself.
- The rods model has no published source checked yet; it matters only for the site check.
- Lyapunov exponents proper, if the appendix needs a rate rather than a table.
