"""LOCKED test set: 20% of source videos are held out FIRST (work/locked/heldout_videos.json, written once, never changed); every later model is trained without them.
Two subsets, reported separately: representative (120 random event windows from held-out videos) and diagnostic (180: 50 serve, 50 backhand, 40 forehand, 40 other/none, chosen by the labeller's current or old label; the human decides the truth).
Blind 12-frame sheets for tagging (same page and keys as before). Run on the Mac:  python tests/lockedtest_make.py   then   HT_DIR=work/locked python tests/humantest_serve.py"""
import json, os, random, sys, collections
import cv2, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..")); sys.path.insert(0, os.path.dirname(__file__))
from sphere import labelling
from humantest_make import sheet
OUT = "work/locked"; HELD = f"{OUT}/heldout_videos.json"


def main():
    lab = json.load(open("work/stroke_labels3.json")); vids = sorted({k.split("/")[1] for k in lab})
    if os.path.exists(HELD): held = set(json.load(open(HELD)))
    else:
        rng = random.Random(21); held = set(rng.sample(vids, int(round(0.2 * len(vids))))); json.dump(sorted(held), open(HELD, "w"))
    print(len(vids), "videos,", len(held), "held out")
    pool = [k for k in lab if k.split("/")[1] in held]; rng = random.Random(22); rng.shuffle(pool)
    def fam(v):
        s = {v.get("stroke"), v.get("stroke_old")}
        return [c for c in ("backhand", "serve", "forehand") if c in s] or ["other"]
    os.makedirs(OUT + "/img", exist_ok=True); items, key, used, pv = [], {}, set(), collections.Counter()
    def add(k, subset):
        act, vid = k.split("/")[:2]; vf = labelling.video_file(f"work/{act}/videos", vid)
        if not vf: return False
        w = lab[k]["window"]; im = sheet(vf, w[0], w[1])
        if im is None: return False
        iid = f"{len(items) + 1:03d}"; cv2.imwrite(f"{OUT}/img/{iid}.jpg", im, [cv2.IMWRITE_JPEG_QUALITY, 80])
        items.append({"id": iid}); key[iid] = {"key": k, "subset": subset, "claude": lab[k]["stroke"], "old": lab[k].get("stroke_old"), "vid": vid}; used.add(k); pv[(subset, vid)] += 1; return True
    got = 0
    for k in pool:
        if got >= 120: break
        if pv[("rep", k.split("/")[1])] >= 2: continue
        got += add(k, "rep")
    print("representative", got)
    for c, q in (("serve", 50), ("backhand", 50), ("forehand", 40), ("other", 40)):
        got = 0
        for k in pool:
            if got >= q: break
            if k in used or c not in fam(lab[k]) or pv[("diag", k.split("/")[1])] >= 3: continue
            got += add(k, "diag")
        print("diagnostic", c, got, "of", q)
    random.Random(23).shuffle(items); json.dump(items, open(f"{OUT}/items.json", "w")); json.dump(key, open(f"{OUT}/key_DO_NOT_OPEN.json", "w")); print("windows", len(items))


if __name__ == "__main__":
    main()
