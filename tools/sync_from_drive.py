"""
sync_from_drive.py — membaca folder Google Drive publik "MPM Maospati" (embeddedfolderview),
lalu mengekstrak angka dari setiap berkas .xlsx menjadi data/dashboard_data.json.

Cara pakai:
    python tools/sync_from_drive.py
Persyaratan: python 3 + openpyxl (pip install openpyxl). Tidak butuh API key —
semua folder dibaca via endpoint publik https://drive.google.com/embeddedfolderview?id=<ID>&list
dan berkas diunduh via https://drive.google.com/uc?export=download&id=<ID>
(syarat: folder/berkas dibagikan "anyone with the link -> Viewer").

Jika struktur folder berubah, cukup perbarui dict ROOTS di bawah.
"""

# ====================== 1. CRAWL STRUKTUR FOLDER ======================
import urllib.request, re, json, time, os

BASE = os.path.join(os.environ.get("TMPDIR", "."), "gdrive")
CACHE = os.path.join(BASE, "cache")
os.makedirs(CACHE, exist_ok=True)

ROOTS = {
 "SMD MMD": "1GvbF6KR_MXwwyOlLInTzMxTab3rYw7Fz",
 "LAPORAN POSYANDU": "1HYFFzGGYg9UUjoV5UsjfuDG9WmXJMrqS",
 "RUK": "1rDLnBMxf71TeG85YO74wCrfsKjjOL4Qv",
 "DOKUMENTASI": "1AfusP3TNvnC54SPrRWWxI6twW6G8ASWF",
 "DATA POSYANDU": "19dczLeNHcb20b9r-fVi1QP5ohF7oqQim",
 "DATA KADER": "1ANnRWgVu15SUEsVssE5afvYzzHpgKLgl",
 "SPJ BOK": "1YmIQquag2Qxr3jv3pFzBHjcCd8YB9mE9",
 "LAPORAN KEGIATAN DINKES": "1RTT0Ey5NanOQfGYj2v7yAZf0UrTtGlkw",
}

title_re = re.compile(r'<div class="flip-entry-title">(.*?)</div>', re.S)
link_re = re.compile(r'<a href="https://drive\.google\.com/(drive/folders|file/d)/[A-Za-z0-9_-]+')
mod_re = re.compile(r'<div class="flip-entry-last-modified"><div>(.*?)</div>')

def fetch(fid):
    p = os.path.join(CACHE, fid + ".html")
    if os.path.exists(p):
        html = open(p, encoding="utf-8").read()
    else:
        req = urllib.request.Request(f"https://drive.google.com/embeddedfolderview?id={fid}&list",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
        open(p, "w", encoding="utf-8").write(html)
        time.sleep(0.3)
    t = re.search(r"<title>(.*?)</title>", html)
    name = t.group(1) if t else fid
    items = []
    for chunk in html.split('<div class="flip-entry" id="entry-')[1:]:
        eid = chunk.split('"', 1)[0]
        t2 = title_re.search(chunk)
        l = link_re.search(chunk)
        mo = mod_re.search(chunk)
        if not t2:
            continue
        items.append({"id": eid, "name": t2.group(1).strip(),
                      "kind": "folder" if (l and l.group(1) == "drive/folders") else "file",
                      "modified": mo.group(1).strip() if mo else ""})
    return {"id": fid, "name": name, "items": items}

errors = []
def walk(label, fid, depth=0):
    try:
        node = fetch(fid)
    except Exception as e:
        errors.append(f"{label}/{fid}: {e}")
        return {"label": label, "id": fid, "name": "ERROR: " + str(e), "items": [], "children": []}
    node["label"] = label
    node["children"] = []
    if depth < 5:
        for it in node["items"]:
            if it["kind"] == "folder":
                node["children"].append(walk(it["name"], it["id"], depth + 1))
    return node

tree = {label: walk(label, fid) for label, fid in ROOTS.items()}
json.dump({"tree": tree, "errors": errors}, open(os.path.join(BASE, "tree.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def summary(node, d=0):
    ind = "  " * d
    files = [i for i in node["items"] if i["kind"] == "file"]
    folders = [i for i in node["items"] if i["kind"] == "folder"]
    out = [f"{ind}[{node.get('label')}] {node.get('name','')} | subfolder={len(folders)} file={len(files)}"]
    for i in files:
        out.append(f"{ind}  - {i['name']}  ({i['modified']})")
    for c in node.get("children", []):
        out += summary(c, d + 1)
    return out

lines = []
for k, v in tree.items():
    lines += summary(v)
open(os.path.join(BASE, "summary.txt"), "w", encoding="utf-8").write("\n".join(lines))

def count(node):
    f = len([i for i in node["items"] if i["kind"] == "file"])
    fo = len([i for i in node["items"] if i["kind"] == "folder"])
    for c in node.get("children", []):
        cf, cfo = count(c)
        f += cf; fo += cfo
    return f, fo

tot_f = tot_fo = 0
for k, v in tree.items():
    f, fo = count(v)
    tot_f += f; tot_fo += fo
    print(f"{k}: {f} file, {fo} subfolder (total)")
print("TOTAL:", tot_f, "files,", tot_fo, "subfolders")
print("ERRORS:", errors)

# ====================== 2. EKSTRAK DATA .xlsx ======================
import urllib.request, os, json, re, time, openpyxl

BASE = os.path.join(os.environ.get("TMPDIR", "."), "gdrive")
DL = os.path.join(BASE, "dl")
tree = json.load(open(os.path.join(BASE, "tree.json"), encoding="utf-8"))

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

def pad(r, n):
    out = [("" if x is None else str(x).strip()) for x in list(r)[:n]]
    return out + [""] * (n - len(out))

def dl(fid, name):
    p = os.path.join(DL, re.sub(r"[^A-Za-z0-9._-]", "_", fid + "_" + name))
    if os.path.exists(p) and os.path.getsize(p) > 2000: return p
    req = urllib.request.Request(f"https://drive.google.com/uc?export=download&id={fid}",
                                headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r: data = r.read()
    open(p, "wb").write(data); time.sleep(0.3); return p

ID_BY_NAME = {}
def walk(n):
    for i in n["items"]:
        if i["kind"] == "file": ID_BY_NAME[(n.get("label"), i["name"])] = i["id"]
    for c in n.get("children", []): walk(c)
for v in tree["tree"].values(): walk(v)

def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().upper()

# ---------------- SMD ----------------
def parse_rekap(path, tahun):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        rows = [pad(r, 9) for r in ws.iter_rows(values_only=True)]
        rec = {"desa": ws.title.title(), "tahun": tahun, "responden": None, "ind": [], "kebutuhan": []}
        for r in rows[:12]:
            j = " ".join(x for x in r if x)
            m = re.search(r"Jumlah Responden.*?(\d+)\s*KK", j)
            if m and rec["responden"] is None: rec["responden"] = int(m.group(1))
            d = re.search(r"(?:DESA|KELURAHAN)\s+([A-Z]{3,}[A-Z ]*)", j)
            if d: rec["desa"] = d.group(1).strip().title()
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
                cur_ind = {"t": norm(s1), "k": cur_k or "UMUM", "y": tonum(r[2]), "n": tonum(r[3])}
                rec["ind"].append(cur_ind)
            elif s0 == "" and s1 and cur_ind is not None and re.match(r"^[a-z]\.", s1):
                rec["ind"].append({"t": norm(s1), "k": cur_ind["k"], "y": tonum(r[2]), "n": None})
        if rec["ind"]: out.append(rec)
    wb.close(); return out

smd = []; seen = set()
for (lab, fname), fid in ID_BY_NAME.items():
    low = fname.lower()
    if not low.endswith(".xlsx"): continue
    if lab not in ("HASIL REKAP SMD", "REKAP SMD", "REKAP", "SMD MMD"): continue
    if lab == "SMD MMD" and "rekap" not in low: continue
    m = re.search(r"(20\d\d)", fname)
    tahun = int(m.group(1)) if m else None
    try:
        p = dl(fid, fname)
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True); sheets = wb.sheetnames; wb.close()
        for rec in parse_rekap(p, tahun):
            k = (norm(rec["desa"]), rec["tahun"])
            if k in seen: continue
            seen.add(k); rec["src"] = fname; smd.append(rec)
    except Exception as e:
        print("ERR", fname, e)
print("SMD:", len(smd))

# ---------------- Kader ----------------
p = dl(ID_BY_NAME[("DATA KADER", "Data Kader 2025 (Responses).xlsx")], "kader.xlsx")
wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
kader_pos = []; cur = None
for r in wb["REKAP JUMLAH KADER"].iter_rows(values_only=True):
    c = pad(r, 5)
    if NUM_ROW.match(c[0]) and c[1]: cur = c[1].title()
    if NUM_ROW.match(c[0]) and c[2] and not NUM_ROW.match(c[2]):
        kader_pos.append({"desa": (cur or c[1]).title(), "pos": c[2].title(), "kader": tonum(c[3]) or 0})
kader_desa = {}
for k in kader_pos: kader_desa[k["desa"]] = kader_desa.get(k["desa"], 0) + k["kader"]
kader_total = sum(k["kader"] for k in kader_pos)
kader_person = 0; kader_nama_desa = {}
for i, r in enumerate(wb["NAMA KADER"].iter_rows(values_only=True)):
    c = pad(r, 8)
    if i == 0 or not c[1]: continue
    kader_person += 1
    d = (c[6] or "-").title()
    kader_nama_desa[d] = kader_nama_desa.get(d, 0) + 1
wb.close()
print("kader posyandu:", len(kader_pos), "total kader:", kader_total, "nama terdaftar:", kader_person)

# ---------------- Posyandu ----------------
p = dl(ID_BY_NAME[("DATA POSYANDU", "POSYANDU AKTIF.xlsx")], "posyandu.xlsx")
wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
posyandu = []; cur = None
for r in wb["Sheet1"].iter_rows(values_only=True):
    c = pad(r, 5)
    if NUM_ROW.match(c[0]) and c[1]: cur = c[1].title()
    if not c[2] or c[2].upper() in ("POS", "TOTAL"): continue
    if not NUM_ROW.match(c[0]) and not cur: continue
    posyandu.append({"desa": (cur or "").title(), "pos": c[2].title(),
                     "aktif": tonum(c[3]) or 0, "tidak": tonum(c[4]) or 0})
wb.close()
print("posyandu:", len(posyandu))

# ---------------- Kelengkapan SMD ----------------
p = dl(ID_BY_NAME[("SMD MMD", "KELENGKAPAN SMD.xlsx")], "kel_smd.xlsx")
wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
kel_smd = []; cur = None
for r in wb["Sheet1"].iter_rows(values_only=True):
    c = pad(r, 7)
    if tonum(c[1]) and 2000 < tonum(c[1]) < 2100: cur = tonum(c[1])
    if c[2] and cur and c[2].upper() not in ("DESA/KELURAHAN",):
        kel_smd.append({"tahun": cur, "desa": c[2].title(),
                        "rekap": c[3].upper() == "V", "analisa": c[5].upper() == "V"})
wb.close()
print("kel_smd:", len(kel_smd))

# ---------------- LHK ----------------
p = dl(ID_BY_NAME[("LAPORAN POSYANDU", "KELENGKAPAN LHK.xlsx")], "lhk.xlsx")
wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
lhk = []; cur = None
for r in wb["Sheet1"].iter_rows(values_only=True):
    c = pad(r, 6)
    if tonum(c[1]) and 2000 < tonum(c[1]) < 2100: cur = tonum(c[1])
    if c[2] and cur and c[2].upper() != "BULAN":
        lhk.append({"tahun": cur, "bulan": c[2].title(), "ada": c[3].upper() == "V", "belum": c[4].upper() == "V"})
wb.close()
print("lhk:", len(lhk))

# ---------------- Kegiatan Dinkes ----------------
p = dl(ID_BY_NAME[("LAPORAN KEGIATAN DINKES", "KEGIATAN DINKES.xlsx")], "dinkes.xlsx")
wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
BULAN = {"JANUARI","FEBRUARI","MARET","APRIL","MEI","JUNI","JULI","AGUSTUS","SEPTEMBER","OKTOBER","NOVEMBER","DESEMBER"}
dinkes = []; cur = None
for r in wb["Sheet1"].iter_rows(values_only=True):
    c = pad(r, 6)
    if NUM_ROW.match(c[0]) and c[1]: cur = c[1].title()
    bl = next((x.title() for x in c[:3] if x.upper() in BULAN), None)
    if bl and cur:
        dinkes.append({"kegiatan": cur, "bulan": bl, "sudah": c[3].upper() == "V", "belum": c[4].upper() == "V"})
wb.close()
print("dinkes:", len(dinkes))

# ---------------- Inventaris ----------------
invent = []
def walk2(n, path):
    for i in n["items"]:
        invent.append({"folder": path, "name": i["name"], "kind": i["kind"], "id": i["id"], "mod": i["modified"]})
    for c in n.get("children", []):
        walk2(c, path + "/" + c["name"])
for k, v in tree["tree"].items(): walk2(v, k)

out = {"smd": smd, "kader_pos": kader_pos, "kader_total": kader_total, "kader_person": kader_person,
       "kader_desa": kader_desa, "kader_nama_desa": kader_nama_desa, "posyandu": posyandu,
       "kel_smd": kel_smd, "lhk": lhk, "dinkes": dinkes, "invent": invent}
json.dump(out, open(os.path.join(BASE, "dashboard_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK -> dashboard_data.json")
print("kader_desa:", kader_desa)
print("kader_nama:", kader_nama_desa)
