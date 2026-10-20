/**
 * Code.gs — jembatan data Google Sheets → dashboard (API JSON sederhana).
 * Dipakai kalau berkas sudah dikonversi jadi Google Sheets (native) supaya dashboard
 * selalu membaca data terbaru tanpa build ulang.
 *
 * Langkah:
 *  1. Buat Spreadsheet "MASTER MPM" berisi satu tab per kebutuhan:
 *     - SMD_REKAP  : kolom: tahun, desa, klaster, indikator, ya, tidak, lainnya
 *     - KADER      : kolom: desa, posyandu, nama_kader, jenis, pos
 *     - POSYANDU   : kolom: desa, posyandu, status
 *     - LHK        : kolom: tahun, bulan, status  (ADA/BELUM)
 *     - KEGIATAN   : kolom: kegiatan, bulan, status
 *  2. Extensions > Apps Script, tempel berkas ini, simpan.
 *  3. Deploy > New deployment > Web app > Execute as: Me, Who has access: Anyone.
 *     Salin URL /exec.
 *  4. Di dashboard (index.html) ganti pemanggilan data menjadi:
 *     fetch(SHEET_API + "?fn=smd").then(r => r.json())
 *
 * Catatan: hasil deploy bisa juga di-"publish to web" dan di-embed di Google Sites.
 */
const SHEET_ID = 'GANTI_DENGAN_ID_SPREADSHEET_MASTER';

function doGet(e) {
  const fn = (e && e.parameter && e.parameter.fn) || 'all';
  const out = {
    smd: fn === 'all' || fn === 'smd' ? read('SMD_REKAP') : undefined,
    kader: fn === 'all' || fn === 'kader' ? read('KADER') : undefined,
    posyandu: fn === 'all' || fn === 'posyandu' ? read('POSYANDU') : undefined,
    lhk: fn === 'all' || fn === 'lhk' ? read('LHK') : undefined,
    kegiatan: fn === 'all' || fn === 'kegiatan' ? read('KEGIATAN') : undefined,
    generated: new Date().toISOString()
  };
  return ContentService
    .createTextOutput(JSON.stringify(out))
    .setMimeType(ContentService.MimeType.JSON);
}

function read(name) {
  const sh = SpreadsheetApp.openById(SHEET_ID).getSheetByName(name);
  if (!sh) return [];
  const v = sh.getDataRange().getValues();
  const head = v.shift().map(h => String(h).trim().toLowerCase().replace(/\s+/g, '_'));
  return v.filter(r => r.join('') !== '').map(r => {
    const o = {};
    head.forEach((h, i) => o[h] = r[i]);
    return o;
  });
}
