import json,sys,os,numpy as np,collections
sys.path.insert(0,".")
from scipy.ndimage import gaussian_filter1d
from sphere.skeleton import J
lab=json.load(open("work/stroke_labels3.json"))
def auc(p,n):
    p,n=np.array(p),np.array(n);return float(((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean()))
T=np.arange(-1.0,-0.19,1/10);res=collections.defaultdict(lambda:{"forehand":[],"backhand":[]});cache={}
for k,v in lab.items():
    if v["stroke"] not in("forehand","backhand") or v.get("contact_frame",0)==0 or v.get("confidence",0)<2: continue
    hv={"player_right":"r","player_left":"l"}.get(v.get("hand_vis"))
    if not hv: continue
    act,vid=k.split("/")[:2];f=f"work/{act}/clips/{vid}.npz"
    if not os.path.exists(f): continue
    if f not in cache:
        d=np.load(f,allow_pickle=True);cache[f]=(gaussian_filter1d(d["pose"],1.5,axis=0,mode="nearest"),float(d["fps"]))
    P,fps=cache[f];w0,w1=v["window"];tc=w0+(w1-w0)*((v["contact_frame"]-1)/7)
    o="l" if hv=="r" else "r"
    own,opp=P[:,J[f"{hv}_shoulder"]],P[:,J[f"{o}_shoulder"]];u=opp-own;u[:,1]=0;w=np.linalg.norm(u,axis=1,keepdims=True)+1e-6;u=u/w
    t=np.arange(len(P))/fps;ms=(own+opp)/2;torso=np.median(np.linalg.norm(ms-(P[:,J["l_hip"]]+P[:,J["r_hip"]])/2,axis=1))
    # fixed lateral axis for the window: mean shoulder line over the take-back (avoids trunk rotation circularity), torso-normalised
    a,b=int((tc-1.0)*fps),int((tc-0.2)*fps)
    if a<0 or b>=len(P): continue
    ub=u[a:b].mean(0);ub/=np.linalg.norm(ub)+1e-9
    cr=((P[:,J[f"{hv}_wrist"]]-ms)*ub).sum(1)/torso
    sidelook=abs(ub[2])   # |shoulder line along camera depth|: 1 = side-on, 0 = front/back
    sp=np.linalg.norm(np.gradient(P[:,J[f"{hv}_wrist"]],axis=0),axis=1)*fps
    lo,hi=int((v["peak"]-0.6)*fps),int((v["peak"]+0.6)*fps);lo=max(lo,0);hi=min(hi,len(P)-1)
    hp=(lo+int(np.argmax(sp[lo:hi+1])))/fps
    for name,anc in(("vision contact",tc),("skeleton event",v["peak"]),("racket-hand speed peak",hp)):
        y=np.interp(T+anc,t,cr);res[(name,"side-on" if sidelook>0.7 else "front/back" if sidelook<0.4 else "oblique")][v["stroke"]].append(float(np.mean(y)))
    for name,anc in(("vision contact",tc),("skeleton event",v["peak"]),("racket-hand speed peak",hp)):
        res[(name,"all views")][v["stroke"]].append(float(np.mean(np.interp(T+anc,t,cr))))
for (name,view),d in sorted(res.items()):
    f,b=np.array(d["forehand"]),np.array(d["backhand"])
    if len(b)>=5 and len(f)>=5: print(f"depth pose, {name:15s} {view:11s} AUC {auc(b,f):.3f} (fh {len(f)}, bh {len(b)})")
