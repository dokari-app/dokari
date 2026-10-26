"""Do the phone's body positions match the Mac's for the same video?

  python tests/compare_skeletons.py "work/auto/coaching/IMG_2935 3.skeleton.npz" "work/phone/phone-IMG_2935 3.skeleton.npz"

Three levels, from raw to what matters:
  1. the joints themselves (centimetres apart, per joint)
  2. the signals the engine measures (angles of the swing events: how well the two curves follow each other)
  3. what the engine concludes: the swings it finds and what it takes them for, side by side"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import coach                                              # noqa: E402
from sphere.features import compute_features             # noqa: E402
from sphere.identify import identify                      # noqa: E402
from sphere.skeleton import JOINTS, load_clip             # noqa: E402


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    mac, phone = load_clip(sys.argv[1]), load_clip(sys.argv[2])
    print(f"Mac    {len(mac['pose'])} frames at {mac['fps']:.2f} fps, person found in {mac['meta'].get('detect_rate')}")
    print(f"Phone  {len(phone['pose'])} frames at {phone['fps']:.2f} fps, person found in {phone['meta'].get('detect_rate')}  ({phone['meta'].get('tracker')})")
    n = min(len(mac["pose"]), len(phone["pose"]))
    if abs(len(mac["pose"]) - len(phone["pose"])) > 2 or abs(mac["fps"] - phone["fps"]) > 0.5:
        print("  ! the two do not have the same number of frames or the same frame rate: comparing the first", n, "frames")
    a = {"pose": mac["pose"][:n], "vis": mac["vis"][:n], "fps": mac["fps"], "meta": mac["meta"]}
    b = {"pose": phone["pose"][:n], "vis": phone["vis"][:n], "fps": phone["fps"], "meta": phone["meta"]}
    both = (a["vis"].mean(1) > 0.4) & (b["vis"].mean(1) > 0.4)

    print(f"\n1. Joints: distance between Mac and phone, in centimetres (frames where both found the person: {both.sum()} of {n})")
    d = 100 * np.linalg.norm(a["pose"][both] - b["pose"][both], axis=2)
    print(f"   {'joint':<11} {'median':>7} {'90 %':>7} {'worst':>7}")
    for j, name in enumerate(JOINTS):
        print(f"   {name:<11} {np.median(d[:, j]):7.1f} {np.percentile(d[:, j], 90):7.1f} {d[:, j].max():7.1f}")
    print(f"   all joints: median {np.median(d):.1f} cm, 90 % under {np.percentile(d, 90):.1f} cm")
    mirrored = 100 * np.linalg.norm(a["pose"][both][:, [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]] - b["pose"][both], axis=2)
    if np.median(mirrored) < np.median(d):
        print("   ! left and right look swapped between the two (the phone's picture may be mirrored)")

    print("\n2. Signals the engine measures (angles in degrees, others in torso lengths)")
    names, Fa, _ = compute_features(a)
    _, Fb, _ = compute_features(b)
    wanted = []
    for act, entry in coach.load_all_entries("tennis_serve,tennis_forehand").items():
        for e in entry["metadata"]["provenance"]["attempt_events"]:
            if e["feature"] in names and e["feature"] not in wanted:
                wanted.append(e["feature"])
    print(f"   {'signal':<34} {'range':>7} {'typical gap':>12} {'follows (r)':>12}")
    for f in wanted:
        x, y = Fa[:, names.index(f)], Fb[:, names.index(f)]
        ok = np.isfinite(x) & np.isfinite(y)
        if ok.sum() < 10:
            continue
        span = np.nanpercentile(x[ok], 95) - np.nanpercentile(x[ok], 5)
        print(f"   {f:<34} {span:7.1f} {np.median(np.abs(x[ok] - y[ok])):12.1f} {np.corrcoef(x[ok], y[ok])[0, 1]:12.3f}")

    print("\n3. What the engine concludes")
    entries = coach.load_all_entries("tennis_serve,tennis_forehand")
    rows = {}
    for label, clip in (("Mac", a), ("phone", b)):
        _, found = identify(entries, clip)
        rows[label] = [(f["start"], f["end"], f["activity"]) for f in found if f["owner"] == f["activity"]]
        print(f"   {label:<6} {len(rows[label])} swings: " + ", ".join(f"{s:.1f}s {act.replace('tennis_', '')}" for s, e, act in rows[label]))
    agree = sum(any(abs(s - s2) < 0.5 and act == act2 for s2, e2, act2 in rows["phone"]) for s, e, act in rows["Mac"])
    print(f"   {agree} of the Mac's {len(rows['Mac'])} swings are found by the phone at the same time with the same name")


if __name__ == "__main__":
    main()
