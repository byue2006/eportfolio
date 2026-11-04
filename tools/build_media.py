#!/usr/bin/env python3
"""
Turn CAD files and videos into web-ready media for brianyue.me.

    python3 tools/build_media.py INPUT SLUG [options]

CAD  (.step .stp .stl .obj .3mf .glb .gltf, or a .zip holding one of them)
  -> media/SLUG.glb     the model the 3D viewer loads
  -> media/SLUG.webp    a studio render, shown until the model loads (and without JavaScript)
     --up z|y           which axis points up in the source (Onshape: z, SolidWorks: y). Default z.
     --finish NAME      repaint every part: aluminum, steel, dark, white. Default: keep CAD colors.
     --tol N            mesh tolerance in model units (smaller = smoother, bigger file). Default 0.05.
     --orbit "θ φ r"    starting camera, e.g. "-35deg 65deg auto".

Video (.mov .mp4 .m4v .webm .mkv .avi)
  -> media/SLUG.mp4     H.264, ≤1920 px long edge, ≤30 fps, fast start, location data stripped,
                        iPhone HDR tone-mapped to normal range
  -> media/SLUG.webp    poster frame
     --loop             silent background loop (drops audio, smaller)
     --start S --end E  trim, in seconds
     --poster-at S      which moment to use as the poster

Every output is kept under 24 MB (Cloudflare serves files up to 25 MB). Details of each file go
in tools/media.json, which tools/build_site.py reads to label the players (size, length, shape).
Needs: ffmpeg; Pillow; cascadio + trimesh for CAD; node + Playwright for the model poster.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.join(ROOT, 'media')
MANIFEST = os.path.join(ROOT, 'tools', 'media.json')
LIMIT = 24 * 1024 * 1024
CAD = ('.step', '.stp', '.stl', '.obj', '.3mf', '.glb', '.gltf')
VIDEO = ('.mov', '.mp4', '.m4v', '.webm', '.mkv', '.avi')
FINISHES = {  # base color (linear-ish sRGB 0-1), metallic, roughness
    'aluminum': ([0.80, 0.81, 0.83, 1], 0.85, 0.38),
    'steel':    ([0.62, 0.63, 0.65, 1], 0.90, 0.30),
    'dark':     ([0.10, 0.10, 0.11, 1], 0.40, 0.45),
    'white':    ([0.90, 0.90, 0.89, 1], 0.00, 0.55),
}


def die(msg):
    print('error:', msg, file=sys.stderr); sys.exit(1)


def load_manifest():
    try:
        with open(MANIFEST) as f: return json.load(f)
    except FileNotFoundError: return {}


def save_manifest(m):
    with open(MANIFEST, 'w') as f: json.dump(dict(sorted(m.items())), f, indent=2); f.write('\n')


def unzip_first(path, tmp):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(CAD + VIDEO) and not n.startswith('__MACOSX')]
        if not names: die('the zip has no CAD or video file in it')
        names.sort(key=lambda n: -z.getinfo(n).file_size)
        out = os.path.join(tmp, os.path.basename(names[0]))
        with z.open(names[0]) as src, open(out, 'wb') as dst: shutil.copyfileobj(src, dst)
        print('using', names[0], 'from the zip')
        return out


# ------------------------------------------------------------------ CAD
def to_glb(src, out, tol, up, finish):
    import trimesh, numpy as np
    ext = os.path.splitext(src)[1].lower()
    raw = out + '.raw.glb'
    if ext in ('.step', '.stp'):
        import cascadio
        cascadio.step_to_glb(src, raw, tol_linear=tol, tol_angular=0.3)
    else:
        trimesh.load(src, force='scene', process=False).export(raw)
    scene = trimesh.load(raw, force='scene', process=False)
    os.remove(raw)
    if up == 'z':  # glTF is y-up; most CAD (Onshape, STEP) is z-up
        scene.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    for g in scene.geometry.values():
        if ext in ('.stl', '.obj', '.3mf') and finish is None:
            finish = 'aluminum'  # no colors in the file: give it a machined finish
        if finish:
            c, m, r = FINISHES[finish]
            g.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
                baseColorFactor=c, metallicFactor=m, roughnessFactor=r, doubleSided=False))
    scene.export(out, include_normals=True)
    return os.path.getsize(out), len(scene.geometry)


def render_poster(glb_rel, out, orbit):
    js = os.path.join(ROOT, 'tools', 'media_poster.js')
    subprocess.run(['node', js, ROOT, glb_rel, out, orbit], check=True)


def do_model(src, slug, a):
    out = os.path.join(MEDIA, slug + '.glb')
    tol = a.tol
    for _ in range(5):
        size, parts = to_glb(src, out, tol, a.up, a.finish)
        print(f'{slug}.glb: {size / 1048576:.1f} MB, {parts} parts (tolerance {tol:g})')
        if size <= LIMIT: break
        tol *= 2.5
    else:
        die('still over 24 MB at a coarse tolerance; export a lighter model (fewer parts or no fasteners)')
    poster = os.path.join(MEDIA, slug + '.webp')
    orbit = a.orbit or '-35deg 65deg auto'
    render_poster(f'media/{slug}.glb', poster, orbit)
    return {f'{slug}.glb': dict(kind='model', bytes=size, parts=parts, poster=f'media/{slug}.webp', orbit=orbit)}


# ------------------------------------------------------------------ video
def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def do_video(src, slug, a):
    info = probe(src)
    v = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    if not v: die('no video stream found')
    has_audio = any(s['codec_type'] == 'audio' for s in info['streams']) and not a.loop
    hdr = v.get('color_transfer') in ('arib-std-b67', 'smpte2084')
    num, den = (v.get('avg_frame_rate') or '30/1').split('/')
    fps = float(num) / float(den or 1) if float(den or 1) else 30
    out = os.path.join(MEDIA, slug + '.mp4')
    edge = a.width
    crfs = [26, 29, 32] if a.loop else [23, 26, 29, 32]
    while True:
        for crf in crfs:
            vf = []
            if hdr:
                vf.append('zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,'
                          'tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p')
            vf.append(f"scale='if(gte(iw,ih),min({edge},iw),-2)':'if(gte(iw,ih),-2,min({edge},ih))':flags=lanczos")
            if fps > 30.5: vf.append('fps=30')
            vf.append('format=yuv420p')
            cmd = ['ffmpeg', '-v', 'error', '-y']
            if a.start: cmd += ['-ss', str(a.start)]
            cmd += ['-i', src]
            if a.end: cmd += ['-t', str(a.end - (a.start or 0))]
            cmd += ['-vf', ','.join(vf), '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf),
                    '-profile:v', 'high', '-movflags', '+faststart', '-map_metadata', '-1', '-map_chapters', '-1',
                    '-map', '0:v:0']
            cmd += ['-map', '0:a:0?', '-c:a', 'aac', '-b:a', '128k', '-ac', '2'] if has_audio else ['-an']
            subprocess.run(cmd + [out], check=True)
            size = os.path.getsize(out)
            print(f'{slug}.mp4: {size / 1048576:.1f} MB at {edge}px, CRF {crf}{" (HDR tone-mapped)" if hdr else ""}')
            if size <= LIMIT: break
        else:
            if edge <= 960: die('still over 24 MB; trim it with --start/--end, or post it on YouTube (unlisted)')
            edge = 1280 if edge > 1280 else 960
            continue
        break
    o = probe(out)
    ov = next(s for s in o['streams'] if s['codec_type'] == 'video')
    dur = float(o['format']['duration'])
    at = a.poster_at if a.poster_at is not None else min(1.0, dur / 3)
    png = out + '.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(at), '-i', out, '-frames:v', '1', png], check=True)
    from PIL import Image
    im = Image.open(png).convert('RGB')
    im.thumbnail((1600, 1600))
    im.save(os.path.join(MEDIA, slug + '.webp'), 'WEBP', quality=82, method=6)
    os.remove(png)
    return {f'{slug}.mp4': dict(kind='video', bytes=size, w=int(ov['width']), h=int(ov['height']), dur=round(dur, 2),
                                audio=has_audio, loop=bool(a.loop), poster=f'media/{slug}.webp')}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input'); ap.add_argument('slug')
    ap.add_argument('--up', choices=['z', 'y'], default='z')
    ap.add_argument('--finish', choices=sorted(FINISHES))
    ap.add_argument('--tol', type=float, default=0.05)
    ap.add_argument('--orbit')
    ap.add_argument('--loop', action='store_true')
    ap.add_argument('--start', type=float); ap.add_argument('--end', type=float)
    ap.add_argument('--poster-at', type=float, dest='poster_at')
    ap.add_argument('--width', type=int, default=1920)
    a = ap.parse_args()
    if not a.slug.replace('-', '').isalnum() or a.slug != a.slug.lower(): die('slug must be lowercase letters, digits and dashes')
    os.makedirs(MEDIA, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        src = unzip_first(a.input, tmp) if a.input.lower().endswith('.zip') else a.input
        ext = os.path.splitext(src)[1].lower()
        if ext in CAD: entry = do_model(src, a.slug, a)
        elif ext in VIDEO: entry = do_video(src, a.slug, a)
        else: die(f'unsupported file type {ext}')
    m = load_manifest(); m.update(entry); save_manifest(m)
    print('recorded in tools/media.json')


if __name__ == '__main__':
    main()
