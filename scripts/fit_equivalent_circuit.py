"""Fit the lumped equivalent circuit of the cross-slot FSS to the CST S-parameters.

Circuit (shunt admittance between two free-space ports, Z0 = 376.73 ohm):
    Y(f) = 1/(R + j*w*L1) + j*w*C1 + 1/(j*w*L2 + 1/(j*w*C2))

Usage:  python scripts/fit_equivalent_circuit.py
Input : data/normal_incidence_sparams.csv  (frequency_GHz, S11_dB, S21_dB)
Output: prints fitted values, saves images/sparams_fit_check.png
"""
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
Z0 = 376.73

data = np.loadtxt(ROOT / "data" / "normal_incidence_sparams.csv", delimiter=",", skiprows=1)
f = data[:, 0] * 1e9
w = 2 * np.pi * f
s11_cst, s21_cst = data[:, 1], data[:, 2]


def admittance(p, w):
    L1, C1, R, L2, C2 = p[0] * 1e-9, p[1] * 1e-12, p[2], p[3] * 1e-9, p[4] * 1e-12
    return 1 / (R + 1j * w * L1) + 1j * w * C1 + 1 / (1j * w * L2 + 1 / (1j * w * C2))


def s_db(p, w):
    Y = admittance(p, w)
    s21 = 2 / (2 + Z0 * Y)
    s11 = -Z0 * Y / (2 + Z0 * Y)
    return 20 * np.log10(np.abs(s11) + 1e-12), 20 * np.log10(np.abs(s21) + 1e-12)


def residual(p):
    a, b = s_db(p, w)
    wt = np.where((f > 1.8e9) & (f < 3.3e9), 3.0, 1.0)      # weight the passband
    return np.r_[wt * (a - s11_cst) * 0.5, wt * (b - s21_cst)]


# parameters: L1 [nH], C1 [pF], R [ohm], L2 [nH], C2 [pF]
p0 = np.array([3.0, 0.6, 0.5, 0.5, 0.6])
lo = np.array([0.1, 0.05, 0.0, 0.05, 0.005])
hi = np.array([50, 20, 200, 50, 20])
best = None
for seed in range(30):                                      # multi-start for a robust fit
    rng = np.random.default_rng(seed)
    x0 = np.clip(p0 * np.exp(rng.normal(0, 0.5, 5)), lo * 1.01 + 1e-9, hi * 0.99)
    try:
        r = least_squares(residual, x0, bounds=(lo, hi))
    except Exception:
        continue
    if best is None or r.cost < best.cost:
        best = r
p = best.x
a, b = s_db(p, w)
print("L1 = %.3f nH, C1 = %.3f pF, R = %.3f ohm, L2 = %.3f nH, C2 = %.3f pF" % tuple(p))
print("rms error: S11 %.3f dB, S21 %.3f dB" % (np.sqrt(np.mean((a - s11_cst) ** 2)), np.sqrt(np.mean((b - s21_cst) ** 2))))
print("series L2-C2 resonance: %.2f GHz" % (1 / (2 * np.pi * np.sqrt(p[3] * 1e-9 * p[4] * 1e-12)) / 1e9))

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(f / 1e9, s11_cst, "k", label="|S11| CST"); ax.plot(f / 1e9, s21_cst, color="#8b4513", label="|S21| CST")
ax.plot(f / 1e9, a, "--", color="#00a0ff", label="|S11| circuit"); ax.plot(f / 1e9, b, "--", color="#e0301e", label="|S21| circuit")
ax.set_xlabel("Frequency (GHz)"); ax.set_ylabel("dB"); ax.grid(alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig(ROOT / "images" / "sparams_fit_check.png", dpi=200)
