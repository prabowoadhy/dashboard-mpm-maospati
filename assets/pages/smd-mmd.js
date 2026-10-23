/* SMD MMD · rekap per desa & tahun, kelengkapan, heatmap indikator */
window.renderPage = function(a, d){
  const tahun = a.tahun || [], desa = a.desa || [];
  const k = a.kpi || {};
  set('kpis', kpiCards([
    { label: 'Desa / kelurahan', value: k.desa, sub: 'wilayah tercakup' },
    { label: 'Tahun SMD', value: (tahun[0] || '-') + '-' + (tahun[tahun.length - 1] || '-'), sub: tahun.join(', '), small: true },
    { label: 'Total responden', value: fnum(k.responden), sub: 'KK dari semua berkas rekap' },
    { label: 'Indikator terbaca', value: k.indikator, sub: 'gabungan instrumen lama & baru' },
    { label: 'Rekap selesai', value: k.rekapSelesai + '/' + k.kelTotal, sub: 'per desa-tahun (KELENGKAPAN SMD)' },
    { label: 'Analisa selesai', value: k.analisaSelesai + '/' + k.kelTotal, sub: 'KAK, prioritas & metode masalah' },
  ]));

  /* responden per desa per tahun: tabel angka, lebih mudah dibaca daripada grafik */
  const nilaiResponden = (v, t) => {
    const r = a.rekap.find(x => x.desa === v && x.tahun === t);
    return r && r.responden ? r.responden : null;
  };
  const totalTahun = tahun.map(t => desa.reduce((n, v) => n + (nilaiResponden(v, t) || 0), 0));
  const totalDesa = v => tahun.reduce((n, t) => n + (nilaiResponden(v, t) || 0), 0);
  const totalSemua = totalTahun.reduce((n, v) => n + v, 0);
  const sortHead = (label, num) => `<th scope="col" class="sortable${num ? ' num' : ''}" aria-sort="none"><button class="sort-btn" type="button" title="Klik untuk mengurutkan">${label}<span class="sort-ind" aria-hidden="true"></span></button></th>`;
  let s = '<div class="scroll"><table aria-label="Responden per desa dan tahun">'
    + '<thead><tr>'
    + sortHead('Desa / kelurahan')
    + tahun.map(t => sortHead(esc(String(t)), true)).join('')
    + sortHead('Jumlah', true)
    + '</tr></thead><tbody>';
  desa.forEach(v => {
    s += `<tr><th scope="row">${esc(v)}</th>`;
    tahun.forEach(t => {
      const val = nilaiResponden(v, t);
      s += `<td class="num${val === null ? ' muted' : ''}">${val === null ? '&ndash;' : fnum(val)}</td>`;
    });
    s += `<td class="num"><b>${fnum(totalDesa(v))}</b></td></tr>`;
  });
  s += '</tbody><tfoot><tr><th scope="row">Jumlah</th>'
    + totalTahun.map(n => `<td class="num">${fnum(n)}</td>`).join('')
    + `<td class="num">${fnum(totalSemua)}</td></tr></tfoot></table></div>`
    + '<p class="note">Klik judul kolom untuk mengurutkan. Tanda &ndash; berarti belum ada berkas rekap pada tahun itu.</p>';
  set('c-responden', s);
  if (typeof aktifkanSortir === 'function' && typeof document.querySelector === 'function'){
    const tabel = document.querySelector('#c-responden table');
    if (tabel) aktifkanSortir(tabel);
  }

  /* kelengkapan rekap & analisa: matriks desa × tahun */
  const rows = [];
  desa.forEach(v => rows.push({
    label: v,
    cells: tahun.map(t => {
      const x = (a.kelengkapan || []).find(y => y.tahun === t && y.desa === v);
      if (!x) return { v: '' };
      return { v: 'x', color: null, html: `<span class="pill ${x.rekap ? 'ok' : 'no'}">R</span> <span class="pill ${x.analisa ? 'ok' : 'no'}">A</span>`, title: `${v} ${t} · rekap ${x.rekap ? 'sudah' : 'belum'}, analisa ${x.analisa ? 'sudah' : 'belum'}` };
    })
  }));
  set('c-kel', '<div class="scroll">' + matrixBox(tahun, rows, { labelWidth: '130px' }) + '</div>' +
    '<div class="legend"><span class="pill ok">R</span> rekap selesai &nbsp;<span class="pill no">R</span> rekap belum &nbsp;<span class="pill ok">A</span> analisa selesai &nbsp;<span class="pill no">A</span> analisa belum</div>');

  /* kebutuhan & harapan */
  set('c-keb', barRows((a.kebutuhan || []).slice(0, 14).map(x => ({
    label: x.teks, value: x.jumlah, note: x.jumlah + ' org'
  }))));

  /* heatmap indikator × desa untuk tahun terpilih */
  const selT = el('f-tahun');
  selT.innerHTML = tahun.map(t => `<option>${t}</option>`).join('');
  selT.value = tahun[tahun.length - 1];
  function heat(){
    const t = +selT.value;
    const cols = desa.filter(v => a.rekap.some(r => r.desa === v && r.tahun === t));
    const ref = a.rekap.find(r => r.tahun === t && r.desa === cols[0]);
    if (!ref){ set('c-heat', '<p class="muted">Belum ada berkas rekap untuk tahun ' + t + '.</p>'); return; }
    const seen = {}; const inds = [];
    ref.ind.forEach(i => { const txt = a.indTexts[i[0]]; if (!/^[A-Z]\./.test(txt) && !seen[txt]){ seen[txt] = 1; inds.push(i[0]); } });
    const rows = inds.map(idx => ({
      label: a.indTexts[idx].toLowerCase(),
      cells: cols.map(v => {
        const r = a.rekap.find(x => x.desa === v && x.tahun === t);
        const it = r && r.ind.find(x => x[0] === idx);
        const c = it ? cov(it[1], it[2]) : null;
        if (c === null) return { v: '' , title: v + ': data tidak lengkap' };
        return { v: c.toFixed(0), color: c < 50 ? '#fce8e6' : c < 75 ? '#fef7e0' : '#e6f4ea',
                 text: c.toFixed(0), title: `${v} ${t} · ${a.indTexts[idx]}: ${fpct(c)}` };
      })
    }));
    set('c-heat-sub', 'tahun ' + t + ' · warna = % jawaban YA');
    set('c-heat', matrixBox(cols, rows, { labelWidth: 'minmax(210px,360px)' }));
  }
  selT.onchange = heat; heat();

  /* tabel indikator per desa · tahun dipilih dulu, desa mengikuti yang punya data */
  const selD = el('f-desa'), selT2 = el('f-tahun2');
  selT2.innerHTML = tahun.map(t => `<option>${t}</option>`).join('');
  selT2.value = tahun[tahun.length - 1] || '';
  function isiDesa(){
    const t = +selT2.value;
    const ada = desa.filter(v => a.rekap.some(r => r.desa === v && r.tahun === t));
    const daftar = ada.length ? ada : desa;
    const lama = selD.value;
    selD.innerHTML = daftar.map(v => `<option>${v}</option>`).join('');
    selD.value = daftar.includes(lama) ? lama : daftar[0] || '';
  }
  function detail(){
    isiDesa();
    const v = selD.value, t = +selT2.value;
    const r = a.rekap.find(x => x.desa === v && x.tahun === t);
    if (!r){
      set('t-ind', '');
      set('c-tbl-sub', 'belum ada berkas untuk ' + v + ' ' + t);
      return;
    }
    const prev = tahun.filter(y => y < t).pop();
    const rp = prev ? a.rekap.find(x => x.desa === v && x.tahun === prev) : null;
    const pmap = {};
    if (rp) rp.ind.forEach(i => pmap[i[0]] = cov(i[1], i[2]));
    set('c-tbl-sub', `${v} ${t} · sumber: ${r.src}${prev ? ' · Δ vs ' + prev : ''}`);
    set('t-ind', table(
      [{ label: 'Klaster' }, { label: 'Indikator' }, { label: 'YA', num: true }, { label: 'TIDAK', num: true },
       { label: '%', num: true }, { label: 'Δ ' + (prev || ''), num: true }],
      r.ind.map(i => {
        const c = cov(i[1], i[2]), p = pmap[i[0]];
        const dl = (c !== null && p !== undefined && p !== null) ? c - p : null;
        return { k: String(i[3] || '').replace('KLASTER ', 'K'), t: a.indTexts[i[0]].toLowerCase(),
                 ya: i[1], tidak: i[2], p: fpct(c), d: dl === null ? '–' : (dl > 0 ? '+' : '') + dl.toFixed(1) };
      })
    ));
  }
  selD.onchange = selT2.onchange = detail; detail();

  /* dokumen analisa per tahun */
  const docs = a.dokumen || {};
  const dk = Object.keys(docs).sort();
  set('c-doc', dk.length ? dk.map(folder => `<div class="fld">${esc(folder)}</div>` +
      docs[folder].map(f => `<div class="file" style="padding-left:14px"><a class="nm" href="${f.url}" target="_blank" rel="noopener">${esc(f.name)}</a><span class="mod">${esc(f.modified || '')}</span></div>`).join('')
    ).join('') : '<p class="muted">Belum ada berkas analisa.</p>');
};
