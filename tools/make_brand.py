"""Make every logo file from one definition.

    python3 tools/make_brand.py

Writes favicon.svg, favicon.ico (16/32/48), apple-touch-icon.png, images/og-card.png
and assets/brand/ (mark + lockups, SVG and PNG). The site header draws the same mark
inline (BRAND_MARK in build_site.py) with colors from CSS so it follows light/dark mode.

The mark is a bold Geist "BY" with an orange square full stop on a white tile; the
wordmark is "Brian Yue" in Geist SemiBold. Both are stored as outlines, so nothing here
needs the font installed. PNGs are rendered with Playwright (tools/brand_png.js); the
share card loads Geist from Google Fonts, so it needs the network.
"""
import json, os, shutil, subprocess, tempfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- geometry (512 x 512 tile) ---------------------------------------------
BY = ('M79.9 346V166H150Q183.5 166 201.2 177.7Q218.9 189.5 218.9 214.9Q218.9 226.1 214.4 234.3Q209.8 242.6 201.1 247.4'
      'Q192.3 252.2 179.8 253.1L179.7 252.8Q202.5 254.2 214.5 265.7Q226.5 277.2 226.5 296.4Q226.5 321.5 208.9 333.7'
      'Q191.2 346 158.6 346ZM118.5 314.7H156.7Q170.6 314.7 179.1 309Q187.6 303.3 187.6 291.8Q187.6 280.3 179.2 274.4'
      'Q170.8 268.5 156.7 268.5H118.5ZM118.5 240.5H148.8Q163.1 240.5 171.5 235Q180 229.5 180 218.9Q180 207.8 171.8 202.6'
      'Q163.6 197.3 148.8 197.3H118.5ZM291.3 346V276.1L228.7 166H271.3L310.7 238.6L349.8 166H392.4L330 276.1V346Z')
STOP = (405.1, 319, 27)  # x, y, size of the orange square full stop
# "Brian Yue", Geist 600 at 290 units (17/30 of the tile, as in the header), tracking -0.025em, baseline at 0
WORDMARK = ('M23.2 0V-206H100.3Q138 -206 157.6 -192.6Q177.2 -179.2 177.2 -150.2Q177.2 -137.2 171.8 -127.5Q166.4 -117.9 156.2 -112.3'
            'Q145.9 -106.8 131.4 -106.1L131.3 -106.9Q157.4 -105.8 171.7 -92.3Q185.9 -78.9 185.9 -56.7Q185.9 -28.2 166.4 -14.1'
            'Q146.8 0 110.7 0ZM60.9 -32H109.2Q126.9 -32 137.2 -39.3Q147.5 -46.5 147.5 -60.7Q147.5 -74.9 137.3 -82.4Q127 -90 109.2 -90'
            'H60.9ZM60.9 -119.5H99.3Q117.8 -119.5 128.3 -126.5Q138.8 -133.6 138.8 -146.7Q138.8 -160.7 128.6 -167.3Q118.4 -174 99.3 -174'
            'H60.9ZM214.8 0V-154.9H249.5L250.9 -111.9L247.9 -112.6Q251.4 -134.9 261 -144.9Q270.7 -154.9 287.4 -154.9H301.8V-123.1'
            'H287.3Q275.4 -123.1 267.6 -119.6Q259.8 -116.1 255.9 -108.7Q252 -101.3 252 -89.2V0ZM326.2 0V-154.9H363.4V0ZM325.5 -175.6'
            'V-208.5H364.1V-175.6ZM441.8 3.5Q417.6 3.5 402.8 -7.7Q388 -18.8 388 -38.8Q388 -59 400.4 -70.2Q412.9 -81.5 438.3 -86.5'
            'L489.8 -96.5Q489.8 -113 482.2 -121.3Q474.7 -129.6 460 -129.6Q446.5 -129.6 438.7 -123.5Q431 -117.3 428.4 -105.6L390.6 -107.5'
            'Q395 -131.9 413.1 -145.2Q431.1 -158.4 460 -158.4Q493.1 -158.4 510 -141.8Q526.9 -125.2 526.9 -94.1V-37.7Q526.9 -31.5 529.1 -29.3'
            'Q531.2 -27 535.5 -27H540.5V0Q538.7 0.5 534.8 0.9Q530.9 1.3 527 1.3Q517.4 1.3 509.9 -1.9Q502.3 -5 498.2 -12.6Q494 -20.2 494 -33.5'
            'L497.3 -31.3Q494.9 -21.1 487.3 -13.2Q479.6 -5.3 468 -0.9Q456.3 3.5 441.8 3.5ZM449.4 -23.6Q461.8 -23.6 470.8 -28.4'
            'Q479.8 -33.2 484.8 -42Q489.8 -50.8 489.8 -62.6V-71.3L449.6 -63.1Q437.3 -60.7 431.9 -55.6Q426.4 -50.4 426.4 -42.2'
            'Q426.4 -33.4 432.4 -28.5Q438.4 -23.6 449.4 -23.6ZM558 0V-154.9H591.6L593.1 -111.5L588.6 -113.3Q591 -129.5 598.2 -139.4'
            'Q605.4 -149.2 615.9 -153.8Q626.5 -158.4 638.9 -158.4Q656 -158.4 667.7 -150.9Q679.4 -143.4 685.5 -130.2Q691.6 -117 691.6 -99.6'
            'V0H654.4V-87.7Q654.4 -100.7 651.9 -109.8Q649.4 -118.8 643.5 -123.5Q637.5 -128.2 627.6 -128.2Q612.6 -128.2 603.9 -117.8'
            'Q595.2 -107.4 595.2 -87.7V0ZM836 0V-81.4L764 -206H806.3L855 -118.5L903.4 -206H945.7L873.8 -81.4V0ZM1007.9 3.5'
            'Q984.3 3.5 970.6 -12Q957 -27.6 957 -55.2V-154.9H994.1V-64.3Q994.1 -44.9 1000.5 -35.8Q1006.9 -26.7 1020.3 -26.7'
            'Q1035.4 -26.7 1043.7 -36.7Q1052.1 -46.7 1052.1 -65.8V-154.9H1089.2V0H1055.1L1054.3 -42.5L1059.1 -41.1Q1055.4 -19.2 1042.3 -7.9'
            'Q1029.3 3.5 1007.9 3.5ZM1189.7 3.5Q1166.6 3.5 1149.5 -6.5Q1132.5 -16.5 1123.2 -34.7Q1113.9 -53 1113.9 -77.5Q1113.9 -102 1123.2 -120.1'
            'Q1132.5 -138.2 1149.4 -148.3Q1166.2 -158.4 1189 -158.4Q1211.1 -158.4 1227.7 -148.5Q1244.3 -138.6 1253.4 -120.1'
            'Q1262.5 -101.5 1262.5 -75.4V-67.1H1152.4Q1153.5 -46.7 1163.5 -36.4Q1173.5 -26.2 1190.2 -26.2Q1202.6 -26.2 1210.8 -31.8'
            'Q1219 -37.3 1222.3 -47.5L1260.3 -45.1Q1254.1 -22.7 1235.3 -9.6Q1216.5 3.5 1189.7 3.5ZM1152.4 -92.1H1224'
            'Q1222.8 -110.9 1213.3 -120.1Q1203.8 -129.2 1189 -129.2Q1174.1 -129.2 1164.4 -119.6Q1154.7 -110.1 1152.4 -92.1Z')
WM_X, WM_BASE, WM_W = 683, 359, 1263  # wordmark origin (10/30 tile gap) and right edge

# --- colors: the same values as the header tokens in assets/site.css --------
ON_LIGHT = dict(tile='#ffffff', edge='#d3d3ce', ink='#141414', stop='#c2410c', text='#141414')
ON_DARK = dict(tile='#f5f5f2', edge=None, ink='#0b0c0d', stop='#d4541a', text='#ededeb')


def tile(c, rounded=True):
    if not rounded:  # full-bleed square for the phone home screen (iOS rounds it itself)
        return f'<rect width="512" height="512" fill="{c["tile"]}"/>'
    if c['edge']:  # a hairline so the white tile still reads on white
        return f'<rect x="8" y="8" width="496" height="496" rx="106" fill="{c["tile"]}" stroke="{c["edge"]}" stroke-width="16"/>'
    return f'<rect width="512" height="512" rx="112" fill="{c["tile"]}"/>'


def mark_body(c, rounded=True):
    x, y, s = STOP
    return f'{tile(c, rounded)}<path fill="{c["ink"]}" d="{BY}"/><rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{c["stop"]}"/>'


def mark_svg(c, rounded=True):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Brian Yue">'
            f'{mark_body(c, rounded)}</svg>')


def lockup_svg(c, pad=48):
    w = WM_X + WM_W + pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w + pad} {512 + 2 * pad}" role="img" aria-label="Brian Yue">'
            f'{mark_body(c)}<path fill="{c["text"]}" transform="translate({WM_X} {WM_BASE})" d="{WORDMARK}"/></svg>')


def og_card_html(lockup):
    # The share card. Headline style follows the home page hero.
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:ital,wght@0,500;0,600;1,700&family=Geist+Mono:wght@500&display=swap">
<style>
*{{box-sizing:border-box}}body{{margin:0}}
.c{{position:relative;width:1200px;height:630px;background:#f5f5f2;color:#141414;font-family:Geist,sans-serif;padding:64px 72px 0;overflow:hidden}}
.c::before{{content:"";position:absolute;inset:0;background-image:radial-gradient(rgba(20,20,20,.16) 1px,transparent 1.2px);background-size:22px 22px;
  -webkit-mask-image:radial-gradient(ellipse 70% 80% at 80% 25%,#000 20%,transparent 75%);mask-image:radial-gradient(ellipse 70% 80% at 80% 25%,#000 20%,transparent 75%)}}
.top{{position:relative;display:flex;justify-content:space-between;align-items:center;height:52px}}
.top img{{height:61.75px;display:block;margin:-4.9px 0 -4.9px -4.9px}}  /* tile 52px; the svg has 48/512 padding */
.lab{{font:500 16px/1 'Geist Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:#55585d}}
h1{{position:relative;margin:92px 0 0;font:500 120px/.98 Geist,sans-serif;letter-spacing:-.052em}}
h1 em{{font-weight:700;font-style:italic;letter-spacing:-.05em;color:#c2410c}}
.foot{{position:absolute;left:72px;right:72px;top:514px;border-top:2px solid #141414;padding-top:24px;display:flex;justify-content:space-between;align-items:center}}
.url{{font:600 28px/1 Geist,sans-serif;letter-spacing:-.02em}}
</style></head><body><div class="c" id="card">
<div class="top"><img src="{lockup}" alt=""><span class="lab">Portfolio · 2026</span></div>
<h1>I design hardware<br>and then <em>make it.</em></h1>
<div class="foot"><span class="lab">Mechanical engineering · Duke University</span><span class="url">brianyue.me</span></div>
</div></body></html>'''


def wrap(svg_file, w, h):
    return (f'<!doctype html><html><head><style>html,body{{margin:0;background:transparent}}img{{display:block;width:{w}px;height:{h}px}}</style></head>'
            f'<body><img id="card" src="{svg_file}" alt=""></body></html>')


def main():
    brand = os.path.join(ROOT, 'assets', 'brand')
    os.makedirs(brand, exist_ok=True)
    files = {
        os.path.join(ROOT, 'favicon.svg'): mark_svg(ON_LIGHT),
        os.path.join(brand, 'logo-mark.svg'): mark_svg(ON_LIGHT),
        os.path.join(brand, 'logo-lockup.svg'): lockup_svg(ON_LIGHT),
        os.path.join(brand, 'logo-lockup-on-dark.svg'): lockup_svg(ON_DARK),
    }
    for p, s in files.items():
        open(p, 'w', encoding='utf-8').write(s + '\n')
    for old in ('logo-mark-light.svg', 'logo-mark-light-1024.png'):  # the old serif mark's dark-background variant
        if os.path.exists(os.path.join(brand, old)):
            os.remove(os.path.join(brand, old))

    tmp = tempfile.mkdtemp()
    try:
        open(os.path.join(tmp, 'mark.svg'), 'w').write(mark_svg(ON_LIGHT))
        open(os.path.join(tmp, 'square.svg'), 'w').write(mark_svg(ON_LIGHT, rounded=False))
        open(os.path.join(tmp, 'lockup.svg'), 'w').write(lockup_svg(ON_LIGHT))
        open(os.path.join(tmp, 'lockup-dark.svg'), 'w').write(lockup_svg(ON_DARK))
        lw = WM_X + WM_W + 96; lh = 512 + 96
        pages = {
            'mark1024.html': wrap('mark.svg', 1024, 1024), 'touch.html': wrap('square.svg', 180, 180),
            'ico16.html': wrap('mark.svg', 16, 16), 'ico32.html': wrap('mark.svg', 32, 32), 'ico48.html': wrap('mark.svg', 48, 48),
            'lockup.html': wrap('lockup.svg', 2400, round(2400 * lh / lw)),
            'lockup-dark.html': wrap('lockup-dark.svg', 2400, round(2400 * lh / lw)),
            'og.html': og_card_html('lockup.svg'),
        }
        for n, s in pages.items():
            open(os.path.join(tmp, n), 'w').write(s)
        jobs = [
            ('mark1024.html', os.path.join(brand, 'logo-mark-1024.png'), True),
            ('lockup.html', os.path.join(brand, 'logo-lockup-2400.png'), True),
            ('lockup-dark.html', os.path.join(brand, 'logo-lockup-on-dark-2400.png'), True),
            ('touch.html', os.path.join(ROOT, 'apple-touch-icon.png'), False),
            ('og.html', os.path.join(ROOT, 'images', 'og-card.png'), False),
            ('ico16.html', os.path.join(tmp, '16.png'), True),
            ('ico32.html', os.path.join(tmp, '32.png'), True),
            ('ico48.html', os.path.join(tmp, '48.png'), True),
        ]
        jf = os.path.join(tmp, 'jobs.json')
        json.dump([{'html': os.path.join(tmp, h), 'out': o, 'transparent': t} for h, o, t in jobs], open(jf, 'w'))
        subprocess.run(['node', os.path.join(ROOT, 'tools', 'brand_png.js'), jf], check=True)
        Image.open(os.path.join(ROOT, 'apple-touch-icon.png')).convert('RGB').save(os.path.join(ROOT, 'apple-touch-icon.png'))
        Image.open(os.path.join(ROOT, 'images', 'og-card.png')).convert('RGB').save(os.path.join(ROOT, 'images', 'og-card.png'))
        icons = [Image.open(os.path.join(tmp, f'{s}.png')).convert('RGBA') for s in (48, 32, 16)]
        icons[0].save(os.path.join(ROOT, 'favicon.ico'), sizes=[(48, 48), (32, 32), (16, 16)], append_images=icons[1:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('brand files written')


if __name__ == '__main__':
    main()
