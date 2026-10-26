"""Image-plane pose (MediaPipe 2D landmarks, not the estimated-depth world pose) for every labelled stroke window, 12 frames per second.
Free, Mac only, resumable (safe to stop and restart).   python tests/pose2d_extract.py
Writes work/pose2d.pkl : key -> (T, 13, 3) array [x/H, y/H, visibility] for nose, shoulders, elbows, wrists, hips, knees, ankles + times."""
import json, os, pickle, random, sys, time, collections
import numpy as np
sys.path.insert(0, ".")
JOINTS = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
OUT = "work/pose2d.pkl"; FPS = 12


def work(job):
    import cv2, mediapipe as mp
    from mediapipe.tasks import python as mpp
    from mediapipe.tasks.python import vision
    from sphere import extract
    items = job
    lm = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=extract.ensure_model("full")), running_mode=vision.RunningMode.IMAGE, num_poses=3))
    out = {}
    for key, vf, w0, w1 in items:
        cap = cv2.VideoCapture(vf); ts = np.arange(w0, w1, 1.0 / FPS); arr = np.full((len(ts), 13, 3), np.nan)
        for i, t in enumerate(ts):
            cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * max(0, t)); ok, fr = cap.read()
            if not ok: continue
            h, w = fr.shape[:2]; res = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)))
            if not res.pose_landmarks: continue
            best = max(res.pose_landmarks, key=lambda p: max(q.y for q in p) - min(q.y for q in p))
            arr[i] = [[best[j].x * w / h, best[j].y, best[j].visibility] for j in JOINTS]
        cap.release(); out[key] = (ts, arr)
    return out


def main():
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import multiprocessing as mpc
    from sphere import labelling
    lab = json.load(open("work/stroke_labels3.json")); rng = random.Random(2)
    done = pickle.load(open(OUT, "rb")) if os.path.exists(OUT) else {}
    sel = collections.defaultdict(list)
    for k, v in lab.items():
        s = "no_stroke" if v["stroke"] == "none" else v["stroke"]
        sel[s].append(k)
    keys = []
    for s, L in sel.items():
        rng.shuffle(L); keys += L[:700] if s == "no_stroke" else L
    todo = [k for k in keys if k not in done]
    jobs = collections.defaultdict(list)
    for k in todo:
        act, vid = k.split("/")[:2]; vf = labelling.video_file(f"work/{act}/videos", vid)
        if vf: jobs[vid].append((k, vf, *lab[k]["window"]))
    chunks = [v for v in jobs.values()]
    print("windows selected", len(keys), "| to do", sum(len(c) for c in chunks), "| videos", len(chunks), flush=True)
    t0 = time.time(); n = 0
    with ProcessPoolExecutor(3, mp_context=mpc.get_context("spawn")) as ex:
        futs = [ex.submit(work, c) for c in chunks]
        for f in as_completed(futs):
            done.update(f.result()); n += 1
            if n % 10 == 0 or n == len(futs):
                pickle.dump(done, open(OUT + ".tmp", "wb")); os.replace(OUT + ".tmp", OUT)
                print(f"  {n}/{len(futs)} videos, {len(done)} windows, {(time.time()-t0)/60:.0f} min", flush=True)
    pickle.dump(done, open(OUT + ".tmp", "wb")); os.replace(OUT + ".tmp", OUT); print("done", len(done))


if __name__ == "__main__":
    main()
