"""Contoh shot aktivitas (pakai karakter_pixel.py). Menyimpan frame PNG ke folder keluaran.
Jalankan: python3 demo_aktivitas.py [folder_keluaran]
Tiap fungsi shot_*(t) menggambar satu frame 480x270 dari waktu t (deterministik), lalu diperbesar 4x saat encode."""
import sys, math, numpy as np
from PIL import Image
from karakter_pixel import person, blit

W, H = 480, 270
def rnd(seed, n): return np.random.default_rng(seed).random(n)

def sky_ground(horizon, sky=((120, 160, 205), (225, 215, 190)), ground=(205, 170, 110)):
    cv = np.zeros((H, W, 3), np.uint8)
    for y in range(horizon):
        f = y / horizon; cv[y] = [int(sky[0][i] + (sky[1][i] - sky[0][i]) * f) for i in range(3)]
    cv[horizon:] = ground
    r = rnd(1, (H - horizon, W)); cv[horizon:][r < .04] = [int(c * .88) for c in ground]
    return cv

def tree(cv, x, y, s=1):
    cv[y - 14 * s:y, x - s:x + s] = (96, 66, 40)
    for j in range(-8 * s, 4 * s):
        w = int((8 * s) * (1 - abs(j) / (9 * s)))
        cv[y - 20 * s + j + 6 * s, max(0, x - w):x + w] = (56, 130, 52)

def shot_tebang(t):
    """Close-up: karakter menebang pohon (aksi jelas, karakter besar)."""
    cv = sky_ground(150)
    for x in (60, 120, 360, 430): tree(cv, x, 170, 2)
    tree(cv, 318, 214, 4)
    blit(cv, person('chop', t, k=7, shirt=2, flip=False), 235, 244)
    # serpihan kayu mengikuti ayunan
    if int(t * 3) % 2 == 1:
        for i in range(8):
            a = i * .8; cv[int(190 + math.sin(a) * 10 - i), int(312 + math.cos(a) * 12 + i * 2)] = (200, 160, 100)
    return cv

def shot_tambang(t):
    """Close-up di dalam tambang: karakter mencangkul dinding batu dengan obor."""
    cv = np.full((H, W, 3), (46, 42, 52), np.uint8)
    r = rnd(3, (H, W)); cv[r < .06] = (66, 60, 72); cv[r > .97] = (34, 30, 40)
    cv[196:] = (70, 60, 56)
    for k in range(5): cv[40 + k * 40:44 + k * 40, 0:40] = (110, 80, 50)   # balok penyangga
    yy, xx = np.mgrid[0:H, 0:W]
    fl = 1 + .06 * math.sin(t * 17)
    light = np.clip(1 - np.hypot(xx - 170, yy - 120) / (210 * fl), 0, 1)[..., None]
    cv = np.clip(cv * (.35 + light * .95) + light * np.array((60, 30, 0)), 0, 255).astype(np.uint8)
    cv[116:128, 168:172] = (255, 190, 60); cv[110:116, 167:173] = (255, 240, 140)   # obor
    for i in range(12): cv[100 + (i * 13) % 80, 360 + (i * 29) % 90] = (240, 210, 90) if i % 3 == 0 else (200, 120, 60)  # bijih
    blit(cv, person('dig', t, k=7, shirt=3, skin=1), 230, 244)
    if int(t * 3) % 2 == 1:
        for i in range(10): cv[170 + (i * 7) % 24 - i, 350 + i * 3] = (220, 220, 230)
    return cv

def shot_musyawarah(t):
    """Beberapa warga melingkar berembuk; yang bicara bergantian (tangan bergerak + gelembung)."""
    cv = sky_ground(120, ground=(190, 165, 110))
    cx, cy = 240, 210
    cv[cy - 6:cy + 4, cx - 70:cx + 70] = (150, 120, 80)           # tikar/api unggun
    n = 6; sp = int(t * .8) % n
    order = sorted(range(n), key=lambda i: math.sin(i * 2 * math.pi / n))
    for i in order:
        a = i * 2 * math.pi / n + .3
        x = int(cx + math.cos(a) * 100); y = int(cy + math.sin(a) * 26 + 20)
        act = 'talk' if i == sp else 'idle'
        blit(cv, person(act, t, k=4, shirt=i, skin=i % 3, flip=(x > cx)), x, y)
        if i == sp:
            bx, by = x - 14, y - 100
            cv[by:by + 14, bx:bx + 34] = (250, 250, 250)
            for d in range(3): cv[by + 6:by + 8, bx + 7 + d * 9:bx + 11 + d * 9] = (60, 60, 70)
    return cv

def shot_lebar(t):
    """Shot lebar: banyak orang, tetap berbentuk manusia (k=1 -> tinggi 13 px internal = 52 px di 1080p)."""
    cv = sky_ground(60, ground=(110, 170, 80))
    for i in range(70):
        x = 40 + (i * 37) % 400; y = 100 + (i * 53) % 150
        act = ('walk', 'chop', 'hoe', 'carry', 'idle')[i % 5]
        blit(cv, person(act, t + i * .13, k=2, shirt=i, skin=i % 4, flip=i % 2 == 0), x + int(math.sin(t + i) * 3 if act == 'walk' else 0), y)
    return cv

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    fr = [shot_lebar(1.0), shot_tebang(1.1), shot_tambang(1.1), shot_musyawarah(1.4)]
    sheet = Image.new('RGB', (W * 2, H * 2))
    for i, f in enumerate(fr): sheet.paste(Image.fromarray(f), ((i % 2) * W, (i // 2) * H))
    sheet.resize((W * 4, H * 4), Image.NEAREST).save(f'{out}/demo_aktivitas.png'); print('ok')
