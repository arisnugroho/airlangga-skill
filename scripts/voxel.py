"""
voxel.py - renderer 3D gaya Minecraft (voxel) berbasis numpy + OpenCV, tanpa GPU/browser/jaringan.

Ide dasar:
  - Dunia terdiri dari kotak (box) berwarna. Tiap kotak = pusat, ukuran, warna.
  - Model = kumpulan kotak dengan koordinat lokal; ditaruh di dunia dengan posisi + rotasi (yaw/pitch/roll).
  - Render = proyeksi perspektif, buang sisi yang membelakangi kamera, urutkan dari jauh ke dekat
    (painter's algorithm), gambar tiap sisi dengan shading datar ala Minecraft.
  - Opsi pixel=N merender di resolusi 1/N lalu diperbesar tanpa smoothing -> tampilan blok pixel.

Konvensi: sumbu Y ke atas, X ke kanan, Z menjauh dari kamera awal. Satuan bebas (1 = 1 blok).

Batas yang perlu diketahui:
  - Urutan jauh->dekat memakai jarak pusat kotak. Kotak yang sangat besar bisa tumpang tindih salah.
    Pecah benda besar menjadi kotak <= 2-3 satuan, atau gambar lantai/air terpisah lewat floor_quad().
  - Murni CPU. Ribuan kotak per frame masih wajar (sekitar 0.1-0.4 detik/frame di 1080x1920 dengan pixel=3).
"""
import math
import numpy as np
import cv2

# 6 sisi kotak: (normal lokal, indeks 4 sudut). Sudut = kombinasi (+-1,+-1,+-1) setengah ukuran.
_SIGN = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)], np.float32)  # 8x3
_FACES = []
for ax in range(3):
    for sgn in (-1, 1):
        idx = [i for i in range(8) if _SIGN[i, ax] == sgn]
        # urutkan melingkar agar poligon tidak menyilang
        others = [a for a in range(3) if a != ax]
        idx.sort(key=lambda i: math.atan2(_SIGN[i, others[1]], _SIGN[i, others[0]]))
        n = np.zeros(3, np.float32); n[ax] = sgn
        _FACES.append((n, idx))
_FN = np.array([f[0] for f in _FACES], np.float32)      # 6x3
_FI = np.array([f[1] for f in _FACES], np.int32)        # 6x4


def rot_matrix(yaw=0.0, pitch=0.0, roll=0.0):
    """Derajat. yaw=putar sekitar Y, pitch=sekitar X, roll=sekitar Z."""
    y, p, r = map(math.radians, (yaw, pitch, roll))
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]], np.float32)
    Rx = np.array([[1, 0, 0], [0, math.cos(p), -math.sin(p)], [0, math.sin(p), math.cos(p)]], np.float32)
    Rz = np.array([[math.cos(r), -math.sin(r), 0], [math.sin(r), math.cos(r), 0], [0, 0, 1]], np.float32)
    return Ry @ Rx @ Rz


class Model:
    """Kumpulan kotak: box(x,y,z, sx,sy,sz, (r,g,b)) -> pusat (x,y,z), ukuran penuh (sx,sy,sz)."""
    def __init__(self): self.c, self.s, self.col = [], [], []

    def box(self, x, y, z, sx, sy, sz, color):
        self.c.append((x, y, z)); self.s.append((sx, sy, sz)); self.col.append(color); return self

    def block(self, x, y, z, color):  # kotak 1x1x1 berpusat di (x,y,z)
        return self.box(x, y, z, 1, 1, 1, color)

    def arrays(self):
        return np.array(self.c, np.float32), np.array(self.s, np.float32), np.array(self.col, np.float32)


class Scene:
    def __init__(self):
        self.C, self.S, self.COL, self.R, self.floor = [], [], [], [], []

    def add(self, model, pos=(0, 0, 0), yaw=0.0, pitch=0.0, roll=0.0, scale=1.0, tint=None, alpha_cols=None):
        """Taruh model di dunia. Rotasi terhadap titik asal model."""
        if not model.c: return
        c, s, col = model.arrays()
        R = rot_matrix(yaw, pitch, roll)
        c = (c * scale) @ R.T + np.array(pos, np.float32)
        s = s * scale
        if tint is not None: col = col * np.array(tint, np.float32)
        self.C.append(c); self.S.append(s); self.COL.append(col)
        self.R.append(np.repeat(R[None], len(c), 0))

    def add_box(self, x, y, z, sx, sy, sz, color, yaw=0.0):
        m = Model().box(0, 0, 0, sx, sy, sz, color)
        self.add(m, (x, y, z), yaw)

    def floor_quad(self, y, x0, x1, z0, z1, color):
        """Bidang datar besar (air/tanah) yang selalu digambar paling belakang."""
        self.floor.append((y, x0, x1, z0, z1, color))


class Camera:
    def __init__(self, pos, target, fov=60.0, up=(0, 1, 0)):
        self.pos = np.array(pos, np.float32); self.target = np.array(target, np.float32)
        self.fov = fov; self.up = np.array(up, np.float32)

    def basis(self):
        f = self.target - self.pos; f /= np.linalg.norm(f) + 1e-9
        r = np.cross(f, self.up); r /= np.linalg.norm(r) + 1e-9
        u = np.cross(r, f)
        return r, u, f

    def project(self, P, W, H):
        r, u, f = self.basis()
        d = P - self.pos
        x, y, z = d @ r, d @ u, d @ f
        fl = 0.5 * H / math.tan(math.radians(self.fov) / 2)   # fov vertikal
        zz = np.maximum(z, 1e-3)
        return np.stack([W / 2 + x / zz * fl, H / 2 - y / zz * fl], -1), z


def _hash_jitter(c):
    h = np.sin(c[:, 0] * 12.9898 + c[:, 1] * 78.233 + c[:, 2] * 37.719) * 43758.5453
    return (h - np.floor(h)) - .5


def render(scene, cam, W=1080, H=1920, sky=((120, 190, 255), (200, 230, 255)), fog=None,
           light=(-.45, .8, .4), ambient=.58, pixel=1, jitter=.05, outline=0.0):
    """
    Kembalikan gambar RGB uint8 (H,W,3).
    sky=(atas,bawah) gradien latar; fog=(warna, jarak_mulai, jarak_penuh) atau None.
    pixel=N: render di (W/N, H/N) lalu perbesar nearest (gaya blok pixel).
    outline: 0..1, garis gelap tipis di tepi sisi (kesan blok).
    """
    rw, rh = W // pixel, H // pixel
    t = np.linspace(0, 1, rh, dtype=np.float32)[:, None, None]
    top = np.array(sky[0], np.float32); bot = np.array(sky[1], np.float32)
    img = np.broadcast_to(top * (1 - t) + bot * t, (rh, rw, 3)).astype(np.uint8).copy()
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    fogc = np.array(fog[0], np.float32) if fog else None

    def fogmix(col, dist):
        if fog is None: return col
        k = float(np.clip((dist - fog[1]) / max(1e-6, fog[2] - fog[1]), 0, 1))
        return col * (1 - k) + fogc * k

    # lantai
    for (y, x0, x1, z0, z1, color) in sorted(scene.floor, key=lambda q: q[0]):
        P = np.array([[x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1]], np.float32)
        d = np.linalg.norm(P - cam.pos, axis=1)
        pts, z = cam.project(P, rw, rh)
        if (z <= 0.05).any():  # potong sederhana: dekatkan titik di belakang kamera
            continue
        col = fogmix(np.array(color, np.float32) * (ambient + (1 - ambient) * max(0, L[1])), float(d.mean()))
        cv2.fillConvexPoly(img, np.round(pts * 16).astype(np.int32), tuple(int(v) for v in col), cv2.LINE_AA, 4)

    if scene.C:
        C = np.concatenate(scene.C); S = np.concatenate(scene.S); COL = np.concatenate(scene.COL); R = np.concatenate(scene.R)
        M = len(C)
        corners = C[:, None, :] + np.einsum('mij,kj->mki', R, _SIGN) * (S[:, None, :] * .5)   # M,8,3
        r_, u_, f_ = cam.basis()
        dist = np.linalg.norm(C - cam.pos, axis=1)
        ok = ((C - cam.pos) @ f_) > -float(S.max()) * 1.5
        order = np.argsort(-dist)
        order = order[ok[order]]
        pts_all, zs = cam.project(corners.reshape(-1, 3), rw, rh)
        pts_all = pts_all.reshape(M, 8, 2); zs = zs.reshape(M, 8)
        wn = np.einsum('mij,fj->mfi', R, _FN)                      # M,6,3 normal dunia
        half = S * .5
        # pusat sisi = pusat + normal * setengah ukuran sepanjang sumbu lokal tsb
        axis_half = np.stack([half[:, 0], half[:, 0], half[:, 1], half[:, 1], half[:, 2], half[:, 2]], 1)  # M,6
        fc = C[:, None, :] + wn * axis_half[..., None]
        facing = np.einsum('mfi,mfi->mf', wn, cam.pos - fc) > 0
        shade = ambient + (1 - ambient) * np.clip(np.einsum('mfi,i->mf', wn, L), 0, 1)
        jit = _hash_jitter(C)[:, None] * jitter * 2
        for m in order:
            if zs[m].min() <= 0.05: continue
            base = COL[m]
            for f in range(6):
                if not facing[m, f]: continue
                p = pts_all[m, _FI[f]]
                col = np.clip(base * (shade[m, f] + jit[m, 0]), 0, 255)
                col = fogmix(col, dist[m])
                q = np.round(p * 16).astype(np.int32)
                cv2.fillConvexPoly(img, q, tuple(int(v) for v in col), cv2.LINE_AA, 4)
                if outline > 0:
                    cv2.polylines(img, [q], True, tuple(int(v * (1 - outline * .5)) for v in col), 1, cv2.LINE_AA, 4)
    if pixel > 1:
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_NEAREST)
    return img


# ---------------------------------------------------------------- pembangun objek siap pakai
CONT = [(235, 92, 52), (30, 120, 200), (220, 60, 70), (40, 170, 160), (250, 190, 50), (235, 235, 235), (90, 90, 200), (60, 170, 90)]


def make_ship(length=16, width=4, seed=3):
    """Kapal kontainer voxel; haluan ke +Z, berpusat di (0,0,0), garis air di y=0."""
    import random
    r = random.Random(seed); m = Model()
    hull_c, red = (40, 62, 98), (170, 50, 52)
    for iz in range(length):
        z = iz - length / 2 + .5
        taper = 0 if iz < length - 3 else (iz - (length - 4))
        w = max(1, width - taper)
        m.box(0, -.5, z, w, 1, 1, red)
        m.box(0, .5, z, w, 1, 1, hull_c)
    for iz in range(2, length - 4):
        z = iz - length / 2 + .5
        for ix in range(width // 2):
            for h in range(r.choice([1, 2, 2, 3])):
                m.box(-width / 2 + 1 + ix * 1.0 + .0, 1.5 + h, z, .95, .95, .95, r.choice(CONT))
    m.box(0, 2.5, -length / 2 + 1.5, width, 3, 2, (238, 242, 248))
    m.box(0, 4.5, -length / 2 + 1.5, width - 1, 1, 1.5, (210, 218, 230))
    return m


def make_tug():
    m = Model()
    m.box(0, 0, 0, 2, 1, 4, (30, 34, 42)); m.box(0, .8, 0, 1.8, .6, 3.8, (255, 112, 48))
    m.box(0, 1.6, -.6, 1.2, 1, 1.4, (240, 244, 250)); m.box(0, 2.3, -.6, 1.4, .3, 1.6, (60, 90, 130))
    return m


def water_grid(scene, T, x0, x1, z0, z1, step=2.0, amp=.25, base=(24, 120, 206), speed=1.6, y=-.1):
    """Permukaan air dari kolom kotak yang naik-turun. Hati-hati: jumlah kolom = (x1-x0)/step * (z1-z0)/step."""
    m = Model()
    nx = int((x1 - x0) / step); nz = int((z1 - z0) / step)
    for i in range(nx):
        for j in range(nz):
            x = x0 + (i + .5) * step; z = z0 + (j + .5) * step
            h = amp * (math.sin(x * .6 + T * speed) + math.sin(z * .45 - T * speed * 1.3))
            k = 1 + .08 * math.sin(x * .9 + z * .7 + T)
            m.box(x, y + h - 1, z, step, 2, step, tuple(min(255, c * k) for c in base))
    scene.add(m)
