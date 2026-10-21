/* Laporan Posyandu — kelengkapan LHK bulanan */
window.renderPage = function(a){
  const k = a.kpi || {}, bulan = a.bulan || [];
  const tahun = k.tahun || [];
  set('kpis', kpiCards([
    { label: 'Laporan terkumpul', value: k.terkumpul + '/' + k.total, sub: 'bulan berstatus ADA (KELENGKAPAN LHK.xlsx)' },
    { label: 'Kelengkapan', value: fpct(k.total ? 100 * k.terkumpul / k.total : null), sub: 'semua tahun tercatat' },
    { label: 'Tahun terakhir', value: k.tahunTerakhir || '–', sub: 'bulan ADA: ' + k.bulanIni + '/12' },
    { label: 'Berkas laporan', value: (a.berkasLaporan || []).length, sub: 'docx/xlsx/pdf di folder ini' },
  ]));

  const perTahun = {};
  tahun.forEach(t => {
    const rows = (a.lhk || []).filter(x => x.tahun === t);
    perTahun[t] = { ada: rows.filter(x => x.ada).length, belum: rows.filter(x => x.belum).length, kosong: rows.filter(x => !x.ada && !x.belum).length, total: rows.length };
  });
  set('c-perTahun', barRows(tahun.map((t, i) => ({
    label: 'Tahun ' + t, value: perTahun[t].ada, max: perTahun[t].total || 12, color: COL[i % COL.length],
    note: perTahun[t].ada + '/' + perTahun[t].total + ' bulan'
  }))));

  const rows = bulan.map(b => ({
    label: b,
    cells: tahun.map(t => {
      const x = (a.lhk || []).find(y => y.tahun === t && y.bulan === b);
      if (!x) return { v: '' };
      if (x.ada) return { v: 'ADA', html: '<span class="pill ok">ADA</span>', color: null, title: `${t} ${b}: laporan ada` };
      if (x.belum) return { v: 'BELUM', html: '<span class="pill no">BELUM</span>', color: null, title: `${t} ${b}: belum ada laporan` };
      return { v: 'kosong', html: '<span class="pill wr">kosong</span>', color: null, title: `${t} ${b}: belum ditandai` };
    })
  }));
  set('c-matriks', matrixBox(tahun.map(String), rows, { labelWidth: '120px' }));
  set('c-sisa', '<ul class="tl">' + Object.keys(perTahun).map(t => {
    const p = perTahun[t];
    return `<li><b>${t}</b> — terkumpul ${p.ada}, belum ${p.belum}${p.kosong ? ', tanpa status ' + p.kosong : ''}.</li>`;
  }).join('') + '</ul>');

  const berkas = a.berkasLaporan || [];
  set('c-berkas', berkas.length ? berkas.map(f => `<div class="file"><span class="ext">${esc((f.name.split('.').pop() || '').toLowerCase())}</span>
      <a class="nm" href="${f.url}" target="_blank" rel="noopener">${esc(f.name)}</a><span class="mod">${esc(f.modified || '')}</span></div>`).join('')
    : '<p class="muted">Belum ada berkas laporan di folder ini.</p>');
};
