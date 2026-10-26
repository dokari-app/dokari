"""Viewer comments of a YouTube video, the second signal next to the captions. Comments often say what is wrong or right ("the toss is too far left", "2:13 that
is the contact point") and a comment that starts with a time ("2:13 ...") points at one moment of the video. Fetched with yt-dlp (no video), cached per video as
<act>/comments/<id>.json, spaced out like the caption requests. Never needed for anything else: if a video has none, the labelling goes on without."""
import json, os, re, time, random

MIN_GAP_S = 6
_LAST = [0.0]
LAST_ERROR = [""]
_TS = re.compile(r"(?<![\d:])(?:(\d{1,2}):)?(\d{1,2}):(\d{2})(?![\d:])")


def timestamps(text):
    """Seconds of every m:ss or h:mm:ss in the text."""
    return [int(h or 0) * 3600 + int(m) * 60 + int(s) for h, m, s in _TS.findall(text) if int(s) < 60]


def fetch(url, n=60, tries=3):
    """-> list of {text, likes, t} (t = first timestamp in the text, or None), most liked first; [] when the video has no comments or they cannot be read."""
    import yt_dlp
    for attempt in range(tries):
        gap = MIN_GAP_S + random.uniform(0, 3) - (time.time() - _LAST[0])
        if gap > 0: time.sleep(gap)
        _LAST[0] = time.time()
        opts = {"quiet": True, "no_warnings": True, "skip_download": True, "getcomments": True, "retries": 2, "extractor_retries": 2, "ignore_no_formats_error": True,
                "extractor_args": {"youtube": {"max_comments": [f"{n}", f"{n}", "0", "0"], "comment_sort": ["top"]}}}
        if os.environ.get("SPHERE_COOKIES"): opts["cookiesfrombrowser"] = (os.environ["SPHERE_COOKIES"],)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            out = []
            for c in info.get("comments") or []:
                if c.get("parent", "root") != "root": continue
                text = " ".join(str(c.get("text") or "").split())
                if len(text) < 12: continue
                ts = timestamps(text)
                out.append({"text": text[:400], "likes": int(c.get("like_count") or 0), "t": ts[0] if ts else None})
            return sorted(out, key=lambda c: -c["likes"])
        except Exception as e:
            LAST_ERROR[0] = str(e)[:300]
            if "429" in str(e) or "Too Many" in str(e): time.sleep(30 * (attempt + 1)); continue
            return []
    return []


def cached(act_dir, vid, url, n=60):
    p = os.path.join(act_dir, "comments", vid + ".json")
    if os.path.exists(p):
        try:
            got = json.load(open(p))
            if got: return got               # an empty file is a failed fetch: try again
        except Exception: pass
    cs = fetch(url, n)
    os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(cs, open(p, "w"))
    return cs


def text_for(comments, windows=None, general=8, near=4.0, max_chars=2500):
    """The comments worth showing the labelling model: the most liked ones, plus those whose timestamp falls in or just around an attempt window."""
    if not comments: return ""
    pick = [c for c in comments if c["t"] is None][:general]
    for c in comments:
        if c["t"] is not None and (windows is None or any(a - near <= c["t"] <= b + near for a, b in windows)): pick.append(c)
    lines, n = [], 0
    for c in pick:
        s = (f"[about {c['t'] // 60}:{c['t'] % 60:02d}] " if c["t"] is not None else "") + c["text"]
        if n + len(s) > max_chars: break
        lines.append("- " + s); n += len(s)
    return "Viewer comments (opinions of other viewers, not evidence; use only where the frames agree):\n" + "\n".join(lines) if lines else ""
