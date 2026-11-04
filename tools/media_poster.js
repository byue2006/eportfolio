// Studio render of a .glb for the 3D viewer's poster: node tools/media_poster.js ROOT media/x.glb OUT.webp "orbit"
// Renders with the same model-viewer build the site uses, on a transparent background.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [root, glb, out, orbit] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 1600, height: 900 } });
  await pg.route('http://poster.local/**', (r) => {
    const u = new URL(r.request().url());
    if (u.pathname === '/') return r.fulfill({ contentType: 'text/html', body:
      `<!doctype html><style>html,body{margin:0;background:transparent}model-viewer{width:1600px;height:900px;--poster-color:transparent}</style>
       <script type="module" src="/assets/vendor/model-viewer.min.js"></script>
       <model-viewer src="/${glb}" camera-orbit="${orbit}" shadow-intensity="1" shadow-softness="0.8"
         environment-image="legacy" exposure="1" interaction-prompt="none"></model-viewer>` });
    const f = path.join(root, decodeURIComponent(u.pathname));
    if (!fs.existsSync(f)) return r.fulfill({ status: 404 });
    r.fulfill({ body: fs.readFileSync(f), contentType: f.endsWith('.js') ? 'text/javascript' : 'model/gltf-binary' });
  });
  await pg.goto('http://poster.local/');
  const data = await pg.evaluate(async () => {
    const mv = document.querySelector('model-viewer');
    await customElements.whenDefined('model-viewer');
    if (!mv.loaded) await new Promise((res, rej) => { mv.addEventListener('load', res); mv.addEventListener('error', rej); });
    await new Promise((r) => setTimeout(r, 800));
    const blob = await mv.toBlob({ mimeType: 'image/webp', qualityArgument: 0.9 });
    const buf = new Uint8Array(await blob.arrayBuffer());
    let s = ''; for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
    return btoa(s);
  });
  fs.writeFileSync(out, Buffer.from(data, 'base64'));
  console.log('poster', out, fs.statSync(out).size, 'bytes');
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
