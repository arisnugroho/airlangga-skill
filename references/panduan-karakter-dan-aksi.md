# Panduan Karakter dan Aksi

Baca file ini kapan pun ada orang atau kegiatan manusia di layar, terutama untuk gaya pixel-art atau simulasi (misalnya ala WorldBox). Kode siap pakai: `scripts/karakter_pixel.py` (sprite manusia + aksi) dan `scripts/demo_aktivitas.py` (contoh shot).

## Daftar isi
1. Karakter harus berbentuk manusia
2. Ukuran minimum
3. Jenis shot dan kapan dipakai
4. Aturan aktivitas
5. Tabel kegiatan ke shot
6. Cara membuat shot aksi
7. Larangan
8. Pemeriksaan sebelum menyerahkan

## 1. Karakter harus berbentuk manusia

Setiap orang punya kepala, badan, dua tangan, dua kaki, dan bergerak (jalan, mengayun alat, bicara). Titik atau satu-dua piksel tidak diterima, termasuk di shot lebar yang ramai. `karakter_pixel.py` menyediakan aksi: `idle`, `walk`, `chop` (kapak), `dig` (cangkul tambang), `hoe` (cangkul tanah), `hammer`, `carry`, `talk`, `plant`. Tambahkan aksi baru dengan menambah pose di tabel `_P` (dua frame: bersiap dan mengayun).

## 2. Ukuran minimum (dihitung dari layar akhir)

Orang di `karakter_pixel.py` setinggi 13 unit. Satu unit = `k` piksel internal, dan piksel internal diperbesar sesuai rasio render (misalnya 4x dari 480x270 ke 1920x1080).

| Jenis shot | Tinggi orang di layar akhir | Contoh `k` pada render 480x270 (4x) |
|---|---|---|
| Shot lebar ramai | minimal 40 px | `k=1` (52 px) atau `k=2` (104 px) |
| Shot sedang (kelompok) | 150 sampai 250 px | `k=3` sampai `k=4` |
| Close-up aktivitas | 30 sampai 45 persen tinggi layar (sekitar 330 sampai 480 px) | `k=6` sampai `k=8` |

Kalau merender langsung 1920x1080 tanpa pembesaran, kalikan `k` dengan 4. Kecil dari batas ini = ulangi.

## 3. Jenis shot dan kapan dipakai

- **Shot lebar (konteks):** menunjukkan tempat, jumlah orang, dan perubahan dunia. Orang tetap berbentuk manusia dan bergerak.
- **Shot sedang:** kelompok kecil melakukan kegiatan bersama (berembuk, antre, gotong royong).
- **Close-up aktivitas:** satu atau dua karakter besar mengerjakan kegiatan yang disebut narasi. Latar sederhana yang menjelaskan tempat (hutan, tambang, ladang, tepi sungai), karakter dan alatnya dominan, ada efek kecil (serpihan, debu, percikan).

Pola ritme yang disarankan: lebar, aksi, lebar. Kamera atau latar harus tetap bergerak (parallax, awan, api obor berkedip), jangan membekukan close-up.

## 4. Aturan aktivitas

1. Tiap kali narasi menyebut karakter melakukan kegiatan, tayangkan kegiatan itu dengan jelas pada saat kalimatnya diucapkan. Ganti shot di batas kalimat (pakai jeda dari `silencedetect`/SRT), bukan di tengah kata.
2. Kalau hanya disebut sebuah kegiatan kelompok (misalnya "beberapa warga berkumpul untuk musyawarah"), buat adegan kegiatan itu: karakter melingkar, bergantian bicara (aksi `talk` pada satu orang, gelembung bicara tanpa teks).
3. Kalau kegiatannya berada di tempat khusus, pentaskan di tempat itu. Contoh: menggali tambang = karakter mencangkul di dalam terowongan tambang berobor, bukan ikon tambang atau bangunan dari luar.
4. Durasi shot aksi minimal selama kalimatnya diucapkan, dan minimal sekitar 2 detik agar gerakannya terbaca (dua sampai empat ayunan).
5. Gerakan harus selaras dengan suara: ayunan kapak dengan ketukan efek suara, bukan acak.

## 5. Tabel kegiatan ke shot

| Kegiatan di narasi | Shot aksi | Aksi dan alat | Efek suara |
|---|---|---|---|
| Menebang pohon | Close-up hutan, pohon besar di samping karakter | `chop`, kapak; serpihan kayu | ketukan kayu |
| Membangun rumah | Karakter di rangka rumah yang bertambah | `hammer`; rumah muncul bertahap | ketukan palu |
| Menggali tambang | Dalam terowongan tambang, obor | `dig`, beliung; percikan, bijih | dentang batu |
| Bertani, membuka ladang | Barisan tanah, tunas muncul | `hoe`, `plant` | tanah dicangkul |
| Memanen, mengangkut hasil | Karakter membawa kotak atau karung ke lumbung | `carry` | langkah kaki |
| Berembuk, musyawarah | Lingkaran 5 sampai 8 orang, bergantian bicara | `talk`, `idle` | gumam pelan |
| Berdagang, pasar | Lapak dan pembeli berpindah barang | `carry`, `talk` | keramaian |
| Menggali saluran irigasi | Parit yang memanjang dan terisi air | `dig` atau `hoe` | air mengalir |
| Memperbaiki tanggul | Karakter menumpuk batu atau karung | `carry`, `hammer` | batu ditumpuk |
| Berlayar, mengangkut lewat sungai | Perahu dengan karakter di atasnya | `idle` / `carry` di perahu | air, kayu berderit |
| Menanam bibit pohon | Karakter menunduk dan menanam | `plant` | tanah |
| Mengawetkan daging, menyimpan makanan | Karakter menggantung daging di rak, mengisi lumbung | `carry`, `hammer` | rak berderit |

Tabel ini contoh. Kegiatan lain diperlakukan dengan prinsip yang sama: tempat yang tepat, alat yang tepat, gerakan yang terbaca.

## 6. Cara membuat shot aksi

```python
from karakter_pixel import person, blit
spr = person('dig', t, k=7, shirt=3, skin=1)   # t = detik, deterministik
blit(canvas, spr, x_tengah, y_kaki)
```
Gambar latar, karakter, lalu efek (serpihan, percikan) sebagai fungsi `t`. Lihat `scripts/demo_aktivitas.py` untuk empat contoh: shot lebar, menebang, menggali tambang, musyawarah. Jalankan skrip itu untuk membuat gambar contoh, dan bandingkan ukuran karakter dengan tabel di atas.

## 7. Larangan

- Karakter berupa titik atau bentuk yang tidak terbaca sebagai manusia.
- Kegiatan yang disebut narasi tapi tidak pernah tampil di layar.
- Memberi nama, profesi, atau label pada karakter yang tidak disebut voiceover.
- Panel angka atau data yang tidak diucapkan voiceover.
- Menampilkan teks yang mengulang narasi (caption). Gelembung bicara hanya berisi titik-titik atau ikon.

## 8. Pemeriksaan sebelum menyerahkan

1. Ekstrak satu frame untuk tiap kegiatan yang tercatat di daftar aktivitas. Karakter terlihat jelas, alatnya terbaca, dan gerakannya sesuai.
2. Ukur tinggi karakter di frame 1080p: sesuai tabel ukuran minimum.
3. Setiap kegiatan yang disebut narasi punya shot, dan shot-nya muncul saat kalimat itu diucapkan.
