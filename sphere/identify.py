"""Which activity is this? Every entry knows what a typical attempt of its activity looks like (its recognition signature). Each entry finds the
attempts it can in a video; an attempt belongs to the entry whose signature it fits best, and to none when it fits no entry."""
import numpy as np
from .engine import attempts_in


FOLLOW_S = 0.4          # an attempt of another activity that starts within this long of the end of a stronger one is its follow-through


def fit(entry, arr, names):
    """How far an attempt is from the entry's typical attempt, as a share of the distance the entry allows: 1.0 or below = it fits."""
    sig = entry["recognition"]["signature"]
    idx = [names.index(f) for f in sig["features"] if f in names]
    if len(idx) != len(sig["features"]):
        return float("inf")
    mean, std = np.asarray(sig["mean"], float), np.asarray(sig["std"], float)
    x = arr[:, idx]
    return float(np.nanmean(((x - mean) / std) ** 2) / max(sig["threshold"], 1e-9))


def false_accepts(entry):
    """Share of other activities' attempts the entry wrongly accepted when it was built (None when unknown)."""
    return entry.get("recognition", {}).get("accuracy", {}).get("false_accept_rate_vs_other_activities")


MAX_FALSE_ACCEPTS = 0.2    # an entry that accepted more than this share of other activities' attempts when it was built is a draft: it is not used beside others
MIN_RECALL = 0.8


def ready(entry):
    """(True, '') when the entry is reliable enough to run beside others, else (False, why)."""
    a = entry.get("recognition", {}).get("accuracy", {})
    fa, rc = a.get("false_accept_rate_vs_other_activities"), a.get("recall")
    if fa is not None and fa > MAX_FALSE_ACCEPTS:
        return False, f"it accepted {fa:.0%} of other activities' attempts when built (the limit is {MAX_FALSE_ACCEPTS:.0%})"
    if rc is not None and rc < MIN_RECALL:
        return False, f"it recognised only {rc:.0%} of its own attempts when built (the minimum is {MIN_RECALL:.0%})"
    return True, ""


def _overlap(a, b):
    inter = max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
    return inter / max(1e-9, min(a[1] - a[0], b[1] - b[0]))


def identify(entries, clip, overlap=0.5):
    """entries: {activity: entry}. -> (owned {activity: [(start, end)]}, found [{activity, start, end, fit, owner}]) in video seconds.
    Every attempt any entry finds is listed once per entry that found it; `owner` is the activity it belongs to (None when none fits).
    An attempt goes to the entry that fits it best, a tie going to the entry that is harder to fool (see false_accepts); an attempt of
    another activity that overlaps a stronger one or starts right as it ends is its follow-through and is not counted as a swing."""
    found = []
    for act, entry in entries.items():
        names, atts = attempts_in(entry, clip)
        for a in atts:
            found.append({"activity": act, "start": a["start"], "end": a["end"], "fit": fit(entry, a["arr"], names), "owner": None})

    def score(f):
        """Higher = a better claim. None = the attempt does not fit the entry. A tie in fit goes to the entry that is harder to fool: its fit is
        weighed by how often it wrongly accepted other activities' attempts when it was built. An activity of several events in order (a serve) comes before one of a
        single event: its window holds the other's (the follow-through of a serve looks like a forehand) and its order of events is the stronger evidence."""
        if f["fit"] > 1.0:
            return None
        n_events = len(entries[f["activity"]].get("metadata", {}).get("provenance", {}).get("attempt_events", []))
        return (1.0 if n_events > 1 else 0.0) + 1.0 / (1.0 + f["fit"] * (1.0 + 2.0 * (false_accepts(entries[f["activity"]]) or 0.0)))
    claimed = []
    for f in sorted((f for f in found if score(f) is not None), key=lambda f: -score(f)):       # the surest first; a window is owned once
        if not any(_overlap((f["start"], f["end"]), (c["start"], c["end"])) > overlap for c in claimed):
            f["owner"] = f["activity"]
            claimed.append(f)
    kept, last = [], None
    for f in sorted(claimed, key=lambda f: f["start"]):          # in time: a swing of another activity that overlaps the one before it, or begins just as it ends, is its follow-through
        if last and last["activity"] != f["activity"] and (_overlap((f["start"], f["end"]), (last["start"], last["end"])) > 0.2 or f["start"] <= last["end"] + FOLLOW_S):
            f["owner"] = None
        else:
            kept.append(f); last = f
    owned = {act: [(f["start"], f["end"]) for f in kept if f["owner"] == act] for act in entries}
    return owned, sorted(found, key=lambda f: f["start"])


def accepts(owned_windows, s, e, overlap=0.5):
    return any(_overlap((s, e), w) > overlap for w in owned_windows)
