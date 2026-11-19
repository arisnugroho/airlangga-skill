#!/usr/bin/env python3
"""Render video panjang dalam beberapa bagian (tiap bagian <= 180 detik) dari satu fungsi dunia deterministik.

Pemakaian:
  python3 render_parts.py --modul proyek.py --vo VO.MP3 --bagian "0:158.4,158.4:302.6,302.6:433.26,433.26:531.5" \
        --internal 960x540 --keluar out --mix scripts/mix_and_verify.sh

Bila kamera di resolusi akhir (disarankan, lihat kamera_pixel.py), pakai --internal 1920x1080.
proyek.py wajib punya:   render(T) -> uint8 array (tinggi, lebar, 3) berukuran --internal
proyek.py opsional:      gen_sfx(T0, T1) -> float32 array (n, 2) pada 48 kHz (efek suara; tanpa musik latar)

Konvensi waktu: voiceover bagian mulai di detik ke-1 video, jadi T video = awal_bagian - 1.0 + n/fps.
Durasi video = ceil(panjang_vo + 2.5). Titik potong HARUS di jeda hening (cek dengan silencedetect), sebelum awal kalimat.
Jalankan lewat:  setsid nohup python3 render_parts.py ... > log.txt 2>&1 < /dev/null &   (supaya tidak mati saat sesi tool berakhir)
"""
import argparse, importlib.util, math, os, subprocess, sys, time, wave
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--modul', required=True); ap.add_argument('--vo', required=True)
ap.add_argument('--bagian', required=True); ap.add_argument('--internal', default='960x540')
ap.add_argument('--keluar', default='out'); ap.add_argument('--mix', default=None)
ap.add_argument('--fps', type=int, default=30); ap.add_argument('--hanya', type=int, default=None, help='render satu bagian saja (1-based)')
ap.add_argument('--prefix', default='Part')
a = ap.parse_args()
IW, IH = map(int, a.internal.split('x'))
spec = importlib.util.spec_from_file_location('proyek', a.modul); proyek = importlib.util.module_from_spec(spec); sys.path.insert(0, os.path.dirname(os.path.abspath(a.modul))); spec.loader.exec_module(proyek)
os.makedirs(a.keluar, exist_ok=True)
parts = [tuple(float(v) for v in p.split(':')) for p in a.bagian.split(',')]
for idx, (s, e) in enumerate(parts, 1):
    if a.hanya and idx != a.hanya: continue
    dur = math.ceil((e - s) + 2.5); fr = dur * a.fps; T0 = s - 1.0
    print(f'bagian {idx}: vo {s}-{e} ({e - s:.2f}s) -> video {dur}s, {fr} frame', flush=True)
    assert dur <= 180, 'bagian melebihi 180 detik, pecah lagi'
    vo = f'{a.keluar}/vo_{idx}.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(s), '-t', str(e - s), '-i', a.vo, '-ar', '48000', '-ac', '2', vo], check=True)
    sfx = None
    if hasattr(proyek, 'gen_sfx'):
        x = proyek.gen_sfx(T0, T0 + dur); sfx = f'{a.keluar}/sfx_{idx}.wav'
        with wave.open(sfx, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000); w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())
    vid = f'{a.keluar}/v_{idx}.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{IW}x{IH}', '-r', str(a.fps), '-i', '-',
                           '-vf', 'scale=1920:1080:flags=neighbor', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p',
                           '-r', str(a.fps), '-frames:v', str(fr), vid], stdin=subprocess.PIPE)
    t0 = time.time()
    for n in range(fr):
        f = proyek.render(T0 + n / a.fps)
        assert f.shape == (IH, IW, 3) and f.dtype == np.uint8, f'render() harus uint8 {IH}x{IW}x3, dapat {f.shape} {f.dtype}'
        ff.stdin.write(np.ascontiguousarray(f).tobytes())
        if n % 300 == 0: print(f'  frame {n}/{fr}  {time.time() - t0:.0f}s', flush=True)
    ff.stdin.close(); ff.wait()
    out = f'{a.keluar}/{a.prefix}{idx}.mp4'
    if a.mix:
        cmd = ['bash', a.mix, vid, vo, out] + ([sfx, '1'] if sfx else [])
        subprocess.run(cmd, check=True)
    print(f'bagian {idx} selesai', flush=True)
print('SEMUA SELESAI', flush=True)
