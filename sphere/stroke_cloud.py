"""Cloud reading of one swing (forehand / backhand / serve / volley_or_smash / none) and a confidence gate that combines it with the skeleton network.
STANDALONE: not wired into the engine. Prompt and schema = the 'v2' labeller that scored 0.66 accuracy / 0.815 forehand-vs-backhand side accuracy on Basile's human tags
(12 frames, ONE window per call: batching several windows in one call cost ~14 points).
Thresholds in gate() are PLACEHOLDERS, to be tuned on work/humantest tags and, later, on phone-session data."""
import base64, os

CLASSES = ["forehand", "backhand", "serve", "no_stroke"]
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["windows"], "properties": {"windows": {"type": "array", "items": {
    "type": "object", "additionalProperties": False,
    "required": ["n", "player_faces", "racket_hand", "side_in_takeback", "side_at_contact", "stroke", "confidence", "evidence"],
    "properties": {
        "n": {"type": "integer"},
        "player_faces": {"type": "string", "enum": ["toward_camera", "away_from_camera", "side_on", "unclear"]},
        "racket_hand": {"type": "string", "enum": ["player_right", "player_left", "unclear"]},
        "side_in_takeback": {"type": "string", "enum": ["player_right_side", "player_left_side", "centre", "no_swing", "unclear"]},
        "side_at_contact": {"type": "string", "enum": ["player_right_side", "player_left_side", "centre", "no_swing", "unclear"]},
        "stroke": {"type": "string", "enum": ["forehand", "backhand", "serve", "volley_or_smash", "none", "unclear"]},
        "confidence": {"type": "integer", "enum": [1, 2, 3]},
        "evidence": {"type": "string"}}}}}}
PROMPT = """Each window below is {k} frames of one video in time order (numbered 1-{k}, a fraction of a second apart), about 2-3 seconds in all. Judge the main player only. For each window:
1. player_faces: toward the camera, away from it, or side-on. Decide this first.
2. racket_hand, side_in_takeback, side_at_contact: always the PLAYER's own right and left, never the viewer's. The take-back is where the racket is when drawn back before the forward swing.
3. stroke:
   - forehand: the racket hand swings on its own side of the body (take-back and contact on the same side as the racket hand).
   - backhand: the racket crosses to the opposite side (a two-handed backhand included; a one-handed backhand has the racket arm across the body). Slice shots count as forehand or backhand by the same side rule.
   - serve: ball toss and overhead swing.
   - volley_or_smash: a short punch at the net, or an overhead hit in a rally.
   - none: no tennis stroke is being played (coach talking or walking, gesture or set-up, a swing in another sport, no real swing). A practice or shadow swing of a tennis stroke still counts as that stroke.
   - unclear: you cannot tell which stroke it is.
Answer by calling the submit tool exactly once."""


def classify(frames_jpeg, client, model):
    """frames_jpeg: list of 12 JPEG byte strings (one swing, in time order) -> dict with stroke, confidence (1-3), racket_hand, ... or None."""
    content = [{"type": "text", "text": PROMPT.format(k=len(frames_jpeg))}, {"type": "text", "text": "Window 1"}]
    for i, jb in enumerate(frames_jpeg, 1):
        content.append({"type": "text", "text": f"frame {i}"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(jb).decode()}})
    r = client.messages.create(model=model, max_tokens=1500, tools=[{"name": "submit", "description": "Submit.", "input_schema": SCHEMA}], messages=[{"role": "user", "content": content}])
    for blk in r.content:
        if blk.type == "tool_use":
            ws = blk.input.get("windows", [])
            return ws[0] if ws and isinstance(ws[0], dict) else None
    return None


def gate(p_skel, cloud=None, skel_accept=0.8, cloud_min_conf=2):
    """p_skel: probabilities over CLASSES from the skeleton network. cloud: result of classify() or None (not asked / unavailable).
    Returns (label or None, source). None = stay silent for this swing.
    Rule: a confident skeleton answer stands; otherwise the cloud answer stands if it is confident (and not 'unclear'); agreement of both always stands."""
    top = max(range(len(CLASSES)), key=lambda i: p_skel[i]); skel = CLASSES[top]
    cl = None
    if cloud and cloud.get("stroke") not in (None, "unclear") and cloud.get("confidence", 0) >= cloud_min_conf:
        cl = {"none": "no_stroke", "volley_or_smash": "other"}.get(cloud["stroke"], cloud["stroke"])
    if cl == skel: return skel, "agree"
    if p_skel[top] >= skel_accept: return skel, "skeleton"
    if cl in CLASSES: return cl, "cloud"
    return None, "unsure"


def needs_cloud(p_skel, skel_accept=0.8):
    """Only ask the cloud when the skeleton is not confident (saves cost)."""
    return max(p_skel) < skel_accept


if __name__ == "__main__":
    assert gate([0.9, 0.05, 0.03, 0.02]) == ("forehand", "skeleton")
    assert gate([0.4, 0.4, 0.1, 0.1], {"stroke": "backhand", "confidence": 2}) == ("backhand", "cloud")
    assert gate([0.4, 0.4, 0.1, 0.1], {"stroke": "unclear", "confidence": 3}) == (None, "unsure")
    assert gate([0.5, 0.3, 0.1, 0.1], {"stroke": "forehand", "confidence": 1}) == (None, "unsure")
    assert gate([0.5, 0.3, 0.1, 0.1], {"stroke": "forehand", "confidence": 2}) == ("forehand", "agree")
    print("gate logic ok")
