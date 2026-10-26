import json,collections
old=json.load(open("work/stroke_labels2.json"));new=json.load(open("work/stroke_contact_all.json"))
print("relabelled",len(new))
print("old -> new",sorted(collections.Counter((old[k]["stroke"],v["stroke"]) for k,v in new.items() if k in old).items(),key=lambda x:-x[1])[:16])
out={}
for k,v in old.items():
    if k in new:
        n=new[k];v=dict(v);v["stroke_old"]=v["stroke"]
        if v["stroke"] not in ("smash","slice","lob","drop_shot"): v["stroke"]=n["stroke"]   # the new prompt had no smash/slice/lob option: keep those old labels
        v["confidence"]=n["confidence"]
        v["contact_in_frames"]="yes" if n["contact_frame"]>0 else "no"
        if n["stroke"]=="none": v["shown"]="not_a_stroke"
        v["contact_frame"]=n["contact_frame"];v["hand_vis"]=n["swinging_hand"];v["side_vis"]=n["racket_side_at_contact"]
    out[k]=v
json.dump(out,open("work/stroke_labels3.json","w"))
print(collections.Counter(v["stroke"] for v in out.values()))
