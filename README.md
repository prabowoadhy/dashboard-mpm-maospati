# Dashboard MPM Maospati

Dashboard delapan menu kegiatan **Manajemen Pemberdayaan Masyarakat — UPTD Puskesmas Maospati**,
dibangun dari berkas yang sudah ada di Google Drive (sumber: <https://sites.google.com/view/mpmmaospati/home>).

Delapan menu mengikuti delapan folder Drive; tiap menu punya **halaman sendiri** dan **berkas data sendiri**
supaya mudah dirawat:

| # | Menu | Halaman | Data | Isi ringkasan |
|---|---|---|---|---|
| 1 | SMD MMD | `smd-mmd.html` | `data/smd-mmd.json` | responden per desa & tahun, capaian per klaster, heatmap indikator × desa, kelengkapan rekap & analisa, kebutuhan/harapan warga, berkas analisa |
| 2 | Laporan Posyandu | `laporan-posyandu.html` | `data/laporan-posyandu.json` | matriks kelengkapan LHK bulan × tahun, progres per tahun, sisa yang belum |
| 3 | RUK | `ruk.html` | `data/ruk.json` | jumlah kegiatan per bagian, daftar kegiatan + tujuan/sasaran/target/PJ (dari BAB IV) |
| 4 | Dokumentasi | `dokumentasi.html` | `data/dokumentasi.json` | daftar berkas/foto + saran struktur (folder masih kosong) |
| 5 | Data Posyandu | `data-posyandu.html` | `data/data-posyandu.json` | posyandu per desa, status aktif, tabel lengkap |
| 6 | Data Kader | `data-kader.html` | `data/data-kader.json` | kader per desa/posyandu, selisih rekap vs form (**tanpa data pribadi**) |
| 7 | SPJ BOK | `spj-bok.html` | `data/spj-bok.json` | daftar berkas SPJ + saran format rekap serapan |
| 8 | Laporan Kegiatan Dinkes | `laporan-kegiatan-dinkes.html` | `data/laporan-kegiatan-dinkes.json` | matriks kegiatan × bulan, progres, berkas pendukung |

Beranda `index.html` menampilkan 8 kartu menu + jumlah berkas tiap folder.
Setiap halaman punya tombol **menuju folder Google Drive** dan daftar isi folder (berkas & subfolder)
yang bisa diklik untuk membuka berkas aslinya.

## Struktur proyek

```
index.html                   beranda (8 kartu menu)
<slug>.html                  8 halaman menu (hasil tools/build_pages.py)
assets/style.css             tampilan (tema terang minimalis, ikut mode gelap sistem)
assets/app.js                kerangka bersama: menu, pemuatan data, KPI, tabel, matriks, daftar berkas
assets/pages/<slug>.js       ISI ringkasan tiap halaman (satu berkas per halaman -> mudah dirawat)
data/<slug>.json             hasil ekstraksi berkas dari Drive (dibuat tools/sync.py)
data/site.json               daftar menu + jumlah berkas per folder
tools/sync.py                baca Drive -> analisa .xlsx -> tulis data/*.json
tools/build_pages.py         rakit 9 berkas HTML dari satu kerangka
tools/serve.py               jalankan dashboard di komputer sendiri
tools/check_pages.py         uji statis: id yang dipakai skrip harus ada di HTML-nya
tools/uji_render.mjs         uji render tiap halaman di DOM tiruan dengan data asli (butuh Node)
.github/workflows/sync.yml   sinkronisasi otomatis setiap hari (opsional)
.cache/                      simpanan sementara unduhan (tidak ikut di-commit)
```

## Menjalankan

```bash
pip install openpyxl
python tools/sync.py            # tarik & analisa data dari Drive  -> data/*.json
python tools/build_pages.py     # (kalau struktur halaman berubah) -> *.html
python tools/serve.py           # buka http://127.0.0.1:8080
```

Halaman membaca `data/*.json` lewat `fetch()`, jadi **harus dibuka via `python tools/serve.py`**
(bukan klik dua kali berkas HTML).

Uji cepat sebelum mengunggah:

```bash
python tools/check_pages.py     # id HTML <-> skrip
node   tools/uji_render.mjs     # 9 halaman harus "OK" semua
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
| Data Posyandu | `POSYANDU AKTIF.xlsx` | kolom `STATUS` (AKTIF/TIDAK AKTIF) per posyandu, bukan hanya angka 1/0 |
| Data Kader | `Data Kader .xlsx` | samakan jumlah rekap dengan daftar form (selisih sekarang 236 vs 241) |
| Kegiatan Dinkes | `KEGIATAN DINKES.xlsx` | tambah baris untuk setiap kegiatan DINKES baru + kolom `PIC` dan `LINK BUKTI` |
| SPJ BOK *(kosong)* | — | `REKAP-SPJ-BOK.xlsx`: `TAHUN · TRIWULAN · KEGIATAN · ANGGARAN · REALISASI · SISA · STATUS` |
| Dokumentasi *(kosong)* | — | foto per kegiatan; opsional `REKAP-DOKUMENTASI.xlsx`: `TANGGAL · KEGIATAN · LOKASI · JUMLAH FOTO · LINK` |

## Menambah / mengubah halaman

1. **Menu baru**: tambah entri di `FOLDERS` pada `tools/sync.py` (slug, nama, ID folder, subjudul, deskripsi)
   dan di `MENU` pada `assets/app.js`.
2. **Ringkasan**: tambah fungsi `analisa_<slug>()` di `tools/sync.py`, panggil di blok pemilihan analisa.
3. **Tampilan**: buat `assets/pages/<slug>.js` berisi `window.renderPage = (analisa, data) => {...}`
   (pakai bantuan `kpiCards()`, `barRows()`, `table()`, `matrixBox()` dari `assets/app.js`).
4. **Kartu halaman**: tambah entri di `PAGES` pada `tools/build_pages.py`, lalu jalankan
   `python tools/build_pages.py`.

## Data yang terbaca saat ini

* Sumber: 8 folder Drive, **65 berkas** (SMD MMD 43 · RUK 10 · Kegiatan Dinkes 7 · Data Posyandu 4 ·
  Laporan Posyandu 1 · Data Kader 1 · Dokumentasi 0 · SPJ BOK 0).
* SMD/MMD: 24 kombinasi desa-tahun, 8 desa, **3.144 KK** responden, 80 judul indikator
  (instrumen 2023–2024 dan 2025–2026 berbeda, jadi tren jangka panjang perlu pemetaan indikator).
* Posyandu: 42 (semua aktif) · Kader: 236 rekap / 241 nama form.
* LHK: 15 dari 24 bulan berstatus ADA (2026 baru 3 bulan) · Kegiatan Dinkes: 1 kegiatan, 4 dari 6 bulan selesai ·
  RUK 2027: 114 kegiatan, 43 bagian, 108 punya penanggung jawab.