/* Beranda · kartu 8 menu + ringkasan berkas */
window.renderPage = function(site){
  const totalBerkas = site.folders.reduce((a, f) => a + (f.jenis === 'kalender' ? 0 : f.berkas), 0);
  const aktif = site.folders.filter(f => f.berkas > 0).length;
  const kalender = site.folders.find(f => f.jenis === 'kalender');
  set('kpis', kpiCards([
    { label: 'Menu kegiatan', value: site.folders.length, sub: '8 folder Drive + 1 kalender Promkes' },
    { label: 'Berkas terindeks', value: fnum(totalBerkas), sub: 'terbaca dari 8 folder Drive' },
    { label: 'Folder berisi data', value: aktif + '/8', sub: 'folder kosong: ' + (site.folders.filter(f => f.jenis !== 'kalender' && !f.berkas).map(f => f.menu).join(', ') || '-') },
    { label: 'Agenda Promkes', value: kalender ? fnum(kalender.berkas) : '–', sub: kalender ? (kalender.keterangan || 'dari kalender publik Google') : 'kalender belum terbaca' },
  ]));
  set('cards', '<div class="dir">' + site.folders.map((f, i) => {
    const meta = f.jenis === 'kalender'
      ? `${fnum(f.berkas)} agenda &middot; Google Calendar`
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
      <b>Menu Jadwal Promkes</b> bersumber dari kalender publik Google.</li>
    <li>Pada tiap panel ada keterangan <b>Sumber data</b> yang menyebut nama berkas Excel-nya, supaya mudah dicek dan diperbaiki.</li>
    <li>Menambah berkas baru di Drive lalu menjalankan <code>python tools/sync.py</code> (atau tombol <b>Sinkronkan data</b>) sudah cukup untuk memperbarui semua halaman.</li>
  </ul>`);
};
