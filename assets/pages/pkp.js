/* PKP · capaian indikator Penilaian Kinerja Puskesmas per klaster.
   Sumber: spreadsheet "PKP KLASTER 1_2026" (dibaca tools/sync.py). */
window.renderPage = function(a){
  a = a || {};
  const k = a.kpi || {};
  const ind = a.indikator || [];
  const klaster = a.klaster || [];
  const sebaran = a.sebaran || [];

  const STATUS = {
    tercapai: { label: 'tercapai', cls: 'ok' },
    hampir:   { label: 'hampir', cls: '' },
    kurang:   { label: 'perlu dorongan', cls: 'wr' },
    rendah:   { label: 'jauh dari target', cls: 'no' },
    belum:    { label: 'belum ada data', cls: '' }
  };
  const pill = s => {
    const x = STATUS[s] || STATUS.belum;
    return `<span class="pill${x.cls ? ' ' + x.cls : ''}">${x.label}</span>`;
  };
  /* persentase memakai koma desimal seperti angka di spreadsheet aslinya */
  const pct = v => (v === null || v === undefined || isNaN(v)) ? '&ndash;'
    : Number(v).toLocaleString('id-ID', { maximumFractionDigits: 1 }) + '%';
  const angka = v => (v === null || v === undefined) ? '&ndash;' : fnum(v);

  if (!ind.length){
    set('kpis', '<p class="empty" style="grid-column:1/-1">Belum ada indikator yang terbaca dari spreadsheet PKP. ' +
      'Pastikan spreadsheet dibagikan <b>Anyone with the link, Viewer</b>, lalu tekan <b>Sinkronkan data</b>.</p>');
    ['c-klaster', 'c-sebaran', 'c-catatan'].forEach(id =>
      set(id, '<p class="empty">Menunggu data indikator dari spreadsheet.</p>'));
    set('t-terendah', '<p class="empty">Menunggu data indikator dari spreadsheet.</p>');
    set('t-pkp', '<p class="empty">Menunggu data indikator dari spreadsheet.</p>');
    set('c-info', 'belum ada data');
    return;
  }

  set('kpis', kpiCards([
    { label: 'Indikator', value: fnum(k.total),
      sub: `${fnum(k.klaster || klaster.length)} klaster · ${fnum(k.dinilai)} sudah terisi` },
    { label: 'Tercapai target', value: fnum(k.tercapai),
      sub: `${k.total ? pct(100 * k.tercapai / k.total) : '–'} dari ${fnum(k.total)} indikator` },
    { label: 'Rata-rata hasil kinerja', value: pct(k.rata),
      sub: `${fnum(k.dinilai)} indikator terisi · nilai dibatasi 100%` },
    { label: 'Perlu perhatian', value: fnum(k.rendah),
      sub: `indikator di bawah 50% · ${fnum(k.belum)} belum ada data` },
  ]));

  /* satu batang per klaster: panjang = rata-rata hasil kinerja, angka kanan = tercapai/total */
  set('c-klaster', barRows(klaster.map(x => ({
    label: `${x.kode} ${x.nama}`,
    value: x.rata === null || x.rata === undefined ? 0 : x.rata,
    max: 100,
    note: x.rata === null || x.rata === undefined ? 'belum ada' : `${x.tercapai}/${x.indikator}`,
    color: '#0b57d0'
  }))));

  const warna = { tercapai: '#137333', hampir: '#0b57d0', kurang: '#b06000', rendah: '#c5221f', belum: '#9aa0a6' };
  set('c-sebaran', barRows(sebaran.map(s => ({
    label: STATUS[s.status] ? STATUS[s.status].label : s.status,
    value: s.jumlah,
    max: k.total || 1,
    note: angka(s.jumlah),
    color: warna[s.status]
  }))));

  const terendah = ind
    .filter(x => x.kinerja !== null && x.kinerja !== undefined && !isNaN(x.kinerja))
    .sort((x, y) => x.kinerja - y.kinerja)
    .slice(0, 8);
  set('t-terendah', terendah.length ? table(
    [{ label: 'Hasil kinerja', num: true, html: r => pct(r.kinerja) },
     { label: 'Indikator', html: r => `${esc(r.indikator)}<span class="cellsub">${esc(r.klaster)} ${esc(r.klasterNama)}</span>` },
     { label: 'Status', html: r => pill(r.status) }],
    terendah
  ) : '<p class="empty">Semua indikator sudah terisi nilainya.</p>');

  /* tabel rincian: disaring per klaster dan kata kunci */
  const sel = el('f-klaster');
  if (sel){
    sel.innerHTML = '<option value="">Semua klaster</option>' + klaster.map(x =>
      `<option value="${esc(x.kode)}">${esc(x.kode + ' ' + x.nama)}</option>`).join('');
  }
  const isi = () => {
    const kl = sel ? sel.value : '';
    const cari = el('q-pkp') ? el('q-pkp').value.toLowerCase().trim() : '';
    const rows = ind.filter(x => (!kl || x.klaster === kl) &&
      (!cari || (x.indikator + ' ' + x.kegiatan + ' ' + x.klasterNama).toLowerCase().indexOf(cari) >= 0));
    set('c-info', `${fnum(rows.length)} dari ${fnum(ind.length)} indikator`);
    set('t-pkp', rows.length ? table(
      [{ label: 'No', key: 'no', num: true },
       { label: 'Indikator', key: 'indikator' },
       { label: 'Klaster', key: 'klasterNama' },
       { label: 'Hasil kinerja', num: true, html: r => pct(r.kinerja) },
       { label: 'Status', html: r => pill(r.status) },
       { label: 'Target', num: true, html: r => r.target === null || r.target === undefined ? '&ndash;' : pct(100 * r.target) },
       { label: 'Satuan', key: 'satuan' },
       { label: 'Target sasaran', num: true, html: r => angka(r.targetSasaran) },
       { label: 'Pencapaian', num: true, html: r => angka(r.pencapaian) },
       { label: 'Capaian riil', num: true, html: r => pct(r.capaianRiil) }],
      rows
    ) : '<p class="empty">Tidak ada indikator yang cocok dengan saringan ini. Kosongkan kata kunci atau pilih klaster lain.</p>');
  };
  if (sel) sel.onchange = isi;
  const cari = el('q-pkp');
  if (cari) cari.oninput = isi;
  isi();

  const catatan = ind.filter(x => x.catatan);
  const bukti = ind.filter(x => x.bukti);
  set('c-catatan',
    (catatan.length
      ? '<ul class="tl">' + catatan.map(x =>
          `<li><b>${esc(x.indikator)}</b> <span class="muted">(${esc(x.klaster)} ${esc(x.klasterNama)})</span> · ${esc(x.catatan)}</li>`
        ).join('') + '</ul>'
      : '<p class="empty">Belum ada catatan petugas pada spreadsheet.</p>') +
    (bukti.length
      ? `<p class="note">Tautan folder bukti pada spreadsheet (${fnum(bukti.length)} indikator): ` +
        bukti.map(x => `<a href="${esc(x.bukti)}" target="_blank" rel="noopener">${esc(x.klaster)} baris ${esc(x.no)}</a>`).join(' · ') +
        '.</p>'
      : ''));
};
