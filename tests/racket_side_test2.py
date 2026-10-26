import json,numpy as np,collections
R=json.load(open(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "work/racket_side.json"));lab=json.load(open("work/stroke_labels3.json"))
def auc(p,n):
    p,n=np.array(p),np.array(n);return float(((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean())) if len(p) and len(n) else float("nan")
rows=[];nodet=0
for k,fr in R.items():
    fr=[f for f in fr if f["rk"] and f["rk"][0]>=0.12]
    if not fr: nodet+=1;continue
    f=max(fr,key=lambda f:(f["off"]==0,f["rk"][0]))
    ls,rs,lw,rw,lh,rh=[np.array(f[x]) for x in("ls","rs","lw","rw","lh","rh")]
    ms=(ls+rs)/2;mh=(lh+rh)/2;torso=np.linalg.norm(ms-mh)
    if torso<5: continue
    x0,y0,x1,y1=f["rk"][1:];rc=np.array([(x0+x1)/2,(y0+y1)/2])
    sgn=np.sign(rs[0]-ls[0]) or 1.0;sw=abs(rs[0]-ls[0])/torso
    lat=lambda x:(x-ms[0])*sgn/torso               # + = toward the player's right
    hand="r" if np.linalg.norm(rw-rc)<np.linalg.norm(lw-rc) else "l"
    far=x1 if abs(x1-ms[0])>abs(x0-ms[0]) else x0
    v=lab[k];vh={"player_right":"r","player_left":"l"}.get(v.get("hand_vis"))
    rows.append(dict(y=int(v["stroke"]=="backhand"),conf=v["confidence"],sw=sw,hand=hand,vh=vh,
        latc=lat(rc[0]),latf=lat(far),lw=lat(rw[0]) if hand=="r" else lat(lw[0])))
print("windows",len(R),"| no racket box (score>=0.12)",nodet,"| usable",len(rows),"| backhand",sum(r["y"] for r in rows))
hh=[(r["hand"],r["vh"]) for r in rows if r["vh"]];print("hand from nearest wrist to racket == hand seen by the labeller:",sum(a==b for a,b in hh),"of",len(hh))
def score(r,key,hand): return -r[key] if hand=="r" else r[key]
def rep(name,sel,key,hk):
    sel=[r for r in sel if r[hk]];y=np.array([r["y"] for r in sel]);c=np.array([score(r,key,r[hk]) for r in sel])
    if y.sum()<3: print(name,"few");return
    a=auc(c[y==1],c[y==0]);acc0=((c>0)==y).mean();bt=max(((c>t)==y).mean() for t in np.linspace(-2,2,81))
    print(f"{name:42s} n={len(sel):4d} bh={int(y.sum()):3d} AUC {a:.3f} acc@0 {acc0:.3f} best {bt:.3f} (majority {max(y.mean(),1-y.mean()):.3f})")
for nm,sel in [("all",rows),("conf>=2",[r for r in rows if r["conf"]>=2]),("front/back view (shoulders wide)",[r for r in rows if r["sw"]>0.5]),("conf>=2 & wide",[r for r in rows if r["conf"]>=2 and r["sw"]>0.5])]:
    for key in("latc","latf"):
        rep(f"{nm} / racket {key[3:]} / hand=nearest wrist",sel,key,"hand")
    rep(f"{nm} / racket centre / hand=labeller",sel,"latc","vh")
print("--- is the pose's left/right identity right? geometric side of racket (from pose names) vs side the labeller saw")
agree=collections.Counter()
for k,fr in R.items():
    fr=[f for f in fr if f["rk"] and f["rk"][0]>=0.12]
    if not fr: continue
    f=max(fr,key=lambda f:(f["off"]==0,f["rk"][0]));ls,rs,lh,rh=[np.array(f[x]) for x in("ls","rs","lh","rh")]
    ms=(ls+rs)/2;torso=np.linalg.norm(ms-(lh+rh)/2);x0,y0,x1,y1=f["rk"][1:]
    if torso<5: continue
    sgn=np.sign(rs[0]-ls[0]) or 1.0;lat=((x0+x1)/2-ms[0])*sgn/torso;sw=abs(rs[0]-ls[0])/torso
    side=lab[k].get("side_vis")
    if side not in("player_right_side","player_left_side") or abs(lat)<0.3: continue
    geo="player_right_side" if lat>0 else "player_left_side"
    agree[("wide" if sw>0.5 else "narrow",geo==side)]+=1
print(dict(agree))
print("--- does the pose swap left/right when the player faces away from the camera? (nose visibility = facing the camera)")
import pickle
P2=pickle.load(open("work/pose2d.pkl","rb"))
tab=collections.Counter()
for k,fr in R.items():
    fr=[f for f in fr if f["rk"] and f["rk"][0]>=0.12]
    if not fr or k not in P2: continue
    f=max(fr,key=lambda f:(f["off"]==0,f["rk"][0]))
    vh={"player_right":"r","player_left":"l"}.get(lab[k].get("hand_vis"))
    if not vh: continue
    ts,A=P2[k];nv=float(np.nanmedian(A[:,0,2]))
    rc=np.array([(f["rk"][1]+f["rk"][3])/2,(f["rk"][2]+f["rk"][4])/2]);rw,lw=np.array(f["rw"]),np.array(f["lw"])
    hand="r" if np.linalg.norm(rw-rc)<np.linalg.norm(lw-rc) else "l"
    b="nose clearly visible (faces camera)" if nv>0.8 else ("nose hidden (back to camera)" if nv<0.4 else "in between")
    tab[(b,vh,hand==vh)]+=1
for b in ("nose clearly visible (faces camera)","in between","nose hidden (back to camera)"):
    for vh in "rl":
        ok,no=tab[(b,vh,True)],tab[(b,vh,False)]
        if ok+no: print(f"  {b:38s} labeller says racket hand={vh}: pose agrees {ok} / disagrees {no}")
print("--- per video: share of windows where the pose's nearest-wrist hand equals the labeller's racket hand (mixed values = flips inside one video)")
bv=collections.defaultdict(list)
for k,fr in R.items():
    fr=[f for f in fr if f["rk"] and f["rk"][0]>=0.12]
    if not fr: continue
    f=max(fr,key=lambda f:(f["off"]==0,f["rk"][0]));vh={"player_right":"r","player_left":"l"}.get(lab[k].get("hand_vis"))
    if not vh: continue
    rc=np.array([(f["rk"][1]+f["rk"][3])/2,(f["rk"][2]+f["rk"][4])/2]);rw,lw=np.array(f["rw"]),np.array(f["lw"])
    bv[k.split("/")[1]].append(("r" if np.linalg.norm(rw-rc)<np.linalg.norm(lw-rc) else "l")==vh)
sh=[np.mean(v) for v in bv.values() if len(v)>=4]
print("videos with >=4 windows:",len(sh),"| share bins (0-.2,.2-.4,.4-.6,.6-.8,.8-1):",np.histogram(sh,bins=[0,.2,.4,.6,.8,1.01])[0].tolist())
