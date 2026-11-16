"""How much signal does the Chapter 19 generator contain?

Uses the generator's own coefficients (examples/defect_prediction/model.py) as an
oracle: the systematic part of the logit, without the noise term. No fitted model
can rank modules better than this in expectation. Also counts what the test split
of make_evaluate_fn(n_samples=1000, test_fraction=0.3, seed=42) contains.

Usage: python ch19_oracle.py <structural-fuzzing checkout> <out.json>
"""
import json
import os
import sys

sys.path[:0] = [os.path.join(sys.argv[1], "src"), sys.argv[1]]
import numpy as np  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

from examples.defect_prediction.model import generate_defect_data  # noqa: E402

X, y = generate_defect_data(n_samples=1000, seed=42)
cyc, ess, des = X[:, 3], X[:, 4], X[:, 5]
rev, auth, churn, loc = X[:, 13], X[:, 14], X[:, 15], X[:, 0]
logit = (-3 + 0.1 * np.log1p(cyc) + 0.15 * np.log1p(ess) + 0.05 * np.log1p(des)
         + 0.12 * np.log1p(rev) + 0.1 * np.log1p(auth) + 0.08 * np.log1p(churn / 100)
         + 0.03 * np.log1p(loc / 1000))
p = 1 / (1 + np.exp(-logit))
idx = np.random.default_rng(42 + 1).permutation(1000)   # the split in make_evaluate_fn
te = idx[:300]
out = {
    "defect_rate": float(y.mean()),
    "systematic_logit_mean": float(logit.mean()),
    "systematic_logit_sd": float(logit.std()),
    "noise_sd": 0.5,
    "max_systematic_p": float(p.max()),
    "modules_with_systematic_p_above_half": int((p > 0.5).sum()),
    "oracle_auc_all": float(roc_auc_score(y, logit)),
    "oracle_auc_test": float(roc_auc_score(y[te], logit[te])),
    "test_defects": int(y[te].sum()),
    "test_size": int(len(te)),
    "test_majority_accuracy": float(1 - y[te].mean()),
}
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps(out, indent=1))
