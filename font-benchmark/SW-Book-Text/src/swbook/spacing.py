"""Optical sidebearings for the Hebrew letters (script-generated, deterministic).

For each letter the *optical depth* of its left and right side is measured: the mean, over the
letter-height band, of the distance from the ink bounding box to the nearest ink, clipped at
``D`` units (rows without ink count as D).  Open sides (resh, dalet, kaf ... on the left) get a
large depth, flush sides a small one.  Sidebearings then move *against* the depth, by a
fraction ``alpha`` of its deviation from the family mean, so overall spacing keeps its average
while open-sided letters sit closer and flush-sided ones keep a little more air.
"""
import numpy as np
from .kern import _Flat, YS

D = 110.0
BAND = (0.0, 650.0)


def depths(path, band=BAND, D=D):
    pen = _Flat()
    path.draw(pen)
    lo = np.full(len(YS), np.nan)
    hi = np.full(len(YS), np.nan)
    for (x0, y0), (x1, y1) in pen.segs:
        if y0 == y1:
            continue
        ya, yb = sorted((y0, y1))
        for i, y in enumerate(YS):
            if ya <= y < yb:
                x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                lo[i] = x if np.isnan(lo[i]) else min(lo[i], x)
                hi[i] = x if np.isnan(hi[i]) else max(hi[i], x)
    b = path.bounds
    sel = (YS >= band[0]) & (YS <= band[1])
    L = np.where(np.isnan(lo[sel]), D, np.minimum(lo[sel] - b[0], D)).mean()
    R = np.where(np.isnan(hi[sel]), D, np.minimum(b[2] - hi[sel], D)).mean()
    return float(L), float(R)


def assign(depth_by_key, base, alpha=0.55, lo=38.0, hi=92.0):
    """depth_by_key: {key: (L, R)} -> {key: (lsb, rsb)}"""
    Lm = np.mean([d[0] for d in depth_by_key.values()])
    Rm = np.mean([d[1] for d in depth_by_key.values()])
    out = {}
    for k, (L, R) in depth_by_key.items():
        out[k] = (float(np.clip(base - alpha * (L - Lm), lo, hi)), float(np.clip(base - alpha * (R - Rm), lo, hi)))
    return out
