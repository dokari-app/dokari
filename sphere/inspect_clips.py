"""Diagnostic picture: for every clip, the attempt-event signals over time with the attempts the factory found.
Lets a human see at a glance whether a clip really contains clean repetitions and how deep they go."""
import glob
import os
import numpy as np
from .skeleton import load_clip
from .features import compute_features, FEATURES
from .segment import segment_attempts


def inspect(clips_dir, out_png, events, cols=3, primary=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    paths = sorted(glob.glob(os.path.join(clips_dir, "*.npz")))
    if not paths:
        raise SystemExit(f"no clips in {clips_dir}")
    ev_idx = [FEATURES.index(e["feature"]) for e in events]
    rows = int(np.ceil(len(paths) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 2.6 * rows), squeeze=False)
    for ax in axes.ravel():
        ax.axis("off")
    for ax, p in zip(axes.ravel(), paths):
        clip = load_clip(p)
        names, F, info = compute_features(clip)
        seg = segment_attempts(F, clip["fps"], names, events, primary)
        t = np.arange(len(F)) / clip["fps"]
        ax.axis("on")
        for j, e in zip(ev_idx, events):
            ax.plot(t, F[:, j], lw=0.8, label=f"{e['feature']} ({e['direction']})")
        v = seg["valid"]
        i = 0
        while i < len(v):
            if not v[i]:
                j = i
                while j < len(v) and not v[j]:
                    j += 1
                ax.axvspan(i / clip["fps"], j / clip["fps"], color="grey", alpha=0.25, lw=0)
                i = j
            else:
                i += 1
        for a, b in seg["attempts"]:
            ax.axvspan(a / clip["fps"], b / clip["fps"], color="green", alpha=0.18)
        ax.set_title(f"{clip['meta'].get('id')}  {len(seg['attempts'])} attempts, "
                     f"believable {round(100 * seg['valid_share'])}%", fontsize=8)
        ax.tick_params(labelsize=7)
    axes[0][0].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(out_png, dpi=90)
    return out_png
