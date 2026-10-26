import sys, pickle; sys.path.insert(0, "tests"); sys.path.insert(0, ".")
import ball_night as bn
bn.ROOT = "work/ball_night"
s = bn.state(); parts = bn.base_parts(); lp = bn.lab_parts(s["accepted"])
clf = bn.fit((parts[0] + lp[0], parts[1] + lp[1], parts[2] + lp[2]))
pickle.dump(clf, open("work/ball_night/clf.pkl", "wb")); print("saved")
