/* Beranda · kartu menu + ringkasan berkas */
window.renderPage = function(site){
  const drive = site.folders.filter(f => !f.jenis);
  const totalBerkas = drive.reduce((a, f) => a + f.berkas, 0);
  const aktif = drive.filter(f => f.berkas > 0).length;
  const kosong = drive.filter(f => !f.berkas).map(f => f.menu).join(', ') || '-';
  const kalender = site.folders.find(f => f.jenis === 'kalender');
  set('kpis', kpiCards([
    { label: 'Menu kegiatan', value: site.folders.length, sub: '8 folder Drive + PKP (spreadsheet) + kalender Promkes' },
    { label: 'Berkas terindeks', value: fnum(totalBerkas), sub: `terbaca dari ${fnum(drive.length)} folder Drive` },
    { label: 'Folder berisi data', value: aktif + '/' + drive.length, sub: 'folder kosong: ' + kosong },
    { label: 'Agenda Promkes', value: kalender ? fnum(kalender.berkas) : '–', sub: kalender ? (kalender.keterangan || 'dari kalender publik Google') : 'kalender belum terbaca' },
  ]));
  set('cards', '<div class="dir">' + site.folders.map((f, i) => {
    const meta = f.jenis === 'kalender'
      ? `${fnum(f.berkas)} agenda &middot; Google Calendar`
      : f.jenis === 'sheet'
        ? `${fnum(f.indikator)} indikator &middot; Google Sheets`
        : f.berkas
          ? `${fnum(f.berkas)} berkas &middot; ${fnum(f.subfolder)} subfolder`
          : `<span class="pill wr">0 berkas</span> ${fnum(f.subfolder)} subfolder`;
    return `<a class="dirrow" href="${f.slug}.html">
      <span class="no">${String(i + 1).padStart(2, '0')}</span>
      <span class="ti">${esc(f.menu)}<span class="sub">${esc(f.subjudul)}</span></span>
      <span class="meta">${meta}</span>
    </a>`;
  }).join('') + '</div>');
  set('catatan', `<ul class="tl">
    <li>Setiap menu di atas punya halaman sendiri (<code>smd-mmd.html</code>, <code>ruk.html</code>, <code>jadwal-promkes.html</code>, …)
      dan berkas data sendiri (<code>data/&lt;menu&gt;.json</code>) supaya mudah dirawat.</li>
    <li>Angka dihitung dari berkas <b>.xlsx</b> yang ada di folder Google Drive masing-masing kegiatan · bukan input manual.
      <b>Menu PKP</b> bersumber dari spreadsheet Google, <b>menu Jadwal Promkes</b> dari kalender publik Google.</li>
    <li>Pada tiap panel ada keterangan <b>Sumber data</b> yang menyebut nama berkas Excel-nya, supaya mudah dicek dan diperbaiki.</li>
    <li>Menambah berkas baru di Drive lalu menjalankan <code>python tools/sync.py</code> (atau tombol <b>Sinkronkan data</b>) sudah cukup untuk memperbarui semua halaman.</li>
  </ul>`);
};
