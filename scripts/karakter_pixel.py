"""Pustaka karakter pixel-art berbentuk manusia untuk skill motion-graphics-by-airlangga.

Karakter punya kepala, badan, dua tangan, dua kaki, dan bisa memegang alat.
Dipakai untuk gaya 2D pixel-art / simulasi (WorldBox). Tanpa dependensi selain numpy dan Pillow.

Pakai:
    from karakter_pixel import person, ACTIONS, blit
    spr = person('chop', t=1.2, k=1)          # shot lebar: tinggi ~13 px internal
    spr = person('dig', t=1.2, k=7)           # close-up: tinggi ~91 px internal
    blit(canvas, spr, x_tengah, y_kaki)       # canvas = array uint8 (H,W,3)

Ukuran: satu 'unit' = k piksel. Orang setinggi 13 unit, selebar 12 unit (termasuk alat).
Aturan ukuran ada di references/panduan-karakter-dan-aksi.md.
"""
import numpy as np

SKIN = [(236, 190, 150), (214, 160, 120), (170, 118, 84), (120, 80, 56)]
SHIRT = [(70, 190, 210), (230, 120, 210), (250, 190, 60), (230, 80, 70), (120, 220, 120), (240, 240, 240), (110, 130, 230)]
PANTS = (52, 54, 76)
HAIR = [(40, 30, 28), (90, 60, 36), (200, 170, 80), (230, 230, 235)]
WOOD = (130, 90, 52); STEEL = (190, 196, 208); DARK = (70, 70, 84)

# pose: tangan kanan r, tangan kiri l (koordinat unit; bahu kanan (8,5), bahu kiri (3,5)),
# alat: (jenis, pangkal, ujung), lift: kaki yang diangkat saat jalan, dip: badan turun 1 unit
_P = {
 'idle':   [dict(r=(8, 9), l=(3, 9))],
 'walk':   [dict(r=(8, 8), l=(3, 10), lift='L'), dict(r=(8, 10), l=(3, 8), lift='R')],
 'chop':   [dict(r=(10, 3), l=(9, 4), tool=('axe', (10, 3), (11, -1))), dict(r=(11, 8), l=(10, 8), tool=('axe', (11, 8), (14, 11)), dip=1)],
 'dig':    [dict(r=(10, 4), l=(9, 5), tool=('pick', (10, 4), (12, 0))), dict(r=(11, 9), l=(10, 9), tool=('pick', (11, 9), (14, 12)), dip=1)],
 'hoe':    [dict(r=(10, 5), l=(9, 6), tool=('hoe', (10, 5), (12, 1))), dict(r=(11, 9), l=(10, 9), tool=('hoe', (11, 9), (14, 12)), dip=1)],
 'hammer': [dict(r=(10, 2), l=(3, 8), tool=('hammer', (10, 2), (11, -1))), dict(r=(11, 8), l=(3, 8), tool=('hammer', (11, 8), (13, 10)))],
 'carry':  [dict(r=(10, 7), l=(9, 8), box=1, lift='L'), dict(r=(10, 7), l=(9, 8), box=1, lift='R')],
 'talk':   [dict(r=(9, 6), l=(3, 9)), dict(r=(10, 3), l=(3, 9))],
 'plant':  [dict(r=(9, 8), l=(3, 9), dip=1), dict(r=(9, 10), l=(3, 9), dip=1)],
}
ACTIONS = list(_P)

def _line(a, b):
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]

def person(action='idle', t=0.0, k=1, shirt=0, skin=0, hair=0, flip=False, speed=3.0):
    """Mengembalikan (rgb, mask) sebuah orang. t = waktu detik; speed = siklus animasi per detik."""
    frames = _P[action]; ph = int(t * speed) % len(frames); p = frames[ph]
    Wu, Hu, ox, oy = 16, 20, 1, 5            # kanvas unit + margin untuk alat di atas kepala
    g = {}                                   # (x,y) -> warna
    def put(x, y, c, w=1, h=1):
        for j in range(h):
            for i in range(w): g[(x + i + ox, y + j + oy)] = c
    dip = p.get('dip', 0); sh = SHIRT[shirt % len(SHIRT)]; sk = SKIN[skin % len(SKIN)]; hr = HAIR[hair % len(HAIR)]
    lift = p.get('lift')
    # kaki
    put(4, 9 + dip, PANTS, 2, 4 - dip - (1 if lift == 'L' else 0)); put(6, 9 + dip, PANTS, 2, 4 - dip - (1 if lift == 'R' else 0))
    put(4, 12 - (1 if lift == 'L' else 0), (60, 40, 30), 2, 1); put(6, 12 - (1 if lift == 'R' else 0), (60, 40, 30), 2, 1)
    # badan, kepala
    put(4, 5 + dip, sh, 4, 4); put(4, 5 + dip, tuple(int(v * .8) for v in sh), 1, 4)
    put(4, 1 + dip, sk, 4, 4); put(4, 1 + dip, hr, 4, 1); put(3, 2 + dip, hr, 1, 2); put(7, 1 + dip, hr, 1, 1)
    put(6, 3 + dip, (30, 24, 28)); put(7 if not p.get('talk') else 6, 3 + dip, (30, 24, 28)) if False else None
    put(7, 3 + dip, (30, 24, 28))
    if action == 'talk' and ph == 1: put(6, 4 + dip, (150, 60, 60))
    # lengan (garis dari bahu ke tangan)
    for (a, b, c) in (((3, 5 + dip), p['l'], tuple(int(v * .8) for v in sh)), ((8, 5 + dip), p['r'], sh)):
        for (x, y) in _line(a, b): put(x, y, c)
        put(b[0], b[1], sk)
    tool = p.get('tool')
    if tool:
        kind, a, b = tool
        for (x, y) in _line(a, b): put(x, y, WOOD)
        bx, by = b
        if kind == 'axe': put(bx - 1, by - 1, STEEL, 3, 2)
        elif kind == 'pick': put(bx - 2, by, STEEL, 5, 1); put(bx - 2, by + 1, DARK, 1, 1); put(bx + 2, by + 1, DARK, 1, 1)
        elif kind == 'hoe': put(bx, by, STEEL, 3, 1); put(bx + 2, by + 1, STEEL, 1, 1)
        elif kind == 'hammer': put(bx - 1, by - 1, DARK, 3, 2)
    if p.get('box'):
        put(8, 3 + dip, WOOD, 5, 5); put(9, 4 + dip, (200, 150, 90), 3, 3)
    H, W = Hu * k, Wu * k
    rgb = np.zeros((H, W, 3), np.uint8); m = np.zeros((H, W), bool)
    for (x, y), c in g.items():
        if 0 <= x < Wu and 0 <= y < Hu:
            rgb[y * k:(y + 1) * k, x * k:(x + 1) * k] = c; m[y * k:(y + 1) * k, x * k:(x + 1) * k] = True
    if flip: rgb = rgb[:, ::-1]; m = m[:, ::-1]
    return rgb, m

def blit(cv, spr, x, y):
    """x = tengah badan, y = telapak kaki (kaki berada 12+oy unit dari atas kanvas sprite)."""
    rgb, m = spr; h, w = m.shape; k = max(1, h // 20)
    x0 = x - 8 * k; y0 = y - (5 + 13) * k
    H, W = cv.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0); ex, ey = min(w, W - x0), min(h, H - y0)
    if ex <= sx0 or ey <= sy0: return
    np.copyto(cv[y0 + sy0:y0 + ey, x0 + sx0:x0 + ex], rgb[sy0:ey, sx0:ex], where=m[sy0:ey, sx0:ex, None])

def tinggi_px(k): return 13 * k

if __name__ == '__main__':
    from PIL import Image
    cv = np.full((190, 640, 3), (200, 180, 130), np.uint8)
    for i, a in enumerate(ACTIONS):
        for ph in (0, 1):
            blit(cv, person(a, t=(ph + .01) / 3.0, k=3, shirt=i), 34 + i * 66 + ph * 0, 90 + ph * 85)
    Image.fromarray(cv).resize((1280, 380), Image.NEAREST).save('/tmp/karakter_sheet.png')
    print('ok', ACTIONS)
