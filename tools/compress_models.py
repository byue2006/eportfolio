"""Meshopt-compress the 3D models, about 4x smaller with no visible change.

    python3 tools/compress_models.py                 # every media/*.glb not yet compressed
    python3 tools/compress_models.py media/x.glb     # just these

Run it LAST for a model: after tools/build_media.py, tools/recolor_balance.py (it reads the
uncompressed file) and tools/media_poster.js (it can read either). Needs Node; it fetches
@gltf-transform/cli with npx. The viewer decodes with assets/vendor/meshopt_decoder.js, which
build_site.py points model-viewer to on every page that has a model. Updates the sizes in
tools/media.json, so the "Interactive 3D · size" label stays right after the next site build.
"""
import glob, json, os, struct, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GT = ['npx', '--yes', '@gltf-transform/cli@4.1.1']


def is_compressed(path):
    with open(path, 'rb') as f:
        f.read(12)
        n, _ = struct.unpack('<II', f.read(8))
        return b'EXT_meshopt_compression' in f.read(n)


def main(paths):
    paths = paths or sorted(glob.glob(os.path.join(ROOT, 'media', '*.glb')))
    mj = os.path.join(ROOT, 'tools', 'media.json')
    media = json.load(open(mj)) if os.path.exists(mj) else {}
    for p in paths:
        if is_compressed(p):
            print('already compressed:', os.path.relpath(p, ROOT)); continue
        before = os.path.getsize(p)
        tmp = tempfile.mktemp(suffix='.glb')
        subprocess.run(GT + ['meshopt', p, tmp, '--level', 'medium'], check=True, stdout=subprocess.DEVNULL)
        os.replace(tmp, p)
        after = os.path.getsize(p)
        key = os.path.basename(p)
        if key in media:
            media[key]['bytes'] = after
        print(f'{os.path.relpath(p, ROOT)}: {before / 1e3:.0f} KB -> {after / 1e3:.0f} KB')
    with open(mj, 'w') as f:
        json.dump(media, f, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main(sys.argv[1:])
