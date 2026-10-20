import json, os, re, statistics, html

BASE = os.path.join(os.environ.get("TMPDIR", "."), "gdrive")
D = json.load(open(os.path.join(BASE, "dashboard_data.json"), encoding="utf-8"))

# ---------- dictionary indikator ----------
ind_texts = []
ind_idx = {}
for rec in D["smd"]:
    for it in rec["ind"]:
        if it["t"] not in ind_idx:
            ind_idx[it["t"]] = len(ind_texts); ind_texts.append(it["t"])

smd = []
for rec in D["smd"]:
    smd.append({
        "desa": rec["desa"], "tahun": rec["tahun"], "responden": rec["responden"], "src": rec["src"],
        "ind": [[ind_idx[i["t"]], i["y"], i["n"], i["k"]] for i in rec["ind"]],
        "klaster": sorted({i["k"] for i in rec["ind"]}, key=lambda s: (len(s), s)),
        "keb": rec["kebutuhan"],
    })

# kebutuhan & harapan -> parse "N ORANG INGIN ..."
def parse_keb(lst):
    out = []
    for s in lst:
        m = re.match(r"^\s*(\d+)\s*ORANG\s*(?:INGIN|MENGINGINKAN)?\s*(.*)$", s, re.I)
        if m:
            out.append({"n": int(m.group(1)), "t": m.group(2).strip(" .:-").title()})
        else:
            out.append({"n": 1, "t": s.strip(" .:-").title()})
    return out

for rec in smd:
    rec["kebp"] = parse_keb(rec["keb"])

keb_agg = {}
for rec in smd:
    for k in rec["kebp"]:
        key = re.sub(r"[^A-Z ]", "", k["t"].upper()).strip()
        key = re.sub(r"\s+", " ", key)
        if len(key) < 6: continue
        e = keb_agg.setdefault(key, {"t": k["t"], "n": 0, "desa": set(), "tahun": set()})
        e["n"] += k["n"]; e["desa"].add(rec["desa"]); e["tahun"].add(rec["tahun"])
keb_top = sorted(
    [{"t": v["t"], "n": v["n"], "desa": sorted(v["desa"]), "tahun": sorted(v["tahun"])} for v in keb_agg.values()],
    key=lambda x: -x["n"])[:18]

# ---------- data kualitas / temuan ----------
dupes = {}
for f in D["invent"]:
    if f["kind"] != "file": continue
    dupes.setdefault(f["name"].lower(), []).append(f)
dupe_list = [{"name": v[0]["name"], "folders": [x["folder"] for x in v]} for k, v in dupes.items() if len(v) > 1]
temp_files = [f["name"] for f in D["invent"] if f["kind"] == "file" and f["name"].startswith("~$")]
empty_folders = [k for k, v in D["invent"].items() if False] if False else []

tahun_desa = {}
for rec in smd:
    tahun_desa.setdefault(rec["tahun"], set()).add(rec["desa"])
tahun_desa = {k: sorted(v) for k, v in sorted(tahun_desa.items())}
all_desa = sorted({r["desa"] for r in smd})

# ---------- KPI ----------
tot_kk = {}
for rec in smd:
    if rec["responden"]:
        tot_kk[rec["tahun"]] = tot_kk.get(rec["tahun"], 0) + rec["responden"]

def cov(y, n):
    if y is None or n is None: return None
    if (y + n) == 0: return None
    return round(100.0 * y / (y + n), 1)

lhk_2026 = [x for x in D["lhk"] if x["tahun"] == 2026]
lhk_ada = sum(1 for x in lhk_2026 if x["ada"])
kel_2026 = [x for x in D["kel_smd"] if x["tahun"] == 2026]

payload = {
    "smd": smd, "indTexts": ind_texts, "allDesa": all_desa, "tahunDesa": tahun_desa,
    "kaderPos": D["kader_pos"], "kaderTotal": D["kader_total"], "kaderPerson": D["kader_person"],
    "kaderDesa": D["kader_desa"], "kaderNama": D["kader_nama_desa"],
    "posyandu": D["posyandu"], "kelSmd": D["kel_smd"], "lhk": D["lhk"], "dinkes": D["dinkes"],
    "invent": [{"folder": f["folder"], "name": f["name"], "kind": f["kind"], "mod": f["mod"]} for f in D["invent"]],
    "kebTop": keb_top, "totKk": tot_kk,
    "temuan": {"dupes": dupe_list, "temp": temp_files,
               "emptyFolders": ["DOKUMENTASI", "SPJ BOK"],
               "lhk2026": {"ada": lhk_ada, "total": len(lhk_2026)},
               "kel2026": {"rekap": sum(1 for x in kel_2026 if x["rekap"]),
                           "analisa": sum(1 for x in kel_2026 if x["analisa"]), "total": len(kel_2026)}},
}

TPL = r"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Dashboard MPM - UPTD Puskesmas Maospati</title>
<style>
  :root{
    --bg:#f4f6f9; --surface:#ffffff;
    --fg:#111827; --mut:#58606d; --bd:#e4e8ee; --bd2:#eef1f5; --ac:#2563eb;
    --c1:#3b82f6; --c2:#10b981; --c3:#f59e0b; --c4:#ef4444; --c5:#8b5cf6; --c6:#ec4899;
    --shadow:0 1px 2px rgba(15,23,42,.04), 0 14px 30px -22px rgba(15,23,42,.45);
  }
  *{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%}
  body{
    margin:0;min-height:100vh;
    font-family:var(--font-family,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif);
    color:var(--fg);
    background:
      radial-gradient(1100px 420px at 12% -8%, rgba(59,130,246,.12), transparent 62%),
      radial-gradient(900px 400px at 88% -12%, rgba(16,185,129,.12), transparent 60%),
      var(--bg);
    font-size:13.5px;line-height:1.5;
    -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
  }
  h1,h2,h3{margin:0;font-weight:700;letter-spacing:-.01em}
  .wrap{max-width:1320px;margin:0 auto;padding:20px 20px 46px}
  header.top{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;border-bottom:1px solid var(--bd);padding-bottom:14px}
  .brand{display:flex;gap:13px;align-items:center}
  .logo{width:44px;height:44px;border-radius:13px;background:linear-gradient(135deg,var(--c1),var(--c2));display:grid;place-items:center;font-weight:800;color:#04121f;font-size:14px;letter-spacing:.03em;box-shadow:0 10px 22px -14px rgba(59,130,246,.95)}
  .brand h1{font-size:18px;line-height:1.25}
  .brand p{margin:3px 0 0;color:var(--mut);font-size:12px;font-weight:500}
  .meta{color:var(--mut);font-size:11.5px;text-align:right;line-height:1.55}
  nav.tabs{position:sticky;top:0;z-index:6;display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:16px -6px 18px;padding:12px 6px;background:color-mix(in srgb,var(--bg) 82%,transparent);backdrop-filter:blur(10px) saturate(150%);-webkit-backdrop-filter:blur(10px) saturate(150%)}
  nav.tabs button{border:1px solid var(--bd);background:var(--surface);color:var(--mut);padding:7px 14px;border-radius:999px;cursor:pointer;font-size:12.5px;font-weight:600;font-family:inherit;letter-spacing:.01em;box-shadow:0 1px 2px rgba(15,23,42,.05);transition:background .16s,color .16s,border-color .16s,transform .16s}
  nav.tabs button:hover{color:var(--fg);border-color:#cdd4de;transform:translateY(-1px)}
  nav.tabs button.on{color:#fff;border-color:var(--fg);background:var(--fg);box-shadow:0 10px 20px -14px rgba(15,23,42,.9)}
  nav.tabs button:focus-visible{outline:2px solid var(--ac);outline-offset:2px}
  section{display:none}
  section.on{display:block;animation:fade .24s ease}
  @keyframes fade{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
  .grid{display:grid;gap:14px}
  .k4{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
  .k2{grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}
  .card{border:1px solid var(--bd);border-radius:14px;padding:15px 16px;background:var(--surface);box-shadow:var(--shadow)}
  .kpi .v{font-size:26px;font-weight:700;letter-spacing:-.025em;line-height:1.15;margin-top:6px;font-variant-numeric:tabular-nums}
  .kpi .l{color:var(--mut);font-size:10.5px;font-weight:650;text-transform:uppercase;letter-spacing:.08em}
  .kpi .s{font-size:11.5px;color:var(--mut);margin-top:4px}
  .card h3{font-size:13px;font-weight:650;margin-bottom:11px;padding-bottom:10px;border-bottom:1px solid var(--bd2);display:flex;justify-content:space-between;align-items:center;gap:8px}
  .card h3 span{color:var(--mut);font-weight:500;font-size:11.5px}
  table{border-collapse:separate;border-spacing:0;width:100%;font-size:12.5px}
  th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--bd2);vertical-align:top}
  th{color:var(--mut);font-weight:650;font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;background:#f7f9fc}
  th:first-child{border-top-left-radius:9px}
  th:last-child{border-top-right-radius:9px}
  tbody tr:last-child td{border-bottom:0}
  tbody tr:hover td{background:#f8fafd}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  .barchart{display:flex;flex-direction:column;gap:7px}
  .brow{display:grid;grid-template-columns:minmax(150px,44%) 1fr 60px;gap:9px;align-items:center;font-size:12px}
  .brow .lab{color:#384152;line-height:1.3;font-size:11.5px}
  .track{height:9px;border-radius:99px;background:#edf0f5;overflow:hidden;box-shadow:inset 0 1px 2px rgba(15,23,42,.07)}
  .fill{height:100%;border-radius:99px}
  .val{text-align:right;color:var(--mut);font-weight:600;font-variant-numeric:tabular-nums}
  .hm{display:grid;gap:3px;font-size:10.5px;align-items:stretch}
  .hm .hc{height:30px;border-radius:6px;display:grid;place-items:center;color:#0b1220;font-weight:650;font-variant-numeric:tabular-nums;box-shadow:inset 0 0 0 1px rgba(255,255,255,.45)}
  .hm .hl{min-height:30px;display:flex;align-items:center;color:var(--mut);font-size:10.5px;line-height:1.2;padding:2px 8px 2px 0;white-space:normal}
  .legend{display:flex;gap:11px;align-items:center;color:var(--mut);font-size:11px;margin-top:9px;flex-wrap:wrap}
  .sw{width:11px;height:11px;border-radius:3px;display:inline-block;margin-right:4px;vertical-align:-1px}
  .pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:10.5px;font-weight:650;letter-spacing:.02em;border:1px solid transparent;white-space:nowrap}
  .pill.ok{color:#0c7a5e;background:#e7f8f1;border-color:#bde9da}
  .pill.no{color:#c0362c;background:#fdeceb;border-color:#f6cdc9}
  .pill.wr{color:#95650c;background:#fdf3e2;border-color:#f4dfba}
  select,input{background:var(--surface);color:var(--fg);border:1px solid var(--bd);border-radius:9px;padding:6px 9px;font-family:inherit;font-size:12.5px;transition:border-color .15s,box-shadow .15s}
  select:focus-visible,input:focus-visible{outline:none;border-color:var(--ac);box-shadow:0 0 0 3px rgba(37,99,235,.16)}
  .rowctl{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:11px}
  .muted{color:var(--mut)}
  .tl{font-size:12.5px;margin:0;padding-left:17px}
  .tl li{margin:5px 0}
  .tl b{font-weight:650}
  .tag{display:inline-block;padding:2px 7px;border-radius:6px;border:1px solid var(--bd);background:#f7f9fc;color:#4b5563;font-size:10.5px;margin:2px 4px 2px 0}
  svg text{fill:#6b7280;font-size:10px}
  .foot{color:var(--mut);font-size:11px;margin-top:16px;border-top:1px solid var(--bd);padding-top:12px}
  .scroll{overflow:auto;max-height:430px;border-radius:10px}
  .scroll thead th{position:sticky;top:0;z-index:1;box-shadow:inset 0 -1px 0 var(--bd)}
  .scroll::-webkit-scrollbar{width:10px;height:10px}
  .scroll::-webkit-scrollbar-track{background:transparent}
  .scroll::-webkit-scrollbar-thumb{background:#d2d8e1;border-radius:99px;border:2px solid transparent;background-clip:content-box}
  .scroll::-webkit-scrollbar-thumb:hover{background:#b8c0cc;background-clip:content-box}
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
  @media print{
    body{background:#fff}
    nav.tabs{position:static;background:none;backdrop-filter:none}
    .card{box-shadow:none;break-inside:avoid}
    .scroll{max-height:none;overflow:visible}
  }
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="brand">
      <div class="logo">MPM</div>
      <div>
        <h1>Dashboard Manajemen Pemberdayaan Masyarakat</h1>
        <p>UPTD Puskesmas Maospati &middot; SMD/MMD, Posyandu, Kader, LHK, Kegiatan DINKES &amp; RUK</p>
      </div>
    </div>
    <div class="meta">
      Prototipe dashboard &middot; data dari Google Drive MPM<br/>
      <span id="stamp"></span>
    </div>
  </header>

  <nav class="tabs" id="tabs"></nav>

  <section id="t-ringkasan" class="on">
    <div class="grid k4" id="kpis" style="margin-bottom:12px"></div>
    <div class="grid k2">
      <div class="card"><h3>Responden SMD/MMD per Desa &amp; Tahun <span>KK</span></h3><div id="ch-responden"></div>
        <div class="legend" id="lg-responden"></div></div>
      <div class="card"><h3>Status Kelengkapan Dokumen <span>dari checklist internal</span></h3><div id="ch-status"></div></div>
      <div class="card"><h3>Kebutuhan &amp; Harapan Masyarakat (SMD) <span>top 12, gabungan semua desa/tahun</span></h3><div id="ch-keb"></div></div>
      <div class="card"><h3>Temuan Kualitas Data <span>perlu dibereskan</span></h3><div id="temuan"></div></div>
    </div>
  </section>

  <section id="t-smd">
    <div class="rowctl">
      <label>Desa/Kel <select id="f-desa"></select></label>
      <label>Tahun <select id="f-tahun"></select></label>
      <span class="muted" id="smd-info"></span>
    </div>
    <div class="grid k4" id="smd-kpi" style="margin-bottom:12px"></div>
    <div class="grid k2">
      <div class="card"><h3>Capaian per Klaster <span>% rata-rata indikator (YA / (YA+TIDAK))</span></h3><div id="ch-klaster"></div></div>
      <div class="card"><h3>10 Indikator Capaian Terendah <span>desa &amp; tahun terpilih (hati-hati arah indikator)</span></h3><div id="ch-terendah"></div></div>
      <div class="card" id="card-heat"><h3>Heatmap Indikator &times; Desa <span>tahun terpilih &middot; warna = % jawaban YA</span></h3>
        <div class="scroll"><div id="ch-heat"></div></div>
        <div class="legend"><span><i class="sw" style="background:#ef4444"></i>&lt;50%</span><span><i class="sw" style="background:#f59e0b"></i>50-75%</span><span><i class="sw" style="background:#10b981"></i>&ge;75%</span><span class="muted">sel abu = data belum ada &middot; indikator bertanda merah pada panel terendah belum tentu masalah (mis. "keluarga ada yang menderita TB" rendah = baik)</span></div>
      </div>
      <div class="card"><h3>Detail Indikator <span id="tbl-info"></span></h3><div class="scroll"><table id="tbl-ind"></table></div></div>
    </div>
  </section>

  <section id="t-posyandu">
    <div class="grid k2" style="margin-bottom:12px">
      <div class="card"><h3>Posyandu Aktif per Desa <span>42 posyandu ILP</span></h3><div id="ch-pos"></div></div>
      <div class="card"><h3>Jumlah Kader per Desa <span>rekap vs daftar nama</span></h3><div id="ch-kader"></div>
        <div class="legend"><span><i class="sw" style="background:var(--c1)"></i>Rekap jumlah kader</span><span><i class="sw" style="background:var(--c5)"></i>Daftar nama (form 2025)</span></div></div>
    </div>
    <div class="card"><h3>Rasio &amp; Sebaran Kader per Posyandu <span>klik kolom untuk urut</span></h3>
      <div class="scroll"><table id="tbl-kader"></table></div></div>
  </section>

  <section id="t-kelengkapan">
    <div class="grid k2">
      <div class="card"><h3>Laporan LHK Bulanan <span>ADA / BELUM</span></h3><div id="ch-lhk"></div></div>
      <div class="card"><h3>Kelengkapan SMD/MMD <span>rekap &amp; analisa per desa</span></h3><div class="scroll"><table id="tbl-kelsmd"></table></div></div>
      <div class="card"><h3>Kegiatan DINKES <span>kader buaian 2026</span></h3><div id="ch-dinkes"></div></div>
      <div class="card"><h3>Progres Kegiatan per Bulan <span>semua kegiatan tercatat</span></h3><div id="ch-dinkes2"></div></div>
    </div>
  </section>

  <section id="t-dokumen">
    <div class="rowctl"><label>Cari <input id="q-doc" placeholder="nama file..." size="26"/></label>
      <label>Folder <select id="f-doc"></select></label>
      <span class="muted" id="doc-info"></span></div>
    <div class="grid k4" id="doc-kpi" style="margin-bottom:12px"></div>
    <div class="card"><h3>Inventaris Berkas Drive</h3><div class="scroll"><table id="tbl-doc"></table></div></div>
  </section>

  <div class="foot">Prototipe dashboard dibuat dari pembacaan langsung folder Google Drive MPM (lihat tab Dokumen). Angka dihitung ulang dari berkas .xlsx sumber; sel kosong/tidak relevan tidak dihitung sebagai 0.</div>
</div>

<script>
const D = __DATA__;
const $ = s => document.querySelector(s);
const el = (t,c,h) => { const e=document.createElement(t); if(c)e.className=c; if(h!==undefined)e.innerHTML=h; return e; };
const fmt = n => (n===null||n===undefined) ? '–' : n.toLocaleString('id-ID');
const pct = v => (v===null||v===undefined) ? '–' : (v.toFixed(v%1?1:0)+'%');
const COV = (y,n) => (y===null||y===undefined||n===null||n===undefined||(y+n)===0) ? null : 100*y/(y+n);
const COL = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899'];

/* ---------- KPI ---------- */
const thnList = Object.keys(D.totKk).map(Number).sort();
const tLatest = thnList[thnList.length-1];
const allRec = D.smd.filter(r=>r.tahun===tLatest);
const covAll = [];
allRec.forEach(r=>r.ind.forEach(i=>{const c=COV(i[1],i[2]); if(c!==null&&!/^[a-z]\./.test(D.indTexts[i[0]]))covAll.push(c);}));
const covAvg = covAll.length ? covAll.reduce((a,b)=>a+b,0)/covAll.length : null;
const totalKK = Object.values(D.totKk).reduce((a,b)=>a+b,0);
const kpi = [
 ['Desa / Kelurahan', D.allDesa.length, 'wilayah kerja UPTD'],
 ['Posyandu ILP', D.posyandu.length, 'aktif: '+D.posyandu.filter(p=>p.aktif).length+' · tidak aktif: '+D.posyandu.filter(p=>p.tidak).length],
 ['Kader Posyandu', D.kaderTotal, 'kader terdaftar (form): '+D.kaderPerson],
 ['Responden SMD (semua tahun)', totalKK, 'tahun '+thnList.join(', ')],
 ['Rata-rata capaian indikator '+tLatest, covAvg===null?null:covAvg, 'dari '+allRec.length+' desa yang masuk'],
 ['LHK 2026 terkumpul', D.temuan.lhk2026.ada+'/'+D.temuan.lhk2026.total, 'bulan dengan laporan ADA'],
];
$('#kpis').innerHTML = kpi.map(k=>`<div class="card kpi"><div class="l">${k[0]}</div><div class="v">${typeof k[1]==='number'&&k[0].includes('capaian')?pct(k[1]):fmt(k[1])}</div><div class="s">${k[2]}</div></div>`).join('');

/* ---------- Responden SMD grouped bar (SVG) ---------- */
(function(){
  const desa = D.allDesa, thn = thnList;
  const W = 660, H = 60 + desa.length*13, padL = 96, bw = 6;
  let max = 0; desa.forEach(d=>thn.forEach(t=>{const r=D.smd.find(x=>x.desa===d&&x.tahun===t); if(r&&r.responden)max=Math.max(max,r.responden);}));
  const scale = v => (W-padL-40) * v / (max||1);
  let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}">`;
  desa.forEach((d,di)=>{
    const y = 34 + di*13;
    s += `<text x="0" y="${y+8}">${d}</text>`;
    thn.forEach((t,ti)=>{
      const r = D.smd.find(x=>x.desa===d&&x.tahun===t);
      const v = r&&r.responden ? r.responden : 0;
      const yy = y + ti*(13/thn.length), hh = Math.max(1.4,(13/thn.length)-1.6);
      s += v ? `<rect x="${padL}" y="${yy.toFixed(1)}" width="${scale(v).toFixed(1)}" height="${hh.toFixed(1)}" rx="1.5" fill="${COL[ti%6]}"><title>${d} ${t}: ${v} KK</title></rect>`
             : `<rect x="${padL}" y="${yy.toFixed(1)}" width="4" height="${hh.toFixed(1)}" rx="1.5" fill="#cbd5e1"><title>${d} ${t}: belum ada data</title></rect>`;
    });
  });
  s += `<line x1="${padL}" y1="26" x2="${padL}" y2="${H-14}" stroke="#d5dbe4" stroke-width=".6"/>`;
  [0,0.5,1].forEach(f=>{const x=padL+scale(max*f); s+=`<text x="${x-6}" y="22">${Math.round(max*f)}</text>`;});
  s += '</svg>';
  $('#ch-responden').innerHTML = s;
  $('#lg-responden').innerHTML = thn.map((t,i)=>`<span><i class="sw" style="background:${COL[i%6]}"></i>${t}</span>`).join('') + '<span><i class="sw" style="background:#cbd5e1"></i>belum ada berkas</span>';
})();

/* ---------- status dokumen ---------- */
(function(){
  const rows = [];
  const t = thnList, desa = D.allDesa;
  const kelBy = {}; D.kelSmd.forEach(k=>kelBy[k.tahun+'|'+k.desa]=k);
  let rekap=0, analisa=0, total=0;
  t.forEach(th=>desa.forEach(d=>{total++; const k=kelBy[th+'|'+d]; if(k){if(k.rekap)rekap++; if(k.analisa)analisa++;}}));
  const lhkBy = {}; D.lhk.forEach(x=>lhkBy[x.tahun+'|'+x.bulan]=x);
  const mk = (y)=>D.lhk.filter(x=>x.tahun===y&&x.ada).length;
  rows.push(['Rekap SMD/MMD selesai (semua tahun)', rekap, total]);
  rows.push(['Analisa hasil SMD selesai', analisa, total]);
  rows.push(['LHK 2025 terkumpul', mk(2025), 12]);
  rows.push(['LHK 2026 terkumpul', mk(2026), 12]);
  rows.push(['Kegiatan DINKES dikerjakan', D.dinkes.filter(x=>x.sudah).length, D.dinkes.length]);
  rows.push(['Berkas SMD tersedia (desa-tahun)', D.smd.length, desa.length*t.length]);
  $('#ch-status').innerHTML = '<div class="barchart">'+rows.map((r,i)=>{
    const p = r[2]?100*r[1]/r[2]:0;
    const c = p>=80?'var(--c2)':p>=50?'var(--c3)':'var(--c4)';
    return `<div class="brow"><div class="lab">${r[0]}</div><div class="track"><div class="fill" style="width:${p.toFixed(0)}%;background:${c}"></div></div><div class="val">${r[1]}/${r[2]}</div></div>`;
  }).join('')+'</div>';
})();

/* ---------- kebutuhan ---------- */
(function(){
  const m = Math.max(...D.kebTop.map(k=>k.n),1);
  $('#ch-keb').innerHTML = '<div class="barchart">'+D.kebTop.slice(0,12).map((k,i)=>
    `<div class="brow"><div class="lab" title="${k.t}">${k.t}</div><div class="track"><div class="fill" style="width:${100*k.n/m}%;background:${COL[i%6]}"></div></div><div class="val">${k.n} org</div></div>`).join('')+'</div>';
})();

/* ---------- temuan ---------- */
(function(){
  const T = D.temuan; let h = '<ul class="tl">';
  h += `<li><b>${T.dupes.length} berkas duplikat</b> tersimpan di dua folder berbeda ` + T.dupes.slice(0,6).map(d=>`<span class="tag">${d.name}</span>`).join('') + `</li>`;
  h += `<li><b>${T.temp.length} file sementara Office</b> ikut terunggah: ` + T.temp.map(x=>`<span class="tag">${x}</span>`).join('') + '</li>';
  h += `<li><b>Folder kosong:</b> ` + T.emptyFolders.map(x=>`<span class="tag">${x}</span>`).join('') + ' — belum ada isi.</li>';
  h += `<li><b>Kader tidak konsisten:</b> rekap ${D.kaderTotal} kader vs daftar nama ${D.kaderPerson} (selisih ${Math.abs(D.kaderTotal-D.kaderPerson)}); beberapa desa berbeda jauh (mis. Malang 15 vs 20, Maospati 47 vs 32).</li>`;
  h += `<li><b>Kelengkapan SMD ${tLatest}:</b> rekap ${T.kel2026.rekap}/${T.kel2026.total}, analisa ${T.kel2026.analisa}/${T.kel2026.total} desa.</li>`;
  h += `<li><b>Instrumen berubah:</b> berkas 2023-2024 memakai 52 indikator (tanpa klaster), 2025-2026 memakai 61 baris klaster 1-4 — tren antar tahun belum sebanding.</li>`;
  h += '</ul>';
  $('#temuan').innerHTML = h;
})();

/* ---------- TABS ---------- */
const TABS = [['ringkasan','Ringkasan'],['smd','SMD / MMD'],['posyandu','Posyandu &amp; Kader'],['kelengkapan','Kelengkapan &amp; Kegiatan'],['dokumen','Dokumen &amp; Berkas']];
$('#tabs').innerHTML = TABS.map((t,i)=>`<button data-t="${t[0]}" class="${i===0?'on':''}">${t[1]}</button>`).join('');
$('#tabs').onclick = e => {
  const b = e.target.closest('button'); if(!b) return;
  document.querySelectorAll('nav.tabs button').forEach(x=>x.classList.toggle('on',x===b));
  document.querySelectorAll('section').forEach(s=>s.classList.toggle('on', s.id==='t-'+b.dataset.t));
};

/* ---------- SMD tab ---------- */
const selDesa = $('#f-desa'), selTahun = $('#f-tahun');
selDesa.innerHTML = D.allDesa.map(d=>`<option>${d}</option>`).join('');
selTahun.innerHTML = thnList.slice().reverse().map(t=>`<option>${t}</option>`).join('');
function recOf(d,t){ return D.smd.find(r=>r.desa===d&&r.tahun===t); }
function renderSMD(auto){
  const d = selDesa.value; let t = +selTahun.value; let r = recOf(d,t);
  if(!r && auto){
    const cand = thnList.filter(y=>D.smd.some(x=>x.desa===d&&x.tahun===y));
    if(cand.length){ t = cand[cand.length-1]; selTahun.value = t; r = recOf(d,t); }
  }
  const desaTahun = D.allDesa.filter(x=>D.smd.some(y=>y.desa===x&&y.tahun===t));
  $('#smd-info').textContent = r ? ('sumber: '+r.src) : 'belum ada berkas untuk kombinasi ini';
  if(!r){
    $('#smd-kpi').innerHTML=''; $('#tbl-ind').innerHTML=''; $('#ch-heat').innerHTML='';
    const ada = thnList.filter(y=>D.smd.some(x=>x.desa===d&&x.tahun===y));
    const msg = `<span class="pill wr">belum ada berkas</span> rekap SMD <b>${d} ${t}</b>. Yang tersedia: ${ada.length?ada.join(', '):'—'}.`;
    $('#ch-klaster').innerHTML = msg; $('#ch-terendah').innerHTML = '<span class="muted">—</span>';
    return;
  }
  const covs = r.ind.map(i=>({t:D.indTexts[i[0]],c:COV(i[1],i[2]),y:i[1],n:i[2]})).filter(x=>x.c!==null && !/^[a-z]\./.test(x.t));
  const avg = covs.length? covs.reduce((a,b)=>a+b.c,0)/covs.length : null;
  const prev = thnList.filter(x=>x<t).pop();
  const rp = prev ? recOf(d,prev) : null;
  let avgP = null;
  if(rp){ const c2 = rp.ind.map(i=>COV(i[1],i[2])).filter(x=>x!==null); if(c2.length) avgP = c2.reduce((a,b)=>a+b,0)/c2.length; }
  const delta = (avg!==null&&avgP!==null)? avg-avgP : null;
  $('#smd-kpi').innerHTML = [
    ['Responden', fmt(r.responden), 'KK di '+d],
    ['Indikator terukur', covs.length, 'dari '+r.ind.length+' baris instrumen'],
    ['Rata-rata capaian', avg===null?'–':pct(avg), prev?('vs '+prev+': '+(delta===null?'–':(delta>0?'+':'')+pct(delta))):'—'],
    ['Baris instrumen', r.ind.length, 'instrumen 2025-2026 (klaster 1-4)'],
  ].map(k=>`<div class="card kpi"><div class="l">${k[0]}</div><div class="v">${k[1]}</div><div class="s">${k[2]}</div></div>`).join('');

  // klaster bars
  const perK = {};
  r.ind.forEach(i=>{const c=COV(i[1],i[2]); if(c===null||/^[a-z]\./.test(D.indTexts[i[0]]))return; const k=String(i[3]); (perK[k]=perK[k]||[]).push(c);});
  const kb = Object.entries(perK).map(([k,v])=>[k, v.reduce((a,b)=>a+b,0)/v.length]);
  $('#ch-klaster').innerHTML = '<div class="barchart">'+kb.map((k,i)=>
    `<div class="brow"><div class="lab">${k[0]}</div><div class="track"><div class="fill" style="width:${k[1].toFixed(0)}%;background:${COL[i%6]}"></div></div><div class="val">${pct(k[1])}</div></div>`).join('')+'</div>';

  // terendah
  const low = covs.slice().sort((a,b)=>a.c-b.c).slice(0,10);
  $('#ch-terendah').innerHTML = '<div class="barchart">'+low.map(x=>
    `<div class="brow"><div class="lab" title="${x.t}">${x.t}</div><div class="track"><div class="fill" style="width:${x.c.toFixed(0)}%;background:${x.c<50?'var(--c4)':x.c<75?'var(--c3)':'var(--c2)'}"></div></div><div class="val">${pct(x.c)}</div></div>`).join('')+'</div>';

  // tabel indikator
  const prevMap = {};
  if(rp) rp.ind.forEach(i=>prevMap[D.indTexts[i[0]]]=COV(i[1],i[2]));
  const rowsHtml = r.ind.map(i=>{
    const t2 = D.indTexts[i[0]], c = COV(i[1],i[2]);
    const pp = prevMap[t2];
    const dl = (c!==null&&pp!==null&&pp!==undefined)? c-pp : null;
    return `<tr><td>${String(i[3]).replace('KLASTER ','K')}</td><td>${t2.toLowerCase()}</td><td class="num">${fmt(i[1])}</td><td class="num">${fmt(i[2])}</td><td class="num">${pct(c)}</td><td class="num" style="color:${dl===null?'var(--mut)':dl>=0?'#0c8f66':'#d9382e'}">${dl===null?'–':(dl>0?'+':'')+dl.toFixed(1)}</td></tr>`;
  }).join('');
  $('#tbl-ind').innerHTML = `<thead><tr><th>Klaster</th><th>Indikator</th><th class="num">YA</th><th class="num">TIDAK</th><th class="num">%</th><th class="num">Δ ${prev||''}</th></tr></thead><tbody>${rowsHtml}</tbody>`;
  $('#tbl-info').textContent = d+' '+t;

  // heatmap
  const cols = desaTahun;
  const texts = r.ind.filter(i=>!i[2] && i[2]!==0 ? true : true).map(i=>i);
  const uniq = [];
  const seen = {};
  r.ind.forEach(i=>{ const t2=D.indTexts[i[0]]; if(!/^[a-z]\./.test(t2) && !seen[t2]){seen[t2]=1;uniq.push(t2);} });
  let h = `<div class="hm" style="grid-template-columns:minmax(190px,340px) repeat(${cols.length},minmax(46px,1fr))">`;
  h += '<div class="hl">Indikator</div>' + cols.map(c=>`<div class="hl" style="justify-content:center;text-align:center">${c}</div>`).join('');
  uniq.forEach(t2=>{
    h += `<div class="hl" title="${t2}">${t2.toLowerCase().slice(0,42)}</div>`;
    cols.forEach(c=>{
      const rr = D.smd.find(x=>x.desa===c&&x.tahun===t);
      if(!rr){ h += '<div class="hc" style="background:#eef1f5;color:#9aa4b4" title="tidak ada data">–</div>'; return; }
      const it = rr.ind.find(x=>D.indTexts[x[0]]===t2);
      const cv = it ? COV(it[1],it[2]) : null;
      if(cv===null){ h += '<div class="hc" style="background:#eef1f5;color:#9aa4b4" title="data tidak lengkap">–</div>'; return; }
      const bg = cv<50?'#ef4444':cv<75?'#f59e0b':'#10b981';
      h += `<div class="hc" style="background:${bg}" title="${c} ${t} — ${t2}: ${pct(cv)}">${cv.toFixed(0)}</div>`;
    });
  });
  h += '</div>';
  $('#ch-heat').innerHTML = h;
}
selDesa.onchange = selTahun.onchange = () => { renderSMD(true); };
selDesa.value = (D.allDesa.includes('Malang') ? 'Malang' : D.allDesa[0]);
selTahun.value = tLatest;

/* ---------- posyandu ---------- */
(function(){
  const perDesa = {}; D.posyandu.forEach(p=>perDesa[p.desa]=(perDesa[p.desa]||0)+1);
  const m = Math.max(...Object.values(perDesa),1);
  $('#ch-pos').innerHTML = '<div class="barchart">'+Object.entries(perDesa).sort((a,b)=>b[1]-a[1]).map((k,i)=>
    `<div class="brow"><div class="lab">${k[0]}</div><div class="track"><div class="fill" style="width:${100*k[1]/m}%;background:${COL[i%6]}"></div></div><div class="val">${k[1]} pos</div></div>`).join('')+'</div>';
  const md = Math.max(...Object.values(D.kaderDesa), ...Object.values(D.kaderNama));
  $('#ch-kader').innerHTML = '<div class="barchart">'+D.allDesa.map(d=>{
    const a = D.kaderDesa[d]||0, b = D.kaderNama[d]||0;
    return `<div class="brow"><div class="lab">${d}</div><div class="track" style="position:relative;height:14px">
      <div class="fill" style="width:${100*a/md}%;background:var(--c1);height:6px;margin-top:1px"></div>
      <div class="fill" style="width:${100*b/md}%;background:var(--c5);height:6px;position:absolute;top:7px"></div></div>
      <div class="val">${a}/${b}</div></div>`;}).join('')+'</div>';
  const byDesa = {};
  D.kaderPos.forEach(k=>{(byDesa[k.desa]=byDesa[k.desa]||[]).push(k);});
  let rows = '';
  D.allDesa.forEach(d=>{
    const pos = D.kaderPos.filter(k=>k.desa===d);
    const sum = pos.reduce((a,b)=>a+b.kader,0);
    const nm = D.kaderNama[d];
    rows += `<tr><td><b>${d}</b></td><td class="muted">${pos.length} posyandu</td><td class="num">${sum}</td><td class="num">${nm!==undefined?nm:'–'}</td><td class="num">${pos.length?(sum/pos.length).toFixed(1):'–'}</td></tr>`;
    pos.forEach(k=>{ rows += `<tr><td></td><td style="padding-left:14px">${k.pos}</td><td class="num muted">${k.kader}</td><td></td><td></td></tr>`; });
  });
  $('#tbl-kader').innerHTML = `<thead><tr><th>Desa/Kel</th><th>Posyandu</th><th class="num">Kader rekap</th><th class="num">Kader daftar nama</th><th class="num">Rata2/pos</th></tr></thead><tbody>${rows}</tbody>`;
})();

/* ---------- kelengkapan ---------- */
(function(){
  const BUL = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
  const ths = [...new Set(D.lhk.map(x=>x.tahun))].sort();
  let h = '<table><thead><tr><th>Bulan</th>'+ths.map(t=>`<th>${t}</th>`).join('')+'</tr></thead><tbody>';
  BUL.forEach(b=>{
    h += `<tr><td>${b}</td>`;
    ths.forEach(t=>{
      const x = D.lhk.find(y=>y.tahun===t&&y.bulan===b);
      if(!x){ h += '<td>–</td>'; return; }
      h += `<td>${x.ada?'<span class="pill ok">ADA</span>':x.belum?'<span class="pill no">BELUM</span>':'<span class="pill wr">kosong</span>'}</td>`;
    });
    h += '</tr>';
  });
  h += '</tbody></table>';
  $('#ch-lhk').innerHTML = h;

  const desa = D.allDesa, th = [...new Set(D.kelSmd.map(x=>x.tahun))].sort();
  let t2 = '<thead><tr><th>Desa/Kel</th>'+th.map(y=>`<th>${y}</th>`).join('')+'</tr></thead><tbody>';
  desa.forEach(d=>{
    t2 += `<tr><td>${d}</td>`;
    th.forEach(y=>{
      const k = D.kelSmd.find(x=>x.tahun===y&&x.desa===d);
      if(!k){ t2 += '<td>–</td>'; return; }
      t2 += `<td>${k.rekap?'<span class="pill ok">rekap</span>':'<span class="pill no">rekap</span>'} ${k.analisa?'<span class="pill ok">analisa</span>':'<span class="pill no">analisa</span>'}</td>`;
    });
    t2 += '</tr>';
  });
  t2 += '</tbody>';
  $('#tbl-kelsmd').innerHTML = t2;

  const BUL2 = BUL;
  const keg = [...new Set(D.dinkes.map(x=>x.kegiatan))];
  let d1 = '<table><thead><tr><th>Kegiatan</th>'+BUL2.map(b=>`<th style="font-size:9.5px">${b.slice(0,3)}</th>`).join('')+'</tr></thead><tbody>';
  keg.forEach(k=>{
    d1 += `<tr><td>${k}</td>`;
    BUL2.forEach(b=>{
      const x = D.dinkes.find(y=>y.kegiatan===k&&y.bulan===b);
      d1 += `<td>${!x?'<span class="muted">·</span>':x.sudah?'<span class="pill ok">✓</span>':'<span class="pill no">…</span>'}</td>`;
    });
    d1 += '</tr>';
  });
  d1 += '</tbody></table>';
  $('#ch-dinkes').innerHTML = d1;
  const su = D.dinkes.filter(x=>x.sudah).length;
  const p = 100*su/D.dinkes.length;
  $('#ch-dinkes2').innerHTML = '<div class="barchart"><div class="brow"><div class="lab">'+keg[0]+' 2026</div><div class="track"><div class="fill" style="width:'+p.toFixed(0)+'%;background:var(--c3)"></div></div><div class="val">'+su+'/'+D.dinkes.length+'</div></div></div><p class="muted" style="font-size:12px;margin:10px 0 0">Juni–September sudah dikerjakan, Oktober–November belum. Kegiatan lain (mis. SMD/MMD per desa, pembinaan kader, RUK 2027) belum tercatat di sheet ini — calon menu tambahan dashboard.</p>';
})();

/* ---------- dokumen ---------- */
(function(){
  const filesOnly = D.invent.filter(f=>f.kind==='file');
  const folders = [...new Set(D.invent.filter(f=>f.kind==='folder').map(f=>f.folder))];
  const ext = {}; filesOnly.forEach(f=>{const e=(f.name.split('.').pop()||'').toLowerCase(); ext[e]=(ext[e]||0)+1;});
  $('#doc-kpi').innerHTML = [
    ['Berkas', filesOnly.length, 'file di Drive'],
    ['Subfolder', D.invent.filter(f=>f.kind==='folder').length, 'tersebar pada 8 folder utama'],
    ['Jenis berkas', Object.keys(ext).length, Object.entries(ext).map(([k,v])=>k+':'+v).join(' · ')],
    ['Folder utama', 8, 'SMD MMD, LHK, RUK, DOKUMENTASI, DATA POSYANDU, DATA KADER, SPJ BOK, LAP. DINKES'],
  ].map(k=>`<div class="card kpi"><div class="l">${k[0]}</div><div class="v">${k[1]}</div><div class="s">${k[2]}</div></div>`).join('');
  const topFolders = [...new Set(filesOnly.map(f=>f.folder.split('/')[0]))].sort();
  $('#f-doc').innerHTML = ['<option value="">Semua folder</option>'].concat(topFolders.map(f=>`<option>${f}</option>`)).join('');
  function draw(){
    const q = $('#q-doc').value.toLowerCase(), fo = $('#f-doc').value;
    const rows = filesOnly.filter(f=>(!q||f.name.toLowerCase().includes(q))&&(!fo||f.folder.startsWith(fo)));
    $('#doc-info').textContent = rows.length+' berkas ditampilkan';
    $('#tbl-doc').innerHTML = '<thead><tr><th>Folder</th><th>Nama berkas</th><th>Diubah</th></tr></thead><tbody>'+rows.map(f=>`<tr><td class="muted">${f.folder}</td><td>${f.name}</td><td class="muted">${f.mod||''}</td></tr>`).join('')+'</tbody>';
  }
  $('#q-doc').oninput = draw; $('#f-doc').onchange = draw; draw();
})();

renderSMD();
$('#stamp').textContent = 'disusun ' + new Date().toLocaleDateString('id-ID',{day:'numeric',month:'long',year:'numeric'});
</script>
</body>
</html>
"""

OUTDIR = r"D:/Documents/Dashboard-MPM"
os.makedirs(OUTDIR, exist_ok=True)
html_out = TPL.replace("__DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
open(os.path.join(OUTDIR, "index.html"), "w", encoding="utf-8").write(html_out)
open(os.path.join(BASE, "index_preview.html"), "w", encoding="utf-8").write(html_out)
print("wrote", os.path.join(OUTDIR, "index.html"), len(html_out), "bytes")
print("kebTop sample:", json.dumps(keb_top[:5], ensure_ascii=False))
print("totKk:", tot_kk, "covAvg:", covAvg if 'covAvg' in dir() else '')
