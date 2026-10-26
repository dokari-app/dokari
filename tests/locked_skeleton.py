"""Score the final skeleton networks (trained WITHOUT the held-out videos) on the locked windows. Depth pose only, the same input the app has. Mac (torch).
  python tests/locked_skeleton.py  -> work/locked/skel_preds.json"""
import json, os, sys
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
import numpy as np, torch
import stroke_net as sn


def main():
    cfg = json.load(open("work/net_final/locked_config.json")); sn.CHAN, sn.ARCH = "3d", "conv"
    key = json.load(open("work/locked/key_DO_NOT_OPEN.json")); lab = json.load(open("work/stroke_labels3.json"))
    dev = "mps" if torch.backends.mps.is_available() else "cpu"; nets = []
    for i in range(cfg["n"]):
        net = sn.Net(cfg["cin"], len(sn.CLASSES)); net.load_state_dict(torch.load(f"work/net_final/locked_s{i}.pt", map_location="cpu")); nets.append(net.to(dev).eval())
    out = {}
    for iid, v in key.items():
        k = v["key"]; act, vid = k.split("/")[:2]
        try: P, fps = sn.clip(act, vid)
        except Exception: continue
        x = torch.tensor(np.stack([sn.tensor_from_clip(P, fps, lab[k]["peak"]), sn.tensor_from_clip(P, fps, lab[k]["peak"], mirror=True)])).to(dev)
        with torch.no_grad(): p = np.mean([(torch.softmax(n(x[:1]), 1) + torch.softmax(n(x[1:]), 1)).cpu().numpy()[0] / 2 for n in nets], 0)
        out[iid] = p.tolist()
    json.dump(out, open("work/locked/skel_preds.json", "w")); print("scored", len(out), "of", len(key))


if __name__ == "__main__":
    main()
