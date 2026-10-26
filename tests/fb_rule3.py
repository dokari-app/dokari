import json,sys,numpy as np,collections,os
sys.path.insert(0,".")
from scipy.ndimage import gaussian_filter1d
from sphere.skeleton import J
lab=json.load(open("work/stroke_labels2.json"));cache={};rows=[]
for k,v in lab.items():
    if v.get("stroke") not in("forehand","backhand") or v.get("hit_above_head")=="yes": continue
    act,vid=k.split("/")[:2];f=f"work/{act}/clips/{vid}.npz"
    if not os.path.exists(f): continue
    if f not in cache:
        d=np.load(f,allow_pickle=True);cache[f]=(gaussian_filter1d(d["pose"],1.5,axis=0,mode="nearest"),float(d["fps"]))
    P,fps=cache[f];pk=int(round(v["peak"]*fps));a,b=max(0,pk-int(.35*fps)),min(len(P),pk+int(.35*fps)+1)
    if b-a<5: continue
    sp={s:np.linalg.norm(np.gradient(P[:,J[f"{s}_wrist"]],axis=0),axis=1)[a:b] for s in "lr"}
    s="r" if sp["r"].max()>=sp["l"].max() else "l";o="l" if s=="r" else "r";i=a+int(np.argmax(sp[s]))
    own,opp=P[:,J[f"{s}_shoulder"]],P[:,J[f"{o}_shoulder"]];u=opp-own;u[:,1]=0;w=np.linalg.norm(u,axis=1,keepdims=True)+1e-6;u=u/w
    cr=((P[:,J[f"{s}_wrist"]]-(own+opp)/2)*u).sum(1)/w[:,0]
    rows.append(dict(y=int(v["stroke"]=="backhand"),c=float(cr[i]),v=v,k=k))
def auc(p,n):
    p,n=np.array(p),np.array(n);return float(((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean()))
def rep(n,R):
    y=np.array([r["y"] for r in R]);c=np.array([r["c"] for r in R])
    if y.sum()<3 or (1-y).sum()<3: print(n,len(R),"few");return
    print(n,"n",len(R),"bh",int(y.sum()),"AUC",round(auc(c[y==1],c[y==0]),3),"med fh/bh",round(float(np.median(c[y==0])),2),round(float(np.median(c[y==1])),2))
q=lambda r:r["v"]
rep("contact yes",[r for r in rows if q(r).get("contact_in_frames")=="yes"])
rep("contact yes & conf>=2 & clean",[r for r in rows if q(r).get("contact_in_frames")=="yes" and q(r)["confidence"]>=2 and q(r)["view_clean"]])
rep("contact yes & conf3",[r for r in rows if q(r).get("contact_in_frames")=="yes" and q(r)["confidence"]>=3])
rep("1H, contact yes, conf>=2",[r for r in rows if q(r).get("grip")=="one_handed" and q(r).get("contact_in_frames")=="yes" and q(r)["confidence"]>=2])
print("confidence dist bh:",collections.Counter(q(r)["confidence"] for r in rows if r["y"]),"fh:",collections.Counter(q(r)["confidence"] for r in rows if not r["y"]))
print("contact dist bh:",collections.Counter(q(r).get("contact_in_frames") for r in rows if r["y"]),"fh:",collections.Counter(q(r).get("contact_in_frames") for r in rows if not r["y"]))
