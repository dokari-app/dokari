"""Ball tracking test on serve videos, with automatic truth.
  python tests/ball_bench.py --videos DIR --skeletons DIR --model yolox_m.onnx --out work/ball [--max-per-video 2]
Truth comes from the skeleton: the serve entry finds each serve (identify), the highest wrist is the moment of contact, and a served
ball must have been thrown up before it. A serve counts as 'toss found' when a ballistic track of >= 6 frames, whose apex is above the
player's head, is found in the second before contact. Control: windows of the same length where no serve happens; a track found there
that meets the same test is a false alarm. Methods: det_full (detector on the whole frame), det_crop (detector on a crop around the
player, enlarged), motion (frame differencing in the crop), all (the union)."""
import argparse, glob, json, os, sys, time
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere import ball
from sphere.identify import identify
from sphere.skeleton import load_clip, J

PRE, POST = 1.2, 0.2


def serve_windows(entry, skel):
    clip = load_clip(skel)
    owned, _ = identify({"tennis_serve": entry}, clip)
    P = clip["pose"]; fps = clip["fps"]; out = []
    for s, e in owned["tennis_serve"]:
        a, b = int(s * fps), min(int(e * fps) + 1, len(P))
        wr = np.nanmax(np.stack([P[a:b, J["l_wrist"], 1], P[a:b, J["r_wrist"], 1]]), axis=0)
        out.append((s, e, (a + int(np.nanargmax(wr))) / fps))
    return out, len(P) / fps


def detect_window(det, video, t_contact, pdet=None):
    """The slow part: decode, find the player, find ball candidates. Everything the scoring needs is returned (and cached by the caller)."""
    W, H, fps = ball.probe(video)
    t0 = max(0.0, t_contact - PRE); dur = PRE + POST
    fr = list(ball.frames(video, t0, dur))
    if len(fr) < 12:
        return None
    times = [t for t, _ in fr]; imgs = [f for _, f in fr]
    cuts = ball.shot_cuts(imgs)
    ic = int(np.argmin([abs(t - t_contact) for t in times]))
    lo = max([c for c in cuts if c <= ic], default=0); hi = min([c for c in cuts if c > ic], default=len(imgs))
    times, imgs = times[lo:hi], imgs[lo:hi]
    if len(imgs) < 12:
        return {"skipped": "shot too short (cut)"}
    pb, prev = {}, None
    for i in range(0, len(imgs), 3):
        prev = ball.player_box((pdet or det).run(imgs[i], conf=0.2, classes=(ball.PERSON,)), prev); pb[i] = prev
    boxes = ball.steady_boxes(pb, len(imgs))
    if boxes is None:
        return None
    raw, mot, rois, col = [], [], [], []
    for i, f in enumerate(imgs):
        c, roi = ball.detect_tiled(det, f, boxes[i], ball_px=9.0); rois.append(roi)
        raw.append([(x, y, s_) for x, y, s_ in c])
        col.append([ball.is_ball_coloured(f, x, y) for x, y, s_ in c])
        mot.append([(x, y, 1.0) for x, y, a_ in ball.motion_candidates(imgs[i - 1], f, imgs[i + 1], roi)] if 0 < i < len(imgs) - 1 else [])
    return {"times": times, "boxes": boxes, "rois": rois, "raw": raw, "col": col, "mot": mot, "imgs": imgs}


def score_window(d, t_contact, min_inliers=5, fill=True, use_colour=True, min_score=0.1, methods=None):
    """Cheap: from the candidates to the tracks and the verdict. Rerun freely while tuning."""
    times, boxes, rois, imgs = d["times"], d["boxes"], d["rois"], d["imgs"]
    ph = float(np.median([b[3] - b[1] for b in boxes]))
    top = float(np.median([b[1] for b in boxes])); cxm = float(np.median([(b[0] + b[2]) / 2 for b in boxes]))
    sets = {"det_tiled": [[c for c in cs if c[2] >= min_score and (not use_colour or ball.is_ball_coloured(imgs[i], c[0], c[1]))] for i, cs in enumerate(d["raw"])], "motion": d["mot"]}
    sets["all"] = [a + b for a, b in zip(sets["det_tiled"], sets["motion"])]
    out, tracks = {}, {}
    for name, cands in sets.items():
        if methods and name not in methods:
            continue
        inroi = lambda c, i: rois[i][0] <= c[0] <= rois[i][2] and rois[i][1] <= c[1] <= rois[i][3]
        def not_body(c, i):
            # the player's own torso and shorts (a yellow-green trim, a logo) move with him: not a ball
            b = boxes[i]; h = b[3] - b[1]; cx = (b[0] + b[2]) / 2
            return not (abs(c[0] - cx) < 0.22 * h and b[1] + 0.2 * h < c[1] < b[1] + 0.62 * h)
        flt = ball.drop_static([[c for c in cs if inroi(c, i) and not_body(c, i)] for i, cs in enumerate(cands)])
        tol = max(3.0, 0.012 * ph)
        tr = ball.link(flt, times, min_inliers=min_inliers, tol=tol)
        if tr and fill:
            rawall = [[c for c in cs if inroi(c, i)] for i, cs in enumerate([a + b for a, b in zip(d["raw"], d["mot"])])]
            fr, add = ball.extend_track(tr, rawall, times, tol)
            tr["frames"] = fr; tr["n"] = len(fr); tr["pts"] = tr["pts"] + [(x, y) for _, x, y in add]
        above = sum(any(c[1] < boxes[i][1] + 0.1 * ph and abs(c[0] - cxm) < 0.6 * ph for c in cs) for i, cs in enumerate(flt))
        # a toss may leave the picture: the ascent alone (>= 5 frames, 0.15 s) with the arc's apex above the head counts
        # ... and it must really travel (a logo, a graphic, a sign that the camera pans past hardly moves): >= 0.3 body heights along the track
        moved = bool(tr) and float(np.hypot(np.ptp([p[0] for p in tr["pts"]]), np.ptp([p[1] for p in tr["pts"]]))) >= 0.3 * ph
        ok = bool(tr and moved and tr["apex_y"] < top - 0.15 * ph and tr["t1"] - tr["t0"] >= 0.15 and tr["n"] >= 0.5 * (tr["frames"][-1] - tr["frames"][0] + 1))
        out[name] = {"above_head_frames": above, "frames": len(flt), "toss_found": ok,
                     "track": None if tr is None else {**{k: tr[k] for k in ("n", "a", "apex_t", "apex_y", "t0", "t1")}, "first": tr["frames"][0], "last": tr["frames"][-1]}}
        tracks[name] = tr
    return {"player_h": ph, "methods": out}, tracks


def annotate(d, tracks, t_contact, path):
    imgs, times, rois = d["imgs"], d["times"], d["rois"]
    X0, Y0, X1, Y1 = rois[len(rois) // 2]
    scale = 480.0 / max(X1 - X0, Y1 - Y0)
    size = (int((X1 - X0) * scale) // 2 * 2, int((Y1 - Y0) * scale) // 2 * 2)
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), 8.0, size)
    tr = tracks.get("all") or tracks.get("det_tiled")
    for i, f in enumerate(imgs):
        c = cv2.resize(f[Y0:Y1, X0:X1], None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        for (x, y, s_), k in zip(d["raw"][i], d["col"][i]):
            cv2.circle(c, (int((x - X0) * scale), int((y - Y0) * scale)), 8, (0, 200, 255) if (k and s_ >= 0.1 and ball.is_ball_coloured(imgs[i], x, y)) else (150, 150, 150), 1)
        if tr:
            for (px, py) in tr["pts"]:
                cv2.circle(c, (int((px - X0) * scale), int((py - Y0) * scale)), 3, (0, 255, 0), -1)
        cv2.putText(c, f"{times[i]-t_contact:+.2f}s", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        vw.write(cv2.resize(c, size))
    vw.release()


def process(det, video, t_contact, tag, outdir, pdet=None):
    import pickle
    os.makedirs(outdir, exist_ok=True)
    cache = os.path.join(outdir, tag + ".cache.pkl")
    if os.path.exists(cache):
        d = pickle.load(open(cache, "rb"))
    else:
        d = detect_window(det, video, t_contact, pdet)
        if d is not None and "skipped" not in d:
            pickle.dump(d, open(cache, "wb"))
    if d is None:
        return None
    if "skipped" in d:
        return {"tag": tag, "video": os.path.basename(video), "t_contact": t_contact, "skipped": d["skipped"], "methods": {}}
    res, tracks = score_window(d, t_contact)
    annotate(d, tracks, t_contact, os.path.join(outdir, tag + ".mp4"))
    return {"tag": tag, "video": os.path.basename(video), "t_contact": t_contact, **res}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True); ap.add_argument("--skeletons", required=True)
    ap.add_argument("--entry", default="work/tennis_serve/entry.json"); ap.add_argument("--model", default=os.path.expanduser("~/models/yolox_m.onnx"))
    ap.add_argument("--out", default="work/ball"); ap.add_argument("--max-per-video", type=int, default=2)
    ap.add_argument("--person-model", default=os.path.expanduser("~/models/yolox_m.onnx"), help="finds the player (the ball model's own player class gives boxes that are too large)"); ap.add_argument("--only", default=None, help="comma-separated video ids"); ap.add_argument("--budget", type=float, default=1e9, help="stop starting new windows after this many seconds (rerun to continue)")
    a = ap.parse_args()
    entry = json.load(open(a.entry)); det = ball.Detector(a.model); pdet = ball.Detector(a.person_model)
    ids = [x.strip() for x in a.only.split(",")] if a.only else [os.path.basename(p)[:-4] for p in sorted(glob.glob(os.path.join(a.videos, "*.mp4")))]
    t_start = time.time()
    rpath = os.path.join(a.out, "ball_results.json"); os.makedirs(a.out, exist_ok=True)
    results = json.load(open(rpath)) if os.path.exists(rpath) else []
    done = {r["tag"] for r in results}
    for vid in ids:
        v = os.path.join(a.videos, vid + ".mp4"); sk = os.path.join(a.skeletons, vid + ".npz")
        if not (os.path.exists(v) and os.path.exists(sk)):
            continue
        wins, dur = serve_windows(entry, sk)
        print(f"{vid}: {len(wins)} serves found in {dur:.0f}s", flush=True)
        pos = [w[2] for w in wins if w[2] >= PRE][:a.max_per_video]
        # control: moments at least 4 s away from any serve
        rng = np.random.default_rng(1); neg = []
        for _ in range(60):
            t = float(rng.uniform(PRE, max(PRE + 1, dur - 1)))
            if all(abs(t - w[2]) > 4.0 for w in wins) and len(neg) < max(1, len(pos)):
                neg.append(t)
        for kind, ts in (("serve", pos), ("control", neg)):
            for k, t in enumerate(ts):
                if f"{vid}_{kind}{k}" in done:
                    continue
                if time.time() - t_start > a.budget:
                    print("budget used; rerun to continue"); break
                t1 = time.time()
                r = process(det, v, t, f"{vid}_{kind}{k}", a.out, pdet)
                if r:
                    r["kind"] = kind; results.append(r)
                    if r.get("skipped"):
                        print(f"  {kind} {t:6.1f}s  skipped: {r['skipped']}"); continue
                    print(f"  {kind} {t:6.1f}s  " + "  ".join(f"{m}:{'TOSS' if x['toss_found'] else '-'}({x['above_head_frames']}/{x['frames']})" for m, x in r["methods"].items()) + f"  [{time.time()-t1:.0f}s]", flush=True)
        json.dump(results, open(os.path.join(a.out, "ball_results.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("\nmethod      serves with toss found   control with false toss   frames with a ball above the head: serves / controls (mean share)")
    for m in ("det_tiled", "motion", "all"):
        s = [r for r in results if r["kind"] == "serve" and r.get("methods")]; c = [r for r in results if r["kind"] == "control" and r.get("methods")]
        print(f"{m:10s}  {sum(r['methods'][m]['toss_found'] for r in s if r.get('methods'))}/{len(s)}                    {sum(r['methods'][m]['toss_found'] for r in c if r.get('methods'))}/{len(c)}                 "
              f"{np.mean([r['methods'][m]['above_head_frames']/r['methods'][m]['frames'] for r in s]) if s else 0:.2f} / {np.mean([r['methods'][m]['above_head_frames']/r['methods'][m]['frames'] for r in c]) if c else 0:.2f}")


if __name__ == "__main__":
    main()
