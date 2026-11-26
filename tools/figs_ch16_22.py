"""Figures for Chapters 16 to 22 of Geometric Methods.

Every figure is drawn from a formula, a definition or numbers printed in its chapter. Where a
figure repeats a printed number, the function asserts that the value it computed agrees.
Section 21.8 gives the class of each chapter's numbers, and the captions repeat it.
"""

import json
import math
import os

from figkit import (BOX, CRITICAL, GRID, INK, INK2, INK3, ROOT, SERIES, SURFACE, Axes, Canvas,
                    legend, reg)

CH16 = "chapters/chapter-16-geometric-pipelines.md"
CH17 = "chapters/chapter-17-scaling.md"
CH18 = "chapters/chapter-18-production-deployment.md"
CH19 = "chapters/chapter-19-case-study-defect-prediction.md"
CH20 = "chapters/chapter-20-case-study-bioacoustics.md"
CH21 = "chapters/chapter-21-measurement-discipline.md"
CH22 = "chapters/chapter-22-the-read-metric.md"


def _poly(c, pts, fill, opacity, stroke="none", width=0):
    d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    c.add(f'<polygon points="{d}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
          f'stroke-width="{width}" stroke-linejoin="round"/>')


# ------------------------------------------------------------------ chapter 16
def fig_16_1():
    p = reg(CH16, "16.1",
            "Schematic of the data flow in run_campaign, as the listing of Section 16.2.2 has it. The six stages "
            "run in a fixed order. Five of them call the evaluation function, and the Pareto stage only filters "
            "the results of stage 1. The parameter vector of the best subset found in stage 1 is the point that "
            "stages 3, 4 and 5 probe, so a poor result in stage 1 sends all three to the wrong point.",
            "## 16.2 The `run_campaign` API")
    c = Canvas(720, 420, "One evaluation function and one best configuration feed the stages")
    stages = [("1  Subset enumeration", "optimizes every subset up to max size"),
              ("2  Pareto frontier", "filter over the results of stage 1"),
              ("3  Sensitivity profile", "ablates each dimension"),
              ("4  Model Robustness Index", "perturbs the best configuration"),
              ("5  Adversarial search", "per dimension, from the best point"),
              ("6  Compositional test", "greedy build from a start dimension")]
    x0, w, h, y0, pitch = 220, 240, 42, 66, 54
    c.box(24, y0, 140, pitch * 5 + h, "evaluate_fn", "params in, errors out")
    for i, (name, sub) in enumerate(stages):
        y = y0 + pitch * i
        c.box(x0, y, w, h, name, sub)
        if i:
            c.arrow(x0 + w / 2, y - (pitch - h), x0 + w / 2, y - 1, INK3, 1.5)
        yc = y + h / 2
        if i == 1:
            c.text(192, yc + 4, "no calls", 10, "middle", INK3, italic=True)
        else:
            c.arrow(x0 - 2, yc, 167, yc, SERIES[0], 1.5)
    bx = 520
    y1 = y0 + h / 2
    c.line(x0 + w, y1, bx, y1, SERIES[1], 1.5)
    c.line(bx, y1, bx, y0 + pitch * 4 + h / 2, SERIES[1], 1.5)
    for i in (2, 3, 4):
        yc = y0 + pitch * i + h / 2
        c.arrow(bx, yc, x0 + w + 3, yc, SERIES[1], 1.5)
    c.text(bx + 12, 196, "best_params", 12, "start", INK, "600")
    c.text(bx + 12, 213, "the parameter vector of", 10.5, "start", INK2)
    c.text(bx + 12, 228, "the best subset of stage 1", 10.5, "start", INK2)
    legend(c, 24, 48, [("execution order", INK3), ("calls evaluate_fn", SERIES[0]),
                       ("best configuration from stage 1", SERIES[1])])
    c.text(16, 410, "schematic; all six results are returned in one StructuralFuzzReport", 10.5, "start", INK3,
           italic=True)
    c.save(p)


def fig_16_2():
    n, grid, rand = 5, 20, 5000
    enum = [(k, math.comb(n, k), grid if k == 1 else grid ** 2 if k == 2 else rand) for k in (1, 2, 3, 4)]
    total = sum(m * cost for _, m, cost in enum)
    assert total == 79100
    assert [m * cost for _, m, cost in enum] == [100, 4000, 50000, 25000]
    rows = [(f"size {k}: {m} subsets × {cost:,}", m * cost, 0, f"{m * cost:,}") for k, m, cost in enum]
    rows += [("MRI perturbations", 300, 1, "300"), ("sensitivity profile, 2n", 2 * n, 1, "10"),
             ("adversarial search", 100, 1, "roughly 100")]
    p = reg(CH16, "16.2",
            "The evaluation budget of Section 16.2.3 for five dimensions with the default settings, on a "
            "logarithmic axis. The four rows of subset enumeration are the number of subsets of each size times "
            "the cost of optimizing one, and they sum to 79,100 calls. The MRI, the sensitivity profile and the "
            "adversarial search together add about 410. The counts follow from the formulas of the section and "
            "are not measurements; the compositional test and the baselines are not shown because the section "
            "gives no count for them.",
            "## 16.3 `StructuralFuzzReport`: Structured Output")
    c = Canvas(720, 340, "With five dimensions, enumeration takes nearly all the evaluations")
    ax = Axes(c, 230, 60, 400, 30 * len(rows), (1, 1e5), (0, len(rows)), [], [],
              "calls to the evaluation function, logarithmic scale", "", xlog=True)
    for v, lab in ((1, "1"), (10, "10"), (100, "100"), (1e3, "1,000"), (1e4, "10,000"), (1e5, "100,000")):
        c.line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, GRID, 1)
        c.text(ax.X(v), ax.y0 + ax.h + 16, lab, 11, "middle", INK2)
    for i, (name, v, s, lab) in enumerate(rows):
        y = ax.y0 + 30 * (i + 0.5)
        c.text(ax.x0 - 12, y + 4, name, 11.5, "end", INK2)
        c.line(ax.x0, y, ax.X(v), y, SERIES[s], 2, opacity=0.45)
        c.dot(ax.X(v), y, SERIES[s], 5, title=f"{name}: {lab}")
        c.text(ax.X(v) + 11, y + 4, lab, 11, "start", INK)
    legend(c, 230, 46, [("subset enumeration, 79,100 in all", SERIES[0]), ("other stages", SERIES[1])])
    c.save(p)


# ------------------------------------------------------------------ chapter 17
def fig_17_1():
    def s_of(n, k):
        return sum(math.comb(n, i) for i in range(1, k + 1))

    # Entries of the table in Section 17.2 that agree with the formula. The K = 4 column of that table
    # from n = 20 up, and its K = 3 entry at n = 50, do not agree with the formula and are not used.
    table = {5: (15, 25, 30), 10: (55, 175, 385), 20: (210, 1350, None), 50: (1275, None, None),
             100: (5050, 166750, None), 200: (20100, 1333500, None)}
    for n, row in table.items():
        for k, v in zip((2, 3, 4), row):
            assert v is None or s_of(n, k) == v
    p = reg(CH17, "17.1",
            "The number of subsets of at most K dimensions out of n, the sum S(n, K) of Section 17.2, computed "
            "from that formula and drawn on logarithmic axes. The marked points are at the values of n the "
            "section tabulates. Each curve approaches a straight line of slope K, which is growth as n to the "
            "power K: going from 20 to 200 dimensions multiplies the count by about 100 for K = 2 and by about "
            "10,000 for K = 4. Each of those subsets still has to be optimized.",
            "## 17.3 Greedy Alternatives")
    c = Canvas(720, 400, "Subsets to enumerate grow as n to the power K")
    ax = Axes(c, 110, 52, 470, 280, (5, 200), (10, 2e8), [5, 10, 20, 50, 100, 200], [],
              "number of dimensions n (logarithmic scale)", "", xlog=True, ylog=True)
    c.text(30, ax.y0 + ax.h / 2, "subsets of size at most K", 11.5, "middle", INK2, rotate=-90)
    for v, lab in ((10, "10"), (1e3, "1,000"), (1e5, "100,000"), (1e7, "10 million")):
        c.line(ax.x0, ax.Y(v), ax.x0 + ax.w, ax.Y(v), GRID, 1)
        c.text(ax.x0 - 8, ax.Y(v) + 4, lab, 11, "end", INK2)
    for j, k in enumerate((2, 3, 4)):
        ns = list(range(5, 201))
        c.polyline([(ax.X(n), ax.Y(s_of(n, k))) for n in ns], SERIES[j], 2, title=f"K = {k}")
        for n in table:
            c.dot(ax.X(n), ax.Y(s_of(n, k)), SERIES[j], 4, title=f"n = {n}, K = {k}: {s_of(n, k):,}")
        c.text(ax.X(200) + 12, ax.Y(s_of(200, k)) + 4, f"K = {k}", 11, "start", INK)
    c.save(p)


def fig_17_2():
    rows = [("Attractiveness skew", 0.543, 0.474, 0.07), ("Top-1% mass over its null", 0.399, -0.513, 0.91),
            ("Maximum over its null", 1.101, -1.034, 2.14)]
    for _, a, b, d in rows:
        assert abs(abs(a - b) - d) < 0.006
    p = reg(CH17, "17.2",
            "Slope of three hubness statistics per tenfold increase in corpus size, at k = 10, under two "
            "protocols that differ only in whether the query budget or the number of queries is held constant "
            "(table of Section 17.11.2). The two statistics formed by dividing by a null change sign with the "
            "protocol. The attractiveness skew, which models the sampling and inverts it, gives nearly the same "
            "slope twice. The values are measurements from the openvector-bench campaign, not peer reviewed. "
            "The comparison between protocols stands, but the slopes are not a property of the corpus: queries "
            "and corpus came from different files, and the claim that hubness rises with corpus size was "
            "withdrawn.",
            "### 17.11.3 Rules for Practice")
    c = Canvas(720, 270, "Dividing by a null does not remove the query budget")
    ax = Axes(c, 210, 76, 360, 46 * len(rows), (-1.5, 1.5), (0, len(rows)), [-1, -0.5, 0, 0.5, 1], [],
              "slope per tenfold increase in corpus size", "")
    for v in (-1, -0.5, 0.5, 1):
        c.line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, GRID, 1)
    c.line(ax.X(0), ax.y0, ax.X(0), ax.y0 + ax.h, INK3, 1.5, dash="4 4")
    for i, (name, a, b, d) in enumerate(rows):
        y = ax.y0 + 46 * (i + 0.5)
        c.text(ax.x0 - 14, y + 4, name, 11.5, "end", INK2)
        xa, xb = ax.X(a), ax.X(b)
        c.line(xa, y, xb, y, INK3, 2)
        c.dot(xa, y, SERIES[0], 5, title=f"{name}, constant budget: {a:+.3f}")
        c.dot(xb, y, SERIES[1], 5, title=f"{name}, constant number of queries: {b:+.3f}")
        c.text(min(xa, xb) - 10, y + 4, f"{min(a, b):+.3f}", 10.5, "end", INK)
        c.text(max(xa, xb) + 10, y + 4, f"{max(a, b):+.3f}", 10.5, "start", INK)
        c.text(704, y + 4, f"differ by {d:.2f}", 10.5, "end", INK2, italic=True)
    legend(c, 210, 52, [("constant query budget", SERIES[0]), ("constant number of queries", SERIES[1])])
    c.save(p)


# ------------------------------------------------------------------ chapter 18
def fig_18_1():
    def pareto_hypervolume(dims, maes, ref_dims=10, ref_mae=10.0):
        # the function printed in Section 18.6.2
        points = sorted((d, m) for d, m in zip(dims, maes) if d < ref_dims and m < ref_mae)
        area, best = 0.0, ref_mae
        for i, (d, m) in enumerate(points):
            nxt = points[i + 1][0] if i + 1 < len(points) else ref_dims
            best = min(best, m)
            area += (nxt - d) * (ref_mae - best)
        return area

    base = [(1, 8.0), (2, 5.0), (3, 3.5), (5, 2.5)]
    curr = [(1, 8.0), (5, 2.5)]
    hv_b = pareto_hypervolume(*zip(*base))
    hv_c = pareto_hypervolume(*zip(*curr))
    assert abs(hv_b - 57.5) < 1e-9 and abs(hv_c - 45.5) < 1e-9
    ratio = hv_c / hv_b
    assert ratio < 0.85
    p = reg(CH18, "18.1",
            "The hypervolume indicator of Section 18.6.2 on an invented example. The axes are the number of "
            "active dimensions and the MAE, both minimized, with the default reference point (10, 10). A "
            "baseline frontier of four points dominates an area of 57.5. In the next version the two middle "
            "points are gone and the best MAE is unchanged; the area falls to 45.5, which is 79% of the "
            "baseline and below the 85% bar of the check. The frontier points are illustrative values chosen "
            "for the drawing, not measurements.",
            "### 18.6.3 Integration with Monitoring Infrastructure")
    c = Canvas(720, 400, "A frontier can lose area while its best MAE stays the same")
    ax = Axes(c, 80, 52, 400, 290, (0, 10.6), (0, 10.6), [0, 2, 4, 6, 8, 10], [0, 2, 4, 6, 8, 10],
              "number of active dimensions", "MAE")
    kept = [(1, 10), (1, 8), (5, 8), (5, 2.5), (10, 2.5), (10, 10)]
    lost = [(2, 8), (2, 5), (3, 5), (3, 3.5), (5, 3.5), (5, 8)]
    _poly(c, [(ax.X(x), ax.Y(y)) for x, y in kept], SERIES[0], 0.22)
    _poly(c, [(ax.X(x), ax.Y(y)) for x, y in lost], CRITICAL, 0.30)
    stair = [(1, 10), (1, 8), (2, 8), (2, 5), (3, 5), (3, 3.5), (5, 3.5), (5, 2.5), (10, 2.5)]
    c.polyline([(ax.X(x), ax.Y(y)) for x, y in stair], INK2, 1.5, title="baseline frontier")
    for d, m in base:
        gone = (d, m) not in curr
        c.dot(ax.X(d), ax.Y(m), CRITICAL if gone else SERIES[0], 5,
              title=f"{d} dimensions, MAE {m}" + (", lost in the next version" if gone else ""))
    c.add(f'<rect x="{ax.X(10) - 4:.2f}" y="{ax.Y(10) - 4:.2f}" width="8" height="8" fill="{INK}"/>')
    c.text(ax.X(10) - 9, ax.Y(10) - 8, "reference point", 10.5, "end", INK2)
    c.text(ax.X(7.5), ax.Y(6.4), "still dominated", 11, "middle", INK)
    c.text(ax.X(4), ax.Y(6.4) , "lost", 11, "middle", INK)
    x0 = 512
    c.text(x0, 110, "baseline, four points", 12, "start", INK, "600")
    c.text(x0, 129, f"area {hv_b:.1f}", 11.5, "start", INK2)
    c.text(x0, 168, "next version, two points", 12, "start", INK, "600")
    c.text(x0, 187, f"area {hv_c:.1f}", 11.5, "start", INK2)
    c.text(x0, 226, f"ratio {100 * ratio:.0f}%", 12, "start", INK, "600")
    c.text(x0, 245, "below the 85% bar: alert", 11.5, "start", INK2)
    legend(c, 80, 40, [("area still dominated", SERIES[0]), ("area lost", CRITICAL)])
    c.text(16, 390, "illustrative frontier, not measured", 10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 19
def fig_19_1():
    rows = [("{OO, Process}", 50.2), ("{Size, Complexity}", 58.5), ("{Complexity, Halstead, Process}", 58.4),
            ("{Complexity}", 53.6), ("{Size, Complexity, Halstead}", 57.7), ("All five groups", 53.3)]
    oracle, target, se = 54.5, 80.0, 5.0
    lo, hi = 43.0, 59.0
    assert all(abs(v - 50) <= 2 * se for _, v in rows) and 50 - 2 * se <= lo and hi <= 50 + 2 * se
    p = reg(CH19, "19.1",
            "AUC on the 300 test modules for the six configurations whose AUC the table of Section 19.4.1 "
            "prints, in percent. The shaded band is two standard errors either side of chance, with the "
            "standard error of about 5 points given in Section 19.5.1. The bar under the rows is the range of "
            "all 31 configurations, 43 to 59. The generator's own formula, used as an oracle, reaches 54.5, and "
            "the target the evaluation function scores against is 80. Measured on one recorded run; exploratory, "
            "since no prediction was registered before it.",
            "### 19.5.2 The Winner Is a Draw")
    c = Canvas(720, 400, "Every AUC sits near chance; the target is beyond the oracle")
    nrow = len(rows) + 1
    ax = Axes(c, 226, 76, 420, 34 * nrow, (40, 85), (0, nrow), [40, 50, 60, 70, 80], [],
              "AUC on the test modules, percent", "")
    c.add(f'<rect x="{ax.X(40):.2f}" y="{ax.y0:.2f}" width="{ax.X(60) - ax.X(40):.2f}" height="{ax.h:.2f}" '
          f'fill="{BOX}" fill-opacity="0.75"/>')
    for i, (name, v) in enumerate(rows):
        y = ax.y0 + 34 * (i + 0.5)
        c.text(ax.x0 - 12, y + 4, name, 11.5, "end", INK2)
        c.line(ax.x0, y, ax.x0 + ax.w, y, GRID, 1)
    for x, lab, col in ((50, "chance", INK3), (oracle, "oracle 54.5", CRITICAL), (target, "target 80", INK3)):
        c.line(ax.X(x), ax.y0, ax.X(x), ax.y0 + ax.h, col, 1.5, dash="4 4")
        c.text(ax.X(x) + 4, ax.y0 - 6, lab, 10.5, "start", INK2, italic=True)
    for i, (name, v) in enumerate(rows):
        y = ax.y0 + 34 * (i + 0.5)
        c.dot(ax.X(v), y, SERIES[0], 5, title=f"{name}: AUC {v}")
        c.text(ax.x0 + ax.w + 8, y + 4, f"{v:.1f}", 10.5, "start", INK)
    y = ax.y0 + 34 * (nrow - 0.5)
    c.text(ax.x0 - 12, y + 4, "range of all 31 configurations", 11.5, "end", INK2)
    c.line(ax.X(lo), y, ax.X(hi), y, SERIES[0], 4)
    c.text(ax.x0 + ax.w + 8, y + 4, "43 to 59", 10.5, "start", INK)
    legend(c, 226, 48, [("within two standard errors of chance", "#22405c")])
    c.text(16, 390, "one recorded run, exploratory", 10.5, "start", INK3, italic=True)
    c.save(p)


def fig_19_2():
    # MAE of each configuration on a greedy path, by number of active groups (Sections 19.4.1 and 19.6)
    comp = [(1, 49.22), (2, 47.23), (3, 47.45), (4, 48.13), (5, 48.27)]
    fwd = [(1, 47.34), (2, 47.23), (3, 47.45), (4, 48.13)]
    bwd = [(5, 48.27), (4, 47.47), (3, 48.24), (2, 47.23), (1, 47.34)]
    best, floor = 39.40, (70 + 65 + 67) / 5
    assert abs(floor - 40.4) < 1e-9
    assert comp[1][1] == fwd[1][1] == bwd[3][1] and comp[4][1] == bwd[0][1] and fwd[0][1] == bwd[4][1]
    assert min(v for path in (comp, fwd, bwd) for _, v in path) > floor > best
    p = reg(CH19, "19.2",
            "MAE of every configuration the three greedy searches of Section 19.6 visit, against the number of "
            "active feature groups. Where two paths pass through the same configuration their markers are "
            "drawn side by side. All of them lie between 47.2 and 49.3, above the floor of 40.4 that any "
            "configuration with zero recall must have. The exhaustive optimum, {OO, Process} at 39.40, is below "
            "that floor because of one correct positive prediction, and no greedy path reaches it. Measured on "
            "one recorded run; exploratory.",
            "## 19.7 The Model Robustness Index")
    c = Canvas(720, 400, "The exhaustive optimum is an isolated point no greedy path reaches")
    ax = Axes(c, 70, 60, 540, 272, (0.5, 5.5), (38, 51), [1, 2, 3, 4, 5], [38, 40, 42, 44, 46, 48, 50],
              "number of active feature groups", "MAE, points")
    yf = ax.Y(floor)
    c.line(ax.x0, yf, ax.x0 + ax.w, yf, INK3, 1.5, dash="4 4")
    c.text(ax.x0 + ax.w, yf - 6, "40.4: least MAE with zero recall", 10.5, "end", INK2, italic=True)
    names = ("composition from Size", "forward selection", "backward elimination")
    for j, (path, dx) in enumerate(((comp, -9), (fwd, 0), (bwd, 9))):
        pts = [(ax.X(k) + dx, ax.Y(v)) for k, v in path]
        c.polyline(pts, SERIES[j], 2, title=names[j])
        for (x, y), (k, v) in zip(pts, path):
            c.dot(x, y, SERIES[j], 4, title=f"{names[j]}, {k} groups: MAE {v:.2f}")
    c.dot(ax.X(2), ax.Y(best), CRITICAL, 5.5, title="{OO, Process}: MAE 39.40")
    c.text(ax.X(2) + 13, ax.Y(best) + 4, "{OO, Process} 39.40, the exhaustive optimum", 11, "start", INK)
    c.text(ax.X(1) - 14, ax.Y(49.22) - 11, "{Size} 49.22", 10.5, "start", INK2)
    c.text(ax.X(5) + 18, ax.Y(48.27) + 4, "all five 48.27", 10.5, "start", INK2)
    legend(c, 70, 46, [(nm, SERIES[j]) for j, nm in enumerate(names)])
    c.text(16, 390, "one recorded run, exploratory", 10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 20
def fig_20_1():
    rows = [("time_shift", 0, 0.300, 0.281), ("amplitude_scale", 0, 0.0, 1.0), ("additive_noise", 0, 0.0, 1.0),
            ("pink_noise", 0, 0.0, 1.0), ("time_stretch", 1, 0.150, 0.922), ("click_dropout", 1, 0.138, 1.0),
            ("doppler_shift", 1, 0.075, 1.0), ("multipath_echo", 1, 0.0, 1.0), ("spectral_mask", 1, 0.0, 1.0)]
    assert len(rows) == 9 and sum(1 for r in rows if r[1] == 0) == 4
    p = reg(CH20, "20.1",
            "The robustness measurement of Section 20.9.3 on the template decoder, one row for each of the nine "
            "transforms, grouped by the class Section 20.5.1 gives them. Left: mean omega at intensity 1.0. "
            "Right: the least intensity that flips the decision, where 1.000 is the top of the searched range "
            "and means no flip was found. A decoder should not respond at all to an invariant transform, and "
            "time_shift, which is one, has the largest omega and flips the decision at 0.281. The numbers come "
            "from an executed notebook that is not committed, so they have no public record yet.",
            "### 20.9.4 What Remains to Be Run")
    c = Canvas(720, 400, "A shift in time flips the template decoder; noise does not")
    pitch, y0 = 28, 80
    axl = Axes(c, 150, y0, 210, pitch * 9, (0, 0.3), (0, 9), [0, 0.1, 0.2, 0.3], [], "mean omega at intensity 1.0", "")
    axr = Axes(c, 440, y0, 210, pitch * 9, (0, 1), (0, 9), [0, 0.25, 0.5, 0.75, 1], [], "flip threshold", "")
    for ax, ticks in ((axl, (0.1, 0.2, 0.3)), (axr, (0.25, 0.5, 0.75))):
        for v in ticks:
            c.line(ax.X(v), y0, ax.X(v), y0 + ax.h, GRID, 1)
        c.line(ax.x0, y0, ax.x0, y0 + ax.h, GRID, 1)
    c.line(axr.X(1), y0, axr.X(1), y0 + axr.h, INK3, 1.5, dash="4 4")
    c.text(axr.X(1), y0 - 7, "top of the searched range", 10.5, "end", INK2, italic=True)
    for i, (name, cls, om, thr) in enumerate(rows):
        y = y0 + pitch * (i + 0.5)
        col = SERIES[cls]
        kind = "invariant" if cls == 0 else "stress"
        c.text(axl.x0 - 12, y + 4, name, 11.5, "end", INK2)
        if om > 0:
            c.hrect(axl.x0, y - 7, axl.X(om) - axl.x0, 14, col, title=f"{name} ({kind}): mean omega {om:.3f}")
        else:
            c.line(axl.x0, y - 7, axl.x0, y + 7, col, 3)
        c.text(axl.X(om) + 7, y + 4, f"{om:.3f}", 10.5, "start", INK)
        c.hrect(axr.x0, y - 7, axr.X(thr) - axr.x0, 14, col, title=f"{name} ({kind}): flip threshold {thr:.3f}")
        c.text(axr.X(1) + 9, y + 4, f"{thr:.3f}", 10.5, "start", INK)
    ysep = y0 + pitch * 4
    c.line(24, ysep, 696, ysep, GRID, 1)
    legend(c, 150, 48, [("invariant transform", SERIES[0]), ("stress transform", SERIES[1])])
    c.text(16, 390, "20 synthesized signals; the executed notebook is not committed", 10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 21
def fig_21_1():
    p = reg(CH21, "21.1",
            "Schematic of the order of events that makes a statement measured (Section 21.2). The registration "
            "is written and sealed in a commit before the run. Amendments are allowed only between the seal and "
            "the unblinding of the data. The seal commit must be an ancestor of the first commit that holds the "
            "result, which is how priority is shown. Grading by the registered code then has three outcomes, "
            "and the registration says in advance which gate leads to which.",
            "## 21.3 Frozen-Null Gates")
    c = Canvas(720, 400, "Registration, then the run, then grading: the order is the evidence")
    y, h, w = 100, 52, 152
    xs = [20, 196, 372, 548]
    top = [("Registration", "prediction, bar, design"), ("Seal commit", "content hash recorded"),
           ("Run", "measurement made"), ("Result commit", "every outcome kept")]
    for x, (a, b) in zip(xs, top):
        c.box(x, y, w, h, a, b)
    for x in xs[:-1]:
        c.arrow(x + w + 2, y + h / 2, x + w + 22, y + h / 2, INK2, 1.5)
    # ancestry bracket from the seal commit to the result commit
    xa, xb = xs[1] + w / 2, xs[3] + w / 2
    c.line(xa, y - 2, xa, 76, SERIES[0], 1.5)
    c.line(xa, 76, xb, 76, SERIES[0], 1.5)
    c.arrow(xb, 76, xb, y - 2, SERIES[0], 1.5)
    c.text((xa + xb) / 2, 68, "must be an ancestor of", 11, "middle", INK)
    # what happens before the data are seen
    c.line(xs[0], 170, xs[1] + w, 170, INK3, 1.5)
    c.line(xs[0], 164, xs[0], 176, INK3, 1.5)
    c.line(xs[1] + w, 164, xs[1] + w, 176, INK3, 1.5)
    c.text((xs[0] + xs[1] + w) / 2, 188, "fixed before the data are seen", 11, "middle", INK2)
    c.text((xs[1] + w + xs[2]) / 2 + 76, 188, "amendments: dated, with a reason,", 10.5, "middle", INK2, italic=True)
    c.text((xs[1] + w + xs[2]) / 2 + 76, 202, "before the data are unblinded", 10.5, "middle", INK2, italic=True)
    c.line(xs[1] + w + 12, 152, xs[1] + w + 12, 176, INK3, 1, dash="3 3")
    # grading
    gx, gy, gw = 284, 232, 152
    c.box(gx, gy, gw, h, "Grading", "by the registered code")
    c.line(xb, y + h, xb, gy + h / 2, INK2, 1.5)
    c.arrow(xb, gy + h / 2, gx + gw + 3, gy + h / 2, INK2, 1.5)
    outs = [(60, "Instrument gate missed", "run void, claim not refuted", SERIES[1]),
            (275, "Physics gate missed", "claim refuted", CRITICAL),
            (490, "Bar met", "demonstrated, in one setting", SERIES[0])]
    for x, a, b, col in outs:
        c.box(x, 320, 170, h, a, b, stroke=col)
        c.arrow(gx + gw / 2 + (x - 275) * 0.25, gy + h + 2, x + 85, 318, INK2, 1.5)
    c.text(16, 392, "schematic of Sections 21.2 to 21.4", 10.5, "start", INK3, italic=True)
    c.save(p)


def fig_21_2():
    def tail(z):
        return 0.5 * math.erfc(z / math.sqrt(2))

    assert abs(tail(0) - 0.5) < 1e-12 and abs(tail(1.6448536) - 0.05) < 1e-6
    p = reg(CH21, "21.2",
            "The probability that a system with no effect passes a frozen-null gate, as a function of the "
            "margin measured in standard errors of the difference under no effect, from equation (21.2). The "
            "vertical axis is logarithmic. A margin of zero passes half the time. Margins of one, two and "
            "three standard errors pass about 16%, 2.3% and 0.13% of the time. A margin stated without the "
            "standard error has no place on the horizontal axis, so its false-pass rate is unknown.",
            "## 21.4 Admissibility")
    c = Canvas(720, 400, "A margin sized in noise units has a known false-pass rate")
    ax = Axes(c, 90, 52, 520, 280, (0, 3.5), (1e-4, 1), [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5], [],
              "margin δ in standard errors of the difference, z", "", ylog=True)
    c.text(26, ax.y0 + ax.h / 2, "probability of passing with no effect", 11.5, "middle", INK2, rotate=-90)
    for v, lab in ((1, "1"), (0.1, "0.1"), (0.01, "0.01"), (1e-3, "0.001"), (1e-4, "0.0001")):
        c.line(ax.x0, ax.Y(v), ax.x0 + ax.w, ax.Y(v), GRID, 1)
        c.text(ax.x0 - 8, ax.Y(v) + 4, lab, 11, "end", INK2)
    zs = [3.5 * i / 140 for i in range(141)]
    c.polyline([(ax.X(z), ax.Y(tail(z))) for z in zs], SERIES[0], 2, title="1 − Φ(z)")
    for z, lab in ((0, "0.5"), (1, "0.159"), (2, "0.023"), (3, "0.0013")):
        assert abs(tail(z) - float(lab)) < 0.6 * 10 ** -(len(lab.split(".")[1]))
        c.dot(ax.X(z), ax.Y(tail(z)), SERIES[0], 4.5, title=f"z = {z}: {tail(z):.4f}")
        c.text(ax.X(z) + 11, ax.Y(tail(z)) - 7, lab, 11, "start", INK)
    c.text(ax.X(2.45), ax.Y(0.3), "Pr(pass | no effect) = 1 − Φ(z)", 11.5, "start", INK2, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 22
def fig_22_1():
    v1, v2, deg = 2.0, 0.5, 30
    p = reg(CH22, "22.1",
            "Two read metrics on the same plane, each shown by the set of displacements whose loss is at most 1. "
            "Left: the whitening consumer, whose read metric is the inverse covariance, so the set is the "
            "Mahalanobis ellipse of Chapter 2, closed in every direction. Right: a consumer that reads one "
            "linear combination of the coordinates. Its read metric has rank 1, the set is a strip that never "
            "closes, and a displacement along the strip, the kernel, costs nothing. Drawn for a covariance "
            "with variances 2 and 0.5 on axes turned by 30 degrees, and a read direction at 30 degrees; these "
            "are illustrative values.",
            "## 22.2 Computing the Metric When the Consumer Can Only Be Queried")
    c = Canvas(720, 400, "The Mahalanobis matrix is one read metric, and it has no kernel")
    th = math.radians(deg)
    ux, uy = math.cos(th), -math.sin(th)      # read direction on the screen (y points down)
    kx, ky = math.sin(th), math.cos(th)       # the direction orthogonal to it
    s = 56
    for cx in (190, 530):
        c.line(cx - 150, 212, cx + 150, 212, GRID, 1)
        c.line(cx, 92, cx, 332, GRID, 1)
    # left: ellipse of the whitening consumer
    cx, cy = 190, 212
    c.ellipse(cx, cy, s * math.sqrt(v1), s * math.sqrt(v2), -deg, SERIES[0], SERIES[0], 2, 0.14,
              title="displacements with squared Mahalanobis distance at most 1")
    for a, (dx, dy) in ((math.sqrt(v1), (ux, uy)), (math.sqrt(v2), (kx, ky))):
        c.arrow(cx, cy, cx + s * a * dx, cy + s * a * dy, INK2, 1.5)
    c.text(cx, 62, "whitening consumer", 12, "middle", INK, "600")
    c.text(cx, 79, "c(x) = Σ^(−1/2) (x − μ)", 11, "middle", INK2)
    c.text(cx, 356, "read metric Σ⁻¹: rank 2, no kernel", 11.5, "middle", INK2)
    # right: strip of a consumer that reads one direction
    cx, cy = 530, 212
    half = 100
    corners = [(cx + s * ux * a + half * kx * b, cy + s * uy * a + half * ky * b)
               for a, b in ((1, -1), (1, 1), (-1, 1), (-1, -1))]
    _poly(c, corners, SERIES[1], 0.14)
    c.line(*corners[0], *corners[1], SERIES[1], 2)
    c.line(*corners[2], *corners[3], SERIES[1], 2)
    c.line(cx - half * kx, cy - half * ky, cx + half * kx, cy + half * ky, INK3, 1.5, dash="5 5")
    c.arrow(cx, cy, cx + s * ux, cy + s * uy, INK2, 1.5)
    c.text(cx + s * ux + 10, cy + s * uy - 6, "read direction u", 11, "start", INK)
    c.text(cx - half * kx - 8, cy - half * ky - 8, "kernel: not read", 11, "end", INK2)
    c.text(cx, 62, "consumer that reads one direction", 12, "middle", INK, "600")
    c.text(cx, 79, "c(x) = u · x", 11, "middle", INK2)
    c.text(cx, 356, "read metric u uᵀ: rank 1, the strip never closes", 11.5, "middle", INK2)
    c.text(16, 390, "sets of displacements with loss at most 1; illustrative covariance and direction", 10.5, "start",
           INK3, italic=True)
    c.save(p)


def fig_22_2():
    rates = [1, 2, 4]
    recon = {"identity": [1.012, 0.638, 0.307], "estimated": [1.414, 1.002, 0.722]}
    loss = {"identity": [0.630, 0.388, 0.170], "estimated": [0.300, 0.129, 0.033]}
    printed_ratio = [0.476, 0.334, 0.196]
    for a, b, r in zip(loss["estimated"], loss["identity"], printed_ratio):
        assert abs(a / b - r) < 0.003
    assert all(e > i for e, i in zip(recon["estimated"], recon["identity"]))
    run = os.path.join(ROOT, "formal", "runs", "ch22_read_metric.json")
    if os.path.exists(run):  # the table of Section 22.4 and the recorded run agree
        with open(run, encoding="utf-8") as f:
            rec = json.load(f)["rates"]
        for i, row in enumerate(rec):
            assert row["rate_nats"] == rates[i]
            for key, name in (("identity_weight", "identity"), ("estimated_weight", "estimated")):
                assert abs(row[key]["reconstruction_error"] - recon[name][i]) < 6e-4
                assert abs(row[key]["consumer_loss"] - loss[name][i]) < 6e-4
            assert abs(row["loss_ratio_weighted_over_identity"] - printed_ratio[i]) < 6e-4
    p = reg(CH22, "22.2",
            "The recorded run of Section 22.4: two allocations of the same description rate, one by "
            "reverse water-filling with the identity weight and one with the read metric estimated from 200 "
            "probe points. Left: reconstruction error, tr Δ. Right: the consumer loss measured on 200,000 "
            "simulated vectors. At 1, 2 and 4 nats the weighted allocation has the larger reconstruction error "
            "and the smaller consumer loss, by ratios of 0.476, 0.334 and 0.196. The result is exploratory: one "
            "synthetic consumer and one seed, with a kernel that is the same at every point.",
            "## 22.5 When One Averaged Matrix Is the Wrong Object")
    c = Canvas(720, 400, "Worse reconstruction, better service to the consumer, at every rate")
    panels = [(80, recon, (0, 1.6), [0, 0.4, 0.8, 1.2, 1.6], "reconstruction error, tr Δ"),
              (430, loss, (0, 0.7), [0, 0.2, 0.4, 0.6], "consumer loss, measured")]
    for x0, data, ylim, yticks, name in panels:
        ax = Axes(c, x0, 84, 250, 236, (0, 3), ylim, [], yticks, "description rate, nats per vector", "")
        c.text(x0, 70, name, 12, "start", INK, "600")
        for i, r in enumerate(rates):
            xm = ax.X(i + 0.5)
            for j, key in enumerate(("identity", "estimated")):
                v = data[key][i]
                x = xm - 29 + j * 34
                c.rect(x, ax.Y(v), 24, ax.Y(0) - ax.Y(v), SERIES[j], 4,
                       title=f"{name}, {r} nats, {key} weight: {v:.3f}")
                c.text(x + 12, ax.Y(v) - 6, f"{v:.3f}", 10.5, "middle", INK)
            c.text(xm, ax.Y(0) + 16, str(r), 11, "middle", INK2)
    legend(c, 80, 46, [("identity weight", SERIES[0]), ("estimated read metric", SERIES[1])])
    c.text(16, 390, "one recorded run, one synthetic consumer, one seed: exploratory", 10.5, "start", INK3,
           italic=True)
    c.save(p)
