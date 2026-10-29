/* ============================================================================
 * app.js - kerangka bersama semua halaman Dashboard MPM
 * Tugasnya: menggambar menu, memuat data/<slug>.json, menampilkan KPI,
 * daftar isi folder Drive, dan waktu sinkron. Isi/khusus tiap halaman ada di
 * assets/pages/<slug>.js (window.renderPage) supaya mudah dirawat terpisah.
 * ========================================================================== */
const MENU = [
  { slug: 'index',                   label: 'Beranda',                file: 'index.html' },
  { slug: 'smd-mmd',                 label: 'SMD MMD',                file: 'smd-mmd.html' },
  { slug: 'laporan-posyandu',        label: 'Laporan Posyandu',       file: 'laporan-posyandu.html' },
  { slug: 'ruk',                     label: 'RUK',                    file: 'ruk.html' },
  { slug: 'pkp',                     label: 'PKP',                    file: 'pkp.html' },
  { slug: 'dokumentasi',             label: 'Dokumentasi',            file: 'dokumentasi.html' },
  { slug: 'data-posyandu',           label: 'Data Posyandu',          file: 'data-posyandu.html' },
  { slug: 'data-kader',              label: 'Data Kader',             file: 'data-kader.html' },
  { slug: 'spj-bok',                 label: 'SPJ BOK',                file: 'spj-bok.html' },
  { slug: 'laporan-kegiatan-dinkes', label: 'Laporan Kegiatan Dinkes',file: 'laporan-kegiatan-dinkes.html' },
  { slug: 'jadwal-promkes',          label: 'Jadwal Promkes',         file: 'jadwal-promkes.html' }
];
const COL = ['#0b57d0','#137333','#b06000','#c5221f','#7b1fa2','#00796b','#c2185b','#3949ab'];
const BULAN = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];

/* ---------- helper tampilan ---------- */
const esc = s => String(s === null || s === undefined ? '' : s)
  .replace(/\u2014/g,'\u00b7')
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const fnum = n => (n === null || n === undefined || n === '') ? '–' : Number(n).toLocaleString('id-ID');
const fpct = v => (v === null || v === undefined || isNaN(v)) ? '–' : (Number(v) % 1 ? Number(v).toFixed(1) : Number(v)) + '%';
const cov = (y, n) => (y === null || y === undefined || n === null || n === undefined || (y + n) === 0) ? null : 100 * y / (y + n);
const el = id => document.getElementById(id);
const set = (id, html) => { const e = el(id); if (e) e.innerHTML = html; };

function kpiCards(items){
  return items.map((k, i) => {
    const wide = items.length % 4 === 2 && i >= items.length - 2 ? ' wide' : '';
    return `<div class="card kpi${wide}"><div class="l">${esc(k.label)}</div>
    <div class="v${k.small ? ' text' : ''}">${k.raw ? k.value : esc(k.value)}</div>
    <div class="s">${esc(k.sub || '')}</div></div>`;
  }).join('');
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
  const nk = s => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
  return '<table><thead><tr>' + cols.map(c => `<th scope="col" class="${c.num ? 'num' : ''}">${esc(c.label)}</th>`).join('') + '</tr></thead><tbody>' +
    rows.map(r => {
      const keys = Object.keys(r);
      return '<tr>' + cols.map((c, i) => {
        let v;
        if (c.html) {
          v = c.html(r);
        } else {
          /* pakai c.key bila ada; kalau tidak, cocokkan label dengan nama kolom data,
             lalu jatuh ke urutan kolom. Ini menjaga tabel lama tetap terisi. */
          let key = c.key;
          if (key === undefined) {
            const lab = nk(c.label);
            key = keys.find(k => nk(k) === lab)
              || keys.find(k => lab && nk(k).length > 1 && lab.includes(nk(k)))
              || keys[i];
          }
          v = esc(r[key]);
        }
        return `<td class="${c.num ? 'num' : ''}">${v}</td>`;
      }).join('') + '</tr>';
    }).join('') +
    '</tbody></table>';
}
function aktifkanSortir(table){
  const head = table.tHead, body = table.tBodies[0];
  if (!head || !body) return;
  const headers = Array.from(head.rows[0].cells);
  const rows = Array.from(body.rows);
  let active = -1, dir = 1;
  const nilai = (row, i) => {
    const cell = row.cells[i];
    if (!cell) return null;
    const raw = (cell.textContent || '').trim();
    if (!cell.classList || !cell.classList.contains('num')) return raw.toLocaleLowerCase('id');
    if (!/\d/.test(raw)) return null;
    const n = Number(raw.replace(/\./g, '').replace(',', '.'));
    return Number.isFinite(n) ? n : null;
  };
  const urut = i => {
    const next = active === i ? -dir : 1;
    active = i; dir = next;
    const sorted = rows.slice().sort((a, b) => {
      const av = nilai(a, i), bv = nilai(b, i);
      if (av === null && bv === null) return 0;
      if (av === null) return 1;
      if (bv === null) return -1;
      if (typeof av === 'string' && typeof bv === 'string') return av.localeCompare(bv, 'id') * dir;
      return (av - bv) * dir;
    });
    sorted.forEach(r => body.appendChild(r));
    headers.forEach((h, n) => h.setAttribute('aria-sort', n === i ? (dir === 1 ? 'ascending' : 'descending') : 'none'));
  };
  headers.forEach((h, i) => {
    const btn = h.querySelector && h.querySelector('.sort-btn');
    if (btn) btn.addEventListener('click', () => urut(i));
  });
}

function matrixBox(cols, rows, cfg){
  /* cols: array label kolom; rows: {label, cells:[{v, color, title}]} */
  const w = cfg && cfg.labelWidth ? cfg.labelWidth : '300px';
  let h = `<div class="mx" style="grid-template-columns:${w} repeat(${cols.length},minmax(46px,1fr))">`;
  h += '<div class="hd"></div>' + cols.map(c => `<div class="hd" style="justify-content:center;text-align:center">${esc(c)}</div>`).join('');
  rows.forEach(r => {
    h += `<div class="hd" title="${esc(r.label)}">${esc(r.label)}</div>`;
    r.cells.forEach(c => {
      if (c.v === null || c.v === undefined || c.v === '') h += `<div class="cell" style="background:var(--surface-2)" title="${esc(c.title || 'data belum ada')}"></div>`;
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
      <a href="${node.url}" target="_blank" rel="noopener">${esc(node.name)}</a>
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
const driveBtn = (url, label) => `<a class="btn" href="${url}" target="_blank" rel="noopener">${esc(label || 'Buka folder Drive')}</a>`;
/* keterangan sumber data untuk setiap panel, supaya mudah dicek ke berkas Excel aslinya */
const srcLine = txt => `<p class="src">Sumber data: ${txt}</p>`;

/* sumber data untuk baris KPI di tiap halaman (KPI berada di luar kartu) */
const KPI_SRC = {
  'index': 'hasil pembacaan otomatis <code>tools/sync.py</code> atas 8 folder Google Drive MPM + kalender Promkes',
  'smd-mmd': 'berkas rekap SMD per desa di folder <b>SMD MMD</b> dan <code>KELENGKAPAN SMD.xlsx</code>',
  'laporan-posyandu': '<code>KELENGKAPAN LHK.xlsx</code> · folder <b>LAPORAN POSYANDU</b>',
  'ruk': '<code>Copy of BAB IV Perencanaan Belanja 2027 SIP.xlsx</code> · folder <b>RUK</b>',
  'pkp': 'spreadsheet <b>PKP KLASTER 1_2026</b> (Google Sheets) · kolom indikator, target, dan hasil kinerja',
  'dokumentasi': 'folder <b>DOKUMENTASI</b> di Google Drive (belum ada berkas)',
  'data-posyandu': '<code>POSYANDU AKTIF.xlsx</code> · folder <b>DATA POSYANDU</b>',
  'data-kader': '<code>Data Kader .xlsx</code> · folder <b>DATA KADER</b>',
  'spj-bok': 'folder <b>SPJ BOK</b> di Google Drive (belum ada berkas)',
  'laporan-kegiatan-dinkes': '<code>KEGIATAN DINKES.xlsx</code> · folder <b>LAPORAN KEGIATAN DINKES</b>',
  'jadwal-promkes': 'kalender publik Google <b>dhellayaamanda2@gmail.com</b> · bukan berkas Excel'
};

/* ---------- tombol Sinkron (header) ----------
   Situs statis tidak bisa menjalankan Python sendiri, jadi tombol ini memanggil endpoint:
     - lokal  : tools/serve.py  (POST /api/sync)  -> menjalankan tools/sync.py + build_pages.py
     - hosting: api/sync.js     (POST /api/sync)  -> memicu workflow GitHub Actions
   Kalau dua-duanya tidak ada, tombol memberi tahu cara sinkron manual. */
const SYNC_URL = '/api/sync';

function drawSync(){
  const host = el('drivebtn');
  if (!host) return;
  host.innerHTML = `<button class="btn primary" id="btnsync" type="button" aria-label="Sinkronkan data" title="Sinkronkan data">
      <svg class="sync-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 0 0-14.9-3M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.9 3M20 20v-4h-4"/></svg>
      <span class="sync-label">Sinkronkan data</span>
    </button>
    <div class="muted" id="synctime">Terakhir sinkron: memuat…</div>`;
  const btn = el('btnsync');
  if (btn) btn.onclick = () => jalankanSinkron();
}

function setSyncLabel(btn, text){
  if (!btn) return;
  const span = typeof btn.querySelector === 'function' ? btn.querySelector('.sync-label') : null;
  if (span) span.textContent = text;
  else btn.textContent = text;
}

function resetSyncButton(btn, label){
  if (!btn) return;
  btn.disabled = false;
  if (typeof btn.removeAttribute === 'function') btn.removeAttribute('aria-busy');
  setSyncLabel(btn, label);
}

const kodeSinkron = () => { try { return localStorage.getItem('mpm_sync') || ''; } catch (e) { return ''; } };

async function jalankanSinkron(){
  const btn = el('btnsync');
  const labelEl = btn && typeof btn.querySelector === 'function' ? btn.querySelector('.sync-label') : null;
  const label = labelEl ? labelEl.textContent : btn ? btn.textContent : '';
  if (btn){ btn.disabled = true; if (typeof btn.setAttribute === 'function') btn.setAttribute('aria-busy', 'true'); setSyncLabel(btn, 'Menyinkronkan…'); }
  set('synctime', 'Menjalankan sinkronisasi…');
  let hasil = null, pesan = '';
  try {
    const r = await fetch(SYNC_URL, { method: 'POST', headers: { 'x-sync-secret': kodeSinkron() } });
    const j = await r.json().catch(() => ({}));
    if (r.status === 401 || r.status === 403){
      const kode = prompt('Kode sinkronisasi:');
      if (kode){ try { localStorage.setItem('mpm_sync', kode); } catch (e) {} }
      if (btn){ resetSyncButton(btn, label); }
      set('synctime', 'Kode dimasukkan. Tekan tombol Sinkronkan data lagi.');
      return;
    }
    if (!r.ok) throw new Error(j.detail || j.error || ('HTTP ' + r.status));
    hasil = j;
  } catch (e){
    pesan = e.message;
  }
  if (!hasil){
    if (btn){ resetSyncButton(btn, label); }
    set('synctime', `Sinkron otomatis tidak aktif di sini (${esc(pesan)}). Jalankan <code>python tools/sync.py --refresh</code> lalu muat ulang halaman.`);
    return;
  }
  /* tunggu status selesai (lokal: status dicek ke endpoint; hosting: lewat GitHub) */
  const mulai = Date.now();
  const batas = mulai - 30000;   /* run yang mulai sebelum ini dianggap run lama */
  const cek = async () => {
    let st = null;
    try { st = await (await fetch(SYNC_URL + '?t=' + Date.now())).json(); } catch (e) {}
    const umur = Math.round((Date.now() - mulai) / 1000);
    const mulaiRun = st && st.mulai ? Date.parse(st.mulai) : 0;
    /* setelah dispatch, GitHub bisa masih menampilkan run sebelumnya; jangan anggap selesai */
    const basi = mulaiRun > 0 && mulaiRun < batas;
    if (st && st.state === 'running' && !basi){
      set('synctime', `Sinkronisasi berjalan… ${umur}s (${esc(st.detail || '')})`);
      setTimeout(cek, 3000);
    } else if (st && !basi && st.state === 'error'){
      if (btn){ resetSyncButton(btn, label); }
      set('synctime', 'Sinkronisasi gagal: ' + esc(String(st.detail || '').slice(0, 160)));
    } else if (st && !basi && st.state === 'done'){
      set('synctime', `Sinkron selesai dalam ${umur}s. Memuat ulang…`);
      setTimeout(() => location.reload(), 800);
    } else if (umur > 300){
      if (btn){ resetSyncButton(btn, label); }
      set('synctime', 'Sinkron masih diproses. Muat ulang halaman beberapa saat lagi untuk melihat hasilnya.');
    } else {
      set('synctime', `Menunggu workflow dimulai… ${umur}s`);
      setTimeout(cek, 3000);
    }
  };
  setTimeout(cek, 1500);
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
  if (!host) return;
  host.innerHTML = MENU.map(m =>
    `<a href="${m.file}" class="${m.slug === active ? 'on' : ''}"${m.slug === active ? ' aria-current="page"' : ''}>${esc(m.label)}</a>`).join('');
  /* di layar sempit menu bisa digeser: bawa butir aktif ke tengah */
  if (host.querySelector){
    const aktif = host.querySelector('a.on');
    if (aktif) host.scrollLeft = Math.max(0, aktif.offsetLeft - (host.clientWidth - aktif.offsetWidth) / 2);
  }
}

function setupMobileMenu(){
  const nav = document.querySelector('nav.menu');
  const btn = el('menutoggle');
  if (!nav || !btn) return;
  const host = el('navmenu');
  const label = typeof btn.querySelector === 'function' ? btn.querySelector('.menu-toggle-label') : null;
  const setMenu = open => {
    nav.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', open ? 'Tutup menu' : 'Buka menu');
    if (label) label.textContent = open ? 'Tutup' : 'Menu';
    if (open && host) host.scrollTop = 0;
  };
  btn.addEventListener('click', () => setMenu(!nav.classList.contains('open')));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && nav.classList.contains('open')){
      setMenu(false);
      btn.focus();
    }
  });
  const desktop = window.matchMedia('(min-width: 721px)');
  const saatLebar = e => { if (e.matches) setMenu(false); };
  if (desktop.addEventListener) desktop.addEventListener('change', saatLebar);
  else desktop.addListener(saatLebar);
}

async function boot(){
  const page = document.body.dataset.page;
  drawFrame(page);
  setupMobileMenu();
  drawSync();
  try {
    if (page === 'index'){
      const site = await loadJSON('data/site.json');
      window.renderPage(site, null);
      const kh = el('kpis');
      if (kh && KPI_SRC.index) kh.innerHTML = kh.innerHTML + srcLine(KPI_SRC.index);
      const drive = site.folders.filter(f => f.id);
      set('treehost', drive.map(f => `<div class="fld"><a href="${f.url}" target="_blank" rel="noopener">${esc(f.menu)}</a>
        <span class="cnt">(${fnum(f.berkas)} berkas${f.subfolder ? ', ' + fnum(f.subfolder) + ' subfolder' : ''})</span></div>`).join(''));
      set('filecount', fnum(site.folders.reduce((a, f) => a + (f.jenis === 'kalender' ? 0 : f.berkas), 0)) + ' berkas');
      set('synced', 'Data disinkronkan: <b>' + esc(site.generated) + '</b>');
      set('synctime', 'Terakhir sinkron: <b>' + esc(site.generated) + '</b>');
      return;
    }
    const d = await loadJSON('data/' + page + '.json');
    document.title = d.menu + ' · Dashboard MPM Maospati';
    set('pagetitle', esc(d.menu));
    set('pagesub', esc(d.subjudul) + ' · ' + esc(d.deskripsi));
    if (d.folder && d.folder.kalender){
      /* halaman berbasis kalender publik, bukan folder Drive */
      set('drivebtn2', `<a class="btn" href="${d.folder.url}" target="_blank" rel="noopener">Buka kalender</a>`);
      set('pagemeta', `kalender publik: <b>${esc(d.folder.name)}</b> · <b>${fnum(d.statistik.berkas)}</b> agenda terbaca`);
      set('treehost', `<p class="muted">Halaman ini bersumber dari kalender publik Google, bukan folder Drive.</p>`);
      set('treecard', 'Sumber: Google Calendar');
      set('filecount', 'kalender');
    } else if (d.folder && d.folder.sheet){
      /* halaman berbasis spreadsheet publik, bukan folder Drive */
      set('drivebtn2', `<a class="btn" href="${d.folder.url}" target="_blank" rel="noopener">Buka spreadsheet</a>`);
      set('pagemeta', `spreadsheet: <b>${esc(d.folder.name)}</b> · <b>${fnum(d.statistik.indikator)}</b> indikator`);
      set('treehost', '<p class="muted">Halaman ini bersumber dari Google Sheets, bukan folder Drive.</p>');
      set('treecard', 'Sumber: Google Sheets');
      set('filecount', 'spreadsheet');
    } else {
      set('drivebtn2', driveBtn(d.folder.url));
      set('pagemeta', `<b>${fnum(d.statistik.berkas)}</b> berkas · <b>${fnum(d.statistik.subfolder)}</b> subfolder ·
        folder: <a href="${d.folder.url}" target="_blank" rel="noopener">${esc(d.folder.name)}</a>`);
      if (d.struktur) set('treehost', folderTree(d.struktur, 0));
      set('filecount', d.files.length + ' berkas');
    }
    if (window.renderPage) window.renderPage(d.analisa, d);
    /* keterangan sumber untuk baris KPI (di luar kartu) */
    const kh = el('kpis');
    if (kh && KPI_SRC[page]) kh.innerHTML = kh.innerHTML + srcLine(KPI_SRC[page]);
    /* lengkapi keterangan sumber pada panel yang berkasnya dideteksi otomatis */
    const det = d.analisa && d.analisa.kpi ? (d.analisa.kpi.sumber || d.analisa.kpi.sumberFile) : null;
    if (det){
      document.querySelectorAll('[data-auto-sumber]').forEach(function(e){
        e.innerHTML += ' &middot; terdeteksi: <b>' + esc(det) + '</b>';
      });
    }
    set('synced', 'Data disinkronkan: <b>' + esc(d.generated || '-') + '</b>');
    set('synctime', 'Terakhir sinkron: <b>' + esc(d.generated || '-') + '</b>');
  } catch (e){
    const b = el('banner');
    if (b){
      b.classList.add('on');
      b.innerHTML = 'Gagal memuat data (' + esc(e.message) + '). Jalankan <code>python tools/sync.py --refresh</code> lalu buka situs lewat web server: <code>python tools/serve.py</code> (bukan dengan klik dua kali berkas HTML).';
    }
    console.error(e);
  }
}
document.addEventListener('DOMContentLoaded', boot);
