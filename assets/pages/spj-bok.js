/* SPJ BOK · berkas pertanggungjawaban BOK (folder ini masih kosong) */
window.renderPage = function(a, d){
  const files = (d && d.files) || [];
  set('kpis', kpiCards([
    { label: 'Berkas SPJ', value: files.length, sub: 'kwitansi, laporan, bukti bayar' },
    { label: 'Subfolder', value: (d && d.statistik.subfolder) || 0, sub: 'mis. per triwulan' },
    { label: 'Status', value: files.length ? 'Terisi' : 'Belum ada isi', sub: files.length ? 'siap ditampilkan' : 'folder masih kosong di Drive', small: true },
    { label: 'Sumber', value: 'Google Drive', sub: 'folder SPJ BOK', small: true },
  ]));

  if (!files.length){
    set('c-isi', `<div class="empty">
      <p style="margin:0 0 8px"><b>Folder SPJ BOK masih kosong.</b></p>
      <p style="margin:0">Setelah berkas SPJ diunggah, jalankan <code>python tools/sync.py</code>.
      Daftar berkas beserta tautannya akan otomatis tampil di halaman ini.</p>
    </div>`);
  }

  set('c-saran', `<ul class="tl">
    <li><b>Struktur yang disarankan:</b> <code>SPJ BOK/&lt;tahun&gt;/&lt;triwulan&gt;/</code> (mis. <code>2026/TW3/</code>).</li>
    <li><b>Penamaan berkas:</b> <code>SPJ-BOK-&lt;tahun&gt;-&lt;tribulan&gt;-&lt;jumlah&gt;.xlsx</code> agar mudah dilacak.</li>
    <li>Bila ingin ringkasan otomatis di dashboard, buat berkas <code>REKAP-SPJ-BOK.xlsx</code> berisi kolom:
        <code>tahun | triwulan | kegiatan | anggaran | realisasi | sisa | status</code> · dashboard akan menghitung
        persentase serapan per triwulan.</li>
    <li>Simpan bukti bayar/kwitansi dalam satu folder per triwulan supaya jumlah berkas per periode bisa ditampilkan.</li>
  </ul>`);
};
