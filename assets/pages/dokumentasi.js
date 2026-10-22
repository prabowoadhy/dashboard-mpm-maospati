/* Dokumentasi · galeri berkas dokumentasi kegiatan (folder ini masih kosong) */
window.renderPage = function(a, d){
  const files = (d && d.files) || [];
  set('kpis', kpiCards([
    { label: 'Berkas dokumentasi', value: files.length, sub: 'foto, laporan, atau berkas lain' },
    { label: 'Subfolder', value: (d && d.statistik.subfolder) || 0, sub: 'mis. per kegiatan / per bulan' },
    { label: 'Status', value: files.length ? 'Terisi' : 'Belum ada isi', sub: files.length ? 'siap ditampilkan' : 'folder masih kosong di Drive', small: true },
    { label: 'Sumber', value: 'Google Drive', sub: 'folder Dokumentasi', small: true },
  ]));

  if (!files.length){
    set('c-isi', `<div class="empty">
      <p style="margin:0 0 8px"><b>Folder Dokumentasi masih kosong.</b></p>
      <p style="margin:0">Setelah berkas/foto diunggah ke folder ini, jalankan <code>python tools/sync.py</code>.
      Daftar berkas akan otomatis muncul di halaman ini beserta tautannya ke Google Drive.</p>
    </div>`);
  } else {
    set('c-isi', (d.struktur ? '' : '') + '');
  }

  set('c-saran', `<ul class="tl">
    <li><b>Struktur yang disarankan:</b> <code>Dokumentasi/&lt;tahun&gt;/&lt;bulan atau nama kegiatan&gt;/</code> supaya mudah dicari.</li>
    <li><b>Penamaan berkas:</b> <code>KEGIATAN-TANGGAL-LOKASI.jpg</code> (contoh: <code>posyandu-balita-12-03-2026-gulun.jpg</code>).</li>
    <li>Untuk tampil sebagai galeri foto di dashboard, unggah foto ke Drive dengan izin <i>anyone with the link</i>; tautan tiap foto otomatis bisa dibuka dari halaman ini.</li>
    <li>Bila ingin ada ringkasan per bulan, tambahkan satu berkas <code>REKAP-DOKUMENTASI.xlsx</code> berisi kolom: <code>tanggal | kegiatan | lokasi | jumlah_foto | link</code>.</li>
  </ul>`);
};
