"""
build_pages.py · membuat berkas HTML tiap halaman dari satu kerangka.

Satu halaman = satu berkas HTML (mudah dirawat & dibuka sendiri-sendiri) + satu
berkas skrip di assets/pages/<slug>.js. Kerangka (header, tombol Sinkron, menu,
kartu isi folder) dibuat di sini supaya tidak berulang.

Setiap panel diberi keterangan **sumber data** (`src=...`) supaya mudah dicek ke
berkas Excel aslinya. Untuk panel yang nama berkasnya dideteksi otomatis oleh
tools/sync.py, tambahkan `auto=True` · keterangan akan dilengkapi nama berkas nyata.

Jalankan setelah mengubah daftar menu / struktur kartu:
    python tools/build_pages.py
Untuk mengubah ISI/ringkasan data cukup sunting assets/pages/<slug>.js.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def card(title, sub, inner, full=False, src=None, auto=False):
    garis = ""
    if src is not None:
        auto_attr = ' data-auto-sumber="1"' if auto else ''
        garis = f'<p class="src"{auto_attr}>Sumber data: {src}</p>'
    return (f'<section class="card{" full" if full else ""}">'
            f'<h3>{title}<span>{sub}</span></h3>{inner}{garis}</section>')


def page(slug, menu, title, subtitle, content, show_tree=True):
    data_file = "site.json" if slug == "index" else slug + ".json"
    data_path = os.path.join(ROOT, "data", data_file)
    inline = ""
    if os.path.exists(data_path):
        blob = open(data_path, encoding="utf-8").read().replace("</", "<\\/")
        inline = ('<script>window.__DATA__ = window.__DATA__ || {}; '
                  f'window.__DATA__["{slug}"] = {blob};</script>\n')
    tre = """
  <details class="utility">
    <summary><span id="treecard">Isi folder Google Drive</span> <span id="filecount">memuat</span></summary>
    <div class="body">
      <div class="tree" id="treehost"><p class="muted">Memuat daftar berkas...</p></div>
      <p class="note">Klik nama berkas atau folder untuk membukanya di Google Drive. Daftar ini mengikuti isi
      folder saat data disinkronkan ulang (<code>python tools/sync.py</code>).</p>
    </div>
  </details>""" if show_tree else ""
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="theme-color" content="#f7f9fc"/>
<title>{title}</title>
<meta name="description" content="{subtitle}"/>
<link rel="stylesheet" href="assets/style.css"/>
</head>
<body data-page="{slug}">
<a class="skip" href="#main">Langsung ke isi</a>
<div class="topwrap">
  <header class="top">
    <div class="inner">
      <button class="menu-toggle" id="menutoggle" type="button" aria-expanded="false" aria-controls="navmenu" aria-label="Buka menu">
        <span class="bars" aria-hidden="true"><span></span><span></span><span></span></span>
        <span class="menu-toggle-label">Menu</span>
      </button>
      <div class="brand">
        <div class="logo" aria-hidden="true">MPM</div>
        <div>
          <h1>Dashboard MPM Maospati</h1>
          <p>Manajemen Pemberdayaan Masyarakat &middot; UPTD Puskesmas Maospati</p>
        </div>
      </div>
      <div id="drivebtn"></div>
    </div>
  </header>
  <nav class="menu" aria-label="Menu utama"><div class="navinner" id="navmenu"></div></nav>
</div>

<main class="wrap" id="main">
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
{tre}

  <details class="utility">
    <summary>Cara membaca &amp; memperbaiki data</summary>
    <div class="body">
      <ul class="tl">
        <li>Setiap panel mencantumkan <b>sumber data</b> di bagian bawah kartu: nama berkas Excel-nya
        beserta folder tempat berkas itu berada di Google Drive.</li>
        <li>Kalau angka di halaman berbeda dengan dugaan Anda, buka berkas Excel pada folder itu
        (tombol <b>Buka folder Drive</b> di atas) dan cocokkan kolomnya.</li>
        <li>Sesudah berkas diperbaiki di Drive, tekan <b>Sinkronkan data</b> di kanan atas agar
        halaman menampilkan angka terbaru.</li>
        <li>Format berkas yang dipakai dashboard dijelaskan di README pada bagian
        "Saran perbaikan data".</li>
      </ul>
    </div>
  </details>

  <footer class="foot">
    <span>Sumber data: Google Drive <b>MPM Maospati</b> &amp; kalender Promkes &middot; <span id="synced">memuat…</span></span>
    <span>UPTD Puskesmas Maospati</span>
  </footer>
</main>

{inline}<script src="assets/app.js"></script>
<script src="assets/pages/{slug}.js"></script>
</body>
</html>
"""


SRC_SMD_REKAP = ('berkas rekap tiap desa di folder <b>SMD MMD</b> · mis. <code>HASIL REKAP MPT 2023.xlsx</code>, '
                 '<code>SUGIHWARAS SMD 2025 REKAP.xlsx</code>, <code>MALANG REKAP 2026.xlsx</code> (baris indikator &amp; '
                 'baris "Jumlah Responden : N KK")')
SRC_KEL_SMD = ('<code>KELENGKAPAN SMD.xlsx</code> · folder <b>SMD MMD</b> (kolom REKAP &amp; ANALISA HASIL)')
SRC_KEL_LHK = ('<code>KELENGKAPAN LHK.xlsx</code> · folder <b>LAPORAN POSYANDU</b> (kolom TAHUN, BULAN, '
               'LAPORAN: ADA/BELUM)')
SRC_RUK = ('<code>Copy of BAB IV Perencanaan Belanja 2027 SIP.xlsx</code> · folder <b>RUK</b>, sheet <code>BAB IV</code> '
           '(kolom pelayanan/unit, kegiatan, tujuan, sasaran, target, penanggung jawab)')

PAGES = [
 dict(slug="index", menu="Beranda", title="Dashboard MPM Maospati",
      subtitle="Ringkasan sembilan menu kegiatan Manajemen Pemberdayaan Masyarakat UPTD Puskesmas Maospati",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div id="cards"></div>\n'
              + card("Cara kerja dashboard ini", "singkat", '<div id="catatan"></div>',
                     src='<code>data/site.json</code> · hasil pembacaan 8 folder Google Drive MPM '
                         '+ kalender publik Promkes oleh <code>tools/sync.py</code>')),

 dict(slug="smd-mmd", menu="SMD MMD", title="SMD MMD · Dashboard MPM Maospati",
      subtitle="Survey Mawas Diri &amp; Musyawarah Masyarakat Desa: rekap per desa, capaian indikator, dan kelengkapan berkas",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Responden per Desa &amp; Tahun", "KK", '<div id="c-responden"></div>',
               full=True, src=SRC_SMD_REKAP)
        + card("Kelengkapan Rekap &amp; Analisa", "KELENGKAPAN SMD.xlsx", '<div id="c-kel"></div>',
               full=True, src=SRC_KEL_SMD, auto=True)
        + card("Kebutuhan &amp; Harapan Masyarakat", "top 14 dari hasil SMD", '<div id="c-keb"></div>',
               src='baris <b>Kebutuhan dan Harapan</b> di bagian bawah setiap berkas rekap desa (folder <b>SMD MMD</b>)')
        + card("Berkas Analisa per Tahun", "KAK, prioritas masalah, metode pemecahan", '<div id="c-doc"></div>',
               src='berkas <code>.docx/.pdf/.pptx</code> pada subfolder <b>ANALISA</b> / <b>HASIL REKAP SMD</b> (folder SMD MMD)')
        + card("Heatmap Indikator &times; Desa", 'tahun terpilih &middot; <span id="c-heat-sub"></span>',
               '<div class="rowctl"><label>Pilih tahun <select id="f-tahun"></select></label></div>'
               '<div class="scroll"><div id="c-heat"></div></div>'
               '<div class="legend"><span><i class="sw" style="background:#fce8e6"></i>&lt;50%</span>'
               '<span><i class="sw" style="background:#fef7e0"></i>50–75%</span>'
               '<span><i class="sw" style="background:#e6f4ea"></i>&ge;75%</span>'
               '<span class="muted">sel abu = data belum lengkap · perhatikan arah indikator (sebagian rendah = baik)</span></div>',
               full=True, src=SRC_SMD_REKAP)
        + card("Detail Indikator per Desa", '<span id="c-tbl-sub"></span>',
               '<div class="rowctl"><label>Desa <select id="f-desa"></select></label>'
               '<label>Tahun <select id="f-tahun2"></select></label></div>'
               '<div class="scroll"><table id="t-ind"></table></div>',
               full=True, src=SRC_SMD_REKAP)
        + '</div>'),

 dict(slug="laporan-posyandu", menu="Laporan Posyandu", title="Laporan Posyandu · Dashboard MPM Maospati",
      subtitle="Kelengkapan laporan bulanan LHK posyandu per bulan dan per tahun",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Laporan Terkumpul per Tahun", "bulan berstatus ADA", '<div id="c-perTahun"></div>',
               src=SRC_KEL_LHK, auto=True)
        + card("Belum / Tanpa Status", "yang perlu dilengkapi", '<div id="c-sisa"></div>', src=SRC_KEL_LHK)
        + card("Matriks Bulan &times; Tahun", "ADA / BELUM / kosong", '<div class="scroll"><div id="c-matriks"></div></div>',
               full=True, src=SRC_KEL_LHK)
        + card("Berkas Laporan di Folder", "docx &amp; xlsx", '<div id="c-berkas"></div>', full=True,
               src='berkas laporan pada folder <b>LAPORAN POSYANDU</b> (LHK bulanan; dokumen pendukung ada di folder <b>DATA POSYANDU</b>)')
        + '</div>'),

 dict(slug="ruk", menu="RUK", title="RUK · Dashboard MPM Maospati",
      subtitle="Rencana Usulan Kegiatan: daftar usulan kegiatan per bagian, lengkap dengan tujuan, sasaran, target dan penanggung jawab",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Jumlah Kegiatan per Bagian", "RUK", '<div id="c-bagian"></div>', src=SRC_RUK, auto=True)
        + card("Catatan &amp; Saran Format", "agar terbaca otomatis", '<div id="c-catatan"></div>',
               src='pengamatan otomatis atas berkas RUK di folder <b>RUK</b>')
        + card("Daftar Kegiatan", '<span id="c-info"></span>',
               '<div class="rowctl"><label>Bagian <select id="f-bagian"></select></label>'
               '<label>Cari <input id="q-ruk" type="search" placeholder="kata kunci..." size="22"/></label></div>'
               '<div class="scroll"><table id="t-ruk"></table></div>',
               full=True, src=SRC_RUK)
        + '</div>'),

 dict(slug="dokumentasi", menu="Dokumentasi", title="Dokumentasi · Dashboard MPM Maospati",
      subtitle="Dokumentasi kegiatan: daftar berkas &amp; foto pada folder Dokumentasi",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Isi Folder", "dokumentasi kegiatan", '<div id="c-isi"></div>', full=True,
               src='folder <b>DOKUMENTASI</b> di Google Drive (belum ada berkas)')
        + card("Saran Struktur Berkas", "supaya mudah dibaca dashboard", '<div id="c-saran"></div>', full=True,
               src='rekomendasi · belum ada berkas sumber')
        + '</div>'),

 dict(slug="data-posyandu", menu="Data Posyandu", title="Data Posyandu · Dashboard MPM Maospati",
      subtitle="Daftar posyandu ILP wilayah kerja UPTD Puskesmas Maospati beserta status keaktifannya",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Jumlah Posyandu per Desa", "posyandu ILP", '<div id="c-desa"></div>',
               src='<code>POSYANDU AKTIF.xlsx</code> · folder <b>DATA POSYANDU</b> (kolom DESA/KEL, POS, AKTIF)', auto=True)
        + card("Catatan &amp; Saran Format", "agar data tetap terbaca", '<div id="c-catatan"></div>',
               src='pengamatan otomatis atas <code>POSYANDU AKTIF.xlsx</code>')
        + card("Daftar Posyandu", "seluruh wilayah kerja", '<div class="scroll"><table id="t-pos"></table></div>',
               full=True, src='<code>POSYANDU AKTIF.xlsx</code> · satu baris = satu posyandu')
        + '</div>'),

 dict(slug="data-kader", menu="Data Kader", title="Data Kader · Dashboard MPM Maospati",
      subtitle="Rekap jumlah kader posyandu per posyandu dan per desa (tanpa data pribadi)",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Rekap vs Daftar Nama", "selisih yang perlu dicek", '<div id="c-selisih"></div>',
               src='<code>Data Kader .xlsx</code> · folder <b>DATA KADER</b>: sheet <b>REKAP JUMLAH KADER</b> (jumlah resmi) '
                   'vs sheet <b>NAMA KADER</b> (hasil form)', auto=True)
        + card("Kader per Desa", "rekap / nama terdaftar", '<div id="c-desa"></div>',
               src='<code>Data Kader .xlsx</code> · sheet REKAP JUMLAH KADER (kolom DESA/KEL, POS, KADER) &amp; sheet NAMA KADER (kolom POSYANDU DESA)')
        + card("Jenis Kader", "sebaran jenis", '<div id="c-jenis"></div>',
               src='<code>Data Kader .xlsx</code> · sheet <b>NAMA KADER</b>, kolom <b>JENIS KADER</b>')
        + card("Ringkasan per Desa", "sinkron atau belum", '<div class="scroll"><table id="t-kader"></table></div>',
               full=True, src='<code>Data Kader .xlsx</code> · sheet REKAP JUMLAH KADER')
        + card("Rincian per Posyandu", "jumlah kader", '<div class="scroll"><table id="t-perpos"></table></div>',
               full=True, src='<code>Data Kader .xlsx</code> · sheet REKAP JUMLAH KADER (satu baris = satu posyandu; baris <b>PUSTU</b> tanpa nomor tetap dihitung)')
        + '</div>'),

 dict(slug="spj-bok", menu="SPJ BOK", title="SPJ BOK · Dashboard MPM Maospati",
      subtitle="Berkas pertanggungjawaban Bantuan Operasional Kesehatan",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Isi Folder", "berkas SPJ BOK", '<div id="c-isi"></div>', full=True,
               src='folder <b>SPJ BOK</b> di Google Drive (belum ada berkas)')
        + card("Saran Struktur Berkas", "supaya ringkasan bisa otomatis", '<div id="c-saran"></div>', full=True,
               src='rekomendasi · belum ada berkas sumber')
        + '</div>'),

 dict(slug="laporan-kegiatan-dinkes", menu="Laporan Kegiatan Dinkes", title="Laporan Kegiatan Dinkes · Dashboard MPM Maospati",
      subtitle="Kegiatan yang ditugaskan Dinas Kesehatan: status pengerjaan per bulan dan berkas administrasinya",
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n  <div class="grid k2">\n'
        + card("Progres per Kegiatan", "bulan sudah / dijadwalkan", '<div id="c-progres"></div>',
               src='<code>KEGIATAN DINKES.xlsx</code> · folder <b>LAPORAN KEGIATAN DINKES</b> (kolom NAMA KEGIATAN, BULAN, DIKERJAKAN SUDAH/BELUM)', auto=True)
        + card("Belum Dikerjakan", "daftar bulan yang tertunda", '<div id="c-belum"></div>',
               src='<code>KEGIATAN DINKES.xlsx</code> · baris dengan kolom DIKERJAKAN = BELUM')
        + card("Matriks Kegiatan &times; Bulan", "sudah / belum / kosong", '<div id="c-matriks"></div>', full=True,
               src='<code>KEGIATAN DINKES.xlsx</code> · kolom BULAN')
        + card("Rincian Status", "semua baris berkas sumber", '<div class="scroll"><table id="t-keg"></table></div>',
               full=True, src='<code>KEGIATAN DINKES.xlsx</code> · seluruh baris')
        + '</div>'),

 dict(slug="jadwal-promkes", menu="Jadwal Promkes", title="Jadwal Promkes · Dashboard MPM Maospati",
      subtitle="Jadwal kegiatan promosi kesehatan dari kalender publik Google · plus daftar agenda mendatang",
      show_tree=False,
      content='<div class="grid k4" id="kpis" style="margin-bottom:14px"></div>\n'
        + card("Kalender Jadwal Promkes", "tampilan langsung dari Google Calendar",
               '<div class="cal-wrap">'
               '<iframe src="JADWAL_EMBED" title="Kalender Jadwal Promkes UPTD Puskesmas Maospati" '
               'loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen '
               'style="border:0" frameborder="0" scrolling="no"></iframe>'
               '</div>'
               '<div class="legend"><span class="muted">Tampilkan/tutup kalender lain lewat menu di kanan atas kalender; '
               'klik salah satu agenda untuk melihat rinciannya.</span></div>',
               full=True,
               src='kalender publik Google <b>dhellayaamanda2@gmail.com</b> · <b>bukan</b> berkas Excel; '
                   'agenda dikelola langsung di Google Calendar')
        + '<div class="grid k2" style="margin-top:14px">\n'
        + card("Agenda 30 Hari ke Depan", "urut waktu terdekat", '<div id="c-agenda"></div>',
               src='feed ICS publik kalender tersebut (<code>calendar/ical/.../public/basic.ics</code>)')
        + card("Jumlah Agenda per Bulan", "dari kalender publik", '<div id="c-perbulan"></div>',
               src='feed ICS publik · seluruh agenda yang dibagikan publik')
        + card("Agenda Bulan Ini", "seluruh kegiatan bulan berjalan", '<div class="scroll"><table id="t-bulanini"></table></div>',
               full=True, src='feed ICS publik · agenda dengan bulan berjalan')
        + card("Semua Agenda Mendatang", "termasuk yang belum terjadwal rapi", '<div class="scroll"><table id="t-agenda"></table></div>',
               full=True, src='feed ICS publik · agenda yang belum lewat')
        + '</div>'
        + card("Cara mengisi &amp; memperbarui jadwal", "bukan dari berkas Excel", '<div id="c-catatan"></div>',
               src='Google Calendar <b>dhellayaamanda2@gmail.com</b>'),
 ),
]


def main():
    for p in PAGES:
        embed = ("https://calendar.google.com/calendar/embed?src=dhellayaamanda2%40gmail.com"
                 "&ctz=Asia%2FJakarta&hl=id&mode=MONTH&showTitle=0&showPrint=0&showTz=0&showCalendars=0&showTabs=1")
        html = page(p["slug"], p["menu"], p["title"], p["subtitle"], p["content"],
                    show_tree=p.get("show_tree", True)).replace("JADWAL_EMBED", embed)
        open(os.path.join(ROOT, p["slug"] + ".html"), "w", encoding="utf-8").write(html)
        print("  -> " + p["slug"] + ".html")
    print(f"{len(PAGES)} halaman dibuat di {ROOT}")


if __name__ == "__main__":
    main()