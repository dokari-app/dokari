"""Run:  python -m tests.test_pipeline    (plain asserts, no test framework needed)"""
import copy, json, os, shutil, tempfile
import numpy as np
from sphere import synth, skeleton, pipeline, propose, calibrate as C, features, segment
from sphere.segment import segment_attempts
from sphere.checks import run_checks
from sphere.builder import InsufficientData, build_entry


SQ = [{"feature": "height.hip", "direction": "falls", "seconds": 3.0}]
SQ_PRIM = ["angle.knee.dom", "angle.hip.dom", "height.hip"]
ARM = [{"feature": "angle.shoulder.dom", "direction": "rises", "seconds": 2.0}]
ARM_PRIM = ["angle.shoulder.dom", "angle.shoulder.non"]


def squat_attempts(clip, **kw):
    n, F, _ = features.compute_features(clip)
    return segment_attempts(F, clip["fps"], n, SQ, SQ_PRIM)


def stub(act, r):
    return [propose.stub_squat_proposal() for _ in range(r)]


def make_work():
    w = tempfile.mkdtemp()
    os.makedirs(f"{w}/squat/clips"); os.makedirs(f"{w}/arm_raise/clips")
    for s, y in enumerate([0, 40, 80, 20, 60, 10]):
        skeleton.save_clip(f"{w}/squat/clips/g{s}.npz", synth.squat_clip(yaw=y, seed=s, tag="good"))
    for i in range(4):
        skeleton.save_clip(f"{w}/squat/clips/c{i}.npz", synth.squat_clip(yaw=40, seed=10 + i, tag="knee_cave", valgus=0.05))
    for i in range(3):
        skeleton.save_clip(f"{w}/squat/clips/s{i}.npz", synth.squat_clip(yaw=30, seed=20 + i, tag="shallow_depth", depth=0.5))
    for s, y in enumerate([0, 40, 70]):
        skeleton.save_clip(f"{w}/arm_raise/clips/a{s}.npz", synth.arm_raise_clip(seed=s, yaw=y))
    json.dump({"primary_features": ARM_PRIM, "attempt_events": ARM, "events_rule": 6}, open(f"{w}/arm_raise/prior.json", "w"))
    return w


def status(checks):
    return {c["id"]: c["status"] for c in checks}


def test_features_are_view_invariant():
    vals = []
    for yaw in (0, 45, 90):
        n, F, _ = features.compute_features(synth.squat_clip(yaw=yaw, seed=1))
        vals.append(np.nanmedian(F, axis=0))
    spread = np.nanmax(np.abs(vals[0] - vals[2]))
    assert spread < 0.5, spread


def test_segmentation_counts():
    r = squat_attempts(synth.squat_clip(reps=8))
    assert 7 <= len(r["attempts"]) <= 8, len(r["attempts"])


def test_one_attempt_is_an_attempt():
    r = squat_attempts(synth.squat_clip(reps=1))
    assert len(r["attempts"]) == 1, r["attempts"]


def test_one_attempt_amid_standing():
    from sphere.skeleton import make_clip
    one = synth.squat_clip(reps=1, seed=2, yaw=30)["pose"]
    stand = one[:1].repeat(600, axis=0) + np.random.default_rng(1).normal(0, 0.004, (600,) + one.shape[1:])
    pose = np.concatenate([stand, one, stand])
    clip = make_clip(pose, np.full(pose.shape[:2], 0.95), 30, {"id": "one"})
    r = squat_attempts(clip)
    assert len(r["attempts"]) == 1, r["attempts"]
    a, b = r["attempts"][0]
    assert 540 <= a and b <= 600 + len(one) + 60, (a, b)


def test_five_attempts_with_pauses():
    from sphere.skeleton import make_clip
    one = synth.squat_clip(reps=1, seed=2, yaw=30)["pose"]
    stand = one[:1].repeat(300, axis=0)
    pose = np.concatenate([stand] + [np.concatenate([one, stand]) for _ in range(5)])
    r = squat_attempts(make_clip(pose, np.full(pose.shape[:2], 0.95), 30, {"id": "five"}))
    assert len(r["attempts"]) == 5, r["attempts"]


def test_tracking_noise_is_not_an_attempt():
    from sphere.skeleton import make_clip
    c = synth.squat_clip(reps=1, seed=3, yaw=30)["pose"]
    rng = np.random.default_rng(0)
    still = c[:1].repeat(900, axis=0)
    flick = np.stack([c[0] if i % 2 == 0 else c[45] for i in range(300)])      # the tracker flips between two poses
    pose = np.concatenate([still, flick, still])
    r = squat_attempts(make_clip(pose, np.full(pose.shape[:2], 0.95), 30, {"id": "flicker"}))
    assert len(r["attempts"]) == 0, r["attempts"]


def test_curation_drops_other_movement_keeps_faulty_form():
    depth = [1.2, 0.85, 1.1, 0.95, 1.0, 0.9]                         # people differ a little; real data are never identical
    sq = [C.collect_attempts(synth.squat_clip(yaw=y, seed=i, depth=depth[i], tag="good"), SQ, SQ_PRIM) for i, y in enumerate([0, 40, 80, 20, 60, 10])]
    bad = [C.collect_attempts(synth.squat_clip(yaw=30, seed=20 + i, tag="shallow_depth", depth=0.6), SQ, SQ_PRIM) for i in range(3)]
    junk = [C.collect_attempts(synth.arm_raise_clip(seed=i, yaw=y), ARM, ARM_PRIM) for i, y in enumerate([0, 40, 70])]
    out, rep = C.curate(sq + bad + junk)
    kept = {r["clip"]: r["kept"] for r in rep["clips"]}
    assert len(kept) == 12 and all(kept[k] == 0 for k in kept if "arm" in k), kept
    assert all(kept[k] > 0 for k in kept if "shallow" in k), kept


def test_reps_found_inside_messy_clip():
    from sphere.skeleton import make_clip
    rng = np.random.default_rng(0)
    a = synth.squat_clip(reps=6, seed=1, yaw=30); b = synth.squat_clip(reps=6, seed=2, yaw=30)
    deep = synth.squat_clip(reps=1, seed=3, yaw=30)["pose"]
    noise = lambda n: rng.normal(0, 0.01, (n,) + a["pose"].shape[1:])
    stand = a["pose"][:1].repeat(1200, axis=0) + noise(1200)                    # standing and talking
    hold = deep[45:46].repeat(600, axis=0) + noise(600)                          # a held position
    flick = np.stack([a["pose"][0] if i % 2 == 0 else deep[45] for i in range(300)])   # tracking failure
    pose = np.concatenate([stand, a["pose"], hold, flick, b["pose"], stand[:300]])
    clip = make_clip(pose, np.full(pose.shape[:2], 0.95), 30, {"id": "messy"})
    messy = C.collect_attempts(clip, SQ, SQ_PRIM)
    ref = [C.collect_attempts(synth.squat_clip(reps=6, seed=5 + i, yaw=30), SQ, SQ_PRIM) for i in range(3)]
    out, rep = C.size_gate([messy] + ref)       # a 17 s hold is an excursion of the signal, but it is not an attempt
    assert len(out[0]["attempts"]) == 12, (len(messy["attempts"]), len(out[0]["attempts"]), rep)


def test_alignment_fixes_cycle_start():
    cols = [C.collect_attempts(synth.squat_clip(yaw=y, seed=i, tag="good"), SQ, SQ_PRIM) for i, y in enumerate([0, 40, 80, 20])]
    for c in cols[:2]:                                        # pretend these clips were cut at the other extreme
        c["attempts"] = [np.roll(a, 25, axis=0) for a in c["attempts"]]
    fixed, rep = C.align_cycles(cols)
    ms = [np.nanmedian(np.stack(c["attempts"]), axis=0) for c in fixed]
    spread = max(np.nanmax(np.abs(ms[0] - m)) for m in ms[1:])
    raw = [np.nanmedian(np.stack(c["attempts"]), axis=0) for c in cols]
    assert rep["applied"] and spread < 0.25 * np.nanmax(np.abs(raw[0] - raw[3])), (spread, rep)


def test_primary_features_ignore_other_motion():
    clip = synth.arm_raise_clip(seed=1, yaw=30)                        # only the arms move
    n, F, _ = features.compute_features(clip)
    legs = segment_attempts(F, 30, n, [{"feature": "angle.knee.dom", "direction": "falls"}], ["angle.knee.dom", "angle.hip.dom"])
    arms = segment_attempts(F, 30, n, ARM, ARM_PRIM)
    assert len(legs["attempts"]) == 0, legs["attempts"]
    assert len(arms["attempts"]) >= 4, arms["attempts"]


def test_one_joint_gesturing_is_not_a_repetition():
    clip = synth.arm_raise_clip(seed=1, yaw=30)                        # only the arms move
    n, F, _ = features.compute_features(clip)
    r = segment_attempts(F, 30, n, ARM, ["angle.knee.dom", "angle.hip.dom", "height.hip", "angle.shoulder.dom"])
    assert len(r["attempts"]) == 0, r["attempts"]                      # 1 of 4 joints swinging is not the movement


def test_ordered_events_need_both_in_order():
    from sphere.segment import _chain, excursions
    t = np.arange(900)
    bump = lambda c, w: np.exp(-((t - c) / w) ** 2)
    toss = bump(100, 12) + bump(400, 12) + bump(700, 12)         # three tosses, the middle one abandoned
    hit = bump(125, 8) + bump(725, 8)
    got = _chain([excursions(toss, 30, 0.2), excursions(hit, 30, 0.2)], 30)
    assert len(got) == 2 and got[0][0] < 100 < 125 < got[0][1] and got[1][0] < 700, got
    assert _chain([excursions(hit, 30, 0.2), excursions(toss[::-1].copy(), 30, 0.2)], 30) != got   # order matters


def test_events_are_lined_up():
    from sphere.segment import resample_anchored
    F = np.zeros((200, 1)); F[60:70, 0] = 1; F[140:150, 0] = 2          # first event peaks at 65, second at 145
    G = np.zeros((300, 1)); G[100:110, 0] = 1; G[250:260, 0] = 2
    a = resample_anchored(F, 0, 199, [65, 145], 50)[:, 0]; b = resample_anchored(G, 0, 299, [105, 255], 50)[:, 0]
    assert abs(int(np.argmax(a == 1)) - int(np.argmax(b == 1))) <= 2 and abs(int(np.argmax(a == 2)) - int(np.argmax(b == 2))) <= 2


def test_grow_stops_when_enough_attempts():
    from sphere import grow, acquire, extract
    w = make_work()
    json.dump({"primary_features": SQ_PRIM, "attempt_events": SQ, "events_rule": 6, "search_queries": [{"query": "squat", "kind": "good_form"}]},
              open(f"{w}/squat/prior.json", "w"))
    for f in os.listdir(f"{w}/squat/clips")[4:]:
        os.rename(f"{w}/squat/clips/{f}", f"{w}/{f}")                      # start with only a few clips
    spare = sorted(f for f in os.listdir(w) if f.endswith(".npz"))
    calls = {"q": 0, "a": 0}
    P_q, A_a, E_e = propose.propose_queries, acquire.acquire, extract.extract_folder
    propose.propose_queries = lambda *a, **k: calls.__setitem__("q", calls["q"] + 1) or [{"query": "more", "kind": "demonstration"}]
    def fake_acquire(*a, **k):
        calls["a"] += 1
        return [{"id": "x"}] if calls["a"] <= 3 else []
    def fake_extract(vdir, cdir, *a, **k):
        for f in spare[:3]:
            os.rename(f"{w}/{f}", f"{cdir}/{f}")
        del spare[:3]
    acquire.acquire, extract.extract_folder = fake_acquire, fake_extract
    try:
        r = grow.grow("squat", w, target_attempts=40, target_clips=6)
        assert r["target_reached"] and r["rounds"] >= 1 and r["attempts"] >= 40, r
        r2 = grow.grow("squat", w, target_attempts=10 ** 6, target_clips=6, max_rounds=2)
        assert not r2["target_reached"], r2                                   # asks for the impossible: stops and says so
    finally:
        propose.propose_queries, acquire.acquire, extract.extract_folder = P_q, A_a, E_e
    shutil.rmtree(w)


def test_recognition_needs_the_defining_events():
    from sphere.calibrate import events_present
    names = features.FEATURES
    ev = [{"feature": "height.wrist.non", "direction": "rises", "peak_at_least": 0.8},
          {"feature": "height.wrist.dom", "direction": "rises", "peak_at_least": 0.8}]
    t = np.arange(50)
    bump = lambda c: np.exp(-((t - c) / 4.0) ** 2) * 1.5 - 0.6
    mk = lambda a, b: np.stack([a if n == "height.wrist.non" else b if n == "height.wrist.dom" else np.zeros(50) for n in names], axis=1)
    assert events_present(mk(bump(15), bump(33)), ev, names)                      # toss, then hit
    assert not events_present(mk(bump(33), bump(15)), ev, names)                  # the wrong way round
    assert not events_present(mk(bump(15), bump(33) * 0.3), ev, names)           # the hit never gets overhead
    assert events_present(mk(bump(24), bump(25)), ev, names)                      # together counts (either order)


def test_consensus_keeps_what_most_runs_agree_on():
    base = propose.stub_squat_proposal()
    f = copy.deepcopy(base["objectives"][0]); f["id"] = "guess"; f["caused_by"] = []; f["test"] = dict(f["test"], feature="angle.knee.dom")
    base["objectives"].append(f)                                      # only the first run thought of this
    runs = [base, copy.deepcopy(propose.stub_squat_proposal()), copy.deepcopy(propose.stub_squat_proposal())]
    out, support, dropped = propose.consensus(runs)
    ids = [x["id"] for x in out["objectives"]]
    assert "guess" not in ids and "guess" in dropped and support["knee_cave"] == 3, (ids, support)


def test_parallel_extraction_gives_the_same_clips():
    from sphere import extract as E
    from sphere.skeleton import make_clip, load_clip
    def fake(path, meta=None, variant="full", target_fps=30.0):
        if "bad" in path:
            raise ValueError("damaged")
        if "none" in path:
            return None
        rng = np.random.default_rng(sum(map(ord, meta["id"])))
        return make_clip(rng.normal(0, 1, (40, len(E.JOINTS), 3)), np.full((40, len(E.JOINTS)), 0.9), 30, dict(meta, detect_rate=0.9))
    keep, E.extract_video = E.extract_video, fake
    d = tempfile.mkdtemp()
    try:
        os.makedirs(d + "/v")
        for n in ("a", "b", "c", "bad", "none"):
            open(f"{d}/v/{n}.mp4", "wb").write(b"x")
        assert E.extract_folder(d + "/v", d + "/s/clips", workers=1) == 3
        assert E.extract_folder(d + "/v", d + "/p/clips", workers=3, start_method="fork") == 3
        assert all(np.array_equal(load_clip(f"{d}/s/clips/{n}.npz")["pose"], load_clip(f"{d}/p/clips/{n}.npz")["pose"]) for n in "abc")
        assert json.load(open(d + "/p/rejected.json")) == ["none"]          # no person: ruled out for good; a damaged file is retried later
    finally:
        E.extract_video = keep
        shutil.rmtree(d)


class _Block:
    def __init__(self, inp):
        self.type, self.input = "tool_use", inp


class FakeClient:
    """Stands in for the language model: answers every call with the next prepared tool input."""
    def __init__(self, *answers):
        self.answers, self.calls = list(answers), []
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        a = self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]
        return type("R", (), {"content": [_Block(a(kw) if callable(a) else a)]})()


def _items():
    mk = lambda i, t, ch: {"id": i, "title": f"t{i}", "channel": ch, "duration": 100, "url": f"u{i}"}
    return [mk("a", "x", "c1"), mk("b", "x", "c1"), mk("c", "x", "c1"), mk("d", "x", "c2"), mk("e", "x", "c3"), mk("f", "x", "c4")]


def test_foot_and_heel_features():
    clip = synth.squat_clip(yaw=0, seed=1)
    n, F, _ = features.compute_features(clip)
    ix = {k: n.index(k) for k in ("height.heel.dom", "rot.foot_turnout.dom", "rot.foot_turnout.non", "height.heel.non")}
    assert np.isfinite(F[:, list(ix.values())]).all()
    base = np.nanmedian(F[:, [ix["rot.foot_turnout.dom"], ix["rot.foot_turnout.non"]]])
    out = copy.deepcopy(clip)
    from sphere.skeleton import J
    out["pose"][:, J["l_toe"], 0] -= 0.05; out["pose"][:, J["r_toe"], 0] += 0.05      # both toes turned outward
    n2, F2, _ = features.compute_features(out)
    turned = np.nanmedian(F2[:, [ix["rot.foot_turnout.dom"], ix["rot.foot_turnout.non"]]])
    assert turned > base + 10, (base, turned)
    lifted = copy.deepcopy(clip); lifted["pose"][:, J["l_heel"], 1] += 0.05; lifted["pose"][:, J["r_heel"], 1] += 0.05
    n3, F3, _ = features.compute_features(lifted)
    assert np.nanmedian(F3[:, ix["height.heel.dom"]]) > np.nanmedian(F[:, ix["height.heel.dom"]]) + 0.05
    from sphere.vocab import plausible_range
    assert plausible_range("rot.foot_turnout.dom") == (-180.0, 180.0) and features.feature_measure("rot.foot_turnout.dom") == "M02"


def test_link_calls_a_loose_match_a_proxy():
    from sphere import knowledge as K
    kmap = K._count(_map(None), 3)
    efs = [{"id": "knee_cave", "goal": "knees track over the toes", "feature": "dev.knee_inward.dom"}]
    resp = {"links": [{"fault": "knees_cave", "objective": "knee_cave", "measurable": "measured", "note": ""},
                      {"fault": "heels_lift", "objective": "knee_cave", "measurable": "proxy", "note": ""}]}
    out, unsup = K.link(kmap, efs, features.FEATURE_DOC, "squat", client=FakeClient(resp))
    assert out["knees_cave"]["measurable"] == "measured" and out["heels_lift"]["measurable"] == "proxy" and unsup == []
    resp3 = {"links": [{"fault": "heels_lift", "objective": None, "measurable": "feature_available", "note": "rot.foot_turnout.dom"}]}
    out3, _ = K.link(kmap, efs, features.FEATURE_DOC, "squat", client=FakeClient(resp3))
    assert out3["heels_lift"]["measurable"] == "feature_available" and out3["heels_lift"]["note"] == "rot.foot_turnout.dom"
    resp2 = {"links": [{"fault": "knees_cave", "objective": "knee_cave", "measurable": "needs_new_feature", "note": "x"}]}
    out2, _ = K.link(kmap, efs, features.FEATURE_DOC, "squat", client=FakeClient(resp2))
    assert out2["knees_cave"]["measurable"] == "proxy"                             # names a test but does not call it the thing itself


def _retag_unlabelled(w):
    for f in os.listdir(f"{w}/squat/clips"):
        clip = skeleton.load_clip(f"{w}/squat/clips/{f}"); clip["meta"]["tag"] = "unlabelled"
        skeleton.save_clip(f"{w}/squat/clips/{f}", clip)


def _demos_as_sources(w):
    cols = pipeline.load_collections(f"{w}/squat/clips", SQ, None, SQ_PRIM)
    good = lambda c: "good" in c["clip_id"]                                          # the clips with correct form play the coach demonstrations
    json.dump([{"id": c["clip_id"], "tier": "coach_demo" if good(c) else "practice_session", "shows": "good_form" if good(c) else "unknown"} for c in cols],
              open(f"{w}/squat/sources.json", "w"))


def test_weak_check_compares_demonstrations_with_everyday_footage():
    w = make_work()
    _retag_unlabelled(w); _demos_as_sources(w)
    entry, _ = pipeline.build("squat", w, runs=1, proposer=stub)
    wc = entry["metadata"]["weak_check"]
    assert set(wc) == {o["id"] for o in entry["objectives"]}, wc
    assert wc["knee_cave"]["verdict"] == "supports" and wc["knee_cave"]["good"]["flagged_per_clip"] < wc["knee_cave"]["other"]["flagged_per_clip"]   # the planted fault departs from the demonstrated range
    assert "Sanity check of the target ranges" in open(f"{w}/squat/report.md").read()
    shutil.rmtree(w)


def test_target_range_comes_from_demonstrations_when_there_are_enough():
    w = make_work()
    _retag_unlabelled(w)
    e0, _ = pipeline.build("squat", w, runs=1, proposer=stub)                         # no rated sources: only everyday footage to go on
    assert {o["calibration"]["basis"] for o in e0["objectives"]} == {"everyday_footage"}
    _demos_as_sources(w)
    e1, _ = pipeline.build("squat", w, runs=1, proposer=stub)
    assert {o["calibration"]["basis"] for o in e1["objectives"]} == {"good_form_demonstrations"}
    assert all(o["calibration"]["n_reference_clips"] == 6 for o in e1["objectives"])
    assert e1["metadata"]["provenance"]["calibration_basis"] == {"good_form_demonstrations": 3}
    shutil.rmtree(w)


def test_sides_decide_which_bounds_a_range_has():
    w = make_work()
    _retag_unlabelled(w)
    entry, _ = pipeline.build("squat", w, runs=1, proposer=stub)
    cmp_ = {o["id"]: o["tests"][0]["compare"] for o in entry["objectives"]}
    assert cmp_["knee_cave"]["op"] == "LESS_OR_EQUAL" and cmp_["shallow_depth"]["op"] == "LESS_OR_EQUAL"       # only 'above' is wrong
    assert cmp_["excess_forward_lean"]["op"] == "WITHIN_RANGE" and cmp_["excess_forward_lean"]["low"] < cmp_["excess_forward_lean"]["high"]
    rep = open(f"{w}/squat/report.md").read()
    assert "at most" in rep and "between" in rep and "Wrong if above: trunk leans far forward (low); below: trunk stays bolt upright (low)" in rep
    shutil.rmtree(w)


def test_calibrate_objective_labelled_and_one_sided():
    n = 22
    A = np.zeros((n, C.N_T, len(features.FEATURES)))
    rng = np.random.default_rng(0)
    vals = np.concatenate([rng.normal(0, 0.1, 10), np.full(6, -2.0) + rng.normal(0, 0.1, 6), np.full(6, 2.0) + rng.normal(0, 0.1, 6)])
    A[:, 24:27, 0] = vals[:, None]
    tags = ["good"] * 10 + ["miss"] * 12
    meta = [{"clip_id": f"c{i}", "tag": t, "view_yaw_deg": 0} for i, t in enumerate(tags)]
    both = C.calibrate_objective(A, meta, 0, 25, {"below", "above"}, tag="miss")
    assert both["basis"] == "labelled" and both["validated"] and both["low"] < -0.3 and both["high"] > 0.3 and abs(both["low"] + both["high"]) < 0.3, both
    one = C.calibrate_objective(A, meta, 0, 25, {"above"}, tag="miss")
    assert one["low"] is None and one["high"] is not None
    plain = C.calibrate_objective(A, [dict(m, tag="unlabelled") for m in meta], 0, 25, {"below"})
    assert plain["high"] is None and plain["low"] is not None and plain["basis"] == "everyday_footage" and not plain["validated"]


def test_a_bound_beyond_what_the_body_can_do_drops_out():
    assert C.within_limits(-16.0, 95.0, (0.0, 180.0)) == (None, 95.0)             # an angle cannot go below 0: that side can never be crossed
    assert C.within_limits(61.0, 196.0, (0.0, 180.0)) == (61.0, None)
    assert C.within_limits(10.0, 170.0, (0.0, 180.0)) == (10.0, 170.0)
    w = make_work(); _retag_unlabelled(w)
    prop = propose.stub_squat_proposal()
    prop["objectives"][2]["test"]["feature"] = "angle.hip.dom"                      # a hip angle is between 0 and 180
    prop["objectives"][2]["sides"] = {"below": {"looks_like": "x", "severity": "low"}, "above": {"looks_like": "y", "severity": "low"}}
    entry, checks = pipeline.build("squat", w, runs=1, proposer=lambda a, r: [prop])
    o = [x for x in entry["objectives"] if x["id"] == "excess_forward_lean"][0]
    lo, hi = o["tests"][0]["compare"].get("low"), o["tests"][0]["compare"].get("high")
    assert all(x is None or 0 <= x <= 180 for x in (lo, hi))
    assert status(checks)[5] == "pass"
    shutil.rmtree(w)


def test_range_allows_for_differences_between_videos():
    rng = np.random.default_rng(3)
    def clip(): return rng.normal(0, 1.0) + rng.normal(0, 0.1, 10)                      # a video: its own level, little spread inside
    pooled, clustered = [], []
    for _ in range(100):
        v = np.concatenate([clip() for _ in range(5)]); ids = np.repeat([f"r{i}" for i in range(5)], 10)
        new = np.concatenate([clip() for _ in range(60)])
        pooled.append((new > C.target_range(v, {"above"}, 5)[1]).mean())               # attempts treated as independent
        clustered.append((new > C.target_range(v, {"above"}, 5, ids)[1]).mean())
    assert np.mean(pooled) > 0.10 and 0.02 < np.mean(clustered) < 0.08, (np.mean(pooled), np.mean(clustered))    # nominal: 5% of new videos' attempts
    v = np.concatenate([clip() for _ in range(2)]); ids = np.repeat(["a", "b"], 10)
    assert C.target_range(v, {"above"}, 5, ids)[1] == np.percentile(v, 95)             # two videos only: plain percentiles


def test_stub_proposal_follows_the_schema():
    import jsonschema
    from sphere.schema import PROPOSAL_SCHEMA
    p = propose.stub_squat_proposal()
    assert not list(jsonschema.Draft202012Validator(PROPOSAL_SCHEMA).iter_errors(p))
    q = copy.deepcopy(p); q["objectives"][0]["sides"] = {}                            # an objective must say which way it can be wrong
    assert list(jsonschema.Draft202012Validator(PROPOSAL_SCHEMA).iter_errors(q))
    r = copy.deepcopy(p); r["objectives"][0]["test"]["direction"] = "above"           # no direction: the range has sides instead
    assert list(jsonschema.Draft202012Validator(PROPOSAL_SCHEMA).iter_errors(r))


def test_sources_are_rated_and_ranked():
    from sphere import sources as S
    items = _items()
    r = lambda i, t, sh: {"id": i, "tier": t, "shows": sh}
    client = FakeClient({"ratings": [r("a", "other", "unknown"), r("b", "instruction_talk", "unknown"), r("c", "coach_demo", "good_form"),
                                      r("d", "mistake_analysis", "mistakes"), r("e", "pro_footage", "good_form"), r("f", "practice_session", "good_form")]})
    S.rate("squat", items, client=client)
    assert [i["tier"] for i in items][:2] == ["other", "instruction_talk"]
    top = S.rank_for_footage(items, 4)
    ids = [i["id"] for i in top]
    assert "a" not in ids and len(ids) == 4                                  # 'other' only when nothing better is left
    assert "a" in [i["id"] for i in S.rank_for_footage(items, 6)]            # ... but it is not thrown away
    assert "d" in ids                                                        # a place is kept for footage of mistakes
    assert ids.index("c") < ids.index("b") if "b" in ids else True           # coach demonstration before a talk
    kn = S.rank_for_knowledge(items, 5, per_channel=1)
    assert [i["channel"] for i in kn].count("c1") <= 1 and all(i["tier"] in S.KNOWLEDGE_ORDER for i in kn)
    again = S.rate("squat", items, client=FakeClient({"ratings": []}))        # already rated: no second call needed
    assert all(i["tier"] for i in again)


def test_unrated_videos_are_kept():
    from sphere import sources as S
    items = _items()[:2]
    S.rate("squat", items, client=FakeClient({"ratings": []}))
    assert all(i["tier"] == "unrated" for i in items)
    assert len(S.rank_for_footage(items, 5)) == 2


def test_acquire_survives_a_failed_rating():
    from sphere import acquire, sources as S
    w = tempfile.mkdtemp()
    s0, d0, r0 = acquire.search, acquire.download, S.rate
    acquire.search = lambda q, n, **k: _items()
    acquire.download = lambda it, d: f"{d}/{it['id']}.mp4"
    S.rate = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no network"))
    try:
        got = acquire.acquire([{"query": "q", "kind": "good_form"}], w, "squat", max_videos=3)
        assert [g["id"] for g in got] == ["a", "b", "c"]                      # search order, nothing lost
    finally:
        acquire.search, acquire.download, S.rate = s0, d0, r0
    shutil.rmtree(w)


def test_captions_become_plain_speech():
    from sphere.knowledge import parse_vtt
    vtt = ("WEBVTT\nKind: captions\n\n00:00:01.000 --> 00:00:03.000\nknees go out over the\n\n"
           "00:00:03.000 --> 00:00:05.000\nknees go out over the\ntoes <c>not</c> inward\n\n00:00:05.000 --> 00:00:06.000\ntoes not inward\nkeep your chest up\n")
    assert parse_vtt(vtt) == "knees go out over the toes not inward keep your chest up", parse_vtt(vtt)


NOTE = {"about_this_activity": True, "good_form": ["chest up"], "faults": [
    {"name": "knees caving", "kind": "safety", "looks_like": "knees fall in", "why_it_matters": "strain", "causes": ["weak glutes"],
     "fixes": ["push knees out"], "outcome_effects": []}]}


def _map(kw):
    return {"good_form": [{"point": "chest up", "sources": [0, 1, 7]}], "faults": [
        {"id": "knees_cave", "description": "knees fall inward", "kind": "safety", "sources": [0, 1, 2, 9], "disagreement": "",
         "causes": [{"cause": "weak glutes", "proximity": "fundamental"}], "fixes": [{"idea": "push knees out", "type": "cue"}], "outcome_effects": []},
        {"id": "heels_lift", "description": "heels leave the floor", "kind": "form", "sources": [1], "disagreement": "one coach says it is fine",
         "causes": [], "fixes": [], "outcome_effects": []},
        {"id": "invented", "description": "made up", "kind": "form", "sources": [8, 9], "disagreement": "", "causes": [], "fixes": [], "outcome_effects": []}]}


def test_coaching_counts_come_from_real_sources():
    from sphere import knowledge as K
    m = K.merge("squat", [NOTE, NOTE, NOTE], client=FakeClient(_map))
    ids = {f["id"]: f for f in m["faults"]}
    assert "invented" not in ids                                              # cites sources that do not exist
    assert ids["knees_cave"]["n_sources"] == 3 and ids["knees_cave"]["support"] == "strong"      # source 9 does not exist: not counted
    assert ids["heels_lift"]["support"] == "single" and ids["heels_lift"]["disagreement"]
    assert m["good_form"][0]["n_sources"] == 2


def test_merge_says_why_it_failed_and_learn_keeps_the_notes():
    from sphere import knowledge as K
    bad = {"good_form": [], "faults": [{"id": "Bad Id!", "description": "x", "kind": "form", "sources": [0], "causes": [], "fixes": [], "outcome_effects": [], "disagreement": ""}]}
    try:
        K.merge("squat", [NOTE, NOTE], client=FakeClient(bad))
        raise AssertionError("expected a failure")
    except RuntimeError as e:
        assert "group" in str(e) or "merged" in str(e), str(e)                  # it says what failed, it does not hide it
    w = tempfile.mkdtemp()
    vids = [{"id": f"v{i}", "title": f"c{i}", "channel": f"ch{i}", "duration": 300, "url": f"u{i}"} for i in range(3)]
    rate = {"ratings": [{"id": v["id"], "tier": "instruction_talk", "shows": "unknown"} for v in vids]}
    state = {"merge": 0}
    def answer(kw):
        if "submit_ratings" in str(kw["tools"]): return rate
        if "submit_notes" in str(kw["tools"]): return NOTE
        state["merge"] += 1
        return bad if state["merge"] <= 3 else _map(kw)                       # the merge fails (3 tries), then works on the second run
    args = dict(n_videos=3, client=FakeClient(answer), search=lambda q, n, **kw: vids, transcripts=lambda u: "t" * 500, log=lambda *a: None)
    try:
        K.learn("squat", w, **args)
        raise AssertionError("expected the first merge to fail")
    except RuntimeError:
        pass
    assert os.path.exists(f"{w}/squat/coaching_notes.json")                   # the reading was not lost
    calls = len(args["client"].calls)
    k = K.learn("squat", w, **args)
    assert k["n_sources"] == 3 and len(args["client"].calls) == calls + 1      # only the merge ran again
    shutil.rmtree(w)


def test_merge_survives_a_dropped_connection():
    from sphere import knowledge as K
    K.time.sleep = lambda s: None                                                          # no waiting in the test
    notes = [dict(NOTE, faults=[dict(NOTE["faults"][0])]) for _ in range(3)]
    def answer(kw):
        t = str(kw["tools"])
        if "submit_map" in t: raise ConnectionError("Server disconnected without sending a response")
        if "submit_clusters" in t:
            return {"clusters": [{"id": "knees_cave", "members": [{"source": i, "fault": 0} for i in range(3)]}]}
        if "submit_fault" in t:
            return {"description": "d", "kind": "form", "causes": [], "fixes": [], "outcome_effects": [], "disagreement": ""}
        return {"good_form": [{"point": "chest up", "sources": [0, 1]}]}
    m = K.merge("squat", notes, client=FakeClient(answer))
    assert [f["id"] for f in m["faults"]] == ["knees_cave"] and m["faults"][0]["n_sources"] == 3


def test_merge_in_smaller_steps_when_one_answer_fails():
    from sphere import knowledge as K
    notes = [dict(NOTE, faults=[dict(NOTE["faults"][0]), dict(NOTE["faults"][0], name="heels up", kind="form")]) for _ in range(3)]
    def answer(kw):
        t = str(kw["tools"])
        if "submit_map" in t: return {"good_form": [], "faults": []}                  # one-step merge: nonsense (no usable cluster), falls through
        if "submit_clusters" in t:
            return {"clusters": [{"id": "knees_cave", "members": [{"source": i, "fault": 0} for i in range(3)]},
                                  {"id": "heels_up", "members": [{"source": 0, "fault": 1}, {"source": 9, "fault": 0}]},   # source 9 does not exist
                                  {"id": "ghost", "members": [{"source": 7, "fault": 7}]}]}
        if "submit_fault" in t:
            return {"description": "d", "kind": "safety", "causes": [], "fixes": [], "outcome_effects": [], "disagreement": ""}
        return {"good_form": [{"point": "chest up", "sources": [0, 1]}]}
    class Broken(FakeClient):
        def create(self, **kw):
            if "submit_map" in str(kw["tools"]):
                self.calls.append(kw)
                return type("R", (), {"content": [], "stop_reason": "max_tokens"})()            # the long answer is cut off every time
            return super().create(**kw)
    m = K.merge("squat", notes, client=Broken(answer))
    ids = {f["id"]: f for f in m["faults"]}
    assert set(ids) == {"knees_cave", "heels_up"}, ids                                  # the ghost group has no real members
    assert ids["knees_cave"]["n_sources"] == 3 and ids["heels_up"]["n_sources"] == 1    # counts come from the real members
    assert m["good_form"][0]["n_sources"] == 2


def test_safety_needs_more_than_one_source():
    from sphere import knowledge as K
    m = K.merge("squat", [NOTE, NOTE, NOTE], client=FakeClient(lambda kw: {**_map(kw), "faults": [
        dict(_map(kw)["faults"][0]),                                                              # safety, 3 sources, uncontested
        dict(_map(kw)["faults"][0], id="one_source", sources=[0]),                               # safety claimed by one source
        dict(_map(kw)["faults"][0], id="disputed", disagreement="others say it is fine")]}))     # safety but disputed
    kinds = {f["id"]: K.effective_kind(f) for f in m["faults"]}
    assert kinds == {"knees_cave": "safety", "one_source": "form", "disputed": "form"}, kinds


def test_learn_reads_captions_and_keeps_only_notes():
    from sphere import knowledge as K, sources as S
    w = tempfile.mkdtemp()
    vids = [{"id": f"v{i}", "title": f"coach {i}", "channel": f"ch{i}", "duration": 300, "url": f"u{i}"} for i in range(5)]
    ratings = {"ratings": [{"id": v["id"], "tier": "mistake_analysis", "shows": "mixed"} for v in vids]}
    client = FakeClient(lambda kw: ratings if "submit_ratings" in str(kw["tools"]) else NOTE if "submit_notes" in str(kw["tools"]) else _map(kw))
    texts = {"u0": "x" * 500, "u1": None, "u2": "y" * 500, "u3": "z" * 500, "u4": "w" * 500}
    k = K.learn("squat", w, n_videos=3, client=client, search=lambda q, n, **kw: vids, transcripts=lambda u: texts[u], log=lambda *a: None)
    assert k["n_sources"] == 3 and len(k["sources"]) == 3                      # v1 had no captions and was skipped
    saved = json.load(open(f"{w}/squat/knowledge.json"))
    assert "xxxxx" not in json.dumps(saved)                                   # the transcript itself is not kept
    assert K.for_prompt(saved).startswith("WHAT COACHES SAY (3")
    n = len(client.calls)
    k2 = K.learn("squat", w, n_videos=3, client=client, search=lambda q, n, **kw: vids, transcripts=lambda u: texts[u], log=lambda *a: None)
    assert len(client.calls) == n and k2["faults"] == k["faults"]                # run again: the same notes are not merged again, so the fault names stay put
    shutil.rmtree(w)


def test_build_uses_coaching_and_only_coaches_make_safety():
    from sphere import knowledge as K
    w = make_work()
    kmap = K._count(_map(None), 3)
    kmap["sources"] = [{"id": "v0"}, {"id": "v1"}, {"id": "v2"}]
    json.dump(kmap, open(f"{w}/squat/knowledge.json", "w"))
    seen = {}
    def stub_with_prompt(act, r):
        return [propose.stub_squat_proposal() for _ in range(r)]
    def linker(k, efs):
        seen["efs"] = [e["id"] for e in efs]
        return ({"knees_cave": {"objective": "knee_cave", "measurable": "measured", "note": ""},
                 "heels_lift": {"objective": None, "measurable": "needs_new_feature", "note": "heel_lift"}}, ["shallow_depth", "excess_forward_lean"])
    entry, checks = pipeline.build("squat", w, runs=1, proposer=stub_with_prompt, linker=linker)
    kinds = {f["id"]: f["kind"] for f in entry["objectives"]}
    assert kinds["knee_cave"] == "safety" and kinds["shallow_depth"] == "form", kinds       # only a coach-named risk is safety
    co = entry["coaching"]
    assert co["n_sources"] == 3 and {f["id"] for f in co["faults"]} == {"knees_cave", "heels_lift"}
    assert [c for c in checks if c["id"] == 1][0]["status"] == "pass"
    rep = open(f"{w}/squat/report.md").read()
    assert "What coaches say" in rep and "would need a new body feature" in rep and "named by no coach" in rep
    shutil.rmtree(w)


def test_proposal_prompt_carries_the_coaches_map():
    from sphere import knowledge as K
    kmap = K._count(_map(None), 3)
    p = propose.build_prompt("squat", None, K.for_prompt(kmap))
    assert "WHAT COACHES SAY" in p and "knees_cave [safety, named by 3 of 3]" in p
    assert "WHAT COACHES SAY" not in propose.build_prompt("squat")


def test_cap_per_clip():
    cols = [C.collect_attempts(synth.squat_clip(reps=8, seed=1), SQ, SQ_PRIM)]
    cols[0]["attempts"] = cols[0]["attempts"] * 4
    assert len(C.cap_per_clip(cols, 10)[0]["attempts"]) == 10


def test_end_to_end_all_pass():
    w = make_work()
    entry, checks = pipeline.build("squat", w, runs=2, proposer=stub)
    assert all(c["status"] == "pass" for c in checks if c["id"] != 10), status(checks)       # principles need coaching knowledge: tested separately
    assert entry["objectives"][0]["id"] == "knee_cave"       # high severity, no cause, first
    shutil.rmtree(w)


def test_unlabelled_is_not_validated():
    w = make_work()
    for f in os.listdir(f"{w}/squat/clips"):
        d = np.load(f"{w}/squat/clips/{f}", allow_pickle=True)
        clip = skeleton.load_clip(f"{w}/squat/clips/{f}"); clip["meta"]["tag"] = "unlabelled"
        skeleton.save_clip(f"{w}/squat/clips/{f}", clip)
    entry, checks = pipeline.build("squat", w, runs=1, proposer=stub)
    s = status(checks)
    assert s[6] == "not_testable" and s[8] == "not_testable", s
    assert entry["metadata"]["confidence_tier"] == "low"
    assert all(f["detection"]["reliability"] == "C" for f in entry["objectives"])
    shutil.rmtree(w)


def test_checks_reject_bad_entries():
    w = make_work()
    entry, _ = pipeline.build("squat", w, runs=2, proposer=stub)
    base = {k: v for k, v in entry.items()}
    # free text instead of a structured comparison
    e = copy.deepcopy(base); e["objectives"][0]["tests"][0]["compare"] = "above 0.8 x arm_length"
    assert status(run_checks(e))[1] == "fail"
    # unknown feature
    e = copy.deepcopy(base); e["objectives"][0]["tests"][0]["feature"] = "angle.made_up"
    assert status(run_checks(e))[1] == "fail"
    # deferred measurement
    e = copy.deepcopy(base); e["objectives"][0]["tests"][0]["measure"] = "M15"
    assert status(run_checks(e))[2] == "fail"
    # a cause that comes after its effect
    e = copy.deepcopy(base)
    for f in e["objectives"]:
        if f["id"] == "shallow_depth": f["priority"] = 9
    assert status(run_checks(e))[9] == "fail"
    # unknown cause id
    e = copy.deepcopy(base); e["objectives"][0]["caused_by"] = ["nonexistent"]
    assert status(run_checks(e))[9] == "fail"
    # implausible threshold
    e = copy.deepcopy(base); e["objectives"][0]["tests"][0]["compare"]["value"] = 50.0
    assert status(run_checks(e))[5] == "fail"
    # a heavy-model measure on a per-frame budget
    e = copy.deepcopy(base); t = e["objectives"][0]["tests"][0]; t["measure"] = "M16"; t["time_budget"] = "per_frame"
    assert status(run_checks(e))[3] == "fail"
    # recognition: an unrelated activity must not be accepted
    shutil.rmtree(w)


def test_insufficient_data():
    cols = [C.collect_attempts(synth.squat_clip(reps=3, seed=0), SQ, SQ_PRIM)]
    try:
        build_entry(propose.stub_squat_proposal(), cols)
    except InsufficientData:
        return
    raise AssertionError("expected InsufficientData")


def test_recognition_rejects_other_activity():
    w = make_work()
    entry, _ = pipeline.build("squat", w, runs=1, proposer=stub)
    far = entry["recognition"]["accuracy"]["false_accept_rate_vs_other_activities"]
    assert far is not None and far <= 0.15, far
    shutil.rmtree(w)


def test_windows_follow_attempts_through_processing():
    w = make_work()
    cols, *_ = pipeline.prepare(f"{w}/squat/clips", SQ, SQ_PRIM)
    assert any(c["attempts"] for c in cols)
    for c in cols:
        assert len(c["windows"]) == len(c["attempts"])
        assert all(b > a >= 0 for a, b in c["windows"])
    A, meta = C.stack([c for c in cols if c["usable"]])
    assert len(meta) == len(A) and all(m["window"] for m in meta)
    cols = C.cap_per_clip(cols, 3)                              # a cut that keeps only some attempts keeps their windows with them
    assert all(len(c["windows"]) == len(c["attempts"]) <= 3 for c in cols)
    shutil.rmtree(w)


def test_timed_captions_drop_the_scrolling_repeats():
    from sphere import knowledge as K, labelling as LB
    vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000 align:start\nhello there\n\n00:00:03.000 --> 00:00:05.000\nhello there\nnow watch the <c>knees</c>\n\n00:00:65.000 --> 00:01:07.000\nthey cave in\n"
    cues = K.parse_vtt_timed(vtt)
    assert cues[0] == (1.0, 3.0, "hello there") and cues[1][2] == "now watch the knees" and cues[2][0] == 65.0
    t = LB.transcript_text(cues, span=2)
    assert t.startswith("[0:01] hello there") and "[1:05] they cave in" in t


def test_mistake_footage_is_chosen_for_showing_mistakes():
    from sphere import labelling as LB
    mk = lambda i, tier, shows, ch: {"id": i, "tier": tier, "shows": shows, "channel": ch}
    items = [mk("a", "coach_demo", "good_form", "c1"), mk("b", "mistake_analysis", "mistakes", "c2"), mk("c", "coach_demo", "mixed", "c3"),
             mk("d", "other", "mistakes", "c4"), mk("e", "mistake_analysis", "mixed", "c1")]
    got = [it["id"] for it in LB.rank_for_labelling(items, 10)]
    assert got == ["e", "c", "b"], got                          # mixed first; good-form and unrelated videos are not taken
    qs = LB.mistake_queries("bodyweight_squat", {"faults": [{"id": "knees_cave", "n_sources": 3}, {"id": "heels_lift", "n_sources": 1}]})
    assert any("knees cave" in q["query"] for q in qs) and all(q["query"].startswith("bodyweight squat") for q in qs)


def test_label_lookup_by_overlap_and_tags():
    from sphere import labelling as LB
    lab = {"clips": {"v": {"attempts": [{"window": [2.0, 5.0], "not_an_attempt": False, "present": ["a"], "absent": ["b"]},
                                        {"window": [6.0, 9.0], "not_an_attempt": False, "present": [], "absent": ["a", "b"]},
                                        {"window": [10.0, 12.0], "not_an_attempt": True, "present": [], "absent": []}]}}}
    assert LB.find(lab, "v", (2.2, 5.1))["present"] == ["a"] and LB.find(lab, "v", (6.2, 8.8)) is not None
    assert LB.find(lab, "v", (20.0, 22.0)) is None and LB.find(lab, "w", (2.0, 5.0)) is None
    meta = [{"clip_id": "v", "window": w} for w in ((2.1, 5.0), (6.0, 9.0), (10.0, 12.0), (30.0, 33.0))]
    f = LB.tags_for(lab, {"obj": ["a"], "two": ["a", "b"]})
    assert f("obj", meta) == ["bad", "good", "unlabelled", "unlabelled"]
    assert f("two", meta) == ["bad", "good", "unlabelled", "unlabelled"] and f("none", meta) is None


def _labelling_work():
    from sphere import knowledge as K
    w = make_work()
    ids = sorted(f[:-4] for f in os.listdir(f"{w}/squat/clips"))
    json.dump([{"id": skeleton.load_clip(f"{w}/squat/clips/{i}.npz")["meta"]["id"], "title": i, "channel": i, "url": "u" + i, "tier": "mistake_analysis", "shows": "mixed"}
               for i in ids], open(f"{w}/squat/sources.json", "w"))
    os.makedirs(f"{w}/squat/videos")
    for i in ids:
        open(f"{w}/squat/videos/{skeleton.load_clip(f'{w}/squat/clips/{i}.npz')['meta']['id']}.mp4", "w").close()
    json.dump({"primary_features": SQ_PRIM, "attempt_events": SQ, "events_rule": 6}, open(f"{w}/squat/prior.json", "w"))
    kmap = K._count(_map(None), 3)
    kmap["sources"] = [{"id": "v0"}, {"id": "v1"}, {"id": "v2"}]
    json.dump(kmap, open(f"{w}/squat/knowledge.json", "w"))
    return w


def _picture_client():
    """A stand-in for the model that 'sees' the clip through the frame it is shown: knee cave in the clips named c*, none elsewhere."""
    def answer(kw):
        blocks = kw["messages"][0]["content"]
        clip = [b["source"]["data"] for b in blocks if b["type"] == "image"][0]
        n = sum(1 for b in blocks if b["type"] == "text" and b["text"].startswith("Attempt "))
        bad = "knee_cave" in clip
        return {"attempts": [{"n": k, "not_an_attempt": False, "present": ["knees_cave"] if bad else [], "absent": [] if bad else ["knees_cave"]} for k in range(1, n + 1)]}
    return FakeClient(answer)


def test_labelling_run_and_labels_calibrate_the_objective():
    from sphere import labelling as LB
    w = _labelling_work()
    cli = _picture_client()
    frames = lambda vid, a, b: ([os.path.basename(vid)], [round(a, 1)])
    cues = lambda url: [(0.0, 4.0, "watch the knees")]
    lab, est = LB.label_activity("squat", w, client=cli, estimate_only=True, log=lambda *_: None, frames=frames, cues=cues)
    assert not cli.calls and est["clips"] >= 8 and est["attempts"] > 40          # an estimate calls nothing
    lab, _ = LB.label_activity("squat", w, client=cli, log=lambda *_: None, frames=frames, cues=cues)
    assert len(cli.calls) == est["clips"] and os.path.exists(f"{w}/squat/labels.json")
    assert "watch the knees" not in open(f"{w}/squat/labels.json").read()           # captions are not kept
    n_calls = len(cli.calls)
    LB.label_activity("squat", w, client=cli, log=lambda *_: None, frames=frames, cues=cues)
    assert len(cli.calls) == n_calls                                               # a finished run is not repeated
    stale = json.load(open(f"{w}/squat/labels.json"))
    for rec in stale["clips"].values():
        for a in rec["attempts"]:
            a["window"] = [a["window"][0] + 500, a["window"][1] + 500]                 # as if the videos had been cut differently when labelled
    json.dump(stale, open(f"{w}/squat/labels.json", "w"))
    LB.label_activity("squat", w, client=cli, log=lambda *_: None, frames=frames, cues=cues)
    assert len(cli.calls) == 2 * n_calls                                           # labels that fit none of today's attempts are made again
    linker = lambda k, efs: ({"knees_cave": {"objective": "knee_cave", "measurable": "measured", "note": ""},
                             "heels_lift": {"objective": None, "measurable": "not_visible", "note": ""}}, [])
    entry, checks = pipeline.build("squat", w, runs=1, proposer=stub, linker=linker)
    kc = [o for o in entry["objectives"] if o["id"] == "knee_cave"][0]["calibration"]
    assert kc["basis"] == "labelled" and kc["n_bad"] >= 3 and kc["n_good"] >= 3, kc
    assert kc["n_bad_clips"] >= 3 and kc["held_out_accuracy"] is not None
    assert entry["metadata"]["provenance"]["labels"]["per_fault"]["knees_cave"]["videos_present"] >= 3
    rep = open(f"{w}/squat/report.md").read()
    assert "Check against labelled mistake videos" in rep and "knees_cave" in rep
    shutil.rmtree(w)


def test_calibration_is_checked_on_videos_it_was_not_fitted_on():
    rng = np.random.default_rng(3)
    n = 60
    A = np.zeros((n, C.N_T, len(features.FEATURES)))
    cid = np.array([f"v{i // 10}" for i in range(n)])
    tag = np.array(["good", "bad"] * (n // 2))
    sep = np.where(tag == "bad", 20.0, 0.0) + rng.normal(0, 3, n)
    A[:, :, 5] = sep[:, None]
    meta = [{"clip_id": c, "tag": t, "view_yaw_deg": 0.0} for c, t in zip(cid, tag)]
    good = C.calibrate_objective(A, meta, 5, 25, {"above"}, tag="bad")
    assert good["basis"] == "labelled" and good["validated"] and good["held_out_accuracy"] >= 0.9
    A2 = A.copy(); A2[:, :, 5] = rng.normal(0, 3, n)[:, None]               # nothing separates them
    flat = C.calibrate_objective(A2, meta, 5, 25, {"above"}, tag="bad")
    assert not flat["validated"]


def test_link_labels_tell_a_missing_tracker_from_the_unseeable():
    from sphere import knowledge as K
    kmap = K._count(_map(None), 3)
    resp = {"links": [{"fault": "knees_cave", "objective": None, "measurable": "needs_new_tracker", "note": "hand and racket tracker"},
                      {"fault": "heels_lift", "objective": None, "measurable": "not_visible", "note": "ignored"}]}
    out, _ = K.link(kmap, [{"id": "shallow_depth", "goal": "g", "feature": "height.hip"}], {"height.hip": "x"}, "squat", client=FakeClient(resp))
    assert out["knees_cave"] == {"objective": None, "measurable": "needs_new_tracker", "note": "hand and racket tracker"}
    assert out["heels_lift"]["measurable"] == "not_visible" and out["heels_lift"]["note"] == ""


def test_attempts_confirmed_by_looking_survive_every_filter():
    w = make_work()
    raw = pipeline.load_collections(f"{w}/squat/clips", SQ, None, SQ_PRIM)
    target = [c for c in raw if "shallow" in c["clip_id"]][0]
    win = tuple(target["windows"][0])
    trusted = lambda cid, window: cid == target["clip_id"] and tuple(window) == win
    cols, *_ = pipeline.prepare(f"{w}/squat/clips", SQ, SQ_PRIM, trusted=trusted)
    got = [c for c in cols if c["clip_id"] == target["clip_id"]][0]
    assert win in [tuple(x) for x in got["windows"]] and got["usable"]
    plain, *_ = pipeline.prepare(f"{w}/squat/clips", SQ, SQ_PRIM)
    assert len([c for c in cols for _ in c["attempts"]]) >= len([c for c in plain for _ in c["attempts"]])
    others = [c for c in raw if c is not target][:3]
    small = dict(target, prominence=[0.01] * len(target["attempts"]))
    sg, _ = C.size_gate([small] + others, trusted=trusted)
    assert len(sg[0]["attempts"]) == 1 and sg[0]["usable"]
    assert len(C.size_gate([small] + others)[0][0]["attempts"]) == 0          # too small to be kept by size, kept because it was confirmed
    shutil.rmtree(w)


def test_labelled_cut_is_used_only_after_it_works_on_other_videos():
    rng = np.random.default_rng(5)
    n = 40
    A = np.zeros((n, C.N_T, len(features.FEATURES)))
    cid = np.array(["v0"] * 3 + [f"g{i // 6}" for i in range(n - 3)])           # all 3 wrong examples come from one video
    tag = np.array(["bad"] * 3 + ["good"] * (n - 3))
    A[:, :, 5] = (np.where(tag == "bad", 20.0, 0.0) + rng.normal(0, 2, n))[:, None]
    meta = [{"clip_id": c, "tag": t, "view_yaw_deg": 0.0} for c, t in zip(cid, tag)]
    cal = C.calibrate_objective(A, meta, 5, 25, {"above"}, tag="bad")
    assert cal["basis"] == "everyday_footage" and not cal["validated"]           # not tested on a video it was not fitted on: range not taken from it
    assert cal["labelled"]["auc"] >= 0.9 and cal["labelled"]["held_out_accuracy"] is None and cal["labelled"]["n_bad_clips"] == 1


# ---------------------------------------------------------------- coaching engine
def _squat_entry():
    w = make_work()
    entry, _ = pipeline.build("squat", w, runs=1, proposer=stub)
    shutil.rmtree(w)
    return entry


def test_engine_judge_and_unknown_view():
    from sphere import engine
    assert engine.judge({"op": "WITHIN_RANGE", "low": 1, "high": 2}, 0.5)[:2] == (False, "below")
    assert engine.judge({"op": "LESS_OR_EQUAL", "value": 2}, 3)[:2] == (False, "above")
    assert engine.judge({"op": "GREATER_OR_EQUAL", "value": 2}, 3)[0] is True
    assert engine.judge({"op": "LESS_OR_EQUAL", "value": 2}, float("nan"))[0] is None
    entry = _squat_entry()
    names, atts = engine.attempts_in(entry, synth.squat_clip(yaw=40, seed=3))
    assert len(atts) >= 6
    res = engine.evaluate(entry, atts[2]["arr"], names, atts[2]["yaw"])
    assert set(res) == {o["id"] for o in entry["objectives"]}
    far = engine.evaluate(entry, atts[2]["arr"], names, yaw=170.0)
    assert all(r["status"] == "unknown" and r["why"] == "view" for r in far.values())


def test_engine_policy_cues_after_persistent_miss_then_waits_then_praises():
    from sphere import engine
    entry = _squat_entry()
    o = entry["objectives"][0]["id"]
    others = [x["id"] for x in entry["objectives"][1:]]
    def res(status):
        r = {i: {"status": "met", "side": None, "value": 0, "overshoot": 0} for i in others}
        r[o] = {"status": status, "side": "below" if status == "missed" else None, "value": 0, "overshoot": 1.0 if status == "missed" else 0}
        return r
    pol = engine.Policy(entry)
    out = [pol.update(res("missed")) for _ in range(5)]
    assert out[0] is None and out[1] is None and out[2]["kind"] == "cue" and out[2]["objective"] == o
    assert out[3] is None and out[4] is None                                  # cooldown: not repeated straight away
    again = pol.update(res("missed"))                                        # still missing after the cooldown: it is said again
    assert again and again["kind"] == "cue" and again["objective"] == o
    pol2 = engine.Policy(entry)
    for _ in range(3): pol2.update(res("missed"))
    # streak of met after a cue: the second one earns praise, once
    got = [pol2.update(res("met")) for _ in range(4)]
    assert sum(1 for g in got if g and g["kind"] == "praise") == 1


def test_engine_wording_offline_and_with_a_model():
    from sphere import engine
    entry = _squat_entry()
    o = entry["objectives"][0]
    dec = {"kind": "cue", "objective": o["id"], "side": next(iter(o["sides"])), "why": {}}
    txt = engine.Wording(entry).say(dec)
    assert txt and not txt.startswith("Cue ")
    class R:  # a stand-in for the model client
        class B: type = "text"; text = '"Push your knees out."'
        content = [B()]
    class Cl:
        class messages:
            seen = []
            @staticmethod
            def create(**kw): Cl.messages.seen.append(kw); return R()
    w = engine.Wording(entry, client=Cl())
    assert w.say(dec) == "Push your knees out."
    w.say(dec)
    assert "reminder number 2" in Cl.messages.seen[-1]["messages"][0]["content"]
    class Bad:
        class messages:
            @staticmethod
            def create(**kw): raise RuntimeError("offline")
    assert engine.Wording(entry, client=Bad()).say(dec) == txt                  # a failing model never silences the coach


def test_engine_session_judges_each_attempt_once_and_cues_the_planted_fault():
    from sphere import engine
    entry = _squat_entry()
    good = synth.squat_clip(reps=8, yaw=40, seed=31, tag="good")
    ev, log = engine.run_clip(entry, good)
    n_good = len(log)
    assert n_good >= 6 and len({round(r["start"], 1) for r in log}) == n_good           # no attempt judged twice
    assert not [e for e in ev if e["kind"] == "cue"], ev
    bad = synth.squat_clip(reps=10, yaw=40, seed=32, tag="shallow_depth", depth=0.5)
    ev, log = engine.run_clip(entry, bad)
    cues = [e for e in ev if e["kind"] == "cue"]
    assert cues and cues[0]["t"] > 0 and all(e["text"] for e in cues)
    assert all(b["t"] - a["t"] > 3 for a, b in zip(cues, cues[1:]) if a["objective"] == b["objective"])


def test_events_must_follow_each_other_not_happen_together():
    names = features.FEATURES
    fps = 30.0
    t = np.arange(int(12 * fps)) / fps
    bump = lambda c: np.exp(-((t - c) / 0.25) ** 2) * 1.6 - 0.6
    ev = [{"feature": "height.wrist.non", "direction": "rises", "peak_at_least": 0.8}, {"feature": "height.wrist.dom", "direction": "rises", "peak_at_least": 0.8}]
    mk = lambda a, b: np.stack([a if n == "height.wrist.non" else b if n == "height.wrist.dom" else np.zeros(len(t)) for n in names], axis=1)
    prim = ["height.wrist.non", "height.wrist.dom"]
    assert len(segment_attempts(mk(bump(4.0), bump(4.8)), fps, names, ev, prim)["attempts"]) == 1      # toss, then hit
    assert len(segment_attempts(mk(bump(4.0), bump(4.05)), fps, names, ev, prim)["attempts"]) == 0     # both hands up at once: not a serve


def test_a_rally_is_cut_into_single_strokes_when_the_events_say_how_long_they_take():
    names = features.FEATURES
    fps = 30.0
    t = np.arange(int(40 * fps)) / fps
    turn = sum(np.exp(-((t - c) / 0.4) ** 2) for c in (5, 9, 13, 17, 21, 25)) * 60            # the coil before each stroke (one slow, huge one first)
    turn = turn + np.exp(-((t - 3.0) / 3.0) ** 2) * 90
    swing = sum(np.exp(-((t - (c + 1.0)) / 0.3) ** 2) for c in (5, 9, 13, 17, 21, 25)) * 0.9
    F = np.zeros((len(t), len(names)))
    F[:, names.index("angle.shoulder_hip_twist")] = turn
    F[:, names.index("height.wrist.dom")] = swing
    prim = ["angle.shoulder_hip_twist", "height.wrist.dom"]
    ev = lambda sec: [{"feature": "angle.shoulder_hip_twist", "direction": "rises", **sec}, {"feature": "height.wrist.dom", "direction": "rises", "peak_at_least": 0.5, **sec}]
    cut = segment_attempts(F, fps, names, ev({"seconds": 1.0}), prim)
    assert len(cut["attempts"]) == 6 and max(cut["duration"]) < 4.5                         # one stroke each, not a stretch of several
    loose = segment_attempts(F, fps, names, ev({}), prim)
    assert max(loose["duration"]) > max(cut["duration"])                                    # without the durations the windows run on


def test_labels_made_under_earlier_fault_names_are_matched_to_the_current_ones():
    from sphere import labelling as LB
    faults = [{"id": "arm_only_takeback", "description": "x"}, {"id": "late_prep", "description": "y"}]
    mk = lambda pres, ab: {"window": [0, 1], "not_an_attempt": False, "present": pres, "absent": ab}
    lab = {"clips": {"c": {"attempts": [mk(["arm_only_take_back"], ["late_prep", "poor_spacing"]), mk([], ["arm_only_take_back"])]}}}
    cli = FakeClient({"matches": [{"old": "arm_only_take_back", "current": "arm_only_takeback"}, {"old": "poor_spacing", "current": None}]})
    assert LB.reconcile(lab, faults, client=cli) == 2
    a, b = lab["clips"]["c"]["attempts"]
    assert a["present"] == ["arm_only_takeback"] and a["absent"] == ["late_prep"] and b["absent"] == ["arm_only_takeback"]
    n = len(cli.calls)
    assert LB.reconcile(lab, faults, client=cli) == 0 and len(cli.calls) == n    # decided once, kept in the file


def test_a_contested_principle_without_a_competing_view_is_dropped_not_kept():
    from sphere import principles as PR
    _, entry, _ = _squat_with_principles()
    p = dict(entry["principles"][0], basis="contested", alternatives=[])
    kept, dropped = PR.clean([p], entry)
    assert kept == [] and "competing" in dropped[0]["why"]


def _squat_with_principles():
    from sphere import knowledge as K
    w = make_work()
    kmap = K._count(_map(None), 3)
    kmap["sources"] = [{"id": "v0"}, {"id": "v1"}, {"id": "v2"}]
    json.dump(kmap, open(f"{w}/squat/knowledge.json", "w"))
    linker = lambda k, efs: ({"knees_cave": {"objective": "knee_cave", "measurable": "measured", "note": ""},
                              "heels_lift": {"objective": None, "measurable": "needs_new_feature", "note": "heel_lift"}}, [])
    gen = lambda act, entry, knowledge, model: propose.stub_squat_principles()
    entry, checks = pipeline.build("squat", w, runs=1, proposer=stub, linker=linker, principler=gen)
    return w, entry, checks


def test_principles_are_built_checked_and_reported():
    from sphere import principles as PR
    w, entry, checks = _squat_with_principles()
    assert {p["id"] for p in entry["principles"]} == {"stable_base", "depth_gives_range"} and all(p["support"] == 3 for p in entry["principles"])
    assert [c for c in checks if c["id"] == 10][0]["status"] == "pass" and not any(c["status"] == "fail" for c in checks), status(checks)
    assert "## Principles" in open(f"{w}/squat/report.md").read()
    assert PR.for_objective(entry, "shallow_depth")["id"] == "depth_gives_range" and PR.for_objective(entry, "excess_forward_lean") is None
    bad = copy.deepcopy(entry)
    bad["principles"][0]["handle_intent"] = "squeeze the knees outward"                       # names a body part
    bad["principles"][1]["statement"] = "This is the safe way to squat."                       # a safety claim
    bad["principles"].append(dict(bad["principles"][0], id="p3", handle_intent="stay wide", basis="contested"))   # contested without alternatives
    probs = PR.problems(bad)
    assert any("body part" in x for x in probs) and any("safety" in x for x in probs) and any("alternatives" in x for x in probs), probs
    assert [c for c in run_checks(bad) if c["id"] == 10][0]["status"] == "fail"
    shutil.rmtree(w)


def test_principles_need_agreement_and_real_references():
    from sphere import principles as PR
    w, entry, _ = _squat_with_principles()
    a = [dict(propose.stub_squat_principles()[0]), dict(propose.stub_squat_principles()[1])]
    b = [dict(propose.stub_squat_principles()[0], id="same_idea_other_name")]
    c = [dict(propose.stub_squat_principles()[0], id="third")]
    got = PR.merge([a, b, c])
    assert [p["id"] for p in got] == ["stable_base"] and got[0]["support"] == 3                 # the idea three runs reach; the one run's idea is dropped
    junk = dict(a[0], id="ghost", explains=["not_a_thing"])
    kept, dropped = PR.clean([junk, a[0]], entry)
    assert [p["id"] for p in kept] == ["stable_base"] and dropped[0]["id"] == "ghost"
    shutil.rmtree(w)


def test_engine_points_at_the_principle_and_explains_it_on_request():
    from sphere import engine
    w, entry, _ = _squat_with_principles()
    o = next(x for x in entry["objectives"] if x["id"] == "shallow_depth")
    dec = {"kind": "cue", "objective": "shallow_depth", "side": next(iter(o["sides"])), "why": {}}
    wd = engine.Wording(entry)
    assert wd.say(dec) == "Sink into the bottom of the movement."                              # the effect-focused handle, not the body-part cue
    assert "full range" in wd.why("shallow_depth") and wd.why("excess_forward_lean") is None
    s = engine.Session(entry, wording=wd)
    s.last_cue, s.last_end, s.t = "shallow_depth", 10.0, 40.0
    ev = s._rest_offer()
    assert ev and ev[0]["kind"] == "principle" and s._rest_offer() == []                         # offered once, at a rest
    s2 = engine.Session(entry, wording=wd); s2.last_cue, s2.last_end, s2.t = "shallow_depth", 10.0, 15.0
    assert s2._rest_offer() == []                                                                 # not while the player is still practising
    shutil.rmtree(w)


def test_caption_fetch_waits_out_rate_limits_and_does_not_retry_missing_captions():
    import sys, time, types
    from sphere import knowledge as K
    calls = {"n": 0}
    script = ["limit", "limit", "ok"]
    class YDL:
        def __init__(self, opts): self.opts = opts
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def download(self, urls):
            what = script[min(calls["n"], len(script) - 1)]; calls["n"] += 1
            if what == "limit":
                self.opts["logger"].error("ERROR: Unable to download video subtitles for 'en': HTTP Error 429: Too Many Requests")
            elif what == "ok":
                open(os.path.join(os.path.dirname(self.opts["outtmpl"]), "x.en.vtt"), "w").write("WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nhello\n")
    fake = types.ModuleType("yt_dlp"); fake.YoutubeDL = YDL
    old, slept = sys.modules.get("yt_dlp"), []
    sys.modules["yt_dlp"] = fake
    real_sleep = time.sleep
    K.CAPTION_STATS.update(fetched=0, none=0, rate_limited=0)
    time.sleep = lambda s: slept.append(s)
    try:
        assert "hello" in K.fetch_vtt("u")
        assert calls["n"] == 3 and K.CAPTION_STATS["fetched"] == 1 and max(slept) >= 40          # waited longer after each refusal
        calls["n"] = 0; script[:] = ["none"]
        assert K.fetch_vtt("u") is None and calls["n"] == 1 and K.CAPTION_STATS["none"] == 1       # no captions: asked once, not five times
        calls["n"] = 0; script[:] = ["limit"]
        assert K.fetch_vtt("u", tries=3) is None and calls["n"] == 3 and K.CAPTION_STATS["rate_limited"] == 1
        assert "refused by YouTube" in K.caption_summary()
    finally:
        time.sleep = real_sleep
        if old is not None: sys.modules["yt_dlp"] = old
        else: del sys.modules["yt_dlp"]


def test_run_goes_through_every_step_and_shows_a_banner_when_done_or_stopped():
    import argparse, importlib.util
    spec = importlib.util.spec_from_file_location("factory_cli", os.path.join(os.path.dirname(__file__), "..", "factory.py"))
    F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
    seen, shown = [], []
    for st in F.STEPS:
        setattr(F, "cmd_" + st, lambda a, st=st: seen.append(st))
    F.banner = lambda title, message, good=True: shown.append((title, message, good))
    F.cmd_run(argparse.Namespace(activity="tennis forehand"))
    assert seen == ["grow", "learn", "mistakes", "label", "build"]
    assert len(shown) == 1 and shown[0][2] and "tennis forehand" in shown[0][1]
    def boom(a): raise RuntimeError("x")
    F.cmd_label = boom; shown.clear()
    try: F.cmd_run(argparse.Namespace(activity="tennis forehand"))
    except RuntimeError: pass
    assert len(shown) == 1 and not shown[0][2] and "'label'" in shown[0][1]            # says where it stopped
    def stop(a): raise KeyboardInterrupt
    F.cmd_label = stop; shown.clear()
    try: F.cmd_run(argparse.Namespace(activity="x"))
    except KeyboardInterrupt: pass
    assert shown == []                                                                  # you stopped it yourself: no banner


def test_a_cue_handle_naming_a_body_part_is_removed_but_the_principle_stays():
    from sphere import principles as PR
    _, entry, _ = _squat_with_principles()
    p = dict(entry["principles"][0], handle_intent="Open the hips earlier")
    kept, dropped = PR.clean([p], entry)
    assert len(kept) == 1 and kept[0]["handle_intent"] == "" and not PR.has_handle(kept[0])
    assert dropped and "body part" in dropped[0]["why"]
    assert PR.problems(dict(entry, principles=kept)) == []


def test_swing_events_are_asked_again_until_each_one_has_the_level_it_must_reach():
    from sphere import propose as P
    from types import SimpleNamespace as N
    answers = [[{"feature": "reach.wrist.dom", "direction": "rises", "seconds": 1.0}],
               [{"feature": "reach.wrist.dom", "direction": "rises", "peak_at_least": 0.9, "seconds": 1.0}]]
    sent = []
    class C:
        class messages:
            @staticmethod
            def create(**kw):
                sent.append(kw["messages"][0]["content"])
                return N(content=[N(type="tool_use", input={"attempt_events": answers[len(sent) - 1]})])
    ev = P.propose_events("tennis forehand", ["reach.wrist.dom"], client=C)
    assert ev[0]["peak_at_least"] == 0.9 and len(sent) == 2                  # the first answer had no level: asked again
    assert "wrist distance from shoulder" in sent[0]                          # the model is told the feature's units
    assert "peak_at_least" in P.EVENTS_SCHEMA["properties"]["attempt_events"]["items"]["required"]


def test_an_objective_is_judged_by_the_faults_it_measures_not_by_those_it_only_stands_in_for():
    from sphere import pipeline as PL
    links = {"a": {"objective": "o1", "measurable": "measured"}, "b": {"objective": "o1", "measurable": "proxy"},
             "c": {"objective": "o2", "measurable": "proxy"}, "d": {"objective": None, "measurable": "not_visible"}}
    assert PL.deciding_faults(links) == {"o1": ["a"], "o2": ["c"]}


def test_tracker_flicker_is_repaired_but_fast_real_movement_is_kept():
    import numpy as np
    from sphere.features import repair_flicker
    names = ["angle.elbow.dom"]
    ramp = np.concatenate([np.full(10, 170.0), np.linspace(170, 60, 4), np.full(10, 60.0)])[:, None]     # a fast real extension: about 37 a frame
    assert np.allclose(repair_flicker(ramp, names, 30.0), ramp)
    spike = np.full((30, 1), 100.0); spike[15] = 43.0                                                    # one frame the tracker lost
    assert np.allclose(repair_flicker(spike, names, 30.0), 100.0)
    step = np.concatenate([np.full(15, 120.0), np.full(15, 71.0)])[:, None]                              # a real one-frame step stays a step
    assert np.allclose(repair_flicker(step, names, 30.0), step)


def test_each_swing_goes_to_the_activity_it_fits_and_to_none_when_nothing_fits():
    from sphere import engine
    from sphere.identify import identify, accepts
    w = make_work()
    entry, _ = pipeline.build("squat", w, runs=2, proposer=stub)
    squat = synth.squat_clip(yaw=30, seed=3, tag="good")
    owned, found = identify({"squat": entry}, squat)
    assert owned["squat"] and all(f["owner"] == "squat" for f in found if f["fit"] <= 1.0)
    arm = synth.arm_raise_clip(seed=1, yaw=30)
    owned2, found2 = identify({"squat": entry}, arm)
    assert owned2["squat"] == []                                              # raising an arm is not a squat
    ev, log = engine.run_clip(entry, squat, accept=lambda s, e: False)
    assert log == []                                                          # an attempt that belongs to another activity is not coached here
    ev, log = engine.run_clip(entry, squat, accept=lambda s, e, o=owned["squat"]: accepts(o, s, e))
    assert len(log) == len(owned["squat"])


def test_a_spoken_line_is_short_and_claims_nothing_unmeasured():
    from sphere.engine import Wording
    assert Wording.allowed("Let the arm swing freely and finish across.")
    assert not Wording.allowed("Drive up so the ball leaves with real pace and spin.")      # the ball is not tracked
    assert not Wording.allowed("Reach high and finish tall through the whole swing, then recover quickly.")    # more than ten words
    assert not Wording.allowed("")


def test_an_entry_that_often_fooled_itself_is_a_draft():
    from sphere.identify import ready
    good = {"recognition": {"accuracy": {"false_accept_rate_vs_other_activities": 0.05, "recall": 0.95}}}
    loose = {"recognition": {"accuracy": {"false_accept_rate_vs_other_activities": 0.6, "recall": 0.95}}}
    assert ready(good)[0] and not ready(loose)[0] and ready({})[0]


def test_the_follow_through_of_another_activity_is_not_a_second_swing():
    from sphere import identify as I
    import numpy as np
    arr = np.zeros((5, 1)); names = ["x"]
    calls = {"a": [{"start": 10.0, "end": 12.0, "arr": arr}], "b": [{"start": 12.1, "end": 12.8, "arr": arr}, {"start": 20.0, "end": 21.0, "arr": arr}]}
    sig = {"features": ["x"], "mean": [0.0] * 5, "std": [1.0] * 5, "threshold": 1.0}
    entries = {k: {"recognition": {"signature": sig, "accuracy": {}}} for k in calls}
    real = I.attempts_in
    I.attempts_in = lambda entry, clip: (names, calls[[k for k, e in entries.items() if e is entry][0]])
    try:
        owned, _ = I.identify(entries, None)
    finally:
        I.attempts_in = real
    assert len(owned["a"]) == 1 and owned["b"] == [(20.0, 21.0)]              # b's window right after a's end is a follow-through; the later one is a swing


if __name__ == "__main__":
    ok = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); ok += 1; print("ok  ", name)
    print(f"{ok} tests passed")
