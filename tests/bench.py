"""Test bench: what the entries make of three of your own clips whose content is known.
  python tests/bench.py --clips DIR      (DIR holds the skeletons of the three videos; `python factory.py check` makes them)
Prints one table: per set of entries and per clip, the swings found, how many carry the right label, how many the wrong one, and how many
real swings were missed. Truth (from what was filmed): IMG_2935 3 = 5 serves; IMG_2935 = 5 forehands; IMG_2935 2 = 5 serves (the first 50 s), then forehands."""
import argparse, glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere.identify import identify
from sphere.skeleton import load_clip

# clip -> (skeleton file name, [(from_s, to_s, label, how many real swings, or None if not counted)])
CLIPS = {      # video name -> [(from_s, to_s, label, how many real swings there are, or None when not counted)]
    "IMG_2935 3": [(0, 1e9, "tennis_serve", 5)],
    "IMG_2935": [(0, 1e9, "tennis_forehand", 5)],
    "IMG_2935 2": [(0, 50, "tennis_serve", 5), (50, 1e9, "tennis_forehand", None)],
}
NOTE = {"IMG_2935 3": "5 serves", "IMG_2935": "5 forehands", "IMG_2935 2": "long"}


def load_entries(work, only=None):
    starts = tuple(x.strip() for x in only.split(",")) if only else ("tennis",)
    out = {}
    for d in sorted(os.listdir(work)):
        p = os.path.join(work, d, "entry.json")
        if d.startswith(starts) and os.path.exists(p):
            e = json.load(open(p))
            if e.get("recognition") and e["metadata"]["provenance"].get("attempt_events"):
                out[d] = e
    return out


def find_skeleton(clips, stem):
    for name in (stem + ".skeleton.npz", "last_debug_clip.npz" if stem == "IMG_2935" else None):
        if name and os.path.exists(os.path.join(clips, name)):
            return os.path.join(clips, name)
    return None


def score(entries, clip, truth):
    owned, found = identify(entries, clip)
    swings = sorted(((s, e, act) for act, ws in owned.items() for s, e in ws))
    rows = []
    for lo, hi, label, n in truth:
        mine = [w for w in swings if lo <= (w[0] + w[1]) / 2 < hi]
        right = [w for w in mine if w[2] == label]
        rows.append({"label": label, "n": n, "found": len(mine), "right": len(right), "wrong": len(mine) - len(right),
                     "missed": (max(0, n - len(right)) if n else None), "wrong_labels": sorted({w[2] for w in mine if w[2] != label})})
    return swings, rows


def report(work, clips):
    """The table (a list of lines): per set of entries and per clip, the swings found and how many carry the right label."""
    from sphere.identify import ready
    everything = load_entries(work)
    configs = [("serve + forehand", {k: v for k, v in everything.items() if k in ("tennis_serve", "tennis_forehand")}),
               ("as the coach loads tennis", {k: v for k, v in everything.items() if ready(v)[0]}),
               ("all seven, drafts included", everything)]
    out = [f"{'entries':28s}{'clip':24s}{'expected':>14s}{'found':>6s}{'right':>6s}{'wrong':>6s}{'missed':>7s}  wrong labels"]
    for cname, entries in configs:
        tot = [0, 0, 0]
        for stem, truth in CLIPS.items():
            p = find_skeleton(clips, stem)
            label = f"{stem} ({NOTE[stem]})"
            if not p:
                out.append(f"{cname:28s}{label:24s}  (skeleton not found)"); continue
            swings, rows = score(entries, load_clip(p), truth)
            for r in rows:
                exp = f"{r['n'] if r['n'] else 'some'} {r['label'].replace('tennis_', '')}"
                out.append(f"{cname:28s}{label:24s}{exp:>14s}{r['found']:>6d}{r['right']:>6d}{r['wrong']:>6d}{(r['missed'] if r['missed'] is not None else '-'):>7}  {', '.join(r['wrong_labels'])}")
                if r["n"]:
                    tot[0] += r["right"]; tot[1] += r["wrong"]; tot[2] += r["missed"]
        out.append(f"{cname:28s}{'swings that count (5+5+5)':24s}{'15':>14s}{'':>6s}{tot[0]:>6d}{tot[1]:>6d}{tot[2]:>7d}\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="work"); ap.add_argument("--clips", required=True, help="folder with the skeletons of the three videos")
    a = ap.parse_args()
    print("\n".join(report(a.work, a.clips)))


if __name__ == "__main__":
    main()
