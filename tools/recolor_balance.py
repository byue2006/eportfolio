"""Give the shear-balance GLB readable materials by part role, then write it back in place.
usage: python3 tools/recolor_balance.py media/shear-balance.glb  (run after tools/build_media.py "Master Assembly.step" shear-balance)"""
import sys, trimesh
from trimesh.visual.material import PBRMaterial

path = sys.argv[1]
s = trimesh.load(path, force='scene', process=False)

M = {  # base color 0-1, metallic, roughness
    'insert':    ([0.075, 0.08, 0.09, 1], 0.15, 0.55),  # lab's tunnel insert (context): dark, so the parts read
    'aluminum':  ([0.80, 0.81, 0.83, 1], 0.85, 0.38),   # frame, 6061
    'float':     ([0.36, 0.62, 0.86, 1], 0.55, 0.40),   # floating plate + carriage block (light blue, as in the figures)
    'steel':     ([0.66, 0.67, 0.69, 1], 0.90, 0.30),   # rail, carriage, bracket
    'fastener':  ([0.13, 0.13, 0.14, 1], 0.60, 0.42),   # black-oxide screws
    'loadcell':  ([0.20, 0.21, 0.23, 1], 0.50, 0.45),
}

def role(name):
    if name.startswith('id309'): return 'insert'
    if name.startswith('Frame'): return 'aluminum'
    if name.startswith(('Panel', 'Part 1')): return 'float'
    if name.startswith(('6709K', '2313N')): return 'steel'
    if name.startswith('Srf1'): return None  # load cell: keep vendor colors where present
    if name[:1].isdigit(): return 'fastener'
    return None

for name, g in s.geometry.items():
    r = role(name)
    if r is None:
        has = getattr(getattr(g.visual, 'material', None), 'baseColorFactor', None) is not None
        if name.startswith('Srf1') and has: continue
        r = 'loadcell'
    c, m, ro = M[r]
    g.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(baseColorFactor=c, metallicFactor=m, roughnessFactor=ro))
s.export(path, include_normals=True)
print('wrote', path)
