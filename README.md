# Geometric Methods (Book 1)

Computational Modeling. Volume 1 of the Geometric Series. Served at
https://erisml.org/geometric-methods/ via the erisml-lib `site` submodule.

> **Epistemic status (2026-07-14): the series' metrology discipline.** This volume defines the
> method — posited/measured separation, admission filters, frozen-null gates, pre-registration —
> that the domain volumes are held to. The method itself is normative (a discipline, not a
> finding); results it has produced are reported in the instrument repos
> ([xbse](https://github.com/ahb-sjsu/xbse),
> [moral-spectrum-analyzer](https://github.com/ahb-sjsu/moral-spectrum-analyzer),
> [lebse](https://github.com/ahb-sjsu/lebse)). Domain volumes are *posited* until they pass
> these gates; as of this date roughly two domains (legal text, moral dimensions 8/9) have.

## Structure

- `chapters/*.md` — the book content (source of truth). The site is a
  single-page app: `index.html` renders these Markdown files client-side
  (marked.js + KaTeX) and mounts the interactive visualizations in
  `assets/demos.js`.
- `index.html` — the app shell. Its chapter manifest (the `CHAPTERS` array,
  `CHAPTER_TITLES`, and the landing-page counts) is **generated** from
  `chapters/*.md`, not hand-edited.

## Build (Markdown → HTML manifest)

After adding, removing, or renaming a chapter in `chapters/`, run:

```bash
python .build/build_methods.py
```

It rescans `chapters/*.md`, re-orders them (chapters by number, then
appendices), and rewrites the marked regions of `index.html`
(`<!--BUILD:CHCOUNT-->`, `<!--BUILD:APXCOUNT-->`, `// <BUILD:MANIFEST>`).
Nav labels come from the curated `NAV_TITLES` map in the script; a new file
without an entry gets a label derived from its `# ` heading (and a note to
curate it). `python .build/build_methods.py --check` exits non-zero if
`index.html` is out of sync — suitable for CI.
