import json,sys,numpy as np,collections,os
sys.path.insert(0,"tests");sys.path.insert(0,".")
from scipy.ndimage import gaussian_filter1d
from sphere.skeleton import J
import stroke_model as M
H=M.hands()
lab=json.load(open("work/stroke_labels2.json"));cache={};rows=[]
for k,v in lab.items():
    if v.get("stroke") not in("forehand","backhand") or v.get("hit_above_head")=="yes" or v.get("contact_in_frames")=="no": continue
    act,vid=k.split("/")[:2]
    if f"{act}/{vid}" not in H: continue
    f=f"work/{act}/clips/{vid}.npz"
    if not os.path.exists(f): continue
    if f not in cache:
        d=np.load(f,allow_pickle=True);cache[f]=(gaussian_filter1d(d["pose"],1.5,axis=0,mode="nearest"),float(d["fps"]))
    P,fps=cache[f];pk=int(round(v["peak"]*fps));a,b=max(0,pk-int(.35*fps)),min(len(P),pk+int(.35*fps)+1)
    if b-a<5: continue
    s=H[f"{act}/{vid}"];o="l" if s=="r" else "r"
    sp=np.linalg.norm(np.gradient(P[:,J[f"{s}_wrist"]],axis=0),axis=1)[a:b];i=a+int(np.argmax(sp))
    own,opp=P[:,J[f"{s}_shoulder"]],P[:,J[f"{o}_shoulder"]]
    u=opp-own;u[:,1]=0;w=np.linalg.norm(u,axis=1,keepdims=True)+1e-6;u=u/w
    cr=((P[:,J[f"{s}_wrist"]]-(own+opp)/2)*u).sum(1)/w[:,0]
    # mean of both wrists relative to racket-side
    cb=((((P[:,J["l_wrist"]]+P[:,J["r_wrist"]])/2)-(own+opp)/2)*u).sum(1)/w[:,0]
    rows.append(dict(y=int(v["stroke"]=="backhand"),c=float(cr[i]),cb=float(cb[i]),grip=v.get("grip"),clean=v["view_clean"],conf=v["confidence"],hand=s))
def auc(p,n):
    p,n=np.array(p),np.array(n);return float(((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean()))
for name,R in [("all",rows),("one-handed",[r for r in rows if r["grip"]=="one_handed"]),("two-handed",[r for r in rows if r["grip"]=="two_handed"]),("lefty",[r for r in rows if r["hand"]=="l"])]:
    y=np.array([r["y"] for r in R])
    if y.sum()<3: print(name,len(R),"few bh");continue
    for key in("c","cb"):
        c=np.array([r[key] for r in R]);print(name,key,"n",len(R),"bh",int(y.sum()),"AUC",round(auc(c[y==1],c[y==0]),3),"median fh/bh",round(float(np.median(c[y==0])),2),round(float(np.median(c[y==1])),2))
print("-----")
import random
lab2=[(k,v) for k,v in lab.items() if v.get("stroke")=="backhand" and v.get("grip")=="one_handed" and f"{k.split('/')[0]}/{k.split('/')[1]}" in H]
random.Random(1).shuffle(lab2)
for k,v in lab2[:14]: print(k,H[f"{k.split('/')[0]}/{k.split('/')[1]}"],v["confidence"],v["evidence"])
