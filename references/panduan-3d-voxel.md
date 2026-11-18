# Panduan Gaya 3D Voxel (Minecraft)

Baca file ini kalau user meminta animasi 3D, gaya Minecraft, voxel, blok, atau low-poly. Teknik render dan kodenya ada di `render-3d-voxel.md`.

## Daftar isi
1. Kapan memakai gaya ini
2. Bahasa visual voxel
3. Membangun dunia dari kotak
4. Kamera
5. Animasi yang cocok untuk voxel
6. Menyinkronkan dengan voiceover
7. Teks di layar dan audio
8. Batas dan kejujuran

## 1. Kapan memakai gaya ini

Pakai kalau user menyebut: "3D", "Minecraft", "voxel", "blok", "low-poly", atau mengunggah referensi yang jelas 3D bergaya blok. Kalau user hanya meminta "motion graphic" tanpa menyebut 3D, tetap pakai gaya 2D di `panduan-visual.md`. Kalau ragu, tanyakan satu kali di Tahap 2 (2D editorial atau 3D voxel).

Voxel cocok untuk topik yang punya ruang dan benda: mesin, kendaraan, bangunan, proses fisik, rantai sebab-akibat yang bisa dipentaskan. Kurang cocok untuk topik yang isinya angka dan diagram abstrak, yang lebih jelas di 2D.

## 2. Bahasa visual voxel

- Semua benda disusun dari kotak. Jangan mencampur dengan bentuk melengkung halus; kekhasan gaya ini adalah kekasarannya yang disengaja.
- Palet jenuh dan sedikit warna. Satu warna dominan per adegan, satu warna aksen untuk benda yang sedang dijelaskan.
- Shading datar per sisi (atas paling terang, sisi samping lebih gelap) sudah ditangani `voxel.py`. Jitter warna kecil antar kotak memberi kesan tekstur.
- `pixel=2` atau `3` di `render()` membuat tampilan blok pixel yang khas. Tanpa itu hasilnya lebih halus dan mirip render low-poly.
- Kabut jarak (`fog`) membuat latar menyatu dan menyembunyikan tepi dunia.
- Skala konsisten: tetapkan 1 kotak = satu satuan nyata (misalnya 1 m) dan jaga rasio antar benda.

## 3. Membangun dunia dari kotak

1. Buat tiap benda utama sebagai `Model` (fungsi pembangun kecil, mis. `make_ship()`), lalu taruh dengan `Scene.add(model, pos, yaw, pitch, roll)`.
2. Benda yang bergerak: ubah `pos` atau rotasi per frame dari fungsi waktu `t`. Jangan membangun ulang model tiap frame kalau tidak berubah (simpan di luar loop).
3. Air, tanah, atau lantai: pakai `water_grid()` untuk permukaan bergelombang dari kolom kotak, atau `floor_quad()` untuk bidang datar besar yang murah.
4. Jaga jumlah kotak: sekitar 1.000 sampai 4.000 per frame masih wajar. Lebih dari itu, kurangi detail air atau jauhkan benda dari kamera.
5. Benda yang butuh penjelasan (penampang, bagian dalam) dibuat dengan membuang satu sisi kotak atau menggunakan model terbelah dua yang dibuka dengan animasi.

## 4. Kamera

Kamera adalah alat bercerita utama. Variasikan antar adegan:
- Orbit pelan mengitari benda utama (hook, pengenalan).
- Dolly masuk atau zoom ke bagian yang dijelaskan (baling-baling, mesin).
- Tampak atas (top-down) untuk peta, jarak, dan pergerakan antar benda.
- Tampak samping untuk penampang dan hubungan antar benda.
- Gerak kamera memakai easing (lihat `panduan-visual.md` bagian 4). Hindari gerak konstan yang kaku, dan hindari putaran cepat yang membuat mual.

Tentukan `fov` 50 sampai 65 untuk tampilan alami. Portrait 1080x1920 butuh benda utama dibingkai vertikal, dekatkan kamera atau naikkan posisinya.

## 5. Animasi yang cocok untuk voxel

- Perpindahan dan rotasi benda utuh (kapal melaju, roda berputar, pintu terbuka).
- Benda tersusun atau terurai blok demi blok (membangun, membongkar, ledakan blok).
- Gelombang, riak, dan partikel dari kotak kecil yang naik, turun, atau jatuh.
- Penekanan: benda utama membesar sedikit, berkedip warna, atau diberi panah blok melayang.
- Transisi antar adegan: kamera menembus benda, wipe berbentuk blok, atau potongan cepat searah gerak.

## 6. Menyinkronkan dengan voiceover

Sama dengan 2D: voiceover adalah acuan timing. Buat daftar cue dari jeda audio, lalu pasang animasi ke cue itu. Satu adegan, satu ide visual. Kalau satu kalimat membahas dua hal, bagi menjadi dua gerakan kamera atau dua aksi benda, jangan menumpuk keduanya sekaligus.

## 7. Teks di layar dan audio

- Teks tetap berupa label kata kunci (bukan caption penuh) dan ditempel sebagai lapisan 2D di atas hasil render 3D (PIL/OpenCV), supaya huruf tetap tajam dan tidak ikut pecah menjadi blok. Kalau ingin teks bergaya blok, boleh dibuat dari kotak, tetapi ejaan harus diverifikasi.
- Ikuti preferensi user soal caption, nama channel, logo, dan musik (lihat bagian "Kejujuran soal hasil" di `SKILL.md`).
- Efek suara yang cocok: ombak, mesin, benturan blok, klik, klakson. Buat sintetis dan jujur soal itu.

## 8. Batas dan kejujuran

- Ini grafis voxel buatan kode, bukan model 3D profesional atau render fotorealistik. Katakan itu di pesan serah terima.
- Tidak ada GPU di lingkungan render. Waktu render per frame harus diukur dulu (10 sampai 20 frame uji) sebelum merender semuanya.
- Urutan gambar berdasarkan jarak pusat kotak, jadi benda sangat besar bisa tampak salah tumpang tindih. Pecah benda besar menjadi kotak kecil atau pakai `floor_quad()`.
- Kalau user punya model `.glb/.gltf/.obj` sendiri, jelaskan bahwa `voxel.py` tidak memuatnya langsung; opsinya adalah mem-voxelisasi sederhana dengan kode atau memakai jalur WebGL (lihat `render-3d-voxel.md` bagian 5).
