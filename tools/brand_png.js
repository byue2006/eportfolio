// Renders the pages tools/make_brand.py prepares into PNGs (run by that script).
// Each job: { html, out, transparent }. The element with id="card" is captured at 1x.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 2600, height: 1400 }, deviceScaleFactor: 1 });
  for (const j of jobs) {
    await pg.goto('file://' + j.html);
    await pg.evaluate(() => document.fonts.ready);
    await pg.waitForTimeout(300);
    await (await pg.$('#card')).screenshot({ path: j.out, omitBackground: j.transparent });
  }
  await b.close();
})();
