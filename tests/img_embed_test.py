import pickle,json,numpy as np,collections
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA
from sklearn.model_selection import GroupKFold
E_=pickle.load(open("work/img_embed.pkl","rb"));lab=json.load(open("work/stroke_labels3.json"))
rows=[]
for k,E in E_.items():
    v=lab[k];s="no_stroke" if v["stroke"]=="none" else v["stroke"]
    if s in("forehand","backhand") and (v.get("contact_in_frames")=="no" or v.get("hit_above_head")=="yes"): continue
    if s=="serve" and v.get("ball_toss_seen")=="no" and v.get("hit_above_head")=="no": continue
    ok=[e for e in E if e is not None]
    if len(ok)<2: continue
    m=np.mean(ok,0);X=np.concatenate([e if e is not None else m for e in E])
    rows.append((k.split("/")[1],s,X,v["confidence"]))
print("windows",len(rows),collections.Counter(r[1] for r in rows))
def run(rs,label,classes=None):
    y=np.array([r[1] for r in rs]);g=np.array([r[0] for r in rs]);X=np.stack([r[2] for r in rs]);cls=sorted(set(y));pred=np.empty(len(y),object)
    for tr,te in GroupKFold(5).split(X,y,g):
        m=make_pipeline(StandardScaler(),PCA(128,random_state=0),LogisticRegression(C=0.05,max_iter=2000,class_weight="balanced")).fit(X[tr],y[tr]);pred[te]=m.predict(X[te])
    print(f"\n[{label}] n={len(y)} accuracy {np.mean(pred==y):.3f} recall",{c:round(float(np.mean(pred[y==c]==c)),2) for c in cls})
    for c in cls: print("   %-10s"%c,[int(((y==c)&(pred==d)).sum()) for d in cls])
    return pred,y
run(rows,"images: forehand/backhand/serve/no_stroke")
run([r for r in rows if r[3]>=2],"images, confidence>=2 labels")
fb=[r for r in rows if r[1] in("forehand","backhand")]
p,y=run(fb,"images: forehand vs backhand only (the hard pair)")
print("  majority baseline",round(max(np.mean(y=='forehand'),np.mean(y=='backhand')),3),"| balanced accuracy",round((np.mean(p[y=='forehand']=='forehand')+np.mean(p[y=='backhand']=='backhand'))/2,3))
