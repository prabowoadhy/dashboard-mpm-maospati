/* Beranda — kartu 8 menu + ringkasan berkas */
window.renderPage = function(site){
  const totalBerkas = site.folders.reduce((a, f) => a + (f.jenis === 'kalender' ? 0 : f.berkas), 0);
  const aktif = site.folders.filter(f => f.berkas > 0).length;
  const kalender = site.folders.find(f => f.jenis === 'kalender');
  set('kpis', kpiCards([
    { label: 'Menu kegiatan', value: site.folders.length, sub: '8 folder Drive + 1 kalender Promkes' },
    { label: 'Berkas terindeks', value: fnum(totalBerkas), sub: 'terbaca dari 8 folder Drive' },
    { label: 'Folder berisi data', value: aktif + '/8', sub: 'folder kosong: ' + (site.folders.filter(f => f.jenis !== 'kalender' && !f.berkas).map(f => f.menu).join(', ') || '—') },
    { label: 'Agenda Promkes', value: kalender ? fnum(kalender.berkas) : '–', sub: kalender ? (kalender.keterangan || 'dari kalender publik Google') : 'kalender belum terbaca' },
  ]));
  set('cards', '<div class="grid k4">' + site.folders.map((f, i) => `
    <a class="card" href="${f.slug}.html" style="display:block;color:inherit">
      <div class="l muted" style="font-size:11px;text-transform:uppercase;letter-spacing:.4px">Menu ${i + 1}</div>
      <div style="font-size:16px;font-weight:650;margin:4px 0 3px">${esc(f.menu)}</div>
      <div class="muted" style="font-size:12px">${esc(f.subjudul)}</div>
      <div style="margin-top:9px;font-size:12px">
        ${f.jenis === 'kalender'
          ? `<span class="pill ok">${f.berkas} agenda</span> <span class="pill">Google Calendar</span>`
          : `<span class="pill ${f.berkas ? 'ok' : 'wr'}">${f.berkas} berkas</span> <span class="pill">${f.subfolder} subfolder</span>`}
      </div>
    </a>`).join('') + '</div>');
  set('catatan', `<ul class="tl">
    <li>Setiap menu di atas punya halaman sendiri (<code>smd-mmd.html</code>, <code>ruk.html</code>, <code>jadwal-promkes.html</code>, …)
      dan berkas data sendiri (<code>data/&lt;menu&gt;.json</code>) supaya mudah dirawat.</li>
    <li>Angka dihitung dari berkas <b>.xlsx</b> yang ada di folder Google Drive masing-masing kegiatan — bukan input manual.
      <b>Menu Jadwal Promkes</b> bersumber dari kalender publik Google.</li>
    <li>Pada tiap panel ada keterangan <b>Sumber data</b> yang menyebut nama berkas Excel-nya, supaya mudah dicek dan diperbaiki.</li>
    <li>Menambah berkas baru di Drive lalu menjalankan <code>python tools/sync.py</code> (atau tombol <b>Sinkron sekarang</b>) sudah cukup untuk memperbarui semua halaman.</li>
  </ul>`);
};
