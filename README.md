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

- `chapters/*.md` — the book content (source of truth): 20 chapters + 3
  appendices, one file each, `# Chapter N: Title` as the first line.
- `assets/demos.js`, `assets/demos.css` — the interactive visualizations.
  `injectDemos(chapterId, element)` mounts a demo under the section listed in
  `DEMO_MAP`; the built chapter pages call it on load.
- `.build/` — the shared Geometric Series build kit (see below). The
  canonical copy lives in `erisml-lib/tools/series-build/`; do not edit the
  copy here, edit the canonical one and re-sync.

## Build (Markdown → static HTML)

The volume is rendered to one static page per chapter in the unified
Geometric Series look (shared CSS, manifest-driven series nav from
`erisml-lib/docs/books.json`, breadcrumb, prev/next, KaTeX):

```bash
python .build/build.py                 # -> output/  (index.html + one page per chapter)
python .build/series_check.py          # mechanical proofreading + KaTeX/xref/code checks
python .build/publish_site.py --keep assets --push   # rebuild + push the `site` branch
```

Old single-page URLs of the form `index.html#chapter-02-...` are forwarded
to the static pages by a small script on the contents page. After publishing,
re-pin the submodule in erisml-lib with
`python tools/series-build/bump_submodules.py --commit`.

## License

Two licenses, split by what the file is.

| What | License | File |
|---|---|---|
| Prose and figures: chapters, appendices, front and back matter, figures, ledgers, protocol and standards documents, README | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | `LICENSE-TEXT` |
| Source code: build scripts, tools, experiment harnesses, site generators | [MIT](https://opensource.org/licenses/MIT) | `LICENSE` |

Manuscripts under `paper/` or `papers/` that are submitted, accepted or
published elsewhere are outside both files. They carry the rights their
publisher agreement assigns.

CC BY asks you to attribute and to indicate whether you changed anything. Both
halves of that matter here. Every claim in this series carries a status label,
such as `[proved]`, `[posited]` or `[open]`, graded against a claim ledger, and
an adapted version presented as the original misstates the evidence behind it.
Attribution that names the author, the volume and this repository, and that
says whether the text was changed, is enough.
