"""
sync.py - mesin data Dashboard MPM.

Membaca 8 folder Google Drive "MPM Maospati" (lewat endpoint publik embeddedfolderview),
mengunduh & menganalisis berkas .xlsx di dalamnya, lalu menulis SATU berkas JSON per halaman:

    data/site.json                     -> daftar 8 menu + ringkasan jumlah berkas
    data/smd-mmd.json                  -> halaman SMD MMD
    data/laporan-posyandu.json
    data/ruk.json
    data/dokumentasi.json
    data/data-posyandu.json
    data/data-kader.json
    data/spj-bok.json
    data/laporan-kegiatan-dinkes.json

Cara pakai (dari root repo):
    pip install openpyxl
    python tools/sync.py                # baca ulang semua folder
    python tools/sync.py --only smd-mmd # hanya satu halaman
    python tools/sync.py --offline      # pakai cache .cache/ tanpa akses Drive

Syarat: folder & berkas di Drive dibagikan "Anyone with the link -> Viewer".
Kalau ada folder/berkas baru di Drive, cukup jalankan ulang skrip ini
(atau biarkan GitHub Actions menjalankannya otomatis - lihat .github/workflows/sync.yml).
"""
import urllib.request, re, json, time, os, sys, glob, argparse
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache")
DL = os.path.join(CACHE, "dl")
DATA = os.path.join(ROOT, "data")
REFRESH = False   # diisi dari argumen --refresh
os.makedirs(DL, exist_ok=True); os.makedirs(DATA, exist_ok=True)

# ============================ daftar 8 menu ============================
FOLDERS = [
    ("smd-mmd",                "SMD MMD",                 "1GvbF6KR_MXwwyOlLInTzMxTab3rYw7Fz",
     "Survey Mawas Diri & Musyawarah Masyarakat Desa", "Data SMD/MMD, analisa hasil & rekap per desa"),
    ("laporan-posyandu",       "Laporan Posyandu",        "1HYFFzGGYg9UUjoV5UsjfuDG9WmXJMrqS",
     "Laporan bulanan LHK posyandu", "Kelengkapan laporan LHK per bulan"),
    ("ruk",                    "RUK",                     "1rDLnBMxf71TeG85YO74wCrfsKjjOL4Qv",
     "Rencana Usulan Kegiatan", "Usulan kegiatan & kebutuhan anggaran tahunan"),
    ("dokumentasi",            "Dokumentasi",             "1AfusP3TNvnC54SPrRWWxI6twW6G8ASWF",
     "Dokumentasi kegiatan", "Foto & berkas dokumentasi kegiatan"),
    ("data-posyandu",          "Data Posyandu",           "19dczLeNHcb20b9r-fVi1QP5ohF7oqQim",
     "Data posyandu & laporan LHK", "Daftar posyandu ILP beserta statusnya"),
    ("data-kader",             "Data Kader",              "1ANnRWgVu15SUEsVssE5afvYzzHpgKLgl",
     "Data kader posyandu", "Rekap jumlah kader per posyandu"),
    ("spj-bok",                "SPJ BOK",                 "1YmIQquag2Qxr3jv3pFzBHjcCd8YB9mE9",
     "SPJ Bantuan Operasional Kesehatan", "Berkas pertanggungjawaban BOK"),
    ("laporan-kegiatan-dinkes","Laporan Kegiatan Dinkes", "1RTT0Ey5NanOQfGYj2v7yAZf0UrTtGlkw",
     "Kegiatan dari Dinas Kesehatan", "Kegiatan DINKES & administrasi kader buaian"),
]
SLUGS = [f[0] for f in FOLDERS]
DRIVE = "https://drive.google.com/drive/folders/"

# ============================ menu tambahan: kalender Promkes ============================
# Jadwal Promkes tidak memakai folder Drive, tetapi kalender publik Google.
# ICS publik dibaca sebagai data (agenda mendatang), embed dipakai untuk tampilan kalender.
CALENDAR = {
    "slug": "jadwal-promkes",
    "menu": "Jadwal Promkes",
    "subjudul": "Jadwal kegiatan promosi kesehatan (kalender publik)",
    "deskripsi": "Kalender kegiatan Promkes - agenda SMD/MMD, posyandu, dan penyuluhan",
    "src": "dhellayaamanda2@gmail.com",
    "embed": ("https://calendar.google.com/calendar/embed?src=dhellayaamanda2%40gmail.com"
              "&ctz=Asia%2FJakarta&hl=id&mode=MONTH&showTitle=0&showPrint=0&showTz=0&showCalendars=0&showTabs=1"),
    "ics": "https://calendar.google.com/calendar/ical/dhellayaamanda2%40gmail.com/public/basic.ics",
}
BULAN_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# ============================ crawl folder ============================
def folder_items(fid, offline=False):
    p = os.path.join(CACHE, "folder_" + fid + ".html")
    if offline and os.path.exists(p):
        html = open(p, encoding="utf-8").read()
    elif os.path.exists(p) and offline:
        html = open(p, encoding="utf-8").read()
    else:
        try:
            req = urllib.request.Request(f"https://drive.google.com/embeddedfolderview?id={fid}&list",
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                html = r.read().decode("utf-8", "replace")
            open(p, "w", encoding="utf-8").write(html)
            time.sleep(0.25)
        except Exception as e:
            if os.path.exists(p):
                html = open(p, encoding="utf-8").read()
            else:
                raise
    title = re.search(r"<title>(.*?)</title>", html)
    items = []
    for chunk in html.split('<div class="flip-entry" id="entry-')[1:]:
        eid = chunk.split('"', 1)[0]
        t = re.search(r'<div class="flip-entry-title">(.*?)</div>', chunk, re.S)
        l = re.search(r'<a href="https://drive\.google\.com/(drive/folders|file/d)/', chunk)
        m = re.search(r'<div class="flip-entry-last-modified"><div>(.*?)</div>', chunk)
        if not t: continue
        items.append({"id": eid, "name": t.group(1).strip(),
                      "kind": "folder" if (l and l.group(1) == "drive/folders") else "file",
                      "modified": (m.group(1).strip() if m else ""),
                      "url": f"https://drive.google.com/drive/folders/{eid}" if (l and l.group(1) == "drive/folders")
                             else f"https://drive.google.com/file/d/{eid}/view"})
    return (title.group(1) if title else fid), items

def crawl(fid, offline=False, depth=0, maxdepth=4):
    name, items = folder_items(fid, offline)
    node = {"id": fid, "name": name, "url": DRIVE + fid, "items": items, "children": []}
    if depth < maxdepth:
        for it in items:
            if it["kind"] == "folder":
                node["children"].append(crawl(it["id"], offline, depth + 1, maxdepth))
    return node

def flatten_files(node, path=""):
    out = []
    for i in node["items"]:
        if i["kind"] == "file":
            out.append({**i, "path": (path or node["name"])})
    for c in node["children"]:
        out += flatten_files(c, path + "/" + c["name"] if path else c["name"])
    return out

def count_tree(node):
    files = len([i for i in node["items"] if i["kind"] == "file"])
    subs = len(node["children"])
    for c in node["children"]:
        f, s = count_tree(c); files += f; subs += s
    return files, subs

def outline(node, depth=1):
    """struktur folder ringkas untuk ditampilkan di halaman."""
    o = {"name": node["name"], "id": node["id"], "url": node["url"],
         "files": [i for i in node["items"] if i["kind"] == "file"], "children": []}
    for c in node["children"]:
        o["children"].append(outline(c, depth + 1))
    return o

# ============================ unduh & helper xlsx ============================
def dl(fid, name):
    p = os.path.join(DL, re.sub(r"[^A-Za-z0-9._-]", "_", fid + "_" + name))
    if not REFRESH and os.path.exists(p) and os.path.getsize(p) > 2000:
        return p
    req = urllib.request.Request(f"https://drive.google.com/uc?export=download&id={fid}",
                                headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    open(p, "wb").write(data); time.sleep(0.25); return p

def pad(r, n):
    out = [("" if x is None else str(x).strip()) for x in list(r)[:n]]
    return out + [""] * (n - len(out))

NUM_ROW = re.compile(r"^\d+(\.0+)?\.?$")
def tonum(v):
    if v is None: return None
    if isinstance(v, (int, float)): return int(v)
    s = str(v).strip()
    if not s or s.upper() in ("V", "-"): return None
    if re.match(r"^\d+([.,]0+)?$", s): return int(float(s.replace(",", ".")))
    m = re.search(r"(\d[\d.,]*)", s)
    if not m: return None
    try: return int(float(m.group(1).replace(".", "").replace(",", ".")))
    except ValueError: return None

def norm(s): return re.sub(r"\s+", " ", str(s)).strip().upper()
def title(s): return re.sub(r"\s+", " ", str(s)).strip().title()
def cap(s): return re.sub(r"\s+", " ", str(s)).strip()

def load_book(fid, name):
    import openpyxl
    return openpyxl.load_workbook(dl(fid, name), read_only=True, data_only=True)

BULAN = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

def stempel(dt):
    return f"{dt.day} {BULAN[dt.month - 1]} {dt.year} {dt:%H:%M} WIB"

def write(slug, payload):
    payload["generated"] = stempel(datetime.now(timezone(timedelta(hours=7))))
    json.dump(payload, open(os.path.join(DATA, slug + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"  -> data/{slug}.json")

# ============================ analisa per halaman ============================
def analisa_smd(root, files):
    """SMD MMD: rekap per desa-tahun + kelengkapan + kebutuhan/harapan."""
    rekap_files = [f for f in files if f["name"].lower().endswith(".xlsx") and
                   ("rekap" in f["name"].lower() or "smd" in f["name"].lower()) and "kelengkapan" not in f["name"].lower()]
    ind_texts, ind_idx, seen = [], {}, set()
    smd = []
    def parse(path, tahun):
        wb = __import__("openpyxl").load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            rows = [pad(r, 9) for r in ws.iter_rows(values_only=True)]
            rec = {"desa": title(ws.title), "tahun": tahun, "responden": None, "ind": [], "kebutuhan": []}
            for r in rows[:12]:
                j = " ".join(x for x in r if x)
                m = re.search(r"Jumlah Responden.*?(\d+)\s*KK", j)
                if m and rec["responden"] is None: rec["responden"] = int(m.group(1))
                d = re.search(r"(?:DESA|KELURAHAN)\s+([A-Z]{3,}[A-Z ]*)", j)
                if d: rec["desa"] = title(d.group(1))
            cur_k = None; cur_ind = None; in_keb = False
            for r in rows:
                s0, s1 = r[0], r[1]
                if re.match(r"^KLASTER\s*\d", s0, re.I):
                    cur_k = s0.upper(); cur_ind = None; continue
                if re.match(r"^Kebutuhan dan Harapan", s0, re.I) or re.match(r"^Kebutuhan dan Harapan", s1, re.I):
                    in_keb = True; continue
                if in_keb:
                    t = " ".join(x for x in (s0, s1) if x)
                    if t: rec["kebutuhan"].append(t)
                    continue
                if re.match(r"^\d+\.?$", s0) and s1:
                    k = norm(s1)
                    if k not in ind_idx: ind_idx[k] = len(ind_texts); ind_texts.append(k)
                    cur_ind = k
                    rec["ind"].append([ind_idx[k], tonum(r[2]), tonum(r[3]), cur_k or "UMUM"])
                elif s0 == "" and s1 and cur_ind is not None and re.match(r"^[a-z]\.", s1):
                    k = norm(s1)
                    if k not in ind_idx: ind_idx[k] = len(ind_texts); ind_texts.append(k)
                    rec["ind"].append([ind_idx[k], tonum(r[2]), None, cur_k or "UMUM"])
            if rec["ind"]:
                key = (norm(rec["desa"]), rec["tahun"])
                if key not in seen:
                    seen.add(key); rec["src"] = f"/".join([f["path"], f["name"]]); smd.append(rec)
        wb.close()
    for f in rekap_files:
        m = re.search(r"(20\d\d)", f["name"])
        try:
            parse(dl(f["id"], f["name"]), int(m.group(1)) if m else None)
        except Exception as e:
            print("    ! gagal baca", f["name"], e)

    # kelengkapan SMD
    kel = []
    kel_file = next((f for f in files if f["name"].lower().startswith("kelengkapan")), None)
    if kel_file:
        wb = load_book(kel_file["id"], kel_file["name"])
        ws = wb["Sheet1"]; cur = None
        for r in ws.iter_rows(values_only=True):
            c = pad(r, 7)
            y = tonum(c[1])
            if y and 2000 < y < 2100: cur = y
            if c[2] and cur and c[2].upper() != "DESA/KELURAHAN":
                kel.append({"tahun": cur, "desa": title(c[2]), "rekap": c[3].upper() == "V", "analisa": c[5].upper() == "V"})
        wb.close()

    desa = sorted({r["desa"] for r in smd})
    tahun = sorted({r["tahun"] for r in smd if r["tahun"]})
    tot = sum(r["responden"] or 0 for r in smd)
    keb_agg = {}
    for r in smd:
        for s in r["kebutuhan"]:
            m = re.match(r"^\s*(\d+)\s*ORANG\s*(.*)$", s, re.I)
            n = int(m.group(1)) if m else 1
            teks = cap(m.group(2)) if m else cap(s)
            key = re.sub(r"[^A-Z ]", "", teks.upper()).strip()
            if len(key) < 6: continue
            e = keb_agg.setdefault(key, {"teks": title(teks), "jumlah": 0, "desa": set(), "tahun": set()})
            e["jumlah"] += n; e["desa"].add(r["desa"]); e["tahun"].add(r["tahun"])
    keb = sorted([{"teks": v["teks"], "jumlah": v["jumlah"], "desa": sorted(v["desa"]), "tahun": sorted(v["tahun"])}
                  for v in keb_agg.values()], key=lambda x: -x["jumlah"])[:20]

    # dokumen analisa (docx/pptx/pdf)
    docs = {}
    for f in files:
        if f["name"].lower().endswith((".docx", ".doc", ".pptx", ".pdf")):
            docs.setdefault(f["path"], []).append({"name": f["name"], "url": f["url"], "modified": f["modified"]})

    return {
        "kpi": {"desa": len(desa), "tahun": f"{tahun[0]}–{tahun[-1]}" if tahun else "–", "tahunList": tahun,
                "berkasRekap": len([f for f in files if f["name"].lower().endswith(".xlsx")]),
                "responden": tot, "indikator": len(ind_texts),
                "rekapSelesai": len([k for k in kel if k["rekap"]]), "analisaSelesai": len([k for k in kel if k["analisa"]]),
                "kelTotal": len(kel)},
        "desa": desa, "tahun": tahun, "indTexts": ind_texts, "rekap": smd,
        "kelengkapan": kel, "kebutuhan": keb, "dokumen": docs,
    }

def analisa_lhk(root, files):
    f = next((x for x in files if x["name"].lower().startswith("kelengkapan")), None)
    rows = []
    if f:
        wb = load_book(f["id"], f["name"])
        ws = wb["Sheet1"]; cur = None
        for r in ws.iter_rows(values_only=True):
            c = pad(r, 6)
            y = tonum(c[1])
            if y and 2000 < y < 2100: cur = y
            if c[2] and cur and c[2].upper() != "BULAN":
                rows.append({"tahun": cur, "bulan": title(c[2]), "ada": c[3].upper() == "V", "belum": c[4].upper() == "V"})
        wb.close()
    tahun = sorted({r["tahun"] for r in rows})
    latest = tahun[-1] if tahun else None
    return {"kpi": {"tahun": tahun, "terkumpul": len([r for r in rows if r["ada"]]), "total": len(rows),
                    "bulanIni": len([r for r in rows if r["tahun"] == latest and r["ada"]]),
                    "tahunTerakhir": latest},
            "lhk": rows, "bulan": BULAN}

def analisa_ruk(root, files):
    bab = next((f for f in files if f["name"].lower().startswith("copy of bab iv") or "perencanaan belanja" in f["name"].lower()), None)
    keg = []
    if bab:
        import openpyxl
        wb = openpyxl.load_workbook(dl(bab["id"], bab["name"]), read_only=True, data_only=True)
        ws = wb["BAB IV"]
        rows = [[("" if c is None else str(c).strip()) for c in list(r)[:14]] + [""] * 14 for r in ws.iter_rows(values_only=True)]
        wb.close()
        cur_k = ""
        # Struktur sheet BAB IV: kolom 2 = pelayanan/unit, 3 = kegiatan, 4 = tujuan,
        # 5 = sasaran, 6 = target, 7 = penanggung jawab (kolom 1 & sebagian 2 hasil merge sel).
        cur_p = ""
        HEADER_WORDS = {"NO", "PELAYANAN", "KEGIATAN", "TUJUAN", "SASARAN", "TARGET SASARAN",
                        "PENANGGUNG JAWAB", "KEBUTUHAN SUMBER DAYA", "MITRA KERJA", "MAN", "MATERIAL", "METODE"}
        for r in rows:
            if norm(r[2]) in HEADER_WORDS or norm(r[3]) in HEADER_WORDS:
                continue
            if r[2] and norm(r[2]) not in HEADER_WORDS:
                cur_p = r[2]
            if not r[3] or re.match(r"^\d+(\.\d+)?$", r[3]):
                continue
            keg.append({"kode": cur_k, "bagian": cap(cur_p), "kegiatan": cap(r[3]), "tujuan": cap(r[4]),
                        "sasaran": cap(r[5]), "target": cap(r[6]), "pj": cap(r[7])})
    bagian = {}
    for k in keg:
        if k["bagian"]: bagian[k["bagian"]] = bagian.get(k["bagian"], 0) + 1
    return {"kpi": {"kegiatan": len(keg), "bagian": len(bagian), "denganPJ": len([k for k in keg if k["pj"]]),
                    "sumber": bab["name"] if bab else "–"},
            "kegiatan": keg, "perBagian": [{"bagian": k, "jumlah": v} for k, v in sorted(bagian.items(), key=lambda x: -x[1])]}

def analisa_posyandu(root, files):
    f = next((x for x in files if "posyandu aktif" in x["name"].lower() or (x["name"].lower().endswith(".xlsx") and "posyandu" in x["name"].lower())), None)
    pos = []; cur = None
    if f:
        wb = load_book(f["id"], f["name"])
        ws = wb.worksheets[0]
        for r in ws.iter_rows(values_only=True):
            c = pad(r, 5)
            if NUM_ROW.match(c[0]) and c[1]: cur = title(c[1])
            if not c[2] or c[2].upper() in ("POS", "TOTAL"): continue
            pos.append({"desa": title(cur or ""), "pos": title(c[2]), "aktif": (tonum(c[3]) or 0) > 0})
        wb.close()
    per_desa = {}
    for p in pos: per_desa[p["desa"]] = per_desa.get(p["desa"], 0) + 1
    return {"kpi": {"posyandu": len(pos), "aktif": len([p for p in pos if p["aktif"]]),
                    "desa": len([d for d in per_desa if d]), "sumber": f["name"] if f else "–"},
            "posyandu": pos, "perDesa": [{"desa": k, "jumlah": v} for k, v in sorted(per_desa.items(), key=lambda x: -x[1])]}

def analisa_kader(root, files, smd_kader=None):
    f = next((x for x in files if "kader" in x["name"].lower() and x["name"].lower().endswith(".xlsx")), None)
    per_pos, per_desa, jenis = [], {}, {}
    nama_per_desa, total_nama = {}, 0
    total_sheet, pustu = None, []
    unik = set()
    duplikat = []
    if f:
        wb = load_book(f["id"], f["name"])
        if "REKAP JUMLAH KADER" in wb.sheetnames:
            cur = None
            for r in wb["REKAP JUMLAH KADER"].iter_rows(values_only=True):
                c = pad(r, 5)
                pos = title(c[2])
                if not pos or NUM_ROW.match(pos):
                    continue
                # baris ringkasan: TOTAL / JUMLAH ... (bukan posyandu)
                if pos.upper() in ("TOTAL", "JUMLAH") or pos.upper().startswith("JUMLAH "):
                    if total_sheet is None:
                        total_sheet = tonum(c[3])
                    continue
                n = tonum(c[3])
                if n is None:
                    continue
                if c[1]:
                    cur = title(c[1])
                row = {"desa": title(cur or ""), "pos": pos, "kader": n}
                if NUM_ROW.match(c[0]):
                    per_pos.append(row)
                else:
                    # baris tanpa nomor (mis. PUSTU): tetap dihitung ke total & per desa,
                    # tetapi tidak menambah jumlah posyandu.
                    row["tambahan"] = True
                    per_pos.append(row)
                    pustu.append(row)
        for ws in wb.worksheets:
            head = [norm(x) for x in pad(next(ws.iter_rows(values_only=True), ()), 12)]
            if "NAMA LENGKAP" in head:
                iv = head.index("NAMA LENGKAP")
                di = head.index("POSYANDU DESA") if "POSYANDU DESA" in head else None
                ji = next((head.index(h) for h in head if h.startswith("JENIS KADER")), None)
                bi = head.index("TANGGAL LAHIR") if "TANGGAL LAHIR" in head else None
                for i, r in enumerate(ws.iter_rows(values_only=True)):
                    if i == 0: continue
                    c = pad(r, 12)
                    nm = norm(c[iv]) if c[iv] else ""
                    if not nm or nm in ("TOTAL", "JUMLAH") or nm.startswith("JUMLAH "):
                        continue
                    total_nama += 1
                    if di is not None: nama_per_desa[title(c[di])] = nama_per_desa.get(title(c[di]), 0) + 1
                    if ji is not None and c[ji]: jenis[title(c[ji])] = jenis.get(title(c[ji]), 0) + 1
                    # kunci duplikat: nama + tanggal lahir + desa
                    key = (nm, norm(c[bi]) if bi is not None else "", norm(c[di]) if di is not None else "")
                    if key in unik:
                        duplikat.append(cap(c[iv]))
                    else:
                        unik.add(key)
        for p in per_pos: per_desa[p["desa"]] = per_desa.get(p["desa"], 0) + p["kader"]
        wb.close()
    total = sum(p["kader"] for p in per_pos)
    pos_count = len([p for p in per_pos if not p.get("tambahan")])
    pustu_total = sum(p["kader"] for p in pustu)
    daftar_unik = total_nama - len(duplikat)
    return {"kpi": {"total": total, "totalSheet": total_sheet, "pustu": pustu_total,
                    "daftarNama": total_nama, "daftarUnik": daftar_unik, "duplikat": len(duplikat),
                    "posyandu": pos_count,
                    "rataPerPos": round(total / pos_count, 1) if pos_count else 0,
                    "sumber": f["name"] if f else "–"},
            "cek": {"rekap": total, "rekapLembar": total_sheet, "form": total_nama,
                    "formUnik": daftar_unik, "duplikat": len(duplikat),
                    "selisih": total_nama - total,
                    "selisihLembar": (total_nama - total_sheet) if total_sheet is not None else None},
            "perPos": per_pos,
            "pustu": pustu,
            "perDesa": [{"desa": k, "kader": v, "nama": nama_per_desa.get(k, 0),
                         "selisih": nama_per_desa.get(k, 0) - v}
                        for k, v in sorted(per_desa.items(), key=lambda x: -x[1])],
            "jenis": [{"jenis": k, "jumlah": v} for k, v in sorted(jenis.items(), key=lambda x: -x[1])],
            "privasi": "Ringkasan ini hanya memuat JUMLAH. Nama/alamat/no HP kader tidak dimuat ke dashboard publik."}

def analisa_dinkes(root, files):
    f = next((x for x in files if "kegiatan" in x["name"].lower() and x["name"].lower().endswith(".xlsx")), None)
    keg = []
    if f:
        wb = load_book(f["id"], f["name"])
        ws = wb.worksheets[0]; cur = None
        for r in ws.iter_rows(values_only=True):
            c = pad(r, 6)
            if NUM_ROW.match(c[0]) and c[1]: cur = title(c[1])
            bl = next((title(x) for x in c[:3] if norm(x) in [norm(b) for b in BULAN]), None)
            if bl and cur:
                keg.append({"kegiatan": cur, "bulan": bl, "sudah": c[3].upper() == "V", "belum": c[4].upper() == "V"})
        wb.close()
    nama = []
    for k in keg:
        if k["kegiatan"] not in nama: nama.append(k["kegiatan"])
    return {"kpi": {"kegiatan": len(nama), "sudah": len([k for k in keg if k["sudah"]]), "total": len(keg),
                    "sumber": f["name"] if f else "–"},
            "kegiatan": keg, "namaKegiatan": nama, "bulan": BULAN}

# ============================ analisa generik (folder tanpa sheet) ============================
def analisa_umum(root, files, jenis):
    return {"kpi": {"berkas": len(files), "folder": len(root["children"]),
                    "jenis": len({os.path.splitext(f["name"])[1].lower() for f in files if "." in f["name"]}),
                    "sumber": "-" if not files else "struktur folder"},
            "catatan": jenis}

# ============================ analisa kalender Promkes ============================
def analisa_kalender():
    """Membaca ICS publik Google Calendar -> agenda mendatang + rekap jumlah."""
    from datetime import datetime, timedelta, timezone
    WIB = timezone(timedelta(hours=7))
    teks = ""
    cache = os.path.join(CACHE, "promkes.ics")
    try:
        req = urllib.request.Request(CALENDAR["ics"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=40) as r:
            teks = r.read().decode("utf-8", "replace")
        open(cache, "w", encoding="utf-8").write(teks)
    except Exception as e:
        print("    ! gagal membaca ICS:", e)
        if os.path.exists(cache):
            teks = open(cache, encoding="utf-8").read()

    # buka baris lanjutan (diawali spasi) lalu kumpulkan VEVENT
    baris = []
    for b in teks.replace("\r\n", "\n").split("\n"):
        if b[:1] in (" ", "\t") and baris:
            baris[-1] += b[1:]
        else:
            baris.append(b)
    acara = []
    cur = None
    for b in baris:
        if b == "BEGIN:VEVENT":
            cur = {}
        elif b == "END:VEVENT" and cur is not None:
            acara.append(cur); cur = None
        elif cur is not None and ":" in b:
            k, _, v = b.partition(":")
            cur[k.split(";")[0].upper()] = v.strip()

    def waktu(v):
        """ubah nilai DTSTART/DTEND menjadi datetime lokal WIB (atau tanggal saja)."""
        if not v:
            return None, True
        v = v.strip()
        if v.endswith("Z"):
            return datetime.strptime(v, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).astimezone(WIB), False
        if "T" in v:
            try:
                return datetime.strptime(v, "%Y%m%dT%H%M%S").replace(tzinfo=WIB), False
            except ValueError:
                return None, True
        try:
            return datetime.strptime(v, "%Y%m%d").replace(tzinfo=WIB), True
        except ValueError:
            return None, True

    sekarang = datetime.now(WIB)
    agenda = []
    for a in acara:
        mulai, seharian = waktu(a.get("DTSTART"))
        if not mulai:
            continue
        selesai, _ = waktu(a.get("DTEND"))
        agenda.append({
            "nama": (a.get("SUMMARY") or "(tanpa nama)").strip(),
            "mulai": mulai.isoformat(),
            "tanggal": f"{mulai.day} {BULAN_ID[mulai.month - 1]} {mulai.year}",
            "jam": None if seharian else mulai.strftime("%H.%M"),
            "jamSelesai": None if (seharian or not selesai) else selesai.strftime("%H.%M"),
            "seharian": seharian,
            "lokasi": (a.get("LOCATION") or "").strip(),
            "catatan": (a.get("DESCRIPTION") or "").strip()[:300],
            "selesai": selesai.isoformat() if selesai else None,
        })
    agenda.sort(key=lambda x: x["mulai"])
    mendatang = [x for x in agenda if datetime.fromisoformat(x["mulai"]) >= sekarang - timedelta(hours=6)]
    ini = [x for x in agenda if datetime.fromisoformat(x["mulai"]).year == sekarang.year
           and datetime.fromisoformat(x["mulai"]).month == sekarang.month]
    batas = sekarang + timedelta(days=30)
    dekat = [x for x in mendatang if datetime.fromisoformat(x["mulai"]) <= batas]
    per_bulan = {}
    for x in agenda:
        d = datetime.fromisoformat(x["mulai"])
        k = f"{BULAN_ID[d.month - 1]} {d.year}"
        per_bulan[k] = per_bulan.get(k, 0) + 1
    return {
        "kpi": {"total": len(agenda), "mendatang": len(mendatang), "dekat30": len(dekat),
                "bulanIni": len(ini),
                "berikutnya": (mendatang[0]["tanggal"] + " - " + mendatang[0]["nama"]) if mendatang else "belum ada agenda",
                "sumber": f"Kalender publik Google ({CALENDAR['src']})"},
        "agenda": mendatang,
        "semuaAgenda": agenda,
        "bulanIni": ini,
        "perBulan": [{"bulan": k, "jumlah": v} for k, v in per_bulan.items()],
        "kalender": {"embed": CALENDAR["embed"], "ics": CALENDAR["ics"], "sumber": CALENDAR["src"]},
        "catatan": ("Agenda dibaca dari feed ICS publik kalender tersebut. Tambah/ubah jadwal di Google Calendar, "
                    "lalu jalankan sinkronisasi untuk memperbarui daftar ini."),
    }


# ============================ main ============================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="hanya proses satu slug")
    ap.add_argument("--offline", action="store_true", help="jangan akses Drive, pakai cache")
    ap.add_argument("--refresh", action="store_true", help="unduh ulang berkas, abaikan cache .cache/dl")
    args = ap.parse_args()
    global REFRESH
    REFRESH = args.refresh

    print("Membaca struktur 8 folder Drive MPM...")
    roots = {}
    for slug, name, fid, sub, desc in FOLDERS:
        try:
            roots[slug] = crawl(fid, args.offline)
            nf, ns = count_tree(roots[slug])
            print(f"  {slug:<24} {nf:>3} berkas · {ns} subfolder")
        except Exception as e:
            print(f"  ! {slug}: {e}")
            roots[slug] = {"id": fid, "name": name, "url": DRIVE + fid, "items": [], "children": []}

    site = {"generated": None, "folders": []}
    for slug, name, fid, sub, desc in FOLDERS:
        root = roots[slug]
        nf, ns = count_tree(root)
        # daftar menu (site.json) selalu memuat 8 folder, walau hanya satu yang dianalisis
        site["folders"].append({"slug": slug, "menu": name, "subjudul": sub, "deskripsi": desc,
                                "id": fid, "url": DRIVE + fid, "berkas": nf, "subfolder": ns,
                                "adaData": bool(nf)})
        if args.only and slug != args.only:
            continue
        files = flatten_files(root)
        print(f"Analisa {slug} ...")
        analyzed = False
        if slug == "smd-mmd":        ana = analisa_smd(root, files); analyzed = True
        elif slug == "laporan-posyandu": ana = analisa_lhk(root, files); analyzed = True
        elif slug == "ruk":          ana = analisa_ruk(root, files); analyzed = True
        elif slug == "data-posyandu": ana = analisa_posyandu(root, files); analyzed = True
        elif slug == "data-kader":   ana = analisa_kader(root, files); analyzed = True
        elif slug == "laporan-kegiatan-dinkes": ana = analisa_dinkes(root, files); analyzed = True
        else:
            ana = analisa_umum(root, files, "belum ada berkas" if not files else "belum ada sheet ringkasan")

        # gabungkan LHK ke halaman Laporan Posyandu (berkas checklist-nya ada di sana)
        if slug == "laporan-posyandu":
            lhk_files = [f for f in files if f["name"].lower().endswith((".docx", ".doc", ".xlsx", ".pdf"))]
            ana["berkasLaporan"] = lhk_files
        payload = {
            "slug": slug, "menu": name, "subjudul": sub, "deskripsi": desc,
            "folder": {"id": fid, "url": DRIVE + fid, "name": root["name"]},
            "statistik": {"berkas": nf, "subfolder": ns},
            "struktur": outline(root),
            "files": files,
            "analisa": ana,
            "adaData": analyzed and not (slug in ("dokumentasi", "spj-bok")),
        }
        write(slug, payload)
    # --- menu tambahan: Jadwal Promkes (Google Calendar, bukan folder Drive) ---
    ana_k = None
    if not args.only or args.only == CALENDAR["slug"]:
        print("Analisa jadwal-promkes ...")
        ana_k = analisa_kalender()
        write(CALENDAR["slug"], {
            "slug": CALENDAR["slug"], "menu": CALENDAR["menu"], "subjudul": CALENDAR["subjudul"],
            "deskripsi": CALENDAR["deskripsi"],
            "folder": {"id": "", "url": CALENDAR["embed"], "name": f"Google Calendar ({CALENDAR['src']})",
                       "kalender": True},
            "statistik": {"berkas": ana_k["kpi"]["total"], "subfolder": 0},
            "struktur": None, "files": [], "analisa": ana_k, "adaData": True, "jenis": "kalender",
        })
    if ana_k is None:
        # saat --only dipakai, pertahankan entri menu dari hasil sinkron sebelumnya
        try:
            ana_k = json.load(open(os.path.join(DATA, CALENDAR["slug"] + ".json"), encoding="utf-8"))["analisa"]
        except Exception:
            ana_k = {"kpi": {"total": 0, "dekat30": 0}}
    site["folders"].append({
        "slug": CALENDAR["slug"], "menu": CALENDAR["menu"], "subjudul": CALENDAR["subjudul"],
        "deskripsi": CALENDAR["deskripsi"],
        "id": "", "url": CALENDAR["embed"], "berkas": ana_k["kpi"]["total"], "subfolder": 0,
        "adaData": True, "jenis": "kalender",
        "keterangan": f"{ana_k['kpi']['dekat30']} agenda 30 hari ke depan",
    })

    site["generated"] = stempel(datetime.now(timezone(timedelta(hours=7))))
    json.dump(site, open(os.path.join(DATA, "site.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("  -> data/site.json\nSelesai.")

if __name__ == "__main__":
    main()
