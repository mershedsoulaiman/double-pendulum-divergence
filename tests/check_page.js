// Runs the physics block of sim/index.html in Node and checks it against results.md.
//   node tests/check_page.js
const fs = require("fs"), path = require("path");
const html = fs.readFileSync(path.join(__dirname, "..", "sim", "index.html"), "utf8");
const start = html.indexOf("const T0 ="), end = html.indexOf("const $ =");
const physics = html.slice(start, end);
const { T0, H, SITE_STEP, models, rk4, euler } = new Function(physics + "; return { T0, H, SITE_STEP, models, rk4, euler };")();
function swingsUntilApart(model, startDeg, method, h, maxSwings = 40) {
  const r = d => d * Math.PI / 180, m = models[model];
  let a = [r(startDeg), r(startDeg), 0, 0], b = [r(startDeg + 1e-6), r(startDeg), 0, 0];
  for (let i = 1; i <= maxSwings * T0 / h; i++) {
    a = method(m.f, a, h); b = method(m.f, b, h);
    if (Math.hypot(a[0] - b[0], a[1] - b[1]) >= 1) return +(i * h / T0).toFixed(1);
  }
  return null;
}
const cases = [
  ["masses 60/60, RK4", swingsUntilApart("masses", 60, rk4, H), null],
  ["masses 120/120, RK4", swingsUntilApart("masses", 120, rk4, H), 6.9],
  ["rods 120/120, RK4", swingsUntilApart("rods", 120, rk4, H), 7.9],
  ["site form 60/60, Euler", swingsUntilApart("site", 60, euler, SITE_STEP), 8.5],
];
let ok = true;
for (const [name, got, want] of cases) {
  const pass = got === want;
  ok = ok && pass;
  console.log(`${pass ? "PASS" : "FAIL"}  ${name}: ${got ?? "not apart"} (expected ${want ?? "not apart"})`);
}
process.exit(ok ? 0 : 1);
