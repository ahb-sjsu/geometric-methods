"""Figures for Chapters 8 to 15 (Pareto optimization to Cholesky parameterization).

Every figure is drawn from a formula, a definition or numbers printed in its chapter. The
tables of Chapters 8, 9, 11 and 12 are posited illustrations (Section 21.8), and the
figures that use them say so in their captions. Section 14.9 is a registered experiment in
which prediction P3 failed; Figure 14.2 shows it as failed.
"""

import itertools
import math

from figkit import (BORDER, BOX, CRITICAL, GRID, INK, INK2, INK3, SERIES, SURFACE, Axes, Canvas,
                    legend, reg)

CH08 = "chapters/chapter-08-pareto-optimization.md"
CH09 = "chapters/chapter-09-adversarial-robustness.md"
CH10 = "chapters/chapter-10-adversarial-probing.md"
CH11 = "chapters/chapter-11-subset-enumeration.md"
CH12 = "chapters/chapter-12-compositional-testing.md"
CH13 = "chapters/chapter-13-group-theoretic-augmentation.md"
CH14 = "chapters/chapter-14-gradient-reversal.md"
CH15 = "chapters/chapter-15-cholesky-parameterization.md"


def _canvas(w, h, title):
    assert len(title) <= 68, (len(title), title)
    return Canvas(w, h, title)


def _dominates(a, b):
    """Section 8.1.1: a dominates b when it is no worse on both objectives and better on one."""
    return a[0] <= b[0] and a[1] <= b[1] and (a[0] < b[0] or a[1] < b[1])


def _darrow(c, pts, col, width=1.8):
    """Dashed poly-line with an arrow head at its last point."""
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        c.line(x1, y1, x2, y2, col, width, dash="5 4")
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    for s in (+1, -1):
        a = ang + s * 2.6
        c.line(x2, y2, x2 + 8 * math.cos(a), y2 + 8 * math.sin(a), col, width)


# ------------------------------------------------------------------ chapter 8
def fig_8_1():
    front = [(0.5, 4.5), (1.0, 3.0), (2.0, 2.6), (3.0, 1.0), (4.5, 0.5)]
    pocket = (2.0, 2.6)
    dominated = [(1.5, 4.6), (2.5, 4.0), (3.5, 3.0), (4.0, 2.0)]
    allp = front + dominated
    assert [p for p in allp if not any(_dominates(q, p) for q in allp)] == front
    winners = set()
    for i in range(1, 1000):
        w1 = i / 1000
        winners.add(min(front, key=lambda p: w1 * p[0] + (1 - w1) * p[1]))
    assert pocket not in winners and winners == set(front) - {pocket}
    assert abs(sum(pocket) - 4.6) < 1e-12 and sum(front[1]) == 4.0 and sum(front[3]) == 4.0
    p = reg(CH08, "8.1",
            "Why a weighted sum cannot reach every point of a Pareto frontier, on nine illustrative points with "
            "both objectives to be minimized. Minimizing a weighted sum slides a straight line toward the "
            "origin until it first touches a point; for equal weights (dashed) the line rests on two points, "
            "where the sum is 4, and passes below the point between them, where the sum is 4.6. That point lies "
            "in a non-convex pocket: it is not dominated, yet in each of 999 weightings tried, from 0.001 to "
            "0.999 on the first objective, another point has the smaller weighted sum.",
            "### 8.2.3 The Preference Inversion Problem")
    c = _canvas(720, 400, "A weighted sum cannot reach a point in a pocket of the frontier")
    ax = Axes(c, 90, 56, 420, 280, (0, 5), (0, 5), [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5],
              "objective 1 (lower is better)", "objective 2 (lower is better)")
    c.line(ax.X(0), ax.Y(4), ax.X(4), ax.Y(0), INK3, 1.5, dash="5 4")
    for q in dominated:
        c.dot(ax.X(q[0]), ax.Y(q[1]), INK3, 3.5, title=f"dominated ({q[0]:g}, {q[1]:g})")
    for q in front:
        col = CRITICAL if q == pocket else SERIES[0]
        c.dot(ax.X(q[0]), ax.Y(q[1]), col, 5, title=f"non-dominated ({q[0]:g}, {q[1]:g})")
    c.text(ax.X(pocket[0]) + 11, ax.Y(pocket[1]) - 7, "in the pocket", 11, "start", INK)
    legend(c, 90, 44, [("reached by some weighting", SERIES[0]), ("never reached", CRITICAL), ("dominated", INK3)])
    x0 = 532
    for k, s in enumerate(["equal weights:", "the line rests on two", "points, where the sum is 4,", "and misses the point",
                           "between them, where", "the sum is 4.6"]):
        c.text(x0, 120 + 17 * k, s, 11, "start", INK2)
    c.text(16, 390, "illustrative points, not data", 10.5, "start", INK3, italic=True)
    c.save(p)


def fig_8_2():
    ks = [1, 2, 3, 5]
    mae = [3.8, 2.1, 1.7, 1.5]
    rho = [(mae[i] - mae[i + 1]) / (ks[i + 1] - ks[i]) for i in range(3)]
    assert [round(r, 2) for r in rho] == [1.70, 0.40, 0.10]
    # the rule of Section 8.7.3: select the configuration just before rho drops below the threshold
    chosen = next(ks[i] for i in range(3) if rho[i] < 0.3)
    assert chosen == 3
    p = reg(CH08, "8.2",
            "The selection rule of Section 8.7.3 on the frontier of Section 8.7.2 (illustrative values, not a "
            "recorded run), with the number of feature groups k on the horizontal axis and the error MAE on the "
            "vertical. Each segment is labelled with its marginal return, the error removed per group added: "
            "1.70, 0.40, then 0.10. With a threshold of 0.3 the rule stops at k = 3, the last point reached by "
            "a step that returns at least the threshold. No point stands at k = 4, because no four-group "
            "configuration is on this frontier.",
            "## 8.8 The Defect Prediction Example")
    c = _canvas(720, 400, "Marginal return along the frontier: stop where the slope flattens")
    ax = Axes(c, 70, 52, 540, 280, (0.5, 5.5), (0, 4.5), [1, 2, 3, 4, 5], [0, 1, 2, 3, 4],
              "number of feature groups k", "MAE")
    pts = [(ax.X(k), ax.Y(m)) for k, m in zip(ks, mae)]
    c.polyline(pts, SERIES[0], 2, title="Pareto frontier")
    for i, r in enumerate(rho):
        mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
        c.text(mx - 9, my + 17, f"return {r:.2f}", 11, "end", INK)
    x3, y3 = pts[2]
    c.add(f'<circle cx="{x3:.2f}" cy="{y3:.2f}" r="11" fill="none" stroke="{CRITICAL}" stroke-width="2"/>')
    for (x, y), k, m in zip(pts, ks, mae):
        c.dot(x, y, SERIES[0], 4.5, title=f"k = {k}, MAE {m}")
        c.text(x, y - 16, f"{m:g}", 11, "middle", INK)
    c.text(x3 + 18, y3 - 30, "selected: the next step returns less than 0.3", 11, "start", INK)
    c.text(16, 390, "illustrative values (Section 8.7.2)", 10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 9
def fig_9_1():
    sigma, h_sharp, h_broad = 0.5, 8.0, 0.5
    rise = lambda h, d: 0.5 * h * d * d                      # Section 9.7.1, one parameter
    mean = lambda h: 0.5 * sigma ** 2 * h                    # E[omega] = (sigma^2 / 2) tr(H)
    assert mean(h_sharp) == 1.0 and mean(h_broad) == 0.0625
    assert rise(h_sharp, sigma) == mean(h_sharp) and rise(h_broad, sigma) == mean(h_broad)
    p = reg(CH09, "9.1",
            "A sharp and a broad minimum with the same minimum value, in one parameter: the rise in loss "
            "(vertical) against the perturbation of the parameter (horizontal), from the quadratic form of "
            "Section 9.7.1 with curvatures 8 and 0.5, values chosen for the figure. Under a Gaussian "
            "perturbation of standard deviation 0.5 the mean rise is half the variance times the curvature: 1 "
            "for the sharp minimum and 0.0625 for the broad one, sixteen times less. An evaluation at the "
            "minimum alone gives the two the same score.",
            "### 9.7.2 Directional Robustness")
    c = _canvas(720, 400, "Same minimum value, different cost of a perturbation")
    ax = Axes(c, 70, 56, 400, 276, (-1.5, 1.5), (0, 2.2), [-1.5, -1, -0.5, 0, 0.5, 1, 1.5], [0, 0.5, 1, 1.5, 2],
              "perturbation of the parameter, δ", "rise in loss")
    for s in (-sigma, sigma):
        c.line(ax.X(s), ax.y0 + 14, ax.X(s), ax.y0 + ax.h, INK3, 1.5, dash="4 4")
        c.text(ax.X(s), ax.y0 + 8, "δ = −σ" if s < 0 else "δ = +σ", 10.5, "middle", INK2)
    for j, h in enumerate((h_sharp, h_broad)):
        dmax = min(1.5, math.sqrt(2 * 2.2 / h))
        ds = [-dmax + 2 * dmax * i / 200 for i in range(201)]
        c.polyline([(ax.X(d), ax.Y(rise(h, d))) for d in ds], SERIES[j], 2, title=f"curvature {h:g}")
        for s in (-sigma, sigma):
            c.dot(ax.X(s), ax.Y(rise(h, s)), SERIES[j], 4.5, title=f"curvature {h:g}: rise {rise(h, s):g} at δ = σ")
    legend(c, 70, 44, [("sharp minimum", SERIES[0]), ("broad minimum", SERIES[1])])
    x0 = 494
    c.text(x0, 104, "drawn for σ = 0.5", 11, "start", INK2, italic=True)
    c.text(x0, 140, "sharp, curvature 8", 12, "start", INK, "600")
    c.text(x0, 158, "rise at δ = σ: 1", 11, "start", INK2)
    c.text(x0, 196, "broad, curvature 0.5", 12, "start", INK, "600")
    c.text(x0, 214, "rise at δ = σ: 0.0625", 11, "start", INK2)
    c.text(x0, 252, "mean rise under δ ~ N(0, σ²)", 11, "start", INK2)
    c.text(x0, 269, "= (σ² / 2) × curvature,", 11, "start", INK2)
    c.text(x0, 286, "the same two numbers", 11, "start", INK2)
    c.save(p)


def fig_9_2():
    # Section 9.6.3 (illustrative): (dimension, threshold ratio on decrease, on increase, targets)
    rows = [("Complexity", 0.30, None, "high-complexity modules", None),
            ("Process", 0.12, 4.2, "legacy modules", "high-churn modules"),
            ("Size", 0.08, None, "small modules", None),
            ("OO", None, None, None, None),
            ("Halstead", None, None, None, None)]
    lo_edge, hi_edge = 1e-3, 1e3   # Section 9.4.1: search from the fitted value to 1000 times it, and down to 1/1000
    p = reg(CH09, "9.2",
            "The tipping points of Section 9.6.3 (illustrative values, not a recorded run). The horizontal axis "
            "is one parameter as a multiple of its fitted value, on a logarithmic scale over the range of the "
            "threshold search, 1/1000 to 1000. Each band covers the multiples at which every target stays "
            "within the tolerance of 0.5, and a marked end is the first value at which a target breaks, "
            "labelled with that target. OO and Halstead show no tipping point anywhere in the range; a "
            "direction with no row in the table of Section 9.6.3 is drawn as reaching the edge.",
            "### 9.6.4 Synthesis")
    c = _canvas(720, 400, "Tipping points: how far each parameter moves before a target breaks")
    rh = 46
    ax = Axes(c, 130, 76, 540, rh * len(rows), (lo_edge, hi_edge), (0, 1), [], [],
              "parameter as a multiple of its fitted value (logarithmic scale)", "", xlog=True)
    for v, lab in ((1e-3, "0.001"), (1e-2, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100"), (1000, "1000")):
        c.line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, GRID, 1)
        c.text(ax.X(v), ax.y0 + ax.h + 16, lab, 11, "middle", INK2)
    for i, (name, lo, hi, tlo, thi) in enumerate(rows):
        y = ax.y0 + rh * (i + 0.5)
        c.text(ax.x0 - 10, y + 4, name, 11.5, "end", INK2)
        xa, xb = ax.X(lo or lo_edge), ax.X(hi or hi_edge)
        c.add(f'<rect x="{xa:.2f}" y="{y - 5:.2f}" width="{xb - xa:.2f}" height="10" rx="3" fill="{SERIES[0]}" '
              f'fill-opacity="0.85"><title>{name}: within tolerance</title></rect>')
        if lo:
            c.dot(xa, y, CRITICAL, 5.5, title=f"{name}, decrease: {lo:g} ({tlo})")
            c.text(xa - 11, y + 4, f"{lo:.2f}, {tlo}", 10.5, "end", INK)
        if hi:
            c.dot(xb, y, CRITICAL, 5.5, title=f"{name}, increase: {hi:g} ({thi})")
            c.text(xb + 11, y + 4, f"{hi:g}, {thi}", 10.5, "start", INK)
        if not lo and not hi:
            c.text(ax.X(1) + 8, y - 10, "no tipping point in the range", 10.5, "start", INK2, italic=True)
    c.line(ax.X(1), ax.y0 - 4, ax.X(1), ax.y0 + ax.h, INK, 1.5, dash="4 4")
    c.text(ax.X(1), ax.y0 - 9, "fitted value", 10.5, "middle", INK2)
    legend(c, 130, 44, [("every target within tolerance", SERIES[0]), ("first value that breaks a target", CRITICAL)])
    c.text(16, 390, "illustrative values (Section 9.6.3)", 10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 10
def fig_10_1():
    astar, k = 0.6, 1.0
    shapes = [("flat", lambda a: 0.0, "invariant to the transform", ""),
              ("threshold", lambda a: 0.0 if a < astar else 0.9 * (1 - math.exp(-(a - astar) / 0.03)),
               "no response below α*,", "then a sharp rise"),
              ("linear", lambda a: k * a, "degrades in proportion,", "no hidden tipping point")]
    assert all(f(0.0) == 0.0 for _, f, _, _ in shapes)      # intensity-zero identity, Section 10.2.1
    p = reg(CH10, "10.1",
            "The three canonical shapes of the intensity-response curve of Section 10.1.2: displacement of the "
            "model's output (vertical) against the intensity of the transform, from 0 to 1 (horizontal). All "
            "three start at zero displacement, as the intensity-zero identity requires. These are schematic "
            "shapes, not measurements: the threshold is placed at 0.6 and the linear profile has slope 1.",
            "### 10.1.3 Invariance and Sensitivity as Structural Signatures")
    c = _canvas(720, 400, "Three shapes of the intensity-response curve")
    for j, (name, f, n1, n2) in enumerate(shapes):
        x0 = 70 + 220 * j
        ax = Axes(c, x0, 84, 170, 196, (0, 1), (0, 1.05), [0, 0.5, 1], [0, 0.5, 1], "intensity α",
                  "displacement δ(α)" if j == 0 else "")
        c.text(x0 + 85, 68, name + " profile", 12.5, "middle", INK, "600")
        if name == "threshold":
            c.line(ax.X(astar), ax.y0 + 16, ax.X(astar), ax.y0 + ax.h, INK3, 1.5, dash="4 4")
            c.text(ax.X(astar), ax.y0 + 11, "α*", 11, "middle", INK)
        xs = [i / 400 for i in range(401)]
        c.polyline([(ax.X(a), ax.Y(f(a))) for a in xs], SERIES[j], 2.5, title=name + " profile")
        c.text(x0 + 85, 340, n1, 11, "middle", INK2)
        c.text(x0 + 85, 356, n2, 11, "middle", INK2)
    c.text(16, 390, "schematic shapes, not measurements", 10.5, "start", INK3, italic=True)
    c.save(p)


def fig_10_2():
    astar, tol = 0.37, 0.01
    flips = lambda a: a >= astar
    # the search of Section 10.2.3, with the classifier replaced by a hidden threshold
    assert flips(1.0)
    low, high = 0.0, 1.0
    steps, mids = [(low, high)], []
    while high - low > tol:
        mid = (low + high) / 2
        mids.append(mid)
        if flips(mid):
            high = mid
        else:
            low = mid
        steps.append((low, high))
    assert len(mids) == 7 and abs((high - low) - 1 / 128) < 1e-12 and low < astar <= high and high == 0.375
    sweep = [i / 9 for i in range(10)]                        # np.linspace(0, 1, 10), Section 10.2.2
    s_lo = max(a for a in sweep if not flips(a))
    s_hi = min(a for a in sweep if flips(a))
    assert abs((s_hi - s_lo) - 1 / 9) < 1e-12
    p = reg(CH10, "10.2",
            "The binary search of Section 10.2.3 beside the ten-point sweep of Section 10.2.2, for a decoder "
            "whose output flips at an intensity of 0.37, a value chosen for the figure; the horizontal axis is "
            "the intensity. The sweep (top row) spends ten evaluations and places the threshold between two "
            "points 0.111 apart. Each row below is the interval the search still holds, with a dot at the "
            "midpoint it tests next. Seven halvings after the first check at intensity 1 bring the interval to "
            "a width of 0.0078, inside the tolerance of 0.01, and the search returns its upper end, 0.375.",
            "## 10.3 StructureProbe: The Probe Response Matrix")
    c = _canvas(720, 400, "Binary search halves the interval that holds the threshold")
    X = lambda a: 150 + 480 * a
    base = 326
    c.line(X(0), base, X(1), base, GRID, 1)
    for v in (0, 0.25, 0.5, 0.75, 1):
        c.line(X(v), 68, X(v), base, GRID, 1)
        c.text(X(v), base + 16, f"{v:g}", 11, "middle", INK2)
    c.text(X(0.5), base + 34, "intensity α", 11.5, "middle", INK2)
    c.line(X(astar), 66, X(astar), base, INK, 1.5, dash="4 4")
    c.text(X(astar), 61, "flips at 0.37", 10.5, "middle", INK2)
    c.text(642, 61, "width", 10.5, "start", INK2, italic=True)
    y = 82
    c.text(140, y + 4, "10-point sweep", 11, "end", INK2)
    for a in sweep:
        c.dot(X(a), y, SERIES[1] if flips(a) else SERIES[0], 4, title=f"sweep at {a:.3f}")
    c.text(642, y + 4, f"{s_hi - s_lo:.3f}", 10.5, "start", INK)
    for i, (lo, hi) in enumerate(steps):
        y = 116 + 27 * i
        c.text(140, y + 4, "start" if i == 0 else f"step {i}", 11, "end", INK2)
        c.add(f'<rect x="{X(lo):.2f}" y="{y - 4:.2f}" width="{max(X(hi) - X(lo), 2):.2f}" height="8" rx="2" '
              f'fill="{SERIES[2]}"><title>interval {lo:g} to {hi:g}</title></rect>')
        if i < len(mids):
            m = mids[i]
            c.dot(X(m), y, SERIES[1] if flips(m) else SERIES[0], 4, title=f"test at {m:g}")
        c.text(642, y + 4, f"{hi - lo:.4f}".rstrip("0").rstrip(".") if hi - lo < 1 else "1", 10.5, "start", INK)
    legend(c, 150, 44, [("output unchanged", SERIES[0]), ("output flipped", SERIES[1]), ("interval still held", SERIES[2])])
    c.text(16, 390, "the threshold 0.37 is chosen for the figure; the search is the code of Section 10.2.3", 10.5, "start",
           INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 11
def fig_11_1():
    groups = ["Size", "Complexity", "Halstead", "OO", "Process"]
    init = "SCHOP"
    levels = {k: list(itertools.combinations(range(5), k)) for k in range(1, 6)}
    assert [len(levels[k]) for k in range(1, 6)] == [5, 10, 10, 5, 1]
    assert sum(len(v) for v in levels.values()) == 31 and sum(len(levels[k]) for k in range(1, 5)) == 30
    # one greedy path: the build order printed in Section 12.4.1
    order = [groups.index(g) for g in ("Complexity", "Process", "Size", "OO", "Halstead")]
    path = [tuple(sorted(order[:k])) for k in range(1, 6)]
    p = reg(CH11, "11.1",
            "The lattice of the 31 non-empty subsets of the five feature groups, one row per subset size k (5, "
            "10, 10, 5 and 1 subsets from bottom to top), with a line from each subset to every subset that "
            "adds one group to it. Enumeration with max_dims = 4 evaluates the 30 subsets below the dashed "
            "line. The highlighted chain is a single greedy path, which adds one group at a time and so visits "
            "5 of the 31 subsets. Its order (Complexity, Process, Size, OO, Halstead) is the illustrative build "
            "order of Section 12.4.1, not a measured result.",
            "## 11.2 The `optimize_subset` Algorithm")
    c = _canvas(720, 450, "One greedy path visits 5 of the 31 subsets; enumeration visits all")
    ypos = {5: 76, 4: 148, 3: 220, 2: 292, 1: 364}
    pos = {}
    for k, subs in levels.items():
        for i, s in enumerate(subs):
            pos[s] = (410 + (i - (len(subs) - 1) / 2) * 58, ypos[k])
    onpath = set(zip(path[:-1], path[1:]))
    for k in range(1, 5):
        for a in levels[k]:
            for b in levels[k + 1]:
                if set(a) < set(b) and (a, b) not in onpath:
                    c.line(pos[a][0], pos[a][1] - 10, pos[b][0], pos[b][1] + 10, BORDER, 1, opacity=0.75)
    for a, b in onpath:
        c.line(pos[a][0], pos[a][1] - 10, pos[b][0], pos[b][1] + 10, SERIES[0], 2.5)
    yl = (ypos[5] + ypos[4]) / 2
    c.line(112, yl, 704, yl, INK3, 1.5, dash="5 4")
    c.text(704, yl - 7, "max_dims = 4 stops here: 30 subsets", 10.5, "end", INK2, italic=True)
    for s, (x, y) in pos.items():
        on = s in path
        c.add(f'<rect x="{x - 23:.2f}" y="{y - 10:.2f}" width="46" height="20" rx="10" fill="{BOX}" '
              f'stroke="{SERIES[0] if on else BORDER}" stroke-width="{2 if on else 1}">'
              f'<title>{", ".join(groups[i] for i in s)}</title></rect>')
        c.text(x, y + 4, "".join(init[i] for i in s), 10.5, "middle", INK, "600" if on else "normal")
    for k, y in ypos.items():
        c.text(16, y, f"k = {k}", 12, "start", INK, "600")
        n = len(levels[k])
        c.text(16, y + 15, f"{n} subset" + ("" if n == 1 else "s"), 10.5, "start", INK2)
    c.text(16, 412, "S = Size, C = Complexity, H = Halstead, O = OO, P = Process", 11, "start", INK2)
    legend(c, 16, 436, [("one greedy path", SERIES[0])])
    c.text(704, 437, "path order illustrative (Section 12.4.1)", 10.5, "end", INK3, italic=True)
    c.save(p)


def fig_11_2():
    n = 20
    logg = [10 ** (-2 + 4 * i / (n - 1)) for i in range(n)]       # np.logspace(-2, 2, 20)
    unif = [0.01 + (100 - 0.01) * i / (n - 1) for i in range(n)]  # a uniform grid over the same range
    ratio = logg[1] / logg[0]
    assert abs(ratio - 1.62) < 0.005
    for got, want in zip(logg[:5] + logg[-5:], [0.01, 0.016, 0.026, 0.043, 0.070, 14.4, 23.4, 37.9, 61.6, 100.0]):
        assert abs(got - want) / want < 0.03, (got, want)
    below = lambda g: sum(1 for v in g if v < 1.0)
    assert below(logg) == 10 and below(unif) == 1
    p = reg(CH11, "11.2",
            "Twenty grid points over the search range 0.01 to 100, placed two ways and shown on one logarithmic "
            "axis. The log-spaced grid of Section 11.2.1 steps by a constant factor of 1.62 and puts 10 of its "
            "20 points below 1. A uniform grid over the same range steps by 5.26, so its second point is "
            "already at 5.27 and only its first lies below 1.",
            "### 11.2.2 Sentinel Values for Inactive Dimensions")
    c = _canvas(720, 400, "A uniform grid leaves the range below 1 almost unsampled")
    ax = Axes(c, 120, 64, 550, 250, (0.01, 100), (0, 1), [], [], "parameter value (logarithmic scale)", "", xlog=True)
    c.add(f'<rect x="{ax.X(0.01):.2f}" y="{ax.y0:.2f}" width="{ax.X(1) - ax.X(0.01):.2f}" height="{ax.h:.2f}" '
          f'fill="{BOX}" fill-opacity="0.45"/>')
    for v, lab in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")):
        c.line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, GRID, 1)
        c.text(ax.X(v), ax.y0 + ax.h + 16, lab, 11, "middle", INK2)
    c.text(ax.X(0.01) + 8, ax.y0 + 17, "values below 1", 10.5, "start", INK2, italic=True)
    c.text(ax.X(100) - 8, ax.y0 + 17, "values above 1", 10.5, "end", INK2, italic=True)
    for j, (name, grid, y) in enumerate((("log-spaced", logg, 142), ("uniform", unif, 238))):
        c.text(110, y - 2, name, 12, "end", INK, "600")
        c.text(110, y + 13, "20 points", 10.5, "end", INK2)
        c.line(ax.x0, y, ax.x0 + ax.w, y, GRID, 1)
        for v in grid:
            c.add(f'<circle cx="{ax.X(v):.2f}" cy="{y:.2f}" r="4" fill="{SERIES[j]}" fill-opacity="0.85" '
                  f'stroke="{SURFACE}" stroke-width="1"><title>{name}: {v:.3g}</title></circle>')
        nb = below(grid)
        c.text((ax.X(0.01) + ax.X(1)) / 2, y + 30, f"{nb} point{'' if nb == 1 else 's'} below 1", 11, "middle", INK)
        c.text((ax.X(1) + ax.X(100)) / 2, y + 30, f"{n - nb} points above 1", 11, "middle", INK)
    xa, xb = ax.X(logg[4]), ax.X(logg[5])
    c.line(xa, 126, xb, 126, INK2, 1.5)
    c.line(xa, 122, xa, 130, INK2, 1.5)
    c.line(xb, 122, xb, 130, INK2, 1.5)
    c.text((xa + xb) / 2, 117, f"× {ratio:.2f} each step", 10.5, "middle", INK)
    c.text(16, 390, "both grids: 20 points from 0.01 to 100", 10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 12
def fig_12_1():
    # the two-dimension case of Section 12.1.3: g is the predictive value of a set, f = constant - g
    cases = [("redundant: two copies of one signal", {(): 0, ("i",): 1, ("j",): 1, ("i", "j"): 1}, +1),
             ("complementary: two halves of an exclusive-or", {(): 0, ("i",): 0, ("j",): 0, ("i", "j"): 1}, -1)]
    p = reg(CH12, "12.1",
            "The pairwise interaction as a gap, for the two-dimension cases of Section 12.1.3. In each panel "
            "the bars are increases in error: from removing dimension i, from removing dimension j, the sum of "
            "those two (what single removals predict for removing both), and what removing both does; the "
            "interaction is the last bar minus the third. Two copies of one signal cost nothing to remove "
            "singly and 1 to remove together, an interaction of +1, so ablation calls both unimportant. Two "
            "halves of an exclusive-or cost 1 each to remove and 1 together, an interaction of −1.",
            "## 12.2 The Interaction Matrix")
    c = _canvas(720, 400, "Interaction is the gap between predicted and actual joint removal")
    for j, (name, g, want) in enumerate(cases):
        full = g[("i", "j")]
        d_i, d_j, joint = full - g[("j",)], full - g[("i",)], full - g[()]
        phi = joint - (d_i + d_j)
        assert phi == want == g[("i",)] + g[("j",)] - g[()] - g[("i", "j")]
        x0 = 70 + 335 * j
        ax = Axes(c, x0, 84, 280, 216, (0, 4), (0, 2.3), [], [0, 1, 2], "", "increase in error" if j == 0 else "")
        c.text(x0 + 140, 68, name, 12, "middle", INK, "600")
        bars = [("remove i", "", d_i, SERIES[0]), ("remove j", "", d_j, SERIES[0]),
                ("predicted", "(the sum)", d_i + d_j, SERIES[1]), ("actual", "(both out)", joint, SERIES[2])]
        for i, (l1, l2, v, col) in enumerate(bars):
            xm = ax.X(i + 0.5)
            c.rect(xm - 12, ax.Y(v), 24, ax.Y(0) - ax.Y(v), col, 4, title=f"{l1} {l2}: {v}")
            c.text(xm, ax.Y(v) - 6, f"{v:g}", 11, "middle", INK)
            c.text(xm, ax.y0 + ax.h + 16, l1, 10.5, "middle", INK2)
            if l2:
                c.text(xm, ax.y0 + ax.h + 30, l2, 10.5, "middle", INK2)
        c.text(x0 + 140, 358, f"interaction = {joint:g} − {d_i + d_j:g} = {'+' if phi > 0 else '−'}{abs(phi):g}", 12,
               "middle", INK, "600")
    legend(c, 70, 44, [("single removals", SERIES[0]), ("predicted: their sum", SERIES[1]),
                       ("actual joint removal", SERIES[2])])
    c.text(16, 390, "values of the two-dimension case in Section 12.1.3", 10.5, "start", INK3, italic=True)
    c.save(p)


def fig_12_2():
    names = ["Complexity", "+ Process", "+ Size", "+ OO", "+ Halstead"]
    mae = [3.81, 2.09, 1.72, 1.58, 1.51]
    gains = [round(mae[i] - mae[i + 1], 2) for i in range(4)]
    assert gains == [1.72, 0.37, 0.14, 0.07]
    assert all(g < 0.15 for g in gains[2:]) and gains[1] >= 0.15      # the elbow of Section 12.4.1
    p = reg(CH12, "12.2",
            "The composition path of Section 12.4.1 (illustrative values, not a recorded run): the error MAE "
            "after re-optimization (vertical) along the greedy build order, one dimension added per step "
            "(horizontal). Each segment is labelled with its marginal gain: 1.72, 0.37, 0.14 and 0.07. The "
            "descent is steep, then shallow, then nearly flat. The circled point is the elbow at three "
            "dimensions, after which each further dimension gains less than 0.15.",
            "### 12.4.2 Synergy versus Redundancy")
    c = _canvas(720, 400, "The composition path: each added dimension buys less")
    ax = Axes(c, 70, 52, 560, 268, (0.5, 5.5), (0, 4.4), [], [0, 1, 2, 3, 4], "", "MAE")
    pts = [(ax.X(i + 1), ax.Y(m)) for i, m in enumerate(mae)]
    c.polyline(pts, SERIES[0], 2, title="composition path")
    for i, g in enumerate(gains):
        mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
        if i == 0:
            c.text(mx - 9, my + 18, f"gain {g:.2f}", 11, "end", INK)
        else:
            c.text(mx, my + 22, f"gain {g:.2f}", 11, "middle", INK)
    x3, y3 = pts[2]
    c.add(f'<circle cx="{x3:.2f}" cy="{y3:.2f}" r="11" fill="none" stroke="{CRITICAL}" stroke-width="2"/>')
    for i, ((x, y), m) in enumerate(zip(pts, mae)):
        c.dot(x, y, SERIES[0], 4.5, title=f"{names[i]}: MAE {m}")
        c.text(x, y - 16, f"{m:.2f}", 11, "middle", INK)
        c.text(x, ax.y0 + ax.h + 16, names[i], 11, "middle", INK2)
        c.text(x, ax.y0 + ax.h + 31, f"{i + 1} dimension" + ("" if i == 0 else "s"), 10.5, "middle", INK3)
    c.text(x3 + 16, y3 - 32, "elbow: later gains are below 0.15", 11, "start", INK)
    c.text(16, 390, "illustrative values (Section 12.4.1)", 10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 13
def _rot90(g):
    """np.rot90: a quarter turn counter-clockwise."""
    n, m = len(g), len(g[0])
    return [[g[j][m - 1 - i] for j in range(n)] for i in range(m)]


def _fliplr(g):
    return [row[::-1] for row in g]


def _all_dihedral(g):
    """The function of Section 13.3.2: four rotations, then four rotations of the flipped grid."""
    out, cur = [], g
    for _ in range(4):
        out.append(cur)
        cur = _rot90(cur)
    cur = _fliplr(g)
    for _ in range(4):
        out.append(cur)
        cur = _rot90(cur)
    return out


def fig_13_1():
    labels = ["e", "r", "r²", "r³", "s", "sr", "sr²", "sr³"]
    grids = [("no symmetry", [[1, 1, 0, 0], [1, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0]], 1),
             ("one mirror axis", [[0, 1, 1, 0], [1, 0, 0, 1], [0, 2, 2, 0], [0, 0, 0, 0]], 2),
             ("four-fold rotation", [[0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 0, 1, 0]], 4),
             ("full symmetry", [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]], 8)]
    p = reg(CH13, "13.1",
            "The orbit-stabilizer count on four example 4 by 4 grids, each shown under the eight transforms "
            "that all_dihedral returns, in its order; a transform that reproduces a grid already shown in the "
            "row is dimmed. A grid with no symmetry gives eight distinct grids, one with a single mirror axis "
            "four, one unchanged by quarter turns two, and a fully symmetric one a single grid. In every row "
            "the number of distinct grids times the number of transforms that leave the grid unchanged is 8. "
            "The dimmed copies are the duplicate augmentations of Section 13.6.1.",
            "### 13.6.2 Burnside's Lemma and Counting Distinct Patterns")
    c = _canvas(720, 410, "Symmetric grids have small orbits: orbit × stabilizer = 8")
    cell, colx = 10, lambda j: 152 + 58 * j
    fills = {0: BOX, 1: SERIES[0], 2: SERIES[1]}
    for j, lab in enumerate(labels):
        c.text(colx(j) + 2 * cell, 62, lab, 11.5, "middle", INK2)
    for r, (name, g, stab_want) in enumerate(grids):
        imgs = _all_dihedral(g)
        stab = [lab for lab, t in zip(labels, imgs) if t == g]
        seen = []
        y0 = 74 + 80 * r
        for j, t in enumerate(imgs):
            dup = t in seen
            if not dup:
                seen.append(t)
            op = 0.22 if dup else 1.0
            for i in range(4):
                for k in range(4):
                    c.add(f'<rect x="{colx(j) + k * cell:.2f}" y="{y0 + i * cell:.2f}" width="{cell}" height="{cell}" '
                          f'fill="{fills[t[i][k]]}" fill-opacity="{op}" stroke="{SURFACE}" stroke-width="1"/>')
        assert len(stab) == stab_want and len(seen) * len(stab) == 8, (name, stab, len(seen))
        if stab_want == 4:
            assert stab == ["e", "r", "r²", "r³"]
        c.text(16, y0 + 18, name, 11.5, "start", INK, "600")
        c.text(16, y0 + 34, f"unchanged by {len(stab)} of 8", 10.5, "start", INK2)
        c.text(622, y0 + 18, f"orbit {len(seen)}", 11.5, "start", INK, "600")
        c.text(622, y0 + 34, f"{len(seen)} × {len(stab)} = 8", 10.5, "start", INK2)
    c.text(16, 398, "dimmed: a repeat of a grid already shown in its row", 10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 14
def fig_14_1():
    p = reg(CH14, "14.1",
            "The domain-adversarial network of Section 14.2.1 with both passes drawn (a schematic of the "
            "structure, not a result). Solid arrows are the forward pass: the encoder's output z goes to the "
            "task head directly and to the domain head through the gradient reversal layer (GRL), which passes "
            "it unchanged. Dashed arrows are the backward pass: the task-loss gradient returns to the encoder "
            "as it is, and the domain-loss gradient is multiplied by −λ at the GRL before it reaches the "
            "encoder. The domain head therefore learns to predict the nuisance variable s while the encoder is "
            "pushed to make that prediction harder.",
            "### 14.2.2 The Combined Loss")
    c = _canvas(720, 400, "Gradient reversal: identity going forward, sign flip going back")
    c.box(20, 170, 76, 56, "input x")
    c.box(134, 170, 130, 56, "encoder", "z = f(x; θ)")
    c.box(486, 80, 184, 56, "task head", "g(z; φ) predicts the label y")
    c.box(352, 270, 86, 56, "GRL")
    c.box(486, 270, 184, 56, "domain head", "h(z; ψ) predicts the nuisance s")
    # forward pass
    c.arrow(96, 198, 132, 198, INK2, 1.5)
    c.line(264, 198, 312, 198, INK2, 1.5)
    c.line(312, 116, 312, 290, INK2, 1.5)
    c.arrow(312, 116, 484, 116, INK2, 1.5)
    c.arrow(312, 290, 350, 290, INK2, 1.5)
    c.arrow(438, 290, 484, 290, INK2, 1.5)
    c.text(284, 216, "z", 12.5, "middle", INK, "600", italic=True)
    # backward pass
    _darrow(c, [(486, 98), (296, 98), (296, 184), (266, 184)], SERIES[0])
    _darrow(c, [(486, 312), (440, 312)], SERIES[1])
    _darrow(c, [(352, 312), (199, 312), (199, 228)], CRITICAL)
    c.text(391, 90, "gradient of the task loss", 10.5, "middle", INK2)
    c.text(276, 330, "multiplied by −λ", 10.5, "middle", INK)
    x0 = 352
    c.text(x0, 176, "forward: GRL(z) = z", 11, "start", INK2)
    c.text(x0, 194, "backward: the gradient is multiplied by −λ", 11, "start", INK2)
    c.text(x0, 212, "the encoder receives the task gradient", 11, "start", INK2)
    c.text(x0, 230, "minus λ times the domain gradient", 11, "start", INK2)
    c.text(578, 72, "task loss", 10.5, "middle", INK3, italic=True)
    c.text(578, 344, "domain loss", 10.5, "middle", INK3, italic=True)
    legend(c, 16, 386, [("forward pass", INK2), ("task-loss gradient", SERIES[0]), ("domain-loss gradient", SERIES[1]),
                        ("reversed gradient", CRITICAL)])
    c.save(p)


def fig_14_2():
    # Section 14.9.2, means over three seeds, per cent
    settings = ["no reversal", "λ max = 0.5", "λ max = 1"]
    domain = [95.9, 84.8, 37.7]
    probe = [99.9, 100.0, 99.9]
    shifted = [17.6, 16.7, 17.1]
    probe_fall = round(probe[0] - probe[2], 1)
    shifted_rise = round(shifted[2] - shifted[0], 1)
    assert probe_fall == 0.0 and shifted_rise == -0.5
    assert not (probe_fall >= 15 and shifted_rise >= 5)          # P3 as registered: it fails
    assert round(domain[0] - domain[2], 1) == 58.2
    p = reg(CH14, "14.2",
            "The recorded run of Section 14.9 on the shortcut data, means over three seeds, accuracy in per "
            "cent: the domain head during training, a probe fitted afterwards to recover the recording "
            "condition from the frozen latent vectors, and the task on the shifted test set. Full reversal "
            "brings the domain head from 95.9% down to 37.7%, but the probe still recovers the condition 99.9% "
            "of the time and shifted accuracy stays at chance. Prediction P3, registered before the run, "
            "required the probe to fall by at least 15 points and shifted accuracy to rise by at least 5; the "
            "probe fell by 0.0 and shifted accuracy changed by −0.5, so P3 failed. The setting 0.5 was run "
            "without a prediction.",
            "### 14.9.3 What the Experiment Shows")
    c = _canvas(720, 400, "The domain head is fooled; a probe fitted afterwards is not")
    ax = Axes(c, 70, 60, 450, 266, (0, 3), (0, 110), [], [0, 20, 40, 60, 80, 100], "", "accuracy, per cent")
    series = [("domain head (training)", domain), ("probe (after training)", probe), ("shifted test (task)", shifted)]
    for i, name in enumerate(settings):
        xm = ax.X(i + 0.5)
        for j, (sname, vals) in enumerate(series):
            v = vals[i]
            x = xm - 38 + 26 * j
            c.rect(x, ax.Y(v), 24, ax.Y(0) - ax.Y(v), SERIES[j], 4, title=f"{name}, {sname}: {v:.1f}%")
            c.text(x + 12, min(ax.Y(v) - 5, ax.Y(20) - 6) if j == 2 else ax.Y(v) - 5, f"{v:.1f}", 10, "middle", INK)
        c.text(xm, ax.y0 + ax.h + 16, name, 11, "middle", INK2)
    c.text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 34, "shortcut data: strength of the reversal", 11.5, "middle", INK2)
    for v, lab, dy in ((20.0, "chance, condition: 20%", -5), (16.7, "chance, coda type: 16.7%", 13)):
        c.line(ax.x0, ax.Y(v), ax.x0 + ax.w, ax.Y(v), INK3, 1.2, dash="4 4")
        c.text(ax.x0 + ax.w + 8, ax.Y(v) + dy, lab, 10.5, "start", INK2, italic=True)
    legend(c, 70, 44, [(nm, SERIES[j]) for j, (nm, _) in enumerate(series)])
    x0 = 534
    c.text(x0, 92, "Prediction P3: FAILED", 12, "start", INK, "600")
    c.add(f'<rect x="{x0 - 8}" y="76" width="3" height="118" fill="{CRITICAL}"/>')
    c.text(x0, 114, "needed: probe falls by", 10.5, "start", INK2)
    c.text(x0, 129, "at least 15 points", 10.5, "start", INK2)
    c.text(x0, 144, f"got: {probe_fall:.1f}", 10.5, "start", INK, "600")
    c.text(x0, 164, "needed: shifted test", 10.5, "start", INK2)
    c.text(x0, 179, "rises by at least 5", 10.5, "start", INK2)
    c.text(x0, 194, f"got: −{abs(shifted_rise):.1f}", 10.5, "start", INK, "600")
    c.text(16, 390, "recorded run, 16 November 2026 (ch14_shortcut.json); no model learned the rhythm", 10.5, "start", INK3,
           italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 15
def fig_15_1():
    n = 9
    full, sym = n * n, n * (n + 1) // 2
    off = n * (n - 1) // 2
    assert (full, sym, off, off + n) == (81, 45, 36, 45)
    panels = [("every entry of the matrix", f"{full} numbers", lambda i, j: "entry",
               ["a gradient step can break", "symmetry and positive definiteness"]),
              ("Cholesky factor L", f"{sym} numbers", lambda i, j: "diag" if i == j else ("free" if i > j else "zero"),
               [f"{off} below the diagonal, {n} on it;", "L times its transpose is always SPD"]),
              ("diagonal only", f"{n} numbers", lambda i, j: "diag" if i == j else "zero",
               ["one precision per dimension,", "no cross terms (Section 15.8)"])]
    fills = {"entry": SERIES[2], "free": SERIES[0], "diag": SERIES[1], "zero": BOX}
    p = reg(CH15, "15.1",
            "Three ways to hold a 9 by 9 covariance or precision matrix as numbers to optimize. Left: all 81 "
            "entries, which no constraint keeps symmetric or positive definite. Middle: the log-diagonal "
            "Cholesky factor, 36 unconstrained entries below the diagonal and 9 diagonal entries stored as "
            "logarithms, 45 in all, the number of degrees of freedom of a symmetric matrix; any real values "
            "give a symmetric positive definite product. Right: the diagonal-only simplification of Section "
            "15.8, 9 numbers.",
            "### 15.3.2 Why Log-Space for the Diagonal")
    c = _canvas(720, 400, "A triangle of free numbers: 45 parameters for a 9 by 9 matrix")
    cell = 18
    for k, (name, count, kind, notes) in enumerate(panels):
        x0, y0 = 60 + 219 * k, 92
        cx = x0 + n * cell / 2
        c.text(cx, 62, name, 12, "middle", INK, "600")
        c.text(cx, 79, count, 11, "middle", INK2)
        tally = {}
        for i in range(n):
            for j in range(n):
                t = kind(i, j)
                tally[t] = tally.get(t, 0) + 1
                c.add(f'<rect x="{x0 + j * cell}" y="{y0 + i * cell}" width="{cell}" height="{cell}" fill="{fills[t]}" '
                      f'stroke="{SURFACE}" stroke-width="1.5"><title>row {i + 1}, column {j + 1}: {t}</title></rect>')
        assert sum(v for t, v in tally.items() if t != "zero") == (full, sym, n)[k]
        for q, s in enumerate(notes):
            c.text(cx, y0 + n * cell + 20 + 15 * q, s, 10.5, "middle", INK2)
    legend(c, 60, 340, [("entry of the matrix, unconstrained", SERIES[2]), ("free entry of L, any real number", SERIES[0])])
    legend(c, 60, 362, [("diagonal of L, exp(θ) for any real θ", SERIES[1]), ("fixed at zero", BOX)])
    c.save(p)


def fig_15_2():
    thetas = [-1.0, -0.5, 0.0, 0.25, 0.5]
    ells = [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
    # 2 by 2, theta_1 = 0: L = [[1, 0], [l, exp(theta)]], so M = L L^T = [[1, l], [l, l^2 + exp(2 theta)]]
    cmap = lambda l, th: l * l + math.exp(2 * th)
    for th in thetas:
        for l in ells:
            b, cc = l, cmap(l, th)
            assert abs((cc - b * b) - math.exp(2 * th)) < 1e-12 and cc - b * b > 0     # det M > 0
    p = reg(CH15, "15.2",
            "The parameterization map of Section 15.3.3 for a 2 by 2 matrix with its top-left entry fixed at 1, "
            "plotted by the off-diagonal entry b (horizontal) and the lower-right entry c (vertical); the "
            "matrix is positive definite exactly when c is greater than b squared, the region above the "
            "parabola. The map sends the free off-diagonal parameter ℓ and the log-diagonal parameter θ to b = "
            "ℓ and c = ℓ squared plus exp(2θ). The curves are the images of the lines θ = −1, −0.5, 0, 0.25 and "
            "0.5 and of the lines ℓ = −1.5 to 1.5 in steps of 0.5. Every one lies above the parabola, which is "
            "reached only as θ goes to minus infinity, so a step of any size in the parameters stays inside the "
            "cone.",
            "## 15.4 Implementation: NumPy")
    c = _canvas(720, 400, "Every parameter value lands inside the cone")
    ax = Axes(c, 80, 56, 430, 276, (-2, 2), (0, 6), [-2, -1, 0, 1, 2], [0, 1, 2, 3, 4, 5, 6],
              "off-diagonal entry b", "lower-right entry c")
    bs = [-2 + 4 * i / 200 for i in range(201)]
    for l in ells:
        c.line(ax.X(l), ax.Y(l * l + 0.03), ax.X(l), ax.Y(6), SERIES[1], 1.3, opacity=0.9)
    for th in thetas:
        pts = [(ax.X(b), ax.Y(cmap(b, th))) for b in bs if cmap(b, th) <= 6]
        c.polyline(pts, SERIES[0], 2, title=f"θ = {th:g}")
    c.polyline([(ax.X(b), ax.Y(b * b)) for b in bs], INK, 2, title="boundary: c = b squared")
    c.text(ax.X(1.42), ax.Y(0.22), "not positive definite", 10.5, "middle", INK2, italic=True)
    c.text(ax.X(-1.42), ax.Y(0.22), "not positive definite", 10.5, "middle", INK2, italic=True)
    legend(c, 80, 44, [("θ fixed", SERIES[0]), ("ℓ fixed", SERIES[1]), ("boundary of the cone, c = b²", INK)])
    x0 = 532
    for k, s in enumerate(["matrix: rows (1, b) and (b, c)", "b = ℓ", "c = ℓ² + exp(2θ)", "so c − b² = exp(2θ) > 0", "",
                           "curves, bottom to top:", "θ = −1, −0.5, 0, 0.25, 0.5", "", "vertical lines:",
                           "ℓ = −1.5 to 1.5, step 0.5"]):
        c.text(x0, 104 + 17 * k, s, 11, "start", INK2)
    c.text(16, 390, "2 by 2 case with the first diagonal parameter set to 0", 10.5, "start", INK3, italic=True)
    c.save(p)
