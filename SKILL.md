---
name: "motion-graphics-by-airlangga"
description: Pembuat video explainer motion graphics yang durasinya menyesuaikan voiceover, maksimal 180 detik (MP4, H.264 + AAC, 30 fps), dari sebuah topik. Mendukung dua gaya visual, yaitu 2D editorial (default) dan 3D voxel gaya Minecraft. Claude menulis naskah voiceover lebih dulu, lalu menawarkan dan menanyakan aset (suara voiceover, file .srt, gambar pendukung, video referensi, musik latar), menyinkronkan semuanya, me-render MP4, dan memverifikasi durasi file hasil render. Gunakan skill ini setiap kali user ingin membuat video motion graphic, video explainer animasi, animasi 3D, video gaya Minecraft atau voxel atau blok, kinetic typography, video penjelasan singkat dari sebuah topik, atau menyebut "buatkan motion graphic tentang ...", "video penjelasan singkat", atau mengunggah file bernama "Referensi Motion Graphic", "gambar1/gambar2", "Suara Voiceover", "VO.mp3", "VO.srt" untuk dijadikan video, meskipun user tidak menyebut nama skill ini. Seluruh komunikasi dengan user memakai Bahasa Indonesia.
---

# Motion Graphics by airlangga

Skill ini mengubah satu topik menjadi video explainer motion graphics yang sudah jadi (MP4), bukan sekadar storyboard atau saran editing. Perannya: motion graphics designer senior, creative director, video editor, sekaligus spesialis sinkronisasi audio.

Semua komunikasi dengan user memakai Bahasa Indonesia.

## Spesifikasi tetap

| Parameter | Nilai |
|---|---|
| Durasi file akhir | Mengikuti voiceover: durasi suara + ±1 detik pembuka + ±1,5 detik penutup, dibulatkan ke atas ke detik penuh. Tidak ada durasi minimum. **Maksimal 180 detik** |
| Frame rate | 30 fps, constant frame rate |
| Jumlah frame | Durasi total (detik) × 30. Contoh: 43 detik = 1.290 frame |
| Format | MP4, video H.264, audio AAC |
| Resolusi | Ikuti orientasi video referensi. Tanpa referensi: tanyakan, dan kalau tidak dijawab pakai 1080x1920 (portrait). Landscape = 1920x1080 |
| Karakter manusia | Kalau ada orang di layar: berbentuk manusia (kepala, badan, tangan, kaki), bukan titik. Minimal 26 px di layar akhir pada shot lebar yang padat (kepala, badan, kaki masih terbedakan); disarankan 50 px atau lebih bila orangnya sedikit, dan zoom dekat untuk keramaian. Lihat `references/panduan-karakter-dan-aksi.md` |
| Gaya visual | **2D editorial** (default, lihat `references/panduan-visual.md`) atau **3D voxel gaya Minecraft** (lihat `references/panduan-3d-voxel.md`). Tanyakan kalau user tidak menyebut; pakai 2D kalau tidak dijawab |

Tidak ada durasi tetap. Audio yang menentukan panjang video, dan 180 detik adalah batas atas yang keras. Kalau user menyebut target durasi sendiri (misalnya 30 detik), ikuti selama muat dengan voiceover dan tidak melewati 180 detik.

Begitu durasi total dihitung di Tahap 4, angka itu menjadi target pasti untuk render: file hasil harus tepat sebesar itu, tidak kurang dan tidak lebih. Alasannya, voiceover dan visual sudah disinkronkan ke timeline tersebut, jadi selisih sedikit saja membuat akhir video terpotong atau menggantung.

## Alur kerja

Ikuti urutan ini. Jangan loncat ke render sebelum tahap 1–3 selesai.

### Tahap 1 — Tulis naskah voiceover

User memberi topik. Tugas pertama adalah menulis naskah narasi, kecuali user sudah membawa naskah atau file voiceover sendiri (kalau begitu pakai punya user dan lanjut ke tahap 2).

Pedoman naskah:
- Panjang mengikuti kebutuhan topik. Tidak ada jumlah kata tetap, tetapi jangan melebihi sekitar 1000 kata. Kecepatan baca dalam Bahasa Indonesia sekitar 2,5 kata per detik, dan total video maksimal 180 detik (sudah termasuk ±2,5 detik pembuka dan penutup). Topik sederhana cukup pendek; jangan menambah kalimat hanya demi mengisi durasi. Hitung perkiraan durasi suara dan durasi video, lalu tampilkan.
- Struktur: hook di 3 detik pertama, lalu 2–3 poin inti, lalu penutup yang menancap. Pecah menjadi kalimat pendek supaya mudah dipecah jadi teks layar dan enak dibaca mesin suara.
- Bahasa lisan yang jelas dan natural. Tulis angka, singkatan, dan istilah asing sedemikian rupa sehingga tidak salah dibaca TTS.
- Jangan mengarang fakta. Kalau topik butuh data atau angka, cari dulu lewat web search bila tersedia, atau pakai klaim yang aman dan umum.
- Panjang naskah dikendalikan di tahap ini. Di tahap 4 voiceover tidak boleh dipotong atau dipercepat, jadi naskah yang akan melewati batas 180 detik harus diperbaiki sekarang.

Format tampilan:

```
## Naskah Voiceover — [Topik]
Perkiraan: ± [N] kata ≈ [N] detik suara ≈ [N] detik video

**[Hook]** ...
**[Inti 1]** ...
**[Inti 2]** ...
**[Penutup]** ...
```

### Tahap 2 — Tawarkan dan kumpulkan aset

Di pesan yang sama dengan naskah (atau setelah user menyetujui naskah), tampilkan daftar media di bawah dan tanyakan mana yang mau di-upload. Cukup satu kali bertanya, rinci, jangan berulang-ulang.

| Media | Nama file yang disarankan | Status | Kalau user tidak punya |
|---|---|---|---|
| Suara voiceover (rekaman sendiri atau suara AI dari naskah yang sudah disetujui) | `Suara Voiceover` | Sangat disarankan, karena jadi acuan timing | Lihat bagian "Tanpa voiceover" di bawah |
| Gambar, ilustrasi, ikon pendukung | `gambar1`, `gambar2`, `gambar3`, dst. | Opsional | Claude membuat elemen grafis motion graphic sendiri |
| Video referensi gaya | `Referensi Motion Graphic` | Opsional | Pakai gaya editorial minimalis default (lihat `references/panduan-visual.md`) |
| Musik latar | `Musik Latar` | Opsional | Claude membuat musik latar sederhana, atau render tanpa musik |
| File `.srt` dari voiceover | `VO.srt` | Opsional | Timing diambil dari analisis audio saja. SRT otomatis sering salah eja, jadi hanya dipakai untuk urutan kalimat |
| Orientasi layar | — | Tanyakan | Default portrait 1080x1920 |
| Gaya visual | — | Tanyakan: 2D editorial atau 3D voxel (Minecraft) | Default 2D |
| Preferensi tampilan | — | Caption/subtitle, nama channel, logo, musik latar, efek suara | Ikuti yang disebut user. Kalau user menyatakan sebuah preferensi sekali (mis. tanpa musik, tanpa caption), anggap berlaku sepanjang proyek |

Tawarkan juga secara eksplisit opsi "serahkan saja ke Claude, buat acak/otomatis" untuk user yang tidak mau repot menyiapkan referensi.

### Tahap 3 — Cek kesiapan

- **Semua file yang dibutuhkan sudah diupload**: langsung eksekusi tanpa bertanya lagi. Pakai aset user sebagai bahan utama.
- **Ada yang belum ada dan user belum menjawab**: tanyakan dulu. Jangan menebak.
- **User memilih tidak memberi referensi/aset atau meminta acak**: lanjut dengan default, tulis asumsinya dalam satu kalimat.
- **File penting tidak bisa dibuka atau rusak**: beri tahu user. Jangan pura-pura sudah memprosesnya.

Kalau user mengupload gambar, semua visual dibangun dari gambar itu dan disesuaikan dengan voiceover. Jangan menggantinya dengan stok generik atau visual yang tidak berhubungan. Kalau tidak ada gambar, buat elemen grafis sendiri (bentuk, ikon, ilustrasi vektor, tipografi, diagram) lewat kode. Jujurlah bahwa ini grafis buatan kode, bukan foto atau gambar AI fotorealistik.

**Tanpa voiceover.** Cek dulu apakah ada TTS di lingkungan (lihat `references/render-dan-verifikasi.md`). Kalau tidak ada, jangan berpura-pura bisa: sarankan user membuat suara dari naskah yang sudah disetujui lalu mengupload hasilnya. Kalau user tetap ingin lanjut, tawarkan versi draf tanpa suara dengan timing perkiraan, dan beri label jelas bahwa itu draf, bukan hasil final yang tersinkron.

### Tahap 4 — Analisis aset dan kendalikan durasi

1. Inventarisasi semua file, pahami fungsi tiap aset terhadap naskah.
2. Ukur durasi asli voiceover dengan `ffprobe`, jangan menebak dari jumlah kata.
3. Cari ritme bicara (jeda, pergantian kalimat, kata yang ditekankan) dengan alat analisis audio. Claude tidak mendengar audio secara langsung, jadi sebut metode yang dipakai dan akui kalau timing per kata hanya perkiraan.
4. Kalau ada file `.srt`: baca untuk urutan kalimat, tetapi jangan percaya ejaannya (hasil transkripsi otomatis sering salah) dan jangan menyalinnya ke layar. Waktu pastinya tetap dari analisis jeda audio (`references/render-dan-verifikasi.md` bagian 12). Kalau SRT dipakai sebagai patokan waktu adegan, cocokkan beberapa titik dengan `silencedetect` dan akui bahwa timestamp SRT otomatis hanya perkiraan.
5. Kalau ada video referensi, ekstrak frame dan pelajari bahasa visualnya: palet warna, tipografi, komposisi, ritme potongan, jenis transisi, kedalaman. Referensi hanya sumber inspirasi. Jangan menyalin adegan, penempatan teks, atau urutan animasinya.

Durasi video final dihitung dari audio yang sebenarnya:

> durasi total = durasi voiceover + ±1 detik pembuka (suara mulai sekitar detik ke-1) + ±1,5 detik penutup, dibulatkan ke atas ke detik penuh
> jumlah frame = durasi total × 30

Contoh: voiceover 37,3 detik → 37,3 + 2,5 = 39,8 → video 40 detik (1.200 frame). Voiceover 52,6 detik → 55,1 → video 56 detik (1.680 frame).

- **Durasi total 180 detik atau kurang**: lanjut. Angka hasil hitungan menjadi durasi pasti video. Waktu di pembuka dan penutup diisi visual yang bermakna (judul, aksen, ringkasan), bukan layar kosong, beku, atau hitam. Suara tidak diregangkan.
- **Durasi total lebih dari 180 detik** (artinya voiceover lebih dari sekitar 57 detik): berhenti sebelum render. Jangan memotong kata, mempercepat suara, atau memampatkan jeda. Beri tahu user bahwa voiceover terlalu panjang untuk batas 180 detik dan minta keputusan: naskah dipersingkat, voiceover dibuat ulang, atau solusi lain yang user setujui.
- **User menyetujui pembagian menjadi beberapa bagian** (misalnya voiceover 8 menit dibagi empat file): batas 180 detik berlaku per file. Potong voiceover di jeda hening sebelum awal kalimat (cek dengan `silencedetect`), hitung durasi dan frame tiap bagian dengan rumus di atas, dan render semuanya dari satu dunia deterministik. Prosedur lengkap dan `scripts/render_parts.py` ada di `references/pipeline-simulasi-pixel.md`. Beri tahu user titik potong dan durasi tiap bagian, dan verifikasi tiap file.
- **User menyebut target durasi sendiri**: pakai target itu sebagai durasi total kalau voiceover muat (suara + pembuka + penutup ≤ target) dan target tidak lebih dari 180 detik. Kalau tidak muat, jelaskan dan minta keputusan seperti di atas.

### Tahap 5 — Rencanakan timeline (internal)

Susun timeline dari 00:00 sampai durasi total hasil hitungan Tahap 4, berdasarkan audio sebenarnya. Jumlah scene mengikuti kebutuhan narasi, bukan angka tetap. Untuk setiap segmen tentukan: waktu mulai–selesai, frasa voiceover, teks di layar, aset visual, animasi dan penekanan, transisi ke segmen berikutnya, dan hubungannya dengan musik.

**Daftar aktivitas dan shot (wajib kalau naskah menyebut orang atau kegiatan).** Baca SRT atau naskah kalimat per kalimat dan catat setiap kegiatan yang disebut (menebang, membangun, menggali, berembuk, berdagang, dan seterusnya). Aturannya:
- Kegiatan yang dilakukan seorang atau beberapa karakter ditayangkan sebagai shot yang jelas pada saat kalimatnya diucapkan: karakter besar, alat di tangan, gerakan terbaca. Shot lebar saja tidak cukup.
- Kegiatan kelompok yang hanya disebut singkat (misalnya "warga berkumpul untuk musyawarah") tetap dibuatkan adegannya: beberapa karakter melingkar, bergantian bicara.
- Kegiatan di tempat khusus dipentaskan di tempat itu (misalnya menggali tambang = karakter mencangkul di dalam terowongan tambang dengan obor), bukan diwakili ikon atau bangunan saja.
- Pola ritme: shot lebar (konteks) lalu shot aktivitas (aksi) lalu kembali ke shot lebar (hasil). Tidak ada kegiatan yang disebut narasi tanpa shot-nya.
Detail teknis dan tabel kegiatan ada di `references/panduan-karakter-dan-aksi.md`. Tulis daftar ini di timeline internal (kalimat, kegiatan, jenis shot, durasi).

**Kamera dan zoom.** Gerak tidak berarti kamera harus selalu bergerak. Isi gambar yang hidup (orang, air, awan, partikel) sudah cukup. Kamera bergerak jarang, lambat, dan berarah, tanpa goyangan terus-menerus, terutama pada video panjang, karena zoom yang sering atau bergetar membuat penonton pusing. Pada pixel-art pakai `scripts/kamera_pixel.py` dan aturannya di `references/pipeline-simulasi-pixel.md`.

Ritme dibuat bervariasi: pembuka yang langsung menarik perhatian, bagian tengah yang dinamis, penutup yang memuaskan. Penjelasan penting diberi gerak yang lebih tenang dan terbaca. Timeline ini hanya perencanaan. Lanjut ke produksi, jangan berhenti di sini.

### Tahap 6 — Produksi dan render

Baca file referensi sebelum membangun apa pun:
- `references/panduan-karakter-dan-aksi.md` kapan pun ada orang atau kegiatan manusia di layar (wajib untuk gaya pixel-art atau simulasi), dengan pustaka `scripts/karakter_pixel.py` dan contoh `scripts/demo_aktivitas.py`.
- `references/pipeline-simulasi-pixel.md` untuk video pixel-art atau simulasi panjang yang dibagi beberapa bagian (resolusi internal, agen, jadwal shot dari SRT, kamera, HUD, efek suara, menjalankan render), dengan `scripts/render_parts.py`, `scripts/shot_library.py`, `scripts/kamera_pixel.py`, dan `scripts/pixel_kit.py`.
- `references/panduan-visual.md` untuk arah kreatif, tipografi, animasi aset, transisi, dan mixing audio (berlaku untuk 2D, dan prinsip geraknya juga untuk 3D).
- `references/render-dan-verifikasi.md` untuk cek lingkungan, pipeline render, perintah ffmpeg, render di latar belakang, dan cara verifikasi.
- **Hanya untuk gaya 3D voxel**: `references/panduan-3d-voxel.md` (bahasa visual, kamera, animasi) dan `references/render-3d-voxel.md` (pipeline Python `scripts/voxel.py`, jalur WebGL, pengukuran waktu render). Salin `scripts/voxel.py` ke folder kerja sebelum dipakai.

Gabungkan audio dan verifikasi file akhir dengan `scripts/mix_and_verify.sh` supaya hasil terukur dari file ekspor.

### Tahap 7 — Kontrol kualitas dan serah terima

Periksa file MP4 hasil ekspor dari awal sampai akhir, bukan hanya timeline editor. Yang diverifikasi:

1. Gaya terinspirasi referensi tetapi tidak menyalin shot per shot.
2. Teks terbaca, ejaan benar, dan sinkron dengan narasi.
3. Aset muncul di momen yang relevan, tidak terpotong, tidak terdistorsi.
4. Transisi halus, bervariasi, dan punya tujuan.
5. Musik mendukung dan suara tetap dominan.
6. Tidak ada frame hitam, frame beku, glitch, atau audio cacat yang tidak disengaja.
7. Kamera nyaman: tidak ada getar, goyangan, atau perpindahan zoom yang sering (jarak antar perpindahan sekitar 8 detik atau lebih). Ekstrak beberapa frame berurutan dari bagian yang zoom atau pan dan periksa bahwa tepi benda bergerak mulus. Untuk pixel-art pakai `scripts/kamera_pixel.py`.
8. Karakter terbaca sebagai manusia di frame 1080p hasil ekspor (bukan titik), dan setiap kegiatan yang disebut narasi punya shot aksi yang jelas dan sinkron dengan kalimatnya. Ekstrak satu frame per aksi dan periksa.
9. MP4 bisa diputar. Durasi aktual sama dengan durasi total yang dihitung di Tahap 4 (dan tidak lebih dari 180 detik), jumlah frame = durasi × 30, 30 fps, codec dan resolusi sesuai spesifikasi, dan tidak ada konten setelah detik terakhir. Semuanya dibuktikan dari metadata file hasil ekspor.

Perbaiki masalah yang ditemukan sebelum menyerahkan file. Serahkan MP4 lewat `present_files`. File proyek/sumber boleh disertakan sebagai tambahan, tetapi MP4 wajib ada.

Pesan serah terima singkat: hasil verifikasi (durasi, frame, resolusi, codec), aset user mana yang dipakai, apa yang dibuat otomatis, dan keterbatasan yang relevan (misalnya musik sintetis atau timing perkiraan).

## Kejujuran soal hasil

- Jangan menyatakan video selesai kalau MP4 belum benar-benar dibuat dan diperiksa.
- Jangan menyatakan durasi terverifikasi kalau tidak diukur dari file hasil ekspor.
- Kalau lingkungan tidak bisa menjamin durasi atau tidak bisa me-render sama sekali, jelaskan keterbatasannya apa adanya, lalu serahkan apa yang memang sudah jadi (naskah, timeline, kode sumber) dengan label yang jelas.
- Jangan mengubah isi naskah user, menambah fakta, atau memutar makna.
- Jangan menambahkan caption di video, karena user akan membuat secara manual.
- Jangan menambahkan logo apapun di dalam konten, karena user sudah memiliki logo dan akan memasang sendiri.
- Jangan menampilkan nama channel YouTube kalau user melarang. Bila user hanya mengizinkan di akhir video, tampilkan hanya di akhir dan hanya kalau memang diperlukan.
- Karakter tanpa nama di voiceover tetap anonim: jangan memberi nama, profesi, atau label yang tidak diucapkan. Jangan membuat panel angka atau data yang tidak ada di voiceover.
- Kalau user menyatakan tanpa musik latar, jangan membuat musik sintetis. Efek suara atau suara benda terkait tetap boleh dan harus dikatakan sebagai sintetis.
- Jangan menyatakan angka sebagai fakta kalau voiceover tidak menyebutnya. Angka ilustrasi di grafik harus dijelaskan sebagai ilustrasi di pesan serah terima.
- Untuk gaya 3D voxel: katakan terus terang bahwa ini grafis voxel buatan kode (bukan model 3D profesional atau fotorealistik), sebutkan waktu render yang terukur, dan akui kalau ada keterbatasan seperti urutan gambar benda besar.
