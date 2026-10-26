"""Forehand vs backhand only, take-back features anchored at the SKELETON event (as live), racket hand known (oracle). Grouped CV by video."""
import pickle,json,os,sys,numpy as np,collections
from scipy.ndimage import gaussian_filter1d
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
sys.path.insert(0,".")
from sphere.skeleton import J
P2=pickle.load(open("work/pose2d.pkl","rb"));lab=json.load(open("work/stroke_labels3.json"))
def hands():
    out={}
    for k,fr in json.load(open("work/stroke_hands.json")).items():
        c=collections.Counter(x["racket_hand"] for x in fr if x["racket_hand"]!="unclear")
        if sum(c.values())>=2 and c.most_common(1)[0][1]/sum(c.values())>=0.67: out[k]="r" if c.most_common(1)[0][0]=="player_right" else "l"
    return out
VH=hands();cache={}
OFFS=np.arange(-1.3,0.01,0.1)
def feats(k,v,hv):
    act,vid=k.split("/")[:2];ts,X=P2[k];f={}
    own=1 if hv=="l" else 2;opp=2 if hv=="l" else 1;wr=5 if hv=="l" else 6
    ms=(X[:,1,:2]+X[:,2,:2])/2;mh=(X[:,7,:2]+X[:,8,:2])/2;torso=np.nanmedian(np.linalg.norm(ms-mh,axis=1))
    if not np.isfinite(torso) or torso<.05: return None
    sw=np.abs(X[:,2,0]-X[:,1,0])/torso;f["view_w"]=float(np.nanmedian(sw))
    sg=np.sign(X[:,opp,0]-X[:,own,0]);sg=np.where(sg==0,np.nan,sg);cr=(X[:,wr,0]-ms[:,0])*sg/torso;m=np.isfinite(cr)
    if m.sum()<8: return None
    y=np.interp(v["peak"]+OFFS,ts[m],cr[m],left=np.nan,right=np.nan)
    if np.isnan(y).mean()>.3: return None
    for i,val in enumerate(y): f[f"c2_{i}"]=val
    f["c2_max"]=np.nanmax(y);f["c2_min"]=np.nanmin(y);f["c2_mean"]=np.nanmean(y);f["c2_argmax"]=float(np.nanargmax(y))
    # depth pose, fixed lateral axis from the shoulder line over the window
    cf=f"work/{act}/clips/{vid}.npz"
    if os.path.exists(cf):
        if cf not in cache:
            d=np.load(cf,allow_pickle=True);cache[cf]=(gaussian_filter1d(d["pose"],1.5,axis=0,mode="nearest"),float(d["fps"]))
        P,fps=cache[cf];o="l" if hv=="r" else "r";own3,opp3=P[:,J[f"{hv}_shoulder"]],P[:,J[f"{o}_shoulder"]];u=opp3-own3;u[:,1]=0
        a,b=int((v["peak"]-1.3)*fps),int((v["peak"])*fps)
        if a>=0 and b<len(P):
            ub=u[a:b].mean(0);ub/=np.linalg.norm(ub)+1e-9;ms3=(own3+opp3)/2;t3=np.median(np.linalg.norm(ms3-(P[:,J["l_hip"]]+P[:,J["r_hip"]])/2,axis=1))
            c3=((P[:,J[f"{hv}_wrist"]]-ms3)*ub).sum(1)/t3;tt=np.arange(len(P))/fps;y3=np.interp(v["peak"]+OFFS,tt,c3)
            for i,val in enumerate(y3): f[f"c3_{i}"]=val
            f["c3_max"]=y3.max();f["c3_min"]=y3.min();f["c3_mean"]=y3.mean();f["side_on"]=float(abs(ub[2]))
    return f
rows=[]
for k,(ts,X) in P2.items():
    v=lab[k]
    if v["stroke"] not in("forehand","backhand") or v.get("contact_in_frames")=="no" or v.get("hit_above_head")=="yes": continue
    hv=VH.get(k.split("/")[0]+"/"+k.split("/")[1]) or {"player_right":"r","player_left":"l"}.get(v.get("hand_vis"))
    if hv is None: continue
    f=feats(k,v,hv)
    if f: rows.append((k.split("/")[1],int(v["stroke"]=="backhand"),f,v.get("confidence",2)))
names=sorted({n for r in rows for n in r[2]});print("windows",len(rows),"backhand",sum(r[1] for r in rows))
def run(rs,label,names,model):
    X=np.array([[r[2].get(n,np.nan) for n in names] for r in rs],float);y=np.array([r[1] for r in rs]);g=np.array([r[0] for r in rs]);p=np.zeros(len(y))
    for tr,te in GroupKFold(5).split(X,y,g):
        if model=="gb": m=HistGradientBoostingClassifier(max_iter=150,learning_rate=0.05,max_leaf_nodes=6,l2_regularization=2.0,class_weight="balanced",random_state=0)
        else: 
            Xt=np.nan_to_num(X[tr],nan=0.0);m=make_pipeline(StandardScaler(),LogisticRegression(C=0.3,class_weight="balanced",max_iter=2000))
        if model=="gb": m.fit(X[tr],y[tr]);p[te]=m.predict_proba(X[te])[:,1]
        else: m.fit(np.nan_to_num(X[tr]),y[tr]);p[te]=m.predict_proba(np.nan_to_num(X[te]))[:,1]
    pred=p>0.5;print(f"[{label}] n={len(y)} bh={y.sum()} AUC {roc_auc_score(y,p):.3f} | forehand recall {np.mean(~pred[y==0]):.2f}, backhand recall {np.mean(pred[y==1]):.2f}")
c2=[n for n in names if n.startswith("c2_")]+["view_w"];c3=[n for n in names if n.startswith("c3_")]+["side_on"]
for model in("lr","gb"):
    run(rows,f"{model} 2D take-back",c2,model);run(rows,f"{model} depth take-back",c3,model);run(rows,f"{model} both",c2+c3,model)
wide=[r for r in rows if r[2]["view_w"]>0.45];nar=[r for r in rows if r[2]["view_w"]<=0.45]
run(wide,"lr both, front/back views",c2+c3,"lr");run(nar,"lr both, side-on views",c2+c3,"lr");run([r for r in rows if r[3]>=2],"lr both, confidence>=2",c2+c3,"lr")
