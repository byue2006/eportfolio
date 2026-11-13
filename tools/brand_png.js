// Renders the pages tools/make_brand.py, make_qr.py and make_share_cards.py prepare into PNGs (run by those scripts).
// Each job: { html, out, transparent, scale }. The element with id="card" is captured; scale (default 1) multiplies
// the pixel size, e.g. scale 3 turns a 1170 x 2532 card into 3510 x 7596.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const pages = {};   // one page per scale
  for (const j of jobs) {
    const s = j.scale || 1;
    const pg = pages[s] || (pages[s] = await b.newPage({ viewport: { width: 2600, height: 1400 }, deviceScaleFactor: s }));
    await pg.goto('file://' + j.html);
    await pg.evaluate(() => document.fonts.ready);
    if (j.fit) await pg.evaluate(() => window.fit && window.fit());
    await pg.waitForTimeout(300);
    await (await pg.$('#card')).screenshot({ path: j.out, omitBackground: j.transparent });
  }
  await b.close();
})();
