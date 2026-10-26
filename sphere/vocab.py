"""The shared vocabulary between factory and app (spec sections 4, 6, 7)."""
from .features import FEATURES, FEATURE_DOC

MEASURES = {
    "M01": ("position", "fast", "active"), "M02": ("angle", "fast", "active"),
    "M03": ("distance", "fast", "active"), "M04": ("extent", "fast", "active"),
    "M05": ("speed", "fast", "active"), "M06": ("timing", "fast", "active"),
    "M07": ("path", "fast", "active"), "M08": ("steadiness", "fast", "active"),
    "M09": ("symmetry", "fast", "active"), "M10": ("consistency", "fast", "active"),
    "M11": ("visibility", "fast", "active"), "M12": ("count", "fast", "active"),
    "M13": ("sound_feature", "fast", "deferred"), "M14": ("sound_event", "fast", "active"),
    "M15": ("expression", "fast", "deferred"), "M16": ("ask_scene", "slow", "active"),
    "M17": ("ask_audio", "slow", "deferred"), "M18": ("ask_learner", "slow", "active"),
    "M19": ("flight", "fast", "planned"), "M20": ("keypose_match", "fast", "active"),
}
DEFERRED = {k for k, v in MEASURES.items() if v[2] == "deferred"}
PLANNED = {k for k, v in MEASURES.items() if v[2] == "planned"}
SLOW_ONLY = {"M16", "M17", "M18"}

OPERATORS = ["GREATER_THAN", "GREATER_OR_EQUAL", "LESS_THAN", "LESS_OR_EQUAL", "EQUALS",
             "WITHIN_RANGE", "OUTSIDE_RANGE", "DELTA_GREATER_THAN", "DELTA_LESS_THAN"]
TIME_BUDGETS = ["per_frame", "per_attempt", "seconds", "after_set"]
SCENE_FIELDS = ["session_state", "people.count", "framing.camera_stable", "observable.body",
                "observable.ball", "activity.match_confidence", "anomalies.present"]
CONTEXT_HINTS = ["hold_coaching_until_break", "speak_only_when_asked", "ask_to_confirm_activity",
                 "good_moment_between_attempts"]
SEVERITIES = ["low", "medium", "high"]
RELIABILITY = ["A", "B", "C"]


def plausible_range(feature):
    """Registered plausible ranges (spec check 5). Values outside these are impossible or
    meaningless for a human body in normalised units."""
    if feature == "angle.shoulder_hip_twist" or feature.startswith("rot."):
        return (-180.0, 180.0)
    p = feature.split(".")[0]
    return {"angle": (0.0, 180.0), "height": (-3.0, 3.0), "dev": (-3.0, 3.0), "fwd": (-3.0, 3.0),
            "lat": (-3.0, 3.0), "reach": (0.0, 3.0), "dist": (0.0, 8.0)}[p]


def feature_catalogue():
    return {f: FEATURE_DOC[f] for f in FEATURES}
