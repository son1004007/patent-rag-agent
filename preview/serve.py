"""Static preview only. No API, no uploads, no logs of queries."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parent
ASSETS = {"/":("index.html","text/html; charset=utf-8"),"/index.html":("index.html","text/html; charset=utf-8"),"/style.css":("style.css","text/css; charset=utf-8"),"/app.js":("app.js","application/javascript; charset=utf-8")}
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=urlsplit(self.path).path
        item=ASSETS.get(path)
        if not item:
            self.send_error(404); return
        file,ctype=item
        data=(ROOT/file).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type",ctype)
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("X-Frame-Options","DENY")
        self.send_header("Referrer-Policy","no-referrer")
        self.send_header("Content-Security-Policy","default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; form-action 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(data)
    def log_message(self, format, *args): pass
if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1",18765),Handler).serve_forever()
