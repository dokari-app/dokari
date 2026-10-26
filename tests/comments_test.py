"""python tests/comments_test.py [URL]: fetches the comments of one video and prints how many came back, or the reason they did not."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere import comments
url = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=b6nD-NdKhPU"
cs = comments.fetch(url, 20)
print(len(cs), "comments")
for c in cs[:5]: print(" -", c["likes"], c["t"], c["text"][:100])
if not cs: print("reason:", comments.LAST_ERROR[0] or "none reported (the video may have comments turned off)")
