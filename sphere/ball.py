"""Ball finding in tennis video, offline (no real-time limit): detector candidates + motion candidates, linked into parabolic tracks.

  Detector  : YOLOX (COCO, ONNX) -> persons and 'sports ball' candidates, run on the full frame and on a crop around the player.
  Motion    : 3-frame differencing inside the crop -> small bright/yellow-green blobs.
  link()    : finds the best parabola (x linear, y quadratic in time) through the candidates of consecutive frames = a ball in flight.
Nothing here is specific to one shot: a ball in flight follows a parabola whatever the stroke.
"""
import json, os, subprocess
import numpy as np
import cv2

PERSON, BALL = 0, 32


def probe(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,codec_name",
                          "-of", "json", video], capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(n) / float(d)


def display_size(video):
    """Width, height of a decoded frame (phones store 4K video sideways and tag it rotated: ffmpeg turns it upright)."""
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    h, w = cv2.imdecode(np.frombuffer(out, np.uint8), 1).shape[:2]
    return w, h


def frames(video, t0, dur, max_side=1280):
    """Yield (time_s, BGR frame) for [t0, t0+dur) at the video's own frame rate, upright, the longer side at most max_side pixels.
    ffmpeg decodes every codec we meet (AV1 too)."""
    w, h = display_size(video)
    fps = probe(video)[2]
    k = min(1.0, max_side / max(w, h))
    ow, oh = int(w * k) // 2 * 2, int(h * k) // 2 * 2
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{max(t0, 0):.3f}", "-i", video, "-t", f"{dur:.3f}", "-vf", f"scale={ow}:{oh}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    i = 0
    while True:
        buf = p.stdout.read(ow * oh * 3)
        if len(buf) < ow * oh * 3:
            break
        yield max(t0, 0) + i / fps, np.frombuffer(buf, np.uint8).reshape(oh, ow, 3)
        i += 1
    p.stdout.close(); p.wait()


RACKET = 38      # COCO ids are used for every model: person 0, sports ball 32, tennis racket 38
_V8_NAMES = {"player": PERSON, "person": PERSON, "tennis ball": BALL, "ball": BALL, "racket": RACKET, "racquet": RACKET}


class Detector:
    """YOLOX (COCO, 85 columns) or a YOLOv8 export (4 box columns + classes, names in the model's metadata) run through ONNX Runtime.
    Either way the classes come out as COCO ids (person 0, sports ball 32, tennis racket 38)."""
    def __init__(self, path, threads=4):
        import onnxruntime as ort
        so = ort.SessionOptions(); so.intra_op_num_threads = threads
        self.s = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        self.v8 = None
        shp = self.s.get_outputs()[0].shape
        if len(shp) == 3 and shp[1] < shp[2] and shp[1] != 85:
            import ast
            names = ast.literal_eval(self.s.get_modelmeta().custom_metadata_map.get("names", "{}"))
            self.v8 = {int(k): _V8_NAMES.get(str(v).lower()) for k, v in names.items()}
        self.size = 640
        g = []
        for st in (8, 16, 32):
            n = self.size // st
            xv, yv = np.meshgrid(np.arange(n), np.arange(n))
            g.append((np.stack((xv, yv), 2).reshape(-1, 2), np.full((n * n, 1), st)))
        self.grids = np.concatenate([a for a, _ in g]); self.strides = np.concatenate([b for _, b in g]).astype(np.float32)

    def run(self, img, conf=0.05, classes=(PERSON, BALL, RACKET)):
        """-> list of (cls, score, x0, y0, x1, y1) in img pixels."""
        H, W = img.shape[:2]
        r = min(self.size / H, self.size / W)
        nh, nw = int(H * r), int(W * r)
        canvas = np.full((self.size, self.size, 3), 114, np.uint8)
        canvas[:nh, :nw] = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
        x = canvas.transpose(2, 0, 1)[None].astype(np.float32)
        o = self.s.run(None, {self.s.get_inputs()[0].name: x / (255.0 if self.v8 else 1.0)})[0][0]
        if self.v8:
            o = o.T                    # (8400, 4 + classes)
            res = []
            for k, cid in self.v8.items():
                if cid is None or cid not in classes:
                    continue
                sc = o[:, 4 + k]
                for j in np.where(sc > conf)[0]:
                    cx, cy, w, h = o[j, :4]
                    res.append((cid, float(sc[j]), (cx - w / 2) / r, (cy - h / 2) / r, (cx + w / 2) / r, (cy + h / 2) / r))
            return _nms(res)
        xy = (o[:, :2] + self.grids) * self.strides
        wh = np.exp(o[:, 2:4]) * self.strides
        obj = o[:, 4:5]; cls = o[:, 5:] * obj
        res = []
        for c in classes:
            sc = cls[:, c]
            for k in np.where(sc > conf)[0]:
                cx, cy = xy[k]; w, h = wh[k]
                res.append((c, float(sc[k]), (cx - w / 2) / r, (cy - h / 2) / r, (cx + w / 2) / r, (cy + h / 2) / r))
        return _nms(res)


def _nms(res, iou=0.45):
    out = []
    for c in {r[0] for r in res}:
        rs = sorted((r for r in res if r[0] == c), key=lambda r: -r[1])
        keep = []
        for r in rs:
            ok = True
            for k in keep:
                ix = max(0, min(r[4], k[4]) - max(r[2], k[2])); iy = max(0, min(r[5], k[5]) - max(r[3], k[3]))
                inter = ix * iy
                u = (r[4] - r[2]) * (r[5] - r[3]) + (k[4] - k[2]) * (k[5] - k[3]) - inter
                if u > 0 and inter / u > iou:
                    ok = False; break
            if ok:
                keep.append(r)
        out += keep
    return out


def player_box(dets, prev=None):
    """The player = the largest confident person (the one the video is about); the previous box breaks ties between two people."""
    ps = [d for d in dets if d[0] == PERSON and d[1] > 0.3]
    if not ps:
        return prev
    if prev is not None:
        pcx, pcy = (prev[0] + prev[2]) / 2, (prev[1] + prev[3]) / 2
        ps.sort(key=lambda d: -(d[1] * 0.5 + 1.0 / (1 + np.hypot((d[2] + d[4]) / 2 - pcx, (d[3] + d[5]) / 2 - pcy) / 50.0)))
    else:
        ps.sort(key=lambda d: -(d[4] - d[2]) * (d[5] - d[3]) * d[1])
    d = ps[0]
    return (d[2], d[3], d[4], d[5])


def roi_of(box, W, H, up=2.8, side=1.3, down=0.15):
    """Where a served ball can be: around the player, up to ~2.8 body heights above the feet."""
    x0, y0, x1, y1 = box
    h = y1 - y0; cx = (x0 + x1) / 2
    X0, X1 = int(max(0, cx - side * h)), int(min(W, cx + side * h))
    Y0, Y1 = int(max(0, y1 - up * h)), int(min(H, y1 + down * h))
    return X0, Y0, X1, Y1


def motion_candidates(prev, cur, nxt, roi, max_area=60, bright=True, min_area=2):
    """Small blobs that moved between three consecutive frames and are bright or yellow-green (a tennis ball), inside roi."""
    X0, Y0, X1, Y1 = roi
    g = [cv2.cvtColor(f[Y0:Y1, X0:X1], cv2.COLOR_BGR2GRAY).astype(np.int16) for f in (prev, cur, nxt)]
    d = np.minimum(np.abs(g[1] - g[0]), np.abs(g[1] - g[2])).astype(np.uint8)
    m = (d > 25).astype(np.uint8)
    hsv = cv2.cvtColor(cur[Y0:Y1, X0:X1], cv2.COLOR_BGR2HSV)
    yg = ((hsv[..., 0] >= 20) & (hsv[..., 0] <= 50) & (hsv[..., 1] > 60) & (hsv[..., 2] > 120))
    bright_px = hsv[..., 2] > 200
    m = m & ((yg | bright_px) if bright else yg).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
    out = []
    for i in range(1, n):
        a = st[i, cv2.CC_STAT_AREA]
        if min_area <= a <= max_area:
            out.append((float(X0 + cen[i][0]), float(Y0 + cen[i][1]), float(a)))
    return out


def link(cands, times, min_inliers=6, tol=None, iters=2500, seed=0):
    """cands: list per frame of (x, y, score). times: seconds per frame.
    Best ballistic track: x = x0 + vx t, y = y0 + vy t + a t^2 (image y grows downward, so a > 0 for an upright camera).
    -> dict(frames, pts, a, apex_t, apex_y, inliers) or None."""
    rng = np.random.default_rng(seed)
    T = np.asarray(times, float)
    pts = [(i, x, y, s) for i, cs in enumerate(cands) for (x, y, s) in cs]
    if len(pts) < min_inliers:
        return None
    pts = np.array(pts)
    tt = T[pts[:, 0].astype(int)]
    tol = tol or 4.0
    best = None
    idx = np.arange(len(pts))
    for _ in range(iters):
        k = rng.choice(idx, 3, replace=False)
        if len(set(pts[k, 0])) < 3:
            continue
        t = tt[k]
        try:
            cy = np.polyfit(t, pts[k, 2], 2); cx = np.polyfit(t, pts[k, 1], 1)
        except Exception:
            continue
        if cy[0] <= 0:
            continue
        ex = np.abs(np.polyval(cx, tt) - pts[:, 1]); ey = np.abs(np.polyval(cy, tt) - pts[:, 2])
        inl = (ex < tol) & (ey < tol)
        nfr = len(set(pts[inl, 0]))
        if best is None or nfr > best[0]:
            best = (nfr, inl)
    if best is None or best[0] < min_inliers:
        return None
    inl = best[1]
    cy = np.polyfit(tt[inl], pts[inl, 2], 2); cx = np.polyfit(tt[inl], pts[inl, 1], 1)
    ex = np.abs(np.polyval(cx, tt) - pts[:, 1]); ey = np.abs(np.polyval(cy, tt) - pts[:, 2])
    inl = (ex < tol) & (ey < tol)
    fr = sorted(set(pts[inl, 0].astype(int)))
    ta = -cy[1] / (2 * cy[0])
    return {"cx": cx.tolist(), "cy": cy.tolist(), "n": len(fr), "a": float(cy[0]), "apex_t": float(ta), "apex_y": float(np.polyval(cy, ta)),
            "frames": fr, "t0": float(T[fr[0]]), "t1": float(T[fr[-1]]), "pts": pts[inl][:, 1:3].tolist()}


def is_ball_coloured(img, x, y, r=4):
    """Tennis-ball yellow-green in a small patch around (x, y): rejects orange rackets, white lines, shirts, sky."""
    H, W = img.shape[:2]
    x0, x1, y0, y1 = int(max(0, x - r)), int(min(W, x + r + 1)), int(max(0, y - r)), int(min(H, y + r + 1))
    if x1 <= x0 or y1 <= y0:
        return False
    hsv = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
    m = (hsv[..., 0] >= 22) & (hsv[..., 0] <= 48) & (hsv[..., 1] > 70) & (hsv[..., 2] > 110)
    return float(m.mean()) >= 0.12


def drop_static(cands, tol=3.0, share=0.35):
    """A ball in flight does not stay put: a candidate that reappears at the same place in many frames is a ball on the ground, a logo or a graphic."""
    n = len(cands)
    out = []
    for i, cs in enumerate(cands):
        keep = []
        for (x, y, s) in cs:
            same = sum(any(abs(x - a) < tol and abs(y - b) < tol for (a, b, _) in cands[j]) for j in range(n) if j != i)
            if same < share * n:
                keep.append((x, y, s))
        out.append(keep)
    return out


def shot_cuts(imgs, thr=22.0):
    """Indices where the picture changes completely (a cut between cameras, a graphic): the player's place and the scale change there."""
    small = [cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (64, 36)).astype(np.float32) for f in imgs]
    return [i for i in range(1, len(small)) if float(np.abs(small[i] - small[i - 1]).mean()) > thr]


def detect_tiled(det, img, box, conf=0.03, ball_px=12.0, max_scale=4.0):
    """Ball candidates around the player, with the picture enlarged so that a ball is about ball_px wide (a ball is 0.035 body heights):
    the region is cut into overlapping 640 px tiles. -> list of (x, y, score) in img pixels, and the region used."""
    H, W = img.shape[:2]
    ph = box[3] - box[1]
    roi = roi_of(box, W, H)
    X0, Y0, X1, Y1 = roi
    sc = float(np.clip(ball_px / max(1.0, 0.035 * ph), 1.0, max_scale))
    crop = cv2.resize(img[Y0:Y1, X0:X1], None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    h, w = crop.shape[:2]
    step = 520
    xs = list(range(0, max(1, w - 640 + step), step)) if w > 640 else [0]
    ys = list(range(0, max(1, h - 640 + step), step)) if h > 640 else [0]
    out = []
    for ty in ys:
        for tx in xs:
            tile = crop[ty:ty + 640, tx:tx + 640]
            for r in det.run(tile, conf=conf, classes=(BALL,)):
                out.append((X0 + (tx + (r[2] + r[4]) / 2) / sc, Y0 + (ty + (r[3] + r[5]) / 2) / sc, r[1]))
    return out, roi


def steady_boxes(pb, n):
    """pb: {frame: box or None} for some frames -> a box for every frame. A box whose height is far from the median is a wrong person: dropped, then interpolate."""
    ks = sorted(k for k in pb if pb[k] is not None)
    if not ks:
        return None
    med = float(np.median([pb[k][3] - pb[k][1] for k in ks]))
    ks = [k for k in ks if 0.7 * med < pb[k][3] - pb[k][1] < 1.4 * med] or ks
    return [tuple(float(np.interp(i, ks, [pb[k][j] for k in ks])) for j in range(4)) for i in range(n)]


def extend_track(tr, raw, times, tol):
    """Fill the frames a track skipped: wherever any candidate (even one that failed the colour test) lies within 2 tol of the arc, take it."""
    T = np.asarray(times, float)
    fr = tr["frames"]; cx, cy = tr["cx"], tr["cy"]
    got = set(fr); add = []
    for i in range(fr[0], fr[-1] + 1):
        if i in got:
            continue
        px, py = np.polyval(cx, T[i]), np.polyval(cy, T[i])
        near = [c for c in raw[i] if abs(c[0] - px) < 2 * tol and abs(c[1] - py) < 2 * tol]
        if near:
            got.add(i); add.append((i, near[0][0], near[0][1]))
    return sorted(got), add


def motion_blobs(prev, cur, nxt, roi, min_area, max_area, thr=12):
    """Every small blob that changed against both neighbouring frames, whatever its colour: the candidates a learned classifier will sort into ball and not ball.
    -> list of (x, y, area) in image pixels."""
    X0, Y0, X1, Y1 = roi
    g = [cv2.cvtColor(f[Y0:Y1, X0:X1], cv2.COLOR_BGR2GRAY).astype(np.int16) for f in (prev, cur, nxt)]
    d = np.minimum(np.abs(g[1] - g[0]), np.abs(g[1] - g[2])).astype(np.uint8)
    m = (d > thr).astype(np.uint8)
    m = cv2.dilate(m, np.ones((2, 2), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
    return [(float(X0 + cen[i][0]), float(Y0 + cen[i][1]), float(st[i, cv2.CC_STAT_AREA])) for i in range(1, n) if min_area <= st[i, cv2.CC_STAT_AREA] <= max_area]


def colour_blobs(cur, roi, min_area, max_area):
    """Small yellow-green blobs, moving or not (the toss slows to a stop at its apex, where frame differencing loses the ball)."""
    X0, Y0, X1, Y1 = roi
    hsv = cv2.cvtColor(cur[Y0:Y1, X0:X1], cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 0] >= 18) & (hsv[..., 0] <= 52) & (hsv[..., 1] > 50) & (hsv[..., 2] > 70)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
    return [(float(X0 + cen[i][0]), float(Y0 + cen[i][1]), float(st[i, cv2.CC_STAT_AREA])) for i in range(1, n) if min_area <= st[i, cv2.CC_STAT_AREA] <= max_area]


def union_blobs(a, b, tol=2.5):
    out = list(a)
    for (x, y, ar) in b:
        if not any(abs(x - u) < tol and abs(y - v) < tol for (u, v, _) in a):
            out.append((x, y, ar))
    return out


def link_soft(cands, times, ph, min_frames=5, tol=None, iters=4000, seed=0, a_range=(0.4, 2.0)):
    """Soft, physics-constrained arc: cands = per frame (x, y, p) with many weak candidates kept. A hypothesis (x linear, y quadratic in time)
    is scored by the summed log-odds of the best candidate near it in every frame, and its acceleration must be about gravity for a ball of this
    scale (player height ph px = ~1.75 m): a in a_range x (g/2 px/s^2). -> dict like link() plus 'score', or None."""
    rng = np.random.default_rng(seed); T = np.asarray(times, float)
    pts = np.array([(i, x, y, p) for i, cs in enumerate(cands) for (x, y, p) in cs], float)
    if len(pts) < min_frames: return None
    tt = T[pts[:, 0].astype(int)]; fi = pts[:, 0].astype(int); tol = tol or max(3.0, 0.012 * ph)
    w = np.log(np.clip(pts[:, 3], 1e-3, 0.999) / (1 - np.clip(pts[:, 3], 1e-3, 0.999))) + 4.0   # log-odds, offset: a weak blob still counts a little
    w = np.maximum(w, 0.0); g2 = 0.5 * 9.81 * ph / 1.75; lo, hi = a_range[0] * g2, a_range[1] * g2
    nf = len(T); best = (0.0, None); idx = np.arange(len(pts))
    for _ in range(iters):
        k = rng.choice(idx, 3, replace=False)
        if len(set(fi[k])) < 3: continue
        try: cy = np.polyfit(tt[k], pts[k, 2], 2); cx = np.polyfit(tt[k], pts[k, 1], 1)
        except Exception: continue
        if not (lo <= cy[0] <= hi): continue
        inl = (np.abs(np.polyval(cx, tt) - pts[:, 1]) < tol) & (np.abs(np.polyval(cy, tt) - pts[:, 2]) < tol)
        if inl.sum() < min_frames: continue
        sc = np.zeros(nf); np.maximum.at(sc, fi[inl], w[inl]); tot = float(sc.sum())
        if tot > best[0]: best = (tot, inl)
    if best[1] is None: return None
    inl = best[1]
    for _ in range(2):   # refit on the best candidate per frame
        sel = [np.where(inl & (fi == f))[0][np.argmax(w[inl & (fi == f)])] for f in sorted(set(fi[inl]))]
        if len(sel) < min_frames: return None
        cy = np.polyfit(tt[sel], pts[sel, 2], 2); cx = np.polyfit(tt[sel], pts[sel, 1], 1)
        if not (lo <= cy[0] <= hi): return None
        inl = (np.abs(np.polyval(cx, tt) - pts[:, 1]) < tol) & (np.abs(np.polyval(cy, tt) - pts[:, 2]) < tol)
    fr = sorted(set(fi[inl].tolist())); ta = -cy[1] / (2 * cy[0]); sc = np.zeros(nf); np.maximum.at(sc, fi[inl], w[inl])
    return {"cx": cx.tolist(), "cy": cy.tolist(), "n": len(fr), "a": float(cy[0]), "apex_t": float(ta), "apex_y": float(np.polyval(cy, ta)), "frames": fr,
            "t0": float(T[fr[0]]), "t1": float(T[fr[-1]]), "pts": pts[inl][:, 1:3].tolist(), "score": float(sc.sum())}


def camera_shifts(imgs, boxes=None, width=320):
    """Cumulative camera translation (dx, dy) per frame in pixels of the full image, from phase correlation of the background (player box masked).
    Used to fit the ball's arc in stabilised coordinates when the camera pans or tilts."""
    import cv2
    H, W = imgs[0].shape[:2]; s = width / W; win = None; out = [(0.0, 0.0)]; prev = None
    for i, im in enumerate(imgs):
        g = cv2.cvtColor(cv2.resize(im, (width, int(H * s))), cv2.COLOR_BGR2GRAY).astype(np.float32)
        if boxes is not None:
            b = boxes[min(i, len(boxes) - 1)]; x0, y0, x1, y1 = [int(v * s) for v in (b[0] - 0.2 * (b[2] - b[0]), b[1] - 0.1 * (b[3] - b[1]), b[2] + 0.2 * (b[2] - b[0]), b[3])]
            g[max(y0, 0):y1, max(x0, 0):x1] = g.mean()
        if win is None: win = cv2.createHanningWindow((g.shape[1], g.shape[0]), cv2.CV_32F)
        if prev is not None:
            (dx, dy), resp = cv2.phaseCorrelate(prev, g, win); dx, dy = (dx / s, dy / s) if resp > 0.05 else (0.0, 0.0)
            out.append((out[-1][0] + dx, out[-1][1] + dy))
        prev = g
    return out
