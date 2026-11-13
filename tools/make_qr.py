"""Make the QR codes that open brianyue.me, for sharing at events.

    pip install segno          (works out the QR pattern)
    python3 tools/make_qr.py   (optionally: python3 tools/make_qr.py https://brianyue.me/about)

Writes to assets/brand/:
  qr-brianyue.svg, qr-brianyue-2048.png              the code with the BY mark in the middle
  qr-brianyue-plain.svg, qr-brianyue-plain-2048.png  the code alone
  qr-phone-card.png                                  a phone-sized screen to hold up: logo, code, address

Dark squares on white only (inverted codes fail on some phones), square modules, and the standard
four-module white margin, which scanners need: keep that margin clear wherever the code is placed.
The version with the mark uses a higher error-correction level (Q), so the covered middle is recoverable. Its layout
(25 squares across, a 5-square clearing) was the most reliable of those tried in a stress test of 400 distorted photos:
about 9 in 10 of the plain code's hit rate. A denser code with a bigger mark managed about 7 in 10.
PNGs are rendered with Playwright (tools/brand_png.js); the phone card loads Geist from Google Fonts.
"""
import json, os, shutil, subprocess, sys, tempfile
import segno
from make_brand import BY, STOP, ON_LIGHT, ON_DARK, lockup_svg, WM_X, WM_W

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = sys.argv[1] if len(sys.argv) > 1 else 'https://brianyue.me'
INK, PAPER, QUIET = ON_LIGHT['ink'], '#ffffff', 4
LOGO, MARK = 5, 4.4   # squares cleared for the mark (odd, so it sits exactly in the middle) and the mark's width in squares


def matrix(error, logo=False):
    """The QR pattern as rows of True (dark) / False. A QR code can be drawn with any of eight mask patterns; for the
    version with the mark, pick the one with the fewest dark squares under the clearing, so the mark erases as little
    as possible (in a stress test of 400 distorted photos that was also the pattern that scanned most often)."""
    def rows(mask):
        return [[bool(v) for v in row] for row in segno.make(URL, error=error, micro=False, boost_error=False, mask=mask).matrix]
    if not logo:
        return rows(None)
    def erased(m):
        a, b = (len(m) - LOGO) // 2, (len(m) + LOGO) // 2
        return sum(m[y][x] for y in range(a, b) for x in range(a, b))
    return min((rows(k) for k in range(8)), key=erased)


def qr_svg(m, logo=False):
    n = len(m)
    size = n + 2 * QUIET
    a, b = (n - LOGO) // 2, (n + LOGO) // 2   # the cleared square, in modules
    runs = []
    for y, row in enumerate(m):
        x = 0
        while x < n:
            if row[x] and not (logo and a <= x < b and a <= y < b):
                x0 = x
                while x < n and row[x] and not (logo and a <= x < b and a <= y < b):
                    x += 1
                runs.append(f'M{x0 + QUIET} {y + QUIET}h{x - x0}v1h-{x - x0}z')
            else:
                x += 1
    mark = ''
    if logo:   # the BY mark, centred in the clearing
        s = MARK
        o = QUIET + n / 2 - s / 2
        sx, sy, ss = STOP
        mark = (f'<g transform="translate({o:.3f} {o:.3f}) scale({s / 512:.6f})">'
                f'<path fill="{INK}" d="{BY}"/><rect x="{sx}" y="{sy}" width="{ss}" height="{ss}" fill="{ON_LIGHT["stop"]}"/></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" shape-rendering="crispEdges" role="img" aria-label="QR code for {URL}">'
            f'<rect width="{size}" height="{size}" fill="{PAPER}"/><path fill="{INK}" d="{"".join(runs)}"/>'
            f'<g shape-rendering="geometricPrecision">{mark}</g></svg>')


def wrap(svg_file, px):
    return (f'<!doctype html><html><head><style>html,body{{margin:0;background:#fff}}img{{display:block;width:{px}px;height:{px}px}}</style></head>'
            f'<body><img id="card" src="{svg_file}" alt=""></body></html>')


def phone_card_html(qr, lockup):
    shown = URL.split('://', 1)[1].rstrip('/')
    lw = (WM_X + WM_W + 96) / (512 + 96)   # lockup width / height
    return f'''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@500;600&family=Geist+Mono:wght@500&display=swap">
<style>
*{{box-sizing:border-box}}body{{margin:0}}
.c{{position:relative;width:1170px;height:2532px;background:#0b0c0d;color:#ededeb;font-family:Geist,sans-serif;overflow:hidden;display:flex;flex-direction:column;align-items:center}}
.c::before{{content:"";position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.13) 1.5px,transparent 1.8px);background-size:39px 39px;
  -webkit-mask-image:radial-gradient(ellipse 85% 55% at 50% 52%,#000 25%,transparent 78%);mask-image:radial-gradient(ellipse 85% 55% at 50% 52%,#000 25%,transparent 78%)}}
.c>*{{position:relative}}
.logo{{margin-top:560px;height:150px;width:{150 * lw:.0f}px;display:block}}
.lab{{font:500 30px/1 'Geist Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:#9a9da3}}
.k{{margin-top:44px}}
.tile{{margin-top:92px;width:810px;height:810px;background:#fff;border-radius:24px;padding:0;overflow:hidden}}
.tile img{{display:block;width:810px;height:810px}}
.url{{margin-top:84px;font:600 76px/1 Geist,sans-serif;letter-spacing:-.03em}}
.s{{margin-top:36px;color:#d4541a}}
</style></head><body><div class="c" id="card">
<img class="logo" src="{lockup}" alt="">
<span class="lab k">Mechanical engineering · Duke University</span>
<div class="tile"><img src="{qr}" alt=""></div>
<span class="url">{shown}</span>
<span class="lab s">Scan for my portfolio</span>
</div></body></html>'''


def main():
    brand = os.path.join(ROOT, 'assets', 'brand')
    os.makedirs(brand, exist_ok=True)
    with_mark, plain = qr_svg(matrix('q', logo=True), logo=True), qr_svg(matrix('m'))
    open(os.path.join(brand, 'qr-brianyue.svg'), 'w', encoding='utf-8').write(with_mark + '\n')
    open(os.path.join(brand, 'qr-brianyue-plain.svg'), 'w', encoding='utf-8').write(plain + '\n')
    tmp = tempfile.mkdtemp()
    try:
        files = {'mark.svg': with_mark, 'plain.svg': plain, 'lockup-dark.svg': lockup_svg(ON_DARK),
                 'mark.html': wrap('mark.svg', 2048), 'plain.html': wrap('plain.svg', 2048),
                 'phone.html': phone_card_html('mark.svg', 'lockup-dark.svg')}
        for n, s in files.items():
            open(os.path.join(tmp, n), 'w', encoding='utf-8').write(s)
        jobs = [('mark.html', 'qr-brianyue-2048.png'), ('plain.html', 'qr-brianyue-plain-2048.png'), ('phone.html', 'qr-phone-card.png')]
        jf = os.path.join(tmp, 'jobs.json')
        json.dump([{'html': os.path.join(tmp, h), 'out': os.path.join(brand, o), 'transparent': False} for h, o in jobs], open(jf, 'w'))
        subprocess.run(['node', os.path.join(ROOT, 'tools', 'brand_png.js'), jf], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'QR codes for {URL} written to assets/brand/')


if __name__ == '__main__':
    main()
