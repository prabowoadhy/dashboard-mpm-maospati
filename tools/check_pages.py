"""check_pages.py - verifikasi statis: setiap id yang dipakai skrip halaman harus ada di HTML-nya."""
import re, os, json, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = [os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(ROOT, "*.html"))]
ok = True

for slug in sorted(pages):
    html = open(os.path.join(ROOT, slug + ".html"), encoding="utf-8").read()
    ids_html = set(re.findall(r'id="([^"]+)"', html))
    missing_scripts, missing_ids, errs = [], [], []

    js_path = os.path.join(ROOT, "assets", "pages", slug + ".js")
    if slug != "index" and not os.path.exists(js_path):
        missing_scripts.append(slug + ".js")
    src = open(js_path, encoding="utf-8").read() if os.path.exists(js_path) else ""
    # periksa id yang dipakai set()/el()
    used = set(re.findall(r"\bset\(\s*'([^']+)'", src)) | set(re.findall(r"\bel\(\s*'([^']+)'", src))
    for u in sorted(used):
        if u not in ids_html:
            missing_ids.append(u)
    # kurung kurawal seimbang (deteksi cepat file terpotong)
    if src.count("{") != src.count("}"):
        errs.append(f"kurawal tidak seimbang ({src.count('{')} vs {src.count('}')})")
    if src.count("(") != src.count(")"):
        errs.append(f"tanda kurung tidak seimbang ({src.count('(')} vs {src.count(')')})")

    status = "OK " if not (missing_ids or missing_scripts or errs) else "!! "
    if missing_ids or missing_scripts or errs: ok = False
    print(f"{status}{slug:<26} elemen_id={len(ids_html):>3} dipakai_js={len(used):>3}"
          + (f" | skrip hilang: {missing_scripts}" if missing_scripts else "")
          + (f" | id tak ada di HTML: {missing_ids}" if missing_ids else "")
          + (f" | {errs}" if errs else ""))

print("\n--- berkas data ---")
for p in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
    try:
        d = json.load(open(p, encoding="utf-8"))
        keys = ", ".join(list(d.keys())[:7])
        print(f"  OK {os.path.basename(p):<32} {os.path.getsize(p):>7} B  keys: {keys}")
    except Exception as e:
        ok = False
        print(f"  !! {os.path.basename(p)}: {e}")

print("\n--- berkas wajib ---")
for f in ["index.html", "assets/style.css", "assets/app.js", "tools/sync.py", "tools/build_pages.py",
          "tools/serve.py", ".github/workflows/sync.yml", "README.md"]:
    exists = os.path.exists(os.path.join(ROOT, f))
    ok = ok and exists
    print(("  OK " if exists else "  !! HILANG ") + f)

print("\nHASIL:", "SEMUA TERPERIKSA" if ok else "ADA MASALAH")
sys.exit(0 if ok else 1)
