"""
serve.py — menjalankan dashboard di komputer sendiri (untuk pratinjau lokal).

    python tools/serve.py            # http://127.0.0.1:8080
    python tools/serve.py 9000

Penting: halaman membaca data/<menu>.json lewat fetch(), jadi harus dibuka
melalui alamat http:// (bukan klik dua kali berkas HTML) supaya browser
mengizinkan pembacaan berkas JSON.
"""
import http.server, socketserver, os, sys, webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
os.chdir(ROOT)

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def log_message(self, format, *args):
        print("  " + format % args)

with socketserver.TCPServer(("127.0.0.1", PORT), H) as httpd:
    url = f"http://127.0.0.1:{PORT}/index.html"
    print(f"Dashboard MPM jalan di {url}  (Ctrl+C untuk berhenti)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    httpd.serve_forever()
