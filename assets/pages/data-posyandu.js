/* Data Posyandu — daftar posyandu ILP */
window.renderPage = function(a){
  const k = a.kpi || {}, pos = a.posyandu || [], per = a.perDesa || [];
  set('kpis', kpiCards([
    { label: 'Posyandu', value: k.posyandu, sub: 'dari ' + (k.sumber || '—') },
    { label: 'Aktif', value: k.aktif + '/' + k.posyandu, sub: 'status pada berkas sumber' },
    { label: 'Desa / kelurahan', value: k.desa, sub: 'wilayah kerja UPTD' },
    { label: 'Rata-rata per desa', value: k.desa ? (k.posyandu / k.desa).toFixed(1) : '–', sub: 'posyandu / desa' },
  ]));

  set('c-desa', barRows(per.map(x => ({ label: x.desa, value: x.jumlah, note: x.jumlah + ' pos' }))));
  set('t-pos', table(
    [{ label: 'No', num: true }, { label: 'Desa/Kel' }, { label: 'Posyandu' },
     { label: 'Status', html: r => `<span class="pill ${r.aktif ? 'ok' : 'no'}">${r.aktif ? 'AKTIF' : 'TIDAK AKTIF'}</span>` }],
    pos.map((p, i) => ({ no: i + 1, desa: p.desa, pos: p.pos, aktif: p.aktif }))
  ));
  set('c-catatan', `<ul class="tl">
    <li>Sumber: <b>${esc(k.sumber || '—')}</b> pada folder Data Posyandu.</li>
    <li>Tambahkan kolom <code>STATUS</code> berisi <code>AKTIF</code>/<code>TIDAK AKTIF</code> agar perubahan status otomatis ikut tampil.</li>
    <li>Berkas LHK bulanan (docx) yang ada di subfolder tahun akan muncul di daftar isi folder di bawah.</li>
  </ul>`);
};
