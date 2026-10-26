"""Overnight ball loop. One command, resumable (rerun continues), nothing needs a person.
  python tests/ball_night.py [--act work/tennis_serve] [--hours 7] [--judge-threads 4] [--fake-judge]
Stages (each skips what is already done):
  1 windows  frames around each shot of the videos on disk (sphere/ballwin.py, OpenCV)          -> <act>/ballwin/*.win.pkl
  2 features player boxes (YOLOX), blobs and patches per frame                                   -> work/ball_night/feat/<window>.npz
  3 judge    the current model ranks the blobs; the 40 best crops of 10 frames go to the vision judge
             (sphere/balljudge.py, calibrated against hand-judged crops) -> blob labels                -> work/ball_night/lab/<window>.npz
  4 gate     videos are split 70/30 by hash. Model A (all data accepted so far) vs model B (A + tonight's train split) are compared on
             the test split of every night so far (the test split is never trained on). B becomes the model only if it is not worse.
  5 arcs     soft arc with player context on every window with the model in force; judged-ball windows vs tosses found
  6 report   work/ball_night/report.md + samples.png (random judged balls and random rejected candidates, to glance at)
Needs: scikit-learn, onnxruntime, ANTHROPIC_API_KEY (stage 3), models/yolox_m.onnx."""
import argparse, glob, hashlib, json, os, pickle, random, sys, time
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, HERE)
from sphere import ball, ballwin
from ball_dataset import examples
from ball_train import feats
ROOT = "work/ball_night"; T = 190; COLS, ROWS = 6, 4


ACTS = []
def wpath(tag):
    for a in ACTS + sorted(glob.glob("work/tennis_*")):          # the activities of this run first, then every other one (windows of earlier runs)
        f = f"{a}/ballwin/{tag}.win.pkl"
        if os.path.exists(f): return f
    raise FileNotFoundError(tag)

from sphere.localfile import is_local

def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a); print(s, flush=True); open(f"{ROOT}/log.txt", "a").write(s + "\n")

def is_test(video): return int(hashlib.md5(video.encode()).hexdigest(), 16) % 10 < 3          # 30% of videos
def video_of(tag): return tag.rsplit("_", 1)[0]
def state():
    return json.load(open(f"{ROOT}/state.json")) if os.path.exists(f"{ROOT}/state.json") else {"accepted": [], "history": []}
def save_state(s): json.dump(s, open(f"{ROOT}/state.json", "w"), indent=1)


# ---------------------------------------------------------------- 1 windows
def stage_windows(act, deadline):
    n = 0
    for sk in sorted(glob.glob(f"{act}/clips/*.npz")):
        vid = os.path.basename(sk)[:-4]; mark = f"{act}/ballwin/{vid}.done"
        if os.path.exists(mark): continue
        vp = [p for p in glob.glob(f"{act}/videos/{vid}.*") if not p.endswith(".part") and is_local(p)]
        if not vp: continue
        if time.time() > deadline: log("windows: deadline"); return
        try:
            from sphere.skeleton import load_clip
            k = ballwin.save(vp[0], vid, load_clip(sk), act); n += k
        except Exception as e: log("windows failed", vid, str(e)[:80]); k = 0
        os.makedirs(f"{act}/ballwin", exist_ok=True); open(mark, "w").write(str(k))
    log("windows done;", n, "new,", len(glob.glob(f"{act}/ballwin/*.win.pkl")), "in all")


# ---------------------------------------------------------------- 2 features
def stage_features(act, deadline):
    os.makedirs(f"{ROOT}/feat", exist_ok=True); det = None; n = 0
    for f in sorted(glob.glob(f"{act}/ballwin/*.win.pkl")):
        if not is_local(f): continue
        tag = os.path.basename(f)[:-8]; o = f"{ROOT}/feat/{tag}.npz"
        if os.path.exists(o) or os.path.exists(o + ".skip"): continue
        if time.time() > deadline: log("features: deadline"); return
        try:
            w = ballwin.load(f); imgs, times, tc = w["imgs"], w["times"], w["t_contact"]
            if det is None: det = ball.Detector("models/yolox_m.onnx")
            cuts = ball.shot_cuts(imgs); ic = int(np.argmin([abs(t - tc) for t in times]))
            lo = max([c for c in cuts if c <= ic], default=0); hi = min([c for c in cuts if c > ic], default=len(imgs)); imgs, times = imgs[lo:hi], times[lo:hi]
            if len(imgs) < 12: open(o + ".skip", "w").write("short"); continue
            pb, prev = {}, None
            for i in range(0, len(imgs), 3):
                prev = ball.player_box(det.run(imgs[i], conf=0.2, classes=(ball.PERSON,)), prev); pb[i] = prev
            boxes = ball.steady_boxes(pb, len(imgs))
            if boxes is None: open(o + ".skip", "w").write("no player"); continue
            z = examples(imgs, boxes, {}, 0)
            if len(z["y"]) == 0: open(o + ".skip", "w").write("no blobs"); continue
            H, W = imgs[0].shape[:2]
            np.savez_compressed(o, **{k: np.asarray(v) for k, v in z.items()}, boxes=np.array(boxes), times=np.array(times), lo=lo, HW=np.array([H, W]), t_contact=tc); n += 1
            if n % 10 == 0: log("features:", n, "windows")
        except Exception as e: log("features failed", tag, str(e)[:80])
    log("features done;", n, "new,", len(glob.glob(f"{ROOT}/feat/*.npz")), "in all")


# ---------------------------------------------------------------- models
def base_parts():
    """Everything that is trusted before tonight: phone clips + composites (12% of their negatives), judged YouTube blobs, background negatives."""
    r = np.random.default_rng(0); X, y, w = [], [], []
    for d in ("work/ball_data", "work/ball_comp"):
        for f in sorted(glob.glob(f"{d}/*.npz")):
            z = dict(np.load(f)); F = feats(z); m = (z["y"] == 1) | (r.random(len(F)) < 0.12); X.append(F[m]); y.append(z["y"][m]); w.append(np.ones(m.sum()))
    for f in sorted(glob.glob("work/ball_yt/*.npz")):
        z = dict(np.load(f)); F = feats(z); m = z["y"] >= 0
        if m.any(): X.append(F[m]); y.append(z["y"][m]); w.append(np.where(z["y"][m] == 1, 3.0, 1.0))
    if os.path.exists("work/ball_bgneg_feats.npy"):
        mm = np.load("work/ball_bgneg_feats.npy", mmap_mode="r"); B = np.asarray(mm[np.sort(r.choice(len(mm), min(40000, len(mm)), replace=False))]); X.append(B); y.append(np.zeros(len(B), int)); w.append(np.ones(len(B)))
    return X, y, w

def lab_parts(tags):
    X, y, w = [], [], []
    for t in tags:
        f = f"{ROOT}/lab/{t}.npz"
        if not os.path.exists(f): continue
        z = dict(np.load(f)); F = feats(z); m = z["y"] >= 0
        if m.any(): X.append(F[m]); y.append(z["y"][m]); w.append(np.where(z["y"][m] == 1, 3.0, 1.0))
    return X, y, w

def fit(parts):
    from sklearn.ensemble import HistGradientBoostingClassifier
    X, y, w = parts; X = np.concatenate(X); y = np.concatenate(y).astype(int); w = np.concatenate(w)
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, max_leaf_nodes=15, l2_regularization=1.0, class_weight={0: 1.0, 1: 5.0}, random_state=0).fit(X, y, sample_weight=w)

def rank_stats(clf, tags):
    """Rank of the judged ball among the labelled blobs of its frame, over the given windows."""
    ranks = []
    for t in tags:
        f = f"{ROOT}/lab/{t}.npz"
        if not os.path.exists(f): continue
        z = dict(np.load(f)); p = clf.predict_proba(feats(z))[:, 1]
        for fr in sorted(set(z["frame"][z["y"] == 1].tolist())):
            m = (z["frame"] == fr) & (z["y"] >= 0); yv = z["y"][m]
            ranks.append(1 + int((p[m][yv == 0] > p[m][yv == 1].max()).sum()))
    return np.array(ranks)


# ---------------------------------------------------------------- 3 judge
def crops_for(tag, clf, act, nf=10, top=4):
    z = dict(np.load(f"{ROOT}/feat/{tag}.npz")); H, W = [int(v) for v in z["HW"]]; lo = int(z["lo"]); p = clf.predict_proba(feats(z))[:, 1]
    w = ballwin.load(wpath(tag)); imgs = w["imgs"][lo:lo + len(z["times"])]; d = 0.035 * float(z["ph"]); crops = []
    for fr in np.linspace(2, len(imgs) - 3, nf).astype(int):
        m = np.where(z["frame"] == fr)[0]
        for k in m[np.argsort(-p[m])][:top]: crops.append((int(fr), int(k), float(z["xy"][k][0] * W), float(z["xy"][k][1] * H), float(p[k])))
    tiles = [make_tile(imgs[fr], x, y, d, str(n)) for n, (fr, k, x, y, pk) in enumerate(crops)]
    return z, crops, tiles, d

def make_tile(img, x, y, d, label):
    H, W = img.shape[:2]; r = int(max(24, 3.2 * d)); x0, y0 = int(round(x - r)), int(round(y - r)); pad = np.zeros((2 * r, 2 * r, 3), np.uint8)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + 2 * r, W), min(y0 + 2 * r, H)
    pad[ya - y0:yb - y0, xa - x0:xb - x0] = img[ya:yb, xa:xb]; t = cv2.resize(pad, (T, T), interpolation=cv2.INTER_CUBIC)
    cv2.circle(t, (T // 2, T // 2), int(T * d / (2 * r)) + 5, (0, 0, 255), 1); cv2.putText(t, label, (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    return t

def grids_of(tiles):
    out = []
    for g in range(0, len(tiles), COLS * ROWS):
        grid = np.zeros((ROWS * T, COLS * T, 3), np.uint8)
        for j, t in enumerate(tiles[g:g + COLS * ROWS]): grid[(j // COLS) * T:(j // COLS + 1) * T, (j % COLS) * T:(j % COLS + 1) * T] = t
        out.append(grid)
    return out

def stage_judge(act, clf, deadline, threads, fake):
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(f"{ROOT}/lab", exist_ok=True); os.makedirs(f"{ROOT}/judged", exist_ok=True); os.makedirs(f"{ROOT}/tmp", exist_ok=True)
    todo = [os.path.basename(f)[:-4] for f in sorted(glob.glob(f"{ROOT}/feat/*.npz")) if not os.path.exists(f"{ROOT}/lab/{os.path.basename(f)[:-4]}.npz") and is_local(wpath(os.path.basename(f)[:-4]))]
    log("judge:", len(todo), "windows to judge")
    client = None
    if not fake:
        import anthropic; client = anthropic.Anthropic(timeout=45.0, max_retries=1); from sphere import balljudge

    def one(tag):
        if time.time() > deadline: return None
        if not is_local(wpath(tag)): return tag, None        # evicted since the list was made: leave it for a later run
        z, crops, tiles, d = crops_for(tag, clf, act); yes = {}; ok = True
        for gi, grid in enumerate(grids_of(tiles)):
            if fake: continue
            pth = f"{ROOT}/tmp/{tag}_{gi}.png"; cv2.imwrite(pth, grid); r = balljudge.judge_grid(pth, client=client)
            if r is None: ok = False; break
            yes.update(r)
        if not ok: return tag, None
        return tag, (z, crops, yes, d)

    done = 0
    with ThreadPoolExecutor(threads) as ex:
        from concurrent.futures import as_completed
        for res in (f.result() for f in as_completed([ex.submit(one, t) for t in todo])):   # in any order, so one slow window cannot hold up the rest
            if res is None or res[1] is None: continue
            tag, (z, crops, yes, d) = res; H, W = [int(v) for v in z["HW"]]; xy = z["xy"] * np.array([W, H], np.float32); y = np.full(len(z["frame"]), -1, np.int8); rad = max(4.0, 0.8 * d + 2)
            yes_frames = {crops[i][0] for i in yes if i < len(crops)}
            for fr in {c[0] for c in crops}:
                m = z["frame"] == fr
                if fr in yes_frames:
                    y[m] = 0
                    for i in yes:
                        if i < len(crops) and crops[i][0] == fr: y[m & (np.hypot(xy[:, 0] - crops[i][2], xy[:, 1] - crops[i][3]) < rad)] = 1
                else:
                    for (cf, k, cx, cy, pk) in crops:
                        if cf == fr: y[m & (np.hypot(xy[:, 0] - cx, xy[:, 1] - cy) < rad) & (y != 1)] = 0
            zz = {k: np.asarray(v) for k, v in z.items()}; zz["y"] = y; np.savez_compressed(f"{ROOT}/lab/{tag}.npz", **zz)
            json.dump({"crops": crops, "d": d, "lo": int(z["lo"]), "yes": {str(k): v for k, v in yes.items()}}, open(f"{ROOT}/judged/{tag}.json", "w"))
            done += 1
            if done % 10 == 0: log("judge:", done, "windows judged")
    log("judge done;", done, "new windows")


# ---------------------------------------------------------------- 4 gate
def stage_gate(s, new_tags, state_out):
    prior = [t for t in s["accepted"]]; test_all = s.get("test", [])
    new_train = [t for t in new_tags if not is_test(video_of(t))]; new_test = [t for t in new_tags if is_test(video_of(t))]
    test_all = sorted(set(test_all + new_test))
    log(f"gate: {len(new_train)} new train windows, {len(new_test)} new test windows ({len(test_all)} test windows in all)")
    parts = base_parts(); lp0 = lab_parts(prior); A = fit((parts[0] + lp0[0], parts[1] + lp0[1], parts[2] + lp0[2]))
    rA = rank_stats(A, test_all); verdict = {"test_frames": int(len(rA)), "A_top1": float(np.mean(rA == 1)) if len(rA) else None, "A_top3": float(np.mean(rA <= 3)) if len(rA) else None}
    have_ball = [t for t in new_train if (np.load(f"{ROOT}/lab/{t}.npz")["y"] == 1).any()]
    model = A; promoted = False
    if len(have_ball) >= 3 and len(rA) >= 15:
        la, lb, lc = lab_parts(prior + new_train); B = fit((parts[0] + la, parts[1] + lb, parts[2] + lc)); rB = rank_stats(B, test_all)
        verdict.update({"B_top1": float(np.mean(rB == 1)), "B_top3": float(np.mean(rB <= 3))})
        if np.mean(rB == 1) >= np.mean(rA == 1) and np.mean(rB <= 3) >= np.mean(rA <= 3) - 0.02:
            model = B; promoted = True; s["accepted"] = sorted(set(prior + new_train))
    verdict["promoted"] = promoted; verdict["new_train_windows_with_ball"] = len(have_ball)
    s["test"] = test_all; s["history"].append({"time": time.strftime("%Y-%m-%d %H:%M"), **verdict}); save_state(s)
    log("gate:", json.dumps(verdict)); return model, verdict


# ---------------------------------------------------------------- 5 arcs
def context_filter(cs, b):
    h = b[3] - b[1]; cx = (b[0] + b[2]) / 2; keep = []
    for (x, y, p) in cs:
        inbox = b[0] - 0.1 * h <= x <= b[2] + 0.1 * h and b[1] <= y <= b[3] + 0.1 * h
        if inbox and (y > b[1] + 0.55 * h or abs(x - cx) < 0.22 * h and y > b[1] + 0.2 * h): continue
        keep.append((x, y, p))
    return keep

def stage_arcs(clf, tags):
    rows = []
    for t in tags:
        z = dict(np.load(f"{ROOT}/feat/{t}.npz")); H, W = [int(v) for v in z["HW"]]; times = z["times"]; B = z["boxes"]; ph = float(z["ph"]); p = clf.predict_proba(feats(z))[:, 1]
        cands = [[] for _ in times]
        for k in np.where(p > 0.03)[0]: cands[int(z["frame"][k])].append((float(z["xy"][k][0] * W), float(z["xy"][k][1] * H), float(p[k])))
        cands = [context_filter(cs, B[min(i, len(B) - 1)]) for i, cs in enumerate(cands)]
        tr = ball.link_soft(cands, list(times), ph, min_frames=5, tol=3 * max(3.0, 0.012 * ph)); toss = False   # tol x3, score >= 40: 7/12 moving tosses, 1/31 false (22 Oct sweep)
        if tr:
            x0, y0 = tr["pts"][0]; b0 = B[min(tr["frames"][0], len(B) - 1)]; h0 = b0[3] - b0[1]; cx0 = (b0[0] + b0[2]) / 2
            start = abs(x0 - cx0) < 0.6 * h0 + (b0[2] - b0[0]) / 2 and b0[1] - 0.3 * h0 <= y0 <= b0[1] + 0.8 * h0
            travel = float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) / ph; apex = (float(np.median(B[:, 1])) - tr["apex_y"]) / ph
            toss = bool(start and travel >= 0.2 and apex >= 0.15 and tr["t1"] - tr["t0"] >= 0.2 and tr["score"] >= 40)
        jf = f"{ROOT}/judged/{t}.json"; seen = 0
        if os.path.exists(jf):
            j = json.load(open(jf)); seen = len({j["crops"][int(i)][0] for i, k in j["yes"].items() if k == "free" and int(i) < len(j["crops"])})
        rows.append({"window": t, "toss_found": toss, "judged_free_ball_frames": seen})
    return rows


# ---------------------------------------------------------------- 6 report
def stage_report(s, verdict, rows, model, act):
    present = [r for r in rows if r["judged_free_ball_frames"] >= 4]; absent = [r for r in rows if r["judged_free_ball_frames"] == 0]
    rec = [r for r in present if r["toss_found"]]
    lines = [f"# Ball night report {time.strftime('%Y-%m-%d %H:%M')}", "",
             f"- windows with features: {len(rows)}; with a judged free ball in >=4 frames: {len(present)}; with none judged: {len(absent)}",
             f"- toss recovered in {len(rec)} of {len(present)} windows with a judged ball (and {sum(r['toss_found'] for r in absent)} of {len(absent)} windows without a judged ball: possible false tosses)",
             f"- gate: {json.dumps(verdict)}", f"- history: {len(s['history'])} nights; accepted train windows {len(s['accepted'])}; test windows {len(s.get('test', []))}", ""]
    open(f"{ROOT}/report.md", "w").write("\n".join(lines)); log("report written")
    # samples to glance at
    random.seed(0); tiles = []
    ys, ns = [], []
    for jf in glob.glob(f"{ROOT}/judged/*.json"):
        t = os.path.basename(jf)[:-5]; j = json.load(open(jf)); ys += [(t, int(i)) for i in j["yes"]]; ns += [(t, i) for i in range(len(j["crops"])) if str(i) not in j["yes"]]
    cache = {}
    for name, pool in (("yes", ys), ("no", ns)):
        for t, i in random.sample(pool, min(24, len(pool))):
            try:
                j = json.load(open(f"{ROOT}/judged/{t}.json"))
                if t not in cache: cache = {t: ballwin.load(wpath(t))["imgs"]}
                fr, k, x, y, pk = j["crops"][i]; tt = make_tile(cache[t][j["lo"] + fr], x, y, j["d"], name)
                cv2.putText(tt, f"{j['yes'].get(str(i), '')}", (4, T - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2); tiles.append(tt)
            except Exception as e: log("sample failed", t, str(e)[:60])
    if tiles: cv2.imwrite(f"{ROOT}/samples.png", np.vstack([np.hstack(g) for g in [tiles[i:i + 6] + [np.zeros_like(tiles[0])] * (6 - len(tiles[i:i + 6])) for i in range(0, len(tiles), 6)]]))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--act", default="work/tennis_serve"); ap.add_argument("--hours", type=float, default=7.0)
    ap.add_argument("--judge-threads", type=int, default=4); ap.add_argument("--fake-judge", action="store_true"); ap.add_argument("--root", default="work/ball_night"); a = ap.parse_args()
    global ROOT; ROOT = a.root
    os.makedirs(ROOT, exist_ok=True); t0 = time.time(); deadline = t0 + a.hours * 3600; log("night starts;", a.act, f"{a.hours} h budget")
    if not a.fake_judge and not os.environ.get("ANTHROPIC_API_KEY"): sys.exit("ANTHROPIC_API_KEY is not set in this window")
    ACTS.extend(a.act.split(","))
    for act in ACTS: stage_windows(act, deadline); stage_features(act, deadline)
    s = state(); parts = base_parts(); lp = lab_parts(s["accepted"]); clf = fit((parts[0] + lp[0], parts[1] + lp[1], parts[2] + lp[2])); log("current model trained")
    before = set(os.path.basename(f)[:-4] for f in glob.glob(f"{ROOT}/lab/*.npz"))
    stage_judge(ACTS[0], clf, deadline, a.judge_threads, a.fake_judge)
    new = sorted(set(os.path.basename(f)[:-4] for f in glob.glob(f"{ROOT}/lab/*.npz")) - before)
    # windows labelled in an earlier, interrupted run that never went through the gate
    seen = set(s["accepted"]) | set(s.get("test", [])); new = sorted(set(new) | (set(os.path.basename(f)[:-4] for f in glob.glob(f"{ROOT}/lab/*.npz")) - seen))
    model, verdict = stage_gate(s, new, None)
    rows = stage_arcs(model, [os.path.basename(f)[:-4] for f in sorted(glob.glob(f"{ROOT}/feat/*.npz"))]); json.dump(rows, open(f"{ROOT}/arcs.json", "w"))
    stage_report(state(), verdict, rows, model, a.act); log(f"night finished in {(time.time() - t0) / 60:.0f} min")


if __name__ == "__main__":
    main()
