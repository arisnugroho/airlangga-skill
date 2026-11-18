# Render 3D Voxel

Baca setelah `panduan-3d-voxel.md`. Isi: cek lingkungan, pipeline utama (Python, `scripts/voxel.py`), pola kode proyek, dan jalur alternatif WebGL.

## Daftar isi
1. Cek lingkungan
2. Pipeline utama: `voxel.py`
3. Pola kode proyek
4. Mengukur dan mempercepat
5. Jalur alternatif: WebGL / three.js
6. Verifikasi

## 1. Cek lingkungan

```bash
python3 -c "import numpy, cv2, PIL; print('ok')"
ffmpeg -version | head -1
python3 -c "from playwright.sync_api import sync_playwright; print('playwright ada')"   # hanya untuk jalur WebGL
npm view three version 2>&1 | tail -1     # kosong/gagal = jaringan tertutup, three.js tidak bisa dipasang
nproc; free -g | head -2                  # menentukan kecepatan render
```

Catatan dari pengujian: browser headless Chromium bisa membuat konteks WebGL lewat software renderer, tetapi pustaka three.js tidak bisa dipasang kalau jaringan sandbox tertutup. Karena itu jalur utama adalah `voxel.py`, yang hanya butuh numpy dan OpenCV.

## 2. Pipeline utama: `voxel.py`

`scripts/voxel.py` menyediakan: `Model` (kumpulan kotak), `Scene`, `Camera`, `render()`, serta pembangun siap pakai `make_ship()`, `make_tug()`, dan `water_grid()`. Baca docstring di bagian atas file untuk konvensi sumbu dan batasnya. `scripts/demo_voxel.py` adalah contoh lengkap dan uji kecepatan:

```bash
python3 /path/ke/skill/scripts/demo_voxel.py /tmp/voxel_demo   # menulis 3 frame PNG, mencetak detik per frame
```

Salin `voxel.py` ke folder kerja, lalu `from voxel import *`. File skill hanya bisa dibaca, jadi jangan mengeditnya di tempat.

## 3. Pola kode proyek

Sama dengan 2D: satu fungsi deterministik `frame(T)` yang menggambar seluruh frame dari waktu saja (seed tetap), dipipa ke ffmpeg.

```python
from voxel import *
import cv2, subprocess

def sc_hook(T):
    sc = Scene()
    water_grid(sc, T, -40, 40, -40, 60, step=2.5)
    sc.add(SHIP, (0, 0, 8 * T), yaw=5 * math.sin(T))            # SHIP dibuat sekali di luar fungsi
    ang = math.radians(25 + 15 * ease_io(prog(T, 0, 4)))
    cam = Camera((30 * math.sin(ang), 16, -30 * math.cos(ang)), (0, 2, 8 * T), fov=55)
    img = render(sc, cam, 1080, 1920, fog=((190, 225, 255), 40, 110), pixel=3, outline=.25)
    # label 2D di atas render:
    #   gambar teks dengan PIL (RGBA) lalu blit, seperti di pipeline 2D
    return img

# frame(T) memilih adegan dari timeline, memberi transisi (blend dua frame saat batas adegan),
# lalu  p.stdin.write(frame(i/30).tobytes())  ke  ffmpeg -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i -
```

Susun timeline adegan dari cue audio (lihat `render-dan-verifikasi.md` bagian 12) dan jalankan render di latar belakang dengan `setsid` (bagian 10). Gabungkan audio dan verifikasi dengan `scripts/mix_and_verify.sh`.

## 4. Mengukur dan mempercepat

- Ukur waktu per frame lewat 10 sampai 20 frame uji. Pengujian demo: kapal 18 blok + tugboat + air 32x40 kolom, 1080x1920, `pixel=3` menghasilkan sekitar 0,09 detik per frame pada 1 CPU. Adegan lebih padat akan lebih lambat.
- Pengungkit utama: naikkan `pixel` (3 sampai 4), perbesar `step` air, kurangi kolom air di luar bidang pandang, cull benda jauh, kurangi benda dinamis.
- Jangan menurunkan resolusi akhir. Cukup render di resolusi lebih kecil dengan `pixel=N` lalu diperbesar, yang juga menjadi gaya visualnya.
- Perkirakan total: waktu per frame x jumlah frame. Kalau melebihi sekitar 15 menit, pecah render menjadi beberapa segmen frame dan satukan di ffmpeg, atau sederhanakan.

## 5. Jalur alternatif: WebGL / three.js

Gunakan hanya kalau jaringan tersedia (`npm install three` atau CDN yang diizinkan berhasil) atau user ingin file HTML 3D untuk dijalankan di PC sendiri:
- Bangun halaman HTML dengan fungsi `renderAt(t)` yang menggambar adegan murni dari waktu `t`. Tangkap frame dengan Playwright: `page.evaluate("renderAt(%f)" % t)` lalu `page.screenshot()` atau `canvas.toDataURL()`; luncurkan Chromium dengan `--use-gl=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist`.
- Render software WebGL di CPU lambat. Ukur dulu, dan siapkan opsi menyerahkan HTML ke user untuk direkam di mesin ber-GPU.
- Model `.glb/.gltf` hanya bisa dimuat lewat jalur ini (GLTFLoader). Pastikan file loader tersedia secara lokal.
- Tetap tulis di pesan serah terima mana jalur yang dipakai dan apa keterbatasannya.

## 6. Verifikasi

Sama dengan 2D: ukur durasi, jumlah frame, fps, codec, resolusi dari file hasil ekspor (`mix_and_verify.sh` melakukannya), ekstrak frame kunci dan lihat sendiri apakah ada benda yang tumpang tindih salah, menembus lantai, atau keluar bingkai. Cek juga kehalusan gerak kamera lewat beberapa frame berurutan.
