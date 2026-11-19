"""Pustaka shot aktivitas pixel-art (960x540) untuk skill motion-graphics-by-airlangga.

Pakai:
    import shot_library as sl
    env = sl.env_preset('musim_semi')            # atau buat dict sendiri (lihat ENV_PRESET)
    frame = sl.shot_frame(T, (t0, t1, 'tebang', {}), env)   # uint8 (540, 960, 3)
    jadwal = sl.buat_jadwal('VO.srt', rencana)   # rencana = [(idx_mulai, idx_selesai, 'jenis', {opsi}), ...]
    sh = sl.shot_aktif(T, jadwal)

Jenis shot: tambang, tebang, bangun, angkut, cangkul, parit, pasar, forge, daging, dingin, rapat, banjir, tanggul, jalan, perahu, tanam, bagi.
Opsi umum: bangun {'spr': 'hut'|'strong'|'stone'|'rhut'|'rstrong'|'granary','k': 13}; angkut {'dest': 'granary'|'rack'|'none'};
rapat {'n': 4, 'elder': 1}; banjir {'wade': 1}.
Semua fungsi deterministik terhadap T, jadi aman dirender per bagian.
"""
import re, numpy as np, math
import karakter_pixel as kp
from pixel_kit import rect, house, granary, forge as _forge, stall, rack, boat, sapling, pine
W2, H2 = 960, 540
K = 10
HZ = 290
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, f): return a + (b - a) * f

class Spr:  # pembungkus sederhana (rgb, mask)
    def __init__(s, sp): s.rgb, s.mask = sp.rgb, sp.mask
SP = {}
for _sn in (0, 1):
    SP[('hut', _sn)] = house(7, 5, 3, (214, 176, 116), (150, 96, 54), snow=bool(_sn))
    SP[('strong', _sn)] = house(8, 6, 4, (190, 150, 100), (176, 66, 56), chim=True, snow=bool(_sn), base=(120, 120, 128))
    SP[('stone', _sn)] = house(9, 6, 4, (170, 172, 180), (86, 80, 96), chim=True, snow=bool(_sn), base=(130, 132, 140))
    SP[('rhut', _sn)] = house(7, 5, 3, (220, 186, 120), (190, 150, 64))
    SP[('rstrong', _sn)] = house(8, 6, 4, (226, 196, 140), (190, 80, 60), base=(150, 110, 80))
SP.update(granary=granary(), forge=_forge(), rack=rack(), boat=boat(), sapling=sapling())
STALL = [stall(c) for c in ((220, 70, 60), (70, 140, 230), (240, 170, 50))]
PINE = [pine(False), pine(True)]

ENV_PRESET = {
 'musim_semi':   dict(sky_top=(120, 175, 230), sky_bot=(215, 232, 238), ground=(110, 176, 84), hill=(96, 160, 92), canopy=(120, 190, 90), snow=0, rain=0),
 'musim_panas':  dict(sky_top=(130, 180, 225), sky_bot=(225, 235, 220), ground=(92, 158, 60), hill=(70, 130, 70), canopy=(56, 130, 52), snow=0, rain=0),
 'musim_gugur':  dict(sky_top=(150, 150, 170), sky_bot=(235, 200, 160), ground=(178, 140, 66), hill=(170, 120, 60), canopy=(222, 120, 40), snow=0, rain=0),
 'musim_dingin': dict(sky_top=(165, 185, 210), sky_bot=(228, 234, 242), ground=(228, 238, 246), hill=(215, 225, 236), canopy=None, snow=1.0, rain=0),
 'tropis_kemarau': dict(sky_top=(120, 172, 228), sky_bot=(225, 236, 232), ground=(164, 168, 76), hill=(120, 150, 70), canopy=(50, 150, 70), snow=0, rain=0),
 'tropis_hujan': dict(sky_top=(96, 112, 130), sky_bot=(150, 160, 170), ground=(50, 140, 72), hill=(40, 110, 64), canopy=(50, 150, 70), snow=0, rain=1.0),
 'gurun':        dict(sky_top=(120, 160, 205), sky_bot=(235, 215, 180), ground=(205, 170, 110), hill=(170, 130, 100), canopy=(90, 130, 60), snow=0, rain=0),
}
def env_preset(nama): return dict(ENV_PRESET[nama])
def env_blend(a, b, f):
    """Campur dua preset (0..1) untuk transisi musim yang mulus."""
    e = {}
    for k in ('sky_top', 'sky_bot', 'ground', 'hill'): e[k] = tuple(lerp(a[k][i], b[k][i], f) for i in range(3))
    e['snow'] = lerp(a['snow'], b['snow'], f); e['rain'] = lerp(a['rain'], b['rain'], f)
    e['canopy'] = (b['canopy'] if f > .5 else a['canopy'])
    return e

NZ = np.random.default_rng(4).random((H2, W2))
_pc = {}
def P(action, T, shirt=0, skin=0, hair=0, flip=False, k=K):
    fr = len(kp._P[action]); ph = int(T * 3) % fr
    key = (action, ph, shirt, skin, hair, flip, k)
    if key not in _pc: _pc[key] = kp.person(action, t=(ph + .01) / 3.0, k=k, shirt=shirt, skin=skin, hair=hair, flip=flip)
    return _pc[key]
def actor(cv, action, T, x, y, **kw): kp.blit(cv, P(action, T, **kw), int(x), int(y))
def strike(T): return int(T * 3) % 2 == 1      # True saat frame 'mengayun' (dipakai juga untuk efek suara)
_bc = {}
def big(spr, k):
    key = (id(spr), k)
    if key not in _bc: _bc[key] = (np.kron(spr.rgb, np.ones((k, k, 1), np.uint8)), np.kron(spr.mask, np.ones((k, k), bool)))
    return _bc[key]
def put(cv, bs, x, y, p=1.0):
    """x tengah, y dasar; p = bagian bawah yang tampil (0..1) untuk animasi 'tumbuh'."""
    rgb, m = bs; h, w = m.shape; sy0 = int(h * (1 - p))
    x0 = int(x) - w // 2; y0 = int(y) - h
    sx0 = max(0, -x0); ex = min(w, W2 - x0); ey = h
    if y0 + sy0 < 0: sy0 = -y0
    if y0 + ey > H2: ey = H2 - y0
    if ex <= sx0 or ey <= sy0: return
    np.copyto(cv[y0 + sy0:y0 + ey, x0 + sx0:x0 + ex], rgb[sy0:ey, sx0:ex], where=m[sy0:ey, sx0:ex, None])
def disc(cv, cx, cy, r, col):
    y0, y1 = max(0, cy - r), min(H2, cy + r); x0, x1 = max(0, cx - r), min(W2, cx + r)
    if y1 <= y0 or x1 <= x0: return
    yy, xx = np.ogrid[y0:y1, x0:x1]; cv[y0:y1, x0:x1][(xx - cx) ** 2 + (yy - cy) ** 2 <= r * r] = col

def backdrop(T, env, hz=HZ):
    cv = np.zeros((H2, W2, 3), np.uint8)
    f = np.linspace(0, 1, hz)[:, None]
    cv[:hz] = (np.array(env['sky_top']) * (1 - f) + np.array(env['sky_bot']) * f)[:, None, :].astype(np.uint8)
    xs = np.arange(W2); Y = np.arange(H2)[:, None]
    for j in range(2):
        off = T * (5 + 4 * j)
        ys = (hz - 36 - 30 * j - (16 * np.sin((xs + off) / 90 + j * 2) + 9 * np.sin((xs + off) / 37 + j))).astype(int)
        cv[(Y >= ys[None, :]) & (Y < hz)] = (np.array(env['hill']) * (1 - .12 * j)).astype(np.uint8)
    cl = (255, 255, 255) if env.get('rain', 0) < .5 else (120, 128, 140)
    for i in range(4):
        x = int((i * 280 + T * 9) % 1200) - 120; y = 50 + (i * 53) % 130
        rect(cv, x, y, 140, 18, cl, .85); rect(cv, x + 24, y - 12, 90, 14, cl, .85)
    g = np.array(env['ground']); cv[hz:] = g.astype(np.uint8)
    sp = NZ[hz:]
    cv[hz:][sp < .05] = (g * .88).astype(np.uint8); cv[hz:][sp > .97] = np.clip(g * 1.12, 0, 255).astype(np.uint8)
    return cv

def weather(cv, T, env):
    n = int(260 * env.get('snow', 0))
    if n:
        i = np.arange(n); x = ((i * 37.7) % W2 + np.sin(T + i) * 6) % W2; y = ((i * 91.3) % H2 + T * (60 + (i % 5) * 14)) % H2
        for dx in (0, 1): cv[y.astype(int) % H2, np.minimum(W2 - 1, x.astype(int) + dx)] = (255, 255, 255)
    n = int(240 * max(0, env.get('rain', 0) - .4) / .6)
    if n:
        i = np.arange(n); x = ((i * 53.1) + T * 90) % W2; y = ((i * 77.7) + T * 700) % H2
        for k in range(8): cv[np.minimum(H2 - 1, y.astype(int) + k), np.maximum(0, x.astype(int) - k // 3)] = (190, 214, 245)

def canopy(T, env): return env.get('canopy')

def tree_big(cv, T, env, x, base, s=1.0, notch=0):
    h = int(300 * s); w = int(46 * s)
    rect(cv, x - w // 2, base - h, w, h, (96, 66, 40)); rect(cv, x - w // 2, base - h, w // 4, h, (74, 50, 30))
    c = canopy(T, env)
    if c:
        for dx, dy, r in ((0, -h, int(110 * s)), (-int(70 * s), -h + 40, int(70 * s)), (int(70 * s), -h + 40, int(70 * s))): disc(cv, x + dx, base + dy, r, c)
    else:
        for dx in (-90, 90): rect(cv, x + int(dx * s) - 6, base - h - 10, 12, int(100 * s), (96, 66, 40))
    if notch: rect(cv, x - w // 2 - 12, base - 130, 12 + int(notch), 36, (226, 190, 140))
def grow(cv, name, x, y, k, p, snow=0): put(cv, big(SP[(name, snow)] if isinstance(name, str) and (name, snow) in SP else SP[name], k), x, y, p)

# ---------------- scene ----------------
def chips_fx(cv, T, x, y, col=(210, 170, 110), n=9):
    if strike(T):
        ph = (T * 3) % 1.0
        for i in range(n):
            a = i * .9 + 1
            yy = int(y - 30 * ph * math.sin(a) - i * 2) % H2; xx = int(x + 70 * ph * math.cos(a) + i * 6) % (W2 - 1)
            cv[yy, xx] = col; cv[yy, xx + 1] = col

def sc_tebang(cv, T, tt, dur, env, o):
    for x, s in ((120, .45), (300, .55), (470, .5)): tree_big(cv, T, env, x, HZ + 18, s)
    tree_big(cv, T, env, 760, 470, 1.0, notch=min(60, tt * 20))
    actor(cv, 'chop', T, 560, 470, shirt=2, skin=0)
    chips_fx(cv, T, 640, 380)
    for i in range(3): rect(cv, 150 + i * 4, 480 - i * 14, 90, 12, (150, 100, 56)); rect(cv, 150 + i * 4, 480 - i * 14, 90, 3, (200, 150, 90))
def sc_bangun(cv, T, tt, dur, env, o):
    name = o.get('spr', 'strong'); p = sm(tt / max(1.0, dur * .8))
    snow = 1 if env.get('snow', 0) > .5 else 0
    k = o.get('k', 13)
    put(cv, big(SP[(name, snow)] if (name, snow) in SP else SP[name], k), 700, 470, .15 + .85 * p)
    actor(cv, 'hammer', T, 480, 470, shirt=3); actor(cv, 'hammer', T + .5, 900, 470, shirt=4, flip=True)
    chips_fx(cv, T, 560, 360)
def sc_angkut(cv, T, tt, dur, env, o):
    dest = o.get('dest', 'granary')
    if dest == 'granary': put(cv, big(SP['granary'], 13), 790, 470)
    if dest == 'rack': put(cv, big(SP['rack'], 14), 790, 440)
    if dest == 'none' or dest == 'rack':
        for r in range(8):
            for c in range(14): rect(cv, 20 + c * 66 + (r % 2) * 20, 340 + r * 20, 8, 22, (214, 190, 80) if r % 2 else (230, 200, 90))
    for i in range(3):
        x = ((T * 80 + i * 330) % 1000) - 40; y = 440 + i * 36
        if dest != 'none' and x > 640: continue
        actor(cv, 'carry', T + i * .4, x, y, shirt=i + 1, skin=i % 3, k=K)
def sc_cangkul(cv, T, tt, dur, env, o):
    for r in range(6):
        y = 340 + r * 34; rect(cv, 0, y, W2, 18, (132, 94, 58)); rect(cv, 0, y, W2, 3, (160, 118, 74))
        n = int(min(1, tt / (dur * .7) * 1.4) * 22)
        for c in range(n): rect(cv, 30 + c * 42 + (r % 2) * 20, y - 6, 8, 12, (70, 170, 70))
    actor(cv, 'hoe', T, 450, 450, shirt=2, skin=1); actor(cv, 'hoe', T + .3, 760, 400, shirt=5, k=6, flip=True); actor(cv, 'plant', T, 200, 390, shirt=4, k=6)
def sc_parit(cv, T, tt, dur, env, o):
    rect(cv, 0, 450, W2, 50, (96, 66, 44)); rect(cv, 0, 450, W2, 6, (70, 46, 30))
    xw = int(W2 * sm(tt / max(1.0, dur * .85)))
    rect(cv, 0, 458, xw, 36, (62, 140, 230))
    for i in range(0, xw, 38): rect(cv, i + int(T * 60) % 38, 470, 14, 4, (200, 232, 255))
    for r in range(3): rect(cv, 40 + r * 300, 330 + r * 24, 120, 22, (130, 92, 56))
    actor(cv, 'dig', T, min(W2 - 140, max(220, xw + 130)), 452, shirt=3, skin=1)
    chips_fx(cv, T, min(W2 - 140, max(220, xw + 130)) + 100, 470, (150, 110, 70))
def sc_pasar(cv, T, tt, dur, env, o):
    for i, x in enumerate((200, 480, 760)): put(cv, big(STALL[i % 3], 12), x, 400)
    sp = int(T * .8) % 2
    actor(cv, 'talk' if sp == 0 else 'idle', T, 330, 490, shirt=1, skin=2); actor(cv, 'carry', T, 580, 490, shirt=2, hair=1)
    actor(cv, 'talk' if sp else 'idle', T, 860, 490, shirt=6, flip=True, skin=1)
def sc_forge(cv, T, tt, dur, env, o):
    cv[:] = (cv * .35).astype(np.uint8) if False else cv
    rect(cv, 0, 0, W2, 540, (58, 54, 62), 0.55)
    put(cv, big(SP['forge'], 15), 720, 470)
    rect(cv, 470, 440, 110, 40, (60, 62, 72)); rect(cv, 470, 440, 110, 8, (110, 112, 124))
    actor(cv, 'hammer', T, 430, 470, shirt=3, skin=1)
    if strike(T):
        for i in range(12):
            a = i * .6; cv[int(430 - 30 - 40 * abs(math.sin(a)) * ((T * 3) % 1) * 3), int(560 + 90 * math.cos(a) * ((T * 3) % 1))] = (255, 220, 90)
    fx = 1 + .05 * math.sin(T * 17)
    yy, xx = np.ogrid[:H2, :W2]; gl = np.clip(1 - np.hypot(xx - 720, yy - 400) / (260 * fx), 0, 1)[..., None]
    cv[:] = np.clip(cv.astype(np.float32) + gl * np.array((90, 40, 0)), 0, 255).astype(np.uint8)
def sc_daging(cv, T, tt, dur, env, o):
    put(cv, big(SP['rack'], 16), 760, 400)
    for i in range(4): rect(cv, 700 + i * 24, 400 - 60 + (i % 2) * 6, 14, 28, (190, 70, 64))
    actor(cv, 'carry', T, 520, 470, shirt=3); actor(cv, 'idle', T, 330, 470, shirt=5, flip=False)
def sc_dingin(cv, T, tt, dur, env, o):
    for i in range(3):
        x = ((T * 40 + i * 300) % 1100) - 80
        actor(cv, 'walk', T + i * .3, x, 450 + i * 26, shirt=7 + i, skin=i % 3, k=K)
    for x in (160, 700): put(cv, big(PINE[1], 12), x, HZ + 70)
def sc_rapat(cv, T, tt, dur, env, o):
    cx, cy = 480, 400; n = o.get('n', 5); sp = int(T * .8) % n
    rect(cv, cx - 28, cy - 4, 56, 22, (110, 80, 50)); rect(cv, cx - 14, cy - 18, 28, 16, (255, 170, 60) if int(T * 6) % 2 else (255, 210, 90))
    for i in sorted(range(n), key=lambda i: math.sin(i * 6.283 / n)):
        a = i * 6.283 / n + .3; x = cx + math.cos(a) * 300; y = cy + math.sin(a) * 60 + 70
        elder = o.get('elder') and i < 2
        actor(cv, 'talk' if i == sp else 'idle', T, x, y, shirt=i, skin=i % 3, hair=3 if elder else i % 3, flip=(x > cx), k=9)
        if i == sp:
            bx, by = int(x) - 30, int(y) - 220; rect(cv, bx, by, 80, 34, (250, 250, 250))
            for d in range(3): rect(cv, bx + 14 + d * 20, by + 14, 8, 8, (60, 60, 70))
def sc_banjir(cv, T, tt, dur, env, o):
    lvl = 470 - 140 * sm(tt / max(1.0, dur * .8)) if not o.get('wade') else 430
    for x in (200, 620): put(cv, big(SP['rhut', 0], 12), x, 380)
    rect(cv, 0, int(lvl), W2, H2 - int(lvl), (70, 130, 200), .88)
    for i in range(0, W2, 44): rect(cv, i + int(T * 70) % 44, int(lvl) + 10 + (i % 3) * 8, 20, 4, (190, 226, 255))
    if o.get('wade'):
        for i in range(3):
            x = ((T * 50 + i * 330) % 1100) - 80
            actor(cv, 'carry', T + i * .4, x, 470 + i * 12, shirt=i + 1, skin=i % 3)
        rect(cv, 0, 452, W2, H2 - 452, (70, 130, 200), .6)
    else:
        actor(cv, 'walk', T, 500, 470, shirt=3, flip=True); actor(cv, 'idle', T, 760, 470, shirt=2)
def sc_tanggul(cv, T, tt, dur, env, o):
    rect(cv, 700, HZ, 260, H2, (62, 140, 230))
    n = int(sm(tt / max(1.0, dur * .85)) * 6)
    for r in range(n):
        for c in range(7 - r // 2): rect(cv, 520 + c * 34 + (r % 2) * 17, 480 - r * 28, 32, 26, (150, 152, 160)); rect(cv, 520 + c * 34 + (r % 2) * 17, 480 - r * 28, 32, 4, (180, 182, 190))
    for i in range(2):
        x = ((T * 60 + i * 400) % 700) - 40; actor(cv, 'carry', T + i * .3, x, 480 + i * 20, shirt=i + 2, k=K)
    actor(cv, 'hammer', T, 420, 500, shirt=4)
def sc_jalan(cv, T, tt, dur, env, o):
    xw = int(W2 * sm(tt / max(1.0, dur * .85)))
    rect(cv, 0, 430, xw, 70, (190, 156, 110)); rect(cv, 0, 430, xw, 6, (216, 188, 140)); rect(cv, 0, 494, xw, 6, (150, 120, 80))
    actor(cv, 'dig', T, min(W2 - 160, xw + 150), 430, shirt=2, skin=1); actor(cv, 'hammer', T + .5, max(120, xw - 80), 520, shirt=5)
def sc_perahu(cv, T, tt, dur, env, o):
    rect(cv, 0, 360, W2, 180, (62, 140, 230))
    for i in range(0, W2, 50): rect(cv, (i - int(T * 40)) % W2, 400 + (i % 3) * 36, 22, 4, (200, 232, 255))
    by = 440 + int(math.sin(T * 2) * 5); bx = 480 + int(math.sin(T * .6) * 20)
    put(cv, big(SP['boat'], 22), bx, by + 40)
    actor(cv, 'carry', T, bx - 40, by - 30, shirt=2); actor(cv, 'idle', T, bx + 50, by - 30, shirt=3, flip=True)
    for i in range(3): rect(cv, bx - 90 + i * 28, by - 38, 22, 20, (150, 100, 56))
def sc_tanam(cv, T, tt, dur, env, o):
    for i in range(7):
        pr = sm((tt - i * .3) / 1.5); put(cv, big(SP['sapling'], 8), 100 + i * 120, 440 + (i % 2) * 40, pr)
    actor(cv, 'plant', T, 520, 480, shirt=4, skin=1)
def sc_bagi(cv, T, tt, dur, env, o):
    for i in range(3): rect(cv, 220 + i * 40, 440 - i * 22, 36, 30, (150, 100, 56)); rect(cv, 226 + i * 40, 446 - i * 22, 24, 18, (210, 160, 100))
    actor(cv, 'carry', T, 400, 480, shirt=3)
    for i, x in enumerate((620, 800)): actor(cv, 'talk' if (int(T) + i) % 2 else 'idle', T, x, 490, shirt=i + 4, flip=True)

def sc_tambang(cv, T, tt, dur, env, o):
    """Dalam terowongan tambang berobor: karakter mencangkul dinding batu."""
    r = np.random.default_rng(3).random((H2, W2))
    cv[:] = (46, 42, 52); cv[r < .06] = (66, 60, 72); cv[r > .97] = (34, 30, 40); cv[400:] = (70, 60, 56)
    for k in range(5): rect(cv, 0, 80 + k * 80, 80, 8, (110, 80, 50))
    yy, xx = np.mgrid[:H2, :W2]; fl = 1 + .06 * math.sin(T * 17)
    light = np.clip(1 - np.hypot(xx - 340, yy - 240) / (420 * fl), 0, 1)[..., None]
    cv[:] = np.clip(cv * (.35 + light * .95) + light * np.array((60, 30, 0)), 0, 255).astype(np.uint8)
    rect(cv, 334, 232, 8, 24, (255, 190, 60)); rect(cv, 332, 220, 12, 12, (255, 240, 140))
    for i in range(14): rect(cv, 720 + (i * 59) % 200, 200 + (i * 37) % 170, 6, 6, (240, 210, 90) if i % 3 == 0 else (200, 120, 60))
    actor(cv, 'dig', T, 460, 490, shirt=3, skin=1)
    if strike(T):
        ph = (T * 3) % 1.0
        for i in range(10): rect(cv, int(700 + i * 8 + 30 * ph), int(380 - i * 3 - 40 * ph * math.sin(i)), 5, 5, (230, 230, 240))

SCENES = dict(tambang=sc_tambang, tebang=sc_tebang, bangun=sc_bangun, angkut=sc_angkut, cangkul=sc_cangkul, parit=sc_parit, pasar=sc_pasar, forge=sc_forge, daging=sc_daging,
              dingin=sc_dingin, rapat=sc_rapat, banjir=sc_banjir, tanggul=sc_tanggul, jalan=sc_jalan, perahu=sc_perahu, tanam=sc_tanam, bagi=sc_bagi)


def shot_frame(T, sh, env):
    """sh = (t0, t1, kind, opts). env = dict lingkungan (ENV_PRESET). Hasil uint8 (540, 960, 3)."""
    t0, t1, kind, o = sh[0], sh[1], sh[2], sh[-1]
    if kind == 'dingin': env = env_blend(env, ENV_PRESET['musim_dingin'], 1.0)
    if kind == 'banjir': env = env_blend(env, ENV_PRESET['tropis_hujan'], 1.0)
    cv = backdrop(T, env)
    SCENES[kind](cv, T, T - t0, t1 - t0, env, o)
    if kind != 'tambang': weather(cv, T, env)
    yy, xx = np.ogrid[:H2, :W2]
    v = 1 - .22 * np.clip((np.hypot(xx - 480, yy - 270) - 330) / 300, 0, 1)
    return (cv * v[..., None]).astype(np.uint8)

def _srt(path):
    d = {}
    def tt(s):
        h, m, r = s.split(':'); sec, ms = r.split(','); return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
    for blk in re.split(r'\n\s*\n', open(path, encoding='utf-8').read().strip()):
        ln = blk.strip().split('\n'); a, b = ln[1].split(' --> '); d[int(ln[0])] = (tt(a.strip()), tt(b.strip()))
    return d

def buat_jadwal(srt_path, rencana, min_durasi=1.4):
    """rencana: [(idx_mulai, idx_selesai, kind, opsi)]. Mulai = awal kalimat idx_mulai, selesai = awal kalimat idx_selesai
    (angka pecahan ok, mis. 26.0 + offset detik lewat opsi {'+': 2.7}). Shot di bawah min_durasi dibuang."""
    S = _srt(srt_path); out = []
    for (i0, i1, kind, o) in rencana:
        t0 = S[i0][0] + o.get('+0', 0); t1 = S[i1][0] + o.get('+1', 0) - .1
        if t1 - t0 >= min_durasi: out.append((t0, t1, kind, {k: v for k, v in o.items() if not k.startswith('+')}))
    return sorted(out, key=lambda s: s[0])

def shot_aktif(T, jadwal):
    for sh in jadwal:
        if sh[0] - .01 <= T <= sh[1] + .01: return sh
    return None

def alpha_transisi(T, sh, d=.25): return min(sm((T - sh[0]) / d), sm((sh[1] - T) / d))

if __name__ == '__main__':
    from PIL import Image
    ks = list(SCENES); tiles = []
    for k in ks:
        env = env_preset('tropis_hujan' if k in ('banjir',) else 'musim_semi')
        tiles.append(Image.fromarray(shot_frame(12.3, (10.0, 15.0, k, {}), env)).resize((480, 270), Image.NEAREST))
    sheet = Image.new('RGB', (1920, 270 * ((len(tiles) + 3) // 4)))
    for i, t in enumerate(tiles): sheet.paste(t, ((i % 4) * 480, (i // 4) * 270))
    sheet.save('/tmp/shot_library_sheet.png'); print('ok', len(tiles))
