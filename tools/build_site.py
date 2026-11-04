#!/usr/bin/env python3
"""Generates every page of the site (index, about, personal, work/*, leadership/*).

All page text lives in this file. Edit it, then run:  python3 tools/build_site.py
This overwrites the generated .html files, so make content changes here, not in the HTML.
"""
import os, re, html, json

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the site folder
SCR = os.path.dirname(os.path.abspath(__file__))

SITE = 'https://brianyue.me'          # the live domain (Cloudflare)
EMAIL = 'brian.yue@duke.edu'
LINKEDIN = 'https://www.linkedin.com/in/brianyihanyue/'
DOI = 'https://doi.org/10.2514/6.2026-4344'

# The site logo (tools: assets/brand/). Colors come from CSS so it follows light/dark mode.
BRAND_MARK = '<svg class="mark" viewBox="0 0 512 512" aria-hidden="true" focusable="false"><rect class="m-bg" width="512" height="512" rx="112"/><path class="m-fg" transform="translate(67.0 348.3)" d="M51.68 3.42Q38.76 3.42 28.689999999999998 -3.6100000000000003Q18.62 -10.64 14.63 -24.89Q10.64 -39.14 15.58 -60.42L58.14 -243.2Q60.04 -250.04 58.33 -252.7Q56.62 -255.36 51.3 -255.74L39.9 -256.88Q34.2 -257.26 34.96 -261.82Q35.72 -265.24 40.28 -266.0Q53.96 -268.28000000000003 64.6 -271.51Q75.24 -274.74 81.7 -280.06Q84.74 -282.34 87.4 -282.34Q91.96000000000001 -282.34 90.82000000000001 -276.64L56.24 -127.3Q55.86 -124.64 57.379999999999995 -124.25999999999999Q58.9 -123.88 60.04 -126.16Q80.94 -166.06 97.47 -181.07Q114.0 -196.08 128.44 -196.08Q142.5 -196.08 150.67000000000002 -184.3Q158.84 -172.52 158.84 -149.72Q158.84 -128.06 152.57 -106.21000000000001Q146.3 -84.36 135.47 -64.6Q124.64 -44.84 110.77000000000001 -29.64Q96.9 -14.44 81.7 -5.51Q66.5 3.42 51.68 3.42ZM52.82 -6.08Q62.7 -6.08 73.72 -15.010000000000002Q84.74 -23.94 95.19 -38.95Q105.64 -53.96 114.0 -72.77Q122.36 -91.58 127.30000000000001 -111.53Q132.24 -131.48 132.24 -150.1Q132.24 -164.54 129.2 -170.43Q126.16 -176.32 118.56 -176.32Q110.2 -176.32 99.56 -166.06Q88.92 -155.8 77.9 -138.89000000000001Q66.88 -121.98 57.379999999999995 -102.22Q47.88 -82.46000000000001 42.18000000000001 -63.27Q36.480000000000004 -44.08 36.480000000000004 -29.26Q36.480000000000004 -6.08 52.82 -6.08ZM142.12 81.7Q127.67999999999999 81.7 119.69999999999999 74.28999999999999Q111.72 66.88 111.72 56.24Q111.72 48.26 115.9 44.269999999999996Q120.08 40.28 125.02 40.28Q132.24 40.28 135.28 44.08Q138.32 47.88 139.83999999999997 53.010000000000005Q141.35999999999999 58.14 144.58999999999997 61.94Q147.82 65.74 155.04 65.74Q169.1 65.74 182.77999999999997 54.53Q196.45999999999998 43.32 205.2 23.75Q213.94 4.18 212.8 -20.14L207.1 -156.56Q206.72 -166.44 203.68 -170.43Q200.64 -174.42000000000002 196.07999999999998 -174.42000000000002Q187.72 -174.42000000000002 180.12 -164.35000000000002Q172.51999999999998 -154.28 167.57999999999998 -126.16Q166.44 -121.22 162.64 -121.22Q157.32 -121.22 158.46 -128.06Q163.01999999999998 -154.28 171.19 -169.10000000000002Q179.35999999999999 -183.92000000000002 188.67 -190.0Q197.98 -196.08 205.95999999999998 -196.08Q217.74 -196.08 224.58 -187.91000000000003Q231.42000000000002 -179.74 232.18 -159.98L237.5 -14.06Q237.5 -11.4 239.21 -10.83Q240.92000000000002 -10.26 242.44 -12.540000000000001Q255.74 -31.16 266.57 -51.11Q277.4 -71.06 283.86 -90.44Q290.32 -109.82000000000001 290.32 -126.16Q290.32 -142.12 286.9 -151.43Q283.48 -160.74 279.87 -167.2Q276.26 -173.66 276.26 -181.26Q276.26 -196.08 289.18 -196.08Q307.41999999999996 -196.08 307.41999999999996 -155.8Q307.41999999999996 -133.76 299.82 -107.72999999999999Q292.22 -81.7 279.11 -54.910000000000004Q266.0 -28.12 249.09 -3.8000000000000007Q232.18 20.52 213.75 39.9Q195.32 59.28 176.89 70.49000000000001Q158.46 81.7 142.12 81.7Z"/><circle class="m-dot" cx="410.2" cy="326.3" r="22"/></svg>'

HEAD_SCRIPT = ("document.documentElement.classList.add('js');"
  "try{var th=localStorage.getItem('by-theme');if(th==='light'||th==='dark')document.documentElement.setAttribute('data-theme',th);}catch(e){}"
  "try{var q=location.search;if(/[?&]present=0/.test(q))sessionStorage.removeItem('by-present');"
  "else if(/[?&]present/.test(q))sessionStorage.setItem('by-present','1');"
  "if(sessionStorage.getItem('by-present')==='1'){document.documentElement.classList.add('present');document.documentElement.setAttribute('data-theme','light');}}catch(e){}"
  "window.addEventListener('error',function(e){var t=e.target;if(t&&t.tagName==='IMG'&&t.hasAttribute('data-logo')){t.remove();return;}if(!t||t.tagName!=='IMG'||!t.hasAttribute('data-dropin'))return;"
  "if(t.hasAttribute('data-optional')){var f=t.closest('figure');if(f){f.hidden=true;var r=f.closest('.figs');if(r&&!r.querySelector('figure:not([hidden])'))r.hidden=true;}return;}"
  "var b=t.closest('.frame,.media,.portrait');if(b){b.classList.add('is-missing');b.setAttribute('data-file',t.getAttribute('data-dropin'));}"
  "var a=t.closest('a[data-lightbox]');if(a){a.removeAttribute('href');a.removeAttribute('data-lightbox');}},true);")

# ---------------------------------------------------------------- page order
EXPER = ['shear-balance', 'ttbw']
PROJ = ['forward-closure', 'happy-meal', 'playseat']
LEAD = ['issdc', 'teaching', 'coaching']
ORDER = [('work', s) for s in EXPER + PROJ] + [('leadership', s) for s in LEAD]
GROUP_OF = {}
for _name, _lst in (('Work', EXPER + PROJ), ('Leadership', LEAD)):
    for _i, _s in enumerate(_lst):
        GROUP_OF[_s] = (_name, _i + 1, len(_lst))

# ---------------------------------------------------------------- helpers
def esc(s): return html.escape(s, quote=True)

def fig(src, alt, num, cap, w=None, h=None, mode='contain', group='g', ar=None, dropin=False, optional=False, pos=None):
    ar = ar or (w / h)
    cls = 'frame' + (' contain' if mode in ('contain', 'pad') else '') + (' pad' if mode == 'pad' else '')
    size = f' width="{w}" height="{h}"' if (w and h and not dropin) else ''
    extra = f' data-dropin="{src}"' if dropin else ''
    extra += ' data-optional' if optional else ''
    style = f' style="object-position: {pos}"' if pos else ''
    return (f'<figure style="--ar: {ar:.3f}"><div class="{cls}"><a href="{{{{P}}}}{src}" data-lightbox="{group}">'
            f'<img src="{{{{P}}}}{src}"{size} loading="lazy"{extra}{style} alt="{esc(alt)}"></a></div>'
            f'<figcaption><b>{num}</b>{cap}</figcaption></figure>')

def row(*figs, reveal=True):
    return f'<div class="row"{" data-reveal" if reveal else ""}>' + ''.join(figs) + '</div>'

def lead(src, alt, num, cap, w, h, mode='contain', group='g', pos=None):
    cls = 'frame' + (' contain' if mode in ('contain', 'pad') else '') + (' pad' if mode == 'pad' else '')
    style = f' style="object-position: {pos}"' if pos else ''
    return (f'<figure class="p-lead" data-reveal><div class="{cls}"><a href="{{{{P}}}}{src}" data-lightbox="{group}">'
            f'<img src="{{{{P}}}}{src}" width="{w}" height="{h}" fetchpriority="high"{style} alt="{esc(alt)}"></a></div>'
            f'<figcaption><b>{num}</b>{cap}</figcaption></figure>')

# ---------------------------------------------------------------- 3D models and video
# Media files come from tools/build_media.py, which writes media/<slug>.glb|.mp4 + .webp poster
# and records size, length and shape in tools/media.json.
try:
    MEDIA = json.load(open(os.path.join(SCR, 'media.json'), encoding='utf-8'))
except FileNotFoundError:
    MEDIA = {}

_I = {  # 20px stroke icons for the viewer buttons
  'rotate': '<path d="M20 12a8 8 0 1 1-2.34-5.66"/><path d="M20 4v4h-4"/>',
  'in': '<path d="M12 5v14M5 12h14"/>',
  'out': '<path d="M5 12h14"/>',
  'reset': '<path d="M4 10.5 12 4l8 6.5V20h-5.5v-5h-5v5H4z"/>',
  'full': '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
  'play': '<path d="M8 5.5v13l11-6.5z" fill="currentColor" stroke="none"/>',
  'pause': '<path d="M8 5v14M16 5v14"/>',
}
def _icon(k): return f'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_I[k]}</svg>'
def _btn(act, label, pressed=None):
    p = f' aria-pressed="{pressed}"' if pressed is not None else ''
    return f'<button type="button" data-act="{act}" aria-label="{label}" title="{label}"{p}>{_icon(act)}</button>'
def _mb(b): return f'{b / 1048576:.1f} MB' if b >= 1048576 else f'{max(1, round(b / 1024))} KB'
def _dur(s): s = int(round(s)); return f'{s // 60}:{s % 60:02d}'

def model3d(slug, alt, num, cap, ar=16/9, orbit=None, hotspots=(), lead=False, label='Interactive 3D', max_w=None):
    """A rotatable 3D model. hotspots: (position "x y z" in model units, normal "x y z", text) callouts."""
    m = MEDIA.get(f'{slug}.glb', {})
    orbit = orbit or m.get('orbit', '-35deg 65deg auto')
    hs = ''.join(f'<button type="button" class="hs" slot="hotspot-{i}" data-position="{p}" data-normal="{n}" data-visibility-attribute="visible"><span>{t}</span></button>'
                 for i, (p, n, t) in enumerate(hotspots, 1))
    size = f' · {_mb(m["bytes"])}' if m.get('bytes') else ''
    style = f'--ar: {ar:.3f}' + (f'; max-width: {max_w}px' if max_w else '')
    return (f'<figure class="m3d{" p-lead" if lead else ""}" data-reveal style="{style}"><div class="stage" data-cursor="Drag">'
            f'<model-viewer src="{{{{P}}}}media/{slug}.glb" poster="{{{{P}}}}media/{slug}.webp" alt="{esc(alt)}" camera-orbit="{orbit}" '
            f'camera-controls touch-action="pan-y" disable-zoom interaction-prompt="none" auto-rotate auto-rotate-delay="1200" '
            f'rotation-per-second="14deg" shadow-intensity="1" shadow-softness="0.8" environment-image="{{{{P}}}}assets/studio.hdr" exposure="1" '
            f'loading="lazy">{hs}<div class="bar" slot="progress-bar"></div></model-viewer>'
            f'<img class="fallback" src="{{{{P}}}}media/{slug}.webp" alt="{esc(alt)}" loading="lazy">'
            f'<span class="hud hud-tl">{label}{size}</span><span class="hud hud-bl" aria-hidden="true">Drag to rotate</span>'
            f'<div class="ctl" role="toolbar" aria-label="3D view controls">'
            + _btn('rotate', 'Auto-rotate', 'true') + _btn('in', 'Zoom in') + _btn('out', 'Zoom out')
            + _btn('reset', 'Reset view') + _btn('full', 'Full screen') +
            f'</div></div><figcaption><b>{num}</b>{cap}</figcaption></figure>')

def video(slug, alt, num, cap, loop=False, yt=None, lead=False, label=None, ar=None, max_w=None, poster=None):
    """loop=True: silent clip that plays while on screen (with a pause button).
    Otherwise a player: poster + play button, loads nothing until clicked.
    yt='VIDEO_ID' plays a YouTube video instead (no YouTube code loads until clicked).
    poster='images/x.webp' overrides the poster (e.g. a sharper one than YouTube's thumbnail)."""
    m = MEDIA.get(f'{slug}.mp4', {}) if slug else {}
    ar = ar or (m['w'] / m['h'] if m.get('w') else 16 / 9)
    style = f'--ar: {ar:.3f}' + (f'; max-width: {max_w}px' if max_w else '')
    poster = f'{{{{P}}}}{poster}' if poster else (f'{{{{P}}}}media/{slug}.webp' if slug else f'https://i.ytimg.com/vi/{yt}/hqdefault.jpg')
    if loop:
        label = label or 'Footage'
        inner = (f'<video src="{{{{P}}}}media/{slug}.mp4" poster="{poster}" muted loop playsinline preload="none" aria-label="{esc(alt)}" data-loop></video>'
                 f'<span class="hud hud-tl">{label}</span>'
                 f'<div class="ctl">' + _btn('pause', 'Pause video') + _btn('full', 'Full screen') + '</div>')
        cls, cur = 'vid loop', ''
    else:
        meta = ' · ' + _dur(m['dur']) if m.get('dur') else ''
        label = label or 'Video'
        src = f' data-yt="{esc(yt)}"' if yt else ''
        media_el = '' if yt else f'<video src="{{{{P}}}}media/{slug}.mp4" poster="{poster}" playsinline preload="none" aria-label="{esc(alt)}"></video>'
        inner = (media_el + f'<button type="button" class="start"{src} aria-label="Play video: {esc(alt)}">'
                 + (f'<img src="{poster}" alt="" loading="lazy">' if yt else '')
                 + f'<span class="ring">{_icon("play")}</span><span class="hud hud-bl">Play{meta}</span></button>'
                 f'<span class="hud hud-tl">{label}</span>')
        cls, cur = 'vid', ' data-cursor="Play"'
    return (f'<figure class="{cls}{" p-lead" if lead else ""}" data-reveal style="{style}"><div class="stage"{cur}>{inner}</div>'
            f'<figcaption><b>{num}</b>{cap}</figcaption></figure>')

def media(card, hover=True):
    """Card / next-project thumbnail. Roles show the organization logo at rest and the work on hover."""
    t = card['thumb']
    go = '<span class="go">View <span class="arrow">→</span></span>' if hover else ''
    if t['kind'] == 'type':
        inner = f'<div class="media type" aria-hidden="true"><span class="cap">{t["cap"]}</span> <span class="big">{t["big"]}</span>'
    else:
        cls = 'media' + {'cover': '', 'contain': ' contain', 'fit': ' fit'}[t['mode']] + (' tint' if t.get('tint') else '')
        mstyle = f' style="--tint: {t["tint"]}"' if t.get('tint') else ''
        style = f' style="object-position: {t["pos"]}"' if t.get('pos') else ''
        inner = f'<div class="{cls}"{mstyle}><img src="{{{{P}}}}{t["src"]}" loading="lazy"{style} alt="{esc(t["alt"])}">'
    org = card.get('org')
    if org and hover:
        lw = (f' style="--logo-w: {org["logo_w"]}' + (f'; --logo-h: {org["logo_h"]}' if org.get('logo_h') else '') + '"') if org.get('logo_w') else ''
        logo = f'<img class="logo" data-logo src="{{{{P}}}}{org["logo"]}"{lw} alt="{esc(org["name"])}">' if org.get('logo') else ''
        word_cls = 'word sm' if org.get('small') else 'word'
        inner += (f'<div class="org reveal" aria-hidden="true" style="--org-bg: {org["bg"]}; --org-fg: {org.get("fg", "#fff")}">'
                  f'{logo} <span class="{word_cls}">{org["word"]}</span> <span class="sub">{org["sub"]}</span></div>')
    return inner + go + '</div>'

def tags(lst): return '<ul class="tags">' + ''.join(f'<li>{esc(x)}</li>' for x in lst) + '</ul>'

# ---------------------------------------------------------------- personal data (personal/categories.js + gallery.js)
def _js_array(path, name):
    txt = open(os.path.join(OUT, path), encoding='utf-8').read()
    m = re.search(r'window\.' + name + r'\s*=\s*(\[.*\])\s*;', txt, re.S)
    return json.loads(m.group(1)) if m else []

def _slug(t):
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', str(t or 'personal').lower()))

def _icons():
    js = open(os.path.join(OUT, 'assets', 'site.js'), encoding='utf-8').read()
    block = re.search(r'var ICONS = \{(.*?)\n  \};', js, re.S).group(1)
    return dict(re.findall(r"(\w+): '([^']*)'", block))

def personal_data():
    items = [i for i in _js_array('personal/gallery.js', 'PERSONAL_GALLERY') if i.get('src')]
    cats = [dict(c, key=_slug(c.get('key') or c.get('title'))) for c in _js_array('personal/categories.js', 'PERSONAL_CATEGORIES')]
    for it in items:
        k = _slug(it.get('category'))
        if not any(c['key'] == k for c in cats):
            cats.append({'key': k, 'title': it.get('category') or 'Personal', 'blurb': ''})
    for c in cats:
        c['items'] = [it for it in items if _slug(it.get('category')) == c['key']]
        c['live'] = bool(c['items']) or bool(c.get('blurb'))
    return items, cats

ITEMS, CATS = personal_data()
HAS_PERSONAL = any(c['live'] for c in CATS)

def _count(c):
    n = len(c['items'])
    return (f'{n} photo' + ('' if n == 1 else 's')) if n else 'Coming soon'

def _cover(c):
    if not c['items']:
        return None
    if c.get('cover'):
        for it in c['items']:
            if c['cover'] in (it.get('orig') or ''):
                return it
    return c['items'][0]

def _when(it):
    import datetime
    try:
        return datetime.date.fromisoformat(it['taken']).strftime('%b %Y') if it.get('taken') else ''
    except ValueError:
        return ''

def render_personal(P):
    icons = _icons(); tiles = []; secs = []
    for i, c in enumerate(CATS):
        num = f'{i + 1:02d}'
        cov = _cover(c)
        if cov:
            media = f'<img src="{P}{esc(cov["src"])}" alt="" loading="lazy">'
        elif c['key'] in icons:
            media = f'<svg class="ptile-icon" viewBox="0 0 100 100" aria-hidden="true">{icons[c["key"]]}</svg>'
        else:
            media = ''
        cls = 'ptile' + ('' if c['items'] else ' type')
        meta = (f'<div class="ptile-meta"><div class="ptile-top"><span class="num">{num}</span> <span class="n">{_count(c)}</span></div> '
                f'<span class="t">{esc(c["title"])}</span></div>')
        if c['live']:
            tiles.append(f'<a class="{cls}" href="#{c["key"]}" data-cursor="Open"><div class="ptile-media">{media}</div>{meta}</a>')
        else:
            tiles.append(f'<div class="{cls}"><div class="ptile-media">{media}</div>{meta}</div>')
            continue
        label = f'{num} · {_count(c)}' if c['items'] else num
        blurb = f'<p>{esc(c["blurb"])}</p>' if c.get('blurb') else ''
        link = c.get('link') or {}
        if link.get('href'):
            blurb += f'<a class="pill" href="{P}{esc(link["href"])}">{esc(link.get("text") or "More")} <span class="arrow">→</span></a>'
        if c['items']:
            figs = []
            for it in c['items']:
                size = f' width="{it["width"]}" height="{it["height"]}"' if it.get('width') and it.get('height') else ''
                cap = esc(it.get('caption') or '')
                when = _when(it)
                capt = ''
                if cap or when:
                    capt = f'<figcaption>{cap}' + (f'<span class="when">{when}</span>' if when else '') + '</figcaption>'
                figs.append(f'<figure><div class="frame"><a href="{P}{esc(it.get("full") or it["src"])}" data-lightbox="p-{c["key"]}">'
                            f'<img src="{P}{esc(it["src"])}" loading="lazy" alt="{esc(it.get("alt") or it.get("caption") or "")}"{size}></a></div>{capt}</figure>')
            body = '<div class="masonry">' + ''.join(figs) + '</div>'
        else:
            body = '<p class="pcat-soon">Photos coming soon.</p>'
        secs.append(f'<section class="pcat" id="{c["key"]}" data-reveal><div class="pcat-head"><div><p class="label">{label}</p><h2>{esc(c["title"])}</h2></div>'
                    f'<div class="pcat-blurb">{blurb}</div></div>{body}</section>')
    return ''.join(tiles), ''.join(secs)

def render_teaser(P):
    chips = ''.join((f'<a class="pill" href="{P}personal.html#{c["key"]}">{esc(c["title"])}</a>' if c['live'] else
                     f'<a class="pill soon">{esc(c["title"])}</a>') for c in CATS)
    strip = ''.join(f'<a href="{P}{esc(it.get("full") or it["src"])}" data-lightbox="teaser"><img src="{P}{esc(it["src"])}" '
                    f'alt="{esc(it.get("alt") or it.get("caption") or "")}" loading="lazy"></a>' for it in ITEMS[:4])
    return chips, strip

SCHEMA = '<script type="application/ld+json">' + '{"@context": "https://schema.org", "@type": "Person", "name": "Brian Yue", "url": "https://brianyue.me/", "image": "https://brianyue.me/images/portrait.jpg", "email": "mailto:brian.yue@duke.edu", "jobTitle": "Mechanical engineering student", "affiliation": {"@type": "CollegeOrUniversity", "name": "Duke University", "url": "https://duke.edu"}, "knowsAbout": ["Mechanical design", "GD&T", "Finite element analysis", "Tolerance analysis", "Aerospace structures", "Machining"], "sameAs": ["https://www.linkedin.com/in/brianyihanyue/"]}' + '</script>\n'

# ---------------------------------------------------------------- shell
def page(title, desc, P, active, main, progress=False, path=None):
    def cur(k): return ' aria-current="page"' if active == k else ''
    MV = f'<script type="module" src="{P}assets/vendor/model-viewer.min.js"></script>\n' if '<model-viewer' in main else ''
    home = '' if active == 'home' else P + 'index.html'
    nav = (f'<a href="{home}#work"{cur("work")}>Work</a>'
           f'<a href="{home}#leadership"{cur("leadership")}>Leadership</a>'
           f'<a href="{P}about.html"{cur("about")}>About</a>'
           f'<a href="{P}personal.html" data-nav="personal"{cur("personal")}{"" if HAS_PERSONAL else " hidden"}>Personal</a>')
    menu_links = (f'<a href="{P}index.html"{cur("home")}>Home <span>00</span></a>'
                  f'<a href="{home}#work"{cur("work")}>Work <span>01</span></a>'
                  f'<a href="{home}#leadership"{cur("leadership")}>Leadership <span>02</span></a>'
                  f'<a href="{P}about.html"{cur("about")}>About <span>03</span></a>'
                  f'<a href="{P}personal.html" data-nav="personal"{cur("personal")}{"" if HAS_PERSONAL else " hidden"}>Personal <span>04</span></a>'
                  f'<a href="{P}resume.pdf" target="_blank" rel="noopener">Résumé <span>PDF</span></a>')
    canon = '' if path is None else f'\n<link rel="canonical" href="{SITE}/{path}">\n<meta property="og:url" content="{SITE}/{path}">'
    out = f'''<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#0b0c0d">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE}/images/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">{canon}
{SCHEMA if path in ('', 'about') else ''}<link rel="icon" href="{P}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{P}favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" href="{P}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap">
<link rel="stylesheet" href="{P}assets/site.css">
<script>{HEAD_SCRIPT}</script>
</head>
<body data-base="{P}">
<a class="skip" href="#main">Skip to content</a>
{'<div class="progress" aria-hidden="true"></div>' if progress else ''}
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="{P}index.html" aria-label="Brian Yue, home">{BRAND_MARK}<span class="wm">Brian Yue<span class="stop">.</span></span></a>
    <nav class="navpill" aria-label="Primary">{nav}</nav>
    <div class="bar-right">
      <button class="pill theme-btn" type="button" aria-label="Switch to light theme" title="Switch to light theme"><svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/></svg><svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg></button>
      <a class="pill solid" href="{P}resume.pdf" target="_blank" rel="noopener">Résumé <span class="arrow">↗</span></a>
      <button class="pill menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span>Menu</span></button>
    </div>
  </div>
</header>
<div class="menu" id="menu" inert>
  <nav aria-label="Menu">{menu_links}</nav>
  <a class="label menu-mail" href="mailto:{EMAIL}">{EMAIL}</a>
</div>

<main id="main">
{main}
</main>

<footer class="site-footer" id="contact">
  <div class="wrap">
    <p class="label" data-reveal>Contact</p>
    <a class="contact-big" href="mailto:{EMAIL}" data-reveal>{EMAIL}</a>
    <div class="actions" data-reveal>
      <button class="pill" type="button" data-copy="{EMAIL}">Copy email <span class="hint"></span></button>
      <a class="pill" href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn <span class="arrow">↗</span></a>
      <a class="pill" href="{P}resume.pdf" target="_blank" rel="noopener">Résumé <span class="arrow">↗</span></a>
    </div>
    <div class="foot-bar">
      <span>© 2026 Brian Yue</span>
      <span data-clock>Durham, NC</span>
      <a href="#main">Back to top ↑</a>
    </div>
  </div>
</footer>

<dialog class="lb" id="lightbox" aria-label="Image viewer">
  <div class="lb-inner"><img alt=""><p class="lb-cap"></p></div>
  <button class="lb-btn" type="button" data-close>Close</button>
  <button class="lb-btn lb-nav lb-prev" type="button" data-step="-1" aria-label="Previous image">‹</button>
  <button class="lb-btn lb-nav lb-next" type="button" data-step="1" aria-label="Next image">›</button>
</dialog>
<script src="{P}personal/categories.js"></script>
<script src="{P}personal/gallery.js"></script>
<script src="{P}assets/site.js"></script>
{MV}</body>
</html>
'''
    return out.replace('{{P}}', P)

# ---------------------------------------------------------------- the TTBW diagram (reused from the single-page build)
DIAGRAM = open(os.path.join(SCR, 'partials', 'ttbw-diagram.html'), encoding='utf-8').read().strip()

# ---------------------------------------------------------------- projects & leadership
P_ = {}

P_['shear-balance'] = dict(
  kind='work', num='01', cat='Instrument design', year='2026',
  title='Floating-element shear-force balance',
  desc='A floating-element shear-force balance for a subsonic wind tunnel: load path design, a GD&T drawing package, FEA, and a ~$159 carriage-and-rail redesign.',
  card_title='Floating-element shear-force balance',
  lede='Rerouted the load path onto about $159 of catalog parts after test data from a comparable instrument showed friction eroding ~40% of measured shear.',
  tags=['Onshape', 'GD&T', 'FEA', 'Instrumentation'],
  thumb=dict(kind='img', src='images/card-shear-balance.webp', mode='fit', alt='CAD render of the shear-force balance'),
  meta=[('Role', 'Designer, end to end'), ('When', 'June – August 2026'), ('Where', 'Turbulent Shear Flow Lab, NC State'), ('Advisor', 'Dr. Venkat Narayanaswamy')],
  lead=model3d('shear-balance', 'Interactive 3D model of the shear-force balance: a grey tunnel insert plate holding an aluminum frame and a light-blue floating plate, with a small rail, carriage and load cell on the rear face.',
               'Fig. 1', 'The full assembly in 3D. Drag to rotate. The rear face carries the rail, carriage and load cell; turn it over for the flush, flow-facing floating plate. The outer plate is the lab\'s existing tunnel insert, shown for context.',
               lead=True, hotspots=[('0.165 0.051 0.0345', '0 0 -1', 'Rail + carriage'), ('0.040 0.048 0.0425', '0 0 -1', 'Load cell'),
                                    ('0.262 0.024 0.0520', '0 0 -1', 'Floating plate'), ('0.230 0.051 0.0712', '0 0 1', 'Flow surface')]),
glance=[('Constraint', 'Held rigid in 5 degrees of freedom, free to slide in 1'), ('Sensing', 'Uniaxial load cell, single load path'), ('Fits', 'RC4 running and LC2 locational fits (ASME B4.1)'),
          ('Position tolerance', '⌀0.010 in true position (ASME Y14.5)'), ('Material', '6061 aluminum; 16 µin Ra finish on flow surfaces'), ('Comparable instrument', 'Friction eroded ~40% of measured shear'),
          ('Carriage + rail', 'About $159 of off-the-shelf parts'), ('Deliverables', '5-sheet drawing set, BOM')],
  sections=[
    ('challenge', 'The problem', '''<div class="prose"><p>Skin friction is a wall shear stress, and measuring it directly means letting a small element of the wall float free in one direction while holding it still in the other five. Every parallel path that load can take is measurement error. The instrument also had to fit inside a cavity that already existed in the lab's subsonic tunnel wall, so the envelope, the mounting, and the flow-facing surface were fixed before I drew anything.</p></div>'''),
    ('contribution', 'What was mine', '''<p class="contrib">Design, analysis, the drawing package, and the bill of materials were mine. The tunnel hardware, the cavity and the load cell were not: I designed into them. The male-female interface I started from was a grad student's design, and the idea of trying a carriage came from him; choosing the carriage and rail and designing them in was mine.</p>'''),
    ('process', 'Getting rid of friction', '''<div class="prose"><p>The hard part is that the plate has to be locked down in five directions and still slide almost freely in the sixth. Anything that holds it in place is also something it can rub against, and any rubbing shows up in the data as shear that isn't really there.</p>
<p>I started from a male-female interface adapted from a grad student's comparable instrument in the lab. Before anything was cut, he told me his test data showed friction in that interface eroding roughly 40% of the measured shear force, and that he had been experimenting with carriages. I scrapped the interface, found a ball-bearing carriage and rail that fit the cavity, and rerouted the load path onto them, redesigning the mobile plate so the carriage alone supports it. The carriage and rail came to about $159 in catalog parts.</p>
<p>I also made the plate height adjustable. Setting it lower leaves a recess where a viscoelastic layer of varying thickness can be cured in place.</p></div>
<div class="figs">''' + row(fig('images/balance-section-flow.webp', 'Section view along the flow axis showing the floating plate suspended inside the frame.', 'Fig. 2', 'Section along the flow axis. The mobile plate (light blue) floats and passes shear to the load cell only.', 1500, 178, group='balance')) +
      row(fig('images/balance-section-transverse.webp', 'Section view across the flow axis showing the carriage on its rail beneath the plate.', 'Fig. 3', 'Section along the transverse axis. The carriage and rail fix five degrees of freedom and leave the flow axis free.', 1068, 380, group='balance')) + '</div>'),
    ('outcome', 'The drawings', '''<div class="prose"><p>A five-sheet manufacturing drawing package and a bill of materials with vendor part numbers and unit costs. I modeled the assembly in Onshape and checked it under test loads with SolidWorks FEA.</p>
<p>Mating surfaces carry ASME B4.1 fit classes, the M4 pattern that holds the non-contact gap around the mobile plate carries a ⌀.010 true-position tolerance, and the flow-facing surfaces get a 16 Ra finish, because roughness there would change the quantity being measured. Choosing those numbers meant weighing what a university machine shop can hold against what the instrument needs.</p>
<p>Only two of the five parts start from raw stock. The other three are catalog or existing lab parts with features added, which keeps custom fabrication to a minimum.</p></div>
<div class="figs" data-reveal>
  <div class="sheets-head"><span class="label">Drawing package</span><span class="label">5 sheets · August 2026 · click to enlarge · <a class="link" href="{{P}}drawings/shear-balance-drawing-package.pdf" target="_blank" rel="noopener">PDF ↗</a></span></div>
  <div class="sheets">
    <a href="{{P}}images/dwg-1-panel-frame-2600.webp" data-lightbox="sheets" data-caption="Sheet 1 of 5 · Panel frame · 6061 Al, from stock. Click the drawing to zoom."><div class="frame"><img src="{{P}}images/dwg-1-panel-frame.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 1: panel frame"></div><span class="s-t">1 · Panel frame</span><span class="s-d">6061 Al, from stock</span></a>
    <a href="{{P}}images/dwg-2-panel-2600.webp" data-lightbox="sheets" data-caption="Sheet 2 of 5 · Panel · 6061 Al, from stock. Click the drawing to zoom."><div class="frame"><img src="{{P}}images/dwg-2-panel.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 2: panel"></div><span class="s-t">2 · Panel</span><span class="s-d">6061 Al, from stock</span></a>
    <a href="{{P}}images/dwg-3-l-bracket-2600.webp" data-lightbox="sheets" data-caption="Sheet 3 of 5 · L-bracket · Modified catalog part. Click the drawing to zoom."><div class="frame"><img src="{{P}}images/dwg-3-l-bracket.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 3: L-bracket"></div><span class="s-t">3 · L-bracket</span><span class="s-d">Modified catalog part</span></a>
    <a href="{{P}}images/dwg-4-sidewall-mounting-plate-2600.webp" data-lightbox="sheets" data-caption="Sheet 4 of 5 · Mounting plate · Modified lab hardware. Click the drawing to zoom."><div class="frame"><img src="{{P}}images/dwg-4-sidewall-mounting-plate.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 4: sidewall mounting plate"></div><span class="s-t">4 · Mounting plate</span><span class="s-d">Modified lab hardware</span></a>
    <a href="{{P}}images/dwg-5-carriage-rail-2600.webp" data-lightbox="sheets" data-caption="Sheet 5 of 5 · Carriage rail · Modified catalog part. Click the drawing to zoom."><div class="frame"><img src="{{P}}images/dwg-5-carriage-rail.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 5: carriage rail"></div><span class="s-t">5 · Carriage rail</span><span class="s-d">Modified catalog part</span></a>
  </div>
</div>'''),
    ('reflection', 'What I took away', '''<div class="prose"><p>I came out of this a lot more comfortable with GD&amp;T. Before, I mostly knew the symbols. Doing a full drawing package meant actually picking fit classes out of ASME B4.1, setting up datums and position tolerances to Y14.5, and being able to explain why every callout was there.</p>
<p>It also showed me how much the drawings matter. Nobody at the machine shop was going to call me and ask what I meant, so anything I left off the page just wasn't going to end up on the part.</p>
<p>Honestly, the most useful thing that happened on this project wasn't something I did. The grad student's friction data showed up before anything was cut, so switching interfaces cost me a redesign instead of a rebuild. Next time I'll go looking for data on similar hardware before I commit to a load path.</p></div>'''),
    ('skills', 'Skills', tags(['Onshape', 'SolidWorks Simulation', 'GD&T (ASME Y14.5)', 'Fits (ASME B4.1)', 'Tolerance analysis', 'Load path design', 'DFM', 'BOM'])),
  ])

P_['forward-closure'] = dict(
  kind='work', num='02', cat='Flight hardware', year='2025–',
  title='Unified forward closure', card_title='Unified forward closure',
  lede='Three solid rocket motor closures merged into one flight part.',
  tags=['SolidWorks FEA', 'Lathe', 'Mill', 'Seals'],
  thumb=dict(kind='img', src='images/closure-machined.webp', mode='cover', pos='50% 60%', alt='Partially machined forward closure'),
  meta=[('Role', 'Drove the redesign'), ('When', 'August 2025 – present'), ('Team', 'Duke Aero, Solid Propulsion (member since August 2024)'), ('Status', 'Flown')],
  lead=lead('images/closure-machined.webp', 'A partially machined aluminum forward closure on a shop bench, with two eye bolts threaded into its face and radial ports around its side.',
            'Fig. 1', 'Forward closure, partially machined.', 1600, 1200, mode='cover', group='closure', pos='50% 58%'),
  glance=[('Consolidation', '3 closures → 1'), ('Part count', '−67%'), ('Machining setups', 'Two fewer'), ('Ports', 'Hydrostatic + hot fire merged, sealed for flight'),
          ('Min. factor of safety', 'About 11 (preliminary design)'), ('Processes', 'Lathe, drill press, mill')],
  sections=[
    ('challenge', 'Three closures for one motor', '''<div class="prose"><p>We were machining three separate forward closures for one solid rocket motor: one for the hydrostatic proof test, one for static hot fire, and one for flight. That meant three parts and three machining setups for every motor, and two of those closures were done after one use.</p></div>'''),
    ('contribution', 'What was mine', '''<p class="contrib">I drove the redesign and did the modeling, the analysis, and the fastener and sealing evaluation. Machining was shared with teammates. The thermal and mechanical loads came from our team lead by way of OpenRocket, and teammates produced the final drawings.</p>'''),
    ('process', 'Merging the ports', '''<div class="prose"><p>Going from three closures to one cut the part count by 67% and got rid of two machining setups.</p>
<p>Most of the work was figuring out what each version really needed. The ports were the tricky part. The test closures need fill and instrumentation ports, and for flight you'd rather have no holes at all. I merged the hydrostatic and hot fire ports into one port that gets sealed for flight, so the same part works for all three without weakening the flight version.</p>
<p>I modeled it in Onshape, ran SolidWorks Simulation on a preliminary design to check factor of safety under flight loads, and ran a trade study comparing fastener patterns and seal configurations against the combustion chamber's specified thermal and mechanical loads and our assembly constraints, weighing manufacturability throughout. Duke Aero ultimately scrapped the sealing solution that came out of that study, so it isn't part of what flew, but the evaluation behind it was my work.</p></div>
<div class="figs">''' + model3d('closure', 'Interactive 3D model of the aluminum forward closure: a thick disc with a central bore, holes in its face, and radial ports around its side.', 'Fig. 2', 'The closure that flew, as modeled in Onshape. Drag to rotate, or zoom in on the ports.', max_w=820) + row(fig('images/closure-section.webp', 'Half-section CAD view of the closure showing the bore, seal grooves, and threaded holes.', 'Fig. 3', 'Section view of the final design.', 685, 619, group='closure'),
                       fig('images/closure-port.webp', 'Section through the closure showing an L-shaped internal passage from the face to the side port.', 'Fig. 4', 'Section through the merged hydrostatic / hot fire port.', 696, 450, group='closure')) + '</div>'),
    ('outcome', 'Hot fire and flight', '''<div class="prose"><p>My teammates and I machined the final parts on a lathe, drill press, and mill. The closure went through the April 2026 static hot fire, and the motor flew.</p></div>
<div class="figs"><div class="row" data-reveal style="max-width: 420px">''' + fig('images/closure-hotfire.webp', 'A solid rocket motor firing vertically on a test stand in a green field, its purple and orange plume rising into the sky.', 'Fig. 5', 'Static hot fire, April 2026, with the unified closure on the motor.', 1100, 1956, mode='cover', group='closure') + '</div></div>'),
    ('reflection', "What I'd change", '''<div class="prose"><p>The minimum factor of safety came out around 11, which is not a good number. It means the geometry was set by available stock, machinability, and handling rather than by load, and on a weight-critical vehicle that is mass we'd want back. I'd also verify the chamber pressure independently instead of taking it downstream of someone else's model, since every number after it depends on it.</p>
<p class="next-note">Next: researching head-end ignition ahead of a two-stage vehicle next year.</p></div>
<div class="figs">''' + row(fig('images/closure-fos.webp', 'SolidWorks factor-of-safety plot of the closure, mostly red, with a minimum factor of safety of 11.', 'Fig. 6', 'FEA on a preliminary design. Minimum FOS = 11.', 1400, 794, group='closure')) + '</div>'),
    ('skills', 'Skills', tags(['Onshape', 'SolidWorks Simulation (FEA)', 'Fastener & seal trade study', 'Pressure vessel design', 'Lathe', 'Mill', 'Drill press', 'DFM'])),
  ])

# The 53 references in AIAA 2026-4344, counted from the published reference list.
# Types: journal articles; conference papers ("Proceedings of ..."); NASA/CR and NASA TM
# reports plus workshop presentations; one set of MIT lecture notes (2002).
SRC_YEARS = {2002: 1, 2012: 2, 2013: 0, 2014: 0, 2015: 3, 2016: 1, 2017: 0, 2018: 2, 2019: 2,
             2020: 4, 2021: 4, 2022: 7, 2023: 8, 2024: 12, 2025: 7}
SRC_TYPES = [('Conference papers', 28), ('Journal articles', 18), ('Reports &amp; presentations', 6), ('Lecture notes', 1)]
assert sum(SRC_YEARS.values()) == 53 and sum(n for _, n in SRC_TYPES) == 53

def srcchart(num):
    ymax, tmax = 12, max(n for _, n in SRC_TYPES)
    years = list(SRC_YEARS)
    major = {2002, 2012, 2016, 2020, 2024}
    cols, xs = [], []
    for i, (y, n) in enumerate(SRC_YEARS.items()):
        tip = f'{y} · {n} source{"" if n == 1 else "s"}'
        edge = ' start' if i == 0 else (' end' if i >= len(years) - 2 else '')
        peak = f'<b class="sc-v">{n}</b>' if n == ymax else ''
        cols.append(f'<div class="sc-col{edge}" tabindex="0" style="--v:{n}" data-tip="{tip}" aria-label="{tip}"><i></i>{peak}</div>')
        xs.append(f'<span class="{"" if y in major else "minor"}">{y}</span>')
        if y == 2002:
            cols.append('<div class="sc-gap" aria-hidden="true"></div>')
            xs.append('<span class="sc-gap" aria-hidden="true"></span>')
    ticks = ''.join(f'<span class="sc-tick" style="--t:{t}"><em>{t}</em></span>' for t in (0, 4, 8, 12))
    rows = ''.join(f'<div class="sc-row"><span class="sc-k">{k}</span><span class="sc-track"><i style="--v:{n}"></i><b>{n}</b></span></div>' for k, n in SRC_TYPES)
    t_year = ''.join(f'<tr><th scope="row">{y}</th><td>{n}</td></tr>' for y, n in SRC_YEARS.items() if n)
    t_type = ''.join(f'<tr><th scope="row">{k}</th><td>{n}</td></tr>' for k, n in SRC_TYPES)
    return f'''<div class="figs" data-reveal><figure class="srcchart" style="--ymax:{ymax};--tmax:{tmax}">
  <div class="sc-grid">
    <div class="sc"><p class="sc-h" aria-hidden="true">By publication year</p>
      <div class="sc-plot" aria-hidden="true">{ticks}<div class="sc-cols">{''.join(cols)}</div></div>
      <div class="sc-x" aria-hidden="true">{''.join(xs)}</div></div>
    <div class="sc"><p class="sc-h" aria-hidden="true">By type</p>
      <div class="sc-rows" aria-hidden="true">{rows}</div></div>
  </div>
  <table class="sr-only"><caption>Sources by publication year</caption><thead><tr><th scope="col">Year</th><th scope="col">Sources</th></tr></thead><tbody>{t_year}</tbody></table>
  <table class="sr-only"><caption>Sources by type</caption><thead><tr><th scope="col">Type</th><th scope="col">Sources</th></tr></thead><tbody>{t_type}</tbody></table>
  <figcaption><b>{num}</b>All 53 sources in the review, counted from the paper's reference list. Most were published in 2020 or later.</figcaption>
</figure></div>'''

P_['ttbw'] = dict(
  kind='work', num='03', cat='Research · publication', year='2025–26',
  title='An Overview of Transonic Truss-Braced Wing Technology', card_title='Transonic truss-braced wing review',
  lede='Sole-author AIAA paper synthesizing 53 sources on what stands between the configuration and service.',
  tags=['AIAA 2026-4344', 'Aerostructures', 'Certification'],
  thumb=dict(kind='img', src='images/aiaa-foyer.webp', mode='cover', pos='65% 50%', alt='Brian Yue at the AIAA AVIATION Forum'),
  meta=[('Role', 'Sole author, presenter'), ('When', 'April 2025 – June 2026'), ('Advisor', 'Dr. Earl H. Dowell'), ('Venue', 'AIAA AVIATION Forum 2026')],
  lead='<figure class="p-lead" data-reveal>' + DIAGRAM + '<figcaption><b>Fig. 1</b>Why the strut matters. Schematic drawn for this page, not to scale; the moment curves come from a simple beam model, not from the paper.</figcaption></figure>',
  glance=[('Paper', f'<a href="{DOI}" target="_blank" rel="noopener">AIAA 2026-4344</a>'), ('Venue', 'AIAA AVIATION Forum, San Diego, June 8–12, 2026'),
          ('Sources', '53, from NASA, Boeing, academia, and international groups'), ('Slides', '<a href="{{P}}docs/aiaa-2026-4344-slides.pdf" target="_blank" rel="noopener">26-slide talk deck (PDF)</a>'), ('Funding', 'Bellman Gift Travel Grant, $1,747')],
  sections=[
    ('challenge', 'The question', '''<div class="prose"><p>A transonic truss-braced wing uses an external strut to carry part of the bending load, which lets the wing be much thinner and longer than a cantilever wing of the same weight. The aerodynamic case is strong, but it is fundamentally an aerostructural problem: the benefit of the ultra-high aspect ratio only pays off if the fuel savings survive the structural penalties that come with it.</p>
<p>What I wanted to know was what still stands between the configuration and service. A thorough summary of NASA-led work already existed; no review had pulled in the research from outside it.</p></div>'''),
    ('contribution', 'What was mine', '''<p class="contrib">Sole author. I reviewed and synthesized the literature, wrote the paper, and presented it at the 2026 AIAA AVIATION Forum in San Diego, with travel funded by a departmental grant. Dr. Dowell advised.</p>
<div class="figs">''' + row(fig('images/aiaa-sign.webp', 'Brian Yue in a navy suit and conference badge, standing in front of the AIAA AVIATION 2026 expo-hours sign.', 'Fig. 2', 'At AIAA AVIATION 2026 in San Diego, June 8–12.', 960, 1280, mode='cover', group='ttbw'),
                       fig('images/aiaa-foyer.webp', 'Brian Yue leaning on large blue AIAA letters in the conference foyer.', 'Fig. 3', 'Between sessions in the conference foyer.', 1280, 960, mode='cover', group='ttbw'),
                       fig('images/aiaa-logo.webp', 'Brian Yue standing beside a large AIAA logo display.', 'Fig. 4', 'The forum where I presented AIAA 2026-4344.', 1280, 960, mode='cover', group='ttbw', pos='60% 50%')) + '</div>'),
    ('process', 'Reading 53 sources', '''<div class="prose"><p>I worked through 53 sources from NASA, Boeing, and academic and international groups and organized them by discipline: aerodynamics, low-speed aerodynamics, structures and fatigue, aeroelasticity, sizing and MDO, aeroacoustics, icing, simulation, and systems integration. For each, I tracked what has been demonstrated and what is still open.</p></div>
<div class="figs">''' + row(fig('images/ttbw-paper.webp', 'Title and abstract of the paper An Overview of Transonic Truss-Braced Wing Technology by Brian Y. Yue.', 'Fig. 5', 'First page of AIAA 2026-4344.', 1100, 1025, group='ttbw'),
                       fig('images/ttbw-slide-title.webp', 'Title slide: An Overview of Transonic Truss-Braced Wing Technology, Brian Yue, AIAA AVIATION, 9 June 2026.', 'Fig. 6', 'Title slide from my talk. <a class="link" href="{{P}}docs/aiaa-2026-4344-slides.pdf" target="_blank" rel="noopener">Full 26-slide deck (PDF) ↗</a>', 1920, 1080, mode='cover', group='ttbw')) + '</div>' + srcchart('Fig. 7')),
    ('outcome', "What's still in the way", '''<div class="prose"><p><strong>Certification.</strong> The configuration is novel enough that the usual means of compliance don't transfer. Comparative analysis can't be relied on for icing because there is no operational history to compare against, and current icing simulation tools aren't validated for TTBW certification.</p>
<p>On noise, the baseline configuration clears FAA Stage 4 by about 23 EPNdB cumulative, but its sideline margin under Stage 5 is only 2.9 EPNdB, thin enough to be flagged as a certification risk even if modeling bias may explain part of it.</p>
<p><strong>Systems integration.</strong> The thin, high-aspect-ratio wing that makes the configuration efficient leaves little room for fuel, so proposals move tanks into the fuselage and struts, at some cost in L/D. Engine placement, the wing-fuselage junction, and control-surface layout get pulled along with it.</p></div>
<div class="figs">''' + row(fig('images/ttbw-noise-margins.webp', 'Chart of cumulative noise margin against certification year, with FAA Stage 3, 4, and 5 limits and TTBW predictions near minus 20 EPNdB.', 'Fig. 8', 'Cumulative noise margins vs. FAA limits. Figure by June et al. (2022), not my work; reproduced with citation in my review as Fig. 15.', 753, 324, group='ttbw'),
                       fig('images/ttbw-control-layouts.webp', 'Five candidate wing planforms with different arrangements of Krueger flaps, spoilers, flaps, ailerons, and flaperons; planform 4 is marked final.', 'Fig. 9', 'Control-surface layouts studied for the TTBW. Figure by Harrison et al. (2020), not my work; reproduced with citation as Fig. 16.', 851, 509, group='ttbw')) + '</div>'),
    ('reflection', 'The Q&amp;A', '''<div class="prose"><p>I rehearsed the talk more than a hundred times over three months and prepared answers for every question I could think of. Then a room of engineers who had spent their careers on this configuration asked about details I had never considered, used terms I had never heard, and questioned specifics of studies I had overlooked. I couldn't answer a single question.</p><p>After the session I tracked down the people who had asked, including two authors I had cited, and asked them to explain what they meant and how they had approached their studies. I'm still in touch with some of them. Walking up to them afterward was more uncomfortable than the Q&amp;A itself, and it was worth more than all hundred rehearsals.</p>
<p>At the forum I also sat in on technical panels and plenaries, met engineers on the expo floor, and joined the Rising Leaders speed-mentoring session.</p><p>The topic I keep coming back to is certification. With something this new, part of the engineering is figuring out how you'd even prove it's safe.</p></div>'''),
    ('skills', 'Skills', tags(['Literature synthesis', 'Technical writing', 'Aerodynamics', 'Aeroelasticity', 'MDO', 'Aeroacoustics', 'Conference presentation'])),
  ])

P_['happy-meal'] = dict(
  kind='work', num='03', cat='Product design · injection molding', year='2025',
  title='Celebration of Imagination: a Happy Meal train', card_title='Modular Happy Meal train',
  lede='A modular, injection-moldable toy train: kids swap the snap-fit heads to build it however they like, at $0.31 a unit.',
  tags=['Onshape', 'Modular design', 'DFM'],
  thumb=dict(kind='img', src='images/card-toy.webp', mode='cover', alt='Three 3D-printed train heads on a workbench'),
  meta=[('Role', 'Design engineer, most of the CAD'), ('When', 'Spring 2025'), ('Team', '3 people'), ('Shown at', 'Duke 2025 Toy Fair')],
  lead=lead('images/toy-heads.webp', 'Three 3D-printed train heads, orange, green, and purple, lined up on a workbench.',
            'Fig. 1', 'The three swappable train heads: standard, subway, and bullet.', 1600, 1200, mode='cover', group='toy', pos='50% 62%'),
  glance=[('Brief', 'Injection-moldable, mass-producible Happy Meal toy'), ('Production material', 'PETG (prototypes in PLA)'), ('Unit cost', '$0.31 in PETG'),
          ('Critical fit', 'Shaft collar bore ⌀10.11 ±0.01 mm on a ⌀10.16 mm axle'), ('Mate tolerance', '5.00 ±0.05 mm, head to chassis'), ('Safety', 'Passes the 1.25-inch choke-tube test')],
  sections=[
    ('challenge', 'The brief', '''<div class="prose"><p>Design a McDonald's Happy Meal toy that is attractive and cheap, can be injection molded, and can be mass-produced. The memo to the client weighed practicality, sustainability, safety, cost, ease of use, and looks, and the toy had to be safe for children aged 4 to 8, which means nothing small enough to choke on, even after a child takes it apart.</p></div>'''),
    ('contribution', 'Who did what', '''<p class="contrib">Three-person team with Saina Srivastava and Mariangle Mendez, all three of us working as engineers. I did most of the CAD in Onshape. We brainstormed, scored concepts, and 3D-printed prototypes together, and co-wrote the technical memo. For the Duke 2025 Toy Fair, I made the toy's video.</p>'''),
    ('process', 'From jet to train', '''<div class="prose"><p>Brainstorming started wide; an early favorite was a carrier jet with Toy Story soldiers. We narrowed the field with a weighted Pugh matrix that favored price above everything else, and the plain train won.</p></div>
<div class="figs" data-reveal><div class="glance" style="margin:0"><dl>
  <div><dt>Weights</dt><dd>Price 0.40 · Fun 0.30 · Safety 0.15 · Durability 0.15</dd></div>
  <div><dt>Train</dt><dd><strong>+0.55</strong>, selected</dd></div>
  <div><dt>Train with carriage</dt><dd>−0.10</dd></div>
  <div><dt>Plane</dt><dd>−0.55</dd></div>
</dl></div></div>
<div class="prose" style="margin-top:28px"><p>We split the train into a head, a chassis, and wheels. The head slides onto the chassis along a horizontal male/female mate, so it can't pop off upward during play but a child can swap it with little force. Shaft collars press onto the axles so the wheels can never come off. Every part extrudes along one axis to keep it injection-moldable, and the head and chassis are solid so they survive drops.</p>
<p>Our first prints didn't fit. The 3D printers hold about 0.1 mm, looser than the fits we had designed, so the head and chassis mated badly. We opened up the tolerances in the CAD for the printed prototypes, and because we had started CAD early, there was time to reprint.</p></div>
<div class="figs">''' + row(fig('images/toy-sketch-1.webp', 'Hand sketch of early concepts.', 'Fig. 2', 'Early concept sketch.', 900, 1193, group='toy'),
                       fig('images/toy-sketch-2.webp', 'Hand sketch of the train with rough dimensions in centimeters.', 'Fig. 3', 'Sizing sketch, 5 × 4 × 2.5 cm.', 900, 1193, group='toy'),
                       fig('images/toy-exploded.webp', 'Onshape exploded view of the train: top, head, mate, chassis, axle, wheel, and shaft collar.', 'Fig. 4', 'My exploded assembly in Onshape.', 889, 604, group='toy')) + model3d('toy-head', 'Interactive 3D model of the standard train head: a boiler with a smokestack and a cab, on a flat base that slides onto the chassis.', 'Fig. 5', 'The standard head in 3D, modeled in Onshape. Drag to rotate. The flat base is its half of the mate: every head slides onto the same chassis, so kids can swap and rebuild the train however they like.', max_w=820) + '''</div>'''),
    ('outcome', 'Choke tests and cost', '''<div class="prose"><p>Every detachable piece passed the choke-tube test in every orientation. The train is modular: three heads (standard, subway, and bullet) share one mate, so kids can swap them onto the chassis and rebuild the train however they like, and they work as collectibles. We only built three, but any new head drawn on the same mate would fit, so there's really no limit to how many designs there could be. In production PETG, the toy comes to $0.31 a unit, with one 100-ton press per head design running 100,000 units a week. We presented it at the Duke 2025 Toy Fair.</p>
<p>We put the tightest tolerance where safety needed it. The shaft collar bore is ⌀10.11 ±0.01 mm on a ⌀10.16 mm axle, a press fit that keeps the wheels on for good. The head mate is looser, at ±0.05 mm, since kids are supposed to pull the heads off.</p></div>
<div class="figs">''' + row(fig('images/toy-choke.webp', 'The train head and chassis resting on top of a choke test tube, too large to fall in.', 'Fig. 6', 'Passing the choke-tube test.', 1000, 1333, group='toy'),
                       fig('images/toy-final.webp', 'Orange 3D-printed train head mounted on a green chassis.', 'Fig. 7', 'Final head on its chassis, before wheels.', 1000, 1333, group='toy'),
                       fig('images/toy-section.webp', 'Cross-section of the train head CAD model showing it is solid.', 'Fig. 8', 'Section through the head: solid, for drop strength.', 1200, 934, group='toy')) +
      row(fig('images/toy-drawing-head.webp', 'Dimensioned drawing of a train head with 5.00 ±0.05 mm mate callouts.', 'Fig. 9', 'Toleranced drawing of one train head.', 1600, 689, group='toy'))
      + row(fig('images/toy-poster-1.webp', 'Toy Fair poster panels: an annotated photo of the orange train head on a green chassis, future plans for carriages and more heads, and a Celebration of Imagination title panel.', 'Fig. 10', 'Our Toy Fair poster, outside…', 936, 442, group='toy'),
            fig('images/toy-poster-2.webp', 'Toy Fair poster panels: train facts with photos of the heads, a safety panel showing the head too wide for the choke tube, and customer reviews.', 'Fig. 11', '…and inside. Designed by Saina Srivastava and Mariangle Mendez. Click to read it.', 936, 442, group='toy')) + '''</div>'''),
    ('reflection', 'Looking back', '''<div class="prose"><p>Starting early saved us. We had most of the CAD done before spring break, so when the first prints didn't fit we still had time to fix the tolerances and reprint instead of settling. I also liked how much that one mate did for us: it keeps the head on, lets kids swap it, and it's still easy to injection mold.</p></div>'''),
    ('skills', 'Skills', tags(['Onshape', 'Modular design', 'Pugh matrix', 'Tolerance analysis', 'Design for injection molding', '3D printing', 'Cost analysis', 'Technical memo'])),
  ])

P_['playseat'] = dict(
  kind='work', num='04', cat='Assistive device', year='2024',
  title='Accessible PlaySeat', card_title='Accessible PlaySeat',
  lede='A mobile play seat for a three-year-old, where one fit test moved the wheels and every requirement got a pass/fail test.',
  tags=['User testing', 'Fabrication', 'Requirements'],
  thumb=dict(kind='img', src='images/playseat-iso.webp', mode='cover', pos='45% 55%', alt='The finished PlaySeat with its tray'),
  meta=[('Role', 'Seating structure, fabrication'), ('When', 'September – December 2024'), ('Team', 'Team P-Play, 4 people · EGR 101'), ('Advisor', 'Dr. George Delagrammatikas')],
  lead=lead('images/playseat-iso.webp', 'The finished PlaySeat outdoors: a padded seat with a five-point harness on a white base, a clamp-on tray, a large three-spoke side wheel, and a black faux carbon-fiber front wing over the leg padding.',
            'Fig. 1', 'The finished chair, with its clamp-on tray.', 2000, 1500, mode='cover', group='playseat', pos='50% 58%'),
  glance=[('Timeline', '11 weeks, concept to delivery'), ('Verification', 'Fit test with client and caregivers; six pass/fail tests against target values, one by proxy'),
          ('Change from testing', 'Drive wheels moved forward, rear casters added'), ('Weight', '15.72 lb (target 20 lb or less)'),
          ('Materials', 'Polycarbonate base, acrylic spoilers with carbon-fiber vinyl, 3D-printed PLA cane mount'), ('Processes', 'Laser cutting, acrylic bending, manual machining')],
  sections=[
    ('challenge', 'Who it was for', '''<div class="prose"><p>A three-year-old with spinal conditions needed more upper-body support than any wheelchair on the market gave him, and without it he couldn't play with the other kids in his classroom. We had eleven weeks to find out what he and his caregivers actually needed, turn that into requirements we could measure, build to them, and test every one.</p>
<p>The chair had to let him reach the ground to play with toys on the floor, right himself after leaning, move on his own and get over obstacles, keep up with his peers, and be something he actually enjoyed sitting in.</p></div>'''),
    ('contribution', 'What was mine', '''<p class="contrib">I worked on the seating structure design and the fabrication, and shared requirements elicitation and verification testing with my teammates Anna Karius, Ethan Liao, and Julia Morgan.</p>'''),
    ('process', 'From sketch to fit test', '''<div class="prose"><p>We brainstormed about twenty concepts, cut them down to six, and scored those in a weighted Pugh matrix where mobility counted the most. Solution 8 won with 4.65, against 3.7 for the next best: a race-car seat whose bottom snaps in, with an adjustable headrest, a folding cane, and a lap tray.</p></div>
<div class="figs">''' + row(fig('images/playseat-sketch-8.webp', 'Hand sketch of Solution 8: a race-car style seat with a spoiler, an adjustable headrest, a foldable cane, and a seat that snaps in.', 'Fig. 2', 'Solution 8, the one we picked.', 672, 667, group='playseat'),
                       fig('images/playseat-sketch-12.webp', 'Hand sketch of Solution 12: an upright chair with two support straps, a removable leather seat, and large wheels.', 'Fig. 3', 'Solution 12, the runner-up.', 600, 554, group='playseat'))
      + row(fig('images/playseat-pugh.webp', 'Pugh matrix scoring six solutions on mobility, weight, durability, adjustability, aesthetics, and ease of cleaning; Solution 8 scores highest at 4.65.', 'Fig. 4', 'Our Pugh matrix. Mobility carried the most weight, at 0.3.', 1800, 808, group='playseat')) + '''</div>
<div class="prose" style="margin-top:28px"><p>Prototype #1 was cardboard, and #2 was the first real chair. Between them they showed us a weak wheel connection, a spoiler that was too long, wheels that were too small, a seat base that was hard to get out, exposed metal, and missing casters.</p></div>
<div class="figs">''' + row(fig('images/playseat-proto-1.webp', 'Cardboard mock-up of the seat with a tall back, cardboard side wheels, and a flat base.', 'Fig. 5', 'Prototype #1, in cardboard.', 550, 935, mode='cover', group='playseat'),
                       fig('images/playseat-proto-2.webp', 'The second prototype: a white booster highchair with a patterned seat cover, a tray, and a large side wheel, on a lab bench.', 'Fig. 6', 'Prototype #2, the first real chair.', 799, 935, mode='cover', group='playseat')) + '''</div>
<div class="prose" style="margin-top:28px"><p>We started from a booster highchair with a removable base and built around it: a five-point harness and foam padding for support, side wheels he can push himself, front casters so it turns in place, a cane attachment so caregivers can push him, and a clamp-on tray. He loves Formula 1, so it also got a faux carbon-fiber spoiler and front wing. Not looking like medical equipment ended up being one of our requirements.</p>
<p>A prototype fit test, our first validation against the real user, showed he couldn't reach the push rims. We'd written that requirement down and still gotten it wrong. Moving the drive wheels forward fixed the reach but shifted the center of gravity, so we added rear casters to balance it, which is why the final chair has casters front and back.</p></div>
<div class="figs">''' + row(fig('images/playseat-wheel.webp', "Close-up side view of the final chair's large three-spoke wheel, footrest, and small front caster.", 'Fig. 7', 'Three-spoke side wheel he propels himself, and a front caster for turning in place.', 1400, 965, group='playseat'),
                       fig('images/playseat-rear.webp', 'Rear view of the chair: a black faux carbon-fiber spoiler bolted across the seat back, and a grey mount holding a black cane.', 'Fig. 8', 'Rear view: the faux carbon-fiber spoiler and the cane mount.', 1200, 1600, mode='cover', group='playseat')) + '</div>'),
    ('outcome', 'Testing every requirement', '''<div class="prose"><p>We verified the finished chair against every requirement with a target value. All six passed: five directly, and durability by proxy, since two years of service can't be tested in eleven weeks. The chair was delivered to the client at the end of the build.</p></div>
<div class="figs">''' + row(fig('images/playseat-car63.webp', "The finished chair parked next to Duke Motorsports' Formula SAE car, number 63, with a helmeted driver in the car, outside Duke's engineering buildings.", 'Fig. 9', "The finished chair next to Duke Motorsports' car 63. He loves Formula 1, hence the wings and the spoiler.", 1500, 1125, mode='cover', group='playseat')) + '''</div>
<div class="figs" data-reveal><div class="vtable-wrap"><table class="vtable">
  <thead><tr><th scope="col">Criterion</th><th scope="col">Target</th><th scope="col">Test</th><th scope="col">Result</th></tr></thead>
  <tbody>
    <tr><th scope="row">Safety</th><td data-label="Target">No reachable gaps of 0.6 in (15 mm) or more</td><td data-label="Test">Measured every gap he could reach</td><td data-label="Result"><span class="pass">Pass</span> None 0.6 in or larger</td></tr>
    <tr><th scope="row">Support</th><td data-label="Target">Holds his head 80–100° from the ground</td><td data-label="Test">He leaned away from vertical and tried to return upright</td><td data-label="Result"><span class="pass">Pass</span> Stayed upright</td></tr>
    <tr><th scope="row">Mobility</th><td data-label="Target">10 ft or more in 20 s</td><td data-label="Test">Pushed across carpet, tile, concrete, and over toys</td><td data-label="Result"><span class="pass">Pass</span> All surfaces</td></tr>
    <tr><th scope="row">Aesthetics</th><td data-label="Target">A rating of 4 or more from him</td><td data-label="Test">He rated it on a scale he set himself</td><td data-label="Result"><span class="pass">Pass</span> 4, and visibly enjoyed it</td></tr>
    <tr><th scope="row">Durability</th><td data-label="Target">2 or more years of service</td><td data-label="Test">Verified by proxy: drop tests up to 4 ft, the most severe case we could run in 11 weeks</td><td data-label="Result"><span class="pass proxy">Proxy</span> Survived every drop. Service life itself was not tested.</td></tr>
    <tr><th scope="row">Weight</th><td data-label="Target">20 lb or less</td><td data-label="Test">Crane scale</td><td data-label="Result"><span class="pass">Pass</span> 15.72 lb</td></tr>
  </tbody>
</table></div></div>
<div class="figs">''' + row(fig('images/playseat-cane.webp', 'A black cane clamped into a grey 3D-printed mount on the back of the chair.', 'Fig. 10', 'The cane attachment lets a caregiver push the seat…', 1600, 1200, mode='cover', group='playseat'),
                       fig('images/playseat-cane-out.webp', 'The same mount with the cane lifted out, showing its two metal clamps.', 'Fig. 11', '…and lifts out of its printed mount.', 1600, 1200, mode='cover', group='playseat'),
                       fig('images/playseat-poster.webp', 'Team poster titled Creating an Accessible Seating Solution, with sections for motivation, project goals, design blocks, the final design with labeled features, the design criteria and testing table, conclusions, and acknowledgements.', 'Fig. 12', 'Our final poster. Click to read it full size.', 2400, 2400, group='playseat')) + '</div>'),
    ('reflection', 'Looking back', '''<div class="prose"><p>It's the smallest project here, but it taught me the most about requirements. Until we put him in the chair, ours were really just educated guesses. It also taught me to be upfront about what a test shows: a drop test can stand in for two years of use, but it doesn't prove it, so the table says "proxy" instead of "pass."</p>
<p>The next change would be foam inserts that come out more easily, so the seat can be resized as he grows.</p></div>'''),
    ('skills', 'Skills', tags(['Requirements elicitation', 'Requirements decomposition', 'Verification testing', 'User testing', 'Ergonomics', 'Laser cutting', 'Acrylic bending', 'Manual machining', 'Teamwork'])),
  ])

P_['issdc'] = dict(
  kind='leadership', num='01', cat='Team systems design · 2021–24', year='2021–24',
  title='Space settlement design', card_title='ISSDC: captain and advisor',
  lede='Operations design, including the construction and repair robots, and the atmospheric gas mix for a lunar settlement, for ISSDC proposals; named a Global Champion at Kennedy Space Center in 2023.',
  tags=['Captain', 'Global Champion', 'Robotics'],
  thumb=dict(kind='img', src='images/card-issdc.webp', mode='cover', alt='Dual-mode welding robot concept'),
  meta=[('Role', 'Captain, then student advisor'), ('When', 'September 2021 – August 2024'), ('Result', 'Global Champion, 2023'), ('My sections', 'Operations and robots; atmosphere gas mix')],
  lead=lead('images/issdc-robot-welder.webp', 'Rendering of a boxy robot on magnetic tank treads with RCS thrusters and two articulated arms ending in a laser welder with an oxygen sprayer and a nanobot dispenser; dimension arrows show 2 m, 3 m and 5 m.',
            'Fig. 1', 'My dual-mode welding configuration of the F1M8, a vendor robot. 3D model by Kelly Wang.', 980, 351, mode='pad', group='issdc'),
  glance=[('Result', 'Global Champion, 2023, Kennedy Space Center'), ('Also', 'Asia Regional Finals twice; Best Representor, China Finals 2021–22'),
          ('Format', 'Assigned team answers a request for proposal (RFP) in 24–48 hours'), ('Judges', 'Former NASA engineers')],
  sections=[
    ('challenge', 'How ISSDC works', '''<div class="prose"><p>ISSDC works a lot like a real aerospace proposal. You're put on a team with students you've often never met, you get a request for proposal, and you have 24 to 48 hours to design a whole settlement and present it to judges, many of them former NASA engineers.</p></div>'''),
    ('contribution', 'What was mine', '''<p class="contrib">On <strong>Bellevistat</strong>, Team Bread's proposal for the 30th ISSDC (2022–23), I designed nearly all of the operations and infrastructure section, including its construction and repair robots. On <strong>Alaskol</strong>, DAFC's lunar settlement and the winning design at the 2023 Global Finals, I designed the atmosphere's gas mix. I also built the team's design database and documented team strategy, which later teams worked from.</p>
<p class="contrib"><strong>Not mine:</strong> on Bellevistat, the structural, human factors, automation, and schedule and cost sections, though I added tables and figure labels to some of them; Kelly Wang built the 3D models of my robots. On Alaskol, everything but the gas mix, including the residential season calendar.</p>'''),
    ('process', 'Robots and air', '''<div class="prose"><p>Bellevistat is an orbital settlement for 7,850 people, built mostly by assembling prefabricated modules in orbit. I designed the robots that do that assembly. Looking back, I went at them the way I'd go at hardware now: start from something you can buy, then design around it.</p>
<p>The base is the F1M8, a multipurpose industrial robot offered by one of the competition's vendors, so effectively a COTS part. I configured it as a dual-mode welding robot: it flies in zero gravity on RCS thrusters and crawls along the hull on magnetic tank treads, so it only spends propellant when it has to. It carries two laser welders, each with an oxygen sprayer so the weld works in vacuum, and a magnetic clamp holds the two sections together while it welds. The robots ship as modules with magnets on their mating faces and assemble themselves on arrival.</p>
<p>Once construction ends, the same fleet becomes the settlement's ship-repair service. Swapping parts turns each robot into one of three types, eleven of each per fleet: cutting bots that remove damaged modules from a docked ship, grabber bots that fetch spares from cargo and hold them in place, and welding bots that attach them. Repurposing the construction fleet instead of building a second one kept the cost down.</p></div>
<div class="figs">''' + row(fig('images/issdc-robot-cutter.webp', 'The same robot fitted with a laser cutter on its arms.', 'Fig. 2', 'Repurposed as a cutting bot for ship repair.', 1273, 429, group='issdc'),
                       fig('images/issdc-robot-grabber.webp', 'The same robot fitted with magnetic plates on its arms.', 'Fig. 3', 'Repurposed as a grabber bot. Models by Kelly Wang.', 1097, 425, group='issdc')) + '''
<div class="row" data-reveal style="max-width: 620px">''' + fig('images/issdc-robot-clamp.webp', 'Rendering of a magnetic clamp: two electromagnets joined by a retractable screw that extends from 3 to 15 m.', 'Fig. 4', 'Magnetic clamp that holds sections together during welding.', 885, 441, group='issdc') + '''</div></div>
<div class="prose" style="margin-top:32px"><p>I also sized the settlement's life support and power from per-person and per-area assumptions:</p>
<ul>
  <li><strong>Air:</strong> an Earth-normal mix at 0.75 atm across 4.29 × 10⁸ m³ of pressurized volume, which works out to roughly 11,400 cargo containers of gas.</li>
  <li><strong>Power:</strong> 1.12 × 10⁸ kWh per day, summed from residential, industrial, agricultural, and warehouse demand, met by 3.37 × 10⁶ m² of solar panels with a reactor as backup. The panel area uses the competition program book's figure of 1.39 kW of electricity per m² of panel.</li>
</ul>
<p>Rechecking that power figure now: 1.39 kW per m² is about all the sunlight that reaches a panel near Earth, so it assumes the panels convert nearly all of it. At a realistic 30% efficiency the same load needs about 1.1 × 10⁷ m², roughly 3.4 times the area. That's the check I'd run now before using a number someone hands me.</p>
<p>Alaskol sits on the Moon next to mining operations. I gave each sector its own gas mix, and every number had a reason I had to defend:</p>
<ul>
  <li><strong>Residential:</strong> 28% oxygen, to make physical labor easier, at 50% humidity.</li>
  <li><strong>Industrial:</strong> oxygen down to 20.7% and humidity down to 40% to slow oxidation, but not bone-dry, because some moisture prevents static buildup.</li>
  <li><strong>Agricultural:</strong> carbon dioxide raised to 0.15% to help plants grow, but held below the level that would start acidifying the soil, at 70% humidity.</li>
</ul>
<p>One gap I'd close now: the slide gives the mix but not the total pressure, and 28% oxygen only makes sense with one. At sea-level pressure it's a fire risk. At a reduced cabin pressure it's the right call, because it holds the oxygen partial pressure near Earth's: 28% of 0.75 atm is 0.21 atm, the same as sea level. I'd state the pressure first.</p></div>
<div class="figs">''' + row(fig('images/issdc-bread-atmosphere.webp', 'Proposal page on community infrastructure with an air composition table and food production text.', 'Fig. 5', 'Bellevistat air composition and amounts.', 1100, 1424, group='issdc'),
                       fig('images/issdc-bread-power.webp', 'Proposal page with initial food quantity and power distribution tables.', 'Fig. 6', 'Bellevistat power budget.', 1100, 1424, group='issdc'),
                       fig('images/issdc-alaskol-atmosphere.webp', 'Proposal slide titled Atmosphere: a table of nitrogen, oxygen, carbon dioxide, and humidity for residential, industrial, and agricultural sectors, and a table of residential seasons.', 'Fig. 7', 'Alaskol atmosphere. The gas mix by sector (top table) is mine; the season calendar below it was a teammate&#39;s.', 1600, 900, group='issdc')) + '</div>'),
    ('outcome', 'Kennedy Space Center', '''<div class="prose"><p>I led a team to the Asia Regional Finals twice, was invited onto the Chinese national team for the 2022–23 Global Championship, and was named a Global Champion at Kennedy Space Center. After aging out as a competitor, I came back as a student advisor, and in November 2023 the ISSDC China organizing committee brought me on as a co-CEO for the China Finals: I helped manage one of the competing companies, taught its students STEM topics, and coached them on presenting.</p></div>
<div class="figs">''' + row(fig('images/issdc-presenting.webp', 'A video-call screenshot of a slide titled 5.3 Automation Devices showing a cleaning bot, delivery bot, and butler bot, with Brian Yue speaking in a video tile at the top right.', 'Fig. 8', 'Presenting for Grumbo, the fictional aerospace company ISSDC assigned our team (that\'s me, top right). The robots on this slide are teammates\' designs.', 1728, 1080, group='issdc'),
                       fig('images/issdc-alaskol-cover.webp', 'Title slide: ALASKOL, with a domed lunar habitat and the DAFC logo.', 'Fig. 9', 'Alaskol title slide, our winning Global Finals design. Art by teammates.', 1600, 900, mode='cover', group='issdc'))
      + row(fig('images/issdc-ksc-team.webp', 'The Chinese national team in front of the ISSDC screen at Kennedy Space Center, wearing medals, holding the trophy and a Chinese flag.', 'Fig. 10', "The Chinese national team after the 2023 Global Finals, with our medals and the trophy. I'm on the far right.", 1441, 1080, mode='cover', group='issdc'),
            fig('images/issdc-rocket-garden.webp', "Four students in suits holding a Chinese flag in the Kennedy Space Center rocket garden, with tall white rockets behind them.", 'Fig. 11', "In the Kennedy Space Center rocket garden during the finals. I'm on the left.", 1080, 1440, mode='cover', group='issdc'),
            fig('images/issdc-with-dad.webp', 'Brian Yue in a suit standing with his dad in front of the International Space Settlement Design Competition screen.', 'Fig. 12', 'With my dad at the Global Finals.', 1600, 1001, mode='cover', group='issdc')) + '<div class="row" data-reveal style="max-width: 560px">' + fig('images/issdc-china-finals.webp', 'Tsinghua International School students in navy varsity jackets holding the school banner in front of the ISSDC China Finals screen.', 'Fig. 13', "Our school's team at the ISSDC China Finals.", 1440, 1080, mode='cover', group='issdc') + '</div></div>'),
    ('reflection', 'What it taught me', '''<div class="prose"><p>You hand off work and trust it comes back, and you decide fast which parts of the problem are worth the time you have left. That carries straight over to engineering.</p>
<p>The Global Finals gave us 24 hours to design and present a moon base. Under that deadline, with no sleep, it would have been easy to lift designs from NASA and other legacy projects and present them as ours. I wouldn't, and pushed for our own work instead. Every design decision had to be ours, and defensible.</p>
<p>Alaskol's gas mix is where that stuck. I was drilled on every one of those numbers: why more oxygen where people live, why any humidity at all in a factory, why stop the carbon dioxide at 0.15%. It taught me to justify every design decision I make.</p></div>'''),
    ('skills', 'Skills', tags(['Robotics concept design', 'COTS integration', 'Operations planning', 'Life-support sizing', 'Trade studies', 'Technical writing', 'Team leadership', 'Presenting to judges'])),
  ])

P_['teaching'] = dict(
  kind='leadership', num='02', cat='Teaching', year='2025–',
  title='Undergraduate Teaching Assistant', card_title='Teaching assistant, EGR 105 & ME 221',
  lede='Teaching EGR 105, Computing for Engineers, and grading for ME 221, Structure and Properties of Solids.',
  tags=['EGR 105', 'ME 221', 'Mentoring'],
  thumb=dict(kind='type', big='EGR 105', cap='Computing for Engineers · since 2025'),
  meta=[('Role', 'Undergraduate TA'), ('When', 'August 2025 – present'), ('Courses', 'EGR 105 (teaching), ME 221 (grading)'), ('Where', 'Duke University')],
  lead='',
  glance=[('EGR 105', 'Computing for Engineers, since fall 2025: office hours, lab sections, one-on-one sessions'), ('ME 221', 'Structure & Properties of Solids: grading'), ('Students', '39 in EGR 105, 39 in ME 221')],
  sections=[
    ('challenge', 'The job', '''<div class="prose"><p>I've been a teaching assistant for EGR 105, Computing for Engineers, since fall 2025, and I grade for ME 221, Structure and Properties of Solids. I have a section of 39 students in each course. In EGR 105, students come in with very different backgrounds, and the work spans coding projects, lab work, mini-activities, and problem sets. In ME 221, my job is grading.</p></div>'''),
    ('contribution', 'What I do', '''<p class="contrib">In EGR 105, I hold weekly office hours, lead lab sections, and run one-on-one sessions, and I review student projects, quizzes, and lab work. In ME 221, I grade.</p>'''),
    ('process', 'How I teach', '''<div class="prose"><p>I break hard concepts down into their fundamentals and teach the process instead of supplying answers. When I review EGR 105 work, I give feedback, suggest more efficient approaches where they exist, and recommend specific changes for resubmission.</p></div>
<div class="figs">''' + row(fig('images/teaching.jpg', 'Teaching a lab section.', 'Fig. 1', 'Teaching.', ar=1.5, mode='cover', group='teaching', dropin=True, optional=True)) + '</div>'),
    ('reflection', "What it's taught me", '''<div class="prose"><p>Teaching has taught me a lot of the same things coaching did, mostly how to lead and how to break a hard idea down into its basics. When a student is stuck, giving them the answer almost never helps. Finding the one basic idea they're missing usually does, and I've started working through my own problems the same way.</p></div>'''),
    ('skills', 'Skills', tags(['Technical communication', 'Python', 'Materials science', 'Mentoring', 'Feedback'])),
  ])

P_['coaching'] = dict(
  kind='leadership', num='03', cat='Coaching · 2020–24', year='2020–24',
  title='Student coach', card_title='Student coach, volleyball & basketball',
  lede='Assistant coach, then head coach of two middle school teams, while a full-time student-athlete.',
  tags=['Head coach', 'Volleyball', 'Basketball'],
  thumb=dict(kind='img', src='images/coaching-timeout.webp', mode='cover', alt='Coaching during a timeout'),
  meta=[('Role', 'Assistant, then head coach'), ('When', 'September 2020 – May 2024'), ('Where', 'Tsinghua International School, Beijing'), ('Teams', 'Volleyball, basketball')],
  lead='''<div class="p-lead stats" data-reveal>
  <div><div class="big">3</div><div class="cap">Teams coached: boys' volleyball, girls' volleyball, girls' basketball</div></div>
  <div><div class="big">2nd</div><div class="cap">Girls' basketball, ISAC U14 Division III, 2020–21, as assistant coach</div></div>
  <div><div class="big">3rd</div><div class="cap">Girls' basketball, ISAC U14 Division IV, 2022–23, as assistant coach</div></div>
</div>''',
  glance=[('Started as', 'Assistant coach, three middle school teams'), ('Senior year', 'Head coach, girls\' volleyball and girls\' basketball'), ('Alongside', 'Full-time student-athlete')],
  sections=[
    ('challenge', 'The teams', '''<div class="prose"><p>I started as an assistant coach for the middle school boys' volleyball, girls' volleyball, and girls' basketball teams at Tsinghua International School, and in my senior year became head coach of girls' volleyball and girls' basketball, all while playing as a full-time student-athlete.</p></div>
<div class="figs">''' + row(fig('images/coaching-bball-squad.webp', 'The Tsinghua International School middle school girls basketball program in Spartans jerseys, posed in the gym with their coaches; Brian Yue stands at the far right in a black polo.', 'Fig. 1', "The girls' basketball program. I'm on the far right.", 1080, 624, mode='cover', group='coaching'),
                       fig('images/coaching-vball-white.webp', 'The middle school girls volleyball team in white jerseys in front of the net with their coaches; Brian Yue stands at the far left.', 'Fig. 2', "The girls' volleyball team. I'm on the far left.", 1624, 1080, mode='cover', group='coaching'))
      + row(fig('images/coaching-bball-team.webp', 'A girls basketball team posed under a hoop in front of a climbing wall, with Brian Yue standing at the right in a black polo.', 'Fig. 3', "With one of the girls' basketball teams. I'm standing at right.", 1080, 717, mode='cover', group='coaching'),
            fig('images/coaching-vball-dark.webp', 'The middle school girls volleyball team in dark jerseys in front of the net with their student coaches.', 'Fig. 4', "The girls' volleyball team in their dark kit, with the student coaches.", 1619, 1080, mode='cover', group='coaching')) + '</div>'''),
    ('contribution', 'What I did', '''<p class="contrib">I ran practices, set lineups, gave individual feedback and advice, tracked and analyzed statistics, and managed rosters across multiple teams.</p>'''),
    ('outcome', 'Results', '''<div class="prose"><p>Both placements came with the girls' basketball team while I was an assistant coach, before my senior year: second in ISAC U14 Division III in 2020–21, and third in Division IV in 2022–23.</p></div>
<div class="figs">''' + row(fig('images/coaching-instruction.webp', 'Brian Yue, in a white sweater and holding a volleyball, pointing across the court while giving instructions at practice.', 'Fig. 5', 'Running a girls\' volleyball practice.', 1070, 1080, mode='cover', group='coaching', pos='40% 50%'),
                       fig('images/coaching-timeout.webp', 'Brian Yue, in a Spartans coaching shirt, kneeling with a tactics board while players gather around during a timeout.', 'Fig. 6', 'A timeout: drawing up the next rotation.', 1311, 843, mode='cover', group='coaching'),
                       fig('images/coaching-with-coach.webp', 'Brian Yue talking with a fellow coach courtside, clipboard in hand.', 'Fig. 7', 'Talking through the lineup with a fellow coach.', 1928, 1080, mode='cover', group='coaching'))
      + row(fig('images/coaching-bench.webp', 'The girls basketball bench during a game: players in Spartans jerseys cheering and clapping, with the coaching staff seated at the end of the bench and Brian Yue, in a suit, clapping on the right.', 'Fig. 8', "On the bench during a girls' basketball game. I'm on the right, in the suit.", 1182, 665, mode='cover', group='coaching')) + '</div>'),
    ('reflection', 'What it taught me', '''<div class="prose"><p>Coaching is where I first learned to lead, and to break something complicated into small pieces. A play only works once every kid knows their own part in it, so I'd teach it one piece at a time and then put it back together. I still learn and explain engineering that way.</p>
<p>It also taught me to plan for things going wrong, because they always did. Almost no practice or game went the way I'd drawn it up, so I came in with backups and changed things on the fly.</p></div>'''),
    ('skills', 'Skills', tags(['Leadership', 'Planning', 'Statistics', 'Feedback', 'Time management'])),
  ])

CARD = {
  'shear-balance': dict(card_title='Floating-element shear-force balance', status=['Internship · NC State', 'Finished'], dates='Jun 2026 → Aug 2026',
      lede="I did the design, the FEA and the five-sheet drawing package. Friction data from a grad student's similar rig talked me into a $159 ball-bearing carriage.",
      org=dict(word='NC STATE', sub='Turbulent Shear Flow Laboratory', name='NC State University', bg='#cc0000', logo='images/logo-ncstate.svg', logo_w='78%'),
      thumb_tint='#e9edf3'),
  'ttbw': dict(card_title='Transonic truss-braced wing review', status=['Research · Duke', 'Published'], dates='AIAA AVIATION · Jun 2026',
      lede="I wrote this AIAA paper on my own from 53 sources, then presented it at AVIATION 2026 with two of the authors I'd cited in the room.",
      org=dict(word='DUKE', sub='Mechanical Engineering &amp; Materials Science', name='Duke University', bg='#00539b', logo='images/logo-duke.svg', logo_h=17)),
  'forward-closure': dict(card_title='Unified forward closure', status=['Project', 'Flown'], dates='Duke Aero · Aug 2025 → present',
      lede='We used to machine three forward closures for every motor. I redesigned them as one part, and that part flew.',
      org=dict(word='DUKE AERO', sub='Solid Propulsion', name='Duke AERO', bg='#1d6363', logo='images/logo-duke-aero.svg', logo_w='70%')),
  'happy-meal': dict(card_title='Modular Happy Meal train', status=['Project', 'Toy Fair 2025'], dates='Duke · Spring 2025',
      lede='A Happy Meal train with heads kids can swap to build their own. I did most of the CAD, and it costs $0.31 to make.',
      org=dict(word='EGR CORP', sub='Toy design · 2025 Toy Fair', name='EGR Corp', bg='#ffffff', fg='#1d1f24', logo='images/logo-egr-corp.webp', logo_w='88%', logo_h='70%')),
  'playseat': dict(card_title='Accessible PlaySeat', status=['Project', 'Delivered'], dates='Duke EGR 101 · Sep 2024 → Dec 2024',
      lede='A play seat for a three-year-old who loves Formula 1. The first time he sat in it, we learned the wheels were in the wrong place.',
      org=dict(word='DUKE', sub='EGR 101 · Engineering Design', name='Duke University', bg='#0577b1', logo='images/logo-duke.svg')),
  'issdc': dict(card_title='ISSDC captain, then advisor', status=['Leadership', 'Global Champion'], dates='Sep 2021 → Aug 2024',
      lede='Three years of designing space settlements against the clock. My company won the 2023 Global Finals at Kennedy Space Center.',
      org=dict(word='ISSDC', sub='Space settlement design', name='International Space Settlement Design Competition', bg='#0b0d12', logo='images/logo-issdc.webp', logo_w='40%', logo_h='58%')),
  'teaching': dict(card_title='Teaching assistant, Duke', status=['Leadership', 'Ongoing'], dates='Aug 2025 → present',
      lede='I TA EGR 105, the computing class I took my first semester, and grade for ME 221.',
      org=dict(word='EGR 105<br>ME 221', sub='EGR 105 · ME 221 · Teaching Assistant', name='Duke University', bg='#012169', small=True, logo='images/logo-duke.svg', logo_h=17)),
  'coaching': dict(card_title='Student coach, Tsinghua International School', status=['Leadership', 'Finished'], dates='Sep 2020 → May 2024',
      lede='I coached middle schoolers in Beijing for four years while playing varsity myself, and ended up head coach of two teams.',
      org=dict(word='TIS', sub='Athletics · Beijing', name='Tsinghua International School', bg='#82318e', logo='images/logo-tis.webp', logo_w='84%')),
}
for _slug, _extra in CARD.items():
    _tint = _extra.pop('thumb_tint', None)
    P_[_slug].update(_extra)
    if _tint: P_[_slug]['thumb']['tint'] = _tint

# ---------------------------------------------------------------- build project pages
def next_of(i): return ORDER[(i + 1) % len(ORDER)]

def card(slug, P, delay=0.0):
    d = P_[slug]
    href = f'{P}{d["kind"]}/{slug}.html'
    status = ' '.join(f'<span class="{"k" if n == 0 else ""}">{x}</span>' for n, x in enumerate(d['status']))
    return f'''<article class="card" data-reveal style="--d:{delay:.2f}s">
  <a href="{href}" data-cursor="View">
    {media(d)}
    <div class="card-info"><h3>{d["card_title"]}</h3> <div class="status">{status}</div> <span class="dates">{d["dates"]}</span> <p>{d["lede"]}</p></div>
  </a>
</article>'''

LOGO_AR = {'images/logo-duke-aero.svg': 3405 / 966, 'images/logo-ncstate.svg': 121.25 / 11, 'images/logo-duke.svg': 140 / 50,
           'images/logo-egr-corp.webp': 604 / 246, 'images/logo-issdc.webp': 1.0, 'images/logo-tis.webp': 1600 / 274}
LOGO_SCALE = {'images/logo-duke-aero.svg': 1.3, 'images/logo-egr-corp.webp': 1.5, 'images/logo-issdc.webp': 1.1}

def org_mark(d, P):
    """Small single-color organization mark for the project banner (a mask in the page's ink color, so it never clashes)."""
    o = d.get('org')
    if not o or not o.get('logo'):
        return ''
    ar = LOGO_AR.get(o['logo'], 2.5)
    h = (60 if ar < 1.4 else 44) * LOGO_SCALE.get(o['logo'], 1.0)   # thin or detailed marks get a little more room
    w = ar * h
    if w > 200:
        w, h = 200, 200 / ar
    src = f'{P}{o["logo"]}'
    sub = re.sub(r'<[^>]+>', ' ', o.get('sub', ''))
    return (f'<aside class="p-org fade-in" style="--d:.35s">'
            f'<span class="p-org-logo" role="img" aria-label="{esc(o["name"])}" style="--w:{w:.0f}px;--h:{h:.0f}px;--ar:{ar:.3f};-webkit-mask-image:url({src});mask-image:url({src})"></span>'
            f'<span class="label">{sub}</span></aside>')

# Key numbers under each project banner, all visible at once (same box style as the coaching stats).
# Every figure is stated on that page; keep them in sync if a page changes.
NUMS = {
    'shear-balance': [('$159', 'carriage and rail'), ('~40%', 'of measured shear lost to friction in the old interface'),
                      ('5 / 1', 'degrees of freedom held / free'), ('⌀.010', 'true position on the M4 pattern'),
                      ('16 Ra', 'finish on the flow-facing surfaces'), ('5', 'drawing sheets')],
    'forward-closure': [('3 → 1', 'closures per motor'), ('67%', 'fewer parts'), ('2', 'machining setups cut'),
                        ('1', 'port for both hydrostatic and hot fire'), ('Apr 2026', 'static hot fire'), ('Aug 2024', 'on Duke Aero since')],
    'ttbw': [('53', 'sources'), ('9', 'disciplines covered'), ('~23 EPNdB', 'cumulative margin to FAA Stage 4'),
             ('2.9 EPNdB', 'sideline margin under Stage 5'), ('100+', 'rehearsals before the talk'), ('$1,747', 'travel grant')],
    'happy-meal': [('$0.31', 'per unit in PETG'), ('3', 'swappable heads'), ('±0.01 mm', 'shaft collar bore'),
                   ('+0.55', 'Pugh score for the train'), ('100,000', 'units a week per press'), ('1.25 in', 'choke tube, passed')],
    'playseat': [('6 / 6', 'requirements verified, 1 by proxy'), ('15.72 lb', 'against a 20 lb target'), ('11', 'weeks, concept to delivery'),
                 ('4 ft', 'highest drop test survived'), ('10 ft / 20 s', 'mobility target, met on every surface'), ('0.6 in', 'largest gap allowed')],
    'teaching': [('78', 'students, 39 in each course'), ('2', 'courses, EGR 105 and ME 221'), ('2nd', "year TA'ing EGR 105")],
    'issdc': [('1st', '2023 Global Finals, Kennedy Space Center'), ('24–48 h', 'to design a settlement'), ('7,850', 'residents on Bellevistat'),
              ('33', 'repair robots, 11 of each type'), ('28%', 'residential oxygen on Alaskol'), ('0.15%', 'agricultural CO₂ on Alaskol')],
}

def nums_grid(slug):
    nums = NUMS.get(slug)
    if not nums:
        return ''
    cells = ''.join(f'<div><div class="big">{n}</div><div class="cap">{t}</div></div>' for n, t in nums)
    return f'<div class="stats nums" data-reveal>{cells}</div>\n  '

def project_page(i, kind, slug):
    d = P_[slug]; P = '../'
    gname, gi, gn = GROUP_OF[slug]
    back_href = '../index.html#' + ('work' if kind == 'work' else 'leadership')
    back_label = 'All work' if kind == 'work' else 'All leadership'
    count = f'{gname} {gi:02d} / {gn:02d}'
    meta = ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in d['meta'])
    glance = ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in d['glance'])
    toc = ''.join(f'<li><a href="#{sid}"><span>{n + 1:02d}</span>{name}</a></li>' for n, (sid, name, _) in enumerate(d['sections']))
    secs = ''.join(f'''
      <section class="p-sec" id="{sid}" data-reveal>
        <h2><span class="n">{n + 1:02d}</span>{name}</h2>
        {body}
      </section>''' for n, (sid, name, body) in enumerate(d['sections']))
    todo = f'\n      <!-- TODO: {d["todo"]} -->' if d.get('todo') else ''
    nk, ns = next_of(i); nd = P_[ns]
    main = f'''
<section class="p-hero">
  <div class="wrap">
    <div class="crumbs fade-in" style="--d:.05s">
      <a class="pill" href="{back_href}"><span class="arrow">←</span> {back_label}</a>
      <span class="label">{count}</span>
    </div>
    <div class="p-head">
      <div>
        <p class="label accent fade-in" style="--d:.1s">{d["cat"]}</p>
        <h1 class="split">{d["title"]}</h1>
        <p class="p-lede fade-in" style="--d:.55s">{d["lede"]}</p>
      </div>
      {org_mark(d, P)}
    </div>
    <dl class="meta-grid fade-in" style="--d:.7s">{meta}</dl>
  </div>
</section>

<div class="wrap">
  {nums_grid(slug)}{d["lead"]}
  <div class="p-body">
    <aside class="toc" aria-label="On this page"><p class="label">On this page</p><ol>{toc}</ol></aside>
    <div>
      <div class="glance" data-reveal><dl>{glance}</dl></div>{secs}{todo}
    </div>
  </div>
</div>

<section class="next">
  <div class="wrap">
    <a href="../{nk}/{ns}.html" data-cursor="Next">
      <div><p class="label">Next · {GROUP_OF[ns][0]}</p><p class="t">{nd["card_title"]} <span class="arrow">→</span></p></div>
      {media(nd, hover=False)}
    </a>
  </div>
</section>'''
    title = f'{html.unescape(d["card_title"])} · Brian Yue'
    return page(title, d.get('desc') or d['lede'], P, kind, main, progress=True, path=f'{kind}/{slug}')

# ---------------------------------------------------------------- home
def home():
    P = ''
    marquee_items = ['SolidWorks', 'Onshape', 'GD&amp;T · ASME Y14.5', 'Fits · ASME B4.1', 'FEA', 'Tolerance analysis', 'Load path design',
                     'Lathe', 'Mill', 'CNC · 3- and 5-axis', 'Wire EDM', 'Laser cutting', 'Additive friction stir deposition', 'Load cells', 'Python']
    mq = '<ul>' + ''.join(f'<li>{x}</li>' for x in marquee_items) + '</ul>'
    exp_cards = ''.join(card(s_, P, delay=n * 0.08) for n, s_ in enumerate(EXPER))
    proj_cards = ''.join(card(s_, P, delay=n * 0.08) for n, s_ in enumerate(PROJ))
    small_cards = ''.join(small_card(x, P, delay=n * 0.08) for n, x in enumerate(SMALL))
    lead_cards = ''.join(card(s_, P, delay=n * 0.08) for n, s_ in enumerate(LEAD))
    main = f'''
<section class="hero">
  <div class="hero-grid" aria-hidden="true"></div>
  <div class="xhair" aria-hidden="true"><div class="xl"></div><div class="yl"></div><div class="ro"></div></div>
  <div class="wrap hero-in">
    <figure class="view fade-in" style="--d:.15s">
      <span class="reg" aria-hidden="true"></span>
      <div class="portrait"><img src="images/portrait.jpg" data-dropin="images/portrait.jpg" fetchpriority="high" alt="Portrait of Brian Yue in a navy suit, standing in a stone archway at Duke."></div>
    </figure>
    <div>
      <p class="label kicker fade-in" style="--d:.05s">Mechanical engineering student · Duke University</p>
      <h1 class="display split">I design hardware and then <em>make it.</em></h1>
      <dl class="titleblock fade-in" style="--d:.7s">
        <div class="wide"><dt>What I do</dt><dd>I design aerospace hardware, draw it up properly with GD&amp;T, check it with FEA, and then help machine it.</dd></div>
        <div class="third"><dt>School</dt><dd>Duke University</dd></div>
        <div class="third"><dt>Degree</dt><dd>B.S.E. in Mechanical Engineering</dd></div>
        <div class="third"><dt>Certificate</dt><dd>Aerospace Engineering</dd></div>
        <div><dt>Graduating</dt><dd>May 2028</dd></div>
        <div><dt>Based in</dt><dd>Durham, NC</dd></div>
      </dl>
      <div class="actions fade-in" style="--d:.85s">
        <a class="pill solid" href="#work">See the work <span class="arrow">↓</span></a>
        <a class="pill" href="about.html">About me <span class="arrow">→</span></a>
        <a class="pill" href="mailto:{EMAIL}">{EMAIL} <span class="arrow">↗</span></a>
      </div>
    </div>
  </div>
</section>


<div class="marquee" aria-label="Tools and processes"><div class="marquee-track">{mq}</div></div>

<section class="section" id="work">
  <div class="wrap">
    <div class="sec-head" data-reveal>
      <div><p class="label">Selected work</p><h2>Experience &amp; projects</h2></div>
      <p>The longer write-ups, including the parts that weren't mine and what I'd do differently.</p>
    </div>
    <div class="group">
      <div class="sub-head" data-reveal><h3>Experience</h3><span class="label">Internship · research</span></div>
      <div class="cards">{exp_cards}</div>
    </div>
    <div class="group">
      <div class="sub-head" data-reveal><h3>Projects</h3><span class="label">Design team · coursework · client work</span></div>
      <div class="cards three">{proj_cards}</div>
    </div>
  </div>
</section>

<section class="section" id="leadership">
  <div class="wrap">
    <div class="sec-head" data-reveal>
      <div><p class="label">Teams &amp; teaching</p><h2>Leadership</h2></div>
      <p>Mostly teams and students. Some of it goes back to high school in Beijing.</p>
    </div>
    <div class="cards three">{lead_cards}</div>
  </div>
</section>

<section class="section" id="smaller">
  <div class="wrap">
    <div class="sec-head" data-reveal>
      <div><p class="label">Class projects &amp; side work</p><h2>Smaller work</h2></div>
      <p>Shorter class projects, and one I went way overboard on. <a class="link" href="work/smaller-work.html">All three <span class="arrow">→</span></a></p>
    </div>
    <div class="cards three">{small_cards}</div>
  </div>
</section>

<section class="section" id="about-teaser">
  <div class="wrap split-2">
    <div class="portrait" data-reveal><img src="images/aiaa-sign.webp" loading="lazy" style="object-position: 50% 40%" alt="Brian Yue at the AIAA AVIATION 2026 forum in San Diego."></div>
    <div data-reveal style="--d:.1s">
      <p class="label">About</p>
      <p class="big-text" style="font-family: var(--serif); font-weight: 400; font-size: clamp(2rem, 4vw, 3.2rem); letter-spacing: -0.02em; line-height: 1.05">Beijing, then Durham.</p>
      <p class="big-text" style="margin-top:0"> <span>I'm a mechanical engineering junior at Duke working toward an aerospace certificate. Before that, I captained ISSDC teams and coached middle school volleyball and basketball in Beijing.</span></p>
      <div class="actions">
        <a class="pill solid" href="about.html">More about me <span class="arrow">→</span></a>
        <a class="pill" href="resume.pdf" target="_blank" rel="noopener">Résumé <span class="arrow">↗</span></a>
      </div>
    </div>
  </div>
</section>

<section class="section" id="personalTeaser"{{TEASER_HIDDEN}} data-prerendered>
  <div class="wrap">
    <div class="sec-head" data-reveal>
      <div><p class="label">Personal</p><h2>Outside the shop</h2><div class="pchips">{{TEASER_CHIPS}}</div></div>
      <a class="pill" href="personal.html">See everything <span class="arrow">→</span></a>
    </div>
    <div class="strip" data-reveal>{{TEASER_STRIP}}</div>
  </div>
</section>'''
    chips, strip = render_teaser(P)
    main = (main.replace('{TEASER_HIDDEN}', '' if HAS_PERSONAL else ' hidden')
                .replace('{TEASER_CHIPS}', chips).replace('{TEASER_STRIP}', strip))
    return page('Brian Yue · Mechanical Engineering', 'Brian Yue, Duke mechanical engineering student: instrument design, GD&T drawing packages, FEA, flight hardware, and a sole-author AIAA paper.', P, 'home', main, path='')

# ---------------------------------------------------------------- about
def about():
    P = ''
    main = f'''
<section class="p-hero">
  <div class="wrap split-2">
    <div class="portrait" data-reveal><img src="images/portrait.jpg" data-dropin="images/portrait.jpg" alt="Portrait of Brian Yue in a navy suit, standing in a stone archway at Duke."></div>
    <div>
      <p class="label accent fade-in" style="--d:.05s">About</p>
      <h1 class="split">Beijing, then Durham.</h1>
      <div class="prose fade-in" style="--d:.5s">
        <p>I'm a mechanical engineering junior at Duke's Pratt School of Engineering, working toward a certificate in aerospace engineering. Before Duke I was at Tsinghua International School in Beijing, where I captained our ISSDC teams and, as a full-time student-athlete, coached middle school volleyball and basketball, ending as head coach of both girls' teams.</p>
        <p>At Duke I split my time between research, teaching, and Duke Aero's solid propulsion subteam, which I joined in August 2024. </p>
        <p>I got into space through <i>The Martian</i> when I was ten. What stuck with me wasn't the rescue, it was all the hardware that made it possible. Airplanes came from <i>Mayday: Air Crash Investigation</i>, which I'll admit is a strange way to fall in love with them, but every episode took an aircraft apart and explained how it worked. These days the part I enjoy most is watching something I drew turn into a part that works.</p>
        <p>Outside engineering, I play trombone in the Duke University Marching Band, and I play volleyball and basketball.</p>
        <p>I'm a native speaker of English and Mandarin, and a US citizen.</p>
      </div>
      <div class="actions fade-in" style="--d:.7s; margin-top:28px">
        <a class="pill solid" href="resume.pdf" target="_blank" rel="noopener">Résumé (PDF) <span class="arrow">↗</span></a>
        <a class="pill" href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn <span class="arrow">↗</span></a>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap cv">
    <div data-reveal>
      <h2>Experience</h2>
      <ul class="tl">
        <li><span class="when">2026</span><a href="work/shear-balance.html">Research Intern<span class="sub">Turbulent Shear Flow Laboratory, NC State</span></a></li>
        <li><span class="when">2025–26</span><a href="work/ttbw.html">Student Researcher<span class="sub">Duke MEMS, with Dr. Earl H. Dowell</span></a></li>
        <li><span class="when">2025–</span><a href="leadership/teaching.html">Undergraduate Teaching Assistant<span class="sub">EGR 105 and ME 221, Duke</span></a></li>
        <li><span class="when">2024–</span><a href="work/forward-closure.html">Solid Propulsion Subteam<span class="sub">Duke Aero, since August 2024</span></a></li>
        <li><span class="when">2021–24</span><a href="leadership/issdc.html">Captain, then Student Advisor<span class="sub">International Space Settlement Design Competition</span></a></li>
        <li><span class="when">2020–24</span><a href="leadership/coaching.html">Student Coach<span class="sub">Tsinghua International School athletics, Beijing</span></a></li>
      </ul>
      <h2 style="margin-top:48px">Education</h2>
      <ul class="tl">
        <li><span class="when">2028</span><span>B.S.E. Mechanical Engineering, Certificate in Aerospace Engineering<span class="sub">Duke University, Pratt School of Engineering · GPA 3.776</span></span></li>
      </ul>
      <h2 style="margin-top:48px">Honors</h2>
      <ul class="tl">
        <li><span class="when">2026</span><span>Bellman Gift Travel Grant, $1,747<span class="sub">Duke MEMS</span></span></li>
        <li><span class="when">2024</span><span>Dean's List with Distinction<span class="sub">Duke Pratt School of Engineering</span></span></li>
        <li><span class="when">2023</span><span>Global Champion<span class="sub">ISSDC, Kennedy Space Center</span></span></li>
        <li><span class="when">2022</span><span>Best Representor<span class="sub">ISSDC China Finals, 2021–22 season</span></span></li>
      </ul>
    </div>
    <div class="skills" data-reveal style="--d:.1s">
      <h2>Skills</h2>
      <dl>
        <div><dt>CAD &amp; design</dt><dd>SolidWorks, Onshape, GD&amp;T (datum reference frames, positional tolerancing, surface finish), engineering drawings, BOMs, DFM/DFA</dd></div>
        <div><dt>Analysis</dt><dd>SolidWorks Simulation (FEA), hand calculations, tolerance and load path analysis, measurement system design, trade studies, root cause analysis, ANSYS Granta EduPack</dd></div>
        <div><dt>Fabrication</dt><dd>Lathe, mill, drill press, band saw, CNC (3- and 5-axis), wire EDM, metallographic grinding and polishing, laser cutting, 3D printing, additive friction stir deposition, load cell integration</dd></div>
        <div><dt>Materials testing</dt><dd>Metallography, fractography, tensile testing, exposure to SEM</dd></div>
        <div><dt>Computing &amp; data</dt><dd>Python (NumPy, Matplotlib) for test-data processing; DAQ data collection in solid mechanics and dynamics labs</dd></div>
        <div><dt>Standards</dt><dd>ASME Y14.5, ASME B4.1</dd></div>
        <div><dt>Coursework</dt><dd>Mechanics of Solids (EGR 201), Structure &amp; Properties of Solids (ME 221), Dynamics (EGR 244: a gravity car whose run time I predicted from a dynamic model, then tested), Thermodynamics (ME 331), Mechatronics, Space Systems Design (ME 490-04); in progress: ME Analysis for Design (ME 321), Fluid Mechanics (ME 336), Aircraft Propulsion (ME 490-05)</dd></div>
        <div><dt>Memberships</dt><dd>AIAA and ASME student member since 2024</dd></div>
      </dl>
    </div>
  </div>
</section>'''
    return page('About · Brian Yue', 'About Brian Yue, a Duke mechanical engineering student: experience, education, honors, and skills in CAD, GD&T, FEA, and machining.', P, 'about', main, path='about')


# ---------------------------------------------------------------- animated card posters (smaller work)
# Dark, pointer-reactive posters driven by small physics loops in assets/site.js (data-anim). Still at rest.
STARS = '<circle cx="162" cy="60" r="0.6" opacity="0.18"/><circle cx="268" cy="146" r="0.6" opacity="0.56"/><circle cx="107" cy="34" r="1.2" opacity="0.18"/><circle cx="45" cy="170" r="1.6" opacity="0.21"/><circle cx="112" cy="251" r="0.6" opacity="0.41"/><circle cx="198" cy="391" r="0.6" opacity="0.40"/><circle cx="67" cy="168" r="1.6" opacity="0.20"/><circle cx="154" cy="326" r="0.8" opacity="0.20"/><circle cx="286" cy="75" r="0.6" opacity="0.40"/><circle cx="31" cy="24" r="0.8" opacity="0.37"/><circle cx="266" cy="311" r="1.2" opacity="0.41"/><circle cx="227" cy="120" r="0.8" opacity="0.46"/><circle cx="122" cy="230" r="1.6" opacity="0.37"/><circle cx="172" cy="180" r="1.6" opacity="0.59"/><circle cx="59" cy="167" r="1" opacity="0.22"/><circle cx="244" cy="16" r="0.6" opacity="0.49"/><circle cx="287" cy="350" r="1" opacity="0.30"/><circle cx="175" cy="199" r="1.2" opacity="0.18"/><circle cx="47" cy="108" r="0.6" opacity="0.18"/><circle cx="351" cy="259" r="1.2" opacity="0.28"/><circle cx="193" cy="267" r="0.6" opacity="0.57"/><circle cx="178" cy="244" r="1.2" opacity="0.18"/><circle cx="384" cy="52" r="0.8" opacity="0.33"/><circle cx="458" cy="199" r="0.8" opacity="0.35"/><circle cx="275" cy="353" r="1.2" opacity="0.54"/><circle cx="139" cy="166" r="1" opacity="0.46"/><circle cx="190" cy="92" r="0.6" opacity="0.23"/><circle cx="116" cy="93" r="1.2" opacity="0.52"/><circle cx="91" cy="113" r="0.8" opacity="0.34"/><circle cx="185" cy="227" r="0.8" opacity="0.46"/><circle cx="258" cy="247" r="0.6" opacity="0.36"/><circle cx="435" cy="381" r="1.6" opacity="0.33"/><circle cx="199" cy="41" r="1.2" opacity="0.18"/><circle cx="34" cy="84" r="0.8" opacity="0.20"/><circle cx="300" cy="41" r="1.6" opacity="0.22"/><circle cx="51" cy="145" r="0.6" opacity="0.18"/><circle cx="104" cy="150" r="1" opacity="0.58"/><circle cx="301" cy="190" r="0.6" opacity="0.53"/><circle cx="497" cy="186" r="1.2" opacity="0.29"/><circle cx="72" cy="300" r="1" opacity="0.37"/><circle cx="346" cy="207" r="0.8" opacity="0.58"/><circle cx="264" cy="59" r="1.6" opacity="0.56"/><circle cx="379" cy="119" r="0.6" opacity="0.46"/><circle cx="131" cy="147" r="0.8" opacity="0.31"/><circle cx="111" cy="217" r="1.6" opacity="0.30"/><circle cx="112" cy="325" r="0.8" opacity="0.51"/>'

def _anim_frame(kind, inner, labels):
    """Shared shell: cursor spotlight, the scene, and corner labels. The labels are SVG text in the same 500 x 400 frame as
    the art, so they scale with the card and stay put even when a visitor's browser enlarges small text."""
    tl, bl, br = labels
    hud = (f'<svg class="anim-svg hud" viewBox="0 0 500 400" aria-hidden="true" focusable="false">'
           f'<text x="25" y="40" class="hk">{tl}</text><text x="25" y="374" class="hk">{bl}</text>'
           f'<text x="475" y="374" class="hk end">{br}</text></svg>')
    return f'<span class="spot" aria-hidden="true"></span>{inner}{hud}'


def anim_iss():
    trail = ''.join('<line x1="0" y1="0" x2="0" y2="0"/>' for _ in range(28))
    inner = f'''<svg class="anim-svg iss" viewBox="0 0 500 400" aria-hidden="true" focusable="false">
  <defs><radialGradient id="iss-earth" cx="38%" cy="32%" r="78%"><stop offset="0" stop-color="#2c3036"/><stop offset="1" stop-color="#0c0e10"/></radialGradient>
  <radialGradient id="iss-glow"><stop offset=".55" stop-color="#f08a4b" stop-opacity="0"/><stop offset=".78" stop-color="#f08a4b" stop-opacity=".16"/><stop offset="1" stop-color="#f08a4b" stop-opacity="0"/></radialGradient>
  <radialGradient id="iss-flare"><stop offset="0" stop-color="#fff3e6"/><stop offset=".35" stop-color="#f08a4b"/><stop offset="1" stop-color="#f08a4b" stop-opacity="0"/></radialGradient></defs>
  <g class="par far">{STARS}</g>
  <g class="par near">
    <circle cx="250" cy="200" r="138" class="iss-orbit"/>
    <circle cx="250" cy="200" r="103" fill="url(#iss-glow)"/>
    <circle cx="250" cy="200" r="91" class="iss-atm"/>
    <circle cx="250" cy="200" r="80" fill="url(#iss-earth)" class="iss-earth"/>
    <g class="iss-trail">{trail}</g>
    <g class="iss-st" transform="translate(161.3 94.3)"><circle r="16" fill="url(#iss-flare)" class="iss-flare" opacity="0"/><circle r="5" class="iss-dot"/></g>
  </g>
</svg>'''
    return _anim_frame('iss', inner, ('Team SkyFall · EGR 105', 'Alt <tspan class="hv alt">420</tspan> km', 'Gravity + drag · RK4'))

def anim_snap():
    top_arm = '<polygon points="110,96 374,96 374,112 362,128 351,128 343,114 134,119"/>'
    strain_arm = top_arm.replace('<polygon', '<polygon fill="url(#strain)"')
    def arm(cls, flip):
        g = f'<g class="arm {cls}"><g class="arm-shape">{top_arm}</g><g class="arm-strain" opacity="0">{strain_arm}</g></g>'
        return f'<g transform="matrix(1 0 0 -1 0 400)">{g}</g>' if flip else g
    inner = f'''<svg class="anim-svg snap" viewBox="0 0 500 400" aria-hidden="true" focusable="false">
  <defs><linearGradient id="strain" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#ff5a36"/><stop offset=".22" stop-color="#f08a4b"/><stop offset=".6" stop-color="#f6c36b" stop-opacity=".5"/><stop offset="1" stop-color="#f6c36b" stop-opacity="0"/></linearGradient>
  <pattern id="snap-grid" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".9" fill="#ffffff" opacity=".13"/></pattern></defs>
  <g class="par far"><rect x="-40" y="-40" width="580" height="480" fill="url(#snap-grid)"/></g>
  <g class="par near">
    <g class="cube"><rect x="150" y="125" width="150" height="150" rx="3"/><path d="M150 155h150M150 185h150M150 215h150M150 245h150" class="layers"/></g>
    <rect x="110" y="96" width="24" height="208" class="wall"/>
    {arm("top", False)}{arm("bot", True)}
    <circle cx="362" cy="128" r="8" class="snapring" opacity="0"/><circle cx="362" cy="272" r="8" class="snapring" opacity="0"/>
    <text x="242" y="338" text-anchor="middle" class="eps"><tspan class="nc">ε</tspan> max 6.3 × 10<tspan class="nc">⁻³</tspan> · root corner</text>
  </g>
</svg>'''
    return _anim_frame('snap', inner, ('Snap-fit · FEA check', 'Move to push · pull', 'FOS ≈ 2.9'))

# nozzle exits in images/card-vanguard.webp (% of width, % of height) and plume angle, measured from the 3D model
VANGUARD_NOZZLES = ((65.07, 54.3, 14.5), (63.5, 61.29, 16.2), (67.39, 55.81, 14.7))

def anim_vanguard(src, alt):
    plumes = ''.join(f'<span class="plume" style="--nx:{x}%;--ny:{y}%;--na:{a}deg"></span>' for x, y, a in VANGUARD_NOZZLES)
    inner = (f'<canvas class="warp" aria-hidden="true"></canvas>'
             f'<div class="ship"><img src="{{{{P}}}}{src}" loading="lazy" alt="{esc(alt)}">{plumes}</div>')
    return _anim_frame('fly', inner, ('Duke Vanguard · 1:1.7', 'Onshape · PLA', 'Thrust <tspan class="hv thr">0</tspan>%'))

# ---------------------------------------------------------------- smaller work (its own page + a row of cards on home)
SMALL = [
  dict(id='iss-deorbit', title='Simulating the ISS deorbit', label='EGR 105 · Fall 2024 · Team project',
       card='Our team simulated the ISS falling out of orbit. I wrote the orbital decay code, RK4 integrator and all.',
       thumb=dict(anim='iss'),
       prose="A team project for EGR 105, Computing for Engineers: simulate the International Space Station deorbiting. I wrote the orbital decay script. It treats the station as a point mass under Earth's gravity and aerodynamic drag, takes air density from the 1976 U.S. Standard Atmosphere, and steps the orbit forward with a fourth-order Runge-Kutta integrator I wrote by hand in Python. The project reported the station's altitude at each critical threshold and animated the whole descent.",
       figs=lambda: video(None, 'Team SkyFall ISS deorbit demonstration video', 'Fig. 1', "Team SkyFall's demonstration video, with the animation of the full deorbit. Plays from YouTube.", yt='yojsCxUHBxU', max_w=980, poster='images/iss-deorbit-poster.webp')),
  dict(id='snap-fit-fea', title='Checking a snap-fit with FEA', label='ME 321 · Fall 2026',
       card='I ran the FEA on a printed snap-fit grip, then printed it to check that it really snaps.',
       thumb=dict(anim='snap'),
       prose="A 3D-printed snap-fit grip that holds a 38 mm cube, for an ME 321 lab. My part here was the check, not the sizing. I ran a SolidWorks static study with the tab pushed 1.5 mm, a margin over the real 1.2 mm, which put the peak strain at 6.3 × 10⁻³ and the minimum factor of safety near 2.9, both at the inner arm-to-wall corner. That corner is sharp, so part of that peak is a stress singularity, and I wouldn't trust the exact number until it's filleted and the mesh converges. Then I printed and tested it: the cube snaps in, holds, and slides back out with a firm pull.",
       figs=lambda: row(fig('images/me321-grip-fos.webp', 'SolidWorks factor-of-safety plot of the U-shaped grip, mostly red, with the minimum of about 2.9 marked at the inner corner.', 'Fig. 2', 'Factor of safety: minimum about 2.9, at the inner arm-to-wall corner.', 1400, 717, group='me321'),
                         fig('images/me321-grip-strain.webp', 'SolidWorks strain plot of the grip, highest along the arm near the corner.', 'Fig. 3', 'Strain under the 1.5 mm tab displacement: peak 6.3 × 10⁻³.', 1400, 716, group='me321'))
                    + '<div class="row" data-reveal style="max-width: 560px">' + fig('images/me321-grip-print.webp', 'A purple 3D-printed grip holding a purple printed cube between its two arms, on a shop bench.', 'Fig. 4', 'Printed and assembled: the cube held in the grip.', 682, 511, group='me321') + '</div>'),
  dict(id='vanguard', title='Space Shuttle <i>Vanguard</i>', label='EGR 101 · Fall 2024',
       card='A CAD assignment for EGR 101 that I went way overboard on, lettering and all.',
       thumb=dict(anim='vanguard', src='images/card-vanguard.webp', alt='Render of the Vanguard shuttle model with its raised lettering'),
       prose='A CAD assignment for EGR 101, my first semester at Duke, where I went well past what was asked just for fun: a 4.9-inch Space Shuttle with DUKE and VANGUARD lettering and three engine bells, modeled in Onshape to print in PLA, plus a fully dimensioned drawing.',
       figs=lambda: model3d('shuttle', 'Interactive 3D model of a small Space Shuttle with a tail fin, three engine bells, and VANGUARD lettering along its back.', 'Fig. 5', 'The <i>Vanguard</i> model in 3D. Drag to rotate.', max_w=980)
                    + row(fig('images/dwg-shuttle-2400.webp', 'Drawing of the Space Shuttle Duke Vanguard model: top, right, front and isometric views at 1:1.7 scale, dimensioned in inches, PLA plastic, drawn by Brian Yue on 09/27/2024.', 'Fig. 6', 'Its drawing: four views, dimensioned in inches. Click to zoom.', 1000, 773, group='shuttle'))),
]

def small_card(x, P, delay=0.0):
    t = x['thumb']
    kind = t['anim']
    inner = {'iss': anim_iss, 'snap': anim_snap}[kind]() if kind != 'vanguard' else anim_vanguard(t['src'], t['alt'])
    da = {'iss': 'iss', 'snap': 'snap', 'vanguard': 'fly'}[kind]
    return f'''<article class="card mini" data-reveal style="--d:{delay:.2f}s">
  <a href="{P}work/smaller-work.html#{x["id"]}" data-cursor="View">
    <div class="media anim a-dark a-{da}" data-anim="{da}">{inner}<span class="go">View <span class="arrow">→</span></span></div>
    <div class="card-info"><h3>{x["title"]}</h3> <span class="dates">{x["label"]}</span> <p>{x["card"]}</p></div>
  </a>
</article>'''

def smaller_work():
    P = '../'
    groups = ''.join(f'''
  <section class="group" id="{x["id"]}">
    <div class="sub-head" data-reveal><h3>{x["title"]}</h3><span class="label">{x["label"]}</span></div>
    <div class="prose" data-reveal><p>{x["prose"]}</p></div>
    <div class="figs">{x["figs"]()}</div>
  </section>''' for x in SMALL)
    main = f'''
<section class="p-hero">
  <div class="wrap">
    <div class="crumbs fade-in" style="--d:.05s">
      <a class="pill" href="../index.html#smaller"><span class="arrow">←</span> All work</a>
      <span class="label">{len(SMALL)} projects</span>
    </div>
    <p class="label accent fade-in" style="--d:.1s">Class projects · side work</p>
    <h1 class="split">Smaller work</h1>
    <p class="p-lede fade-in" style="--d:.55s">Class projects that didn't need a full page each, plus one I went way overboard on.</p>
  </div>
</section>

<div class="wrap sw">{groups}
</div>'''
    return page('Smaller work · Brian Yue', 'Smaller projects by Brian Yue: an ISS deorbit simulation, an FEA check on a snap-fit, and a 3D-printable Space Shuttle model.', P, 'work', main, path='work/smaller-work')

# ---------------------------------------------------------------- personal
def personal():
    P = ''
    main = '''
<section class="p-hero">
  <div class="wrap">
    <p class="label accent fade-in" style="--d:.05s">Personal</p>
    <h1 class="split">Outside the shop.</h1>
    <p class="p-lede fade-in" style="--d:.5s">Volleyball, basketball, music, and photography: what I do away from engineering.</p>
  </div>
</section>
<section class="wrap" style="padding-bottom: clamp(72px, 10vw, 128px)">
  <nav class="ptiles fade-in" style="--d:.7s" id="ptiles" aria-label="Categories">{TILES}</nav>
  <div id="psections" data-prerendered>{SECS}</div>
</section>'''
    TILES, SECS = render_personal(P)
    main = main.replace('{TILES}', TILES).replace('{SECS}', SECS)
    return page('Personal · Brian Yue', 'Volleyball, basketball, music, and photography: what Brian Yue does away from engineering.', P, 'personal', main, path='personal')

# ---------------------------------------------------------------- write
def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path) or OUT, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('wrote', rel, len(text))

def not_found():
    P = '/'   # root-absolute: this page is served at whatever broken URL was typed
    main = '''
<section class="p-hero" style="min-height: 62vh">
  <div class="wrap">
    <p class="label accent fade-in" style="--d:.05s">Error 404 · page not found</p>
    <h1 class="split">This part isn't in the assembly.</h1>
    <p class="p-lede fade-in" style="--d:.5s">The page you're looking for doesn't exist, or it moved. Try one of these instead.</p>
    <div class="actions fade-in" style="--d:.7s; margin-top: 32px">
      <a class="pill solid" href="/">Home <span class="arrow">→</span></a>
      <a class="pill" href="/#work">Work</a>
      <a class="pill" href="/#leadership">Leadership</a>
      <a class="pill" href="/about.html">About</a>
    </div>
  </div>
</section>'''
    out = page('Page not found · Brian Yue', 'This page does not exist.', P, 'none', main)
    return out.replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"', 1)

def sitemap():
    import datetime
    today = datetime.date.today().isoformat()
    paths = [''] + ['about', 'personal'] + [f'{k}/{s_}' for k, s_ in ORDER] + ['work/smaller-work']
    urls = ''.join(f'  <url><loc>{SITE}/{x}</loc></url>\n' for x in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'

write('index.html', home())
write('404.html', not_found())
write('sitemap.xml', sitemap())
write('about.html', about())
write('personal.html', personal())
write('work/smaller-work.html', smaller_work())
for i, (kind, slug) in enumerate(ORDER):
    write(f'{kind}/{slug}.html', project_page(i, kind, slug))
