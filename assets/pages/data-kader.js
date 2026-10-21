/* Data Kader — rekap jumlah kader (tanpa data pribadi) */
window.renderPage = function(a){
  const k = a.kpi || {}, perPos = a.perPos || [], perDesa = a.perDesa || [], jenis = a.jenis || [];
  set('kpis', kpiCards([
    { label: 'Total kader (rekap)', value: fnum(k.total), sub: 'jumlah resmi per posyandu' },
    { label: 'Kader terdaftar (form)', value: fnum(k.daftarNama), sub: 'baris pada form pendataan' },
    { label: 'Posyandu', value: k.posyandu, sub: 'yang punya kader' },
    { label: 'Rata-rata per posyandu', value: k.rataPerPos, sub: 'kader / posyandu' },
  ]));

  const selisih = (k.daftarNama || 0) - (k.total || 0);
  set('c-selisih', `<ul class="tl">
    <li>Rekap posyandu <b>${fnum(k.total)}</b> kader, daftar form <b>${fnum(k.daftarNama)}</b> nama — selisih <b>${selisih > 0 ? '+' : ''}${fnum(selisih)}</b>.</li>
    <li>Selisih biasanya karena kader pindah/dobel input. Rapikan di <b>${esc(k.sumber || 'berkas sumber')}</b> agar angka dashboard seragam.</li>
    <li>${esc(a.privasi || '')}</li>
  </ul>`);

  set('c-desa', barRows(perDesa.map(x => ({ label: x.desa, value: x.kader, note: x.kader + ' / ' + x.nama }))));
  set('c-jenis', jenis.length ? barRows(jenis.map(x => ({ label: x.jenis, value: x.jumlah }))) :
    '<p class="muted">Kolom jenis kader belum ada di berkas sumber.</p>');

  set('t-kader', table(
    [{ label: 'Desa/Kel' }, { label: 'Posyandu' }, { label: 'Kader (rekap)', num: true },
     { label: 'Nama terdaftar', num: true }, { label: 'Status', html: r => {
        const nm = perDesa.find(d => d.desa === r.desa);
        const total = perPos.filter(p => p.desa === r.desa).reduce((s, p) => s + p.kader, 0);
        const ok = nm && nm.kader === nm.nama;
        return `<span class="pill ${ok ? 'ok' : 'wr'}">${ok ? 'sinkron' : 'perlu dicek'}</span>`; } }],
    perDesa.map(x => ({ desa: x.desa, pos: perPos.filter(p => p.desa === x.desa).length + ' posyandu',
                        kader: x.kader, nama: x.nama }))
  ));

  set('t-perpos', table(
    [{ label: 'Desa/Kel' }, { label: 'Posyandu' }, { label: 'Kader', num: true },
     { label: 'Aktif', num: true }, { label: 'Tidak aktif', num: true }],
    perPos.map(p => ({
      desa: p.desa, pos: p.pos, kader: p.kader,
      aktif: p.aktif !== undefined ? p.aktif : (p.tidak !== undefined ? fnum(p.kader - p.tidak) : '–'),
      tidak: p.tidak !== undefined ? p.tidak : '–'
    }))
  ));
};
