/* RUK · Rencana Usulan Kegiatan */
window.renderPage = function(a){
  const k = a.kpi || {}, keg = a.kegiatan || [], per = a.perBagian || [];
  const bagian = [...new Set(keg.map(x => x.bagian).filter(Boolean))].sort();
  set('kpis', kpiCards([
    { label: 'Kegiatan diusulkan', value: k.kegiatan, sub: 'baris kegiatan pada BAB IV' },
    { label: 'Bagian / unit', value: k.bagian, sub: 'pelayanan & program' },
    { label: 'Punya penanggung jawab', value: k.denganPJ + '/' + k.kegiatan, sub: 'baris dengan PJ terisi' },
    { label: 'Sumber berkas', value: 'xlsx', sub: k.sumber || '-', small: true },
  ]));

  set('c-bagian', barRows(per.slice(0, 14).map(x => ({ label: x.bagian, value: x.jumlah, note: x.jumlah + ' keg' }))));

  const sel = el('f-bagian'), q = el('q-ruk');
  sel.innerHTML = '<option value="">Semua bagian</option>' + bagian.map(b => `<option>${esc(b)}</option>`).join('');
  function draw(){
    const term = (q.value || '').toLowerCase();
    const rows = keg.filter(x => (!sel.value || x.bagian === sel.value) &&
      (!term || (x.kegiatan + ' ' + x.tujuan + ' ' + x.sasaran + ' ' + x.pj).toLowerCase().includes(term)));
    set('c-info', rows.length + ' dari ' + keg.length + ' kegiatan ditampilkan');
    set('t-ruk', table(
      [{ label: 'Bagian' }, { label: 'Kegiatan' }, { label: 'Tujuan' }, { label: 'Sasaran' }, { label: 'Target' }, { label: 'PJ' }],
      rows.map(x => ({ bagian: x.bagian, kegiatan: x.kegiatan, tujuan: x.tujuan, sasaran: x.sasaran, target: x.target, pj: x.pj }))
    ));
  }
  sel.onchange = draw; q.oninput = draw; draw();

  set('c-catatan', `<ul class="tl">
    <li>Data diambil dari berkas <b>${esc(k.sumber || 'BAB IV')}</b> pada folder RUK.</li>
    <li>Baris yang belum punya penanggung jawab: <b>${k.kegiatan - k.denganPJ}</b> kegiatan · lengkapi di berkas aslinya.</li>
    <li>Supaya terbaca rapi oleh dashboard, usulkan format kolom: <code>Kode | Bagian | Kegiatan | Tujuan | Sasaran | Target | PJ | Anggaran</code> dalam satu baris kepala (tanpa sel gabungan).</li>
  </ul>`);
};
