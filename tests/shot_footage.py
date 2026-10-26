"""Collect footage for the strokes the library lacks (volley, smash, slice, drop shot, lob, backhand), the way the
labeller will check it: pro compilations and technique videos named after the stroke, 480p to save disk and time.
Nothing is trusted by its title: stroke_label2.py decides what is in the frames afterwards.
  python tests/shot_footage.py --estimate              queries and counts, downloads nothing
  python tests/shot_footage.py --per-stroke 12         search, download (480p), extract skeletons; safe to stop and restart
Videos land in work/tennis_<stroke>/videos like the other collections."""
import argparse, json, os, shutil, sys, time
sys.path.insert(0, ".")
from sphere import acquire, extract

QUERIES = {
    "volley": ["best tennis volleys compilation pro", "forehand volley technique lesson slow motion", "backhand volley technique drill", "ATP net play volley highlights"],
    "overhead_smash": ["best tennis overhead smashes compilation", "overhead smash technique lesson", "ATP smash highlights slow motion"],
    "slice": ["best backhand slice compilation tennis pro", "tennis slice technique demonstration slow motion", "forehand slice pro tennis"],
    "drop_shot": ["best drop shots tennis compilation", "drop shot tutorial tennis technique", "ATP drop shot highlights"],
    "lob": ["best tennis lobs compilation", "lob technique tennis lesson"],
    "backhand": ["one handed backhand pro slow motion compilation", "two handed backhand pro slow motion", "backhand technique lesson tennis"],
}
MIN_FREE_GB = 5


def fetch(it, out_dir, cookies_browser=None, max_height=480):
    """Download one video (video stream only). cookies_browser: 'chrome' | 'safari' | 'firefox' | None."""
    import yt_dlp
    os.makedirs(out_dir, exist_ok=True)
    opts = {"quiet": True, "no_warnings": True, "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"), "noplaylist": True,
            "format": f"bv*[height<={max_height}][ext=mp4]/bv*[height<={max_height}]/bv*/b[height<={max_height}]/b"}
    if cookies_browser:
        opts["cookiesfrombrowser"] = (cookies_browser,)
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([it["url"]])
    for f in os.listdir(out_dir):
        if f.startswith(it["id"] + ".") and not f.endswith((".part", ".ytdl")):
            return os.path.join(out_dir, f)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-stroke", type=int, default=12); ap.add_argument("--per-query", type=int, default=8)
    ap.add_argument("--strokes", default=",".join(QUERIES)); ap.add_argument("--estimate", action="store_true")
    ap.add_argument("--cookies-from-browser", default=None, help="chrome | safari | firefox: use that browser's YouTube sign-in (needed when YouTube asks to confirm you are not a bot)")
    args = ap.parse_args()
    for s in args.strokes.split(","):
        act = "tennis_" + s
        d = f"work/{act}"; vdir = d + "/videos"
        os.makedirs(vdir, exist_ok=True)
        src = json.load(open(d + "/sources.json")) if os.path.exists(d + "/sources.json") else []
        tf = d + "/shot_tried.json"
        tried = set(json.load(open(tf))) if os.path.exists(tf) else set()
        tried |= {x["id"] for x in src} | {os.path.splitext(f)[0] for f in os.listdir(vdir)}
        print(f"\n== {s}: {len(os.listdir(vdir))} videos already", flush=True)
        items, seen = [], set()
        for q in QUERIES[s]:
            print("  searching:", q, flush=True)
            try:
                found = acquire.search(q, args.per_query, min_s=20, max_s=900)
            except Exception as e:
                print("  search failed:", str(e)[:80]); continue
            for it in found:
                if it["id"] in seen or it["id"] in tried:
                    continue
                seen.add(it["id"]); it["kind"] = "stroke_footage"; items.append(it)
        items = items[:args.per_stroke]
        print(f"  {len(items)} new videos to fetch:", flush=True)
        for it in items:
            print("    ", it["id"], (it.get("title") or "")[:70], it.get("duration"))
        if args.estimate:
            continue
        bot_blocks = 0
        got = []
        for it in items:
            if bot_blocks >= 3:
                break
            free = shutil.disk_usage(".").free / 1e9
            if free < MIN_FREE_GB:
                print(f"  only {free:.1f} GB free: stopping so the disk does not fill"); return
            try:
                p = fetch(it, vdir, args.cookies_from_browser)
                if p:
                    it["path"] = p; got.append(it); tried.add(it["id"]); bot_blocks = 0; print("  downloaded", it["id"], flush=True)
            except Exception as e:
                msg = str(e)
                if "not a bot" in msg or "Sign in" in msg:
                    bot_blocks += 1
                    print("  YouTube asks to confirm you are not a bot:", it["id"], flush=True)
                else:
                    tried.add(it["id"])           # a real failure (private, removed, 403): do not retry it
                    print("  skipped", it["id"], msg[:80], flush=True)
        if bot_blocks >= 3:
            print("\n  YouTube is blocking downloads from this network. Stopping so the block does not get worse.\n"
                  "  Options: rerun with --cookies-from-browser chrome (uses your signed-in Chrome), or try another network, or wait a few hours.")
            json.dump(src + got, open(d + "/sources.json", "w"), indent=2)
            json.dump(sorted(tried), open(tf, "w"))
            return
        json.dump(src + got, open(d + "/sources.json", "w"), indent=2)
        json.dump(sorted(tried), open(tf, "w"))
        if got:
            extract.extract_folder(vdir, d + "/clips", src + got, delete_video=False, variant="full", workers=3, ball_windows=False)
    print("\ndone. Next: python tests/stroke_label2.py --acts " + ",".join("tennis_" + s for s in args.strokes.split(",")) + " --swing-per-clip 10 --over-per-clip 3 --cap 1500")


if __name__ == "__main__":
    main()
