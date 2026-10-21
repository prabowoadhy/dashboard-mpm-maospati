/**
 * api/sync.js — endpoint tombol "Sinkron sekarang" saat dashboard di-hosting (Vercel).
 *
 * Situs statis tidak bisa menjalankan Python, jadi endpoint ini memicu workflow
 * GitHub Actions (.github/workflows/sync.yml) yang memang menjalankan tools/sync.py
 * dan meng-commit hasilnya. Setelah Actions selesai, hosting otomatis menayangkan
 * data terbaru.
 *
 * Pemasangan di Vercel — Settings → Environment Variables:
 *   GITHUB_REPO    = prabowoadhy/dashboard-mpm-maospati
 *   GITHUB_TOKEN   = token GitHub dengan izin  repo + workflow   (wajib, jangan di-commit)
 *   GITHUB_WORKFLOW= sync.yml            (opsional, default sync.yml)
 *   SYNC_SECRET    = kode rahasia bebas  (opsional; kalau diisi, halaman akan menanyakan kode ini)
 *
 * GET  /api/sync  -> status proses terakhir
 * POST /api/sync  -> jalankan workflow
 */
const REPO = process.env.GITHUB_REPO;
const TOKEN = process.env.GITHUB_TOKEN;
const WORKFLOW = process.env.GITHUB_WORKFLOW || 'sync.yml';
const SECRET = process.env.SYNC_SECRET || '';

const API = 'https://api.github.com';
const headers = () => ({
  Authorization: `Bearer ${TOKEN}`,
  Accept: 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'User-Agent': 'dashboard-mpm',
});

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (!REPO || !TOKEN) {
    return res.status(503).json({
      state: 'error',
      detail: 'Sinkron daring belum disiapkan: variabel GITHUB_REPO dan GITHUB_TOKEN belum diisi di hosting.',
    });
  }
  if (SECRET && req.headers['x-sync-secret'] !== SECRET) {
    return res.status(401).json({ state: 'error', detail: 'Kode sinkronisasi salah atau belum diisi.' });
  }

  try {
    if (req.method === 'POST') {
      const r = await fetch(`${API}/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`, {
        method: 'POST',
        headers: { ...headers(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ ref: 'main' }),
      });
      if (r.status !== 204) {
        const t = await r.text();
        return res.status(502).json({ state: 'error', detail: `GitHub menolak (${r.status}): ${t.slice(0, 160)}` });
      }
      return res.status(200).json({
        state: 'running',
        detail: 'Workflow GitHub Actions dijalankan',
        mulai: new Date().toISOString(),
      });
    }

    /* GET: status proses terakhir */
    const r = await fetch(`${API}/repos/${REPO}/actions/workflows/${WORKFLOW}/runs?per_page=1`, { headers: headers() });
    if (!r.ok) {
      const t = await r.text();
      return res.status(502).json({ state: 'error', detail: `Tidak bisa membaca status (${r.status}): ${t.slice(0, 160)}` });
    }
    const j = await r.json();
    const run = (j.workflow_runs || [])[0];
    if (!run) return res.status(200).json({ state: 'idle', detail: 'belum ada riwayat sinkronisasi' });

    const state = run.status !== 'completed' ? 'running'
      : run.conclusion === 'success' ? 'done'
      : 'error';
    return res.status(200).json({
      state,
      detail: `run #${run.run_number} — ${run.status}${run.conclusion ? '/' + run.conclusion : ''}`,
      mulai: run.run_started_at,
      selesai: run.updated_at,
      url: run.html_url,
    });
  } catch (e) {
    return res.status(502).json({ state: 'error', detail: String(e.message || e) });
  }
}
