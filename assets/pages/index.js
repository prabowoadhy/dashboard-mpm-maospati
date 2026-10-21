/* Beranda — kartu 8 menu + ringkasan berkas */
window.renderPage = function(site){
  const totalBerkas = site.folders.reduce((a, f) => a + f.berkas, 0);
  const aktif = site.folders.filter(f => f.berkas > 0).length;
  set('kpis', kpiCards([
    { label: 'Menu kegiatan', value: site.folders.length, sub: 'sesuai folder Google Drive' },
    { label: 'Berkas terindeks', value: fnum(totalBerkas), sub: 'terbaca dari 8 folder' },
    { label: 'Folder berisi data', value: aktif + '/8', sub: 'folder kosong: ' + (site.folders.filter(f => !f.berkas).map(f => f.menu).join(', ') || '—') },
    { label: 'Sinkron terakhir', value: site.generated, sub: 'dijalankan oleh tools/sync.py', raw: false },
  ]));
  set('cards', '<div class="grid k4">' + site.folders.map((f, i) => `
    <a class="card" href="${f.slug}.html" style="display:block;color:inherit">
      <div class="l muted" style="font-size:11px;text-transform:uppercase;letter-spacing:.4px">Menu ${i + 1}</div>
      <div style="font-size:16px;font-weight:650;margin:4px 0 3px">${esc(f.menu)}</div>
      <div class="muted" style="font-size:12px">${esc(f.subjudul)}</div>
      <div style="margin-top:9px;font-size:12px">
        <span class="pill ${f.berkas ? 'ok' : 'wr'}">${f.berkas} berkas</span>
        <span class="pill">${f.subfolder} subfolder</span>
      </div>
    </a>`).join('') + '</div>');
  set('catatan', `<ul class="tl">
    <li>Setiap menu di atas punya halaman sendiri (<code>smd-mmd.html</code>, <code>ruk.html</code>, …) dan berkas data sendiri (<code>data/&lt;menu&gt;.json</code>) supaya mudah dirawat.</li>
    <li>Angka dihitung dari berkas <b>.xlsx</b> yang ada di folder Google Drive masing-masing kegiatan — bukan input manual.</li>
    <li>Menambah berkas baru di Drive lalu menjalankan <code>python tools/sync.py</code> sudah cukup untuk memperbarui semua halaman.</li>
    <li>Supaya ikut memperbarui otomatis, aktifkan GitHub Actions (<code>.github/workflows/sync.yml</code>) — dijelaskan di README.</li>
  </ul>`);
};
