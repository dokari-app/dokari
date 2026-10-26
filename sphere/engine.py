"""The coaching engine: an entry plus a stream of skeleton frames in, cues out.

Nothing here knows the activity. The entry says what an attempt is (its events), where to look (landmarks of the time-normalised
attempt), what the objectives are, which values meet them and on which side a miss falls. The engine:

  1. finds finished attempts in the incoming frames (the same detector the factory used),
  2. judges every objective on each attempt: met, missed on a side, or unknown (it could not be seen or the camera angle is outside
     what the entry was built from),
  3. keeps the recent attempts and, when an objective is missed often enough (the entry's own rule, for example 3 of the last 5),
     chooses ONE thing to say between attempts: the most important missed objective, not repeated until a few attempts have passed,
  4. words the cue when it is needed, from the objective's goal and intent, never from a stored script.
"""
import re
from collections import deque
import numpy as np
from .features import compute_features, FEATURES
from .segment import segment_attempts, resample_anchored, resample
from . import principles as PR

N_T = 50


# ---------------------------------------------------------------- judging one attempt
def judge(cmp, v):
    """(met, side, overshoot) of one value against an objective's condition. side is 'below' or 'above' when missed; overshoot is how far
    outside the target, in the feature's own units."""
    if v is None or not np.isfinite(v):
        return None, None, None
    op = cmp["op"]
    if op == "WITHIN_RANGE":
        if v < cmp["low"]:
            return False, "below", float(cmp["low"] - v)
        if v > cmp["high"]:
            return False, "above", float(v - cmp["high"])
        return True, None, 0.0
    if op == "LESS_OR_EQUAL":
        return (True, None, 0.0) if v <= cmp["value"] else (False, "above", float(v - cmp["value"]))
    if op == "GREATER_OR_EQUAL":
        return (True, None, 0.0) if v >= cmp["value"] else (False, "below", float(cmp["value"] - v))
    raise ValueError(f"unexpected comparison {op}")


def evaluate(entry, arr, names, yaw=None, yaw_slack=15.0):
    """Judge every objective on one time-normalised attempt `arr` (N_T, D). -> {objective id: {status, side, value, overshoot}}.
    status: 'met' | 'missed' | 'unknown'. A test is unknown when its value cannot be computed or when the camera angle lies outside
    the angles the entry's target was built from (plus some slack): a number from an unfamiliar view is not evidence."""
    lm = {l["id"]: int(round(l["t"] * (N_T - 1))) for l in entry["movement_model"]["landmarks"]}
    out = {}
    for o in entry["objectives"]:
        t = o["tests"][0]
        li = lm[t["at"]]
        v = float(np.nanmedian(arr[max(0, li - 1):li + 2, names.index(t["feature"])])) if t["feature"] in names else float("nan")
        vv = t.get("valid_views")
        if yaw is not None and vv and not (vv["yaw_min"] - yaw_slack <= yaw <= vv["yaw_max"] + yaw_slack):
            out[o["id"]] = {"status": "unknown", "side": None, "value": v, "overshoot": None, "why": "view"}
            continue
        met, side, over = judge(t["compare"], v)
        if met is None:
            out[o["id"]] = {"status": "unknown", "side": None, "value": v, "overshoot": None, "why": "value"}
        elif met:
            out[o["id"]] = {"status": "met", "side": None, "value": v, "overshoot": 0.0}
        else:
            if side not in o["sides"]:                       # the entry only knows how to be wrong on the sides it lists
                out[o["id"]] = {"status": "unknown", "side": None, "value": v, "overshoot": None, "why": "side"}
            else:
                out[o["id"]] = {"status": "missed", "side": side, "value": v, "overshoot": over}
    return out


def attempts_in(entry, clip):
    """Finished attempts of a clip: [{start, end (seconds), arr (N_T, D), yaw}] using the events and primary features the entry was built with."""
    prov = entry["metadata"]["provenance"]
    names, F, info = compute_features(clip)
    seg = segment_attempts(F, clip["fps"], names, prov["attempt_events"], prov.get("primary_features"))
    out = []
    for (a, b), pk in zip(seg["attempts"], seg["peaks"]):
        arr = resample_anchored(F, a, b, pk, N_T) if len(pk) > 1 else resample(F, a, b, N_T)
        out.append({"start": a / clip["fps"], "end": b / clip["fps"], "arr": arr, "yaw": info["view_yaw_deg"]})
    return names, out


# ---------------------------------------------------------------- deciding what to say
class Policy:
    """Remembers recent attempts and decides, after each one, whether to say something and what.
    One cue at most per attempt. An objective is *persistent* when it was missed in at least n of the last `of` attempts (its own
    aggregate rule from the entry). Among persistent objectives the one with the best priority wins; one just cued is left alone for
    `cooldown` attempts so the person can try it. After a cue, an objective met on `praise_after` attempts in a row earns a short
    confirmation, once."""

    def __init__(self, entry, cooldown=3, praise_after=2):
        self.entry = entry
        self.obj = {o["id"]: o for o in entry["objectives"]}
        self.rule = {i: (o["tests"][0]["aggregate"]["n"], o["tests"][0]["aggregate"]["of"]) for i, o in self.obj.items()}
        self.hist = {i: deque(maxlen=self.rule[i][1]) for i in self.obj}
        self.cooldown, self.praise_after = cooldown, praise_after
        self.since_cue = {}            # objective id -> attempts since it was cued
        self.cued = set()              # cued and not yet praised
        self.met_streak = {i: 0 for i in self.obj}
        self.count = 0

    def update(self, result):
        """result = evaluate(...) of the attempt that just finished. -> None or {'kind': 'cue'|'praise', 'objective', 'side', 'why': {...}}"""
        self.count += 1
        for i in self.since_cue:
            self.since_cue[i] += 1
        for i, r in result.items():
            self.hist[i].append(r)
            self.met_streak[i] = self.met_streak[i] + 1 if r["status"] == "met" else 0
        persistent = []
        for i, o in self.obj.items():
            n, of = self.rule[i]
            missed = [r for r in self.hist[i] if r["status"] == "missed"]
            if len(missed) >= n and self.since_cue.get(i, 10 ** 6) >= self.cooldown:
                sides = [r["side"] for r in missed]
                persistent.append((o["priority"], i, max(set(sides), key=sides.count), len(missed), len(self.hist[i])))
        if persistent:
            _, i, side, k, m = min(persistent)
            self.since_cue[i] = 0
            self.cued.add(i)
            return {"kind": "cue", "objective": i, "side": side, "why": {"missed": k, "of": m, "last": result[i]}}
        for i in sorted(self.cued, key=lambda x: self.obj[x]["priority"]):
            if self.met_streak[i] >= self.praise_after and self.since_cue.get(i, 0) >= 1:
                self.cued.discard(i)
                return {"kind": "praise", "objective": i, "side": None, "why": {"met_in_a_row": self.met_streak[i]}}
        return None


# ---------------------------------------------------------------- wording
class Wording:
    """Turns a decision into one short spoken sentence. With a model client the sentence is written for the moment from the objective's
    goal, what the miss looks like and the intents in the entry; without one it falls back to the entry's own cue intent, lightly reshaped.
    Nothing is stored: the same objective is worded afresh each time, and a repeat is told it is a repeat."""
    MAX_WORDS = 10
    BANNED = re.compile(r"\b(balls?|rackets?|racquets?|spins?|topspin|backspin|pace|contact|bounces?|strings?|sweet spot)\b", re.I)
    SYSTEM = ("You are a tennis-or-sport coach speaking into a player's earbud between attempts. Say ONE short spoken sentence (at most 10 words) "
              "that names the EFFECT the player should get (what the movement should achieve), not a body part, and not what they did wrong. No numbers, no "
              "apology, no greeting, no mention of measurements or cameras. Speak only about what the player's own body does: nothing is known about the ball or the "
              "racket, so never mention the ball, the racket, contact, spin, pace or where the ball goes. If told this is a repeat, say it differently and a little more directly. Output only the sentence.")
    WHY_SYSTEM = ("You are a sport coach answering a player who asked why, between attempts. Explain the idea in two or three short spoken sentences, in plain "
                  "words, using only the idea you are given. No lists, no jargon, no medical or safety claims. Output only the sentences.")

    def __init__(self, entry, client=None, model=None, language="English"):
        self.entry, self.client, self.model, self.language = entry, client, model, language
        self.obj = {o["id"]: o for o in entry["objectives"]}
        self.said = {}

    @classmethod
    def allowed(cls, text):
        """A spoken line is short and claims nothing that is not measured (the ball and the racket are not tracked)."""
        return bool(text) and len(text.split()) <= cls.MAX_WORDS and not cls.BANNED.search(text)

    def say(self, decision):
        """The sentence for a decision, or None when nothing allowed can be said (then nothing is said)."""
        text = self._say(decision)
        return text if self.allowed(text) else None

    def _say(self, decision):
        o = self.obj[decision["objective"]]
        n = self.said[decision["objective"]] = self.said.get(decision["objective"], 0) + (1 if decision["kind"] == "cue" else 0)
        if decision["kind"] == "praise":
            return self._ask(o, decision, "The player has now done this right twice in a row after being reminded. Confirm it in a few words, warmly.") \
                or "Good, that's it."
        miss = o["sides"].get(decision["side"], {}).get("looks_like", "")
        extra = f"This is reminder number {n} for this objective." if n > 1 else "This is the first reminder."
        pr = PR.for_objective(self.entry, o["id"])
        if PR.has_handle(pr):
            extra += f"\nThe idea behind it: {pr['statement']}\nPoint at that idea through this intent: {pr['handle_intent']}."
        return self._ask(o, decision, f"What the miss looks like: {miss}\n{extra}") or self._fallback(o, pr)

    def why(self, oid):
        """A short explanation of the principle behind an objective, for when the player asks. None when the entry has no principle for it."""
        pr = PR.for_objective(self.entry, oid)
        if not pr:
            return None
        o = self.obj[oid]
        txt = None
        if self.client:
            try:
                r = self.client.messages.create(model=self.model or "claude-sonnet-5-5", max_tokens=140, system=self.WHY_SYSTEM,
                                                messages=[{"role": "user", "content": f"Idea: {pr['statement']}\nGoal it serves: {o['goal']}\nLanguage: {self.language}."}])
                txt = "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip() or None
            except Exception:
                txt = None
        txt = txt or pr["statement"]
        return None if self.BANNED.search(txt) else txt        # an explanation that talks about the ball claims what is not measured: none is given

    def _ask(self, o, decision, tail):
        if not self.client:
            return None
        prompt = (f"Objective: {o['goal']}\nIntent of the reminder: {o['cue_intent']}\nHow to fix it: {o['fix_intent']}\n{tail}\nLanguage: {self.language}.")
        for attempt in range(2):                 # a line that is too long or claims something unmeasured is asked for once more
            try:
                r = self.client.messages.create(model=self.model or "claude-sonnet-5-5", max_tokens=60, system=self.SYSTEM,
                                                messages=[{"role": "user", "content": prompt + ("" if not attempt else f"\nYour last line was not allowed: it must be at most {self.MAX_WORDS} words and must not mention the ball, the racket, contact, spin or pace. Try again.")}])
                txt = "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip().strip('"')
            except Exception:
                return None
            if self.allowed(txt):
                return txt
        return None

    @staticmethod
    def _fallback(o, pr=None):
        if PR.has_handle(pr):
            s = pr["handle_intent"].strip().rstrip(".")
            return s[:1].upper() + s[1:] + "."
        s = o["cue_intent"].strip().rstrip(".")
        for lead in ("Cue the person to ", "Cue the player to ", "Remind the person to ", "Remind the player to ", "Cue the person ", "Cue "):
            if s.startswith(lead):
                s = s[len(lead):]
                break
        return s[:1].upper() + s[1:] + "."


# ---------------------------------------------------------------- a session
class Session:
    """Frames in, cues out, in video time. Works the same for a recorded video and a live camera: push() frames as they arrive; a cue comes
    back when an attempt has just finished and there is something to say.

    The detector needs context on both sides of an attempt, so every `step` seconds the last `window` seconds are examined and each attempt that ended at
    least `settle` seconds ago and has not been judged yet is judged once (attempts are matched by their time, so a frame buffer that slides
    never judges the same attempt twice)."""

    def __init__(self, entry, wording=None, fps=30.0, window=25.0, step=0.5, settle=0.7, policy=None, accept=None):
        self.accept = accept           # accept(start, end) -> whether an attempt belongs to this activity (several activities share one video)
        self.entry, self.fps, self.window, self.step, self.settle = entry, fps, window, step, settle
        self.policy = policy or Policy(entry)
        self.wording = wording or Wording(entry)
        self.t0 = 0.0                  # time of the first buffered frame
        self.pose, self.vis = [], []
        self.t = 0.0
        self.last_check = -1e9
        self.judged = []               # (start, end) seconds of attempts already judged
        self.log = []                  # every attempt and decision, for the record
        self.last_cue = None           # objective of the latest cue (what "why?" refers to)
        self.offered = set()           # objectives whose principle was already offered at a rest
        self.last_end = None           # when the latest attempt ended
        self.rest_after = 20.0         # seconds without an attempt that count as a rest

    def push(self, pose, vis, t=None):
        """One frame: pose (J, 3), vis (J,). Returns a list of events [{'t', 'kind': 'cue'|'praise', 'text', 'objective', ...}] (usually empty)."""
        self.t = self.t + 1.0 / self.fps if t is None else t
        self.pose.append(np.asarray(pose, float)); self.vis.append(np.asarray(vis, float))
        keep = int(self.window * self.fps)
        if len(self.pose) > keep:
            drop = len(self.pose) - keep
            del self.pose[:drop]; del self.vis[:drop]
            self.t0 += drop / self.fps
        if self.t - self.last_check < self.step or len(self.pose) < 2 * self.fps:
            return []
        self.last_check = self.t
        return self._check() + self._rest_offer()

    def why(self, oid=None):
        """The player asked why: explain the principle behind the latest cue (or a named objective). None when there is none."""
        oid = oid or self.last_cue
        return self.wording.why(oid) if oid else None

    def _rest_offer(self):
        """After a rest with no attempts, offer once the principle behind the latest cue, if the entry has one that may be offered at a rest."""
        oid = self.last_cue
        if not oid or oid in self.offered or self.last_end is None or self.t - self.last_end < self.rest_after:
            return []
        pr = PR.for_objective(self.entry, oid)
        if not pr or "rest" not in pr["offer_when"]:
            return []
        self.offered.add(oid)
        text = self.why(oid)
        return [{"t": round(self.t, 2), "kind": "principle", "objective": oid, "side": None, "text": text}] if text else []

    def _check(self):
        clip = {"pose": np.stack(self.pose), "vis": np.stack(self.vis), "fps": self.fps, "meta": {}}
        names, atts = attempts_in(self.entry, clip)
        events = []
        for a in atts:
            s, e = self.t0 + a["start"], self.t0 + a["end"]
            if self.t - e < self.settle or any(self._same(s, e, js, je) for js, je in self.judged):
                continue
            self.judged.append((s, e))
            if self.accept and not self.accept(s, e):
                continue
            self.last_end = e
            res = evaluate(self.entry, a["arr"], names, a["yaw"])
            dec = self.policy.update(res)
            row = {"attempt": len(self.judged), "start": round(s, 2), "end": round(e, 2), "yaw": round(a["yaw"], 1),
                   "objectives": {i: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k != "why"} | ({"why": r["why"]} if "why" in r else {})
                                  for i, r in res.items()}}
            if dec:
                if dec["kind"] == "cue":
                    self.last_cue = dec["objective"]
                text = self.wording.say(dec)
                if text:                                   # nothing allowed to say: stay quiet
                    ev = {"t": round(self.t, 2), "kind": dec["kind"], "objective": dec["objective"], "side": dec["side"], "text": text}
                    row["said"] = ev
                    events.append(ev)
            self.log.append(row)
        return events

    @staticmethod
    def _same(s, e, js, je):
        inter = max(0.0, min(e, je) - max(s, js))
        return inter / max(1e-9, (e - s) + (je - js) - inter) > 0.3

    def flush(self):
        """Judge attempts that ended right at the end of the stream (call once when the video or camera stops)."""
        self.settle = 0.0
        return self._check() if len(self.pose) >= 2 * self.fps else []


def run_clip(entry, clip, wording=None, **kw):
    """Feed a whole recorded clip through a Session in video time. -> (events, log)."""
    s = Session(entry, wording=wording, fps=clip["fps"], **kw)
    events = []
    for k in range(len(clip["pose"])):
        events += s.push(clip["pose"][k], clip["vis"][k], k / clip["fps"])
    events += s.flush()
    return events, s.log
