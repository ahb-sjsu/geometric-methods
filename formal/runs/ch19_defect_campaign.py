"""Chapter 19 campaign, run exactly as the chapter configures it, plus one variant.

Arm A ("package"): the structural-fuzzing defect example as shipped
(examples/defect_prediction/model.py, random forest), with the run_campaign
arguments printed in Section 19.3.1.

Arm B ("weighted"): the same data, targets and campaign, but each group's
parameter enters the model. Features are log1p-transformed and standardized on
the training split, group g is scaled by 1/sqrt(params[g]), and an L2 logistic
regression is fitted. Scaling a feature by 1/sqrt(p) under an L2 penalty is the
same as giving its coefficient a Gaussian prior with precision proportional to
p, so params[g] is the prior precision of group g (the sentinel still removes it).

Arm A's evaluation function reads only whether params[i] < 1000, so its value is
a function of the 5-bit activity mask. It is wrapped in an exact cache keyed on
that mask. Before the campaign, the cache is checked against 400 uncached calls
on random parameter vectors; any mismatch aborts the run.

Usage: python ch19_defect_campaign.py <structural-fuzzing checkout> <out.json>
"""
from __future__ import annotations

import json
import os
import platform
import sys
import time

CPUS = {40, 41, 42, 43}
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

SF_ROOT, OUT = sys.argv[1], sys.argv[2]
sys.path[:0] = [os.path.join(SF_ROOT, "src"), SF_ROOT]

import numpy as np  # noqa: E402
import sklearn  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (accuracy_score, f1_score, precision_score,  # noqa: E402
                             recall_score, roc_auc_score)

import structural_fuzzing  # noqa: E402
from structural_fuzzing.pipeline import run_campaign  # noqa: E402
from examples.defect_prediction.model import (FEATURE_GROUPS, GROUP_NAMES,  # noqa: E402
                                              generate_defect_data, make_evaluate_fn)

os.sched_setaffinity(0, CPUS)  # re-pin after imports (MKL can pin to core 0)

CAMPAIGN = dict(max_subset_dims=4, n_mri_perturbations=300, mri_scale=0.5,
                mri_weights=(0.5, 0.3, 0.2), start_dim=0, run_baselines=True,
                adversarial_tolerance=0.5, verbose=True)
TARGETS = {"Accuracy": 75.0, "Precision": 70.0, "Recall": 65.0, "F1": 67.0, "AUC": 80.0}


class Counted:
    def __init__(self, fn):
        self.fn, self.calls = fn, 0

    def __call__(self, p):
        self.calls += 1
        return self.fn(p)


def mask_cache(fn):
    store = {}

    def wrapped(p):
        key = tuple(bool(v < 1000) for v in p)
        if key not in store:
            store[key] = fn(np.asarray(p, dtype=float))
        mae, err = store[key]
        return mae, dict(err)
    wrapped.store = store
    return wrapped


def weighted_evaluate_fn(n_samples=1000, test_fraction=0.3, seed=42):
    X, y = generate_defect_data(n_samples=n_samples, seed=seed)
    rng = np.random.default_rng(seed + 1)          # same split as the package example
    idx = rng.permutation(n_samples)
    n_test = int(n_samples * test_fraction)
    te, tr = idx[:n_test], idx[n_test:]
    Z = np.log1p(X)
    mu, sd = Z[tr].mean(0), Z[tr].std(0)
    Z = (Z - mu) / np.where(sd > 0, sd, 1.0)
    groups = list(FEATURE_GROUPS.values())

    def evaluate_fn(params):
        cols, scale = [], []
        for g, members in enumerate(groups):
            if params[g] < 1000:
                cols += members
                scale += [1.0 / np.sqrt(params[g])] * len(members)
        if not cols:
            err = {k: -v for k, v in TARGETS.items()}
            return sum(abs(v) for v in err.values()) / 5, err
        A = Z[:, cols] * np.asarray(scale)
        m = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000)
        m.fit(A[tr], y[tr])
        yp, pr = m.predict(A[te]), m.predict_proba(A[te])[:, 1]
        got = {"Accuracy": accuracy_score(y[te], yp) * 100,
               "Precision": precision_score(y[te], yp, zero_division=0) * 100,
               "Recall": recall_score(y[te], yp, zero_division=0) * 100,
               "F1": f1_score(y[te], yp, zero_division=0) * 100,
               "AUC": roc_auc_score(y[te], pr) * 100}
        err = {k: got[k] - TARGETS[k] for k in TARGETS}
        return sum(abs(v) for v in err.values()) / 5, err
    return evaluate_fn


def sr(r):
    return {"dims": list(map(int, r.dims)), "names": list(r.dim_names), "mae": float(r.mae),
            "errors": {k: float(v) for k, v in r.errors.items()},
            "params": [float(v) for v in r.param_values]}


def dump_report(rep):
    m = rep.mri_result
    return {
        "subsets": [sr(r) for r in rep.subset_results],
        "pareto": [sr(r) for r in rep.pareto_results],
        "sensitivity": [{"dim": int(s.dim), "name": s.dim_name, "delta_mae": float(s.delta_mae),
                         "mae_with": float(s.mae_with), "mae_without": float(s.mae_without),
                         "rank": int(s.importance_rank)} for s in rep.sensitivity_results],
        "mri": {"mri": float(m.mri), "mean": float(m.mean_omega), "p75": float(m.p75_omega),
                "p95": float(m.p95_omega), "worst_case_mae": float(m.worst_case_mae),
                "n": int(m.n_perturbations),
                "omegas": [float(v) for v in getattr(m, "perturbation_errors", [])] or None},
        "adversarial": [{"dim": int(a.dim), "name": a.dim_name, "direction": a.direction,
                         "base": float(a.base_value), "threshold": float(a.threshold_value),
                         "ratio": float(a.threshold_ratio), "flipped": a.target_flipped}
                        for a in rep.adversarial_results],
        "composition": {"order": list(map(int, rep.composition_result.order)),
                        "names": list(rep.composition_result.order_names),
                        "mae": [float(v) for v in rep.composition_result.mae_sequence]},
        "forward": [sr(r) for r in rep.forward_results],
        "backward": [sr(r) for r in rep.backward_results],
    }


def all_masks(fn):
    out = {}
    for b in range(32):
        p = np.array([1.0 if (b >> i) & 1 else 1e6 for i in range(5)])
        mae, err = fn(p)
        out["".join("1" if (b >> i) & 1 else "0" for i in range(5))] = {
            "mae": float(mae), "errors": {k: float(v) for k, v in err.items()}}
    return out


def main():
    rec = {"meta": {"python": platform.python_version(), "numpy": np.__version__,
                    "sklearn": sklearn.__version__, "structural_fuzzing": structural_fuzzing.__version__,
                    "host": platform.node(), "cpus": sorted(os.sched_getaffinity(0)),
                    "campaign": {k: v for k, v in CAMPAIGN.items()}, "groups": GROUP_NAMES,
                    "mask_order": "bit i = group i, in the order of groups"}}
    X, y = generate_defect_data(n_samples=1000, seed=42)
    rec["meta"]["defect_rate"] = float(y.mean())
    rec["meta"]["n_samples"] = int(len(y))

    # ---- Arm A: the package example, cached on the activity mask, cache verified
    raw = make_evaluate_fn(n_samples=1000, test_fraction=0.3, seed=42)
    cached = mask_cache(raw)
    rng = np.random.default_rng(20261116)
    t0, worst = time.time(), 0.0
    for _ in range(400):
        p = np.exp(rng.uniform(np.log(1e-3), np.log(1e6), 5))
        p[rng.random(5) < 0.3] = 1e6
        a, ea = raw(p)
        b, eb = cached(p)
        if a != b or ea != eb:
            raise SystemExit(f"cache mismatch at {p.tolist()}: {a} vs {b}")
    rec["A_cache_check"] = {"calls": 400, "mismatches": 0, "seconds": round(time.time() - t0, 1)}
    print("cache check passed", flush=True)
    fa = Counted(cached)
    t0 = time.time()
    repA = run_campaign(dim_names=GROUP_NAMES, evaluate_fn=fa, **CAMPAIGN)
    rec["A"] = dump_report(repA)
    rec["A"]["calls"] = fa.calls
    rec["A"]["distinct_fits"] = len(cached.store)
    rec["A"]["seconds"] = round(time.time() - t0, 1)
    rec["A"]["all_masks"] = all_masks(cached)
    json.dump(rec, open(OUT, "w"), indent=1)
    print("arm A done", fa.calls, "calls", len(cached.store), "fits", flush=True)

    # ---- Arm B: parameters enter the model
    fb = Counted(weighted_evaluate_fn())
    t0 = time.time()
    repB = run_campaign(dim_names=GROUP_NAMES, evaluate_fn=fb, **CAMPAIGN)
    rec["B"] = dump_report(repB)
    rec["B"]["calls"] = fb.calls
    rec["B"]["seconds"] = round(time.time() - t0, 1)
    rec["B"]["all_masks"] = all_masks(fb)
    json.dump(rec, open(OUT, "w"), indent=1)
    print("arm B done", fb.calls, "calls", flush=True)


if __name__ == "__main__":
    main()
