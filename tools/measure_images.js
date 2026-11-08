// Measures how many pixels each image on the site actually needs, for tools/make_display_images.py.
//   python3 -m http.server 8000 &   then   node tools/measure_images.js http://localhost:8000/ > tools/display_widths.json
// For every <img> (and the masked organization logos) on each page, at desktop (1440, 1920; 2x screens) and phone
// (390; 3x screens) widths, it works out the image width that fills its box at full sharpness (object-fit aware) and
// keeps the largest per page. Output: { page: { image: { px, box } } }. Paths already pointing at images/d/ copies are
// reported under the copy's path; make_display_images.py maps them back to the original.
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://localhost:8000/';
const PAGES = ['index.html', 'about.html', 'work/shear-balance.html', 'work/ttbw.html', 'work/forward-closure.html', 'work/happy-meal.html',
  'work/playseat.html', 'leadership/issdc.html', 'leadership/coaching.html', 'leadership/teaching.html', 'work/smaller-work.html', '404.html'];
(async () => {
  const b = await chromium.launch();
  const need = {};   // page -> image -> need
  for (const [w, h, dpr] of [[1440, 900, 2], [1920, 1080, 2], [390, 844, 3]]) {
    for (const p of PAGES) {
      const pg = await b.newPage({ viewport: { width: w, height: h } });
      await pg.goto(BASE + p, { waitUntil: 'load' });
      await pg.addStyleTag({ content: '[data-reveal],.fade-in{opacity:1!important;transform:none!important}' });
      await pg.evaluate(async () => { for (const i of document.images) { i.loading = 'eager'; if (!i.complete) await new Promise(r => { i.onload = i.onerror = r; }); } });
      const items = await pg.evaluate(() => {
        const out = [];
        for (const i of document.images) {
          const src = i.getAttribute('src'); if (!src || !i.naturalWidth) continue;
          const r = i.getBoundingClientRect(); if (!r.width) continue;
          const fit = getComputedStyle(i).objectFit, W = i.naturalWidth, H = i.naturalHeight;
          const s = fit === 'cover' ? Math.max(r.width / W, r.height / H) : fit === 'contain' || fit === 'scale-down' ? Math.min(r.width / W, r.height / H) : r.width / W;
          out.push({ src, px: W * s });
        }
        for (const e of document.querySelectorAll('.p-org-logo')) {   // masked logos: mask-size contain
          const m = /url\(["']?([^"')]+)/.exec(e.style.maskImage || e.style.webkitMaskImage || ''); if (!m) continue;
          const r = e.getBoundingClientRect(); if (r.width) out.push({ src: m[1], box: [r.width, r.height] });
        }
        return out;
      });
      for (const it of items) {
        const k = it.src.replace(/^(\.\.\/)+|^\//, '');
        const v = it.box ? { box: it.box.map(x => x * dpr) } : { px: it.px * dpr };
        const pn = need[p] || (need[p] = {});
        const e = pn[k] || (pn[k] = { px: 0, box: [0, 0] });
        if (v.px) e.px = Math.max(e.px, v.px);
        if (v.box) e.box = [Math.max(e.box[0], v.box[0]), Math.max(e.box[1], v.box[1])];
      }
      await pg.close();
    }
  }
  await b.close();
  const out = {};
  for (const p of Object.keys(need).sort()) { out[p] = {};
    for (const k of Object.keys(need[p]).sort()) out[p][k] = { px: Math.ceil(need[p][k].px), box: need[p][k].box.map(Math.ceil) }; }
  console.log(JSON.stringify(out, null, 1));
})();
