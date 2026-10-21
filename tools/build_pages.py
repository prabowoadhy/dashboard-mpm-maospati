"""
build_pages.py — membuat berkas HTML tiap halaman dari satu kerangka.

Satu halaman = satu berkas HTML (mudah dirawat & dibuka sendiri-sendiri) + satu
berkas skrip di assets/pages/<slug>.js. Kerangka (header, menu, kartu isi folder)
dibuat di sini supaya tidak berulang.

Jalankan setelah mengubah daftar menu / struktur kartu:
    python tools/build_pages.py
Untuk mengubah ISI/ringkasan data cukup sunting assets/pages/<slug>.js —
berkas HTML tidak perlu dibangun ulang.
"""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def card(title, sub, inner, full=False):
    return (f'<div class="card"{" style=\"grid-column:1/-1\"" if full else ""}>'
            f'<h3>{title}<span>{sub}</span></h3>{inner}</div>')

def page(slug, menu, title, subtitle, content):
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{subtitle}"/>
<link rel="stylesheet" href="assets/style.css"/>
</head>
<body data-page="{slug}">
<header class="top">
  <div class="inner">
    <div class="brand">
      <div class="logo">MPM</div>
      <div>
        <h1>Dashboard MPM Maospati</h1>
        <p>Manajemen Pemberdayaan Masyarakat &middot; UPTD Puskesmas Maospati</p>
      </div>
    </div>
    <div id="drivebtn"></div>
  </div>
</header>
<nav class="menu" id="navmenu"></nav>

<div class="wrap">
  <div class="pagehead">
    <div class="t">
      <h2 id="pagetitle">{menu}</h2>
      <p id="pagesub">{subtitle}</p>
      <div class="stat-line" id="pagemeta"></div>
    </div>
    <div id="drivebtn2"></div>
  </div>

  <div class="banner" id="banner"></div>

{content}

  <div class="card" style="margin-top:14px">
    <h3>Isi folder Google Drive <span id="filecount"></span></h3>
    <div class="tree" id="treehost"><p class="muted">Memuat daftar berkas...</p></div>
    <p class="note">Klik nama berkas atau folder untuk membukanya di Google Drive. Daftar ini otomatis mengikuti isi folder saat data disinkronkan ulang.</p>
  </div>

  <footer class="foot">
    <span>Sumber data: Google Drive <b>MPM Maospati</b> (8 folder) &middot; <span id="synced">memuat…</span></span>
    <span>Dashboard MPM &middot; dibangun dari berkas .xlsx di Drive</span>
  </footer>
</div>

<script src="assets/app.js"></script>
<script src="assets/pages/{slug}.js"></script>
</body>
</html>
"""

PAGES = [
 dict(slug="index", menu="Beranda", title="Dashboard MPM Maospati",
      subtitle="Ringkasan delapan kegiatan Manajemen Pemberdayaan Masyarakat UPTD Puskesmas Maospati",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div id="cards"></div>\n'
              + card("Cara kerja dashboard ini", "singkat", '<div id="catatan"></div>')),

 dict(slug="smd-mmd", menu="SMD MMD", title="SMD MMD — Dashboard MPM Maospati",
      subtitle="Survey Mawas Diri &amp; Musyawarah Masyarakat Desa: rekap per desa, capaian indikator, dan kelengkapan berkas",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Responden per Desa &amp; Tahun", "KK", '<div id="c-responden"></div><div class="legend" id="l-responden"></div>')
        + card("Kelengkapan Rekap &amp; Analisa", "KELENGKAPAN SMD.xlsx", '<div id="c-kel"></div>')
        + card("Kebutuhan &amp; Harapan Masyarakat", "top 14 dari hasil SMD", '<div id="c-keb"></div>')
        + card("Berkas Analisa per Tahun", "KAK, prioritas masalah, metode pemecahan", '<div id="c-doc"></div>')
        + card("Heatmap Indikator &times; Desa", 'tahun terpilih &middot; <span id="c-heat-sub"></span>',
               '<div class="rowctl"><label>Pilih tahun <select id="f-tahun"></select></label></div>'
               '<div class="scroll"><div id="c-heat"></div></div>'
               '<div class="legend"><span><i class="sw" style="background:#f4b6b1"></i>&lt;50%</span>'
               '<span><i class="sw" style="background:#f7dfa8"></i>50–75%</span>'
               '<span><i class="sw" style="background:#b7e2c6"></i>&ge;75%</span>'
               '<span class="muted">sel abu = data belum lengkap · perhatikan arah indikator (sebagian rendah = baik)</span></div>', full=True)
        + card("Detail Indikator per Desa", '<span id="c-tbl-sub"></span>',
               '<div class="rowctl"><label>Desa <select id="f-desa"></select></label>'
               '<label>Tahun <select id="f-tahun2"></select></label></div>'
               '<div class="scroll"><table id="t-ind"></table></div>', full=True)
        + '</div>'),

 dict(slug="laporan-posyandu", menu="Laporan Posyandu", title="Laporan Posyandu — Dashboard MPM Maospati",
      subtitle="Kelengkapan laporan bulanan LHK posyandu per bulan dan per tahun",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Laporan Terkumpul per Tahun", "bulan berstatus ADA", '<div id="c-perTahun"></div>')
        + card("Belum / Tanpa Status", "yang perlu dilengkapi", '<div id="c-sisa"></div>')
        + card("Matriks Bulan &times; Tahun", "ADA / BELUM / kosong", '<div class="scroll">' + '<div id="c-matriks"></div></div>', full=True)
        + card("Berkas Laporan di Folder", "docx &amp; xlsx", '<div id="c-berkas"></div>', full=True)
        + '</div>'),

 dict(slug="ruk", menu="RUK", title="RUK — Dashboard MPM Maospati",
      subtitle="Rencana Usulan Kegiatan: daftar usulan kegiatan per bagian, lengkap dengan tujuan, sasaran, target dan penanggung jawab",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Jumlah Kegiatan per Bagian", "RUK", '<div id="c-bagian"></div>')
        + card("Catatan &amp; Saran Format", "agar terbaca otomatis", '<div id="c-catatan"></div>')
        + card("Daftar Kegiatan", '<span id="c-info"></span>',
               '<div class="rowctl"><label>Bagian <select id="f-bagian"></select></label>'
               '<label>Cari <input id="q-ruk" type="search" placeholder="kata kunci..." size="22"/></label></div>'
               '<div class="scroll"><table id="t-ruk"></table></div>', full=True)
        + '</div>'),

 dict(slug="dokumentasi", menu="Dokumentasi", title="Dokumentasi — Dashboard MPM Maospati",
      subtitle="Dokumentasi kegiatan: daftar berkas &amp; foto pada folder Dokumentasi",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Isi Folder", "dokumentasi kegiatan", '<div id="c-isi"></div>', full=True)
        + card("Saran Struktur Berkas", "supaya mudah dibaca dashboard", '<div id="c-saran"></div>', full=True)
        + '</div>'),

 dict(slug="data-posyandu", menu="Data Posyandu", title="Data Posyandu — Dashboard MPM Maospati",
      subtitle="Daftar posyandu ILP wilayah kerja UPTD Puskesmas Maospati beserta status keaktifannya",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Jumlah Posyandu per Desa", "posyandu ILP", '<div id="c-desa"></div>')
        + card("Catatan &amp; Saran Format", "agar data tetap terbaca", '<div id="c-catatan"></div>')
        + card("Daftar Posyandu", "seluruh wilayah kerja", '<div class="scroll"><table id="t-pos"></table></div>', full=True)
        + '</div>'),

 dict(slug="data-kader", menu="Data Kader", title="Data Kader — Dashboard MPM Maospati",
      subtitle="Rekap jumlah kader posyandu per posyandu dan per desa (tanpa data pribadi)",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Rekap vs Daftar Nama", "selisih yang perlu dicek", '<div id="c-selisih"></div>')
        + card("Kader per Desa", "rekap / nama terdaftar", '<div id="c-desa"></div>')
        + card("Jenis Kader", "sebaran jenis", '<div id="c-jenis"></div>')
        + card("Ringkasan per Desa", "sinkron atau belum", '<div class="scroll"><table id="t-kader"></table></div>', full=True)
        + card("Rincian per Posyandu", "jumlah kader", '<div class="scroll"><table id="t-perpos"></table></div>', full=True)
        + '</div>'),

 dict(slug="spj-bok", menu="SPJ BOK", title="SPJ BOK — Dashboard MPM Maospati",
      subtitle="Berkas pertanggungjawaban Bantuan Operasional Kesehatan",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Isi Folder", "berkas SPJ BOK", '<div id="c-isi"></div>', full=True)
        + card("Saran Struktur Berkas", "supaya ringkasan bisa otomatis", '<div id="c-saran"></div>', full=True)
        + '</div>'),

 dict(slug="laporan-kegiatan-dinkes", menu="Laporan Kegiatan Dinkes", title="Laporan Kegiatan Dinkes — Dashboard MPM Maospati",
      subtitle="Kegiatan yang ditugaskan Dinas Kesehatan: status pengerjaan per bulan dan berkas administrasinya",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Progres per Kegiatan", "bulan sudah / dijadwalkan", '<div id="c-progres"></div>')
        + card("Belum Dikerjakan", "daftar bulan yang tertunda", '<div id="c-belum"></div>')
        + card("Matriks Kegiatan &times; Bulan", "✓ sudah · … belum", '<div id="c-matriks"></div>', full=True)
        + card("Rincian Status", "semua baris berkas sumber", '<div class="scroll"><table id="t-keg"></table></div>', full=True)
        + '</div>'),
]

def main():
    for p in PAGES:
        out = os.path.join(ROOT, p["slug"] + ".html")
        open(out, "w", encoding="utf-8").write(page(p["slug"], p["menu"], p["title"], p["subtitle"], p["content"]))
        print("  -> " + p["slug"] + ".html")
    print(f"{len(PAGES)} halaman dibuat di {ROOT}")

if __name__ == "__main__":
    main()
