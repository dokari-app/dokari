"""JSON Schema for entries (spec section 7) and for the model's proposal (factory stage 1)."""
from .vocab import MEASURES, OPERATORS, TIME_BUDGETS, SEVERITIES, RELIABILITY, CONTEXT_HINTS, SCENE_FIELDS
from .features import FEATURES

ID = {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"}
FEATURE = {"enum": FEATURES}
MEASURE = {"enum": sorted(MEASURES)}

CONDITION = {
    "oneOf": [
        {"type": "object", "additionalProperties": False, "required": ["field", "op", "value"],
         "properties": {"field": {"enum": SCENE_FIELDS},
                        "op": {"enum": ["EQUALS", "NOT_EQUALS", "GREATER_THAN", "LESS_THAN", "IN"]},
                        "value": {}}},
        {"type": "object", "additionalProperties": False, "required": ["all"],
         "properties": {"all": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/condition"}}}},
        {"type": "object", "additionalProperties": False, "required": ["any"],
         "properties": {"any": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/condition"}}}},
        {"type": "object", "additionalProperties": False, "required": ["not"],
         "properties": {"not": {"$ref": "#/$defs/condition"}}},
    ]
}

COMPARE = {
    "oneOf": [
        {"type": "object", "additionalProperties": False, "required": ["op", "value"],
         "properties": {"op": {"enum": ["GREATER_THAN", "GREATER_OR_EQUAL", "LESS_THAN", "LESS_OR_EQUAL", "EQUALS"]},
                        "value": {"type": "number"}}},
        {"type": "object", "additionalProperties": False, "required": ["op", "low", "high"],
         "properties": {"op": {"enum": ["WITHIN_RANGE", "OUTSIDE_RANGE"]},
                        "low": {"type": "number"}, "high": {"type": "number"}}},
        {"type": "object", "additionalProperties": False, "required": ["op", "baseline", "delta"],
         "properties": {"op": {"enum": ["DELTA_GREATER_THAN", "DELTA_LESS_THAN"]},
                        "baseline": {"enum": ["learner_median", "learner_last_session"]},
                        "delta": {"type": "number"}}},
    ]
}

TEST = {
    "type": "object", "additionalProperties": False,
    "required": ["measure", "feature", "at", "compare", "aggregate", "min_confidence", "valid_views", "time_budget"],
    "properties": {
        "measure": MEASURE,
        "feature": FEATURE,
        "at": {"type": "string", "pattern": "^L[0-9]+$"},                 # a landmark id
        "compare": COMPARE,
        "aggregate": {"type": "object", "additionalProperties": False, "required": ["rule", "n", "of"],
                      "properties": {"rule": {"enum": ["at_least", "at_most"]},
                                     "n": {"type": "integer", "minimum": 1}, "of": {"type": "integer", "minimum": 1}}},
        "min_confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "valid_views": {"type": "object", "additionalProperties": False, "required": ["yaw_min", "yaw_max"],
                        "properties": {"yaw_min": {"type": "number"}, "yaw_max": {"type": "number"}}},
        "time_budget": {"enum": TIME_BUDGETS},
    },
}

SIDE = {"type": "object", "additionalProperties": False, "required": ["looks_like", "severity"],
        "properties": {"looks_like": {"type": "string"}, "severity": {"enum": SEVERITIES}}}
SIDES = {"type": "object", "additionalProperties": False, "minProperties": 1,
         "properties": {"below": SIDE, "above": SIDE}}

ENTRY_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "skill-sphere/entry/0.7",
    "type": "object", "additionalProperties": False,
    "required": ["spec_version", "activity", "version", "purpose", "recognition", "context_rules",
                 "movement_model", "outcomes", "links", "objectives", "session_ideas", "metadata"],
    "properties": {
        "spec_version": {"const": "0.7"},
        "activity": ID,
        "version": {"type": "string"},
        "purpose": {"type": "string"},
        "recognition": {
            "type": "object", "additionalProperties": False,
            "required": ["signature", "accuracy", "confusable_with"],
            "properties": {"signature": {"type": "object"}, "accuracy": {"type": "object"},
                           "confusable_with": {"type": "array", "items": {"type": "string"}}}},
        "context_rules": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["when", "hint"],
            "properties": {"when": {"$ref": "#/$defs/condition"}, "hint": {"enum": CONTEXT_HINTS}}}},
        "movement_model": {
            "type": "object", "additionalProperties": False,
            "required": ["signals", "landmarks", "phases", "key_poses", "view_coverage"],
            "properties": {
                "signals": {"type": "array", "items": FEATURE, "minItems": 1},
                "landmarks": {"type": "array", "minItems": 2, "items": {
                    "type": "object", "additionalProperties": False, "required": ["id", "t"],
                    "properties": {"id": {"type": "string", "pattern": "^L[0-9]+$"},
                                   "t": {"type": "number", "minimum": 0, "maximum": 1}}}},
                "phases": {"type": "array", "minItems": 1, "items": {
                    "type": "object", "additionalProperties": False, "required": ["id", "start", "end", "description"],
                    "properties": {"id": ID, "start": {"type": "string", "pattern": "^L[0-9]+$"},
                                   "end": {"type": "string", "pattern": "^L[0-9]+$"}, "description": {"type": "string"}}}},
                "key_poses": {"type": "object"},
                "view_coverage": {"type": "object"}}},
        "outcomes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["id", "description", "requires_observable", "status"],
            "properties": {"id": ID, "description": {"type": "string"}, "measure": {"enum": sorted(MEASURES) + [None]},
                           "requires_observable": {"type": "array", "items": {"type": "string"}},
                           "status": {"enum": ["available", "planned", "proposal"]}}}},
        "links": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["feature", "at", "outcome", "effect", "mechanism", "evidence"],
            "properties": {"feature": FEATURE, "at": {"type": "string", "pattern": "^L[0-9]+$"},
                           "outcome": ID, "effect": {"enum": ["higher_is_better", "lower_is_better", "mid_is_better"]},
                           "mechanism": {"type": "string"}, "evidence": {"enum": ["prior_only", "supported_by_data"]}}}},
        "objectives": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "goal", "severity", "priority", "caused_by", "sides", "tests", "detection",
                         "outcome_links", "cue_intent", "ask_if_unsure_intent", "fix_intent", "calibration"],
            "properties": {
                "id": ID, "goal": {"type": "string"}, "severity": {"enum": SEVERITIES},
                "kind": {"enum": ["safety", "form"]},
                "priority": {"type": "integer", "minimum": 1},
                "caused_by": {"type": "array", "items": ID},
                "sides": SIDES,
                "tests": {"type": "array", "minItems": 1, "items": TEST},
                "detection": {"type": "object", "additionalProperties": False, "required": ["source", "reliability"],
                              "properties": {"source": {"enum": ["pose", "sound", "object_detector", "scene_model", "learner"]},
                                             "reliability": {"enum": RELIABILITY}}},
                "outcome_links": {"type": "array", "items": ID},
                "cue_intent": {"type": "string"}, "ask_if_unsure_intent": {"type": "string"},
                "fix_intent": {"type": "string"}, "calibration": {"type": "object"}}}},
        "session_ideas": {"type": "array", "items": {"type": "string"}},
        "coaching": {"type": "object"},
        "principles": {"type": "array", "items": {"type": "object"}},
        "proposals": {"type": "array", "items": {"type": "object"}},
        "metadata": {"type": "object"},
    },
    "$defs": {"condition": CONDITION},
}

PROPOSAL_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["activity_id", "purpose", "search_queries", "primary_features", "attempt_events", "phases", "objectives", "outcomes", "links",
                 "confusable_with", "session_ideas", "vocabulary_proposals"],
    "properties": {
        "activity_id": ID,
        "purpose": {"type": "string", "description": "What a good performance of this activity achieves."},
        "primary_features": {"type": "array", "minItems": 2, "maxItems": 6, "items": FEATURE,
                             "description": "The registered features that change most during ONE attempt of this activity "
                                            "(the body parts that actually do the movement). Used to find repetitions in video."},
        "attempt_events": {"type": "array", "minItems": 1, "maxItems": 4, "items": {
            "type": "object", "additionalProperties": False, "required": ["feature", "direction", "seconds"],
            "properties": {"feature": FEATURE, "direction": {"enum": ["rises", "falls"]},
                           "seconds": {"type": "number", "minimum": 0.2, "maximum": 30, "description": "How long this event takes in a typical attempt, in seconds: from the feature leaving its rest value to being back at it (a tennis forehand swing about 1; a serve's ball toss about 1.5; a squat about 3)."},
                           "peak_at_least": {"type": "number", "description": "Optional. Only when the event is defined by reaching a level in feature units (e.g. height.wrist.* is torso lengths above the shoulder: a wrist overhead is about 0.8, a tossing wrist above the head about 1.0). Omit when the event is defined only by moving."}}},
            "description": "What the body does, IN ORDER, in one attempt, as 1 to 4 events. Each event is a large excursion of one feature: "
                           "from its rest value it rises (or falls) to an extreme and comes back. Choose events that together tell the "
                           "action apart from every other movement (a squat: the hips fall; a serve: the tossing wrist rises, then the "
                           "hitting wrist rises). Every feature used must be one of primary_features."},
        "search_queries": {"type": "array", "minItems": 3, "maxItems": 8, "items": {
            "type": "object", "additionalProperties": False, "required": ["query", "kind"],
            "properties": {"query": {"type": "string"},
                           "kind": {"enum": ["demonstration", "good_form", "common_mistakes", "instruction"]}}}},
        "phases": {"type": "array", "minItems": 1, "maxItems": 6, "items": {
            "type": "object", "additionalProperties": False, "required": ["id", "description"],
            "properties": {"id": ID, "description": {"type": "string"}}}},
        "objectives": {"type": "array", "minItems": 1, "maxItems": 10, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "goal", "caused_by", "test", "sides", "outcome_links",
                         "cue_intent", "ask_if_unsure_intent", "fix_intent"],
            "properties": {
                "id": ID,
                "goal": {"type": "string", "description": "What the person should achieve, stated as the right thing to do "
                                                          "('keep the knees tracking over the toes'), not as a mistake."},
                "kind": {"enum": ["safety", "form"]},
                "caused_by": {"type": "array", "items": ID},
                "test": {"type": "object", "additionalProperties": False,
                         "required": ["feature", "at_phase", "at_point"],
                         "properties": {"feature": FEATURE, "at_phase": ID, "at_point": {"enum": ["start", "end"]}},
                         "description": "The objective is met when this feature, at this point, is inside a target range. "
                                        "You do not choose the range: it is taken from footage of good performances."},
                "sides": {"type": "object", "additionalProperties": False, "minProperties": 1,
                          "properties": {"below": SIDE, "above": SIDE},
                          "description": "Which way the feature can be wrong. 'below': under the target range; 'above': over it. "
                                         "Give BOTH when both are mistakes (a mallet swing parallel to the horse: angled in risks the "
                                         "horse's head, angled out is a smaller error), each with how it looks and how serious it is. "
                                         "Give only one when the other side is harmless or cannot happen (a squat deeper than the target)."},
                "outcome_links": {"type": "array", "items": ID},
                "cue_intent": {"type": "string"}, "ask_if_unsure_intent": {"type": "string"},
                "fix_intent": {"type": "string"}}}},
        "outcomes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["id", "description", "requires_observable"],
            "properties": {"id": ID, "description": {"type": "string"},
                           "requires_observable": {"type": "array", "items": {"type": "string"}}}}},
        "links": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["feature", "at_phase", "at_point", "outcome", "effect", "mechanism"],
            "properties": {"feature": FEATURE, "at_phase": ID, "at_point": {"enum": ["start", "end"]},
                           "outcome": ID, "effect": {"enum": ["higher_is_better", "lower_is_better", "mid_is_better"]},
                           "mechanism": {"type": "string"}}}},
        "confusable_with": {"type": "array", "items": {"type": "string"}},
        "session_ideas": {"type": "array", "items": {"type": "string"}},
        "vocabulary_proposals": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["kind", "name", "why"],
            "properties": {"kind": {"enum": ["trackable", "measurement", "feature", "operator"]},
                           "name": {"type": "string"}, "why": {"type": "string"}}}},
    },
}
