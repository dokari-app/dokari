import json,sys,numpy as np,collections,os
sys.path.insert(0,".")
from scipy.ndimage import gaussian_filter1d
from sphere.skeleton import J
d=json.load(open("work/stroke_contact_pilot.json"));lab=json.load(open("work/stroke_labels2.json"))
print("n",len(d));print("contact_frame",sorted(collections.Counter(v["contact_frame"] for v in d.values()).items()))
print("old label -> new stroke",collections.Counter((lab[k]["stroke"],v["stroke"]) for k,v in d.items()))
print("side/hand/stroke",collections.Counter((v["stroke"],v["swinging_hand"],v["racket_side_at_contact"]) for v in d.values()).most_common(12))
def auc(p,n):
    p,n=np.array(p),np.array(n);return float(((p[:,None]>n[None,:]).mean()+.5*(p[:,None]==n[None,:]).mean())) if len(p) and len(n) else float("nan")
cache={};rows=[]
for k,v in d.items():
    if v["contact_frame"]==0 or v["stroke"] not in("forehand","backhand"): continue
    act,vid=k.split("/")[:2];f=f"work/{act}/clips/{vid}.npz"
    if f not in cache:
        z=np.load(f,allow_pickle=True);cache[f]=(gaussian_filter1d(z["pose"],1.5,axis=0,mode="nearest"),float(z["fps"]))
    P,fps=cache[f];w0,w1=lab[k]["window"];tc=w0+(w1-w0)*((v["contact_frame"]-1)/7)
    c0=int(tc*fps);a,b=max(0,c0-int(.4*fps)),min(len(P)-1,c0+int(.4*fps))
    sp={s:np.linalg.norm(np.gradient(P[:,J[f"{s}_wrist"]],axis=0),axis=1) for s in "lr"}
    s="r" if sp["r"][a:b+1].max()>=sp["l"][a:b+1].max() else "l";o="l" if s=="r" else "r"
    i=a+int(np.argmax(sp[s][a:b+1]))
    own,opp=P[:,J[f"{s}_shoulder"]],P[:,J[f"{o}_shoulder"]];u=opp-own;u[:,1]=0;w=np.linalg.norm(u,axis=1,keepdims=True)+1e-6;u=u/w
    cr=((P[:,J[f"{s}_wrist"]]-(own+opp)/2)*u).sum(1)/w[:,0]
    sv={'player_right':'r','player_left':'l'}.get(v['swinging_hand'])
    if sv:
        ov='l' if sv=='r' else 'r';ow,op=P[:,J[f'{sv}_shoulder']],P[:,J[f'{ov}_shoulder']];uu=op-ow;uu[:,1]=0;ww=np.linalg.norm(uu,axis=1,keepdims=True)+1e-6;uu=uu/ww
        crv=((P[:,J[f'{sv}_wrist']]-(ow+op)/2)*uu).sum(1)/ww[:,0];j=a+int(np.argmax(sp[sv][a:b+1]));cv=float(crv[j]);cvm=float(crv[max(a,j-2):j+3].mean());cvx=float(crv[a:b+1].max())
    else: cv=cvm=cvx=None
    rows.append(dict(cv=cv,cvm=cvm,cvx=cvx,y_new=int(v["stroke"]=="backhand"),y_old=int(lab[k]["stroke"]=="backhand"),c=float(cr[i]),cmean=float(cr[max(a,i-2):i+3].mean()),conf=v["confidence"],
        skel_hand=s,vis_hand={"player_right":"r","player_left":"l"}.get(v["swinging_hand"]),two=v["other_hand_on_racket"],dt=(i-c0)/fps))
print("usable",len(rows),"| offset of skeleton peak from vision contact (s): median",round(float(np.median([r["dt"] for r in rows])),2),"abs median",round(float(np.median(np.abs([r["dt"] for r in rows]))),2))
hh=[(r["skel_hand"],r["vis_hand"]) for r in rows if r["vis_hand"]];print("skeleton faster wrist == vision racket hand:",sum(a==b for a,b in hh),"of",len(hh))
for nm,sel in [("all",rows),("conf>=2",[r for r in rows if r["conf"]>=2]),("one hand",[r for r in rows if r["two"]=="no"]),("two hands",[r for r in rows if r["two"]=="yes"])]:
    for yk in("y_new","y_old"):
        y=np.array([r[yk] for r in sel])
        if y.sum()<3 or (1-y).sum()<3: print(nm,yk,"few",len(sel),int(y.sum()));continue
        c=np.array([r["c"] for r in sel]);cm=np.array([r["cmean"] for r in sel])
        print(nm,yk,"n",len(sel),"bh",int(y.sum()),"AUC c",round(auc(c[y==1],c[y==0]),3),"cmean",round(auc(cm[y==1],cm[y==0]),3),"median fh/bh",round(float(np.median(c[y==0])),2),round(float(np.median(c[y==1])),2))

print('--- with the racket hand taken from the frames (not guessed from the skeleton)')
for nm,sel in [('all',rows),('one hand',[r for r in rows if r['two']=='no'])]:
    sel=[r for r in sel if r['cv'] is not None];y=np.array([r['y_new'] for r in sel])
    for key in('cv','cvm','cvx'):
        c=np.array([r[key] for r in sel]);print(nm,key,'n',len(sel),'bh',int(y.sum()),'AUC',round(auc(c[y==1],c[y==0]),3),'median fh/bh',round(float(np.median(c[y==0])),2),round(float(np.median(c[y==1])),2))
