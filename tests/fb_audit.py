import json,sys,cv2,numpy as np,random,os,collections
sys.path.insert(0,"tests");sys.path.insert(0,".")
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import stroke_model as M
    H=M.hands()
lab=json.load(open("work/stroke_labels2.json"))
c=[(k,v) for k,v in lab.items() if v.get("stroke") in("forehand","backhand") and v.get("contact_in_frames")=="yes" and v["confidence"]>=2 and v.get("hit_above_head")!="yes" and H.get("/".join(k.split("/")[:2]))=="r"]
rng=random.Random(11);rng.shuffle(c)
tiles=[];key=[]
for want in ("forehand","backhand"):
    n=0
    for k,v in c:
        if v["stroke"]!=want or n>=14: continue
        act,vid=k.split("/")[:2];cap=cv2.VideoCapture(f"work/{act}/videos/{vid}.mp4")
        cap.set(cv2.CAP_PROP_POS_MSEC,v["peak"]*1000);ok,fr=cap.read()
        if not ok or fr is None: continue
        tiles.append((rng.random(),fr,k,want));n+=1
tiles.sort(key=lambda t:t[0]);key=[(i,t[2],t[3]) for i,t in enumerate(tiles)]
imgs=[]
for i,t in enumerate(tiles):
    fr=cv2.resize(t[1],(400,225));cv2.putText(fr,str(i),(6,24),0,.9,(0,255,255),2);imgs.append(fr)
while len(imgs)%4: imgs.append(np.zeros((225,400,3),np.uint8))
for s in range(0,len(imgs),16):
    ch=imgs[s:s+16]
    while len(ch)<16: ch.append(np.zeros((225,400,3),np.uint8))
    cv2.imwrite(f"work/fb_audit_{s//16}.jpg",np.vstack([np.hstack(ch[j:j+4]) for j in range(0,16,4)]))
json.dump(key,open("work/fb_audit_key.json","w"))
print(len(tiles),"tiles")
