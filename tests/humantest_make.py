"""Build the human-verified test set: ~300 windows, blind (labels hidden), as 12-frame contact sheets.
Run on the Mac (needs cv2 + the downloaded videos).  python tests/humantest_make.py"""
import json, os, random, sys, collections
import cv2, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sphere import labelling

OUT = "work/humantest"; K = 12; W = 480; COLS = 4
QUOTA = {"forehand": 90, "backhand": 90, "serve": 50, "none": 50, "other": 20}
PER_VIDEO = 3
OTHER = {"volley", "smash", "slice", "lob", "drop_shot", "other"}

def cls(s): return s if s in QUOTA else ("other" if s in OTHER else None)

def sheet(vf, t0, t1):
    cap = cv2.VideoCapture(vf); fr_ = []
    for i in range(K):
        t = t0 + (t1 - t0) * i / (K - 1)
        cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * t); ok, f = cap.read()
        if not ok: cap.release(); return None
        h, w = f.shape[:2]; f = cv2.resize(f, (W, int(h * W / w)), interpolation=cv2.INTER_AREA)
        cv2.putText(f, str(i + 1), (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        fr_.append(f)
    cap.release()
    hh = max(f.shape[0] for f in fr_)
    fr_ = [cv2.copyMakeBorder(f, 0, hh - f.shape[0], 0, 0, cv2.BORDER_CONSTANT) for f in fr_]
    rows = [np.hstack(fr_[r * COLS:(r + 1) * COLS]) for r in range(K // COLS)]
    return np.vstack(rows)

def main():
    random.seed(7)
    d = json.load(open("work/stroke_labels3.json"))
    pools = collections.defaultdict(list)
    for key, v in d.items():
        c = cls(v.get("stroke"))
        if c: pools[c].append(key)
    os.makedirs(OUT + "/img", exist_ok=True)
    items, keyfile, n = [], {}, 0
    for c, q in QUOTA.items():
        ks = pools[c][:]; random.shuffle(ks); got = 0; pv = collections.Counter()
        for key in ks:
            if got >= q: break
            act, vid = key.split("/")[:2]
            if pv[vid] >= PER_VIDEO: continue
            vf = labelling.video_file(f"work/{act}/videos", vid)
            if not vf: continue
            w = d[key]["window"]; im = sheet(vf, w[0], w[1])
            if im is None: continue
            n += 1; iid = f"{n:03d}"
            cv2.imwrite(f"{OUT}/img/{iid}.jpg", im, [cv2.IMWRITE_JPEG_QUALITY, 80])
            items.append({"id": iid}); keyfile[iid] = {"key": key, "claude": d[key]["stroke"], "conf": d[key].get("confidence"), "vid": vid, "t": w}
            pv[vid] += 1; got += 1
        print(c, got, "of", q, flush=True)
    random.shuffle(items)
    json.dump(items, open(f"{OUT}/items.json", "w"))
    json.dump(keyfile, open(f"{OUT}/key_DO_NOT_OPEN.json", "w"))
    print("windows:", len(items))

if __name__ == "__main__":
    main()
