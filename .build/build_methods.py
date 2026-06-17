#!/usr/bin/env python3
"""
Build step for Geometric Methods (Book 1 of the Geometric Series).

The book is a single-page app: index.html renders the Markdown in
chapters/*.md client-side (marked.js + KaTeX) and mounts interactive demos
from assets/demos.js. The chapter list, per-chapter nav titles, and the
landing-page counts were previously hand-maintained inside index.html and
drifted from the files on disk.

This script makes chapters/*.md the source of truth for *which* chapters
exist and *in what order*, and regenerates three marked regions of
index.html:

    <!--BUILD:CHCOUNT-->N<!--/BUILD:CHCOUNT-->     chapter count (landing stat)
    <!--BUILD:APXCOUNT-->N<!--/BUILD:APXCOUNT-->   appendix count (landing stat)
    // <BUILD:MANIFEST> ... // </BUILD:MANIFEST>   the CHAPTERS array + CHAPTER_TITLES map

Ordering: chapters (chapter-NN-*) by number, then appendices (appendix-L-*)
by letter. Nav titles come from NAV_TITLES (curated short labels); any file
without an entry gets a label derived from its H1, and the build warns so the
label can be curated. The build also fails loudly if a NAV_TITLES key has no
matching file, so the map never silently drifts.

Usage:
    python .build/build_methods.py            # rewrite index.html in place
    python .build/build_methods.py --check     # exit 1 if index.html is stale (CI)
"""

import argparse
import re
import sys
from pathlib import Path

# Curated short nav labels (kept compact for the sidebar). Source of truth for
# *membership* is the filesystem; this map only supplies display strings.
NAV_TITLES = {
    "chapter-01-why-geometry": "Ch 1: Why Geometry?",
    "chapter-02-mahalanobis-distance": "Ch 2: Mahalanobis Distance",
    "chapter-03-hyperbolic-geometry": "Ch 3: Hyperbolic Geometry",
    "chapter-04-spd-manifolds": "Ch 4: SPD Manifolds",
    "chapter-05-topological-data-analysis": "Ch 5: Topological Data Analysis",
    "chapter-06-pathfinding-on-manifolds": "Ch 6: Pathfinding on Manifolds",
    "chapter-07-equilibrium-on-manifolds": "Ch 7: Equilibrium on Manifolds",
    "chapter-08-pareto-optimization": "Ch 8: Pareto Optimization",
    "chapter-09-adversarial-robustness": "Ch 9: Adversarial Robustness",
    "chapter-10-adversarial-probing": "Ch 10: Adversarial Probing",
    "chapter-11-subset-enumeration": "Ch 11: Subset Enumeration",
    "chapter-12-compositional-testing": "Ch 12: Compositional Testing",
    "chapter-13-group-theoretic-augmentation": "Ch 13: Group-Theoretic Augmentation",
    "chapter-14-gradient-reversal": "Ch 14: Gradient Reversal",
    "chapter-15-cholesky-parameterization": "Ch 15: Cholesky Parameterization",
    "chapter-16-geometric-pipelines": "Ch 16: Geometric Pipelines",
    "chapter-17-scaling": "Ch 17: Scaling",
    "chapter-18-production-deployment": "Ch 18: Production Deployment",
    "chapter-19-case-study-defect-prediction": "Ch 19: Case Study: Defect Prediction",
    "chapter-20-case-study-bioacoustics": "Ch 20: Case Study: Bioacoustics",
    "appendix-a-notation": "Appendix A: Notation",
    "appendix-b-software": "Appendix B: Software",
    "appendix-c-proofs": "Appendix C: Proofs",
}

REPO = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = REPO / "chapters"
INDEX = REPO / "index.html"

CH_RE = re.compile(r"^chapter-(\d+)-")
APX_RE = re.compile(r"^appendix-([a-z])-")


def sort_key(stem: str):
    m = CH_RE.match(stem)
    if m:
        return (0, int(m.group(1)), stem)
    m = APX_RE.match(stem)
    if m:
        return (1, m.group(1), stem)
    return (2, 0, stem)  # anything else, last, stable by name


def first_h1(md_path: Path) -> str:
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md_path.stem


def derive_nav_title(stem: str, h1: str) -> str:
    """Fallback nav label for a file with no NAV_TITLES entry."""
    t = h1.replace(" --- ", ": ").replace("---", ":")
    t = re.sub(r"^Chapter\s+(\d+):\s*", lambda m: f"Ch {m.group(1)}: ", t)
    return t


def discover():
    files = sorted(
        (p for p in CHAPTERS_DIR.glob("*.md") if p.is_file()),
        key=lambda p: sort_key(p.stem),
    )
    stems = [p.stem for p in files]

    # Guard: NAV_TITLES must not reference chapters that don't exist.
    orphan_keys = [k for k in NAV_TITLES if k not in stems]
    if orphan_keys:
        print(f"ERROR: NAV_TITLES has keys with no chapters/*.md file: {orphan_keys}")
        sys.exit(2)

    titles = {}
    for stem, path in zip(stems, files):
        if stem in NAV_TITLES:
            titles[stem] = NAV_TITLES[stem]
        else:
            titles[stem] = derive_nav_title(stem, first_h1(path))
            print(f"  note: no NAV_TITLES entry for '{stem}', derived "
                  f"\"{titles[stem]}\" — add a curated label if desired.")

    n_ch = sum(1 for s in stems if CH_RE.match(s))
    n_apx = sum(1 for s in stems if APX_RE.match(s))
    return stems, titles, n_ch, n_apx


def render_manifest(stems, titles) -> str:
    arr = "\n".join(
        (f"  '{s}'" if i == len(stems) - 1 else f"  '{s}',")
        for i, s in enumerate(stems)
    )
    tmap = "\n".join(
        (f"  '{s}': '{titles[s]}'" if i == len(stems) - 1
         else f"  '{s}': '{titles[s]}',")
        for i, s in enumerate(stems)
    )
    return (
        "// <BUILD:MANIFEST> generated by .build/build_methods.py from "
        "chapters/*.md — run the build after adding/renaming a chapter; do "
        "not hand-edit between these markers.\n"
        f"const CHAPTERS = [\n{arr}\n];\n\n"
        f"const CHAPTER_TITLES = {{\n{tmap}\n}};\n"
        "// </BUILD:MANIFEST>"
    )


def apply(html: str, stems, titles, n_ch, n_apx) -> str:
    html = re.sub(
        r"<!--BUILD:CHCOUNT-->.*?<!--/BUILD:CHCOUNT-->",
        f"<!--BUILD:CHCOUNT-->{n_ch}<!--/BUILD:CHCOUNT-->",
        html, flags=re.DOTALL,
    )
    html = re.sub(
        r"<!--BUILD:APXCOUNT-->.*?<!--/BUILD:APXCOUNT-->",
        f"<!--BUILD:APXCOUNT-->{n_apx}<!--/BUILD:APXCOUNT-->",
        html, flags=re.DOTALL,
    )
    html = re.sub(
        r"// <BUILD:MANIFEST>.*?// </BUILD:MANIFEST>",
        lambda _: render_manifest(stems, titles),
        html, flags=re.DOTALL,
    )
    return html


def main():
    ap = argparse.ArgumentParser(description="Sync index.html manifest from chapters/*.md")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if index.html is stale (do not write)")
    args = ap.parse_args()

    if not INDEX.exists():
        print(f"ERROR: {INDEX} not found")
        sys.exit(1)

    stems, titles, n_ch, n_apx = discover()
    original = INDEX.read_text(encoding="utf-8")

    for marker in ("<!--BUILD:CHCOUNT-->", "// <BUILD:MANIFEST>", "<!--BUILD:APXCOUNT-->"):
        if marker not in original:
            print(f"ERROR: build marker '{marker}' missing from index.html")
            sys.exit(1)

    updated = apply(original, stems, titles, n_ch, n_apx)

    if args.check:
        if updated != original:
            print("index.html is STALE — run: python .build/build_methods.py")
            sys.exit(1)
        print(f"index.html is up to date ({n_ch} chapters, {n_apx} appendices).")
        return

    if updated == original:
        print(f"index.html already in sync ({n_ch} chapters, {n_apx} appendices).")
    else:
        INDEX.write_text(updated, encoding="utf-8")
        print(f"index.html updated: {n_ch} chapters, {n_apx} appendices, "
              f"{len(stems)} manifest entries.")


if __name__ == "__main__":
    main()
