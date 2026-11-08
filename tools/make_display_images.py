"""Make lighter on-page copies of large images, without changing how anything looks.

    python3 tools/make_display_images.py      (then python3 tools/build_site.py)

Pages show most images far smaller than their files: a 2400 px poster drawn 353 px wide. For each page
and image in tools/display_widths.json (the pixels it needs there: on-screen size x 2 on desktop, x 3 on
phones, measured by tools/measure_images.js), this writes images/d/<name>-<width>.webp at that width
(+8%) when it is meaningfully smaller than the original, and records in tools/display_map.json which copy
each page uses. So a project image shown full width on its own page and as a small card on the home page
gets a small copy for the home page only. build_site.py swaps each page's <img> (and masked logos) to its
copy; the lightbox link still opens the full original, which is never changed.

An image with no measurement, or no worthwhile saving, simply keeps using its original. Re-run
measure_images.js after a layout change or new images, then this script, then build_site.py.
"""
import glob, json, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'images', 'd')
MARGIN, STEP, MIN_SAVING, MIN_RATIO = 1.08, 64, 10_000, 0.8


def original_of(rel, reverse):
    """A page may already point at an earlier copy; map it back to its original via the previous display_map.json."""
    if not rel.startswith('images/d/'):
        return rel
    return reverse.get(rel)


def needed_width(size, m):
    W, H = size
    px = m.get('px', 0)
    bw, bh = m.get('box', [0, 0])
    if bw and bh:   # a masked logo, fitted (contain) inside its box
        px = max(px, W * min(bw / W, bh / H))
    w = -(-int(px * MARGIN) // STEP) * STEP   # round up so near-equal needs share one copy
    return min(W, w)


def encode(img, width, out):
    W, H = img.size
    alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
    im = img.convert('RGBA' if alpha else 'RGB')
    if width < W:
        im = im.resize((width, round(H * width / W)), Image.LANCZOS)
    if alpha:   # logos (also used as masks): transparency stays exact, colours compress like photos
        im.save(out, 'WEBP', quality=90, alpha_quality=100, method=6)
    else:
        im.save(out, 'WEBP', quality=85, method=6)


def main():
    need = json.load(open(os.path.join(ROOT, 'tools', 'display_widths.json')))
    old_map = os.path.join(ROOT, 'tools', 'display_map.json')
    reverse = {c: o for v in (json.load(open(old_map)).values() if os.path.exists(old_map) else []) for o, c in v.items()}
    os.makedirs(OUT, exist_ok=True)
    widths = {}   # original -> {page: width}
    for page, imgs in need.items():
        for rel, m in imgs.items():
            orig = original_of(rel, reverse)
            if not orig or not orig.startswith('images/') or orig.endswith('.svg') or not os.path.exists(os.path.join(ROOT, orig)):
                continue
            with Image.open(os.path.join(ROOT, orig)) as im:
                widths.setdefault(orig, {})[page] = needed_width(im.size, m)

    page_map, made, saved = {}, set(), 0
    for orig, per_page in sorted(widths.items()):
        src = os.path.join(ROOT, orig)
        img = Image.open(src)
        stem, size = os.path.splitext(os.path.basename(orig))[0], os.path.getsize(src)
        for w in sorted(set(per_page.values())):
            out = os.path.join(OUT, f'{stem}-{w}.webp')
            if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
                encode(img, w, out)
            b = os.path.getsize(out)
            if size - b >= MIN_SAVING and b <= size * MIN_RATIO:
                made.add(out)
                for page, pw in per_page.items():
                    if pw == w:
                        page_map.setdefault(page, {})[orig] = os.path.relpath(out, ROOT)
                print(f'{orig} @ {w}px for {", ".join(sorted(p for p, pw in per_page.items() if pw == w))}: {size / 1e3:.0f} -> {b / 1e3:.0f} KB')
                saved += size - b
    for f in glob.glob(os.path.join(OUT, '*')):   # drop copies no page uses any more
        if f not in made:
            os.remove(f)
    with open(os.path.join(ROOT, 'tools', 'display_map.json'), 'w') as f:
        json.dump({p: dict(sorted(v.items())) for p, v in sorted(page_map.items())}, f, indent=1)
        f.write('\n')
    print(f'{len(made)} copies; per-page savings add up to {saved / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
