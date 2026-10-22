"""
serve.py - menjalankan dashboard di komputer sendiri + tombol "Sinkron" di header.

    python tools/serve.py            # http://127.0.0.1:8080
    python tools/serve.py 9000

Endpoint yang disediakan (dipakai tombol Sinkron pada halaman):
    POST /api/sync   -> menjalankan tools/sync.py lalu tools/build_pages.py
    GET  /api/sync   -> status terakhir: {state: running|done|error|idle, detail, mulai, selesai}

Halaman membaca data/<menu>.json lewat fetch(), jadi harus dibuka lewat alamat http://
(bukan klik dua kali berkas HTML). Versi cadangan tertanam tetap membuat halaman tampil
walau fetch diblokir, hanya saja tombol Sinkron ikut nonaktif.
"""
import http.server, socketserver, subprocess, sys, os, json, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
os.chdir(ROOT)

_status = {"state": "idle", "detail": "belum pernah dijalankan", "mulai": None, "selesai": None}
_lock = threading.Lock()


def jalankan_sinkron():
    with _lock:
        if _status["state"] == "running":
            return False
        _status.update({"state": "running", "detail": "menjalankan tools/sync.py",
                        "mulai": time.strftime("%H:%M:%S"), "selesai": None})

    def jalan():
        log = []
        for skrip, ket in (("tools/sync.py", "menarik data dari Drive"),
                           ("tools/build_pages.py", "merakit halaman HTML")):
            _status["detail"] = f"{ket} ({skrip})"
            p = subprocess.run([sys.executable, skrip], cwd=ROOT, capture_output=True, text=True)
            log.append((p.stdout or "") + (p.stderr or ""))
            if p.returncode != 0:
                with _lock:
                    _status.update({"state": "error", "selesai": time.strftime("%H:%M:%S"),
                                    "detail": (log[-1].strip().splitlines() or ["gagal"])[-1][:300]})
                print("[sinkron] GAGAL:", _status["detail"])
                return
        with _lock:
            jumlah = len([f for f in os.listdir(os.path.join(ROOT, "data")) if f.endswith(".json")])
            _status.update({"state": "done", "selesai": time.strftime("%H:%M:%S"),
                            "detail": f"{jumlah} berkas data diperbarui"})
        print("[sinkron] selesai:", _status["detail"])

    threading.Thread(target=jalan, daemon=True).start()
    return True


class Handler(http.server.SimpleHTTPRequestHandler):
    def _kirim_json(self, obj, kode=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(kode)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/sync"):
            self._kirim_json(_status)
            return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/sync"):
            mulai = jalankan_sinkron()
            self._kirim_json({"ok": True, "dijalankan": mulai, **_status},
                             kode=200 if mulai else 409)
            return
        self.send_error(404, "Hanya /api/sync yang tersedia")

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format, *args):
        print("  " + format % args)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


with Server(("127.0.0.1", PORT), Handler) as httpd:
    url = f"http://127.0.0.1:{PORT}/index.html"
    print(f"Dashboard MPM jalan di {url}  (Ctrl+C untuk berhenti)")
    print("Tombol 'Sinkron sekarang' di header akan menjalankan tools/sync.py + tools/build_pages.py.")
    if not os.environ.get("MPM_NO_BROWSER"):
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass
    httpd.serve_forever()
