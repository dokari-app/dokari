import pickle,json,numpy as np,collections
P2=pickle.load(open("work/pose2d.pkl","rb"));lab=json.load(open("work/stroke_labels3.json"))
def auc(p,n):
    p,n=np.array(p),np.array(n);return float(((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean()))
T=np.arange(-1.0,-0.19,1/12);res=collections.defaultdict(lambda:{"forehand":[],"backhand":[]});offs=[]
for k,(ts,X) in P2.items():
    v=lab[k]
    if v["stroke"] not in("forehand","backhand") or v.get("contact_frame",0)==0 or v.get("confidence",0)<2: continue
    hv={"player_right":"r","player_left":"l"}.get(v.get("hand_vis"))
    if not hv: continue
    w0,w1=v["window"];tc=w0+(w1-w0)*((v["contact_frame"]-1)/7);offs.append(v["peak"]-tc)
    own=1 if hv=="l" else 2;opp=2 if hv=="l" else 1;wr=5 if hv=="l" else 6
    ms=(X[:,1,:2]+X[:,2,:2])/2;mh=(X[:,7,:2]+X[:,8,:2])/2;torso=np.nanmedian(np.linalg.norm(ms-mh,axis=1))
    wide=np.nanmedian(np.abs(X[:,2,0]-X[:,1,0])/torso)>0.45
    if not wide: continue
    sgn=np.sign(X[:,opp,0]-X[:,own,0]);sgn=np.where(sgn==0,np.nan,sgn);cr=(X[:,wr,0]-ms[:,0])*sgn/torso;m=np.isfinite(cr)
    if m.sum()<8: continue
    for name,anc in(("vision contact time",tc),("skeleton swing event",v["peak"]),("skeleton event + 0.3 s",v["peak"]+0.3),("skeleton event - 0.3 s",v["peak"]-0.3)):
        y=np.interp(T+anc,ts[m],cr[m],left=np.nan,right=np.nan);res[name][v["stroke"]].append(np.nanmean(y) if np.isfinite(y).any() else np.nan)
offs=np.array(offs);print("skeleton event minus vision contact (s): median %.2f, 25-75%% %.2f..%.2f, |offset|>0.3 s in %.0f%% of windows"%(np.median(offs),*np.percentile(offs,[25,75]),100*np.mean(np.abs(offs)>0.3)))
for name,d in res.items():
    f=np.array(d["forehand"]);b=np.array(d["backhand"]);f=f[np.isfinite(f)];b=b[np.isfinite(b)]
    print(f"{name:26s} front/back views, AUC {auc(b,f):.3f}  (fh {len(f)}, bh {len(b)})")
