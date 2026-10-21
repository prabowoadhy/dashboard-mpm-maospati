/* Data Kader — rekap jumlah kader (tanpa data pribadi) */
window.renderPage = function(a){
  const k = a.kpi || {}, perPos = a.perPos || [], perDesa = a.perDesa || [], jenis = a.jenis || [];
  const pustu = k.pustu || 0, duplikat = k.duplikat || 0;
  const selisih = (k.daftarNama || 0) - (k.total || 0);
  const beda = perDesa.filter(d => (d.kader || 0) !== (d.nama || 0));

  set('kpis', kpiCards([
    { label: 'Total kader (rekap)', value: fnum(k.total),
      sub: pustu ? `termasuk ${fnum(pustu)} kader PUSTU` : 'jumlah resmi per posyandu' },
    { label: 'Kader terdaftar (form)', value: fnum(k.daftarNama),
      sub: (k.daftarUnik !== undefined ? `${fnum(k.daftarUnik)} nama unik` : 'baris pada form pendataan') +
           (duplikat ? ` · ${fnum(duplikat)} duplikat` : '') },
    { label: 'Posyandu', value: k.posyandu, sub: 'yang punya kader' },
    { label: 'Rata-rata per posyandu', value: k.rataPerPos, sub: 'kader / posyandu' },
  ]));

  const daftarBeda = beda.length
    ? beda.map(d => `<b>${esc(d.desa)}</b> (rekap ${fnum(d.kader)} vs form ${fnum(d.nama)}, ${d.selisih > 0 ? '+' : ''}${fnum(d.selisih)})`).join('; ')
    : '';
  const status = selisih === 0
    ? '<li class="ok">Jumlah rekap dan daftar form sudah <b>sama</b>.</li>'
    : `<li>Rekap posyandu <b>${fnum(k.total)}</b> kader, daftar form <b>${fnum(k.daftarNama)}</b> nama — selisih <b>${selisih > 0 ? '+' : ''}${fnum(selisih)}</b>.</li>`
      + (daftarBeda ? `<li>Selisih per desa: ${daftarBeda}.</li>` : '');
  set('c-selisih', `<ul class="tl">
    ${status}
    ${pustu ? `<li>Baris <b>PUSTU</b> di sheet rekap (${fnum(pustu)} kader) ikut dihitung ke total dan ke desa terdekat.</li>` : ''}
    ${duplikat ? `<li>Ada <b>${fnum(duplikat)} baris form duplikat</b> (nama + tanggal lahir + desa sama). Baris tetap dihitung di angka form, jadi angka unik lebih kecil.</li>` : ''}
    ${k.totalSheet !== undefined && k.totalSheet !== null && k.totalSheet !== k.total
      ? `<li>Sel <b>TOTAL</b> di sheet rekap = <b>${fnum(k.totalSheet)}</b>, berbeda dengan jumlah baris per posyandu (<b>${fnum(k.total)}</b>). Periksa rumus/angka TOTAL.</li>` : ''}
    <li>Rapikan di <b>${esc(k.sumber || 'berkas sumber')}</b> agar angka dashboard seragam, lalu jalankan sinkron.</li>
    <li>${esc(a.privasi || '')}</li>
  </ul>`);

  set('c-desa', barRows(perDesa.map(x => ({ label: x.desa, value: x.kader, note: x.kader + ' / ' + x.nama }))));
  set('c-jenis', jenis.length ? barRows(jenis.map(x => ({ label: x.jenis, value: x.jumlah }))) :
    '<p class="muted">Kolom jenis kader belum ada di berkas sumber.</p>');

  set('t-kader', table(
    [{ label: 'Desa/Kel' }, { label: 'Posyandu' }, { label: 'Kader (rekap)', num: true },
     { label: 'Nama terdaftar', num: true }, { label: 'Selisih', num: true }, { label: 'Status', html: r => {
        const ok = r.kader === r.nama;
        return `<span class="pill ${ok ? 'ok' : 'wr'}">${ok ? 'sinkron' : 'perlu dicek'}</span>`; } }],
    perDesa.map(x => ({ desa: x.desa, pos: perPos.filter(p => p.desa === x.desa && !p.tambahan).length + ' posyandu',
                        kader: x.kader, nama: x.nama,
                        selisih: (x.selisih > 0 ? '+' : '') + fnum(x.selisih) }))
  ));

  set('t-perpos', table(
    [{ label: 'Desa/Kel' }, { label: 'Posyandu' }, { label: 'Kader', num: true },
     { label: 'Keterangan', html: r => r.ket }],
    perPos.map(p => ({
      desa: p.desa, pos: p.pos, kader: p.kader,
      ket: p.tambahan ? '<span class="pill wr">PUSTU (baris tambahan)</span>' : 'posyandu'
    }))
  ));
};
