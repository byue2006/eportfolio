"""Draw each project page's link-preview card (what a shared link shows on LinkedIn, in messages, in Slack).

    python3 tools/build_site.py          (writes tools/share_cards.json: each card's label, title and picture)
    python3 tools/make_share_cards.py    (draws images/og/<slug>.jpg, 1200 x 630)
    python3 tools/build_site.py          (points each project page at its card)

The cards follow the main share card (images/og-card.png, from make_brand.py): the same paper colour, logo
lockup, mono labels and footer rule, with the project's card picture in a tile on the right. A project
without a picture gets its organization colour and wording instead. Home, About, Personal and Smaller work
keep the main card.

build_site.py prints a note when a card on disk was drawn from older text, so re-run this after renaming a
project or changing its picture. Rendered with Playwright (tools/brand_png.js); Geist loads from Google Fonts,
so it needs the network. JPEG, because some link-preview readers still don't take WebP.
"""
import html, json, os, shutil, subprocess, tempfile
from PIL import Image
from make_brand import ON_LIGHT, lockup_svg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
# The tile here is nearly square, so a few projects use a different picture or crop than their home card:
#   image / pos   another file, or where to centre the crop
#   logo, bg, sub no picture: the organization's logo on its tile colour, with a short caption
PICK = {
    'happy-meal': dict(image='images/toy-heads.webp', pos='58% 62%'),      # all three heads
    # ISSDC: every robot render is a wide strip whose labels a square crop would cut, so it shows the competition's logo instead
    'issdc': dict(image=None, logo='images/logo-issdc.webp', bg='#0b0d12', sub='Kennedy Space Center · 2023'),
    'coaching': dict(pos='50% 35%'),                                       # the tactics board, no faces
}


def card_html(slug, c):
    e = html.escape
    c = {**c, **PICK.get(slug, {})}
    if c.get('image'):
        src = os.path.join(ROOT, c['image'])
        if c.get('fit'):   # a CAD render on white: multiply it onto the tile colour, as the home card does
            tile = f'<div class="pic cad" style="background:{c.get("tint") or "#e9edf3"}"><img src="{src}" alt=""></div>'
        else:
            tile = f'<img class="pic" style="object-fit:cover;object-position:{c.get("pos", "50% 50%")}" src="{src}" alt="">'
    else:
        inner = (f'<img class="logo" src="{os.path.join(ROOT, c["logo"])}" alt="">' if c.get('logo')
                 else ''.join(f'<b>{e(x)}</b>' for x in c['big']))
        cap = f'<span class="lab">{e(c["sub"])}</span>' if c.get('sub') else ''
        tile = f'<div class="pic type{" has-logo" if c.get("logo") else ""}" style="background:{c["bg"]}">{inner}{cap}</div>'
    # a hyphenated word never breaks at its hyphen ("shear-force" stays together)
    title = ' '.join(f'<span class="nb">{e(w)}</span>' if '-' in w else e(w) for w in c['title'].split())
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@500;600&family=Geist+Mono:wght@500&display=swap">
<style>
*{{box-sizing:border-box}}body{{margin:0}}
.c{{position:relative;width:1200px;height:630px;background:#f5f5f2;color:#141414;font-family:Geist,sans-serif;overflow:hidden}}
.c::before{{content:"";position:absolute;inset:0;background-image:radial-gradient(rgba(20,20,20,.16) 1px,transparent 1.2px);background-size:22px 22px;
  -webkit-mask-image:radial-gradient(ellipse 60% 80% at 20% 30%,#000 15%,transparent 72%);mask-image:radial-gradient(ellipse 60% 80% at 20% 30%,#000 15%,transparent 72%)}}
.t{{position:absolute;left:72px;top:64px;width:492px;bottom:0}}
.top{{height:52px}}
.top img{{height:61.75px;display:block;margin:-4.9px 0 -4.9px -4.9px}}  /* tile 52px; the svg has 48/512 padding */
.lab{{font:500 16px/1.3 'Geist Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:#55585d}}
.k{{position:absolute;left:0;right:0;top:150px;color:#c2410c}}
h1{{position:absolute;left:0;right:0;top:186px;margin:0;font:500 66px/1.02 Geist,sans-serif;letter-spacing:-.045em;text-wrap:balance}}
.nb{{white-space:nowrap}}
.foot{{position:absolute;left:0;right:0;top:450px;border-top:2px solid #141414;padding-top:24px;display:flex;justify-content:space-between;align-items:center;gap:16px}}
.url{{font:600 28px/1 Geist,sans-serif;letter-spacing:-.02em;white-space:nowrap}}
.pic{{position:absolute;left:600px;top:40px;width:560px;height:550px;border-radius:16px;display:block}}
.pic.cad{{overflow:hidden}}
.cad img{{display:block;width:100%;height:100%;object-fit:contain;padding:36px;mix-blend-mode:multiply}}
.type{{display:flex;flex-direction:column;justify-content:center;padding:0 56px;color:#fff}}
.type b{{font:600 104px/1.02 Geist,sans-serif;letter-spacing:-.05em}}
.type.has-logo{{align-items:center;text-align:center;gap:40px}}
.type .logo{{display:block;width:250px;height:250px;object-fit:contain}}
.type .lab{{color:rgba(255,255,255,.72);font-size:15px}}
</style></head><body><div class="c" id="card">
<div class="t">
  <div class="top"><img src="lockup.svg" alt=""></div>
  <div class="lab k">{e(c["label"])}</div>
  <h1>{title}</h1>
  <div class="foot"><span class="lab">{e(c["foot"])}</span><span class="url">brianyue.me</span></div>
</div>
{tile}
</div>
<script>window.fit = function () {{   // shrink a long title until it clears the footer rule
  var h = document.querySelector('h1'), s = 66;
  while ((h.getBoundingClientRect().bottom > 482 || h.scrollWidth > h.clientWidth) && s > 40) {{ s -= 2; h.style.fontSize = s + 'px'; }}
}};</script></body></html>'''


def main():
    cards = json.load(open(os.path.join(TOOLS, 'share_cards.json'), encoding='utf-8'))
    out = os.path.join(ROOT, 'images', 'og')
    os.makedirs(out, exist_ok=True)
    tmp = tempfile.mkdtemp()
    try:
        open(os.path.join(tmp, 'lockup.svg'), 'w').write(lockup_svg(ON_LIGHT))
        jobs = []
        for slug, c in cards.items():
            open(os.path.join(tmp, f'{slug}.html'), 'w', encoding='utf-8').write(card_html(slug, c))
            jobs.append({'html': os.path.join(tmp, f'{slug}.html'), 'out': os.path.join(tmp, f'{slug}.png'), 'transparent': False, 'fit': True})
        jf = os.path.join(tmp, 'jobs.json')
        json.dump(jobs, open(jf, 'w'))
        subprocess.run(['node', os.path.join(TOOLS, 'brand_png.js'), jf], check=True)
        for slug in cards:   # 4:4:4 colour keeps the small lettering crisp
            Image.open(os.path.join(tmp, f'{slug}.png')).convert('RGB').save(os.path.join(out, f'{slug}.jpg'), quality=90, subsampling=0, optimize=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for f in os.listdir(out):   # a card for a project that no longer exists
        if f.endswith('.jpg') and f[:-4] not in cards:
            os.remove(os.path.join(out, f))
    with open(os.path.join(TOOLS, 'share_cards.done.json'), 'w', encoding='utf-8') as f:
        json.dump(cards, f, indent=1, ensure_ascii=False); f.write('\n')
    print(f'{len(cards)} link-preview cards written to images/og/')


if __name__ == '__main__':
    main()
