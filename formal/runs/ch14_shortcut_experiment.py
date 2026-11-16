"""Section 14.9 experiment: does gradient reversal remove a recording shortcut?

The model code is not rewritten here. It is extracted verbatim from the python
blocks of chapter-14-gradient-reversal.md (GradientReversalFn, GradientReversalLayer,
DomainAdversarialNetwork, lambda_schedule, train_dann, CodaEncoder, CodaTaskHead,
RecordingConditionHead, build_invariant_coda_classifier) and executed, so the
experiment tests the code the reader sees.

Registered before the run (this text and its sha256 are written into the record):

  P1 (null arm, the chapter's original data: random spectrograms, random labels).
     With no gradient reversal at all (max_lambda = 0), the training-time domain
     accuracy ends within 5 points of chance (20%). So "domain accuracy near
     chance" cannot be evidence that reversal worked.
  P2 (shortcut arm). Class is carried by click timing, recording condition by a
     spectral signature, and in training the condition predicts the class 90% of
     the time. On a test set where condition is independent of class, the
     baseline (max_lambda = 0) loses at least 10 points of accuracy relative to a
     test set with the training correlation.
  P3 (shortcut arm). With max_lambda = 1.0, the post-hoc probe (logistic
     regression fitted on frozen latents of held-out data) predicts the condition
     at least 15 points less accurately than for the baseline, and the shifted-test
     accuracy is at least 5 points higher than the baseline's. Mean over 3 seeds.
  max_lambda = 0.5, the chapter's default, is reported without a prediction.

Usage: python ch14_shortcut_experiment.py <chapter-14 markdown> <out.json>
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time

CPUS = {44, 45, 46, 47}
import numpy as np  # noqa: E402
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from torch.utils.data import DataLoader, TensorDataset  # noqa: E402

os.sched_setaffinity(0, CPUS)
torch.set_num_threads(4)

CH, OUT = sys.argv[1], sys.argv[2]
DOC = __doc__
REG_SHA = hashlib.sha256(DOC.encode()).hexdigest()

# ---- extract the chapter's code (blocks 3-8: GRL through the builder)
md = open(CH, encoding="utf-8").read()
blocks = re.findall(r"```python\n(.*?)```", md, flags=re.S)
code = "\n\n".join(blocks[2:8])
CHAPTER_CODE_SHA = hashlib.sha256(code.encode()).hexdigest()
ns: dict = {}
exec(compile(code, "chapter-14-blocks-3-8", "exec"), ns)
build = ns["build_invariant_coda_classifier"]
train_dann = ns["train_dann"]

K, H, N_MELS, N_FRAMES = 6, 5, 32, 48


def make_data(n, rho, rng, signal=0.4):
    """Class k: clicks at a class-specific rhythm. Condition h: a spectral gain
    curve and a narrow noise band. With probability rho, h = k mod H."""
    y = rng.integers(0, K, n)
    h = np.where(rng.random(n) < rho, y % H, rng.integers(0, H, n))
    f = np.linspace(0, 1, N_MELS)
    gains = np.stack([1.0 + 0.8 * np.sin(2 * np.pi * (j + 1) * f / 2 + j) for j in range(H)])
    bands = np.linspace(4, N_MELS - 5, H).astype(int)
    rhythms = [np.cumsum(np.r_[0, np.full(3 + k % 3, 4 + 2 * (k // 3))]) for k in range(K)]
    X = rng.normal(0, 1.0, (n, 1, N_MELS, N_FRAMES)).astype(np.float32)
    for i in range(n):
        start = rng.integers(0, N_FRAMES - 1 - rhythms[y[i]][-1])
        for t in rhythms[y[i]] + start:
            X[i, 0, :, t] += signal * np.exp(-((f - 0.5) ** 2) / 0.1)
        X[i, 0] *= gains[h[i]][:, None]
        X[i, 0, bands[h[i]] - 1:bands[h[i]] + 2, :] += 1.5
    return torch.tensor(X), torch.tensor(y), torch.tensor(h)


@torch.no_grad()
def latents(model, X):
    model.eval()
    return torch.cat([model.encoder(X[i:i + 256]) for i in range(0, len(X), 256)]).numpy()


@torch.no_grad()
def task_acc(model, X, y):
    model.eval()
    logits = torch.cat([model(X[i:i + 256])[0] for i in range(0, len(X), 256)])
    return float((logits.argmax(1) == y).float().mean())


def probe_acc(model, Xa, ha, Xb, hb):
    za, zb = latents(model, Xa), latents(model, Xb)
    mu, sd = za.mean(0), za.std(0) + 1e-6
    clf = LogisticRegression(max_iter=3000).fit((za - mu) / sd, ha.numpy())
    return float(clf.score((zb - mu) / sd, hb.numpy()))


def run(arm, max_lambda, seed, epochs):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    if arm == "null":
        n_cls, n_mels = 23, 128
        Xtr = torch.randn(2000, 1, n_mels, 64)
        ytr = torch.randint(0, n_cls, (2000,))
        htr = torch.randint(0, H, (2000,))
    else:
        n_cls, n_mels = K, N_MELS
        Xtr, ytr, htr = make_data(2400, 0.9, rng)
    model = build(n_mels=n_mels, latent_dim=64 if arm != "null" else 128,
                  n_coda_types=n_cls, n_conditions=H, max_lambda=max_lambda)
    loader = DataLoader(TensorDataset(Xtr, ytr, htr), batch_size=64, shuffle=True)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    t0 = time.time()
    hist = train_dann(model=model, train_loader=loader, optimizer=opt,
                      task_criterion=nn.CrossEntropyLoss(), domain_criterion=nn.CrossEntropyLoss(),
                      total_epochs=epochs, gamma=10.0, max_lambda=max_lambda)
    rec = {"arm": arm, "max_lambda": max_lambda, "seed": seed, "epochs": epochs,
           "train_domain_acc_final": hist["domain_accuracy"][-1],
           "train_domain_acc": hist["domain_accuracy"], "task_loss": hist["task_loss"],
           "seconds": round(time.time() - t0, 1)}
    if arm == "shortcut":
        Xin, yin, hin = make_data(1200, 0.9, rng)        # same correlation as training
        Xsh, ysh, hsh = make_data(1200, 0.0, rng)        # condition independent of class
        Xp, _, hp = make_data(1200, 0.0, rng)            # probe training set
        rec.update(acc_in=task_acc(model, Xin, yin), acc_shift=task_acc(model, Xsh, ysh),
                   probe_acc=probe_acc(model, Xp, hp, Xsh, hsh))
    print(json.dumps({k: v for k, v in rec.items() if not isinstance(v, list)}), flush=True)
    return rec


def main():
    out = {"registration_sha256": REG_SHA, "registration": DOC,
           "chapter_code_sha256": CHAPTER_CODE_SHA, "torch": torch.__version__,
           "cpus": sorted(os.sched_getaffinity(0)), "runs": []}
    for seed in (0, 1, 2):
        out["runs"].append(run("null", 0.0, seed, epochs=15))
    for lam in (0.0, 0.5, 1.0):
        for seed in (0, 1, 2):
            out["runs"].append(run("shortcut", lam, seed, epochs=25))
            json.dump(out, open(OUT, "w"), indent=1)

    def mean(arm, lam, key):
        v = [r[key] for r in out["runs"] if r["arm"] == arm and r["max_lambda"] == lam]
        return float(np.mean(v))
    p1 = abs(mean("null", 0.0, "train_domain_acc_final") - 0.2) <= 0.05
    base_gap = mean("shortcut", 0.0, "acc_in") - mean("shortcut", 0.0, "acc_shift")
    p2 = base_gap >= 0.10
    p3 = (mean("shortcut", 0.0, "probe_acc") - mean("shortcut", 1.0, "probe_acc") >= 0.15
          and mean("shortcut", 1.0, "acc_shift") - mean("shortcut", 0.0, "acc_shift") >= 0.05)
    out["grades"] = {"P1": p1, "P2": p2, "P3": p3, "baseline_gap": base_gap,
                     "summary": {f"{a}/{l}": {k: mean(a, l, k) for k in
                                 (["train_domain_acc_final"] if a == "null" else
                                  ["train_domain_acc_final", "acc_in", "acc_shift", "probe_acc"])}
                                 for a, l in [("null", 0.0), ("shortcut", 0.0),
                                              ("shortcut", 0.5), ("shortcut", 1.0)]}}
    json.dump(out, open(OUT, "w"), indent=1)
    print("GRADES", json.dumps(out["grades"]), flush=True)


if __name__ == "__main__":
    main()
