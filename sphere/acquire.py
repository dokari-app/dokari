"""Factory stage 2: find and download reference videos for an activity.

Runs on a machine with open internet access (not in the Claude workspace). Uses yt-dlp.
Only DERIVED data is kept long-term (see extract.py, which can delete the video after
pose extraction); the factory never redistributes videos."""
import json
import os
from . import sources as sources_mod


def search(query, n=10, min_s=20, max_s=420):
    import yt_dlp
    opts = {"quiet": True, "skip_download": True, "extract_flat": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        res = ydl.extract_info(f"ytsearch{n}:{query}", download=False)
    out = []
    for e in (res or {}).get("entries", []) or []:
        d = e.get("duration")
        if d is not None and not (min_s <= d <= max_s):
            continue
        out.append({"id": e.get("id"), "title": e.get("title"), "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
                    "duration": d, "channel": e.get("channel") or e.get("uploader"), "views": e.get("view_count"), "query": query})
    return out


def download(item, out_dir, max_height=720):
    import yt_dlp
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{item['id']}.mp4")
    if os.path.exists(path):
        return path
    opts = {"quiet": True, "no_warnings": True, "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
            "format": f"bv*[height<={max_height}][ext=mp4]/bv*[height<={max_height}]/bv*/b[height<={max_height}]/b",   # video only: pose needs no audio, and no ffmpeg is required
            "noplaylist": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([item["url"]])
    if os.path.exists(path):
        return path
    for f in os.listdir(out_dir):                      # video-only streams may come as .webm / .mkv
        if f.startswith(item["id"] + ".") and not f.endswith((".part", ".ytdl")):
            return os.path.join(out_dir, f)
    return None


def _load(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default


def acquire(queries, work_dir, activity, max_videos=20, per_query=8, skip=(), model=None, rate=True, chooser=None, search_kw=None):
    """queries: list of {query, kind}. Downloads at most `max_videos` videos not seen before and adds them to sources.json
    (videos found earlier stay listed). Every video id tried is remembered in tried.json, so a later search never
    repeats a download that failed or a clip that was rejected. Before anything is downloaded the candidates are rated
    (sources.py): the best sources come first and clearly unrelated videos are skipped (`chooser(items, n)` replaces that choice). Returns the newly downloaded items."""
    d = os.path.join(work_dir, activity)
    vid_dir = os.path.join(d, "videos")
    os.makedirs(d, exist_ok=True)
    sources = _load(os.path.join(d, "sources.json"), [])
    tried = set(_load(os.path.join(d, "tried.json"), [])) | {x["id"] for x in sources} | set(skip)
    items, seen = [], set()
    for q in queries:
        print(f"     searching: {q['query']}", flush=True)
        try:
            found = search(q["query"], per_query, **(search_kw or {}))
        except Exception as e:
            print(f"     search failed: {str(e)[:80]}"); continue
        for it in found:
            if it["id"] in seen or it["id"] in tried:
                continue
            seen.add(it["id"]); it["kind"] = q["kind"]; items.append(it)
    if rate and items:
        try:
            sources_mod.rate(activity, items, model)
            print("     candidates by kind: " + ", ".join(f"{k} {v}" for k, v in sorted(sources_mod.tier_counts(items).items())), flush=True)
            items = (chooser or sources_mod.rank_for_footage)(items, max_videos)
        except Exception as e:                  # rating helps but must never stop a run; say so and keep the search order
            print(f"     could not rate the candidates ({str(e)[:80]}); taking them in search order", flush=True)
            items = items[:max_videos]
    else:
        items = items[:max_videos]
    got = []
    print(f"     downloading {len(items)} new videos ...", flush=True)
    for it in items:
        tried.add(it["id"])
        try:
            p = download(it, vid_dir)
            if p:
                it["path"] = p; got.append(it)
                print(f"  downloaded {it['id']}  {it['title'][:60]}")
        except Exception as e:             # a failed download should never stop the run
            print(f"  skipped {it['id']}: {str(e)[:80]}")
    json.dump(sources + got, open(os.path.join(d, "sources.json"), "w"), indent=2)
    json.dump(sorted(tried), open(os.path.join(d, "tried.json"), "w"))
    return got
