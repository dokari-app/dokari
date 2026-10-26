import json,sys,numpy as np,collections,os
sys.path.insert(0,".")
from scipy.ndimage import gaussian_filter1d
from sphere.skeleton import J
lab=json.load(open("work/stroke_labels2.json"));cache={};rows=[]
for k,v in lab.items():
    if v.get("stroke") not in("forehand","backhand") or v.get("hit_above_head")=="yes" or v.get("contact_in_frames")!="yes" or v["confidence"]<2: continue
    act,vid=k.split("/")[:2];f=f"work/{act}/clips/{vid}.npz"
    if not os.path.exists(f): continue
    if f not in cache:
        d=np.load(f,allow_pickle=True);cache[f]=(gaussian_filter1d(d["pose"],1.5,axis=0,mode="nearest"),float(d["fps"]))
    P,fps=cache[f];pk=int(round(v["peak"]*fps));a=pk-int(1.0*fps);b=pk+int(.2*fps)
    if a<0 or b>=len(P): continue
    sp={s:np.linalg.norm(np.gradient(P[:,J[f"{s}_wrist"]],axis=0),axis=1)[pk-int(.3*fps):pk+int(.3*fps)+1] for s in "lr"}
    s="r" if sp["r"].max()>=sp["l"].max() else "l";o="l" if s=="r" else "r"
    own,opp=P[:,J[f"{s}_shoulder"]],P[:,J[f"{o}_shoulder"]]
    # body frame from hips+shoulders (facing direction = perpendicular to shoulder line, flipped toward where hips/knees face is unknown) -> use only lateral axis u = own->opp shoulder horizontal at each frame
    u=opp-own;u[:,1]=0;w=np.linalg.norm(u,axis=1,keepdims=True)+1e-6;u=u/w
    # use FIXED axis from the shoulder line at window start-to-peak mean to avoid trunk-rotation circularity
    ub=u[a:pk].mean(0);ub/=np.linalg.norm(ub)+1e-9
    W=P[:,J[f"{s}_wrist"]];ms=(own+opp)/2;sw=w[a:pk].mean()
    cr=((W-ms)*ub).sum(1)/sw
    # shoulder rotation: angle of shoulder line change over window (yaw), sign relative to own->opp
    yaw=np.unwrap(np.arctan2(u[:,2],u[:,0]))
    seg=cr[a:b+1]
    dy=np.abs(np.diff(np.unwrap(np.arctan2(u[a:b+1,2],u[a:b+1,0]))));wd=np.abs(np.diff(np.arctan2(u[a:b+1,2],u[a:b+1,0])));wd=np.minimum(wd,2*np.pi-wd)
    ux=float(np.median(np.abs(u[a:pk,0])));sx=np.sign(np.median(u[a:pk,0]))
    cx=((W-ms)[:,0]*sx)/sw
    flip=bool((np.abs(np.diff(np.arctan2(u[a:b+1,2],u[a:b+1,0])))>2.0).any())
    rows.append(dict(y=int(v["stroke"]=="backhand"),cmax=float(seg.max()),cmin=float(seg.min()),crange=float(seg.max()-seg.min()),cpk=float(cr[pk]),dlat=float(cr[pk]-cr[a:pk].mean()),
       argmax=float((np.argmax(seg)-(pk-a))/fps),yawd=float(abs(yaw[pk]-yaw[a])),grip=v.get("grip"),vid=vid,flip=flip,ux=ux,cxpk=float(cx[pk]),cxmax=float(cx[a:b+1].max()),cxmin=float(cx[a:b+1].min())))
def auc(p,n):
    p,n=np.array(p),np.array(n);return float(((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean()))
for nm,R in [("all",rows),("1H",[r for r in rows if r["grip"]=="one_handed"]),("2H",[r for r in rows if r["grip"]=="two_handed"])]:
    y=np.array([r["y"] for r in R]);print(nm,len(R),int(y.sum()))
    for key in("cmax","cmin","cpk","dlat","crange","argmax","yawd"):
        c=np.array([r[key] for r in R]);print("  ",key,round(auc(c[y==1],c[y==0]),3))
print("---- flip check")

print("windows with a shoulder-line flip:",sum(r['flip'] for r in rows),"of",len(rows))
for nm,R in [("noflip all",[r for r in rows if not r['flip']]),("noflip 1H",[r for r in rows if not r['flip'] and r['grip']=='one_handed'])]:
    y=np.array([r['y'] for r in R]);print(nm,len(R),int(y.sum()))
    for key in('cmax','cmin','cpk','dlat'):
        c=np.array([r[key] for r in R]);print('  ',key,round(auc(c[y==1],c[y==0]),3))

print('---- view-split (ux = |shoulder line along image x|)')
for lo,hi in [(0,.5),(.5,.8),(.8,1.01)]:
    for g in ('one_handed',None):
        R=[r for r in rows if not r['flip'] and lo<=r['ux']<hi and (g is None or r['grip']==g)]
        y=np.array([r['y'] for r in R])
        if y.sum()<5 or (1-y).sum()<5: print(lo,hi,g,len(R),'few');continue
        print(lo,hi,g,len(R),int(y.sum()),{k:round(auc(np.array([r[k] for r in R])[y==1],np.array([r[k] for r in R])[y==0]),3) for k in('cxpk','cxmax','cxmin')})
