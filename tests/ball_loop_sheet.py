"""Contact sheet of the pseudo-labelled balls: one row per accepted window, up to 10 crops, each with the labelled position circled. python tests/ball_loop_sheet.py out.png"""
import glob, os, pickle, sys, numpy as np, cv2
rows = []
for f in sorted(glob.glob("work/ball_pseudo/*.npz")):
    tag = os.path.basename(f)[:-4]; z = np.load(f); w = pickle.load(open(glob.glob(f"work/ball_s_*/{tag}.cache.pkl")[0], "rb")); imgs = w["imgs"]; H, W = imgs[0].shape[:2]
    idx = np.where(z["y"] == 1)[0]; frs = sorted(set(z["frame"][idx].tolist())); sel = [frs[int(k)] for k in np.linspace(0, len(frs) - 1, min(10, len(frs)))]; tiles = []
    for fr in sel:
        k = idx[z["frame"][idx] == fr][0]; x, y = z["xy"][k] * np.array([W, H]); r = int(max(30, 2.5 * 0.035 * z["ph"]))
        x0, y0 = int(min(max(x - r, 0), W - 2 * r)), int(min(max(y - r, 0), H - 2 * r)); c = imgs[fr][y0:y0 + 2 * r, x0:x0 + 2 * r].copy()
        cv2.circle(c, (int(x - x0), int(y - y0)), int(max(5, 0.035 * z["ph"])), (0, 0, 255), 1); t = cv2.resize(c, (120, 120)); cv2.putText(t, str(len(rows)), (2, 14), 0, 0.5, (0, 255, 255), 1); tiles.append(t)
    while len(tiles) < 10: tiles.append(np.zeros((120, 120, 3), np.uint8))
    rows.append(np.hstack(tiles)); print(len(rows) - 1, tag)
cv2.imwrite(sys.argv[1], np.vstack(rows))
