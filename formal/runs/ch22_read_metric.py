#!/usr/bin/env python3
"""Recorded run for Chapter 22 (the read metric).

A smooth consumer g(x) = W tanh(Bx) reads k = 3 directions of a p = 8 dimensional Gaussian
source. The script
  1. estimates the averaged read metric Q = E[J^T J] from finite differences of g at m probe
     points (the consumer is queried, its Jacobian is never read),
  2. allocates a description at a fixed rate in two ways: reverse water-filling for the
     identity weight (reconstruction error) and for the estimated weight (consumer error),
  3. measures the consumer loss E||g(T_hat) - g(T)||^2 of each by simulation.

PREDICTIONS, written before the first run. Each can fail.
  P1  At every rate, the allocation for the estimated weight has at most HALF the consumer
      loss of the allocation for the identity weight.
  P2  At the highest rate, tr(Q Delta) for the weighted allocation is within 10% of the
      measured consumer loss.
  P3  The estimate from m = 200 probe points has relative Frobenius error at most 0.20
      against a reference computed from 200,000 analytic Jacobians.

No prediction was registered outside this file. The class of the result is exploratory
(Chapter 21). Usage:  python ch22_read_metric.py   (NumPy only, a few seconds on one core).
"""
from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone

import numpy as np

SEED = 20261125
P, K = 8, 3
M_PROBE = 200
H = 1e-4
N_REF = 200_000
N_SIM = 200_000
RATES = (1.0, 2.0, 4.0)  # nats per source vector
P1_RATIO, P2_REL, P3_REL = 0.5, 0.10, 0.20


def make_problem(rng):
    a = rng.standard_normal((P, P))
    q, _ = np.linalg.qr(a)
    spectrum = 2.0 ** -np.arange(P)  # variances 1, 1/2, ..., 1/128
    sigma = (q * spectrum) @ q.T
    b = rng.standard_normal((K, P))
    # scale B so that each coordinate of Bx has standard deviation 0.5
    sd = np.sqrt(np.einsum("ij,jk,ik->i", b, sigma, b))
    b = 0.5 * b / sd[:, None]
    w = rng.standard_normal((K, K))
    return sigma, b, w


def consumer(x, b, w):
    return np.tanh(x @ b.T) @ w.T


def jacobian(x, b, w):
    d = 1.0 - np.tanh(x @ b.T) ** 2  # (n, K)
    return np.einsum("ik,nk,kj->nij", w, d, b)  # (n, K, P)


def sym_sqrt(a):
    val, vec = np.linalg.eigh(a)
    return (vec * np.sqrt(np.clip(val, 0.0, None))) @ vec.T


def probe_metric(x, b, w):
    """Average of J^T J over the rows of x, from 2p central-difference queries per row."""
    n = x.shape[0]
    jac = np.empty((n, K, P))
    for j in range(P):
        e = np.zeros(P)
        e[j] = H
        jac[:, :, j] = (consumer(x + e, b, w) - consumer(x - e, b, w)) / (2 * H)
    return np.einsum("nki,nkj->ij", jac, jac) / n


def water_fill(sigma, weight, rate):
    """Error covariance of least weighted error tr(weight Delta) at the given rate.

    In the basis that whitens the source, the modes are the eigenvectors of
    A = Sigma^{1/2} weight Sigma^{1/2}; mode k keeps the fraction min(1, theta/gamma_k)
    of its variance as error, and the rate is (1/2) sum_k [log(gamma_k/theta)]_+.
    """
    s_half = sym_sqrt(sigma)
    gamma, v = np.linalg.eigh(s_half @ weight @ s_half)
    gamma = np.clip(gamma, 0.0, None)

    def rate_at(theta):
        return 0.5 * np.sum(np.log(np.maximum(gamma / theta, 1.0)))

    lo, hi = 1e-300, gamma.max()
    for _ in range(400):
        mid = np.sqrt(lo * hi)
        if rate_at(mid) > rate:
            lo = mid
        else:
            hi = mid
    theta = np.sqrt(lo * hi)
    frac = np.minimum(1.0, theta / np.maximum(gamma, 1e-300))
    delta = s_half @ (v * frac) @ v.T @ s_half
    return delta, float(rate_at(theta)), int(np.sum(gamma > theta))


def consumer_loss(sigma, delta, b, w, rng):
    t_hat = rng.standard_normal((N_SIM, P)) @ sym_sqrt(sigma - delta)
    z = rng.standard_normal((N_SIM, P)) @ sym_sqrt(delta)
    d = consumer(t_hat + z, b, w) - consumer(t_hat, b, w)
    per = np.sum(d * d, axis=1)
    return float(per.mean()), float(per.std(ddof=1) / np.sqrt(N_SIM))


def main():
    rng = np.random.default_rng(SEED)
    sigma, b, w = make_problem(rng)
    s_half = sym_sqrt(sigma)

    ref_x = rng.standard_normal((N_REF, P)) @ s_half
    jac = jacobian(ref_x, b, w)
    q_ref = np.einsum("nki,nkj->ij", jac, jac) / N_REF

    probe_x = rng.standard_normal((M_PROBE, P)) @ s_half
    q_hat = probe_metric(probe_x, b, w)
    rel_err = float(np.linalg.norm(q_hat - q_ref) / np.linalg.norm(q_ref))

    rows = []
    for rate in RATES:
        d_id, r_id, n_id = water_fill(sigma, np.eye(P), rate)
        d_w, r_w, n_w = water_fill(sigma, q_hat, rate)
        loss_id, se_id = consumer_loss(sigma, d_id, b, w, rng)
        loss_w, se_w = consumer_loss(sigma, d_w, b, w, rng)
        rows.append(
            {
                "rate_nats": rate,
                "identity_weight": {
                    "rate_achieved": r_id,
                    "active_modes": n_id,
                    "reconstruction_error": float(np.trace(d_id)),
                    "consumer_loss": loss_id,
                    "consumer_loss_se": se_id,
                    "tr_Q_delta": float(np.trace(q_ref @ d_id)),
                },
                "estimated_weight": {
                    "rate_achieved": r_w,
                    "active_modes": n_w,
                    "reconstruction_error": float(np.trace(d_w)),
                    "consumer_loss": loss_w,
                    "consumer_loss_se": se_w,
                    "tr_Q_delta": float(np.trace(q_ref @ d_w)),
                },
                "loss_ratio_weighted_over_identity": loss_w / loss_id,
            }
        )

    top = rows[-1]["estimated_weight"]
    p2_rel = abs(top["tr_Q_delta"] - top["consumer_loss"]) / top["consumer_loss"]
    verdicts = {
        "P1": {
            "bar": f"loss ratio <= {P1_RATIO} at every rate",
            "values": [r["loss_ratio_weighted_over_identity"] for r in rows],
            "passes": bool(all(r["loss_ratio_weighted_over_identity"] <= P1_RATIO for r in rows)),
        },
        "P2": {"bar": f"relative difference <= {P2_REL}", "value": float(p2_rel), "passes": bool(p2_rel <= P2_REL)},
        "P3": {"bar": f"relative Frobenius error <= {P3_REL}", "value": rel_err, "passes": bool(rel_err <= P3_REL)},
    }
    out = {
        "script": "ch22_read_metric.py",
        "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.system(),
        "seed": SEED,
        "p": P,
        "k": K,
        "probe_points": M_PROBE,
        "probe_queries": 2 * P * M_PROBE,
        "step": H,
        "source_variances": [float(x) for x in np.linalg.eigvalsh(sigma)[::-1]],
        "eigenvalues_Q_reference": [float(x) for x in np.linalg.eigvalsh(q_ref)[::-1]],
        "eigenvalues_Q_estimate": [float(x) for x in np.linalg.eigvalsh(q_hat)[::-1]],
        "rates": rows,
        "verdicts": verdicts,
    }
    with open("ch22_read_metric.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
