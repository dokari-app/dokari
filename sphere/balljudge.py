"""Automatic judge for ball candidates: a vision model looks at a grid of candidate crops and says which show a tennis ball at the centre.
Same grids as tests/ball_crops.py (6 x 4 tiles, red circle at the candidate, yellow index). Calibrated against crops judged by hand
(tests/ball_judge_calibrate.py); the nightly loop uses it instead of a person."""
import base64, os, time
import cv2

MODEL = os.environ.get("SPHERE_MODEL", "claude-sonnet-5-5")
PROMPT = ("Each tile of this grid is a small crop from a tennis video, centred on a candidate. The red circle marks the candidate and the yellow number is its index. "
          "List the tiles where a TENNIS BALL (a yellow-green sphere, possibly motion-blurred, small) sits inside the red circle, at its centre. "
          "kind: 'free' = the ball is in the air or on its own against the background; 'held' = in the hand or against the racket strings; 'static' = resting on the court. "
          "Do NOT list tiles where the ball is off-centre or only partly in the circle, or where the circle holds a wristband, shoe, shirt, skin, foliage, racket frame, graphic or any other yellow thing. "
          "When unsure, leave the tile out. Submit via the tool; an empty list is a valid answer.")
SCHEMA = {"type": "object", "properties": {"balls": {"type": "array", "items": {"type": "object", "properties": {
    "n": {"type": "integer", "description": "the yellow tile number"}, "kind": {"type": "string", "enum": ["free", "held", "static"]}}, "required": ["n", "kind"]}}},
    "required": ["balls"]}


def judge_grid(png_path, client=None, model=None, retries=2):
    """-> {tile index: kind} for the tiles the model says hold a ball, or None if it never answered."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic()
    data = base64.b64encode(open(png_path, "rb").read()).decode()
    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": data}}, {"type": "text", "text": PROMPT}]
    for _ in range(retries + 1):
        try:
            r = client.messages.create(model=model or MODEL, max_tokens=1500, tools=[{"name": "submit", "description": "Submit the tiles with a ball.", "input_schema": SCHEMA}],
                                       messages=[{"role": "user", "content": content}])
        except Exception as e:
            print(f"   judge call failed: {type(e).__name__}: {str(e)[:300]}", flush=True)
            time.sleep(5); continue
        for b in r.content:
            if b.type == "tool_use":
                return {int(x["n"]): x["kind"] for x in b.input.get("balls", [])}
    return None
