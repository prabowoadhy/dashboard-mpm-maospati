/* PKP · capaian Penilaian Kinerja Puskesmas per program, desa, dan bulan.
   Sumber: lima spreadsheet pada folder Drive "PKP" (dibaca tools/sync.py). */
window.renderPage = function(a){
  a = a || {};
  const k = a.kpi || {};
  const pr = a.program || [];

  const pct = v => (v === null || v === undefined || isNaN(v)) ? '&ndash;'
    : (Number(v) % 1 ? Number(v).toFixed(1).replace('.', ',') : Number(v)) + '%';
  const angka = v => (v === null || v === undefined) ? '&ndash;' : fnum(v);

  if (!pr.length){
    set('kpis', '<p class="empty" style="grid-column:1/-1">Belum ada data program PKP. ' +
      'Pastikan spreadsheet di folder <b>PKP</b> dibagikan <b>Anyone with the link, Viewer</b>, ' +
      'lalu tekan <b>Sinkronkan data</b>.</p>');
    ['c-program', 'c-ringkas', 'c-selisih', 'c-catatan'].forEach(id =>
      set(id, '<p class="empty">Menunggu data program PKP.</p>'));
    set('t-bawah', '<p class="empty">Menunggu data program PKP.</p>');
    set('t-desa', '<p class="empty">Menunggu data program PKP.</p>');
    set('c-info', 'belum ada data');
    return;
  }

  const warnaLatar = p => p.persen === null ? '#9aa0a6'
    : (p.persen >= 100 ? '#137333' : (p.persen >= 75 ? '#0b57d0' : '#c5221f'));

  set('kpis', kpiCards([
    { label: 'Program terpantau', value: fnum(k.program),
      sub: `${fnum(k.bulanan)} berdata bulanan · ${fnum((k.program || 0) - (k.bulanan || 0))} tahunan` },
    { label: 'Desa / kelurahan', value: fnum(k.desa),
      sub: 'sama di kelima spreadsheet' },
    { label: 'Capai 100% ke atas', value: fnum(k.mencapai),
      sub: `dari ${fnum(k.program)} program · masing-masing punya satuan sendiri` },
    { label: 'Di bawah target', value: fnum(k.bawah),
      sub: k.bawah ? 'perlu dorongan capaian' : 'semua program sudah mencapai target' },
  ]));

  /* satu batang per program: panjang = persentase capaian (skala 150%) */
  set('c-program', barRows(pr.map(p => ({
    label: `${p.kode} · ${p.nama}`,
    value: p.persen === null ? 0 : Math.min(p.persen, 150),
    max: 150,
    note: p.persen === null ? 'belum ada target'
      : `${pct(p.persen)} · ${angka(p.capaian)}/${angka(p.target)}`,
    color: warnaLatar(p)
  }))));

  /* ringkasan: berapa program di atas dan di bawah 100% */
  set('c-ringkas', barRows([
    { label: 'Mencapai 100% ke atas', value: k.mencapai || 0, max: k.program || 1,
      note: `${fnum(k.mencapai)} program`, color: '#137333' },
    { label: 'Di bawah 100%', value: k.bawah || 0, max: k.program || 1,
      note: `${fnum(k.bawah)} program`, color: '#c5221f' },
  ]));

  /* selisih antara baris TOTAL di spreadsheet dan jumlah baris desa */
  const selisih = a.selisih || [];
  set('c-selisih', selisih.length
    ? '<ul class="tl">' + selisih.map(x =>
        `<li><b>${esc(x.kode)} ${esc(x.nama)}</b>: baris TOTAL menulis <b>${angka(x.sheet)}</b>, ` +
        `jumlah baris desa <b>${angka(x.hitung)}</b> (selisih ${angka(x.selisih)}). ` +
        'Halaman ini memakai jumlah baris desa supaya angkanya bisa ditelusuri.</li>').join('') + '</ul>'
    : '<p class="empty">Tidak ada selisih pada spreadsheet yang baris TOTAL-nya terbaca.</p>');

  /* program yang belum mencapai 100% */
  const bawah = pr.filter(p => p.persen !== null && p.persen < 100)
    .sort((x, y) => x.persen - y.persen);
  set('t-bawah', bawah.length
    ? table(
      [{ label: 'Program', html: r => `${esc(r.kode)}<span class="cellsub">${esc(r.nama)}</span>` },
       { label: 'Capaian', num: true, html: r => angka(r.capaian) },
       { label: 'Target', num: true, html: r => angka(r.target) },
       { label: 'Persentase', num: true, html: r => pct(r.persen) },
       { label: 'Kurang', num: true, html: r => angka(Math.round((r.target - r.capaian) * 100) / 100) }],
      bawah)
    : '<p class="empty">Semua program sudah mencapai 100% ke atas.</p>');

  /* rincian per desa, disaring per program dan kata kunci */
  const sel = el('f-program');
  if (sel){
    sel.innerHTML = '<option value="">Semua program</option>' + pr.map(p =>
      `<option value="${esc(p.kode)}">${esc(p.kode)} · ${esc(p.nama)}</option>`).join('');
  }
  const cari = el('q-pkp');
  const isi = () => {
    const kd = sel ? sel.value : '';
    const q = cari ? cari.value.toLowerCase().trim() : '';
    const rows = [];
    (a.rincian || []).forEach(p => {
      if (kd && p.kode !== kd) return;
      (p.desa || []).forEach(d => {
        rows.push({
          desa: d.desa, program: p.kode, programNama: p.nama,
          target: d.target, capaian: d.capaian, persen: d.persen
        });
      });
    });
    const hasil = rows.filter(r => !q || r.desa.toLowerCase().indexOf(q) >= 0);
    set('c-info', `${fnum(hasil.length)} baris desa-program ditampilkan`);
    set('t-desa', hasil.length ? table(
      [{ label: 'Desa', key: 'desa' },
       { label: 'Program', html: r => `${esc(r.program)}<span class="cellsub">${esc(r.programNama)}</span>` },
       { label: 'Target', num: true, html: r => angka(r.target) },
       { label: 'Capaian', num: true, html: r => angka(r.capaian) },
       { label: 'Persentase', num: true, html: r => pct(r.persen) }],
      hasil)
      : '<p class="empty">Tidak ada baris yang cocok dengan saringan ini.</p>');
  };
  if (sel) sel.onchange = isi;
  if (cari) cari.oninput = isi;
  isi();

  set('c-catatan', '<ul class="tl">' +
    '<li>Lima spreadsheet di folder <b>PKP</b>: ' +
      pr.map(p => `<b>${esc(p.kode)}</b> ${esc(p.nama)}`).join(', ') + '.</li>' +
    '<li>Persentase = capaian dibagi target. Capaian diambil dari kolom <b>TOTAL CAPAIAN</b>; ' +
      'target dari kolom <b>TARGET SASARAN</b> / <b>TOTAL TARGET</b>, dan kalau tidak ada, dari ' +
      'jumlah target bulanan.</li>' +
    '<li>Kolom TOTAL CAPAIAN menumpuk capaian seluruh bulan sampai bulan berjalan, jadi angkanya ' +
      'bisa melewati 100%. Angka di halaman ini dijumlah dari baris desa, bukan disalin dari baris TOTAL.</li>' +
    '<li>' + (pr.filter(p => p.punyaBulan).length) + ' spreadsheet berisi TARGET dan CAPAIAN per bulan' +
      (pr.some(p => !p.punyaBulan)
        ? '; <b>' + pr.filter(p => !p.punyaBulan).map(p => esc(p.kode)).join(', ') + '</b> hanya berisi total sasaran dan capaian tahunan'
        : '') + '.</li>' +
    '<li>Setiap program punya satuan sendiri (rumah tangga, sekolah), karena itu angka antarprogram ' +
      'tidak dijumlahkan.</li>' +
    '</ul>');
};
