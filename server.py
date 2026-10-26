#!/usr/bin/env python3
"""Skill Sphere coaching server: a phone (or anything else) sends a video and gets the coaching back.

  python server.py                       start it on this computer (it prints the address and the token to give the phone)
  python server.py --only tennis         only the tennis entries of the library are tried

  GET  /                                 the coaching page for a phone's browser (open the link the server prints)
  GET  /health                           {"ok": true, "activities": [...]}
  POST /coach?only=tennis&language=English&offline=0
       header  X-Token: <the token printed at start>
       body    the video file itself (any format OpenCV reads: mov, mp4)
       answer  {"seconds": 252, "found": [...], "attempts": [...], "events": [...]}
               found    every swing seen and what it looks like (activity, fit, whether it was taken)
               attempts the coached attempts, with each objective ok / missed / unknown
               events   what is said and when (t in seconds): cues, praise, principles

  POST /joints?only=tennis&name=...
       header  X-Token
       body    {"fps": 30, "tracker": "...", "pose": frames x 17 x 3, "vis": frames x 17}  (the phone read the body itself; no video is sent)
       answer  the same as /coach

  POST /live?id=<session>&activity=auto&language=English&offline=0
       header  X-Token
       body    {"fps": 30, "start": <number of the first frame>, "pose": frames x 17 x 3, "vis": frames x 17}   (a few frames at a time, from a live camera)
       answer  {"events": [{"t", "kind", "text", "attempt_end", ...}],     what to say now (usually empty)
                "swings": [{"activity", "start", "end", "judged_at", "missed": [...]}]}   every swing recognised in this batch
  POST /live/end?id=<session>      judges what ended last, saves the session log, answers like /live

One video at a time. The wording of cues is done by a language model when ANTHROPIC_API_KEY is set where the server runs.
When the server is started with --only, that choice wins over any "only" a client sends."""
import argparse, json, os, secrets, socket, sys, tempfile, threading
from argparse import Namespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import time

import coach

BUSY = threading.Lock()                                   # pose reading is heavy: one video at a time
JOB = {"stage": "", "since": 0.0}                         # what the video being analysed is doing now, and since when


def stage(text):
    """Say what the server is doing, so a stuck analysis shows where it is stuck."""
    JOB["stage"] = text
    print(f"  [{time.time() - JOB['since']:5.0f} s] {text}", flush=True)


def prepare_language_model():
    """Load the language model library (slow on some computers) in the background, and make sure a call to it for the wording can never
    hold the server for minutes. Runs in its own thread so the server starts at once."""
    t0 = time.time()
    try:
        import anthropic
        original = anthropic.Anthropic.__init__

        def quick(self, *a, **kw):
            kw.setdefault("timeout", 20.0)
            kw.setdefault("max_retries", 1)
            original(self, *a, **kw)
        anthropic.Anthropic.__init__ = quick
        print(f"  (language model library loaded in {time.time() - t0:.0f} s)", flush=True)
    except Exception as e:
        print(f"  (language model library not loaded: {e})", flush=True)


def analyse(clip, entries, language="English", offline=False):
    """Coaching of one skeleton clip by every entry given. Returns the answer as a plain dict."""
    from sphere.identify import identify
    _, found = identify(entries, clip)
    events, log = coach.coach_all(entries, clip, Namespace(language=language, offline=offline))
    return {
        "seconds": round(len(clip["pose"]) / clip["fps"], 1),
        "found": [{"start": round(f["start"], 2), "end": round(f["end"], 2), "activity": f["activity"],
                   "fit": round(float(f["fit"]), 2), "taken": f["owner"] == f["activity"]} for f in found],
        "attempts": log,
        "events": events,
    }


def analyse_video(path, only=None, language="English", offline=False, model="full"):
    from sphere.extract import extract_video
    entries = coach.load_all_entries(only)
    stage("reading the body positions from the video")
    clip = extract_video(path, {"source": "server"}, variant=model)
    if clip is None:
        return {"error": "The person could not be followed in this video (too little of the body found)."}
    stage("recognising the swings and coaching")
    out = analyse(clip, entries, language, offline)
    stage("done")
    return out


def describe(path):
    """Size and make-up of a video, to see what a phone really sent (a phone may shrink or re-encode a video before sending it)."""
    import cv2
    cap = cv2.VideoCapture(path)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps, n = cap.get(cv2.CAP_PROP_FPS) or 0.0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join(chr((fourcc >> (8 * i)) & 0xFF) for i in range(4)).strip() or "?"
    cap.release()
    return f"{w}x{h}, {fps:.1f} fps, {n} frames, {(n / fps if fps else 0):.1f} s, codec {codec}"


def clip_from_joints(raw, name=None):
    """The body positions a phone has already read from its own camera (see PoseTracker.swift) -> a skeleton clip, saved beside the others
    so it can be compared with the Mac's own reading of the same video. Returns the clip, or a text saying what is wrong with it."""
    import numpy as np
    from sphere.skeleton import make_clip, save_clip, JOINTS
    try:
        d = json.loads(raw)
        pose, vis, fps = np.asarray(d["pose"], float), np.asarray(d["vis"], float), float(d["fps"])
        if pose.ndim != 3 or pose.shape[1:] != (len(JOINTS), 3) or vis.shape != pose.shape[:2] or not (1.0 <= fps <= 240.0):
            return f"the joints have the wrong shape (expected frames x {len(JOINTS)} x 3, got {list(pose.shape)})"
    except Exception as e:
        return f"the joints could not be read ({type(e).__name__}: {str(e)[:100]})"
    if len(pose) < 10:
        return "too few frames"
    rate = float((vis.mean(1) > 0.4).mean())
    meta = {"source": "phone", "tracker": str(d.get("tracker", "?")), "detect_rate": round(rate, 3), "n_frames": int(len(pose))}
    clip = make_clip(pose, vis, fps, meta)
    folder = os.path.join(coach.WORK, "phone")
    os.makedirs(folder, exist_ok=True)
    safe = "".join(c for c in (name or time.strftime("joints_%Y%m%d_%H%M%S")) if c.isalnum() or c in "-_ ")[:60] or "joints"
    save_clip(os.path.join(folder, safe + ".skeleton.npz"), clip)
    print(f"  kept the joints: {os.path.join(folder, safe)}.skeleton.npz", flush=True)
    if rate < 0.7:
        return "The person could not be followed in this video (too little of the body found)."
    return clip


LIVE = {}                                                  # session id -> {"session", "lock", "seen", "activity"}
LIVE_LOCK = threading.Lock()


WARM = {}                                                  # (activity, language) -> {key: [lines]}: sentences written before they are needed
WARM_LOCK = threading.Lock()


def start_warm(entry, activity, language, offline=False):
    """Begin writing the sentences of an activity in the background (once). Returns the store they go into, or None without a language model."""
    from sphere.engine import Wording
    if coach.make_wording(entry, language, offline).client is None:
        return None
    key = (activity, language)
    with WARM_LOCK:
        store = WARM.get(key)
        first = store is None
        if first:
            store = WARM[key] = {}
    if first:
        def write(k, decisions):
            w = coach.make_wording(entry, language, offline)           # its own, so repeats are counted from the start
            store[k] = [Wording.say(w, d) for d in decisions]
        jobs = []
        for o in entry["objectives"]:
            for side in o["sides"]:
                d = {"kind": "cue", "objective": o["id"], "side": side}
                jobs.append((("cue", o["id"], side), [d, d]))
            jobs.append((("praise", o["id"]), [{"kind": "praise", "objective": o["id"], "side": None}]))

        def run_all():
            from concurrent.futures import ThreadPoolExecutor
            t0 = time.time()
            with ThreadPoolExecutor(max_workers=8) as ex:
                list(ex.map(lambda j: write(*j), jobs))
            print(f"  (sentences for {activity} written in {time.time() - t0:.0f} s)", flush=True)
        threading.Thread(target=run_all, daemon=True).start()
    return store


def fast_wording(entry, activity, language, offline):
    """Wording for a live camera. Writing a sentence with the language model takes seconds, which would be said late. So the sentences
    (the first reminder, one repeat, and a praise for every objective) are written in the background when the server starts,
    and said from there; anything not written yet falls back to writing it on the spot."""
    from sphere.engine import Wording
    base = coach.make_wording(entry, language, offline)
    store = start_warm(entry, activity, language, offline)
    if store is None:
        return base

    class Fast(Wording):
        used = {}

        def say(self, decision):
            if decision["kind"] == "praise":
                k, n = ("praise", decision["objective"]), 0
            else:
                k = ("cue", decision["objective"], decision.get("side"))
                n = self.used[k] = self.used.get(k, 0) + 1
                n -= 1
            lines = store.get(k)
            if lines and n < len(lines) and lines[n]:
                if decision["kind"] == "cue":
                    self.said[decision["objective"]] = self.said.get(decision["objective"], 0) + 1
                return lines[n]
            return super().say(decision)                              # not written yet (or a third reminder): written now
    fast = Fast(entry, client=base.client, model=base.model, language=language)
    fast.used = {}
    return fast


SERVER_ONLY = None                                         # which activities this server was started with (--only)
STEP_S, WINDOW_S = 0.5, 25.0


class LiveMulti:
    """One live camera, every activity at once. Each activity has its own coaching session; every half second the activities are asked
    which of them owns each swing in the last 25 seconds (identify), and a session coaches only the swings that are its own."""

    def __init__(self, entries, language, offline, fps=30.0):
        from sphere import engine
        self.entries, self.fps = entries, fps
        self.taken = []                                    # swings already coached: (activity, start, end)
        self.owned = {a: [] for a in entries}
        self.sessions = {a: engine.Session(e, wording=fast_wording(e, a, language, offline), fps=fps,
                                           accept=(lambda s, end, a=a: self._accept(a, s, end)))
                         for a, e in entries.items()}
        self.pose, self.vis = [], []
        self.t0 = self.t = 0.0
        self.last_ident = -1e9
        self.log, self._seen = [], {a: 0 for a in entries}

    def _accept(self, act, s, e):
        """Does this swing belong to `act`? It must be one the activities' recognition gives to `act`, and not the follow-through of a swing
        already coached as another shot (what recognition sees can change while a swing is still fresh, so what was already coached counts)."""
        from sphere.identify import accepts, _overlap, FOLLOW_S
        if not accepts(self.owned[act], s, e):
            return False
        for other, ts, te in self.taken:
            if other != act and (_overlap((s, e), (ts, te)) > 0.2 or ts <= s <= te + FOLLOW_S):
                return False
        self.taken.append((act, s, e))
        return True

    def _collect(self, act, events):
        ses = self.sessions[act]
        for ev in events:
            ev["activity"] = act
            for row in reversed(ses.log):
                if row.get("said") is ev:
                    ev["attempt_end"] = row["end"]
                    break
        for row in ses.log[self._seen[act]:]:
            self.log.append(dict(row, activity=act))
        self._seen[act] = len(ses.log)
        return events

    def push(self, pose, vis, t):
        import numpy as np
        from sphere.identify import identify
        self.t = t
        self.pose.append(np.asarray(pose, float)); self.vis.append(np.asarray(vis, float))
        keep = int(WINDOW_S * self.fps)
        if len(self.pose) > keep:
            drop = len(self.pose) - keep
            del self.pose[:drop]; del self.vis[:drop]
            self.t0 += drop / self.fps
        if self.t - self.last_ident >= STEP_S and len(self.pose) >= 2 * self.fps:
            self.last_ident = self.t
            owned, _ = identify(self.entries, {"pose": np.stack(self.pose), "vis": np.stack(self.vis), "fps": self.fps, "meta": {}})
            self.owned = {a: [(self.t0 + s, self.t0 + e) for s, e in w] for a, w in owned.items()}
        events = []
        for act, ses in self.sessions.items():
            events += self._collect(act, ses.push(pose, vis, t))
        return events

    def flush(self):
        events = []
        for act, ses in self.sessions.items():
            events += self._collect(act, ses.flush())
        return events


def live_session(sid, activity, language, offline):
    """The coaching session of one live camera, made on its first batch of frames."""
    from sphere import engine
    with LIVE_LOCK:
        for k in [k for k, v in LIVE.items() if time.time() - v["seen"] > 3600]:      # forget sessions nobody has used for an hour
            del LIVE[k]
        if sid not in LIVE:
            if activity in ("auto", "tennis"):                          # every shot the server knows, told apart as they come
                entries = coach.load_all_entries(SERVER_ONLY or "tennis_serve,tennis_forehand")
                session = LiveMulti(entries, language, offline)
                activity = "tennis_live"
                print(f"  live session {sid[:8]} started for: {', '.join(entries)}", flush=True)
            else:
                entry = coach.load_entry(activity)
                session = engine.Session(entry, wording=fast_wording(entry, activity, language, offline), fps=30.0)
                print(f"  live session {sid[:8]} started for {activity}", flush=True)
            LIVE[sid] = {"printed": 0, "session": session, "lock": threading.Lock(), "seen": time.time(), "activity": activity}
        LIVE[sid]["seen"] = time.time()
        return LIVE[sid]


def with_attempt_end(session, events):
    """Each spoken event carries when the attempt it is about ended, so the phone can measure how long the coaching took after the swing."""
    for ev in events:
        if "attempt_end" in ev:
            continue
        for row in reversed(session.log):
            if row.get("said") is ev:
                ev["attempt_end"] = row["end"]
                break
    return events


def live_push(raw, q):
    import numpy as np
    d = json.loads(raw)
    pose, vis, start, fps = np.asarray(d["pose"], float), np.asarray(d["vis"], float), int(d["start"]), float(d.get("fps", 30.0))
    if pose.ndim != 3 or pose.shape[1:] != (17, 3) or vis.shape != pose.shape[:2]:
        raise ValueError(f"the joints have the wrong shape ({list(pose.shape)})")
    live = live_session(q["id"], q.get("activity", "auto"), q.get("language", "English"), q.get("offline") == "1")
    t0 = time.time()
    with live["lock"]:
        events = []
        for k in range(len(pose)):
            events += live["session"].push(pose[k], vis[k], (start + k) / fps)
        events = with_attempt_end(live["session"], events)
        rec = live.setdefault("rec", {"pose": [], "vis": []})            # everything the camera saw, kept to replay and tune offline
        rec["pose"].extend(pose.tolist()); rec["vis"].extend(vis.tolist())
        log = live["session"].log
        new, live["printed"] = log[live["printed"]:], len(log)
    swings = []
    for row in new:
        missed = [k for k, v in row["objectives"].items() if v.get("status") == "missed"]
        swings.append({"activity": row.get("activity", live["activity"]), "start": row["start"], "end": row["end"],
                       "judged_at": round(live["session"].t, 2), "missed": missed})
        print(f"  attempt {row['attempt']} {row.get('activity', '').replace('tennis_', '')} ({row['start']:.1f}-{row['end']:.1f} s) judged at {live['session'].t:.1f} s: "
              + (("missed " + ", ".join(missed)) if missed else "all fine"), flush=True)
    for ev in events:
        print(f"  {ev['t']:6.1f}s  [{ev['kind']}] {ev['text']}   (batch of {len(pose)} frames took {time.time() - t0:.2f} s)", flush=True)
    return {"events": events, "swings": swings}


def live_end(q):
    with LIVE_LOCK:
        live = LIVE.pop(q.get("id", ""), None)
    if not live:
        return {"events": []}
    with live["lock"]:
        events = with_attempt_end(live["session"], live["session"].flush())
        folder = os.path.join(coach.WORK, coach.slug(live["activity"]))
        os.makedirs(folder, exist_ok=True)
        stem = os.path.join(folder, time.strftime("session_%Y%m%d_%H%M%S"))
        json.dump({"activity": live["activity"], "attempts": live["session"].log}, open(stem + ".json", "w"), indent=1)
    print(f"  live session ended, log: {stem}.json", flush=True)
    rec = live.get("rec")
    if rec and len(rec["pose"]) > 30:
        from sphere.skeleton import make_clip, save_clip
        folder = os.path.join(coach.WORK, "phone")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, time.strftime("live_%Y%m%d_%H%M%S") + ".skeleton.npz")
        save_clip(path, make_clip(rec["pose"], rec["vis"], 30.0, {"source": "phone-live", "tracker": "ios-mediapipe-full"}))
        print(f"  the camera's joints, to replay: {path}", flush=True)
    return {"events": events}


def lan_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def make_handler(token, default_only, model, keep_dir=None):
    class H(BaseHTTPRequestHandler):
        def _send(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            line = fmt % args
            if "/live" in line and " 200 " in line + " ":                # a live camera calls twice a second: not worth a line each
                return
            print("  " + line, flush=True)

        def do_GET(self):
            path = urlparse(self.path).path
            if path in ("/", "/index.html"):                 # the page the phone opens: the app itself
                page = open(os.path.join(coach.HERE, "web", "index.html"), "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return self.wfile.write(page)
            if path == "/health":
                return self._send(200, {"ok": True, "activities": list(coach.load_all_entries(default_only))})
            self._send(404, {"error": "unknown address"})

        def _joints(self, n, q):
            """The phone read the body positions itself: only those arrive (about 1 MB for a minute), not the video."""
            stage("receiving the joints")
            body, left = bytearray(), n
            while left > 0:
                chunk = self.rfile.read(min(1 << 20, left))
                if not chunk:
                    break
                body += chunk; left -= len(chunk)
            if left:
                return self._send(400, {"error": "the joints were cut off"})
            clip = clip_from_joints(bytes(body), q.get("name"))
            if isinstance(clip, str):
                return self._send(422, {"error": clip})
            print(f"  received {n / 1e3:.0f} kB of joints: {len(clip['pose'])} frames at {clip['fps']:.1f} fps ({len(clip['pose']) / clip['fps']:.1f} s)", flush=True)
            entries = coach.load_all_entries(default_only or q.get("only"))
            stage("recognising the swings and coaching")
            out = analyse(clip, entries, q.get("language", "English"), q.get("offline") == "1")
            stage("done")
            self._send(200, out)

        def do_POST(self):
            url = urlparse(self.path)
            if url.path not in ("/coach", "/joints", "/live", "/live/end"):
                return self._send(404, {"error": "unknown address"})
            if not secrets.compare_digest(self.headers.get("X-Token", ""), token):
                return self._send(401, {"error": "wrong or missing token"})
            n = int(self.headers.get("Content-Length", 0))
            if url.path in ("/live", "/live/end"):            # a live camera: small batches, many sessions can overlap, no one-video lock
                q = {k: v[0] for k, v in parse_qs(url.query).items()}
                if not q.get("id"):
                    return self._send(400, {"error": "no session id"})
                try:
                    if url.path == "/live/end":
                        self.rfile.read(n)
                        return self._send(200, live_end(q))
                    body, left = bytearray(), n
                    while left > 0:
                        chunk = self.rfile.read(min(1 << 20, left))
                        if not chunk:
                            break
                        body += chunk; left -= len(chunk)
                    return self._send(200, live_push(bytes(body), q))
                except SystemExit as e:
                    return self._send(500, {"error": str(e)})
                except Exception as e:
                    return self._send(422, {"error": f"{type(e).__name__}: {str(e)[:200]}"})
            if n <= 0:
                return self._send(400, {"error": "no video in the request"})
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            if not BUSY.acquire(blocking=False):
                since = int(time.time() - JOB["since"])
                print(f"  busy: the video before is still being analysed ({JOB['stage']}, for {since} s)", flush=True)
                return self._send(503, {"error": f"busy with another video ({JOB['stage']}, for {since} s), try again in a minute"})
            tmp = None
            try:
                JOB["since"] = time.time()
                if url.path == "/joints":
                    return self._joints(n, q)
                stage("receiving the video")
                with tempfile.NamedTemporaryFile(suffix=".mov", delete=False) as f:
                    tmp, left = f.name, n
                    while left > 0:
                        chunk = self.rfile.read(min(1 << 20, left))
                        if not chunk:
                            break
                        f.write(chunk); left -= len(chunk)
                if left:
                    return self._send(400, {"error": "the video was cut off"})
                try:
                    print(f"  received {n / 1e6:.1f} MB: {describe(tmp)}", flush=True)
                    if keep_dir:                             # keep a copy of what the phone sent, to look at it or run it through coach.py
                        import shutil
                        os.makedirs(keep_dir, exist_ok=True)
                        kept = os.path.join(keep_dir, time.strftime("upload_%Y%m%d_%H%M%S.mov"))
                        shutil.copyfile(tmp, kept)
                        print(f"  kept a copy: {kept}", flush=True)
                except Exception as e:
                    print(f"  (could not describe the upload: {e})", flush=True)
                only = default_only or q.get("only")         # the server's own --only wins over the client's
                out = analyse_video(tmp, only, q.get("language", "English"), q.get("offline") == "1", model)
                self._send(422 if "error" in out else 200, out)
            except SystemExit as e:                          # an empty library ends in sys.exit with the explanation
                self._send(500, {"error": str(e)})
            except Exception as e:
                self._send(500, {"error": f"{type(e).__name__}: {str(e)[:200]}"})
            finally:
                BUSY.release()
                if tmp and os.path.exists(tmp):
                    os.remove(tmp)
    return H


def main():
    ap = argparse.ArgumentParser(description="Skill Sphere coaching server")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--only", default=None, help="only the activities whose name starts with this (for example: tennis)")
    ap.add_argument("--model", default="full", help="pose model: lite | full | heavy")
    ap.add_argument("--local", action="store_true", help="answer only this computer (default: other devices on your network too)")
    ap.add_argument("--keep-uploads", default=None, metavar="DIR", help="keep a copy of every video a phone sends in this folder")
    a = ap.parse_args()
    global SERVER_ONLY
    SERVER_ONLY = a.only
    token = os.environ.get("SPHERE_TOKEN") or secrets.token_urlsafe(9)
    server = ThreadingHTTPServer(("127.0.0.1" if a.local else "0.0.0.0", a.port), make_handler(token, a.only, a.model, a.keep_uploads))
    ip = "127.0.0.1" if a.local else lan_address()
    print(f"Coaching server ready for: {', '.join(coach.load_all_entries(a.only))}")
    print(f"  address  http://{ip}:{a.port}")
    print(f"  token    {token}   (the app sends it with every video)")
    print(f"  On the phone, open:  http://{ip}:{a.port}/?t={token}")
    print("  Stop with Ctrl-C.", flush=True)
    threading.Thread(target=prepare_language_model, daemon=True).start()

    def warm_all():                                          # write the live sentences now, so the first cue of a session is not slow
        time.sleep(3)                                        # after the language model library is loaded
        for act, entry in coach.load_all_entries(a.only).items():
            start_warm(entry, act, "English")
    threading.Thread(target=warm_all, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
