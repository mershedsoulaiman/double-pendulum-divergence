// Runs the site's own pendulum.js and simulation.js, unmodified, with the browser stubbed out.
const fs = require('fs'), vm = require('vm'), path = require('path');
const here = f => path.join(__dirname, f);
function makeCtx(screenWidth) {
  const el = () => ({ value: '', innerHTML: '' });
  const ctx = {
    Math, console: { log() {} }, Number, parseFloat,
    canvas_width: 0.45 * screenWidth, canvas_height: 0.45 * screenWidth,
    context: { beginPath(){}, moveTo(){}, lineTo(){}, stroke(){}, arc(){}, fill(){}, fillRect(){} },
    paused: true, pauseToggle() { ctx.paused = !ctx.paused; },
    t1_1_input: el(), t2_1_input: el(), t1_2_input: el(), t2_2_input: el(),
    t1_1_display: el(), t2_1_display: el(), t1_2_display: el(), t2_2_display: el(),
    t1_1_text: el(), t2_1_text: el(), t1_2_text: el(), t2_2_text: el(),
  };
  vm.createContext(ctx);
  // `let` at top level does not attach to the context object, so expose what we need.
  const src = fs.readFileSync(here('pendulum.js'), 'utf8') + '\n' + fs.readFileSync(here('simulation.js'), 'utf8') +
    '\nthis.__api = { update, initParams, updateParams, get p1(){return pendulum_1}, get p2(){return pendulum_2},' +
    ' set(a,b,c,d){ t1_1=a; t2_1=b; t1_2=c; t2_2=d; }, get L(){return length}, get c(){return constant} };';
  vm.runInContext(src, ctx);
  return ctx;
}
function run(screenWidth, blue, red, frames) {
  const ctx = makeCtx(screenWidth), api = ctx.__api;
  const r = d => d * Math.PI / 180;
  api.set(r(blue[0]), r(blue[1]), r(red[0]), r(red[1]));
  api.initParams();                      // as on page load: creates both pendulums, sets dt, length...
  // As the page does when a text box is edited: parseFloat the typed value, rebuild both pendulums.
  ctx.t1_2_text.value = String(red[0]); api.updateParams('t1_2_text');
  const L = api.L, c = api.c, PP = L * L / 2, PT = 6 / (L * L);
  const E = p => { const d = p.t1 - p.t2, cd = Math.cos(d), den = 16 - 9 * cd * cd;
    const w1 = PT * (2 * p.p1 - 3 * cd * p.p2) / den, w2 = PT * (8 * p.p2 - 3 * cd * p.p1) / den;
    return 0.5 * (w1 * p.p1 + w2 * p.p2) - PP * c * (3 * Math.cos(p.t1) + Math.cos(p.t2)); };
  const E0 = E(api.p1); const out = []; let firstPx = null, flips = 0;
  for (let f = 1; f <= frames; f++) {
    api.update();
    const a = api.p1, b = api.p2;
    const bx = (p) => [L * Math.sin(p.t1) + L * Math.sin(p.t2), L * Math.cos(p.t1) + L * Math.cos(p.t2)];
    const [ax, ay] = bx(a), [cx, cy] = bx(b);
    const px = Math.hypot(ax - cx, ay - cy);
    if (firstPx === null && px >= 2) firstPx = f;
    if (Math.abs(Math.atan2(Math.sin(a.t2), Math.cos(a.t2))) > 3.0) flips++;
    if (f % 600 === 0) out.push(`${f / 60}s: tip gap ${px.toFixed(3)} px, blue energy ${((E(a) - E0) / Math.abs(E0) * 100).toFixed(0)}%`);
  }
  return { L: L.toFixed(1), firstPx, flips, out };
}
const W = +process.argv[2] || 1366;
for (const [label, red] of [['red identical 60/60', [60, 60]], ['red 60.000001/60', [60.000001, 60]]]) {
  const res = run(W, [60, 60], red, 60 * 120);      // 2 minutes at 60 frames per second
  console.log(`\n${label} (screen ${W}px, rod ${res.L}px): tips first 2 px apart at frame ${res.firstPx} (${res.firstPx ? (res.firstPx / 60).toFixed(0) + ' s at 60 fps' : '-'}); frames with blue's second arm near the top: ${res.flips}`);
  console.log('  ' + res.out.join('\n  '));
}
