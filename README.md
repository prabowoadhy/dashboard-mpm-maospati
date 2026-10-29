# Dashboard MPM Maospati

Dashboard sepuluh menu kegiatan **Manajemen Pemberdayaan Masyarakat, UPTD Puskesmas Maospati**,
dibangun dari berkas yang sudah ada di Google Drive (sumber: <https://sites.google.com/view/mpmmaospati/home>),
ditambah satu spreadsheet Google (PKP) dan kalender Promkes.

Delapan menu mengikuti delapan folder Drive, satu menu membaca spreadsheet Google, dan satu menu membaca
kalender publik. Tiap menu punya **halaman sendiri** dan **berkas data sendiri** supaya mudah dirawat:

| # | Menu | Halaman | Data | Isi ringkasan |
|---|---|---|---|---|
| 1 | SMD MMD | `smd-mmd.html` | `data/smd-mmd.json` | responden per desa & tahun, capaian per klaster, heatmap indikator × desa, kelengkapan rekap & analisa, kebutuhan/harapan warga, berkas analisa |
| 2 | Laporan Posyandu | `laporan-posyandu.html` | `data/laporan-posyandu.json` | matriks kelengkapan LHK bulan × tahun, progres per tahun, sisa yang belum |
| 3 | RUK | `ruk.html` | `data/ruk.json` | jumlah kegiatan per bagian, daftar kegiatan + tujuan/sasaran/target/PJ (dari BAB IV) |
| 4 | PKP | `pkp.html` | `data/pkp.json` | capaian indikator Penilaian Kinerja Puskesmas per klaster, indikator terendah, catatan & bukti (dari spreadsheet Google) |
| 5 | Dokumentasi | `dokumentasi.html` | `data/dokumentasi.json` | daftar berkas/foto + saran struktur (folder masih kosong) |
| 6 | Data Posyandu | `data-posyandu.html` | `data/data-posyandu.json` | posyandu per desa, status aktif, tabel lengkap |
| 7 | Data Kader | `data-kader.html` | `data/data-kader.json` | kader per desa/posyandu, selisih rekap vs form (**tanpa data pribadi**) |
| 8 | SPJ BOK | `spj-bok.html` | `data/spj-bok.json` | daftar berkas SPJ + saran format rekap serapan |
| 9 | Laporan Kegiatan Dinkes | `laporan-kegiatan-dinkes.html` | `data/laporan-kegiatan-dinkes.json` | matriks kegiatan × bulan, progres, berkas pendukung |
| 10 | Jadwal Promkes | `jadwal-promkes.html` | `data/jadwal-promkes.json` | kalender publik Google (iframe) + agenda 30 hari ke depan, agenda bulan ini, rekap per bulan dari feed ICS |

Beranda `index.html` menampilkan 10 kartu menu + jumlah berkas tiap folder.
Setiap halaman punya tombol **menuju folder Google Drive** dan daftar isi folder (berkas & subfolder)
yang bisa diklik untuk membuka berkas aslinya. Halaman **PKP** tombolnya menuju spreadsheet Google,
halaman **Jadwal Promkes** menuju Google Calendar.

Tampilan memakai **tema putih/terang permanen** (tidak mengikuti mode gelap sistem operasi), dan baris menu
disejajarkan dengan badan halaman. Di ponsel, menu dilipat menjadi tombol garis tiga di header dan terbuka
sebagai panel navigasi penuh di bawah header.

Tabel responden pada halaman SMD MMD bisa diurutkan: klik judul kolom untuk urutan naik, klik lagi untuk
urutan turun. Nilai yang belum ada tetap diletakkan di bawah.

## Keterangan sumber data di setiap panel

Tiap kartu menutup isinya dengan baris <b>📄 Sumber data: …</b> yang menyebut berkas Excel atau
spreadsheet asalnya beserta nama folder di Drive, supaya mudah ditelusuri saat ada angka yang perlu diperbaiki:

* contoh pada halaman SMD MMD: <code>KELENGKAPAN SMD.xlsx</code> (folder SMD MMD), berkas rekap tiap desa
  (<code>SUGIHWARAS SMD 2025 REKAP.xlsx</code>, <code>MALANG REKAP 2026.xlsx</code>, …);
* pada halaman RUK: <code>Copy of BAB IV Perencanaan Belanja 2027 SIP.xlsx</code> sheet <code>BAB IV</code>;
* pada halaman PKP: spreadsheet <code>PKP KLASTER 1_2026</code> (kolom 2 kegiatan sampai kolom 10 hasil kinerja);
* pada halaman Jadwal Promkes: kalender publik Google <code>dhellayaamanda2@gmail.com</code> (bukan berkas Excel).

Panel yang nama berkasnya dideteksi otomatis oleh <code>tools/sync.py</code> menambahkan frasa
<b>“terdeteksi: …”</b> berisi nama berkas yang benar-benar terbaca. Untuk mengubah keterangan itu,
sunting argumen <code>src=</code> pada <code>tools/build_pages.py</code> lalu jalankan
<code>python tools/build_pages.py</code>.

## Tombol "Sinkron sekarang" & waktu sinkron

Di header setiap halaman ada tombol **⟳ Sinkron sekarang** dengan keterangan *Terakhir sinkron: …*
(diambil dari `generated` pada `data/<menu>.json`). Tombol **Buka folder di Google Drive** tetap ada,
dipindah ke bawah judul halaman.

Tombol itu bekerja dengan cara berbeda sesuai tempat situs dibuka:

| Tempat dibuka | Yang terjadi saat tombol ditekan |
|---|---|
| **Lokal** (`python tools/serve.py`) | Server lokal menjalankan `tools/sync.py` lalu `tools/build_pages.py`; halaman menampilkan progres dan memuat ulang sendiri setelah selesai. |
| **Hosting Vercel** (dengan `api/sync.js`) | Memicu workflow GitHub Actions `sync.yml`, lalu statusnya dipantau; setelah Actions selesai hosting menayangkan data baru. Perlu variabel lingkungan `GITHUB_TOKEN` (wajib; classic token dengan scope `repo` + `workflow`, atau fine-grained dengan izin Actions: write) dan opsional `GITHUB_REPO` + `SYNC_SECRET`. `GITHUB_REPO` boleh dikosongkan karena otomatis diambil dari repo Vercel. Setelah menambah variabel, **Redeploy** agar berlaku. |
| Tanpa keduanya | Tombol menampilkan pesan: jalankan `python tools/sync.py --refresh` lalu muat ulang. |

Bila `SYNC_SECRET` diisi di hosting, halaman menanyakan kode sekali dan menyimpannya di browser.

## Struktur proyek

```
index.html                   beranda (10 kartu menu)
<slug>.html                  10 halaman menu (hasil tools/build_pages.py)
assets/logo-puskesmas.png    lambang UPTD Puskesmas Maospati (sumber: https://puskesmas-maospati.magetan.go.id/)
assets/style.css             tampilan Material pastel, header ponsel, dan tabel responsif
assets/app.js                kerangka bersama: menu, tombol Sinkron, pemuatan data, KPI, tabel, matriks
assets/pages/<slug>.js       ISI ringkasan tiap halaman (satu berkas per halaman -> mudah dirawat)
api/sync.js                  serverless function: tombol Sinkron saat di-hosting (pemicu Actions)
data/<slug>.json             hasil ekstraksi folder Drive / spreadsheet (dibuat tools/sync.py)
data/site.json               daftar menu + jumlah berkas per folder
tools/sync.py                baca Drive & spreadsheet -> analisa -> tulis data/*.json
tools/build_pages.py         rakit 11 berkas HTML dari satu kerangka
tools/serve.py               jalankan dashboard di komputer + endpoint /api/sync
tools/check_pages.py         uji statis: id yang dipakai skrip harus ada di HTML-nya
tools/uji_render.mjs         uji render tiap halaman + uji tombol Sinkron (butuh Node)
.github/workflows/sync.yml   sinkronisasi otomatis setiap hari (opsional)
.cache/                      simpanan sementara unduhan (tidak ikut di-commit)
```

## Menjalankan

```bash
pip install openpyxl
python tools/sync.py            # tarik & analisa data dari Drive  -> data/*.json
python tools/sync.py --refresh  # sama, tetapi unduh ulang berkas (abaikan cache .cache/dl)
python tools/build_pages.py     # (kalau struktur halaman berubah) -> *.html
python tools/serve.py           # buka http://127.0.0.1:8080
```

> `tools/sync.py` memakai cache `.cache/dl` agar cepat. Setelah mengubah berkas di Drive,
> pakai `--refresh` supaya berkas terbaru benar-benar diunduh.

Halaman membaca `data/*.json` lewat `fetch()`. Bila `fetch` diblokir (halaman dibuka langsung dengan
klik dua kali, bukan lewat web server), halaman otomatis memakai **data cadangan yang ditanam di berkas HTML**
saat build — jadi dashboard tetap tampil, hanya perlu `build_pages.py` ulang untuk memperbaruinya.
Untuk data yang selalu segar, jalankan lewat `tools/serve.py` atau taruh di hosting.

Uji cepat sebelum mengunggah:

```bash
python tools/check_pages.py     # id HTML <-> skrip
node   tools/uji_render.mjs     # 11 halaman harus "OK" semua (mode fetch)
UJI_MODE=inline node tools/uji_render.mjs   # uji juga data cadangan tertanam
```

Unggah publikasi: repo ini bisa langsung di-import ke Vercel (preset **Other / static**, tanpa build command)
atau dinyalakan lewat GitHub Pages.

## Cara membuat data "live"

Tiga tingkat, dari yang paling murah:

**A. Sinkron terjadwal (sudah tersedia di repo ini).**
Buka tab **Actions → Sinkron data Drive MPM → Run workflow** sekali secara manual (untuk memberi izin
tulis pada workflow), setelah itu jadwal harian 06:00 WIB (`.github/workflows/sync.yml`) menjalankan
`tools/sync.py` otomatis dan men-commit hasilnya → situs selalu menampilkan versi terbaru.
Tidak ada perubahan yang perlu dilakukan di Drive selain memastikan folder tetap dibagikan
*Anyone with the link → Viewer*. Keterlambatan maksimum 1 hari (ubah baris `cron:` bila ingin tiap jam).

**B. Live saat halaman dibuka (paling real-time).**
Konversi sheet kunci ke Google Sheets (di Drive: klik kanan → *Open with → Google Sheets* →
*File → Save as Google Sheets*), lalu halaman membaca CSV-nya langsung:

```js
// contoh: tambahkan di assets/pages/<slug>.js
const CSV = (id, tab) => `https://docs.google.com/spreadsheets/d/${id}/gviz/tq?tqx=out:csv&sheet=${tab}`;
const teks = await (await fetch(CSV(SHEET_ID, 'Rekap'))).text();
```

Syarat: spreadsheet dibagikan *Anyone with the link → Viewer*. Cara ini membuat dashboard berubah
begitu sheet disunting petugas — tanpa build ulang. Catatan: berkas `.xlsx` yang diunggah apa adanya
tidak bisa dibaca live; hanya Google Sheets native.

**C. Web App Apps Script.**
Kalau ada data yang perlu dijaga (mis. data pribadi kader), buat Web App Apps Script yang mengembalikan
JSON hanya untuk kolom aman, lalu halaman memanggil URL `/exec` tersebut.

## Saran perbaikan data (supaya ringkasan otomatis & akurat)

**Aturan umum**

1. **Satu berkas = satu jenis data**, satu sheet, **satu baris kepala tanpa sel gabungan (merge)**.
   Sel gabungan adalah penyebab utama kolom terbaca bergeser (contoh: sheet BAB IV pada berkas RUK).
2. **Nama kolom baku & konsisten** (huruf besar, tanpa spasi ganda), contoh: `TAHUN`, `DESA`, `KEGIATAN`, `STATUS`.
3. **Tahun 4 angka** di nama berkas (`... 2026 ...`) — dipakai dashboard untuk tren tahunan.
4. **Nama desa selalu lengkap & seragam**: `SUGIHWARAS` (bukan SGW), `TANJUNGSEPREH` (bukan TJ),
   `MAOSPATI` (bukan MPT). Satu ejaan berbeda = satu desa hilang dari grafik.
5. **Status berupa teks, bukan centang**: `ADA`/`BELUM`, `SUDAH`/`BELUM`, `AKTIF`/`TIDAK AKTIF`.
6. **Bersihkan duplikat dan berkas kunci** (`~$...docx`) — saat ini masih ada beberapa di folder SMD MMD.
7. **Jangan taruh data pribadi** (nama + alamat + no HP kader) di folder yang dibagikan publik;
   simpan di berkas terpisah yang tidak dibagikan, dashboard cukup menampilkan jumlahnya.

**Tambahan per halaman**

| Halaman | Berkas yang dipantau | Yang perlu ditambahkan |
|---|---|---|
| SMD MMD | `KELENGKAPAN SMD.xlsx`, semua `*REKAP*.xlsx` | satu baris `Jumlah Responden : N KK` di kepala tiap rekap (sudah ada); pastikan satu berkas = satu desa + satu tahun |
| Laporan Posyandu | `KELENGKAPAN LHK.xlsx` | kolom `STATUS` (ADA/BELUM) konsisten, bulan Januari–Desember diisi walau belum ada laporan |
| RUK | `Copy of BAB IV Perencanaan Belanja 2027 SIP.xlsx` | hilangkan sel gabungan; kolom: `KODE · BAGIAN · KEGIATAN · TUJUAN · SASARAN · TARGET · PJ · ANGGARAN` |
| PKP | spreadsheet `PKP KLASTER 1_2026` | isi kolom target sasaran (7) dan pencapaian (8) untuk 8 indikator yang masih kosong; samakan rumus agregat klaster dengan rata-rata baris indikator |
| Data Posyandu | `POSYANDU AKTIF.xlsx` | kolom `STATUS` (AKTIF/TIDAK AKTIF) per posyandu, bukan hanya angka 1/0 |
| Data Kader | `Data Kader .xlsx` | samakan jumlah rekap dengan daftar form (selisih sekarang 236 vs 241) |
| Kegiatan Dinkes | `KEGIATAN DINKES.xlsx` | tambah baris untuk setiap kegiatan DINKES baru + kolom `PIC` dan `LINK BUKTI` |
| SPJ BOK *(kosong)* | — | `REKAP-SPJ-BOK.xlsx`: `TAHUN · TRIWULAN · KEGIATAN · ANGGARAN · REALISASI · SISA · STATUS` |
| Dokumentasi *(kosong)* | — | foto per kegiatan; opsional `REKAP-DOKUMENTASI.xlsx`: `TANGGAL · KEGIATAN · LOKASI · JUMLAH FOTO · LINK` |

## Menambah / mengubah halaman

1. **Menu baru**: tambah entri di `FOLDERS` pada `tools/sync.py` (slug, nama, ID folder, subjudul, deskripsi)
   dan di `MENU` pada `assets/app.js`. Menu yang bukan folder Drive (seperti **PKP** dari spreadsheet dan
   **Jadwal Promkes** dari kalender) punya blok sendiri di `main()` pada `tools/sync.py`.
2. **Ringkasan**: tambah fungsi `analisa_<slug>()` di `tools/sync.py`, panggil di blok pemilihan analisa.
3. **Tampilan**: buat `assets/pages/<slug>.js` berisi `window.renderPage = (analisa, data) => {...}`
   (pakai bantuan `kpiCards()`, `barRows()`, `table()`, `matrixBox()` dari `assets/app.js`).
4. **Kartu halaman**: tambah entri di `PAGES` pada `tools/build_pages.py`, lalu jalankan
   `python tools/build_pages.py`.

## Data yang terbaca saat ini

* Sumber: 8 folder Drive, **68 berkas** (SMD MMD 45 · RUK 10 · Kegiatan Dinkes 7 · Data Posyandu 4 ·
  Laporan Posyandu 1 · Data Kader 1 · Dokumentasi 0 · SPJ BOK 0), ditambah spreadsheet PKP.
* PKP: 98 indikator dalam 9 klaster, rata-rata hasil kinerja **58,3%**, 44 indikator tercapai 100%,
  38 di bawah 50%, 4 belum punya data (sumber: spreadsheet `PKP KLASTER 1_2026`, sinkron 29 Oktober 2026).
* SMD/MMD: 24 kombinasi desa-tahun, 8 desa, **3.144 KK** responden, 80 judul indikator
  (instrumen 2023–2024 dan 2025–2026 berbeda, jadi tren jangka panjang perlu pemetaan indikator).
* Posyandu: 42 (semua aktif) · Kader: 236 rekap / 241 nama form.
* LHK: 15 dari 24 bulan berstatus ADA (2026 baru 3 bulan) · Kegiatan Dinkes: 1 kegiatan, 4 dari 6 bulan selesai ·
  RUK 2027: 114 kegiatan, 43 bagian, 108 punya penanggung jawab.