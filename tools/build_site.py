#!/usr/bin/env python3
"""Generates every page of the site (index, about, personal, work/*, leadership/*).

All page text lives in this file. Edit it, then run:  python3 tools/build_site.py
This overwrites the generated .html files, so make content changes here, not in the HTML.
"""
import os, re, html

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the site folder
SCR = os.path.dirname(os.path.abspath(__file__))

EMAIL = 'brian.yue@duke.edu'
LINKEDIN = 'https://www.linkedin.com/in/brianyihanyue/'
DOI = 'https://doi.org/10.2514/6.2026-4344'

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23141414'/%3E"
           "%3Ctext x='16' y='21' text-anchor='middle' font-family='monospace' font-weight='700' font-size='13' fill='%23fff'%3EBY%3C/text%3E"
           "%3Ccircle cx='26' cy='26' r='3.5' fill='%23c2410c'/%3E%3C/svg%3E")

HEAD_SCRIPT = ("document.documentElement.classList.add('js');"
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
for _name, _lst in (('Experience', EXPER), ('Project', PROJ), ('Leadership', LEAD)):
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

def media(card, hover=True):
    """Card / next-project thumbnail. Roles show the organization at rest and the work on hover."""
    t = card['thumb']
    go = '<span class="go">View <span class="arrow">→</span></span>' if hover else ''
    if t['kind'] == 'type':
        inner = f'<div class="media type"><span class="cap">{t["cap"]}</span><span class="big">{t["big"]}</span>'
    else:
        cls = 'media' + {'cover': '', 'contain': ' contain', 'fit': ' fit'}[t['mode']] + (' tint' if t.get('tint') else '')
        mstyle = f' style="--tint: {t["tint"]}"' if t.get('tint') else ''
        style = f' style="object-position: {t["pos"]}"' if t.get('pos') else ''
        inner = f'<div class="{cls}"{mstyle}><img src="{{{{P}}}}{t["src"]}" loading="lazy"{style} alt="{esc(t["alt"])}">'
    org = card.get('org')
    if org and hover:
        lw = f' style="--logo-w: {org["logo_w"]}"' if org.get('logo_w') else ''
        logo = f'<img class="logo" data-logo src="{{{{P}}}}{org["logo"]}"{lw} alt="{esc(org["name"])}">' if org.get('logo') else ''
        word_cls = 'word sm' if org.get('small') else 'word'
        inner += (f'<div class="org reveal" style="--org-bg: {org["bg"]}; --org-fg: {org.get("fg", "#fff")}">'
                  f'{logo}<span class="{word_cls}">{org["word"]}</span><span class="sub">{org["sub"]}</span></div>')
    return inner + go + '</div>'

def tags(lst): return '<ul class="tags">' + ''.join(f'<li>{esc(x)}</li>' for x in lst) + '</ul>'

# ---------------------------------------------------------------- shell
def page(title, desc, P, active, main, progress=False):
    def cur(k): return ' aria-current="page"' if active == k else ''
    home = '' if active == 'home' else P + 'index.html'
    nav = (f'<a href="{home}#work"{cur("work")}>Work</a>'
           f'<a href="{home}#leadership"{cur("leadership")}>Leadership</a>'
           f'<a href="{P}about.html"{cur("about")}>About</a>'
           f'<a href="{P}personal.html" data-nav="personal"{cur("personal")}>Personal</a>')
    menu_links = (f'<a href="{P}index.html"{cur("home")}>Home <span>00</span></a>'
                  f'<a href="{home}#work"{cur("work")}>Work <span>01</span></a>'
                  f'<a href="{home}#leadership"{cur("leadership")}>Leadership <span>02</span></a>'
                  f'<a href="{P}about.html"{cur("about")}>About <span>03</span></a>'
                  f'<a href="{P}personal.html" data-nav="personal"{cur("personal")}>Personal <span>04</span></a>'
                  f'<a href="{P}resume.pdf" target="_blank" rel="noopener">Résumé <span>PDF</span></a>')
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f5f5f2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f1011" media="(prefers-color-scheme: dark)">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{FAVICON}">
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
    <a class="brand" href="{P}index.html"><span class="mark" aria-hidden="true">BY</span>Brian Yue</a>
    <nav class="navpill" aria-label="Primary">{nav}</nav>
    <div class="bar-right">
      <a class="pill solid" href="{P}resume.pdf" target="_blank" rel="noopener">Résumé <span class="arrow">↗</span></a>
      <button class="pill menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span>Menu</span></button>
    </div>
  </div>
</header>
<div class="menu" id="menu" inert>
  <nav aria-label="Menu">{menu_links}</nav>
  <p class="label">{EMAIL}</p>
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
<script src="{P}personal/gallery.js"></script>
<script src="{P}assets/site.js"></script>
</body>
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
  card_title='Floating-element shear-force balance',
  lede='Rerouted the load path before a 40% friction error got built in.',
  tags=['Onshape', 'GD&T', 'FEA', 'Instrumentation'],
  thumb=dict(kind='img', src='images/balance-rear.webp', mode='contain', alt='CAD render of the shear-force balance'),
  meta=[('Role', 'Designer, end to end'), ('When', 'June – August 2026'), ('Where', 'Turbulent Shear Flow Lab, NC State'), ('Advisor', 'Dr. Venkat Narayanaswamy')],
  lead=lead('images/balance-rear.webp', 'CAD render of the sidewall-insert plate: a blue aluminum frame with a light-blue floating plate, a small rail and carriage at the center, and the load-cell mount at the right.',
            'Fig. 1', 'Rear face of the sidewall-insert assembly. Carriage, rail, and load-cell mount visible; mounting plate hidden.', 1120, 541, mode='pad', group='balance'),
  glance=[('Constraint', '5 DOF fixed, 1 free'), ('Sensing', 'Uniaxial load cell, single load path'), ('Fits', 'RC4 / LC2, ASME B4.1'),
          ('Position', '⌀.010 true position, ASME Y14.5'), ('Material', '6061 aluminum, 16 Ra flow surfaces'), ('Error avoided', '~40% friction loss'),
          ('Carriage + rail', '~$159, catalog parts'), ('Deliverables', '5-sheet drawing set, BOM')],
  sections=[
    ('challenge', 'The challenge', '''<div class="prose"><p>Skin friction is a wall shear stress, and measuring it directly means letting a small element of the wall float free in one direction while holding it still in the other five. Every parallel path that load can take is measurement error. The instrument also had to fit inside a cavity that already existed in the lab's subsonic tunnel wall, so the envelope, the mounting, and the flow-facing surface were fixed before I drew anything.</p></div>'''),
    ('contribution', 'My contribution', '''<p class="contrib">Design, analysis, the drawing package, and the bill of materials were mine. The tunnel hardware and the cavity were not: I designed into them.</p>'''),
    ('process', 'Process &amp; iteration', '''<div class="prose"><p>My first interface was male-female. Before anything was cut, test data from a comparable instrument showed friction in that kind of interface eroding roughly 40% of the measured shear force. Rather than argue my geometry was different, I scrapped the interface and rerouted the load path onto a ball-bearing carriage and rail, redesigning the mobile plate so the carriage alone supports it. The carriage and rail came to about $159 in catalog parts.</p>
<p>I also made the plate height adjustable. Setting it lower leaves a recess where a viscoelastic layer of varying thickness can be cured in place.</p></div>
<div class="figs">''' + row(fig('images/balance-section-flow.webp', 'Section view along the flow axis showing the floating plate suspended inside the frame.', 'Fig. 2', 'Section along the flow axis. The mobile plate (light blue) floats and passes shear to the load cell only.', 1500, 178, group='balance')) +
      row(fig('images/balance-section-transverse.webp', 'Section view across the flow axis showing the carriage on its rail beneath the plate.', 'Fig. 3', 'Section along the transverse axis. The carriage and rail fix five degrees of freedom and leave the flow axis free.', 1068, 380, group='balance')) + '</div>'),
    ('outcome', 'Outcome &amp; evidence', '''<div class="prose"><p>A five-sheet manufacturing drawing package and a bill of materials with vendor part numbers and unit costs. I modeled the assembly in Onshape and checked it under test loads with SolidWorks FEA. Mating surfaces carry ASME B4.1 fit classes, the M4 pattern that holds the non-contact gap around the mobile plate carries a ⌀.010 true-position tolerance, and the flow-facing surfaces get a 16 Ra finish, because roughness there would change the quantity being measured. Choosing those numbers meant weighing what a university machine shop can hold against what the instrument needs.</p>
<p>Only two of the five parts start from raw stock. The other three are catalog or existing lab parts with features added, which keeps custom fabrication to a minimum.</p></div>
<div class="figs" data-reveal>
  <div class="sheets-head"><span class="label">Drawing package</span><span class="label">5 sheets · August 2026 · click for PDF</span></div>
  <div class="sheets">
    <a href="{{P}}drawings/1-panel-frame.pdf" target="_blank" rel="noopener"><div class="frame"><img src="{{P}}images/dwg-1-panel-frame.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 1: panel frame"></div><span class="s-t">1 · Panel frame</span><span class="s-d">6061 Al, from stock</span></a>
    <a href="{{P}}drawings/2-panel.pdf" target="_blank" rel="noopener"><div class="frame"><img src="{{P}}images/dwg-2-panel.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 2: panel"></div><span class="s-t">2 · Panel</span><span class="s-d">6061 Al, from stock</span></a>
    <a href="{{P}}drawings/3-l-bracket.pdf" target="_blank" rel="noopener"><div class="frame"><img src="{{P}}images/dwg-3-l-bracket.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 3: L-bracket"></div><span class="s-t">3 · L-bracket</span><span class="s-d">Modified catalog part</span></a>
    <a href="{{P}}drawings/4-sidewall-mounting-plate.pdf" target="_blank" rel="noopener"><div class="frame"><img src="{{P}}images/dwg-4-sidewall-mounting-plate.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 4: sidewall mounting plate"></div><span class="s-t">4 · Mounting plate</span><span class="s-d">Modified lab hardware</span></a>
    <a href="{{P}}drawings/5-carriage-rail.pdf" target="_blank" rel="noopener"><div class="frame"><img src="{{P}}images/dwg-5-carriage-rail.webp" width="1000" height="773" loading="lazy" alt="Drawing sheet 5: carriage rail"></div><span class="s-t">5 · Carriage rail</span><span class="s-d">Modified catalog part</span></a>
  </div>
</div>'''),
    ('reflection', 'Reflection', '''<div class="prose"><p>The most useful input to this design was someone else's test data. It arrived before anything was cut, so changing the interface cost a redesign instead of a rebuild. The lesson I'd carry forward: look for data on comparable hardware before committing to a load path.</p></div>'''),
    ('skills', 'Skills', tags(['Onshape', 'SolidWorks Simulation', 'GD&T (ASME Y14.5)', 'Fits (ASME B4.1)', 'Tolerance analysis', 'Load path design', 'DFM', 'BOM'])),
  ])

P_['forward-closure'] = dict(
  kind='work', num='02', cat='Flight hardware', year='2025–',
  title='Unified forward closure', card_title='Unified forward closure',
  lede='Three solid rocket motor closures merged into one flight part.',
  tags=['SolidWorks FEA', 'Lathe', 'Mill', 'Seals'],
  thumb=dict(kind='img', src='images/closure-machined.webp', mode='cover', pos='50% 60%', alt='Partially machined forward closure'),
  meta=[('Role', 'Drove the redesign'), ('When', 'August 2025 – present'), ('Team', 'Duke Aero, Solid Propulsion'), ('Status', 'Flown')],
  lead=lead('images/closure-machined.webp', 'A partially machined aluminum forward closure on a shop bench, with two eye bolts threaded into its face and radial ports around its side.',
            'Fig. 1', 'Forward closure, partially machined.', 1600, 1200, mode='cover', group='closure', pos='50% 58%'),
  glance=[('Consolidation', '3 closures → 1'), ('Part count', '−67%'), ('Machining setups', '−2'), ('Ports', 'Hydrostatic + hot fire merged, sealed for flight'),
          ('Min. factor of safety', '≈11, preliminary design'), ('Processes', 'Lathe, drill press, mill')],
  sections=[
    ('challenge', 'The challenge', '''<div class="prose"><p>We were machining three separate forward closures for one solid rocket motor: one for the hydrostatic proof test, one for static hot fire, and one for flight. Three parts, three setups, three chances to get something wrong, and two of them thrown away after a single use.</p></div>'''),
    ('contribution', 'My contribution', '''<p class="contrib">I drove the redesign and did the modeling, the analysis, and the fastener and sealing evaluation. Machining was shared with teammates. The thermal and mechanical loads came from our team lead by way of OpenRocket, and teammates produced the final drawings.</p>'''),
    ('process', 'Process &amp; iteration', '''<div class="prose"><p>Consolidating all three into one part cut part count by 67% and eliminated two machining setups. The hard part was the ports. A flight closure wants to be solid; a test closure needs instrumentation and fill ports. I merged the hydrostatic and hot fire ports into a single port that is sealed for flight, so one part can serve all three roles without compromising the one that matters.</p>
<p>I modeled it in Onshape, ran SolidWorks Simulation on a preliminary design to check factor of safety under flight loads, and evaluated commercial fasteners and seals from several suppliers against the chamber's specified thermal and mechanical loads.</p></div>
<div class="figs">''' + row(fig('images/closure-section.webp', 'Half-section CAD view of the closure showing the bore, seal grooves, and threaded holes.', 'Fig. 2', 'Section view of the final design.', 685, 619, group='closure'),
                       fig('images/closure-port.webp', 'Section through the closure showing an L-shaped internal passage from the face to the side port.', 'Fig. 3', 'Section through the merged hydrostatic / hot fire port.', 696, 450, group='closure')) + '</div>'),
    ('outcome', 'Outcome &amp; evidence', '''<div class="prose"><p>My teammates and I machined the final parts on a lathe, drill press, and mill. The motor flew.</p></div>'''),
    ('reflection', 'Reflection', '''<div class="prose"><p>The minimum factor of safety came out around 11, which is not a good number. It means the geometry was set by available stock, machinability, and handling rather than by load, and on a weight-critical vehicle that is mass we'd want back. I'd also verify the chamber pressure independently instead of taking it downstream of someone else's model, since every number after it depends on it.</p>
<p class="next-note">Next: researching head-end ignition ahead of a two-stage vehicle next year.</p></div>
<div class="figs">''' + row(fig('images/closure-fos.webp', 'SolidWorks factor-of-safety plot of the closure, mostly red, with a minimum factor of safety of 11.', 'Fig. 4', 'FEA on a preliminary design. Minimum FOS = 11.', 1400, 794, group='closure')) + '</div>'),
    ('skills', 'Skills', tags(['Onshape', 'SolidWorks Simulation (FEA)', 'Fastener & seal selection', 'Pressure vessel design', 'Lathe', 'Mill', 'Drill press', 'DFM'])),
  ])

P_['ttbw'] = dict(
  kind='work', num='03', cat='Research · publication', year='2025–26',
  title='An Overview of Transonic Truss-Braced Wing Technology', card_title='Transonic truss-braced wing review',
  lede='First-author AIAA paper synthesizing 53 sources on what stands between the configuration and service.',
  tags=['AIAA 2026-4344', 'Aerostructures', 'Certification'],
  thumb=dict(kind='img', src='images/ttbw-diagram.webp', mode='fit', alt='Truss-braced wing schematic and bending moment plot'),
  meta=[('Role', 'Sole author, presenter'), ('When', 'April 2025 – June 2026'), ('Advisor', 'Dr. Earl H. Dowell'), ('Venue', 'AIAA AVIATION Forum 2026')],
  lead='<figure class="p-lead" data-reveal>' + DIAGRAM + '<figcaption><b>Fig. 1</b>Why the strut matters. Schematic drawn for this page, not to scale; the moment curves come from a simple beam model, not from the paper.</figcaption></figure>',
  glance=[('Paper', f'<a href="{DOI}" target="_blank" rel="noopener">AIAA 2026-4344</a>'), ('Venue', 'AIAA AVIATION Forum, San Diego, June 8–12, 2026'),
          ('Sources', '53, from NASA, Boeing, academia, and international groups'), ('Funding', 'Bellman Gift Travel Grant, $1,747')],
  sections=[
    ('challenge', 'The challenge', '''<div class="prose"><p>A transonic truss-braced wing uses an external strut to carry part of the bending load, which lets the wing be much thinner and longer than a cantilever wing of the same weight. The aerodynamic case is strong. What I wanted to know was what still stands between the configuration and service. A thorough summary of NASA-led work already existed; no review had pulled in the research from outside it.</p></div>'''),
    ('contribution', 'My contribution', '''<p class="contrib">Sole author. I reviewed and synthesized the literature, wrote the paper, and presented it at the 2026 AIAA AVIATION Forum in San Diego, with travel funded by a departmental grant. Dr. Dowell advised.</p>'''),
    ('process', 'Process &amp; iteration', '''<div class="prose"><p>I worked through 53 sources from NASA, Boeing, and academic and international groups and organized them by discipline: aerodynamics, low-speed aerodynamics, structures and fatigue, aeroelasticity, sizing and MDO, aeroacoustics, icing, simulation, and systems integration. For each, I tracked what has been demonstrated and what is still open.</p></div>
<div class="figs">''' + row(fig('images/ttbw-paper.webp', 'Title and abstract of the paper An Overview of Transonic Truss-Braced Wing Technology by Brian Y. Yue.', 'Fig. 2', 'First page of AIAA 2026-4344.', 1100, 1025, group='ttbw')) + '</div>'),
    ('outcome', 'Outcome &amp; evidence', '''<div class="prose"><p><strong>Certification.</strong> The configuration is novel enough that the usual means of compliance don't transfer. Comparative analysis can't be relied on for icing because there is no operational history to compare against, and current icing simulation tools aren't validated for TTBW certification. On noise, the baseline configuration clears FAA Stage 4 by about 23 EPNdB cumulative, but its sideline margin under Stage 5 is only 2.9 EPNdB, thin enough to be flagged as a certification risk even if modeling bias may explain part of it.</p>
<p><strong>Systems integration.</strong> The thin, high-aspect-ratio wing that makes the configuration efficient leaves little room for fuel, so proposals move tanks into the fuselage and struts, at some cost in L/D. Engine placement, the wing-fuselage junction, and control-surface layout get pulled along with it. Each is a decision in one subsystem forcing a change in another.</p></div>
<div class="figs">''' + row(fig('images/ttbw-noise-margins.webp', 'Chart of cumulative noise margin against certification year, with FAA Stage 3, 4, and 5 limits and TTBW predictions near minus 20 EPNdB.', 'Fig. 3', 'Cumulative noise margins vs. FAA limits. Figure by June et al. (2022), not my work; reproduced with citation in my review as Fig. 15.', 753, 324, group='ttbw'),
                       fig('images/ttbw-control-layouts.webp', 'Five candidate wing planforms with different arrangements of Krueger flaps, spoilers, flaps, ailerons, and flaperons; planform 4 is marked final.', 'Fig. 4', 'Control-surface layouts studied for the TTBW. Figure by Harrison et al. (2020), not my work; reproduced with citation as Fig. 16.', 851, 509, group='ttbw')) + '</div>'),
    ('reflection', 'Reflection', '''<div class="prose"><p>Certification is the thread I keep coming back to. For something genuinely new, a real part of the engineering is working out how you would prove it at all.</p></div>'''),
    ('skills', 'Skills', tags(['Literature synthesis', 'Technical writing', 'Aerodynamics', 'Aeroelasticity', 'MDO', 'Aeroacoustics', 'Conference presentation'])),
  ])

P_['happy-meal'] = dict(
  kind='work', num='03', cat='Product design · injection molding', year='2025',
  title='Celebration of Imagination: a Happy Meal train', card_title='Modular Happy Meal train',
  lede='An injection-moldable toy train with swappable snap-fit heads, at $0.31 a unit.',
  tags=['SolidWorks', 'Tolerancing', 'DFM'],
  thumb=dict(kind='img', src='images/toy-heads.webp', mode='cover', pos='50% 65%', alt='Three 3D-printed train heads on a workbench'),
  meta=[('Role', 'Design team member'), ('When', 'Spring 2025'), ('Team', '3 people'), ('Shown at', 'Duke 2025 Toy Fair')],
  lead=lead('images/toy-heads.webp', 'Three 3D-printed train heads, orange, green, and purple, lined up on a workbench.',
            'Fig. 1', 'The three swappable train heads: standard, subway, and bullet.', 1600, 1200, mode='cover', group='toy', pos='50% 62%'),
  glance=[('Brief', 'Injection-moldable, mass-producible Happy Meal toy'), ('Production material', 'PETG (prototypes in PLA)'), ('Unit cost', '$0.31 in PETG'),
          ('Critical fit', 'Shaft collar bore ⌀10.11 ±0.01 mm on a ⌀10.16 mm axle'), ('Mate tolerance', '5.00 ±0.05 mm, head to chassis'), ('Safety', 'Passes the 1.25-inch choke-tube test')],
  sections=[
    ('challenge', 'The challenge', '''<div class="prose"><p>Design a McDonald's Happy Meal toy that is attractive and cheap, can be injection molded, and can be mass-produced. The memo to the client weighed practicality, sustainability, safety, cost, ease of use, and looks, and the toy had to be safe for children aged 4 to 8, which means nothing small enough to choke on, even after a child takes it apart.</p></div>'''),
    ('contribution', 'My contribution', '''<p class="contrib">Three-person team with Saina Srivastava and Mariangle Mendez. We brainstormed, scored concepts, modeled in SolidWorks, and 3D-printed prototypes together, and co-wrote the technical memo. For the Duke 2025 Toy Fair, I made the toy's video.</p>'''),
    ('process', 'Process &amp; iteration', '''<div class="prose"><p>Brainstorming started wide; an early favorite was a carrier jet with Toy Story soldiers. We narrowed the field with a weighted Pugh matrix that favored price above everything else, and the plain train won.</p></div>
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
                       fig('images/toy-exploded.webp', 'SolidWorks exploded view of the train: top, head, mate, chassis, axle, wheel, and shaft collar.', 'Fig. 4', 'Exploded assembly in SolidWorks.', 889, 604, group='toy')) + '''</div>'''),
    ('outcome', 'Outcome &amp; evidence', '''<div class="prose"><p>Every detachable piece passed the choke-tube test in every orientation. Three heads (standard, subway, and bullet) share one mate, so they work as collectibles. In production PETG, the toy comes to $0.31 a unit, with one 100-ton press per head design running 100,000 units a week. We presented it at the Duke 2025 Toy Fair.</p>
<p>The tightest tolerance sits where safety does: the shaft collar bore is ⌀10.11 ±0.01 mm on a ⌀10.16 mm axle, a press fit that keeps the wheels on. The head-to-chassis mate is looser, at ±0.05 mm, because a head that comes off is the point of the toy, not a hazard.</p></div>
<div class="figs">''' + row(fig('images/toy-choke.webp', 'The train head and chassis resting on top of a choke test tube, too large to fall in.', 'Fig. 5', 'Passing the choke-tube test.', 1000, 1333, group='toy'),
                       fig('images/toy-final.webp', 'Orange 3D-printed train head mounted on a green chassis.', 'Fig. 6', 'Final head on its chassis, before wheels.', 1000, 1333, group='toy'),
                       fig('images/toy-section.webp', 'Cross-section of the train head CAD model showing it is solid.', 'Fig. 7', 'Section through the head: solid, for drop strength.', 1200, 934, group='toy')) +
      row(fig('images/toy-drawing-head.webp', 'Dimensioned drawing of a train head with 5.00 ±0.05 mm mate callouts.', 'Fig. 8', 'Toleranced drawing of one train head.', 1600, 689, group='toy')) + '''</div>'''),
    ('reflection', 'Reflection', '''<div class="prose"><p>The biggest takeaway was to start early. We finished most of the CAD before spring break, which left time to print, find the tolerance problem, and work around it without lowering the standard of the toy. The snap-fit was the other lesson: one connection idea solved several problems at once and stayed injection-moldable.</p></div>'''),
    ('skills', 'Skills', tags(['SolidWorks', 'Pugh matrix', 'Tolerance analysis', 'Design for injection molding', '3D printing', 'Cost analysis', 'Technical memo'])),
  ])

P_['playseat'] = dict(
  kind='work', num='04', cat='Assistive device', year='2024',
  title='Accessible PlaySeat', card_title='Accessible PlaySeat',
  lede='Adaptive seating for a young client, where one fit test moved the wheels.',
  tags=['User testing', 'Fabrication', 'Requirements'],
  thumb=dict(kind='img', src='images/playseat-front.webp', mode='cover', alt='The finished PlaySeat'),
  meta=[('Role', 'Seating structure, fabrication'), ('When', 'September – December 2024'), ('Team', '4 people'), ('Advisor', 'Dr. George Delagrammatikas')],
  lead=lead('images/playseat-front.webp', 'The finished PlaySeat: a padded child\'s seat with a harness on a white base, large wheels, and a black footrest platform in front.',
            'Fig. 1', 'The finished chair.', 1600, 900, mode='cover', group='playseat'),
  glance=[('Timeline', '11 weeks, concept to delivery'), ('Verification', 'Predesign evaluation; prototype fit test with client and caregivers'),
          ('Change from testing', 'Drive wheels moved forward, rear wheels added'), ('Processes', 'Laser cutting, acrylic bending, manual machining')],
  sections=[
    ('challenge', 'The challenge', '''<div class="prose"><p>A young client needed seating that fit his postural and reach limitations. Our job over eleven weeks was to turn what he and his caregivers needed into something quantified enough to design against: spinal support geometry, ergonomic reach limits, and the requirement that it not look clinical.</p></div>'''),
    ('contribution', 'My contribution', '''<p class="contrib">I worked on the seating structure design and the fabrication, and shared the requirements work and the fit test with my three teammates.</p>'''),
    ('process', 'Process &amp; iteration', '''<div class="prose"><p>A prototype fit test showed he couldn't reach the push rims. That was a requirement we had written down and gotten wrong. Moving the drive wheels forward fixed the reach and shifted the center of gravity, so we added rear wheels to offset it. One test invalidated an assumption, the fix created a second problem, and we fixed that too, all inside an eleven-week build.</p></div>
<div class="figs">''' + row(fig('images/playseat-prototype.jpg', 'Side view of the PlaySeat prototype in the shop, with a teammate holding the headrest support.', 'Fig. 2', 'Earlier prototype, in the shop.', ar=0.75, mode='cover', group='playseat', dropin=True),
                       fig('images/playseat-wheel.webp', 'Close-up side view of the final chair\'s large spoked wheel, footrest, and small caster.', 'Fig. 3', 'Drive wheel and footrest, final chair.', 1400, 965, group='playseat'),
                       fig('images/playseat-back.webp', 'Rear view of the final chair showing black straps, a bolted headrest support, and a handle.', 'Fig. 4', 'Rear view, final chair.', 975, 1125, group='playseat')) + '</div>'),
    ('outcome', 'Outcome &amp; evidence', '''<div class="prose"><p>The finished chair was delivered to the client at the end of the build.</p></div>
<div class="figs">''' + row(fig('images/playseat-tray.webp', 'Final chair with its white meal tray attached.', 'Fig. 5', 'With the tray attached.', 1400, 1025, group='playseat'),
                       fig('images/playseat-car63.jpg', 'The finished chair parked beside a blue Duke race car, number 63.', 'Fig. 6', 'The finished chair beside car 63.', ar=1.333, mode='cover', group='playseat', dropin=True)) + '</div>'),
    ('reflection', 'Reflection', '''<div class="prose"><p>It's the smallest project here and the one that taught me the most about verification. A requirement you haven't tested against the real user is a guess written in a confident font.</p></div>'''),
    ('skills', 'Skills', tags(['Requirements definition', 'User testing', 'Ergonomics', 'Laser cutting', 'Acrylic bending', 'Manual machining', 'Teamwork'])),
  ])

P_['issdc'] = dict(
  kind='leadership', num='01', cat='Team systems design · 2021–24', year='2021–24',
  title='Space settlement design', card_title='ISSDC: captain and advisor',
  lede='Operations and atmosphere design for ISSDC proposals; named a Global Champion at Kennedy Space Center in 2023.',
  tags=['Captain', 'Global Champion', 'Life support'],
  thumb=dict(kind='img', src='images/issdc-alaskol-cover.webp', mode='cover', pos='0% 50%', alt='Alaskol title slide'),
  meta=[('Role', 'Captain, then student advisor'), ('When', 'September 2021 – August 2024'), ('Result', 'Global Champion, 2023'), ('My sections', 'Operations; atmosphere')],
  lead=lead('images/issdc-alaskol-atmosphere.webp', 'Proposal slide titled Atmosphere: a table of nitrogen, oxygen, carbon dioxide, and humidity for residential, industrial, and agricultural sectors, and a table of residential seasons.',
            'Fig. 1', 'Alaskol atmosphere design: gas mix by sector and the residential season calendar. My section.', 1600, 900, group='issdc'),
  glance=[('Result', 'Global Champion, 2023, Kennedy Space Center'), ('Also', 'Asia Regional Finals twice; Best Representor, China Finals 2021–22'),
          ('Format', 'Assigned team, RFP, 24–48 hours'), ('Judges', 'Former NASA engineers')],
  sections=[
    ('challenge', 'The challenge', '''<div class="prose"><p>The International Space Settlement Design Competition runs like an industry proposal shop. A team is assigned, not chosen, an RFP lands, and a complete settlement design and presentation are due in 24 to 48 hours, then defended in front of judges who are former NASA engineers.</p></div>'''),
    ('contribution', 'My contribution', '''<p class="contrib">Two sections were mine. On <strong>Bellevistat</strong>, Team Bread's proposal for the 30th ISSDC (2022–23), I designed nearly all of the operations and infrastructure section. On <strong>Alaskol</strong>, DAFC's lunar settlement (2023), I designed the atmosphere. I also built the team's design database and documented team strategy, which later teams worked from.</p>'''),
    ('process', 'Process &amp; iteration', '''<div class="prose"><p>Bellevistat is an orbital settlement for 7,850 people. I sized its utilities from per-person and per-area assumptions: an Earth-normal air mix at 0.75 atm across 4.29 × 10⁸ m³ of pressurized volume, which works out to roughly 11,400 cargo containers of gas; a power budget of 1.12 × 10⁸ kWh per day, met by 3.37 × 10⁶ m² of solar panels with a reactor as backup; 170 million gallons of water stored in the central shaft; and a day/night cycle copied from Houston in mid-spring. I also wrote the hull material and construction equipment lists, the maintenance and repair plan, and the plan for expanding infrastructure.</p></div>
<div class="figs">''' + row(fig('images/issdc-bread-operations.webp', 'Section divider page reading 3.0 Operations and Infrastructure, Team Bread, with a rendering of a space station.', 'Fig. 2', 'Bellevistat: the operations section.', 1000, 1295, group='issdc'),
                       fig('images/issdc-bread-atmosphere.webp', 'Proposal page on community infrastructure with an air composition table and food production text.', 'Fig. 3', 'Atmosphere and food sizing.', 1100, 1424, group='issdc'),
                       fig('images/issdc-bread-power.webp', 'Proposal page with initial food quantity and power distribution tables.', 'Fig. 4', 'Food stores and power budget.', 1100, 1424, group='issdc')) + '''</div>
<div class="prose" style="margin-top:32px"><p>Alaskol sits on the Moon next to mining operations. I gave each sector its own atmosphere: residential air at 28% oxygen, industrial and agricultural air close to Earth-normal, carbon dioxide raised to 0.15% in the agricultural unit, and humidity set per sector at 50, 40, and 70%. Residential areas also run a three-season climate calendar. Like every choice in a proposal, the composition had to be defended against the alternatives.</p></div>'''),
    ('outcome', 'Outcome &amp; evidence', '''<div class="prose"><p>I led a team to the Asia Regional Finals twice, was invited onto the Chinese national team for the 2022–23 Global Championship, and was named a Global Champion at Kennedy Space Center. After aging out as a competitor, I came back as a student advisor.</p></div>
<div class="figs">''' + row(fig('images/issdc-alaskol-cover.webp', 'Title slide: ALASKOL, with a domed lunar habitat and the DAFC logo.', 'Fig. 5', 'Alaskol title slide. Art by teammates.', 1600, 900, mode='cover', group='issdc')) + '</div>'),
    ('reflection', 'Reflection', '''<div class="prose"><p>You hand off work and trust it comes back, and you decide fast which parts of the problem are worth the time you have left. That carries straight over to engineering.</p></div>'''),
    ('skills', 'Skills', tags(['Life-support sizing', 'Trade studies', 'Technical writing', 'Team leadership', 'Presenting to judges', 'Working under deadline'])),
  ])

P_['teaching'] = dict(
  kind='leadership', num='02', cat='Teaching', year='2025–',
  title='Undergraduate Teaching Assistant', card_title='Teaching assistant, EGR 105 & ME 221',
  lede='Two engineering courses, two sections of 39 students each, and a rule: teach the process, not the answer.',
  tags=['EGR 105', 'ME 221', 'Mentoring'],
  thumb=dict(kind='type', big='2 × 39', cap='Students per section · EGR 105 & ME 221'),
  meta=[('Role', 'Undergraduate TA'), ('When', 'August 2025 – present'), ('Courses', 'EGR 105, ME 221'), ('Where', 'Duke University')],
  lead='''<div class="p-lead stats" data-reveal>
  <div><div class="big">2</div><div class="cap">Courses: Computing for Engineers (EGR 105) and Structure &amp; Properties of Solids (ME 221)</div></div>
  <div><div class="big">2 × 39</div><div class="cap">Students per section</div></div>
  <div><div class="big">Weekly</div><div class="cap">Office hours, plus lab sections and one-on-one sessions</div></div>
</div>''',
  glance=[('EGR 105', 'Computing for Engineers, two years'), ('ME 221', 'Structure & Properties of Solids, one year'), ('Format', 'Office hours, lab sections, one-on-one sessions')],
  sections=[
    ('challenge', 'The role', '''<div class="prose"><p>I'm a teaching assistant for two courses: EGR 105, Computing for Engineers, for two years, and ME 221, Structure and Properties of Solids, for one, with two sections of 39 students each. Students come in with very different backgrounds, and the work spans coding projects, lab work, mini-activities, and problem sets.</p></div>'''),
    ('contribution', 'My contribution', '''<p class="contrib">I hold weekly office hours, lead lab sections, and run individual instructional sessions. I also advise on student projects, quizzes, and lab work.</p>'''),
    ('process', 'Approach', '''<div class="prose"><p>I break hard concepts down into their fundamentals and teach the process instead of supplying answers. When I review submitted work, I give feedback, suggest more efficient approaches where they exist, and recommend specific changes for resubmission.</p></div>
<div class="figs">''' + row(fig('images/teaching.jpg', 'Teaching a lab section.', 'Fig. 1', 'Teaching.', ar=1.5, mode='cover', group='teaching', dropin=True, optional=True)) + '</div>'),
    ('skills', 'Skills', tags(['Technical communication', 'Python', 'Materials science', 'Mentoring', 'Feedback'])),
  ],
  todo='Add a Reflection section: what has teaching changed about how you work?')

P_['coaching'] = dict(
  kind='leadership', num='03', cat='Coaching · 2020–24', year='2020–24',
  title='Student coach', card_title='Student coach, volleyball & basketball',
  lede='Assistant coach, then head coach of two middle school teams, while a full-time student-athlete.',
  tags=['Head coach', 'Volleyball', 'Basketball'],
  thumb=dict(kind='type', big='2nd', cap='ISAC U14 Division III, 2020–21'),
  meta=[('Role', 'Assistant, then head coach'), ('When', 'September 2020 – May 2024'), ('Where', 'Tsinghua International School, Beijing'), ('Teams', 'Volleyball, basketball')],
  lead='''<div class="p-lead stats" data-reveal>
  <div><div class="big">3</div><div class="cap">Teams coached: boys' volleyball, girls' volleyball, girls' basketball</div></div>
  <div><div class="big">2nd</div><div class="cap">ISAC U14 Division III, 2020–21</div></div>
  <div><div class="big">3rd</div><div class="cap">ISAC U14 Division IV, 2022–23</div></div>
</div>''',
  glance=[('Started as', 'Assistant coach, three middle school teams'), ('Senior year', 'Head coach, girls\' volleyball and girls\' basketball'), ('Alongside', 'Full-time student-athlete')],
  sections=[
    ('challenge', 'The role', '''<div class="prose"><p>I started as an assistant coach for the middle school boys' volleyball, girls' volleyball, and girls' basketball teams at Tsinghua International School, and in my senior year became head coach of girls' volleyball and girls' basketball, all while playing as a full-time student-athlete.</p></div>'''),
    ('contribution', 'My contribution', '''<p class="contrib">I ran practices, set lineups, gave individual feedback and advice, tracked and analyzed statistics, and managed rosters across multiple teams.</p>'''),
    ('outcome', 'Outcome', '''<div class="prose"><p>Teams I coached placed second in ISAC U14 Division III in 2020–21 and third in Division IV in 2022–23.</p></div>
<div class="figs">''' + row(fig('images/coaching.jpg', 'Coaching a middle school team.', 'Fig. 1', 'Coaching.', ar=1.5, mode='cover', group='coaching', dropin=True, optional=True)) + '</div>'),
    ('skills', 'Skills', tags(['Leadership', 'Planning', 'Statistics', 'Feedback', 'Time management'])),
  ],
  todo='Add a Reflection section: what did coaching teach you that engineering uses?')

CARD = {
  'shear-balance': dict(card_title='Research Intern @ NC State', status=['Internship', 'Finished'], dates='Jun 2026 → Aug 2026',
      lede='Designed a floating-element shear-force balance; rerouted the load path before a 40% friction error got built in.',
      org=dict(word='NC STATE', sub='Turbulent Shear Flow Laboratory', name='NC State University', bg='#cc0000', logo='images/logo-ncstate.png', logo_w='82%'),
      thumb_tint='#e9edf3'),
  'ttbw': dict(card_title='Student Researcher @ Duke', status=['Research', 'Published'], dates='Apr 2025 → Jun 2026',
      lede='First-author AIAA paper synthesizing 53 sources on transonic truss-braced wings.',
      org=dict(word='DUKE', sub='Mechanical Engineering &amp; Materials Science', name='Duke University', bg='#00539b', logo='images/logo-duke.svg')),
  'forward-closure': dict(card_title='Unified forward closure', status=['Project', 'Flown'], dates='Duke Aero · Aug 2025 → present',
      lede='Three solid rocket motor closures merged into one flight part: 67% fewer parts, two fewer setups.'),
  'happy-meal': dict(card_title='Modular Happy Meal train', status=['Project', 'Toy Fair 2025'], dates='Duke · Spring 2025',
      lede='An injection-moldable toy train with swappable snap-fit heads, at $0.31 a unit.'),
  'playseat': dict(card_title='Accessible PlaySeat', status=['Project', 'Delivered'], dates='Duke · Sep 2024 → Dec 2024',
      lede='Adaptive seating for a young client, where one fit test moved the wheels.', thumb_tint='#e7efe9'),
  'issdc': dict(card_title='Captain &amp; Advisor @ ISSDC', status=['Leadership', 'Global Champion'], dates='Sep 2021 → Aug 2024',
      lede='Operations and atmosphere design for settlement proposals; Global Champion at Kennedy Space Center.',
      org=dict(word='ISSDC', sub='International Space Settlement Design Competition', name='ISSDC', bg='#0b0d12')),
  'teaching': dict(card_title='Teaching Assistant @ Duke', status=['Leadership', 'Ongoing'], dates='Aug 2025 → present',
      lede='EGR 105 and ME 221: office hours, lab sections, and one-on-one sessions.',
      org=dict(word='EGR 105<br>ME 221', sub='EGR 105 · ME 221 · Teaching Assistant', name='Duke University', bg='#012169', small=True, logo='images/logo-duke.svg')),
  'coaching': dict(card_title='Student Coach @ Tsinghua Intl. School', status=['Leadership', 'Finished'], dates='Sep 2020 → May 2024',
      lede='Assistant, then head coach of girls\' volleyball and basketball while a student-athlete.',
      org=dict(word='TIS', sub='Tsinghua International School Athletics', name='Tsinghua International School', bg='#2a2622')),
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
    status = ''.join(f'<span class="{"k" if n == 0 else ""}">{x}</span>' for n, x in enumerate(d['status']))
    return f'''<article class="card" data-reveal style="--d:{delay:.2f}s">
  <a href="{href}" data-cursor="View">
    {media(d)}
    <div class="card-info"><h3>{d["card_title"]}</h3><div class="status">{status}</div><span class="dates">{d["dates"]}</span><p>{d["lede"]}</p></div>
  </a>
</article>'''

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
    <p class="label accent fade-in" style="--d:.1s">{d["cat"]}</p>
    <h1 class="split">{d["title"]}</h1>
    <p class="p-lede fade-in" style="--d:.55s">{d["lede"]}</p>
    <dl class="meta-grid fade-in" style="--d:.7s">{meta}</dl>
  </div>
</section>

<div class="wrap">
  {d["lead"]}
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
    title = f'{d["card_title"]} · Brian Yue'
    return page(title, d['lede'], P, kind, main, progress=True)

# ---------------------------------------------------------------- home
def home():
    P = ''
    marquee_items = ['SolidWorks', 'Onshape', 'GD&amp;T · ASME Y14.5', 'Fits · ASME B4.1', 'FEA', 'Tolerance analysis', 'Load path design',
                     'Lathe', 'Mill', '5-axis CNC', 'Wire EDM', 'Laser cutting', 'Additive friction stir deposition', 'Load cells', 'Python']
    mq = '<ul>' + ''.join(f'<li>{x}</li>' for x in marquee_items) + '</ul>'
    exp_cards = ''.join(card(s_, P, delay=n * 0.08) for n, s_ in enumerate(EXPER))
    proj_cards = ''.join(card(s_, P, delay=n * 0.08) for n, s_ in enumerate(PROJ))
    lead_cards = ''.join(card(s_, P, delay=n * 0.08) for n, s_ in enumerate(LEAD))
    main = f'''
<section class="hero">
  <div class="hero-grid" aria-hidden="true"></div>
  <div class="xhair" aria-hidden="true"><div class="xl"></div><div class="yl"></div><div class="ro"></div></div>
  <div class="wrap hero-in">
    <figure class="view fade-in" style="--d:.15s">
      <span class="reg" aria-hidden="true"></span>
      <div class="portrait"><img src="images/portrait.jpg" data-dropin="images/portrait.jpg" fetchpriority="high" alt="Portrait of Brian Yue in a navy suit, standing in a stone archway at Duke."></div>
      <figcaption><span class="label">View A · Portrait</span><span class="label">Scale 1:1</span></figcaption>
    </figure>
    <div>
      <p class="label kicker fade-in" style="--d:.05s">Mechanical Engineering · Duke University · Class of 2028</p>
      <h1 class="display split">I design hardware and then <em>make it.</em></h1>
      <dl class="titleblock fade-in" style="--d:.7s">
        <div class="wide"><dt>Scope</dt><dd>Mechanical design of aircraft hardware: detail design, engineering drawings and GD&amp;T, tolerance analysis, structural validation, and hands-on fabrication and assembly.</dd></div>
        <div><dt>Drawn by</dt><dd>Brian Yue</dd></div>
        <div><dt>School</dt><dd>Duke, B.S.E. ME 2028</dd></div>
        <div><dt>Location</dt><dd>Durham, NC</dd></div>
        <div><dt>Rev</dt><dd>November 2026</dd></div>
      </dl>
      <div class="actions fade-in" style="--d:.85s">
        <a class="pill solid" href="#work">See the work <span class="arrow">↓</span></a>
        <a class="pill" href="about.html">About me <span class="arrow">→</span></a>
        <button class="pill" type="button" data-copy="{EMAIL}">{EMAIL} <span class="hint">Copy</span></button>
      </div>
    </div>
  </div>
</section>

<div class="marquee" aria-label="Tools and processes"><div class="marquee-track">{mq}{mq.replace("<ul>", '<ul aria-hidden="true">', 1)}</div></div>

<section class="section" id="work">
  <div class="wrap">
    <div class="sec-head" data-reveal>
      <div><p class="label">Selected work</p><h2>Experience &amp; projects</h2></div>
      <p>Each page walks through the problem, my part, what changed along the way, and what I learned.</p>
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
      <p>Captaining design teams, teaching engineering courses, and coaching.</p>
    </div>
    <div class="cards three">{lead_cards}</div>
  </div>
</section>

<section class="section" id="about-teaser">
  <div class="wrap split-2">
    <div class="portrait" data-reveal><img src="images/portrait.jpg" data-dropin="images/portrait.jpg" loading="lazy" alt="Portrait of Brian Yue in a navy suit, standing in a stone archway at Duke."></div>
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

<section class="section" id="personalTeaser" hidden>
  <div class="wrap">
    <div class="sec-head" data-reveal>
      <div><p class="label">Personal</p><h2>Outside the shop</h2></div>
      <a class="pill" href="personal.html">See everything <span class="arrow">→</span></a>
    </div>
    <div class="strip" data-reveal></div>
  </div>
</section>'''
    return page('Brian Yue · Mechanical Engineering', 'Brian Yue, mechanical engineering student at Duke. Instrument design, flight hardware, aerospace research, assistive devices, and leadership.', P, 'home', main)

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
        <p>At Duke I split my time between Duke Aero's solid propulsion subteam, research, and teaching. I like projects where the envelope is fixed and everything inside it is mine to decide.</p>
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
        <li><span class="when">2025–</span><a href="work/forward-closure.html">Solid Propulsion Subteam<span class="sub">Duke Aero</span></a></li>
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
        <div><dt>Fabrication</dt><dd>Lathe, mill, drill press, band saw, 5-axis CNC, wire EDM, laser cutting, 3D printing, additive friction stir deposition, load cell integration</dd></div>
        <div><dt>Materials testing</dt><dd>Metallography, fractography, tensile testing, exposure to SEM</dd></div>
        <div><dt>Computing</dt><dd>Python (NumPy, Matplotlib)</dd></div>
        <div><dt>Standards</dt><dd>ASME Y14.5, ASME B4.1</dd></div>
        <div><dt>Coursework</dt><dd>Mechanics of Solids, Structure &amp; Properties of Solids, Dynamics, Mechatronics, Thermodynamics, Space Systems Design; now Fluid Mechanics, Aircraft Propulsion</dd></div>
        <div><dt>Memberships</dt><dd>AIAA and ASME student member since 2024</dd></div>
      </dl>
    </div>
  </div>
</section>'''
    return page('About · Brian Yue', 'About Brian Yue: background, experience, education, honors, and skills.', P, 'about', main)

# ---------------------------------------------------------------- personal
def personal():
    P = ''
    main = '''
<section class="p-hero">
  <div class="wrap">
    <p class="label accent fade-in" style="--d:.05s">Personal</p>
    <h1 class="split">Outside the shop.</h1>
    <p class="p-lede fade-in" style="--d:.5s">Photography, sports, and drawings: what I make and do away from engineering.</p>
  </div>
</section>
<section class="wrap" style="padding-bottom: clamp(72px, 10vw, 128px)">
  <div class="filters" id="filters" role="group" aria-label="Filter by category"></div>
  <div class="masonry" id="masonry"></div>
  <p class="empty" id="emptyGallery" hidden>Nothing here yet.</p>
</section>'''
    return page('Personal · Brian Yue', 'Drawings, photographs, and other things Brian Yue makes for fun.', P, 'personal', main)

# ---------------------------------------------------------------- write
def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('wrote', rel, len(text))

write('index.html', home())
write('about.html', about())
write('personal.html', personal())
for i, (kind, slug) in enumerate(ORDER):
    write(f'{kind}/{slug}.html', project_page(i, kind, slug))
