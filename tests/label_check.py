"""A6 + A3: does the labelling call name the stroke correctly on your own clips (truth known)?
  python tests/label_check.py [--videos ~/Desktop/SPHERE]
Takes every swing the entries find in your three clips, shows 6 frames of it to the vision model (the same call the factory uses) and compares the stroke it names
with what was filmed. Writes work/label_check.md (table) and work/label_check.png (contact sheet: every swing, its frames, what the model said)."""
import argparse, base64, json, os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cv2, numpy as np
from sphere import labelling
from sphere.identify import identify
from sphere.skeleton import load_clip
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench
ap = argparse.ArgumentParser(); ap.add_argument("--videos", default="~/Desktop/SPHERE"); a = ap.parse_args()
W = "work"; folder = os.path.expanduser(a.videos); clips = os.path.join(W, "check", "as_filmed")
entries = {k: v for k, v in bench.load_entries(W).items() if k in ("tennis_serve", "tennis_forehand")}
files = {os.path.splitext(f)[0]: os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith((".mov", ".mp4"))}
rows, sheet = [], []
for stem, truth in bench.CLIPS.items():
    sk = bench.find_skeleton(clips, stem)
    if not sk or stem not in files: print("skip", stem); continue
    owned, _ = identify(entries, load_clip(sk))
    wins = sorted((s, e) for ws in owned.values() for s, e in ws)
    frames = [labelling.grab_frames(files[stem], s, e) for s, e in wins]
    got = labelling.ask_labels("tennis", [], wins, frames, "")
    for n, ((s, e), fr) in enumerate(zip(wins, frames), 1):
        t = next(lbl for lo, hi, lbl, _ in truth if lo <= (s + e) / 2 < hi).replace("tennis_", "").replace("_", " ")
        g = got.get(n) or {}
        rows.append((stem, round(s, 1), round(e, 1), t, g.get("stroke", "(no answer)"), g.get("view_clean"), g.get("not_an_attempt")))
        sheet.append((f"{stem} {s:.0f}-{e:.0f}s: truth {t} | model {g.get('stroke', '-')}" + (" NOT-ATTEMPT" if g.get("not_an_attempt") else ""), fr[0]))
ok = [r for r in rows if r[3] in r[4] or r[4] in r[3] and r[4] != "(no answer)"]
by = collections.Counter((r[3], r[4]) for r in rows)
md = [f"# Label check {len(rows)} swings: stroke named correctly {len(ok)} ({100 * len(ok) // max(1, len(rows))}%)", "", "truth -> model: count"]
md += [f"- {t} -> {m}: {c}" for (t, m), c in sorted(by.items())]
md += ["", f"view judged clean: {sum(1 for r in rows if r[5])} of {len(rows)}; judged not an attempt: {sum(1 for r in rows if r[6])}", "", "| clip | from | to | truth | model | clean | not attempt |", "|---|---|---|---|---|---|---|"]
md += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |" for r in rows]
open(os.path.join(W, "label_check.md"), "w").write("\n".join(md)); print("\n".join(md[:12]))
tiles = []
for cap, fr in sheet[:30]:
    ims = [cv2.imdecode(np.frombuffer(base64.b64decode(b), np.uint8), 1) for b in fr]
    ims = [cv2.resize(i, (150, int(i.shape[0] * 150 / i.shape[1]))) for i in ims]; h = max(i.shape[0] for i in ims)
    row = np.concatenate([np.pad(i, ((0, h - i.shape[0]), (0, 0), (0, 0))) for i in ims], 1); bar = np.full((22, row.shape[1], 3), 255, np.uint8)
    cv2.putText(bar, cap[:95], (3, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1); tiles.append(np.concatenate([bar, row], 0))
if tiles:
    w = max(t.shape[1] for t in tiles); cv2.imwrite(os.path.join(W, "label_check.png"), np.concatenate([np.pad(t, ((0, 0), (0, w - t.shape[1]), (0, 0)), constant_values=255) for t in tiles], 0))
print("written work/label_check.md and work/label_check.png")
