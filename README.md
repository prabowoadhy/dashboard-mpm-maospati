# Dashboard MPM — UPTD Puskesmas Maospati

Prototipe dashboard dari data yang sudah diunggah di Google Sites/Drive **MPM Maospati**
(<https://sites.google.com/view/mpmmaospati/home>). Isi folder:

| Berkas / folder | Keterangan |
|---|---|
| `index.html` | Dashboard jadi (satu berkas, tanpa dependensi). Buka langsung di browser atau unggah ke Vercel. |
| `data/dashboard_data.json` | Hasil ekstraksi angka dari semua berkas `.xlsx` Drive — sumber semua angka di dashboard. |
| `tools/sync_from_drive.py` | Membaca ulang struktur folder Drive + mengekstrak angka dari `.xlsx` → `data/dashboard_data.json`. |
| `tools/build_dashboard.py` | Merakit `index.html` dari `data/dashboard_data.json`. |
| `apps-script/Code.gs` | Jembatan Google Sheets → JSON (kalau data ingin dibaca live, bukan di-build ulang). |
| `preview-*.png` | Tangkapan layar tiap tab. |

## 1. Cara pakai cepat

```bash
pip install openpyxl
python tools/sync_from_drive.py     # tarik ulang data dari Drive (butuh akses link publik)
python tools/build_dashboard.py     # rakit ulang index.html
```

Buka `index.html` dengan browser. Kalau ingin online: buat repo GitHub → import ke Vercel →
framework preset **Other** (static), tanpa build command. Selesai, tanpa biaya.

## 2. Peta data yang ditemukan

8 folder utama, 16 subfolder, 65 berkas. Angka yang berhasil dibaca:

- **8 desa/kelurahan**, **42 posyandu ILP**, **236 kader** (rekap) — form pendataan kader berisi **233 nama**.
- **SMD/MMD 2023–2026**, 23 kombinasi desa-tahun: responden total **2.944 KK** (2023: 812 · 2024: 905 · 2025: 1.016 · 2026: 211).
- Instrumen 2023–2024: **52 indikator tanpa klaster**; 2025–2026: **61 baris klaster 1–4**.
- **LHK bulanan**: 2025 lengkap 12/12, 2026 baru 3/12 (April kosong, Mei–Des belum).
- **Kegiatan DINKES**: 1 kegiatan tercatat (Kader Buaian, Juni–September selesai, Okt–Nov belum).
- **RUK 2027**: BAB IV perencanaan belanja, RUK promkes, rekap survey kebutuhan.
- **DOKUMENTASI** dan **SPJ BOK**: folder masih kosong.

## 3. Temuan yang perlu dibereskan

1. **Duplikat berkas** — mis. `HASIL REKAP KRATON 2023.xlsx`, `HASIL REKAP SMD 2023.xlsx`,
   `HASIL REKAP MPT 2023.xlsx` muncul di folder 2023 *dan* 2024 (ID berbeda = salinan terpisah).
2. **Berkas sampah** — `~$TODE PEMECAHAN MASALAH done.docx` (file lock Word) ikut terunggah.
3. **Penamaan tidak konsisten** — `HASIL REKAP SGW 2023` vs `SUGIHWARAS SMD 2025 REKAP` vs
   `REKAP SMD KRATON 2025`; singkatan MPT/SGW/TJ tidak seragam dengan nama desa lengkap.
4. **Angka kader tidak sinkron** — rekap 236 vs daftar nama 233; per desa berbeda jauh
   (Malang 15 vs 20, Maospati 47 vs 32, Kraton 42 vs 44).
5. **Instrumen berubah di tengah jalan** — tren 5 tahun belum bisa dibandingkan langsung
   karena 2023–2024 memakai 52 indikator, 2025–2026 memakai 61 baris berklaster.
6. **Format berkas campur** — `.doc` (lama) + `.docx` + `.xlsx` + `.pptx` + `.pdf`; berkas
   Excel diunggah sebagai **file**, bukan Google Sheets, sehingga tidak bisa dibaca live
   oleh dashboard (harus di-build ulang atau dikonversi).
7. **Arah indikator belum ditandai** — mis. "keluarga ada yang menderita TB" rendah itu *baik*,
   tapi terbaca merah di heatmap. Perlu kolom `arah` (positif/negatif) di data master.
8. **Cakupan belum merata** — 2026 baru 2 desa (Malang, Tanjungsepreh); SEMPOL 2025 tidak
   ada di folder REKAP SMD (ada sebagai `SMD SEMPOL 2025.xlsx`).

## 4. Struktur dashboard yang diusulkan

```
Ringkasan   ─ KPI: 8 desa · 42 posyandu · 236 kader · 2.944 KK responden · rata-rata capaian
            ─ Responden SMD per desa & tahun · status kelengkapan dokumen
            ─ Kebutuhan & harapan masyarakat (top 12) · temuan kualitas data
SMD / MMD   ─ filter desa + tahun · capaian per klaster · 10 indikator terendah
            ─ heatmap indikator × desa · tabel detail + selisih vs tahun sebelumnya
Posyandu & Kader
            ─ posyandu aktif per desa · kader rekap vs daftar nama · tabel per posyandu
Kelengkapan & Kegiatan
            ─ matriks LHK bulan × tahun · checklist rekap/analisa SMD × desa × tahun
            ─ kegiatan DINKES per bulan
Dokumen & Berkas
            ─ inventaris 65 berkas + pencarian + filter folder
```

Tiga jalur pengembangan (pilih sesuai kebutuhan):

| Jalur | Cara kerja | Update data | Cocok untuk |
|---|---|---|---|
| **A. Statis (yang sudah jadi)** | `index.html` + JSON hasil ekstraksi → GitHub → Vercel | jalankan 2 skrip di `tools/` lalu push | tampilan publik, belum perlu input langsung |
| **B. Sheets live** | Data dipindah ke satu Google Sheets "MASTER MPM" → published CSV / `gviz` / Apps Script → dashboard fetch saat dibuka | langsung begitu sheet disunting | pemakaian harian, petugas mengisi sheet |
| **C. Penuh (opsional)** | + Supabase/Neon gratis untuk tabel `smd`, `kader`, `lhk`, `kegiatan` + form input & login | realtime | kalau butuh input dari HP & riwayat perubahan |

Jalur B adalah rekomendasi berikutnya: paling murah, paling sedikit koding, dan Google Sites
bisa tetap dipakai sebagai halaman pengantar sambil menyematkan (embed) dashboard Vercel.

## 5. Langkah lanjutan yang disarankan

1. Rapikan struktur Drive: satu nama desa satu ejaan, hapus duplikat & berkas `~$`, satu berkas
   per desa per tahun dengan pola `SMD-<DESA>-<TAHUN>.xlsx`.
2. Buat satu spreadsheet **MASTER MPM** (tab: `SMD_REKAP`, `KADER`, `POSYANDU`, `LHK`, `KEGIATAN`,
   `RUK`) — semua berkas per-desa dimigrasi ke sini; kolomnya sudah disiapkan di `apps-script/Code.gs`.
3. Isi kolom `arah` (positif/negatif) untuk tiap indikator agar warna dashboard tidak menyesatkan.
4. Deploy `index.html` ke Vercel (atau Netlify/Cloudflare Pages — semuanya gratis), lalu sematkan
   tautannya di halaman Google Sites.
5. Tambahkan menu SPJ BOK dan DOKUMENTASI begitu folder tersebut diisi (galeri foto kegiatan bisa
   langsung dibaca dari folder Drive yang di-share).
