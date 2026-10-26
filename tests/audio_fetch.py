"""Download AUDIO ONLY for a sample of the labelled videos (the factory's video files have no sound). Run on the Mac with VPN off.
  python tests/audio_fetch.py --n 60      -> work/audio/<video id>.m4a   (about 5-10 MB each; skips files already there; safe to stop and restart)"""
import argparse, json, os, random, sys
sys.path.insert(0, ".")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=60); a = ap.parse_args()
    import yt_dlp
    lab = json.load(open("work/stroke_labels3.json")); vids = sorted({k.split("/")[1] for k, v in lab.items() if v["stroke"] in ("forehand", "backhand", "serve") and v.get("confidence", 0) >= 2})
    random.Random(4).shuffle(vids); os.makedirs("work/audio", exist_ok=True); got = 0
    opts = {"format": "bestaudio[ext=m4a]/bestaudio", "outtmpl": "work/audio/%(id)s.%(ext)s", "quiet": True, "no_warnings": True, "noprogress": True, "retries": 2}
    with yt_dlp.YoutubeDL(opts) as ydl:
        for v in vids:
            if got >= a.n: break
            if any(f.startswith(v + ".") for f in os.listdir("work/audio")): got += 1; continue
            try:
                ydl.download([f"https://www.youtube.com/watch?v={v}"]); got += 1; print(f"  {got}/{a.n} {v}", flush=True)
            except Exception as e:
                print("  skipped", v, str(e)[:80], flush=True)
    print("done", got)


if __name__ == "__main__":
    main()
