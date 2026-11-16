"""Is the Chapter 19 winner a property of the data or of one draw?

Evaluates all 31 non-empty feature-group configurations of the package's defect
example (make_evaluate_fn, n_samples=1000, test_fraction=0.3) for 20 seeds. Each
seed draws a new dataset and a new split. Records, per seed, the winning
configuration, its MAE and errors, how many configurations find any defect, and
the spread of AUC.

Usage: python ch19_redraw.py <structural-fuzzing checkout> <out.json>
"""
import json
import os
import sys

os.sched_setaffinity(0, {40, 41, 42, 43})
sys.path[:0] = [os.path.join(sys.argv[1], "src"), sys.argv[1]]
import numpy as np  # noqa: E402

from examples.defect_prediction.model import GROUP_NAMES, make_evaluate_fn  # noqa: E402

out = {"seeds": []}
for seed in range(20):
    f = make_evaluate_fn(n_samples=1000, test_fraction=0.3, seed=seed)
    rows = []
    for b in range(1, 32):
        p = np.array([1.0 if (b >> i) & 1 else 1e6 for i in range(5)])
        mae, err = f(p)
        rows.append({"groups": [GROUP_NAMES[i] for i in range(5) if (b >> i) & 1],
                     "mae": mae, "recall": err["Recall"] + 65, "auc": err["AUC"] + 80})
    rows.sort(key=lambda r: r["mae"])
    rec = {"seed": seed, "winner": rows[0]["groups"], "winner_mae": rows[0]["mae"],
           "winner_recall": rows[0]["recall"], "runner_up_mae": rows[1]["mae"],
           "configs_with_any_recall": sum(r["recall"] > 0 for r in rows),
           "auc_min": min(r["auc"] for r in rows), "auc_max": max(r["auc"] for r in rows),
           "median_mae": float(np.median([r["mae"] for r in rows]))}
    out["seeds"].append(rec)
    print(json.dumps(rec), flush=True)
w = [" + ".join(r["winner"]) for r in out["seeds"]]
out["winner_counts"] = {k: w.count(k) for k in sorted(set(w))}
out["winners_with_OO"] = sum("OO" in r["winner"] for r in out["seeds"])
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps({k: out[k] for k in ("winner_counts", "winners_with_OO")}))
