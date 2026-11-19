"""Kamera nyaman untuk video pixel-art (zoom/pan tanpa getar). Bagian dari skill motion-graphics-by-airlangga.

Prinsip:
1. Gambar dunia dulu diperbesar dengan 'nearest' ke resolusi AKHIR (mis. 960x540 -> 1920x1080 lewat naik2x).
2. Zoom/pan dilakukan di resolusi akhir dengan resampling halus (bilinear) dan posisi pecahan: tidak ada piksel yang
   digandakan tidak merata antar frame, jadi tepi tidak berkedip. (Zoom 'nearest' pada rasio non-bulat = penyebab getar.)
3. Tidak ada goyangan/drift sinus. Kamera diam, atau bergerak lewat transisi berarah dengan easing yang lambat.
4. HUD digambar SETELAH kamera, di resolusi akhir, supaya tidak ikut zoom.

Pakai:
    from kamera_pixel import naik2x, pandangan, terapkan, periksa_kamera, hud_overlay
    keys = [(0, (.5, .5, 1.0)), (12, (.25, .5, 1.6)), (30, (.75, .5, 1.6))]   # (detik, (cx, cy relatif 0..1, zoom))
    for w in periksa_kamera(keys): print(w)
    cx, cy, z = pandangan(T, keys)
    frame = terapkan(naik2x(frame_dunia_960x540), cx, cy, z)                   # -> 1920x1080
    frame = hud_overlay(frame, lambda small: gambar_hud(small), faktor=4)      # HUD digambar di kanvas kecil
Mode 'bulat': zoom hanya 1,2,3,4,5,6 kali (tajam 100 persen), tanpa zoom bertahap; ganti pandangan dengan potongan/crossfade.
"""
import numpy as np
from PIL import Image

def naik2x(frame): return np.repeat(np.repeat(frame, 2, 0), 2, 1)

def _easing(x):
    x = min(1.0, max(0.0, x)); return x * x * x * (x * (x * 6 - 15) + 10)     # smootherstep: mulai dan berhenti sangat lembut

def pandangan(T, keys, dur=3.0):
    """keys: [(t, (cx, cy, zoom))] terurut. Pindah ke pandangan baru mulai di t selama dur detik. Aman untuk T sebelum key pertama."""
    cur = np.array(keys[0][1], float); res = cur
    for i, (t, v) in enumerate(keys):
        if T < t: break
        prev = np.array(keys[i - 1][1], float) if i else np.array(v, float)
        res = prev + (np.array(v, float) - prev) * _easing((T - t) / dur)
    return float(res[0]), float(res[1]), max(1.0, float(res[2]))

def periksa_kamera(keys, dur=3.0, min_tahan=8.0, maks_laju_zoom=0.2, zoom_maks=2.4):
    """Daftar peringatan agar kamera nyaman ditonton (mis. video 10 menit)."""
    w = []
    for i in range(1, len(keys)):
        t0, a = keys[i - 1]; t1, b = keys[i]
        gap = t1 - t0
        if gap < min_tahan: w.append(f'{t0:.1f}-{t1:.1f}s: kamera pindah lagi setelah {gap:.1f}s (< {min_tahan}s); jarangkan atau pakai potongan')
        laju = abs(b[2] - a[2]) / max(dur, 1e-6)
        if laju > maks_laju_zoom: w.append(f'{t1:.1f}s: zoom berubah {abs(b[2] - a[2]):.2f}x dalam {dur}s (laju {laju:.2f}/s > {maks_laju_zoom}); perlambat atau potong')
        if b[2] > zoom_maks: w.append(f'{t1:.1f}s: zoom {b[2]:.2f} melebihi {zoom_maks}')
    for i in range(2, len(keys)):
        z0, z1, z2 = keys[i - 2][1][2], keys[i - 1][1][2], keys[i][1][2]
        if (z1 - z0) * (z2 - z1) < 0 and keys[i][0] - keys[i - 2][0] < 24 and abs(z1 - z0) > .15 and abs(z2 - z1) > .15:
            w.append(f'{keys[i - 1][0]:.1f}s: zoom masuk lalu keluar (atau sebaliknya) dalam < 24s; ini yang membuat pusing')
    return w

def terapkan(frame_besar, cx, cy, zoom, mode='halus'):
    """frame_besar: uint8 (H, W, 3) di resolusi akhir. cx, cy relatif 0..1. Mengembalikan ukuran yang sama."""
    H, W = frame_besar.shape[:2]; z = max(1.0, zoom)
    if mode == 'bulat':
        zi = max(1, int(round(z)))
        if zi == 1: return frame_besar
        w, h = W // zi, H // zi
        x0 = int(round(min(max(cx * W - w / 2, 0), W - w))); y0 = int(round(min(max(cy * H - h / 2, 0), H - h)))
        return np.repeat(np.repeat(frame_besar[y0:y0 + h, x0:x0 + w], zi, 0), zi, 1)
    if z <= 1.0005: return frame_besar
    w, h = W / z, H / z
    x0 = min(max(cx * W - w / 2, 0), W - w); y0 = min(max(cy * H - h / 2, 0), H - h)
    im = Image.fromarray(frame_besar).resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))
    return np.asarray(im)

def hud_overlay(frame, gambar_hud, faktor=4):
    """Gambar HUD dengan fungsi gambar_hud(kanvas_kecil) pada salinan kecil (frame[::faktor, ::faktor]); piksel yang berubah
    ditimpa ke frame besar (digandakan faktor kali). Menjaga font dan panel tetap bergaya piksel kasar."""
    kecil = frame[::faktor, ::faktor].copy(); asli = kecil.copy()
    gambar_hud(kecil)
    m = (kecil != asli).any(2)
    up = np.repeat(np.repeat(kecil, faktor, 0), faktor, 1); m2 = np.repeat(np.repeat(m, faktor, 0), faktor, 1)
    out = frame.copy(); out[m2] = up[m2]
    return out

if __name__ == '__main__':
    # Uji getar: lacak posisi tepi batang pohon pada zoom 1,0 -> 1,6 di gambar statis. Jitter = simpangan posisi dari lintasan mulus.
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import shot_library as sl
    base = sl.shot_frame(1.0, (0, 5, 'tebang', {}), sl.env_preset('musim_semi')); big = naik2x(base)
    N = 120; zs = np.linspace(1.0, 1.6, N); cx, cy = .7, .55
    def lama(z):
        H, W = base.shape[:2]; w, h = W / z, H / z
        x0 = min(max(cx * W - w / 2, 0), W - w); y0 = min(max(cy * H - h / 2, 0), H - h)
        return naik2x(np.asarray(Image.fromarray(base).resize((W, H), Image.NEAREST, box=(x0, y0, x0 + w, y0 + h))))
    lum = lambda f: f[..., 0] * .3 + f[..., 1] * .59 + f[..., 2] * .11
    th = (lum(np.array([[96, 66, 40]], np.float32))[0] + lum(np.array([[110, 176, 84]], np.float32))[0]) / 2
    def jitter(fn, row=900):
        xs = []; prev = None
        for z in zs:
            L = lum(fn(z)[row].astype(np.float32))
            cr = [i + (th - L[i]) / (L[i + 1] - L[i]) for i in range(len(L) - 1) if (L[i] - th) * (L[i + 1] - th) < 0 and abs(L[i + 1] - L[i]) > 5]
            if cr: prev = min(cr, key=lambda c: abs(c - (prev if prev is not None else 1474))); xs.append(prev)
        xs = np.array(xs); t = np.arange(len(xs)); fit = np.polyval(np.polyfit(t, xs, 3), t)
        d = np.abs(np.diff(xs)); return np.sqrt(np.mean((xs - fit) ** 2)), d
    for nama, fn in (('lama (nearest, kotak pecahan)', lama), ('baru (bilinear di resolusi akhir)', lambda z: terapkan(big, cx, cy, z))):
        r, d = jitter(fn)
        print(f'{nama:34s} jitter tepi={r:.3f}px  langkah/frame: median={np.median(d):.2f} maks={d.max():.2f} simpangan-baku={d.std():.2f}')
