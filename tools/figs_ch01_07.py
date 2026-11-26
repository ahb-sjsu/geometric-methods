"""Figures for Chapters 1 to 7 of Geometric Methods.

Every figure is drawn from a formula, a definition or printed code of its chapter. Where a
figure repeats a number printed in the text, the function asserts that the value computed
here agrees. Section 21.8 classes the covariance, penalties, displacement coefficients and
scaling functions of Chapters 6 and 7, and the tables of Chapter 1, as posited; the captions
of the figures that use them say so.
"""

import math

from figkit import BOX, CRITICAL, GRID, INK, INK2, INK3, SERIES, SURFACE, Axes, Canvas, legend, reg

CH1 = "chapters/chapter-01-why-geometry.md"
CH2 = "chapters/chapter-02-mahalanobis-distance.md"
CH3 = "chapters/chapter-03-hyperbolic-geometry.md"
CH4 = "chapters/chapter-04-spd-manifolds.md"
CH5 = "chapters/chapter-05-topological-data-analysis.md"
CH6 = "chapters/chapter-06-pathfinding-on-manifolds.md"
CH7 = "chapters/chapter-07-equilibrium-on-manifolds.md"

# The nine dimensions, in the order of the Dim enumeration of Section 6.3.2.
CONS, RIGHTS, FAIR, AUTO, TRUST, SOCIAL, IDENT, LEGIT, EPIST = range(9)


# ------------------------------------------------------------------ small linear algebra
def _inv(m):
    """Inverse of a small square matrix by Gauss-Jordan elimination with pivoting."""
    n = len(m)
    a = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(a[r][col]))
        a[col], a[piv] = a[piv], a[col]
        p = a[col][col]
        a[col] = [v / p for v in a[col]]
        for r in range(n):
            if r != col and a[r][col] != 0.0:
                f = a[r][col]
                a[r] = [v - f * w for v, w in zip(a[r], a[col])]
    return [row[n:] for row in a]


def _mahal(delta, p):
    """sqrt(delta^T P delta)."""
    return math.sqrt(sum(delta[i] * p[i][j] * delta[j] for i in range(len(delta)) for j in range(len(delta))))


def _default_sigma():
    """The package default covariance, as printed in Section 6.6.1 (_default_sigma)."""
    s = [[0.0] * 9 for _ in range(9)]
    s[CONS][CONS] = 25.0
    for d in range(1, 9):
        s[d][d] = 0.25
    for i, j, v in ((CONS, FAIR, 0.5), (RIGHTS, LEGIT, 0.15), (IDENT, SOCIAL, 0.1), (TRUST, EPIST, 0.1)):
        s[i][j] = s[j][i] = v
    return s


def _poly(c, pts, fill, opacity):
    d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    c.add(f'<polygon points="{d}" fill="{fill}" fill-opacity="{opacity}"/>')


def _band(c, x, y, w, h, fill=BOX, opacity=1.0):
    c.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" fill-opacity="{opacity}"/>')


def _ring(c, x, y, r, stroke):
    """Open marker: a point that is named but does not belong to the set drawn."""
    c.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{SURFACE}" stroke="{stroke}" stroke-width="1.5"/>')


# ------------------------------------------------------------------ chapter 1
def fig_1_1():
    p = reg(CH1, "1.1",
            "Growth of a tree against growth of Euclidean volume, on a logarithmic vertical axis; the "
            "horizontal axis is the depth d or the radius r. A tree with branching factor 2 has 2 to the "
            "power d nodes at depth d. A ball of radius r in dimension k has volume proportional to r to the "
            "power k, drawn for k = 2 and k = 3 with the constant set to 1. The tree's count passes both "
            "polynomial curves and keeps pulling away, which is why a faithful Euclidean embedding needs "
            "more dimensions as the tree deepens.",
            "### 1.3.2 Covariance and Spectral Data on SPD Manifolds")
    c = Canvas(720, 400, "A tree outgrows the volume of any fixed Euclidean dimension")
    ax = Axes(c, 70, 56, 540, 276, (0, 20), (1, 1e7), [0, 5, 10, 15, 20], [], "depth d of the tree, or radius r of the ball",
              "count or volume (logarithmic scale)", ylog=True)
    for v, lab in ((1, "1"), (100, "100"), (1e4, "10⁴"), (1e6, "10⁶")):
        c.line(ax.x0, ax.Y(v), ax.x0 + ax.w, ax.Y(v), GRID, 1)
        c.text(ax.x0 - 8, ax.Y(v) + 4, lab, 11, "end", INK2)
    xs = [1 + 19 * i / 95 for i in range(96)]
    curves = [("2^d", [(d, 2.0 ** d) for d in [20 * i / 100 for i in range(101)]]),
              ("r³", [(r, r ** 3) for r in xs]),
              ("r²", [(r, r ** 2) for r in xs])]
    for j, (name, pts) in enumerate(curves):
        c.polyline([(ax.X(x), ax.Y(y)) for x, y in pts], SERIES[j], 2, title=name)
        c.text(ax.X(pts[-1][0]) + 8, ax.Y(pts[-1][1]) + 4, name, 11.5, "start", INK2)
    assert 2 ** 10 > 10 ** 3 and 2 ** 9 < 9 ** 3  # the tree passes the cube between depth 9 and 10
    legend(c, 70, 42, [("nodes at depth d, branching factor 2", SERIES[0]), ("volume, k = 3", SERIES[1]),
                       ("volume, k = 2", SERIES[2])])
    c.save(p)


def fig_1_2():
    front = [(1, 3.8, "{Complexity}"), (2, 2.1, "{Complexity, Process}"), (3, 1.7, "{Complexity, Process, Size}"),
             (5, 1.5, "all five groups")]
    dominated = (2, 2.3, "{Size, Halstead}")
    assert abs((front[2][1] - front[3][1]) - 0.2) < 1e-12  # "from 1.7 to 1.5"
    p = reg(CH1, "1.2",
            "The Pareto frontier of the motivating example, drawn from the invented values of Section 1.5.2: "
            "number of feature groups used on the horizontal axis, mean absolute error on the vertical axis. "
            "The four joined points are the non-dominated configurations of the table, and {Size, Halstead}, "
            "at 2.3, is dominated by {Complexity, Process} at the same size. Most of the gain comes with the "
            "second group; going from three groups to five lowers the error only from 1.7 to 1.5. These "
            "numbers are illustrations, not measurements (the measured campaign is in Chapter 19).",
            "### 1.5.3 What Geometry Revealed")
    c = Canvas(720, 400, "Error against groups used: the frontier flattens after two")
    ax = Axes(c, 70, 52, 540, 280, (0.5, 5.5), (0, 4.5), [1, 2, 3, 4, 5], [0, 1, 2, 3, 4],
              "number of feature groups used, k", "mean absolute error")
    c.polyline([(ax.X(k), ax.Y(m)) for k, m, _ in front], SERIES[0], 2, title="Pareto frontier")
    k, m, name = dominated
    c.dot(ax.X(k), ax.Y(m), SERIES[1], 4.5, title=f"{name}, MAE {m}")
    c.text(ax.X(k) + 11, ax.Y(m) - 7, f"{name} {m}, dominated", 11, "start", INK)
    place = [("start", 11, 4), ("end", -9, 18), ("start", 8, -10), ("middle", 0, 22)]
    for (k, m, name), (anchor, dx, dy) in zip(front, place):
        c.dot(ax.X(k), ax.Y(m), SERIES[0], 4.5, title=f"{name}, MAE {m}")
        c.text(ax.X(k) + dx, ax.Y(m) + dy, f"{name} {m}", 11, anchor, INK)
    legend(c, 70, 40, [("non-dominated", SERIES[0]), ("dominated", SERIES[1])])
    c.text(16, 390, "invented values (Section 1.5), not measurements", 10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 2
def fig_2_1():
    names = ["Consequences", "Rights", "Fairness", "Autonomy", "Trust", "Social Impact", "Virtue/Identity",
             "Legitimacy", "Epistemic"]
    var = [25.0, 4.0, 0.25, 1.0, 4.0, 9.0, 2.0, 1.0, 0.5]
    sigma = [[var[i] if i == j else 0.0 for j in range(9)] for i in range(9)]
    for i, j, v in ((0, 2, 0.5), (1, 4, 0.3), (0, 5, 2.0), (2, 6, 0.2)):
        sigma[i][j] = sigma[j][i] = v
    prec = _inv(sigma)
    diag = [prec[i][i] for i in range(9)]
    # the text: "(Sigma^-1)_00 is about 1/25 = 0.04" and "(Sigma^-1)_22 is about 4.0", before the couplings
    assert abs(diag[0] - 0.04) < 0.005 and abs(diag[2] - 4.0) < 0.6
    assert all(d >= 1.0 / v - 1e-12 for d, v in zip(diag, var))
    p = reg(CH2, "2.1",
            "Variance and precision for the nine dimensions of the illustrative covariance matrix of Section "
            "2.2, on a logarithmic axis. The variance is the diagonal entry of the matrix and the precision "
            "is the diagonal entry of its inverse, computed from the printed code with its couplings. "
            "Inversion mirrors each dimension about 1: Consequences has the widest variance, 25, and the "
            "lowest precision, "
            f"{diag[0]:.3f}, and Fairness has the narrowest variance, 0.25, and the highest precision, "
            f"{diag[2]:.2f}. "
            "The matrix is an illustration and is not the package default.",
            "## 2.3 The Inverse Covariance as an Attention Mechanism")
    c = Canvas(720, 400, "Inversion mirrors the scale: wide variance, low attention")
    x0, w, y0, rh = 160, 360, 62, 30
    lo, hi = 0.01, 100.0

    def X(v):
        return x0 + w * (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))

    for v, lab in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")):
        c.line(X(v), y0, X(v), y0 + 9 * rh, GRID, 1)
        c.text(X(v), y0 + 9 * rh + 16, lab, 11, "middle", INK2)
    c.line(X(1), y0, X(1), y0 + 9 * rh, INK3, 1.5, dash="4 4")
    c.text(x0 + w / 2, y0 + 9 * rh + 34, "value (logarithmic scale)", 11.5, "middle", INK2)
    c.text(600, y0 - 6, "variance", 11, "end", INK2)
    c.text(690, y0 - 6, "precision", 11, "end", INK2)
    for i, name in enumerate(names):
        y = y0 + rh * (i + 0.5)
        c.text(x0 - 10, y + 4, name, 11.5, "end", INK2)
        c.line(X(var[i]), y, X(diag[i]), y, INK3, 2)
        c.dot(X(var[i]), y, SERIES[0], 5, title=f"{name}: variance {var[i]:g}")
        if abs(X(var[i]) - X(diag[i])) < 6:      # both at 1: draw the second inside the first
            c.add(f'<circle cx="{X(diag[i]):.2f}" cy="{y:.2f}" r="2.6" fill="{SERIES[1]}">'
                  f'<title>{name}: precision {diag[i]:.3f}</title></circle>')
        else:
            c.dot(X(diag[i]), y, SERIES[1], 5, title=f"{name}: precision {diag[i]:.3f}")
        c.text(600, y + 4, f"{var[i]:g}", 11, "end", INK)
        c.text(690, y + 4, f"{diag[i]:.3f}", 11, "end", INK)
    legend(c, 160, 42, [("variance (diagonal of Σ)", SERIES[0]), ("precision (diagonal of the inverse)", SERIES[1])])
    c.text(16, 390, "illustrative matrix of Section 2.2, not the package default", 10.5, "start", INK3, italic=True)
    c.save(p)


def fig_2_2():
    n, a, b = 20, 0.01, 100.0
    logg = [10 ** (math.log10(a) + k * (math.log10(b) - math.log10(a)) / (n - 1)) for k in range(n)]
    uni = [a + k * (b - a) / (n - 1) for k in range(n)]
    for got, want in zip(logg[:4], (0.01, 0.016, 0.026, 0.043)):
        assert abs(got - want) < 0.0006
    for got, want in zip(logg[-4:], (23.4, 37.9, 61.6, 100.0)):
        assert abs(got - want) < 0.06
    assert abs(logg[1] / logg[0] - 1.62) < 0.005
    below_log = sum(1 for v in logg if v <= 1.0)
    below_uni = sum(1 for v in uni if v <= 1.0)
    assert (below_uni, below_log) == (1, 10)
    p = reg(CH2, "2.2",
            "Two grids of 20 points on the range 0.01 to 100, drawn on a logarithmic axis. The uniform grid has equal "
            f"differences between neighbours and places {below_uni} of its 20 points at or below 1. The log-spaced grid "
            f"of Section 2.4 has equal ratios, each value 1.62 times the one before, and places {below_log} of its 20 "
            "points below 1. The shaded band is the part of the range from 0.01 to 1, two of the four decades.",
            "## 2.5 Cholesky Factorization for Positive-Definiteness")
    c = Canvas(720, 400, "A uniform grid spends its points at the top of the range")
    x0, w = 130, 520

    def X(v):
        return x0 + w * (math.log10(v) + 2) / 4

    top, bot = 80, 300
    _band(c, X(0.01), top, X(1) - X(0.01), bot - top)
    for v, lab in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")):
        c.line(X(v), top, X(v), bot, GRID, 1)
        c.text(X(v), bot + 16, lab, 11, "middle", INK2)
    c.line(x0, bot, x0 + w, bot, GRID, 1)
    c.text(x0 + w / 2, bot + 36, "parameter value (logarithmic scale)", 11.5, "middle", INK2)
    rows = [("uniform grid", uni, SERIES[1], 140, f"{below_uni} of 20 points at or below 1"),
            ("log-spaced grid", logg, SERIES[0], 240, f"{below_log} of 20 points below 1")]
    for name, vals, col, y, note in rows:
        c.text(x0 - 12, y + 4, name, 11.5, "end", INK)
        c.line(x0, y, x0 + w, y, INK3, 1)
        for v in vals:
            c.add(f'<line x1="{X(v):.2f}" y1="{y - 11:.2f}" x2="{X(v):.2f}" y2="{y + 11:.2f}" stroke="{col}" '
                  f'stroke-width="2.5" stroke-linecap="round"><title>{name}: {v:.3g}</title></line>')
        c.text(X(0.01) + 10, y - 22, note, 11, "start", INK)
    c.text(X(100), 240 + 30, "each value 1.62 × the one before", 11, "end", INK2, italic=True)
    c.text(X(100), 140 + 30, "equal differences of 5.26", 11, "end", INK2, italic=True)
    assert abs((uni[1] - uni[0]) - 5.26) < 0.005
    c.save(p)


# ------------------------------------------------------------------ chapter 3
def fig_3_1():
    def lam(r):
        return 2.0 / (1.0 - r * r)

    def dist(r):
        return 2.0 * math.atanh(r)

    assert abs(lam(0.95) - 20.51) < 0.005                   # Section 3.2.5
    assert abs(lam(0.99) - 100) < 1 and abs(lam(0.999) - 1000) < 1   # Section 3.7
    p = reg(CH3, "3.1",
            "Geodesic distance from the origin on the Poincaré ball with c = 1, the depth score of Section "
            "3.5.2, against the Euclidean norm of the point. The curve is 2 artanh of the norm; near the "
            "origin it follows the dashed line, twice the norm, and toward the rim it diverges. The marked "
            "points carry the conformal factors quoted in the chapter: 20.51 at the projection radius 0.95, "
            "about 100 at 0.99 and about 1000 at 0.999. Equal steps in depth take ever smaller Euclidean "
            "steps near the rim, which gives room for deep, specific nodes and is also where float precision "
            "runs out.",
            "## 3.6 Einstein Midpoint for Aggregation")
    c = Canvas(720, 400, "Depth on the ball: distance from the origin diverges at the rim")
    ax = Axes(c, 70, 52, 540, 280, (0, 1), (0, 8), [0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 2, 4, 6, 8],
              "Euclidean norm of the point, ‖h‖", "geodesic distance from the origin")
    c.line(ax.X(0), ax.Y(0), ax.X(1), ax.Y(2), INK3, 1.5, dash="5 5")
    c.text(ax.X(0.62), ax.Y(1.24) + 20, "2‖h‖: the conformal factor at the origin is 2", 11, "start", INK2, italic=True)
    rmax = math.tanh(4.0)
    rs = [rmax * (1 - (1 - i / 400) ** 3) for i in range(401)]
    c.polyline([(ax.X(r), ax.Y(dist(r))) for r in rs], SERIES[0], 2, title="2 artanh(‖h‖)")
    marks = [(0.9, "‖h‖ = 0.9: distance {d:.2f}"), (0.95, "0.95, projection radius: {d:.2f}, λ = 20.51"),
             (0.99, "0.99: {d:.2f}, λ ≈ 100"), (0.999, "0.999: {d:.2f}, λ ≈ 1000")]
    for r, lab in marks:
        c.dot(ax.X(r), ax.Y(dist(r)), SERIES[0], 4.5, title=f"norm {r}, distance {dist(r):.3f}, conformal factor {lam(r):.2f}")
        c.text(ax.X(r) - 11, ax.Y(dist(r)) + 4, lab.format(d=dist(r)), 11, "end", INK)
    c.save(p)


def fig_3_2():
    x1, x2 = 0.9, 0.0
    lam1, lam2 = 2 / (1 - x1 * x1), 2 / (1 - x2 * x2)
    klein = (lam1 * x1 + lam2 * x2) / ((lam1 - 1) + (lam2 - 1))
    ein = math.tanh(0.5 * math.atanh(klein))
    w1, w2 = 1 / (1 - x1 * x1), 1 / (1 - x2 * x2)
    short = (w1 * x1 + w2 * x2) / (w1 + w2)
    eucl = (x1 + x2) / 2
    assert abs(ein - 0.627) < 0.0005 and abs(short - 0.756) < 0.0005     # Section 3.6.1
    assert abs(ein - math.tanh(0.5 * math.atanh(0.9))) < 1e-12

    def hd(r):
        return 2 * math.atanh(r)

    total = hd(x1)
    assert abs(hd(ein) - total / 2) < 1e-12
    p = reg(CH3, "3.2",
            "The two-point test of Section 3.6.1 in the unit ball, x1 = (0.9, 0) and x2 at the origin. The "
            "upper ruler is the position on the radius in Euclidean coordinates and the lower ruler is "
            "hyperbolic distance from x2, which runs from 0 to "
            f"{total:.2f}. The Einstein midpoint, at radius 0.627, lands at half that distance, {total / 2:.2f} "
            f"from each point. "
            f"The shortcut that weights Poincaré points by 1/(1 − ‖x‖²) returns 0.756, which is "
            f"{hd(short):.2f} from x2 and {total - hd(short):.2f} from x1, and the Euclidean mean, 0.45, is "
            f"only {hd(eucl):.2f} from x2.",
            "## 3.7 Numerical Considerations and Best Practices")
    c = Canvas(720, 400, "The Einstein midpoint halves the hyperbolic distance")
    xa, xb = 80, 640
    ya, yb = 165, 305

    def XE(r):
        return xa + (xb - xa) * r

    def XH(d):
        return xa + (XE(x1) - xa) * d / total

    c.text(xa, ya - 62, "position on the radius, Euclidean coordinate", 11.5, "start", INK2)
    c.line(xa, ya, xb, ya, INK3, 1.5)
    c.line(xb, ya - 12, xb, ya + 12, INK, 2)
    c.text(xb, ya - 20, "rim, 1", 11, "middle", INK2)
    c.text(xa, yb + 50, "hyperbolic distance from x₂", 11.5, "start", INK2)
    c.line(xa, yb, XE(x1), yb, INK3, 1.5)
    cands = [(eucl, SERIES[2], "0.45", "Euclidean mean"), (ein, SERIES[0], "0.627", "Einstein midpoint"),
             (short, SERIES[1], "0.756", "shortcut")]
    for r, col, lab, name in cands:
        c.line(XE(r), ya, XH(hd(r)), yb, col, 1.5, dash="4 4")
    for r, lab in ((x2, "x₂ = 0"), (x1, "x₁ = 0.9")):
        c.line(XE(r), ya, XH(hd(r)), yb, GRID, 1.5)
        c.dot(XE(r), ya, INK, 4.5, title=lab)
        c.text(XE(r), ya - 20, lab, 11.5, "middle", INK)
        c.dot(XH(hd(r)), yb, INK, 4.5, title=f"{lab}: distance {hd(r):.3f} from x2")
        c.text(XH(hd(r)), yb + 24, f"{hd(r):.2f}" if r else "0", 11, "middle", INK)
    for r, col, lab, name in cands:
        c.dot(XE(r), ya, col, 5, title=f"{name}: radius {r:.3f}")
        c.text(XE(r), ya - 20, lab, 11.5, "middle", INK)
        c.dot(XH(hd(r)), yb, col, 5, title=f"{name}: {hd(r):.3f} from x2")
        c.text(XH(hd(r)), yb + 24, f"{hd(r):.2f}", 11, "middle", INK)
    c.line(XH(total / 2), yb - 16, XH(total / 2), yb + 8, INK3, 1.5)
    c.text(XH(total / 2), yb + 40, "half way", 10.5, "middle", INK2, italic=True)
    legend(c, 80, 62, [("Euclidean mean", SERIES[2]), ("Einstein midpoint", SERIES[0]),
                       ("shortcut weighting 1/(1 − ‖x‖²)", SERIES[1])])
    c.save(p)


# ------------------------------------------------------------------ chapter 4
def fig_4_1():
    e1, e2, e3 = 0.01, 100.0, 10000.0
    f12, f23 = abs(e1 - e2), abs(e2 - e3)
    l12, l23 = abs(math.log(e1) - math.log(e2)), abs(math.log(e2) - math.log(e3))
    assert abs(f12 - 99.99) < 1e-9 and abs(f23 - 9900) < 1e-9 and abs(f23 / f12 - 99) < 0.02
    assert abs(l12 - 9.2) < 0.02 and abs(l23 - 4.6) < 0.01
    p = reg(CH4, "4.1",
            "The three matrices of Section 4.2, S1 = diag(1, 0.01), S2 = diag(1, 100) and S3 = diag(1, 10000), placed "
            "by their second eigenvalue on two rulers. On the linear ruler S1 and S2 fall on the same spot and S3 is "
            "far away: the Frobenius distances are 99.99 and 9900. On the logarithmic ruler S2 sits two thirds of the "
            "way from S1 to S3: the log-Euclidean distances are 9.2 and 4.6, so the change by a factor of 10,000 is "
            "twice as long as the change by a factor of 100.",
            "## 4.3 The Frechet Mean on SPD(n)")
    c = Canvas(720, 400, "Frobenius reads differences, log-Euclidean reads ratios")
    x0, w = 90, 540
    pts = [("S₁", e1, SERIES[0]), ("S₂", e2, SERIES[1]), ("S₃", e3, SERIES[2])]

    def bracket(xl, xr, y, label):
        c.line(xl, y, xr, y, INK3, 1.5)
        c.line(xl, y - 4, xl, y + 4, INK3, 1.5)
        c.line(xr, y - 4, xr, y + 4, INK3, 1.5)
        c.text((xl + xr) / 2, y - 7, label, 11, "middle", INK)

    # linear ruler
    y = 150
    c.text(x0, y - 62, "linear scale: what the Frobenius distance measures", 11.5, "start", INK2)
    c.line(x0, y, x0 + w, y, INK3, 1.5)
    for v in (0, 2500, 5000, 7500, 10000):
        xv = x0 + w * v / 10000
        c.line(xv, y, xv, y + 5, INK3, 1)
        c.text(xv, y + 20, str(v), 11, "middle", INK2)
    XL = lambda v: x0 + w * v / 10000  # noqa: E731
    bracket(XL(e2) + 10, XL(e3), y - 26, "S₂ to S₃: 9900")
    for name, v, col in pts:
        c.dot(XL(v), y, col, 5, title=f"{name}: second eigenvalue {v:g}")
    c.text(XL(e2) + 2, y + 38, "S₁ and S₂, 99.99 apart", 11, "start", INK)
    c.text(XL(e3), y + 38, "S₃", 11, "middle", INK)
    # logarithmic ruler
    y = 300
    c.text(x0, y - 62, "logarithmic scale: what the log-Euclidean distance measures", 11.5, "start", INK2)
    c.line(x0, y, x0 + w, y, INK3, 1.5)
    XG = lambda v: x0 + w * (math.log10(v) + 2) / 6  # noqa: E731
    for v, lab in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100"), (1000, "1000"), (10000, "10000")):
        c.line(XG(v), y, XG(v), y + 5, INK3, 1)
        c.text(XG(v), y + 20, lab, 11, "middle", INK2)
    bracket(XG(e1), XG(e2) - 5, y - 26, "S₁ to S₂: 9.2")
    bracket(XG(e2) + 5, XG(e3), y - 26, "S₂ to S₃: 4.6")
    for name, v, col in pts:
        c.dot(XG(v), y, col, 5, title=f"{name}: second eigenvalue {v:g}")
        c.text(XG(v), y + 38, name, 11, "middle", INK)
    c.text(x0 + w / 2, y + 62, "second eigenvalue of the matrix", 11.5, "middle", INK2)
    c.save(p)


def fig_4_2():
    # Matrices [[a, b], [b, a]] have eigenvalues a + b and a - b, with eigenvectors (1, 1) and (1, -1).
    s1, s2 = (1.0, 0.5), (4.0, 0.0)           # (a, b) of Example 4.1

    def eig(ab):
        return ab[0] + ab[1], ab[0] - ab[1]

    def geo(t):
        lp = math.exp((1 - t) * math.log(eig(s1)[0]) + t * math.log(eig(s2)[0]))
        lm = math.exp((1 - t) * math.log(eig(s1)[1]) + t * math.log(eig(s2)[1]))
        return (lp + lm) / 2, (lp - lm) / 2

    am = ((s1[0] + s2[0]) / 2, (s1[1] + s2[1]) / 2)
    assert am == (2.5, 0.25) and eig(am) == (2.75, 2.25)       # Example 4.1
    lm = geo(0.5)
    le = eig(lm)
    assert abs(le[0] - math.sqrt(6)) < 1e-12 and abs(le[1] - math.sqrt(2)) < 1e-12
    p = reg(CH4, "4.2",
            "A slice of the 2 by 2 symmetric matrices: those with equal diagonal entries a and off-diagonal "
            "entry b, whose eigenvalues are a + b and a − b. The positive definite ones fill the open wedge "
            "a > |b|; the zero matrix at the tip and the negative of S1 lie outside, which is why the set is "
            "not a vector space. S1 and S2 are the matrices of Example 4.1, and the straight chord carries "
            "their arithmetic mean, with eigenvalues 2.75 and 2.25. The curve is the log-Euclidean weighted "
            "mean of Section 4.3 as the weight moves from S1 to S2; its midpoint, the log-Euclidean Frechet "
            "mean, has eigenvalues "
            f"{le[0]:.2f} and {le[1]:.2f}.",
            "## 4.4 Frequency-Band Covariance Extraction")
    c = Canvas(720, 480, "A slice of the cone: the chord and the log-Euclidean geodesic")
    ox, oy, sc = 215, 392, 62
    X = lambda b: ox + sc * b  # noqa: E731
    Y = lambda a: oy - sc * a  # noqa: E731
    bl, at = 3.0, 4.6
    _poly(c, [(X(0), Y(0)), (X(bl), Y(bl)), (X(bl), Y(at)), (X(-bl), Y(at)), (X(-bl), Y(bl))], SERIES[2], 0.10)
    c.line(X(-bl), Y(0), X(bl), Y(0), GRID, 1)
    c.line(X(0), Y(-1.25), X(0), Y(at), GRID, 1)
    for a in (1, 2, 3, 4):
        c.line(X(0) - 4, Y(a), X(0) + 4, Y(a), INK3, 1)
        c.text(X(0) - 9, Y(a) + 4, str(a), 10.5, "end", INK3)
    for b in (-2, -1, 1, 2):
        c.line(X(b), Y(0) - 4, X(b), Y(0) + 4, INK3, 1)
        c.text(X(b), Y(0) + 17, str(b), 10.5, "middle", INK3)
    c.text(X(0) + 8, Y(at) + 4, "a, diagonal entry", 11, "start", INK2)
    c.text(X(bl) + 8, Y(0) + 4, "b, off-diagonal entry", 11, "start", INK2)
    c.line(X(0), Y(0), X(bl), Y(bl), INK3, 1.5, dash="5 5")
    c.line(X(0), Y(0), X(-bl), Y(bl), INK3, 1.5, dash="5 5")
    c.text(X(1.85), Y(1.2), "a − b = 0", 11, "start", INK2, italic=True)
    c.text(X(-1.85), Y(1.2), "a + b = 0", 11, "end", INK2, italic=True)
    c.text(X(-2.85), Y(4.2), "positive definite:", 11.5, "start", INK2)
    c.text(X(-2.85), Y(4.2) + 16, "a > |b|", 11.5, "start", INK2)
    # chord and geodesic
    c.line(X(s1[1]), Y(s1[0]), X(s2[1]), Y(s2[0]), SERIES[1], 2)
    c.polyline([(X(geo(i / 80)[1]), Y(geo(i / 80)[0])) for i in range(81)], SERIES[0], 2, title="log-Euclidean geodesic")
    c.dot(X(am[1]), Y(am[0]), SERIES[1], 4.5, title="arithmetic mean: eigenvalues 2.75, 2.25")
    c.text(X(am[1]) - 11, Y(am[0]) + 4, "arithmetic mean", 11, "end", INK)
    c.dot(X(lm[1]), Y(lm[0]), SERIES[0], 4.5, title=f"log-Euclidean mean: eigenvalues {le[0]:.3f}, {le[1]:.3f}")
    c.text(X(0.387) - 11, Y(lm[0]) + 17, "log-Euclidean mean", 11, "end", INK)
    c.dot(X(s1[1]), Y(s1[0]), INK, 4.5, title="S1 = [[1, 0.5], [0.5, 1]]")
    c.text(X(s1[1]) + 11, Y(s1[0]) + 4, "S₁", 12, "start", INK, "600")
    c.dot(X(s2[1]), Y(s2[0]), INK, 4.5, title="S2 = [[4, 0], [0, 4]]")
    c.text(X(s2[1]) + 11, Y(s2[0]) - 6, "S₂", 12, "start", INK, "600")
    _ring(c, X(0), Y(0), 4.5, INK2)
    c.text(X(0) + 11, Y(0) + 35, "zero matrix: outside", 11, "start", INK2)
    _ring(c, X(-s1[1]), Y(-s1[0]), 4.5, INK2)
    c.text(X(-s1[1]) + 11, Y(-s1[0]) + 4, "−S₁: outside", 11, "start", INK2)
    # notes
    nx = 440
    c.text(nx, 110, "S₁ = [[1, 0.5], [0.5, 1]]", 11.5, "start", INK)
    c.text(nx, 128, "eigenvalues 1.5 and 0.5", 11, "start", INK2)
    c.text(nx, 158, "S₂ = [[4, 0], [0, 4]]", 11.5, "start", INK)
    c.text(nx, 176, "eigenvalues 4 and 4", 11, "start", INK2)
    c.add(f'<rect x="{nx}" y="205" width="12" height="12" rx="3" fill="{SERIES[1]}"/>')
    c.text(nx + 18, 215, "chord: (1 − t) S₁ + t S₂", 11.5, "start", INK)
    c.text(nx + 18, 233, "midpoint eigenvalues 2.75, 2.25", 11, "start", INK2)
    c.add(f'<rect x="{nx}" y="262" width="12" height="12" rx="3" fill="{SERIES[0]}"/>')
    c.text(nx + 18, 272, "exp((1 − t) log S₁ + t log S₂)", 11.5, "start", INK)
    c.text(nx + 18, 290, f"midpoint eigenvalues {le[0]:.2f}, {le[1]:.2f}", 11, "start", INK2)
    c.save(p)


# ------------------------------------------------------------------ chapter 5
def fig_5_1():
    n_samples, periods = 5000, 5
    step = 2 * math.pi * periods / (n_samples - 1)      # t = np.linspace(0, 2*pi*5, 5000), Section 5.6

    def x(i):
        return math.sin(i * step)

    d_text, d_quarter = 50, 250
    assert abs(d_text * step - 2 * math.pi / 20) < 1e-3 and abs(d_quarter * step - math.pi / 2) < 1e-3
    p = reg(CH5, "5.1",
            "Takens' delay embedding of the sine wave of Section 5.6, 5000 samples over five periods. Left: "
            "the signal against the sample index, with one pair of samples a delay τ = 250 apart. Right: "
            "each pair (x(t), x(t + τ)) plotted as a point, the embedding with d = 2. With the delay of the "
            "text, 50 samples, the points trace a thin ellipse, and with 250 samples, a quarter period, a "
            "circle: both are closed loops, which persistent homology reports as a long-lived H1 feature.",
            "## 5.3 Persistent Homology")
    c = Canvas(720, 400, "Delay coordinates turn a sine wave into a closed loop")
    ax = Axes(c, 62, 76, 340, 240, (0, 2000), (-1.2, 1.2), [0, 500, 1000, 1500, 2000], [-1, 0, 1],
              "sample index t", "x(t)")
    c.polyline([(ax.X(i), ax.Y(x(i))) for i in range(0, 2001, 5)], INK3, 2, title="x(t) = sin(t)")
    i0 = 300
    for i, lab, dx, anchor in ((i0, "x(t)", -9, "end"), (i0 + d_quarter, "x(t + τ)", 10, "start")):
        c.line(ax.X(i), ax.Y(-1.2), ax.X(i), ax.Y(x(i)), SERIES[0], 1.5, dash="3 3")
        c.dot(ax.X(i), ax.Y(x(i)), SERIES[0], 4.5, title=f"sample {i}: {x(i):.3f}")
        c.text(ax.X(i) + dx, ax.Y(x(i)) + (-8 if x(i) > 0 else 16), lab, 11, anchor, INK)
    yb = ax.Y(-1.2) - 10
    c.line(ax.X(i0), yb, ax.X(i0 + d_quarter), yb, SERIES[0], 1.5)
    c.text(ax.X(i0 + d_quarter / 2), yb - 6, "τ = 250", 11, "middle", INK)
    bx = Axes(c, 470, 86, 220, 220, (-1.2, 1.2), (-1.2, 1.2), [-1, 0, 1], [-1, 0, 1], "x(t)", "x(t + τ)")
    c.line(bx.X(0), bx.Y(-1.2), bx.X(0), bx.Y(1.2), GRID, 1)
    for j, d in ((1, d_text), (0, d_quarter)):
        pts = [(bx.X(x(i)), bx.Y(x(i + d))) for i in range(0, 1001, 4)]
        c.polyline(pts + pts[:1], SERIES[j], 2, title=f"delay {d} samples")
    c.dot(bx.X(x(i0)), bx.Y(x(i0 + d_quarter)), SERIES[0], 4.5,
          title=f"the pair marked at left: ({x(i0):.3f}, {x(i0 + d_quarter):.3f})")
    legend(c, 62, 50, [("τ = 250 samples, a quarter period", SERIES[0]), ("τ = 50 samples, as in Section 5.6", SERIES[1])])
    c.save(p)


def _rips_persistence(pts):
    """Vietoris-Rips persistence of a small planar cloud, dimensions 0 and 1, by the standard
    column reduction over Z/2. Returns (H0 pairs, H1 pairs) as (birth, death) lists; the one
    component that never dies is left out."""
    n = len(pts)
    dm = [[math.dist(pts[i], pts[j]) for j in range(n)] for i in range(n)]
    simp = [(0.0, 0, (i,)) for i in range(n)]
    simp += [(dm[i][j], 1, (i, j)) for i in range(n) for j in range(i + 1, n)]
    simp += [(max(dm[i][j], dm[i][k], dm[j][k]), 2, (i, j, k))
             for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n)]
    simp.sort()
    index = {s[2]: t for t, s in enumerate(simp)}
    low_col, cols, h0, h1 = {}, {}, [], []
    for t, (val, dim, verts) in enumerate(simp):
        if dim == 0:
            continue
        col = {index[verts[:q] + verts[q + 1:]] for q in range(len(verts))}
        while col and max(col) in low_col:
            col ^= cols[low_col[max(col)]]
        if col:
            low = max(col)
            low_col[low], cols[t] = t, col
            birth = simp[low][0]
            if simp[low][1] == 0:
                h0.append((0.0, val))
            elif val > birth + 1e-12:
                h1.append((birth, val))
    return h0, h1


def fig_5_2():
    def ring(cx, cy, r, m, phase):
        out = []
        for i in range(m):
            ang = 2 * math.pi * i / m + 0.12 * math.sin(3 * i + phase)
            rr = r * (1 + 0.07 * math.sin(7 * i + 2 * phase))
            out.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        return out

    cloud = ring(0.0, 0.0, 1.0, 12, 0.5) + ring(3.3, 0.0, 0.75, 10, 1.1)
    h0, h1 = _rips_persistence(cloud)
    assert len(h0) == len(cloud) - 1
    h0s = sorted(d for _, d in h0)
    merge = h0s[-1]
    loops = sorted(h1, key=lambda bd: bd[1] - bd[0], reverse=True)
    assert len(loops) >= 2 and merge > 2 * h0s[-2]
    big = loops[:2]
    small = loops[2:]
    assert all(d - b < 0.25 * (big[1][1] - big[1][0]) for b, d in small)
    p = reg(CH5, "5.2",
            "The example of Section 5.4, two ring-shaped clusters separated by a gap, computed from the definitions "
            "of Section 5.3 for the 22 points on the left (an illustrative cloud, not data). Right: the persistence "
            "diagram, with birth scale on the horizontal axis, death scale on the vertical axis and the diagonal "
            "death = birth. Every component is born at scale 0: twenty die below "
            f"{math.ceil(h0s[-2] * 100) / 100:.2f} as points join their ring, one lives until {merge:.2f}, where the "
            "two rings join, and the last never dies and is not drawn. The two loops are born at "
            f"{big[0][0]:.2f} and {big[1][0]:.2f} and die at {big[0][1]:.2f} and {big[1][1]:.2f}, far above the diagonal"
            + (f"; {len(small)} short-lived loop{'s' if len(small) > 1 else ''} near the diagonal is sampling noise."
               if small else "."),
            "## 5.5 Feature Extraction from Persistence")
    c = Canvas(720, 400, "Two rings: one late merger and two loops far from the diagonal")
    # left: the cloud, equal scale on both axes
    sc, ox, oy = 58, 92, 200
    PX = lambda q: (ox + sc * q[0], oy - sc * q[1])  # noqa: E731
    c.text(30, 66, "point cloud", 11.5, "start", INK2)
    for q in cloud:
        c.dot(*PX(q), INK2, 3.5)
    gap = min((math.dist(a, b), a, b) for a in cloud[:12] for b in cloud[12:])
    assert abs(gap[0] - merge) < 1e-9
    (ax_, ay_), (bx_, by_) = PX(gap[1]), PX(gap[2])
    c.line(ax_, ay_, bx_, by_, SERIES[0], 1.5, dash="3 3")
    c.text((ax_ + bx_) / 2, max(ay_, by_) + 22, f"gap {merge:.2f}", 11, "middle", INK)
    c.text(PX((0, 0))[0], PX((0, -1.35))[1] + 4, "12 points", 10.5, "middle", INK3)
    c.text(PX((3.3, 0))[0], PX((0, -1.35))[1] + 4, "10 points", 10.5, "middle", INK3)
    # right: the diagram
    lim = 2.0
    assert max(d for _, d in h0 + h1) < lim
    ax = Axes(c, 440, 62, 250, 250, (0, lim), (0, lim), [0, 0.5, 1.0, 1.5, 2.0], [0, 0.5, 1.0, 1.5, 2.0],
              "birth scale ε", "death scale ε")
    c.line(ax.X(0), ax.Y(0), ax.X(lim), ax.Y(lim), INK3, 1.5, dash="5 5")
    c.text(ax.X(1.0) + 12, ax.Y(1.0) + 12, "death = birth", 10.5, "middle", INK2, italic=True, rotate=-45)
    for b, d in h0:
        c.dot(ax.X(b), ax.Y(d), SERIES[0], 4, title=f"H0: born 0, dies {d:.3f}")
    for b, d in h1:
        c.dot(ax.X(b), ax.Y(d), SERIES[1], 4.5, title=f"H1: born {b:.3f}, dies {d:.3f}")
    c.text(ax.X(0) + 10, ax.Y(merge) + 4, "rings join", 11, "start", INK)
    for (b, d), lab in zip(big, ("larger ring", "smaller ring")):
        c.text(ax.X(b) + 10, ax.Y(d) + 4, lab, 11, "start", INK)
    c.text(ax.X(0) + 10, ax.Y(h0s[-2]) - 10, "inside a ring", 11, "start", INK2)
    legend(c, 440, 44, [("H0, components", SERIES[0]), ("H1, loops", SERIES[1])])
    c.save(p)


# ------------------------------------------------------------------ chapter 6
def fig_6_1():
    v_cons, v_fair = 25.0, 0.25

    def ratio(deg):
        t = math.radians(deg)
        return math.sqrt(math.cos(t) ** 2 / v_cons + math.sin(t) ** 2 / v_fair)

    assert abs(ratio(0) - 0.2) < 1e-12 and abs(ratio(90) - 2.0) < 1e-12      # Section 6.1.1
    cross = math.degrees(math.asin(math.sqrt((1 - 1 / v_cons) / (1 / v_fair - 1 / v_cons))))
    assert abs(ratio(cross) - 1.0) < 1e-12
    p = reg(CH6, "6.1",
            "Mahalanobis length of a unit Euclidean step, against the direction of the step in the plane of "
            "Consequences and Fairness, for the diagonal variances 25 and 0.25 of Section 6.1.1 with the "
            "coupling left out, as in the text. The length runs from 0.2 along Consequences to 2.0 along "
            "Fairness, the square roots of the smallest and largest eigenvalues of the precision matrix. "
            f"Below 1, at angles under {cross:.1f} degrees from the Consequences axis, the Euclidean distance "
            f"exceeds the Mahalanobis distance and the Euclidean heuristic overestimates, the failure of "
            f"Proposition 6.1. "
            "The variances are the posited values of the package default.",
            "## 6.3 The Economic Decision Complex")
    c = Canvas(720, 400, "The same Euclidean step costs 0.2 or 2.0, by direction")
    ax = Axes(c, 70, 52, 540, 280, (0, 90), (0, 2.2), [0, 15, 30, 45, 60, 75, 90], [0, 0.5, 1.0, 1.5, 2.0],
              "direction of the step: degrees from the Consequences axis toward the Fairness axis",
              "Mahalanobis length of a unit step")
    _band(c, ax.X(0), ax.y0, ax.X(cross) - ax.X(0), ax.h)
    for v in (0.5, 1.0, 1.5, 2.0):
        c.line(ax.X(0), ax.Y(v), ax.X(cross), ax.Y(v), GRID, 1)
    c.text(ax.X(0) + 8, ax.y0 + 18, "Euclidean distance is the larger:", 11, "start", INK)
    c.text(ax.X(0) + 8, ax.y0 + 34, "the heuristic overestimates", 11, "start", INK)
    c.line(ax.x0, ax.Y(1), ax.x0 + ax.w, ax.Y(1), INK3, 1.5, dash="4 4")
    c.text(ax.x0 + ax.w, ax.Y(1) - 6, "1: Euclidean and Mahalanobis agree", 10.5, "end", INK2, italic=True)
    c.polyline([(ax.X(d / 4), ax.Y(ratio(d / 4))) for d in range(0, 361)], SERIES[0], 2, title="sqrt(cos²/25 + sin²/0.25)")
    c.dot(ax.X(0), ax.Y(ratio(0)), SERIES[0], 4.5, title="along Consequences: 0.2")
    c.text(ax.X(0) + 14, ax.Y(0) - 8, "0.2 along Consequences", 11, "start", INK)
    c.dot(ax.X(90), ax.Y(ratio(90)), SERIES[0], 4.5, title="along Fairness: 2.0")
    c.text(ax.X(90) - 4, ax.Y(2.0) + 36, "2.0 along Fairness", 11, "end", INK)
    c.dot(ax.X(cross), ax.Y(1), CRITICAL, 4.5, title=f"ratio 1 at {cross:.1f} degrees")
    c.text(ax.X(cross) + 10, ax.Y(1) + 18, f"{cross:.1f}°", 11, "start", INK)
    c.save(p)


def _ultimatum_weights():
    """Edge weights of the proposer's complex, from the code printed in Section 6.6.1."""
    prec = _inv(_default_sigma())
    out = []
    for give_pct in (0, 10, 20, 30, 40, 50):
        keep = 10.0 - 10.0 * give_pct / 100
        fairness = 0.1 + 0.8 * (give_pct / 50)
        identity = 0.3 + 0.5 * (give_pct / 50)
        social = -0.2 + 0.6 * (give_pct / 50)
        delta = [0.0] * 9
        delta[CONS] = keep - 10.0
        delta[FAIR] = fairness - 0.5
        delta[IDENT] = identity - 0.5
        delta[SOCIAL] = social - 0.0
        exploitation = delta[CONS] > 0 and delta[FAIR] < -0.3     # boundary of Section 6.4.3; never fires here
        out.append((give_pct, keep, fairness, _mahal(delta, prec) + (5.0 if exploitation else 0.0)))
    return out


def fig_6_2():
    rows = _ultimatum_weights()
    for (_, _, _, w), want in zip(rows, (0.95, 0.54, 0.42, 0.74, 1.19, 1.67)):       # table of Section 6.6.1
        assert abs(w - want) < 0.006, (w, want)
    best = min(rows, key=lambda r: r[3])
    assert best[0] == 20
    p = reg(CH6, "6.2",
            "The proposer's decision complex for the ultimatum game of Section 6.6.1, projected on two of "
            "its nine coordinates, money kept and fairness; identity and social impact also move with the "
            "offer and are not shown. One edge leads from the start vertex to each offer, and each label is "
            "the edge weight in all nine dimensions, as in the table of the section. The 20% offer nearly "
            "reproduces the start's fairness and costs 0.42, the least, so the Bond Geodesic ends there; the "
            "zero offer costs 0.95 and the equal split 1.67. The weights are computed from the printed code, "
            "whose covariance and scaling functions are set by hand, so this is the model's construction and "
            "not a measurement.",
            "### 6.6.2 The Prisoner's Dilemma")
    c = Canvas(720, 400, "Ultimatum game: the least-friction edge ends at the 20% offer")
    ax = Axes(c, 80, 56, 540, 270, (4.5, 10.7), (0, 1), [5, 6, 7, 8, 9, 10], [0, 0.2, 0.4, 0.6, 0.8, 1.0],
              "money kept by the proposer, dollars (dimension 1)", "fairness (dimension 3)")
    sx, sy = ax.X(10.0), ax.Y(0.5)
    for give, keep, fair, w in rows:
        hot = give == 20
        c.line(sx, sy, ax.X(keep), ax.Y(fair), CRITICAL if hot else INK3, 3 if hot else 1.5)
    place = {0: ("start", 11, 4), 10: ("middle", 0, 21), 20: ("middle", 0, 22), 30: ("end", -9, 17),
             40: ("end", -9, 17), 50: ("start", -8, -12)}
    for give, keep, fair, w in rows:
        hot = give == 20
        c.dot(ax.X(keep), ax.Y(fair), CRITICAL if hot else SERIES[0], 5,
              title=f"offer {give}%: keep {keep:g}, fairness {fair:.2f}, edge weight {w:.4f}")
        anchor, dx, dy = place[give]
        c.text(ax.X(keep) + dx, ax.Y(fair) + dy, f"offer {give}%: {w:.2f}", 11, anchor, INK, "600" if hot else "normal")
    c.dot(sx, sy, INK, 5, title="start: money 10, fairness 0.5, identity 0.5")
    c.text(sx + 11, sy - 2, "start", 11.5, "start", INK, "600")
    c.text(sx + 11, sy + 13, "fairness 0.5", 10.5, "start", INK2)
    legend(c, 80, 42, [("Bond Geodesic, the least edge weight", CRITICAL), ("offer vertices", SERIES[0])])
    c.text(16, 390, "edge weights from the printed code; covariance and scaling functions are hand-set (Section 21.8)",
           10.5, "start", INK3, italic=True)
    c.save(p)


# ------------------------------------------------------------------ chapter 7
def _loss_gain(scale=1.0, magnitude=1.0):
    """Displacements of compute_loss_aversion (Section 7.7.1), loss coefficients scaled by `scale`."""
    gain = [0.0] * 9
    gain[CONS] = magnitude
    gain[SOCIAL] = 0.05 * magnitude
    loss = [0.0] * 9
    loss[CONS] = -magnitude
    loss[RIGHTS] = -0.15 * magnitude * scale
    loss[FAIR] = -0.1 * magnitude * scale
    loss[SOCIAL] = -0.1 * magnitude * scale
    loss[IDENT] = -0.1 * magnitude * scale
    return gain, loss


def _lambda(scale):
    prec = _inv(_default_sigma())
    gain, loss = _loss_gain(scale)
    return _mahal(loss, prec) / _mahal(gain, prec)


def fig_7_1():
    sigma = _default_sigma()
    prec = _inv(sigma)
    gain, loss = _loss_gain()
    dg, dl = _mahal(gain, prec), _mahal(loss, prec)
    assert abs(dl / dg - 2.22) < 0.005                                   # Section 7.7.1
    sd = [math.sqrt(sigma[i][i]) for i in range(9)]
    g = [gain[i] / sd[i] for i in range(9)]
    l_ = [loss[i] / sd[i] for i in range(9)]
    ng, nl = sum(1 for v in g if v), sum(1 for v in l_ if v)
    assert (ng, nl) == (2, 5)
    p = reg(CH7, "7.1",
            "The displacements that the code of Section 7.7.1 assigns to a gain and to a loss of magnitude 1, "
            "each divided by the standard deviation of its dimension under the default "
            "covariance, 5 for money and 0.5 for the others. The gain moves two dimensions and the loss "
            "moves five. "
            f"The Mahalanobis distance from the reference is {dl:.3f} for the loss against {dg:.3f} for the "
            "gain, a ratio of 2.22. "
            "The displacement coefficients and the covariance are set by hand, so the ratio is a property of "
            "that construction, not a measured value.",
            "### 7.7.2 The Endowment Effect")
    c = Canvas(720, 400, "A loss moves five dimensions, a gain two")
    names = ["Consequences (money)", "Rights", "Fairness", "Autonomy", "Privacy/trust", "Social impact",
             "Virtue/identity", "Legitimacy", "Epistemic"]
    x0, w, y0, rh = 180, 300, 62, 29
    lo, hi = -0.4, 0.25
    X = lambda v: x0 + w * (v - lo) / (hi - lo)  # noqa: E731
    for v in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2):
        c.line(X(v), y0, X(v), y0 + 9 * rh, GRID, 1)
        c.text(X(v), y0 + 9 * rh + 16, f"{v:g}", 11, "middle", INK2)
    c.line(X(0), y0, X(0), y0 + 9 * rh, INK3, 1.5)
    c.text(x0 + w / 2, y0 + 9 * rh + 34, "displacement, in standard deviations of the dimension", 11.5, "middle", INK2)
    for i, name in enumerate(names):
        y = y0 + rh * (i + 0.5)
        moved = g[i] or l_[i]
        c.text(x0 - 10, y + 4, name, 11.5, "end", INK if moved else INK3)
        if g[i]:
            c.hrect(X(0), y - 10, X(g[i]) - X(0), 9, SERIES[0], title=f"{name}: gain {g[i]:+.2f} sd")
            c.text(X(g[i]) + 6, y - 2, f"+{g[i]:.1f}", 10.5, "start", INK)
        if l_[i]:
            xl = X(l_[i])
            c.add(f'<path d="M{X(0):.2f},{y + 1:.2f} L{xl + 4:.2f},{y + 1:.2f} Q{xl:.2f},{y + 1:.2f} {xl:.2f},{y + 5:.2f} '
                  f'L{xl:.2f},{y + 6:.2f} Q{xl:.2f},{y + 10:.2f} {xl + 4:.2f},{y + 10:.2f} L{X(0):.2f},{y + 10:.2f} Z" '
                  f'fill="{SERIES[1]}"><title>{name}: loss {l_[i]:+.2f} sd</title></path>')
            c.text(xl - 6, y + 10, f"−{abs(l_[i]):.1f}", 10.5, "end", INK)
    nx = 510
    c.text(nx, 100, "gain", 12, "start", INK, "600")
    c.text(nx, 118, f"{ng} dimensions moved", 11.5, "start", INK2)
    c.text(nx, 135, f"distance {dg:.3f}", 11.5, "start", INK2)
    c.text(nx, 172, "loss", 12, "start", INK, "600")
    c.text(nx, 190, f"{nl} dimensions moved", 11.5, "start", INK2)
    c.text(nx, 207, f"distance {dl:.3f}", 11.5, "start", INK2)
    c.text(nx, 246, f"λ = {dl:.3f} / {dg:.3f} = {dl / dg:.2f}", 11.5, "start", INK)
    legend(c, 180, 42, [("gain of magnitude 1", SERIES[0]), ("loss of magnitude 1", SERIES[1])])
    c.text(16, 390, "displacement coefficients and covariance are hand-set (Section 21.8)", 10.5, "start", INK3,
           italic=True)
    c.save(p)


def fig_7_2():
    table = [(0, 0.88), (0.25, 0.99), (0.5, 1.32), (1, 2.22), (2, 4.25)]         # Section 7.7.1
    for s, want in table:
        assert abs(_lambda(s) - want) < 0.006, (s, _lambda(s), want)
    p = reg(CH7, "7.2",
            "The loss aversion ratio λ of Section 7.7.1 against a common scale factor applied to the four "
            "non-monetary loss coefficients, under the default covariance. The curve is computed from the "
            "printed code and the five marked points are the values of the table. At scale 0 the loss moves "
            "money only and λ is 0.88; at scale 1, the coefficients as printed, λ is 2.22, inside the band "
            "2.0 to 2.5 that the chapter cites from Kahneman and Tversky. The ratio falls in the band by the "
            "choice of the coefficients, which are set by hand; it is not a measurement.",
            "### 7.7.2 The Endowment Effect")
    c = Canvas(720, 400, "Loss aversion follows the hand-set displacement coefficients")
    ax = Axes(c, 70, 52, 540, 280, (0, 2), (0, 5), [0, 0.5, 1.0, 1.5, 2.0], [0, 1, 2, 3, 4, 5],
              "scale of the loss coefficients (1 = as printed)", "loss aversion ratio λ")
    _band(c, ax.x0, ax.Y(2.5), ax.w, ax.Y(2.0) - ax.Y(2.5))
    c.text(ax.x0 + 8, ax.Y(2.25) + 4, "empirical range 2.0 to 2.5", 11, "start", INK2, italic=True)
    c.line(ax.x0, ax.Y(1), ax.x0 + ax.w, ax.Y(1), INK3, 1.5, dash="4 4")
    c.text(ax.x0 + ax.w, ax.Y(1) + 16, "λ = 1: loss and gain equally far", 10.5, "end", INK2, italic=True)
    c.polyline([(ax.X(i / 50), ax.Y(_lambda(i / 50))) for i in range(101)], SERIES[0], 2, title="λ against scale")
    place = {0: ("start", 9, 17), 0.25: ("middle", 0, -12), 0.5: ("end", -8, -8), 1: ("end", -10, -6), 2: ("end", 0, -11)}
    for s, want in table:
        lam = _lambda(s)
        c.dot(ax.X(s), ax.Y(lam), CRITICAL if s == 1 else SERIES[0], 4.5, title=f"scale {s:g}: λ = {lam:.3f}")
        anchor, dx, dy = place[s]
        c.text(ax.X(s) + dx, ax.Y(lam) + dy, f"{want:.2f}", 11, anchor, INK, "600" if s == 1 else "normal")
    c.save(p)
