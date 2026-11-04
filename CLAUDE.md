# brianyue.me: notes for Claude

Brian Yue's portfolio. Static site, live at https://brianyue.me (Cloudflare Workers static assets, deploys from `main`). GitHub Pages mirror at byue2006.github.io/eportfolio.

## How it's built
- All page text lives in `tools/build_site.py`. Edit there, then run `python3 tools/build_site.py`; never hand-edit the generated `*.html`.
- Personal gallery: photos go in `personal/<category>/`; `python3 tools/build_gallery.py` (needs Pillow, pillow-heif) writes `personal/_web/` and `personal/gallery.js` (captions/alt edited there persist). Category text: `personal/categories.js` (strict JSON).
- 3D models and video: `python3 tools/build_media.py <file> <slug>` (CAD: STEP/STL/OBJ/GLB/zip, `--up y` for SolidWorks, `--finish aluminum`; video: `--loop` for silent b-roll, `--start/--end`) writes `media/<slug>.glb|.mp4` + `.webp` poster, ≤24 MB, and `tools/media.json`. Needs `pip install cascadio trimesh`. Place on a page with `model3d('slug', alt, num, cap, hotspots=[...])` or `video('slug', ..., loop=True)` / `video(None, ..., yt='ID')`; `lead=True` makes it the page's hero.
- `.github/workflows/deploy.yml` runs both scripts on every push and commits results back to `main`.
- `.assetsignore` keeps tools, READMEs, inbox, originals and stray root uploads off the live site. New top-level files that should NOT be public must be added there.
- Never put `[skip ci]` in a commit message (Cloudflare skips the deploy too).

## Design
- Sleek, hardware-company feel (Brian likes Anduril and Swarm Aero; inspired by, never copied): Geist display headings with tight tracking; Instrument Serif italic only for the hero accent and the "by." logo; one orange accent; 8px radius; dark theme by default with a header switch (choice saved in localStorage as `by-theme`; present mode forces light); every card (experience, projects, leadership) shows the organization's logo tile at rest and the work on hover (Brian likes this, keep it; hover images are cropped to the card shape as images/card-*.webp); renders, diagrams and the 3D viewer sit in a light studio grey (graphite in dark mode); video stages are always dark.

## Working rules
- Always `git pull --rebase origin main` before committing; Brian uploads via the GitHub web UI.
- Brian uploads to the repo root despite `inbox/`; sort uploads, strip EXIF, save web copies, remove originals.
- Accuracy over flattery: credit teammates (forward closure loads/drawings, PlaySeat team, ISSDC models by Kelly Wang); ME 221 TA = grading only; TTBW = sole author; the ~40% friction figure came from a comparable instrument.
- ME 321 snap-fit grip (About page): the sizing numbers were not Brian's. Say only that he did the FEA check, printing and testing; never say he designed it, and never mention AI or where the numbers came from. Alaskol was the winning 2023 Global Finals design. PlaySeat has front and rear casters (rear ones added after the fit test, though the poster omits them).
- Brian is #24 and #15 (volleyball), #24 (basketball). Only caption a number when it is visible.
- Verify after each push: both checks (GitHub Actions, "Workers Builds: eportfolio") succeed and the live page shows the change.
- Open questions for Brian are listed in `inbox/README.md`.
- Private documents Brian shared (high-school résumé, college applications, transcript, application forms) are for checking facts only. Never publish grades, GPA, test scores, addresses, phone numbers, birth date or application IDs.
- Never add: the AFSD research (its absence is deliberate); any ME 221 labs/office hours/discussion; modal analysis, vibration, shock or nonlinear dynamics in skills; TA class sizes or student stats.
- Shear balance: the starting male-female interface was a grad student's design, and he reported the ~40% friction loss and suggested carriages; Brian chose and integrated the carriage and rail. The April 2026 static hot fire used Brian's unified closure. ISSDC robot designs are Brian's; the 3D models are Kelly Wang's.
- Keep as-is: the shear-balance attribution block, the forward-closure contribution and FOS ~11 self-criticism, the ISSDC "Rechecking" notes (historical proposal numbers are annotated, never altered).
