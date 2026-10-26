import json,sys,numpy as np,collections,os
sys.path.insert(0,".")
from scipy.ndimage import gaussian_filter1d
from sphere.skeleton import J
lab=json.load(open("work/stroke_labels2.json"))
cache={};rows=[]
for k,v in lab.items():
    if v.get("stroke") not in("forehand","backhand") or v.get("hit_above_head")=="yes" or v.get("contact_in_frames")=="no": continue
    act,vid=k.split("/")[:2];f=f"work/{act}/clips/{vid}.npz"
    if not os.path.exists(f): continue
    if f not in cache:
        d=np.load(f,allow_pickle=True);cache[f]=(gaussian_filter1d(d["pose"],1.5,axis=0,mode="nearest"),float(d["fps"]))
    P,fps=cache[f];pk=int(round(v["peak"]*fps));a,b=max(0,pk-int(.35*fps)),min(len(P),pk+int(.35*fps)+1)
    if b-a<5: continue
    sp={s:np.linalg.norm(np.gradient(P[:,J[f"{s}_wrist"]],axis=0),axis=1)[a:b] for s in "lr"}
    s="r" if sp["r"].max()>=sp["l"].max() else "l";o="l" if s=="r" else "r"
    i=a+int(np.argmax(sp[s]))
    own,opp=P[:,J[f"{s}_shoulder"]],P[:,J[f"{o}_shoulder"]]
    u=opp-own;u[:,1]=0;w=np.linalg.norm(u,axis=1,keepdims=True)+1e-6;u=u/w
    ms=(own+opp)/2
    cr=((P[:,J[f"{s}_wrist"]]-ms)*u).sum(1)/w[:,0]
    two=np.linalg.norm(P[i,J["l_wrist"]]-P[i,J["r_wrist"]])/w[i,0]
    rows.append(dict(y=int(v["stroke"]=="backhand"),c=float(cr[i]),cm=float(cr[max(a,i-4):i+5].max()),two=float(two),clean=v["view_clean"],conf=v["confidence"],vid=vid,grip=v.get("grip")))
def auc(p,n):
    p,n=np.array(p),np.array(n);return float(((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean()))
def rep(name,R):
    y=np.array([r["y"] for r in R]);c=np.array([r["c"] for r in R])
    best=max(((c>t)==y).mean() for t in np.linspace(-1,1,81))
    print(name,"n",len(R),"bh",y.sum(),"AUC",round(auc(c[y==1],c[y==0]),3),"best-threshold acc",round(float(best),3),"median c fh/bh",round(float(np.median(c[y==0])),2),round(float(np.median(c[y==1])),2))
rep("all",rows);rep("clean conf>=2",[r for r in rows if r["clean"] and r["conf"]>=2]);rep("clean conf3",[r for r in rows if r["clean"] and r["conf"]>=3])
rep("one-handed grip",[r for r in rows if r["grip"] and "one" in str(r["grip"])])
rep("two-handed grip",[r for r in rows if r["grip"] and "two" in str(r["grip"])])
print(collections.Counter(r["grip"] for r in rows))
