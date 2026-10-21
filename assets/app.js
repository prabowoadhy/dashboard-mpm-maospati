/* ============================================================================
 * app.js — kerangka bersama semua halaman Dashboard MPM
 * Tugasnya: menggambar menu, memuat data/<slug>.json, menampilkan KPI,
 * daftar isi folder Drive, dan waktu sinkron. Isi/khusus tiap halaman ada di
 * assets/pages/<slug>.js (window.renderPage) supaya mudah dirawat terpisah.
 * ========================================================================== */
const MENU = [
  { slug: 'index',                   label: 'Beranda',                file: 'index.html' },
  { slug: 'smd-mmd',                 label: 'SMD MMD',                file: 'smd-mmd.html' },
  { slug: 'laporan-posyandu',        label: 'Laporan Posyandu',       file: 'laporan-posyandu.html' },
  { slug: 'ruk',                     label: 'RUK',                    file: 'ruk.html' },
  { slug: 'dokumentasi',             label: 'Dokumentasi',            file: 'dokumentasi.html' },
  { slug: 'data-posyandu',           label: 'Data Posyandu',          file: 'data-posyandu.html' },
  { slug: 'data-kader',              label: 'Data Kader',             file: 'data-kader.html' },
  { slug: 'spj-bok',                 label: 'SPJ BOK',                file: 'spj-bok.html' },
  { slug: 'laporan-kegiatan-dinkes', label: 'Laporan Kegiatan Dinkes',file: 'laporan-kegiatan-dinkes.html' }
];
const COL = ['#1f6feb','#0f9d58','#e8a33d','#d93025','#7c5cff','#d6348a','#0aa2c0','#8a6d3b'];
const BULAN = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];

/* ---------- helper tampilan ---------- */
const esc = s => String(s === null || s === undefined ? '' : s)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const fnum = n => (n === null || n === undefined || n === '') ? '–' : Number(n).toLocaleString('id-ID');
const fpct = v => (v === null || v === undefined || isNaN(v)) ? '–' : (Number(v) % 1 ? Number(v).toFixed(1) : Number(v)) + '%';
const cov = (y, n) => (y === null || y === undefined || n === null || n === undefined || (y + n) === 0) ? null : 100 * y / (y + n);
const el = id => document.getElementById(id);
const set = (id, html) => { const e = el(id); if (e) e.innerHTML = html; };

function kpiCards(items){
  return items.map(k => `<div class="card kpi"><div class="l">${esc(k.label)}</div>
    <div class="v">${k.raw ? k.value : esc(k.value)}</div>
    <div class="s">${esc(k.sub || '')}</div></div>`).join('');
}
function barRows(rows){
  /* rows: {label, value, max, note, color} */
  const max = Math.max(1, ...rows.map(r => r.max !== undefined ? r.max : r.value));
  return '<div class="bars">' + rows.map((r, i) => {
    const p = 100 * r.value / (r.max !== undefined ? r.max : max);
    return `<div class="bar"><div class="lab" title="${esc(r.label)}">${esc(r.label)}</div>
      <div class="track"><div class="fill" style="width:${Math.max(1, p).toFixed(1)}%;background:${r.color || COL[i % COL.length]}"></div></div>
      <div class="val">${esc(r.note !== undefined ? r.note : fnum(r.value))}</div></div>`;
  }).join('') + '</div>';
}
function table(cols, rows){
  return '<table><thead><tr>' + cols.map(c => `<th class="${c.num ? 'num' : ''}">${esc(c.label)}</th>`).join('') + '</tr></thead><tbody>' +
    rows.map(r => '<tr>' + cols.map(c => `<td class="${c.num ? 'num' : ''}">${c.html ? c.html(r) : esc(r[c.key])}</td>`).join('') + '</tr>').join('') +
    '</tbody></table>';
}
function matrixBox(cols, rows, cfg){
  /* cols: array label kolom; rows: {label, cells:[{v, color, title}]} */
  const w = cfg && cfg.labelWidth ? cfg.labelWidth : '300px';
  let h = `<div class="mx" style="grid-template-columns:${w} repeat(${cols.length},minmax(46px,1fr))">`;
  h += '<div class="hd"></div>' + cols.map(c => `<div class="hd" style="justify-content:center;text-align:center">${esc(c)}</div>`).join('');
  rows.forEach(r => {
    h += `<div class="hd" title="${esc(r.label)}">${esc(r.label)}</div>`;
    r.cells.forEach(c => {
      if (c.v === null || c.v === undefined || c.v === '') h += `<div class="cell" style="background:color-mix(in srgb,var(--fg) 8%,transparent)" title="${esc(c.title || 'data belum ada')}"></div>`;
      else if (c.color) h += `<div class="cell" style="background:${c.color}" title="${esc(c.title || c.v)}">${esc(c.text !== undefined ? c.text : c.v)}</div>`;
      else h += `<div title="${esc(c.title || '')}">${c.html || esc(c.v)}</div>`;
    });
  });
  return h + '</div>';
}
function folderTree(node, depth){
  const files = node.files || [];
  const kids = node.children || [];
  let h = '';
  if (depth > 0 || kids.length){
    h += `<div class="fld" style="padding-left:${depth * 14}px">
      ${depth ? '📂' : '🗂️'} <a href="${node.url}" target="_blank" rel="noopener">${esc(node.name)}</a>
      <span class="cnt">(${files.length} berkas langsung${kids.length ? ', ' + kids.length + ' subfolder' : ''})</span></div>`;
  }
  files.forEach(f => {
    const ext = (f.name.split('.').pop() || '').toLowerCase();
    h += `<div class="file" style="padding-left:${(depth + 1) * 14}px">
      <span class="ext">${esc(ext)}</span>
      <a class="nm" href="${f.url}" target="_blank" rel="noopener" title="${esc(f.name)}">${esc(f.name)}</a>
      <span class="mod">${esc(f.modified || '')}</span></div>`;
  });
  kids.forEach(k => { h += folderTree(k, depth + 1); });
  return h;
}
const driveBtn = (url, label) => `<a class="btn primary" href="${url}" target="_blank" rel="noopener">📁 ${esc(label || 'Buka folder di Google Drive')}</a>`;

/* ---------- tombol Sinkron (header) ----------
   Situs statis tidak bisa menjalankan Python sendiri, jadi tombol ini memanggil endpoint:
     - lokal  : tools/serve.py  (POST /api/sync)  -> menjalankan tools/sync.py + build_pages.py
     - hosting: api/sync.js     (POST /api/sync)  -> memicu workflow GitHub Actions
   Kalau dua-duanya tidak ada, tombol memberi tahu cara sinkron manual. */
const SYNC_URL = '/api/sync';

function drawSync(){
  const host = el('drivebtn');
  if (!host) return;
  host.innerHTML = `<button class="btn primary" id="btnsync" type="button">⟳ Sinkron sekarang</button>
    <div class="muted" id="synctime" style="font-size:11px;margin-top:4px;text-align:right">Terakhir sinkron: memuat…</div>`;
  const btn = el('btnsync');
  if (btn) btn.onclick = () => jalankanSinkron();
}

const kodeSinkron = () => { try { return localStorage.getItem('mpm_sync') || ''; } catch (e) { return ''; } };

async function jalankanSinkron(){
  const btn = el('btnsync');
  const label = btn ? btn.textContent : '';
  if (btn){ btn.disabled = true; btn.textContent = 'Menyinkronkan…'; }
  set('synctime', 'Menjalankan sinkronisasi…');
  let hasil = null, pesan = '';
  try {
    const r = await fetch(SYNC_URL, { method: 'POST', headers: { 'x-sync-secret': kodeSinkron() } });
    const j = await r.json().catch(() => ({}));
    if (r.status === 401 || r.status === 403){
      const kode = prompt('Kode sinkronisasi:');
      if (kode){ try { localStorage.setItem('mpm_sync', kode); } catch (e) {} }
      if (btn){ btn.disabled = false; btn.textContent = label; }
      set('synctime', 'Kode dimasukkan — tekan tombol Sinkron lagi.');
      return;
    }
    if (!r.ok) throw new Error(j.error || ('HTTP ' + r.status));
    hasil = j;
  } catch (e){
    pesan = e.message;
  }
  if (!hasil){
    if (btn){ btn.disabled = false; btn.textContent = label; }
    set('synctime', `Sinkron otomatis tidak aktif di sini (${esc(pesan)}). Jalankan <code>python tools/sync.py</code> lalu muat ulang halaman.`);
    return;
  }
  /* tunggu status selesai (lokal: status dicek ke endpoint; hosting: lewat GitHub) */
  const mulai = Date.now();
  const cek = async () => {
    let st = null;
    try { st = await (await fetch(SYNC_URL + '?t=' + Date.now())).json(); } catch (e) {}
    const umur = Math.round((Date.now() - mulai) / 1000);
    if (st && st.state === 'running'){
      set('synctime', `Sinkronisasi berjalan… ${umur}s (${esc(st.detail || '')})`);
      setTimeout(cek, 2500);
    } else if (st && st.state === 'error'){
      if (btn){ btn.disabled = false; btn.textContent = label; }
      set('synctime', 'Sinkronisasi gagal: ' + esc(String(st.detail || '').slice(0, 160)));
    } else if (st && st.state === 'done'){
      set('synctime', `Sinkron selesai dalam ${umur}s — memuat ulang…`);
      setTimeout(() => location.reload(), 800);
    } else {
      set('synctime', 'Sinkron dijalankan. Muat ulang halaman beberapa saat lagi untuk melihat hasilnya.');
      if (btn){ btn.disabled = false; btn.textContent = label; }
    }
  };
  setTimeout(cek, 1200);
}

/* ---------- pemuatan data ---------- */
async function loadJSON(path){
  const slug = document.body.dataset.page;
  try {
    const res = await fetch(path, { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  } catch (e) {
    /* cadangan: data yang ditanam saat build (dipakai bila halaman dibuka tanpa web server) */
    const inline = window.__DATA__ && window.__DATA__[slug];
    if (inline){ console.info('Memakai data cadangan tertanam untuk ' + slug + ' (' + e.message + ')'); return inline; }
    throw new Error(e.message + ' saat memuat ' + path);
  }
}

/* ---------- kerangka halaman ---------- */
function drawFrame(active){
  const host = el('navmenu');
  if (host) host.innerHTML = MENU.map(m =>
    `<a href="${m.file}" class="${m.slug === active ? 'on' : ''}">${esc(m.label)}</a>`).join('');
}

async function boot(){
  const page = document.body.dataset.page;
  drawFrame(page);
  drawSync();
  try {
    if (page === 'index'){
      const site = await loadJSON('data/site.json');
      window.renderPage(site, null);
      set('synced', 'Data disinkronkan: <b>' + esc(site.generated) + '</b>');
      set('synctime', 'Terakhir sinkron: <b>' + esc(site.generated) + '</b>');
      return;
    }
    const d = await loadJSON('data/' + page + '.json');
    document.title = d.menu + ' — Dashboard MPM Maospati';
    set('pagetitle', esc(d.menu));
    set('pagesub', esc(d.subjudul) + ' · ' + esc(d.deskripsi));
    set('drivebtn2', driveBtn(d.folder.url));
    set('pagemeta', `<b>${fnum(d.statistik.berkas)}</b> berkas · <b>${fnum(d.statistik.subfolder)}</b> subfolder ·
      folder: <a href="${d.folder.url}" target="_blank" rel="noopener">${esc(d.folder.name)}</a>`);
    if (window.renderPage) window.renderPage(d.analisa, d);
    if (d.struktur) set('treehost', folderTree(d.struktur, 0));
    set('filecount', d.files.length + ' berkas');
    set('synced', 'Data disinkronkan: <b>' + esc(d.generated || '—') + '</b>');
    set('synctime', 'Terakhir sinkron: <b>' + esc(d.generated || '—') + '</b>');
  } catch (e){
    const b = el('banner');
    if (b){
      b.classList.add('on');
      b.innerHTML = '⚠️ Gagal memuat data (' + esc(e.message) + '). Jalankan <code>python tools/sync.py</code> lalu buka situs lewat web server: <code>python tools/serve.py</code> (bukan dengan klik dua kali berkas HTML).';
    }
    console.error(e);
  }
}
document.addEventListener('DOMContentLoaded', boot);
