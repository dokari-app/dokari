import json,sys,cv2,numpy as np,random,os
exec(open("tests/fb_rule3.py").read().split("def auc")[0])
sel=[r for r in rows if r["v"].get("contact_in_frames")=="yes" and r["v"]["confidence"]>=2 and r["v"]["view_clean"] and r["v"].get("grip")=="one_handed"]
bh=[r for r in sel if r["y"]];random.Random(3).shuffle(bh);bh=bh[:12]
tiles=[]
for r in bh:
    act,vid=r["k"].split("/")[:2];cap=cv2.VideoCapture(f"work/{act}/videos/{vid}.mp4")
    cap.set(cv2.CAP_PROP_POS_MSEC,r["v"]["peak"]*1000);ok,fr=cap.read()
    if not ok: continue
    fr=cv2.resize(fr,(320,180));cv2.putText(fr,f"{vid[:8]} c={r['c']:.2f}",(4,14),0,.45,(0,255,255),1);tiles.append(fr)
while len(tiles)%4: tiles.append(np.zeros((180,320,3),np.uint8))
rowsimg=[np.hstack(tiles[i:i+4]) for i in range(0,len(tiles),4)]
os.makedirs("/tmp/o",exist_ok=True);cv2.imwrite("work/fb_sheet.jpg",np.vstack(rowsimg))
for r in bh: print(r["k"],r["v"]["evidence"])
