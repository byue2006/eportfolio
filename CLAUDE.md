# brianyue.me: notes for Claude

Brian Yue's portfolio. Static site, live at https://brianyue.me (Cloudflare Workers static assets, deploys from `main`). GitHub Pages mirror at byue2006.github.io/eportfolio.

## How it's built
- All page text lives in `tools/build_site.py`. Edit there, then run `python3 tools/build_site.py`; never hand-edit the generated `*.html`.
- Personal gallery: photos go in `personal/<category>/`; `python3 tools/build_gallery.py` (needs Pillow, pillow-heif) writes `personal/_web/` and `personal/gallery.js` (captions/alt edited there persist). Category text: `personal/categories.js` (strict JSON).
- 3D models and video: `python3 tools/build_media.py <file> <slug>` (CAD: STEP/STL/OBJ/GLB/zip, `--up y` for SolidWorks, `--finish aluminum`; video: `--loop` for silent b-roll, `--start/--end`) writes `media/<slug>.glb|.mp4` + `.webp` poster, ≤24 MB, and `tools/media.json`. Needs `pip install cascadio trimesh`. Place on a page with `model3d('slug', alt, num, cap, hotspots=[...])` or `video('slug', ..., loop=True)` / `video(None, ..., yt='ID')`; `lead=True` makes it the page's hero.
- `.github/workflows/deploy.yml` runs both scripts on every push and commits results back to `main`.
- `.assetsignore` keeps tools, READMEs, inbox, originals and stray root uploads off the live site. New top-level files that should NOT be public must be added there.
- Never put `[skip ci]` in a commit message (Cloudflare skips the deploy too).

## Working rules
- Always `git pull --rebase origin main` before committing; Brian uploads via the GitHub web UI.
- Brian uploads to the repo root despite `inbox/`; sort uploads, strip EXIF, save web copies, remove originals.
- Accuracy over flattery: credit teammates (forward closure loads/drawings, PlaySeat team, ISSDC models by Kelly Wang); ME 221 TA = grading only; TTBW = sole author; the ~40% friction figure came from a comparable instrument.
- Brian is #24 and #15 (volleyball), #24 (basketball). Only caption a number when it is visible.
- Verify after each push: both checks (GitHub Actions, "Workers Builds: eportfolio") succeed and the live page shows the change.
- Open questions for Brian are listed in `inbox/README.md`.
- Never add: the AFSD research (its absence is deliberate); any ME 221 labs/office hours/discussion; modal analysis, vibration, shock or nonlinear dynamics in skills; TA class sizes or student stats.
- Keep as-is: the shear-balance attribution block, the forward-closure contribution and FOS ~11 self-criticism, the ISSDC "Rechecking" notes (historical proposal numbers are annotated, never altered).
