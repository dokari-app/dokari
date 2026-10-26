import pickle,json,numpy as np,collections
import matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
P2=pickle.load(open("work/pose2d.pkl","rb"));lab=json.load(open("work/stroke_labels3.json"))
T=np.arange(-1.2,0.41,1/12);curves=collections.defaultdict(list);meta=collections.Counter()
for k,A in P2.items():
    v=lab[k]
    if v["stroke"] not in("forehand","backhand") or v.get("contact_frame",0)==0 or v.get("confidence",0)<2: continue
    hv={"player_right":"r","player_left":"l"}.get(v.get("hand_vis"))
    if not hv: continue
    ts,X=A;w0,w1=v["window"];tc=w0+(w1-w0)*((v["contact_frame"]-1)/7)
    own=1 if hv=="l" else 2;opp=2 if hv=="l" else 1;wr=5 if hv=="l" else 6   # 1 lsh 2 rsh 5 lwr 6 rwr
    ms=(X[:,1,:2]+X[:,2,:2])/2;mh=(X[:,7,:2]+X[:,8,:2])/2;torso=np.nanmedian(np.linalg.norm(ms-mh,axis=1))
    sw=np.abs(X[:,2,0]-X[:,1,0])/torso
    sgn=np.sign(X[:,opp,0]-X[:,own,0]);sgn=np.where(sgn==0,np.nan,sgn)
    cross=(X[:,wr,0]-ms[:,0])*sgn/torso            # own side negative, opposite side positive
    y=np.interp(T+tc,ts,np.nan_to_num(cross,nan=np.nan),left=np.nan,right=np.nan) if np.isfinite(cross).sum()>6 else None
    if y is None: continue
    m=np.isfinite(cross);y=np.interp(T+tc,ts[m],cross[m],left=np.nan,right=np.nan)
    wide=np.nanmedian(sw)>0.45
    curves[(v["stroke"],"wide" if wide else "narrow")].append(y);meta[(v["stroke"],"wide" if wide else "narrow")]+=1
print(dict(meta))
fig,ax=plt.subplots(1,2,figsize=(13,4.5),sharey=True)
for a,view in zip(ax,("wide","narrow")):
    for s,c in (("forehand","tab:green"),("backhand","tab:red")):
        Y=np.array(curves[(s,view)])
        if len(Y)==0: continue
        med=np.nanmedian(Y,0);q1=np.nanpercentile(Y,25,0);q3=np.nanpercentile(Y,75,0)
        a.plot(T,med,c=c,label=f"{s} (n={len(Y)})");a.fill_between(T,q1,q3,color=c,alpha=.18)
    a.axvline(0,c="k",ls=":");a.axhline(0,c="grey",lw=.5);a.set_title(("shoulders wide in image (front/back view)" if view=="wide" else "shoulders narrow (side-on view)"));a.set_xlabel("seconds from contact");a.legend()
ax[0].set_ylabel("racket-hand wrist across the body\n(negative = own side, positive = opposite side), in torso lengths")
plt.tight_layout();plt.savefig("work/traj_plot.png",dpi=90)
print("--- separability with contact time and racket hand known (ceiling), take-back phase")
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
def auc(p,n):
    p,n=np.array(p),np.array(n);return float(((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean()))
sel=(T>=-1.0)&(T<=-0.2)
for view in("wide","narrow"):
    F=curves[("forehand",view)];B=curves[("backhand",view)]
    f=[np.nanmean(np.array(y)[sel]) for y in F];b=[np.nanmean(np.array(y)[sel]) for y in B]
    fm=[np.nanmax(np.array(y)[sel]) for y in F];bm=[np.nanmax(np.array(y)[sel]) for y in B]
    f=np.array(f);b=np.array(b);print(view,"AUC mean cross -1.0..-0.2 s:",round(auc(b[np.isfinite(b)],f[np.isfinite(f)]),3),"| AUC max:",round(auc(np.array(bm)[np.isfinite(bm)],np.array(fm)[np.isfinite(fm)]),3))
