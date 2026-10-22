/* uji_render.mjs — menjalankan assets/app.js + assets/pages/<slug>.js di DOM tiruan
   dengan data/<slug>.json yang asli, lalu melaporkan hasil render tiap halaman.
   Pakai: node tools/uji_render.mjs   (tanpa dependensi npm) */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
const ROOT = path.resolve(here, '..');
const PAGES = ['index', 'smd-mmd', 'laporan-posyandu', 'ruk', 'dokumentasi',
               'data-posyandu', 'data-kader', 'spj-bok', 'laporan-kegiatan-dinkes', 'jadwal-promkes'];

class El {
  constructor(id = '') {
    this.id = id; this._html = ''; this._value = null; this.dataset = {}; this._cls = new Set();
    this.classList = {
      add: c => this._cls.add(c), remove: c => this._cls.delete(c),
      contains: c => this._cls.has(c), toggle: (c, on) => (on === false ? this._cls.delete(c) : this._cls.add(c)),
    };
  }
  set innerHTML(v) { this._html = String(v); }
  get innerHTML() { return this._html; }
  set textContent(v) { this._html = String(v); }
  get textContent() { return this._html.replace(/<[^>]+>/g, ' '); }
  set className(v) { this._cls = new Set(String(v).split(/\s+/).filter(Boolean)); }
  get className() { return [...this._cls].join(' '); }
  /* meniru <select>: utamakan atribut value, kalau tidak ada pakai teks opsi pertama */
  set value(v) { this._value = String(v); }
  get value() {
    if (this._value !== null) return this._value;
    const v = /<option[^>]*\svalue="([^"]*)"/.exec(this._html);
    if (v) return v[1];
    const m = /<option[^>]*>([^<]*)</.exec(this._html);
    return m ? m[1] : '';
  }
  onchange() {} oninput() {}
}

function makeDOM(ids) {
  const els = new Map();
  ids.forEach(i => els.set(i, new El(i)));
  /* meniru DOM: elemen yang muncul dari innerHTML tetap bisa ditemukan getElementById */
  const cari = id => {
    for (const el of els.values()){
      if (new RegExp('id="' + id + '"').test(el._html)){ const baru = new El(id); els.set(id, baru); return baru; }
    }
    return null;
  };
  const doc = {
    title: '', body: { dataset: { page: '' } },
    getElementById: id => els.get(id) || cari(id),
    querySelector: sel => { const m = /^#(.+)$/.exec(sel); return m ? (els.get(m[1]) || cari(m[1])) : null; },
    querySelectorAll: () => [],
    addEventListener: (ev, fn) => { if (ev === 'DOMContentLoaded') doc._boot = fn; },
    createElement: () => new El(),
  };
  return { doc, get: id => els.get(id) || cari(id), els };
}

const base = {
  console, URLSearchParams, setTimeout, setInterval: () => 0, clearInterval: () => 0,
  Date, Math, JSON, Number, String, Boolean, Array, Object, RegExp, isNaN, parseInt, parseFloat, Promise,
  location: { reload: () => { base.__reloaded = true; }, pathname: '/' },
  localStorage: { _d: {}, getItem(k) { return this._d[k] ?? null; }, setItem(k, v) { this._d[k] = String(v); } },
  prompt: () => null, __reloaded: false,
};

async function run(slug) {
  const htmlSrc = fs.readFileSync(path.join(ROOT, slug + '.html'), 'utf8');
  const ids = [...htmlSrc.matchAll(/id="([^"]+)"/g)].map(m => m[1]);
  const dom = makeDOM(ids);
  dom.doc.body.dataset.page = slug;
  const inlineMode = process.env.UJI_MODE === 'inline';
  const sandbox = {
    ...base,
    window: { location: { pathname: '/' + slug + '.html', search: '' } },
    document: dom.doc,
    fetch: inlineMode
      ? async () => { throw new Error('fetch diblokir (uji mode inline)'); }
      : async (p, opts) => {
          if (String(p).includes('/api/sync')) {
            const mode = opts && opts.method === 'POST' ? 'POST' : 'GET';
            const body = mode === 'POST' ? { ok: true, state: 'running', detail: 'uji' } : { state: 'done', detail: 'uji selesai' };
            return { ok: true, status: 200, json: async () => body, text: async () => JSON.stringify(body) };
          }
          const file = path.join(ROOT, p);
          if (!fs.existsSync(file)) return { ok: false, status: 404, json: async () => { throw new Error('404 ' + p); }, text: async () => '' };
          const txt = fs.readFileSync(file, 'utf8');
          return { ok: true, status: 200, text: async () => txt, json: async () => JSON.parse(txt) };
        },
  };
  sandbox.globalThis = sandbox;
  const ctx = vm.createContext(sandbox);
  if (inlineMode){
    /* jalankan blok data tertanam seperti yang ada di berkas HTML */
    const m = /<script>window\.__DATA__[\s\S]*?<\/script>/.exec(htmlSrc);
    if (m) vm.runInContext(m[0].replace(/^<script>/, '').replace(/<\/script>$/, ''), ctx, { filename: 'inline-data' });
  }
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/app.js'), 'utf8'), ctx, { filename: 'app.js' });
  const pageFile = path.join(ROOT, 'assets/pages', slug + '.js');
  if (fs.existsSync(pageFile)) vm.runInContext(fs.readFileSync(pageFile, 'utf8'), ctx, { filename: slug + '.js' });
  if (dom.doc._boot) await dom.doc._boot();
  await new Promise(r => setTimeout(r, 30));

  const html = id => (dom.get(id) ? dom.get(id).innerHTML : '');
  const all = ids.map(html).join('\n');
  const count = (s, re) => (s.match(re) || []).length;
  return {
    slug, title: dom.doc.title,
    kpi: count(html('kpis'), /class="card kpi"/g),
    cards: count(html('cards'), /class="card"/g),
    rows: count(all, /<tr>/g),
    cells: count(all, /class="cell"/g),
    bars: count(all, /class="bar"/g),
    files: count(html('treehost'), /class="file"/g),
    folders: count(html('treehost'), /class="fld"/g),
    drive: /drive\.google\.com/.test(html('drivebtn2')),
    kalBtn: /Buka kalender/.test(html('drivebtn2')),
    driveHeader: /drive\.google\.com/.test(html('drivebtn')),
    syncBtn: /Sinkronkan data/.test(html('drivebtn')),
    syncTime: (html('synctime') || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 80),
    menu: count(html('navmenu'), /<a /g),
    banner: (dom.get('banner') ? dom.get('banner').className : '').includes('on'),
    bad: /undefined|NaN|\[object Object\]/.test(all),
    srcCount: (all.match(/class="src"/g) || []).length + (htmlSrc.match(/class="src"/g) || []).length,
    iframe: (all.match(/<iframe[^>]*calendar\.google\.com/g) || []).length + (htmlSrc.match(/<iframe[^>]*calendar\.google\.com/g) || []).length,
    srcAuto: (htmlSrc.match(/data-auto-sumber/g) || []).length,
    badSnippet: (() => { const m = /undefined|NaN|\[object Object\]/.exec(all); return m ? all.slice(Math.max(0, m.index - 70), m.index + 40).replace(/\s+/g, ' ') : ''; })(),
    sample: html('kpis').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 150),
  };
}

let gagal = 0;
for (const slug of PAGES) {
  try {
    const r = await run(slug);
    const ok = !r.bad && !r.banner && r.menu === 10 && r.syncBtn && !r.driveHeader &&
      (slug === 'index' ? r.srcCount >= 2
        : slug === 'jadwal-promkes' ? (r.iframe === 1 && r.kalBtn && r.srcCount >= 4)
        : (r.drive && r.kpi > 0 && r.srcCount >= 3));
    if (!ok) gagal++;
    console.log(`${ok ? 'OK ' : '!! '}${slug.padEnd(25)} kpi=${String(r.kpi).padStart(2)} kartu=${String(r.cards).padStart(2)}` +
      ` baris=${String(r.rows).padStart(4)} sel=${String(r.cells).padStart(4)} bar=${String(r.bars).padStart(3)}` +
      ` berkas=${String(r.files).padStart(3)} folder=${String(r.folders).padStart(2)} menu=${r.menu}` +
      ` sumber=${String(r.srcCount).padStart(2)}${r.srcAuto ? '(auto ' + r.srcAuto + ')' : ''} iframe=${r.iframe}` +
      ` drive-dibawah=${r.drive ? 'ya' : 'TIDAK'} tombol-sinkron=${r.syncBtn ? 'ada' : 'TIDAK ADA'}` +
      `${r.driveHeader ? ' DRIVE-MASIH-DI-HEADER' : ''}${r.banner ? ' BANNER-ERROR' : ''}${r.bad ? ' TEKS-RUSAK' : ''}`);
    console.log(`     ${r.syncTime}`);
    if (r.bad) console.log(`     >> cuplikan: ${r.badSnippet}`);
  } catch (e) {
    gagal++;
    console.log(`!! ${slug}: ${e.message}`);
    console.log(`     ${(e.stack || '').split('\n').slice(1, 4).map(s => s.trim()).join('\n     ')}`);
  }
}
console.log(`\n${PAGES.length - gagal}/${PAGES.length} halaman berhasil dirender dengan data asli`);

/* --- uji tombol Sinkron: tekan lalu pastikan statusnya berubah --- */
try {
  const htmlSrc = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const ids = [...htmlSrc.matchAll(/id="([^"]+)"/g)].map(m => m[1]);
  const dom = makeDOM(ids);
  dom.doc.body.dataset.page = 'index';
  const sandbox = {
    ...base,
    window: { location: { pathname: '/index.html', search: '' } },
    document: dom.doc,
    fetch: async (p, opts) => {
      if (String(p).includes('/api/sync')) {
        const body = opts && opts.method === 'POST'
          ? { ok: true, state: 'running', detail: 'mengunduh berkas' }
          : { state: 'done', detail: '9 berkas data diperbarui' };
        return { ok: true, status: 200, json: async () => body };
      }
      const txt = fs.readFileSync(path.join(ROOT, p), 'utf8');
      return { ok: true, status: 200, json: async () => JSON.parse(txt), text: async () => txt };
    },
  };
  sandbox.globalThis = sandbox;
  const ctx = vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/app.js'), 'utf8'), ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/pages/index.js'), 'utf8'), ctx);
  await dom.doc._boot();
  const btn = dom.get('btnsync');
  if (!btn || typeof btn.onclick !== 'function') throw new Error('tombol Sinkron tidak ditemukan di header');
  const sebelum = dom.get('synctime').textContent.replace(/\s+/g, ' ').trim();
  btn.onclick();
  await new Promise(r => setTimeout(r, 2600));
  const sesudah = dom.get('synctime').textContent.replace(/\s+/g, ' ').trim();
  const lulus = /sinkron/i.test(sesudah) && sesudah !== sebelum;
  if (!lulus) gagal++;
  console.log(`${lulus ? 'OK ' : '!! '}tombol Sinkron  sebelum="${sebelum}"  ->  sesudah="${sesudah}"`);
} catch (e) {
  gagal++;
  console.log(`!! tombol Sinkron: ${e.message}`);
}

console.log(gagal ? `\n${gagal} pemeriksaan gagal` : '\nSemua pemeriksaan lulus');
process.exit(gagal ? 1 : 0);
