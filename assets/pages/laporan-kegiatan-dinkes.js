/* Laporan Kegiatan Dinkes · matriks kegiatan per bulan */
window.renderPage = function(a){
  const k = a.kpi || {}, keg = a.kegiatan || [], nama = a.namaKegiatan || [], bulan = a.bulan || [];
  set('kpis', kpiCards([
    { label: 'Jenis kegiatan', value: k.kegiatan, sub: 'tercatat di ' + (k.sumber || '-') },
    { label: 'Bulan selesai', value: k.sudah + '/' + k.total, sub: 'status DIKERJAKAN = SUDAH' },
    { label: 'Progres', value: k.total ? fpct(100 * k.sudah / k.total) : '–', sub: 'baris berstatus sudah' },
    { label: 'Berkas pendukung', value: (a.berkas || 0), sub: 'kwitansi, surat tugas, dll' },
  ]));

  set('c-progres', barRows(nama.map(n => {
    const rows = keg.filter(x => x.kegiatan === n), s = rows.filter(x => x.sudah).length;
    return { label: n, value: s, max: rows.length || 12, note: s + '/' + rows.length + ' bulan' };
  })));

  const rows = nama.map(n => ({
    label: n,
    cells: bulan.map(b => {
      const x = keg.find(y => y.kegiatan === n && y.bulan === b);
      if (!x) return { v: '' , title: n + ' ' + b + ': tidak dijadwalkan' };
      return x.sudah
        ? { v: 'sudah', html: '<span class="pill ok">sudah</span>', title: n + ' ' + b + ': sudah dikerjakan' }
        : { v: 'belum', html: '<span class="pill no">belum</span>', title: n + ' ' + b + ': belum dikerjakan' };
    })
  }));
  set('c-matriks', '<div class="scroll">' + matrixBox(bulan.map(b => b.slice(0, 3)), rows, { labelWidth: 'minmax(150px,240px)' }) + '</div>');

  const belum = keg.filter(x => !x.sudah && x.belum);
  set('c-belum', belum.length ? '<ul class="tl">' + belum.map(x => `<li><b>${esc(x.kegiatan)}</b> · ${esc(x.bulan)}</li>`).join('') + '</ul>'
    : '<p class="muted">Semua kegiatan tercatat sudah dikerjakan.</p>');

  set('t-keg', table([{ label: 'Kegiatan' }, { label: 'Bulan' }, { label: 'Status', html: r =>
      `<span class="pill ${r.sudah ? 'ok' : 'no'}">${r.sudah ? 'SUDAH' : r.belum ? 'BELUM' : 'kosong'}</span>` }],
    keg.map(x => ({ kegiatan: x.kegiatan, bulan: x.bulan, sudah: x.sudah, belum: x.belum }))));
};
