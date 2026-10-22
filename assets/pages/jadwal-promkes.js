/* Jadwal Promkes · kalender publik Google + daftar agenda dari feed ICS */
window.renderPage = function(a){
  const k = a.kpi || {}, agenda = a.agenda || [], bulanIni = a.bulanIni || [], perBulan = a.perBulan || [];
  set('kpis', kpiCards([
    { label: 'Agenda terbaca', value: fnum(k.total), sub: 'seluruh agenda pada kalender publik' },
    { label: 'Mendatang', value: fnum(k.mendatang), sub: 'belum lewat, urut terdekat' },
    { label: '30 hari ke depan', value: fnum(k.dekat30), sub: 'rencana terdekat' },
    { label: 'Bulan ini', value: fnum(k.bulanIni), sub: 'agenda bulan berjalan' },
    { label: 'Agenda berikutnya', value: k.berikutnya || '–', sub: 'dari kalender publik', small: true },
    { label: 'Sumber', value: 'Google Calendar', sub: k.sumber || '', small: true },
  ]));

  set('c-agenda', agenda.length
    ? '<ul class="agenda">' + agenda.slice(0, 10).map((x, i) => `<li>
        <span class="tgl">${esc(x.tanggal.split(' ').slice(0, 2).join(' '))}</span>
        <span class="ket"><b>${esc(x.nama)}</b>
          <span class="muted">${x.seharian ? 'seharian' : esc(x.jam || '')}${x.lokasi ? ' · ' + esc(x.lokasi) : ''}</span></span>
      </li>`).join('') + '</ul>'
    : '<p class="muted">Belum ada agenda mendatang pada kalender.</p>');

  const mp = Math.max(1, ...perBulan.map(x => x.jumlah));
  set('c-perbulan', barRows(perBulan.map(x => ({ label: x.bulan, value: x.jumlah, max: mp, note: x.jumlah + ' agenda' }))));

  const kolom = [
    { label: 'Tanggal' }, { label: 'Jam' }, { label: 'Kegiatan' }, { label: 'Lokasi' },
    { label: 'Catatan', html: r => r.catatan ? esc(r.catatan.slice(0, 120)) : '' }
  ];
  const baris = x => ({ tanggal: x.tanggal, jam: x.seharian ? 'seharian' : (x.jam + (x.jamSelesai ? '–' + x.jamSelesai : '')),
                        nama: x.nama, lokasi: x.lokasi, catatan: x.catatan });
  set('t-bulanini', bulanIni.length ? table(kolom, bulanIni.map(baris))
    : '<tbody><tr><td class="muted">Tidak ada agenda pada bulan ini.</td></tr></tbody>');
  set('t-agenda', agenda.length ? table(kolom, agenda.map(baris))
    : '<tbody><tr><td class="muted">Tidak ada agenda mendatang.</td></tr></tbody>');

  set('c-catatan', `<ul class="tl">
    <li>Halaman ini <b>tidak memakai berkas Excel</b> · sumbernya kalender publik Google
      <b>${esc((a.kalender || {}).sumber || '')}</b> (${esc(k.sumber || '')}).</li>
    <li>Menambah/mengubah jadwal: buka Google Calendar akun tersebut, buat agenda seperti biasa.
      Setelah itu tekan <b>Sinkronkan data</b> agar daftar "Agenda 30 Hari ke Depan" di halaman ini ikut diperbarui.</li>
    <li>Tampilan kalender di atas selalu menampilkan jadwal terbaru secara langsung (langsung dari Google),
      jadi tidak perlu sinkron untuk melihat perubahan pada kalender.</li>
    <li>Bila nama kegiatan mengikuti pola yang sama dengan berkas Excel (mis. <code>MMD Sugihwaras</code>,
      <code>Posyandu Maospati</code>), penamaan desa sebaiknya seragam supaya mudah dicocokkan.</li>
  </ul>`);
};