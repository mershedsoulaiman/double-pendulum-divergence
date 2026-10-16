# Checking visualize-it's double pendulum

The first figures for *Chaos Theory* (Volume Two of *The Trilogy of Mind*) came from
<https://visualize-it.github.io/double_pendulum/simulation.html>. This folder runs that page's
own code, unmodified, to show what it computes.

## What the page does (source read 2026-10-16)

- **Model:** two uniform rods, in Hamiltonian form (`rods-site` in `pendulum/model.py`).
  The circles it draws are markers, not masses.
- **Integration:** forward Euler, `dt = 0.1`, one step per animation frame. Forward Euler
  does not conserve energy.
- **Input:** sliders step in whole degrees; the text boxes take decimals. The default for the
  red pendulum is θ₁ = 61°. With identical inputs the two runs are identical and the red
  pendulum is drawn exactly over the blue.

## Run it

```sh
curl -O https://visualize-it.github.io/double_pendulum/pendulum.js
curl -O https://visualize-it.github.io/double_pendulum/simulation.js
node runsite.js 1366        # argument: screen width in px, which sets the rod length
```

The two files are the site's, not ours, so `.gitignore` keeps them out of this repository.

## Result, 2026-10-16 (1366 px screen, 60 frames per second)

| Red pendulum | Gap between the tips | Blue's energy |
|---|---|---|
| identical, 60°/60° | 0 px for 2 minutes | +57% by 10 s, then 90–200% above its start |
| θ₁ = 60.000001° | 2 px at about 26 s, 260 px by 40 s | the same |

The page does show divergence from 60.000001°, but only after its arithmetic has added energy
no real pendulum can gain. Integrated accurately (`reproduce.py`, section 1), a pendulum
released from 60°/60° stays regular for at least 100 swings.
