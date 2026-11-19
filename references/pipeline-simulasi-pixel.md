# Pipeline Simulasi Pixel-Art Panjang (gaya WorldBox)

Baca file ini untuk video pixel-art atau simulasi dengan banyak karakter, durasi panjang (dibagi beberapa bagian), dan shot aktivitas. Kode pendukung: `scripts/karakter_pixel.py`, `scripts/pixel_kit.py`, `scripts/shot_library.py`, `scripts/kamera_pixel.py`, `scripts/render_parts.py`.

## Daftar isi
1. Arsitektur: satu dunia deterministik, banyak bagian
2. Membagi voiceover menjadi bagian
3. Resolusi internal 960x540
4. Dunia, agen, dan aksi
5. Jadwal shot dari SRT
6. Kamera, HUD, dan transisi
7. Efek suara
8. Menjalankan render
9. Jebakan yang sudah terjadi

## 1. Arsitektur: satu dunia deterministik, banyak bagian

Tulis dunia sebagai fungsi `render(T)` yang hanya bergantung pada waktu global `T` (detik pada voiceover utuh). Semua yang bergerak (awan, orang, air, partikel, bangunan yang muncul) dihitung dari `T`, bukan dari status yang disimpan antar frame. Akibatnya:
- Tiap bagian video tinggal memanggil `render(T)` untuk jendela waktunya, dan bisa dirender ulang sendiri tanpa memengaruhi bagian lain.
- Bagian bisa diuji dengan memanggil `render(t)` pada satu waktu dan menyimpan PNG.
- Bangunan dan peristiwa dijadwalkan pada waktu kalimat di SRT, jadi dunia dan narasi selalu sinkron.

Untuk kejadian acak, pakai generator acak dengan seed tetap yang dibuat saat impor, bukan saat render.

## 2. Membagi voiceover menjadi bagian

Hanya setelah user menyetujui pembagian (voiceover lebih dari batas 180 detik per file).
1. Jalankan `ffmpeg -i VO -af silencedetect=noise=-38dB:d=0.3 -f null -` dan cari jeda hening dekat titik pembagian yang diinginkan (awal bab seperti "tahun ke-…").
2. Potong di dalam jeda, tepat sebelum kalimat berikutnya dimulai, sehingga tidak ada kata terpotong dan setiap bagian dimulai dari awal kalimat. Titik potong di tengah rangkaian kata ("…kemajuan mereka | tahun ke 100") dihindari, tapi kalau itu satu-satunya jeda, potong di sana dan sampaikan ke user.
3. Tiap bagian: durasi video = ceil(panjang voiceover bagian + 2,5) dan harus ≤ 180 detik. Hitung ulang jumlah frame dan verifikasi tiap file.
4. Konvensi waktu: voiceover bagian mulai di detik ke-1 video, jadi `T = awal_bagian - 1.0 + n / fps`. Dunia sudah berjalan sebelum suara mulai, dan itulah tempat hook.
5. Beri tahu user titik potong, jumlah bagian, dan durasi tiap bagian.

`scripts/render_parts.py` mengerjakan langkah 3 sampai 4 dan memverifikasi hasilnya lewat `mix_and_verify.sh`.

## 3. Resolusi internal 960x540

Render pixel-art kecil lalu perbesar dengan `scale=1920:1080:flags=neighbor`. Pilih resolusi internal dari ukuran terkecil yang masih terbaca:
- **480x270 (4x)** hanya untuk visual tanpa orang kecil (bentuk, ikon, tipografi). Orang 1x2 piksel di sini menjadi titik, dan itu terjadi di versi pertama proyek WorldBox.
- **960x540 (2x)** untuk simulasi dengan orang. Sprite manusia 13 unit (`k=1`) menjadi sekitar 26 px di layar akhir, dan kepala, badan, tangan, kaki masih terbedakan. Close-up memakai `k=8` sampai `k=10`.
- Terrain boleh dirender di 480x270 lalu digandakan 2x (`np.repeat`), dan orang digambar langsung di 960x540. Hasilnya tampak kasar di terrain dan halus di orang, dan itu cocok untuk gaya ini.

Jam render yang diukur di proyek WorldBox (CPU tunggal, 960x540): sekitar 17 sampai 20 frame per detik termasuk encode, jadi video 161 detik (4.830 frame) selesai sekitar 4 menit.

## 4. Dunia, agen, dan aksi

- **Agen:** tiap orang punya titik tujuan acak (seed tetap) di sekitar "pusat" yang bergerak sesuai adegan, dan berjalan antar titik dengan jeda. Posisi dihitung vektor dari `T` sehingga ratusan agen murah.
- **Pemilihan aksi per agen:** bergerak = `walk` (atau `carry`), berhenti di zona ladang = `hoe`, berhenti dekat peristiwa menebang = `chop`, dan seterusnya. Aksi `hammer` hanya dipakai kalau ada bangunan yang baru dibuat, supaya tidak ada orang memalu tanpa alasan.
- **Batasi jumlah orang yang digambar** (misalnya 110 dan 150 per sisi). Ratusan sprite 13 px di layar yang sama menumpuk dan tidak terbaca. Pertumbuhan populasi cukup ditunjukkan lewat bangunan dan pemukiman.
- **Arah:** balik sprite (`flip`) sesuai arah gerak.
- **Variasi:** warna baju, kulit, rambut dari indeks agen. Warna rambut abu-abu menandai generasi tua, dan baju gelap menandai pakaian musim dingin.
- Urutkan penggambaran berdasarkan koordinat y supaya yang di depan menutupi yang di belakang.

## 5. Jadwal shot dari SRT

1. Baca SRT per kalimat, catat kegiatan (lihat `panduan-karakter-dan-aksi.md`).
2. Tulis rencana sebagai daftar `(idx_mulai, idx_selesai, jenis_shot, opsi)` dan buat jadwal dengan `shot_library.buat_jadwal('VO.srt', rencana)`. Shot lebih pendek dari 1,4 detik dibuang, jadi perpanjang ke kalimat berikutnya agar aksi terbaca.
3. Shot mengikuti waktu SRT, dan titik potong yang dihitung dari `silencedetect` hanya dipakai untuk memotong bagian. Timestamp SRT otomatis bisa meleset (kalimat panjang dengan jeda tersembunyi), jadi cocokkan beberapa titik dengan `silencedetect` dan akui kalau hanya perkiraan.
4. Untuk tiap kegiatan yang disebut, pastikan ada shot, termasuk kegiatan singkat. Setelah render, ekstrak satu frame per shot dan periksa.

## 6. Kamera, HUD, dan transisi

- **Kamera nyaman (`scripts/kamera_pixel.py`):**
  1. Perbesar frame dunia dengan nearest ke resolusi akhir dulu (`naik2x`, 960x540 menjadi 1920x1080), lalu zoom dan pan di resolusi akhir dengan resampling bilinear dan posisi pecahan (`terapkan`). Zoom nearest pada rasio tidak bulat membuat piksel digandakan tidak merata dan posisi tepi melompat antar frame, dan itulah yang terlihat sebagai getar atau kasar. Pada uji statis (zoom 1,0 ke 1,6), jitter tepi batang pohon turun dari 0,58 px (langkah 0, 2, atau 4 px per frame) menjadi 0,07 px (langkah 2,2 sampai 2,6 px). Jalankan `python3 scripts/kamera_pixel.py` untuk mengulang pengukuran.
  2. Tidak ada goyangan sinus, gerak melayang, atau napas zoom. Gerak kecil terus-menerus di pixel-art memperburuk getar dan melelahkan mata.
  3. Kamera bergerak hanya lewat transisi berarah dengan easing lembut (`pandangan`, smootherstep, 3 detik atau lebih), lalu diam. Jeda minimal sekitar 8 detik antar perpindahan, laju zoom paling banyak sekitar 0,2x per detik, dan zoom di kisaran 1,0 sampai 2,4. Hindari zoom masuk lalu keluar dalam waktu singkat, dan untuk pindah antar sisi layar utamakan pan atau potongan, bukan zoom keluar lalu masuk. Untuk video panjang (beberapa menit) jumlah perpindahan kamera harus sedikit, karena gerak yang sering membuat pusing.
  4. Jalankan `periksa_kamera(keys)` pada daftar keyframe sebelum merender dan perbaiki setiap peringatan.
  5. Alternatif paling tajam: mode `'bulat'`, zoom hanya kelipatan bulat dan pindah pandangan dengan potongan atau crossfade.
  6. "Selalu bergerak" berarti isi gambar hidup (orang, awan, air, partikel), bukan kamera yang terus bergerak.
- **Alur frame:** dunia 960x540, naik2x, kamera di 1920x1080, HUD di atasnya. Frame shot aktivitas (960x540) dinaikkan dengan `naik2x` sebelum crossfade dengan frame dunia. Jalankan `render_parts.py` dengan `--internal 1920x1080`.
- **HUD di kanvas kecil:** gambar HUD sesudah kamera pada salinan kecil dari frame (`hud_overlay(frame, fungsi_hud, faktor=4)`), bandingkan dengan aslinya untuk mendapatkan mask, lalu timpa piksel HUD ke frame besar. HUD tidak ikut zoom. Font bitmap 5x7 di `pixel_kit.py` dan `panel()` tetap konsisten, tanpa menulis ulang HUD untuk dua resolusi.
- **Font bitmap:** hanya karakter yang ada di tabel glyph (`pixel_kit._G`) yang tampil. Karakter lain jadi "?" (misalnya "&"), jadi pakai kata ("DAN") atau tambahkan glyph.
- **Transisi dunia ke shot:** crossfade 0,25 detik (`shot_library.alpha_transisi`). HUD tetap menyala selama shot, kecuali elemen yang menutupi (chip bawah) disembunyikan.
- **Label teks tetap bukan caption:** judul hook, nama wilayah, badge tahun, dan chip pencapaian boleh. Kalimat narasi tidak boleh ditulis di layar.

## 7. Efek suara

Efek dibuat dari kode (derau, sinus, jatuh cepat) dan tanpa musik latar kalau user melarang musik. Lapisan yang dipakai: hujan, angin, kicau, ketukan pembangunan, petir, whoosh pergantian tahun, dan ketukan alat pada shot aksi. Ketukan mengikuti `strike(T)`: pada `shot_library` frame mengayun terjadi tiap `(2m+1)/3` detik, jadi hitung waktu ketukan dengan rumus yang sama supaya suara tepat saat alat turun. Normalkan puncak efek (sekitar 0,5) sebelum dicampur dengan voiceover, dan voiceover tetap dominan.

## 8. Menjalankan render

```
setsid nohup python3 scripts/render_parts.py --modul proyek.py --vo VO.MP3 \
  --bagian "0:158.4,158.4:302.6,..." --internal 960x540 --keluar out \
  --mix scripts/mix_and_verify.sh > render.log 2>&1 < /dev/null &
```
`proyek.py` mendefinisikan `render(T)` dan, kalau perlu, `gen_sfx(T0, T1)`. Pantau `render.log`. Proses tanpa `setsid` mati saat panggilan tool berakhir. `--hanya N` merender ulang satu bagian saja.

## 9. Jebakan yang sudah terjadi

- Proses render di latar belakang mati saat panggilan tool selesai: pakai `setsid nohup`.
- Interpolasi keyframe error untuk waktu sebelum keyframe pertama (hook di waktu negatif).
- Zoom kamera di bawah 1 karena goyangan: `max(1.0, zoom)` dulu.
- **Zoom terlihat kasar, bergetar, dan membuat pusing di video panjang:** zoom nearest pada rasio tidak bulat, ditambah goyangan sinus dan perpindahan kamera tiap 3 sampai 5 detik. Pakai `kamera_pixel.py` dan aturan kamera di atas.
- Efek partikel menulis di indeks di luar kanvas (kolom ke-960): batasi indeks dengan `min`/`%` yang benar.
- Penempatan bangunan acak gagal karena ruang penuh: kurangi jarak minimum bertahap.
- Chip pencapaian terpotong di tepi kanan: bungkus ke baris atas bila melebihi lebar.
- Glyph tidak ada ("&"): ganti kata.
- Orang digambar 1x2 piksel pada 480x270: terbaca sebagai titik. Gunakan sprite manusia dan resolusi internal 960x540.
- Shot aksi hilang untuk kegiatan yang disebut singkat: daftar aktivitas dibuat dari SRT sebelum membangun apa pun.
