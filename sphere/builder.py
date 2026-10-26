"""Assemble an entry from a proposal (what the language model thinks) and calibration
(what real movement says)."""
import numpy as np
from .calibrate import (stack, find_landmarks, key_poses, recognition_report, calibrate_objective, N_T, Signature)
from .features import FEATURES, feature_measure
from .vocab import PLANNED, plausible_range

SEV_ORDER = {"high": 0, "medium": 1, "low": 2}


class InsufficientData(Exception):
    pass


def _severity(sides):
    """An objective is as serious as its most serious side."""
    return min((s["severity"] for s in sides.values()), key=lambda v: SEV_ORDER[v])


def _compare(low, high):
    """The condition under which the objective is met."""
    if low is not None and high is not None:
        return {"op": "WITHIN_RANGE", "low": round(low, 4), "high": round(high, 4)}
    if high is not None:
        return {"op": "LESS_OR_EQUAL", "value": round(high, 4)}
    return {"op": "GREATER_OR_EQUAL", "value": round(low, 4)}


def _prio(objectives):
    """Priority by topological order (causes before effects), severity as tie-break."""
    ids = [o["id"] for o in objectives]
    by = {o["id"]: o for o in objectives}
    deps = {o["id"]: {c for c in o["caused_by"] if c in by} for o in objectives}
    order, done = [], set()
    while len(order) < len(objectives):
        ready = [i for i in ids if i not in done and deps[i] <= done]
        if not ready:                                   # cycle: break it, the check will flag it
            ready = [i for i in ids if i not in done][:1]
        ready.sort(key=lambda i: (SEV_ORDER[by[i]["severity"]], ids.index(i)))
        order.append(ready[0]); done.add(ready[0])
    return {i: k + 1 for k, i in enumerate(order)}


def _signature_json(sig, names):
    return {"features": [names[i] for i in sig.feat_idx], "n_samples": N_T,
            "mean": np.round(sig.mean, 4).tolist(), "std": np.round(np.maximum(sig.std, sig.floor), 4).tolist(),
            "threshold": round(sig.threshold, 4), "required_events": sig.events or []}


def observed_structure(collections):
    """What the real clips show: landmarks of one time-normalised attempt and the median value of the
    most characteristic features at each. Used to ground the language model in data, and for the report."""
    A, meta = stack(collections)
    if len(A) < 6:
        raise InsufficientData(f"only {len(A)} usable attempts; need at least 6")
    lm_idx, _ = find_landmarks(A)
    stats, top, _ = key_poses(A, lm_idx)
    rows = []
    for k, (idx, st) in enumerate(zip(lm_idx, stats)):
        rows.append({"id": f"L{k}", "t": round(idx / (N_T - 1), 3),
                     "values": {FEATURES[f]: round(float(st["median"][f]), 3) for f in top}})
    return {"n_phase": len(lm_idx) - 1, "landmarks": rows, "n_attempts": int(len(A)),
            "n_clips": len({m["clip_id"] for m in meta})}


def build_entry(proposal, collections, other_attempts=None, runs=1, agreement=None, version="0.1.0", events=None, reference_clips=None, tags_for=None, cal_collections=None):
    A, meta = stack(collections)
    if len(A) < 6:
        raise InsufficientData(f"only {len(A)} usable attempts; need at least 6")
    names = FEATURES
    lm_idx, _ = find_landmarks(A)
    landmarks = [{"id": f"L{i}", "t": round(idx / (N_T - 1), 4)} for i, idx in enumerate(lm_idx)]
    n_phase = len(lm_idx) - 1
    props = proposal["phases"]
    if len(props) == n_phase:
        pmap = list(range(n_phase)); pnames = [p["id"] for p in props]; pdesc = [p["description"] for p in props]
    else:   # counts differ: generic names, proposal phases mapped by relative order
        pnames = [f"phase_{i + 1}" for i in range(n_phase)]
        pdesc = ["" for _ in range(n_phase)]
    phases = [{"id": pnames[i], "start": landmarks[i]["id"], "end": landmarks[i + 1]["id"],
               "description": pdesc[i] or "movement segment found from the data"} for i in range(n_phase)]
    phase_index = {}
    for k, p in enumerate(props):
        j = k if len(props) == n_phase else min(n_phase - 1, int(round(k * n_phase / max(1, len(props)))))
        phase_index[p["id"]] = j

    def landmark_of(phase_id, point):
        j = phase_index.get(phase_id)
        if j is None:
            return None
        return j if point == "start" else j + 1

    stats, top, imp = key_poses(A, lm_idx)
    kp = {}
    for li, st in zip(landmarks, stats):
        kp[li["id"]] = {names[f]: {"median": round(float(st["median"][f]), 4), "sigma": round(float(st["sigma"][f]), 4),
                                   "p5": round(float(st["p5"][f]), 4), "p95": round(float(st["p95"][f]), 4)}
                        for f in top}
    yaws = [m["view_yaw_deg"] for m in meta]
    view = {"yaw_min": round(float(min(yaws)), 1), "yaw_max": round(float(max(yaws)), 1),
            "n_clips_by_view": {"front/back (<30)": sum(1 for c in collections if c["usable"] and c["view_yaw_deg"] < 30),
                                "oblique (30-60)": sum(1 for c in collections if c["usable"] and 30 <= c["view_yaw_deg"] <= 60),
                                "side (>60)": sum(1 for c in collections if c["usable"] and c["view_yaw_deg"] > 60)}}
    rep, sig = recognition_report(A, meta, others=other_attempts, events=events, names=names)
    sev = {o["id"]: _severity(o["sides"]) for o in proposal["objectives"]}
    prio = _prio([{"id": o["id"], "caused_by": o["caused_by"], "severity": sev[o["id"]]} for o in proposal["objectives"]])

    # Objectives are calibrated on `cal_collections` when given: the typical attempts plus attempts confirmed by looking at them, which may be odd
    # (shallow, slow, wrong) and so are kept out of everything that describes the typical movement (recognition, key poses, landmarks).
    Ac, mc = stack(cal_collections) if cal_collections is not None else (A, meta)
    objectives, no_range = [], []
    for o in proposal["objectives"]:
        t = o["test"]
        li = landmark_of(t["at_phase"], t["at_point"])
        fi = names.index(t["feature"])
        if li is None:
            continue
        om, otag = mc, o["id"]
        mine = tags_for(o["id"], mc) if tags_for else None     # labels for THIS objective: attempts judged to meet it or to miss it
        if mine is not None:
            om, otag = [dict(m, tag=g) for m, g in zip(mc, mine)], "bad"
        cal = calibrate_objective(Ac, om, fi, lm_idx[li], set(o["sides"]), reference_clips, tag=otag, limits=plausible_range(t["feature"]))
        if cal["low"] is None and cal["high"] is None:
            no_range.append(o["id"])                        # no usable value, or every bound lies beyond what the feature can be
            continue
        sides = {k: v for k, v in o["sides"].items() if cal["low" if k == "below" else "high"] is not None}   # a side with no bound cannot be crossed
        test = {"measure": feature_measure(t["feature"]), "feature": t["feature"], "at": landmarks[li]["id"],
                "compare": _compare(cal["low"], cal["high"]), "aggregate": {"rule": "at_least", "n": 3, "of": 5}, "min_confidence": 0.6,
                "valid_views": {"yaw_min": view["yaw_min"], "yaw_max": view["yaw_max"]}, "time_budget": "per_attempt"}
        objectives.append({"id": o["id"], "goal": o["goal"], "severity": _severity(sides), "kind": o.get("kind", "form"), "priority": prio[o["id"]],
                           "caused_by": o["caused_by"], "sides": sides, "tests": [test],
                           "detection": {"source": "pose", "reliability": "B" if cal["validated"] else "C"},
                           "outcome_links": o["outcome_links"], "cue_intent": o["cue_intent"],
                           "ask_if_unsure_intent": o["ask_if_unsure_intent"], "fix_intent": o["fix_intent"],
                           "calibration": cal})
    objectives.sort(key=lambda f: f["priority"])

    outcomes = []
    vocab_props = list(proposal.get("vocabulary_proposals", []))
    for o in proposal["outcomes"]:
        obs = o["requires_observable"]
        if set(obs) <= {"body"}:
            status, measure = "available", "M01"
        elif "ball" in obs:
            status, measure = "planned", "M19"
        else:
            status, measure = "proposal", None
            vocab_props.append({"kind": "measurement", "name": f"outcome:{o['id']}", "why": o["description"]})
        outcomes.append({"id": o["id"], "description": o["description"], "measure": measure,
                         "requires_observable": obs, "status": status})
    links = []
    for l in proposal["links"]:
        li = landmark_of(l["at_phase"], l["at_point"])
        if li is None:
            continue
        links.append({"feature": l["feature"], "at": landmarks[li]["id"], "outcome": l["outcome"],
                      "effect": l["effect"], "mechanism": l["mechanism"], "evidence": "prior_only"})

    used_feats = sorted({names[i] for i in top} | {t["feature"] for f in objectives for t in f["tests"]}
                        | {l["feature"] for l in links})
    bases = [f["calibration"]["basis"] for f in objectives]
    labelled = "labelled" in bases
    n_valid = sum(1 for f in objectives if f["calibration"]["validated"])
    tier = "medium" if (labelled and n_valid >= max(1, len(objectives) // 2) and rep["recall"] >= 0.85 and rep["n_clips"] >= 5) else "low"
    entry = {
        "spec_version": "0.7", "activity": proposal["activity_id"], "version": version, "purpose": proposal["purpose"],
        "recognition": {"signature": _signature_json(sig, names), "accuracy": rep,
                        "confusable_with": proposal["confusable_with"]},
        "context_rules": [
            {"when": {"field": "activity.match_confidence", "op": "LESS_THAN", "value": 0.6}, "hint": "ask_to_confirm_activity"},
            {"when": {"field": "session_state", "op": "IN", "value": ["rest", "conversation"]}, "hint": "hold_coaching_until_break"}],
        "movement_model": {"signals": used_feats, "landmarks": landmarks, "phases": phases, "key_poses": kp, "view_coverage": view},
        "outcomes": outcomes, "links": links, "objectives": objectives, "session_ideas": proposal["session_ideas"],
        "proposals": vocab_props,
        "metadata": {
            "feasibility": {"verdict": "experimental",
                            "reason": "built by the factory; not yet validated in real sessions"},
            "provenance": {"sources": sorted({c["clip_id"] for c in collections if c["usable"]}),
                           "n_clips": rep["n_clips"], "n_attempts": rep["n_attempts"], "runs": runs, "agreement": agreement, "primary_features": proposal.get("primary_features", []),
                           "calibration_basis": {b: bases.count(b) for b in sorted(set(bases))}, "objectives_without_usable_range": no_range},
            "confidence_tier": tier,
            "requires": {"features": used_feats, "measures": sorted({t["measure"] for f in objectives for t in f["tests"]})},
        },
    }
    return entry
