"""Local tagging page. python tests/humantest_serve.py  then open http://localhost:8765  (Ctrl-C to stop; tags autosave)."""
import http.server, json, os
D = os.path.abspath(os.environ.get("HT_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "humantest"))
os.chdir(D)
class H(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); data = self.rfile.read(n)
        json.loads(data); open("tags.json", "wb").write(data)
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass
print("open http://localhost:8765"); http.server.ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
