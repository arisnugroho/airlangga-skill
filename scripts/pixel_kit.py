import numpy as np

# ---------- font pixel 5x7 ----------
_G = {
'A':"01110 10001 10001 11111 10001 10001 10001",'B':"11110 10001 10001 11110 10001 10001 11110",
'C':"01110 10001 10000 10000 10000 10001 01110",'D':"11110 10001 10001 10001 10001 10001 11110",
'E':"11111 10000 10000 11110 10000 10000 11111",'F':"11111 10000 10000 11110 10000 10000 10000",
'G':"01110 10001 10000 10111 10001 10001 01111",'H':"10001 10001 10001 11111 10001 10001 10001",
'I':"01110 00100 00100 00100 00100 00100 01110",'J':"00111 00010 00010 00010 00010 10010 01100",
'K':"10001 10010 10100 11000 10100 10010 10001",'L':"10000 10000 10000 10000 10000 10000 11111",
'M':"10001 11011 10101 10101 10001 10001 10001",'N':"10001 11001 10101 10011 10001 10001 10001",
'O':"01110 10001 10001 10001 10001 10001 01110",'P':"11110 10001 10001 11110 10000 10000 10000",
'Q':"01110 10001 10001 10001 10101 10010 01101",'R':"11110 10001 10001 11110 10100 10010 10001",
'S':"01111 10000 10000 01110 00001 00001 11110",'T':"11111 00100 00100 00100 00100 00100 00100",
'U':"10001 10001 10001 10001 10001 10001 01110",'V':"10001 10001 10001 10001 10001 01010 00100",
'W':"10001 10001 10001 10101 10101 11011 10001",'X':"10001 10001 01010 00100 01010 10001 10001",
'Y':"10001 10001 01010 00100 00100 00100 00100",'Z':"11111 00001 00010 00100 01000 10000 11111",
'0':"01110 10001 10011 10101 11001 10001 01110",'1':"00100 01100 00100 00100 00100 00100 01110",
'2':"01110 10001 00001 00010 00100 01000 11111",'3':"11110 00001 00001 01110 00001 00001 11110",
'4':"00010 00110 01010 10010 11111 00010 00010",'5':"11111 10000 11110 00001 00001 10001 01110",
'6':"00110 01000 10000 11110 10001 10001 01110",'7':"11111 00001 00010 00100 01000 01000 01000",
'8':"01110 10001 10001 01110 10001 10001 01110",'9':"01110 10001 10001 01111 00001 00010 01100",
'?':"01110 10001 00001 00010 00100 00000 00100",'!':"00100 00100 00100 00100 00100 00000 00100",
'.':"00000 00000 00000 00000 00000 01100 01100",'-':"00000 00000 00000 11111 00000 00000 00000",
'>':"10000 01000 00100 00010 00100 01000 10000",'+':"00000 00100 00100 11111 00100 00100 00000",
'/':"00001 00010 00010 00100 01000 01000 10000",':':"00000 01100 01100 00000 01100 01100 00000",
' ':"00000 00000 00000 00000 00000 00000 00000",'=':"00000 00000 11111 00000 11111 00000 00000",
}
GL = {k: np.array([[c == '1' for c in r] for r in v.split()], bool) for k, v in _G.items()}
_tc = {}

def text_mask(s, scale=1):
    key = (s, scale)
    if key in _tc: return _tc[key]
    cols = []
    for ch in s.upper():
        g = GL.get(ch, GL['?'])
        cols.append(g); cols.append(np.zeros((7, 1), bool))
    m = np.hstack(cols[:-1]) if cols else np.zeros((7, 1), bool)
    if scale > 1: m = np.kron(m, np.ones((scale, scale), bool))
    _tc[key] = m
    return m

def text_w(s, scale=1): return text_mask(s, scale).shape[1]

def put_mask(cv, m, x, y, col):
    h, w = m.shape; H, W = cv.shape[:2]
    x0, y0 = max(x, 0), max(y, 0); x1, y1 = min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0: return
    sub = m[y0 - y:y1 - y, x0 - x:x1 - x]
    cv[y0:y1, x0:x1][sub] = col

def text(cv, x, y, s, col=(255, 255, 255), scale=1, shadow=(10, 12, 24)):
    m = text_mask(s, scale)
    if shadow is not None:
        put_mask(cv, m, x + scale, y + scale, shadow)
    put_mask(cv, m, x, y, col)
    return m.shape[1]

def rect(cv, x, y, w, h, col, alpha=1.0):
    H, W = cv.shape[:2]
    x0, y0 = max(x, 0), max(y, 0); x1, y1 = min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0: return
    if alpha >= 1: cv[y0:y1, x0:x1] = col
    else:
        sub = cv[y0:y1, x0:x1].astype(np.float32)
        cv[y0:y1, x0:x1] = (sub * (1 - alpha) + np.array(col, np.float32) * alpha).astype(np.uint8)

def panel(cv, x, y, w, h, accent=None, bg=(18, 22, 36), border=(52, 60, 86)):
    rect(cv, x, y, w, h, border)
    rect(cv, x + 1, y + 1, w - 2, h - 2, bg)
    for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
        if 0 <= cy < cv.shape[0] and 0 <= cx < cv.shape[1]:
            pass
    if accent is not None: rect(cv, x + 1, y + 1, 2, h - 2, accent)

# ---------- sprite ----------
class Spr:
    def __init__(self, rgb, mask):
        self.rgb, self.mask = rgb, mask
        self.h, self.w = mask.shape
        self.m3 = mask[:, :, None]

def new(w, h): return np.zeros((h, w, 3), np.uint8), np.zeros((h, w), bool)

def px_(img, m, x, y, c):
    if 0 <= y < m.shape[0] and 0 <= x < m.shape[1]:
        img[y, x] = c; m[y, x] = True

def rect_(img, m, x, y, w, h, c):
    for j in range(h):
        for i in range(w): px_(img, m, x + i, y + j, c)

def ell_(img, m, cx, cy, rx, ry, c, c2=None):
    for j in range(-ry, ry + 1):
        for i in range(-rx, rx + 1):
            if (i / (rx + .5)) ** 2 + (j / (ry + .5)) ** 2 <= 1:
                col = c
                if c2 is not None and (i + j) > rx * .3: col = c2
                px_(img, m, cx + i, cy + j, col)

def shade(c, f): return tuple(int(max(0, min(255, v * f))) for v in c)

def blit(cv, s, x, y):
    """x,y = tengah-bawah sprite"""
    H, W = cv.shape[:2]
    x0 = x - s.w // 2; y0 = y - s.h
    sx0, sy0 = max(0, -x0), max(0, -y0)
    ex, ey = min(s.w, W - x0), min(s.h, H - y0)
    if ex <= sx0 or ey <= sy0: return
    dst = cv[y0 + sy0:y0 + ey, x0 + sx0:x0 + ex]
    np.copyto(dst, s.rgb[sy0:ey, sx0:ex], where=s.m3[sy0:ey, sx0:ex])

def blit_tl(cv, s, x, y):
    blit(cv, s, x + s.w // 2, y + s.h)

# ---------- pembuat sprite ----------
OUT = (30, 24, 28)

def house(ww, wh, rh, wall, roof, door=(80, 54, 38), chim=False, snow=False, base=None):
    w = ww + 2; h = wh + rh + (3 if chim else 0)
    img, m = new(w, h)
    top = h - wh - rh
    for r in range(rh):
        span = ww + 2 - 2 * (rh - 1 - r) if rh > 1 else ww + 2
        span = max(2, min(w, span if span % 2 == w % 2 else span + 1))
        x0 = (w - span) // 2
        c = (245, 248, 252) if snow else (roof if r % 2 == 0 else shade(roof, .86))
        rect_(img, m, x0, top + r, span, 1, c)
    rect_(img, m, 1, top + rh, ww, wh, wall)
    if base: rect_(img, m, 1, top + rh + wh - 2, ww, 2, base)
    rect_(img, m, 1 + ww // 2 - 1, top + rh + wh - 3, 2, 3, door)
    rect_(img, m, 1, top + rh, 1, wh, shade(wall, .8))
    if chim: rect_(img, m, w - 3, top - 3 + 0, 2, 4, (90, 80, 84))
    return Spr(img, m)

def tent(col):
    img, m = new(9, 7)
    for r in range(5):
        sp = 2 + r * 2
        rect_(img, m, 4 - sp // 2, r + 1, sp, 1, col if r % 2 == 0 else shade(col, .85))
    rect_(img, m, 4, 4, 1, 2, shade(col, .45))
    return Spr(img, m)

def tree_round(cvar, trunk=(96, 66, 40), r=4, snow=False, bare=False):
    w = r * 2 + 3; h = r * 2 + 5
    img, m = new(w, h)
    rect_(img, m, w // 2, h - 4, 1, 4, trunk)
    if bare:
        for k in range(3):
            px_(img, m, w // 2 - 1 - k, h - 6 - k, trunk); px_(img, m, w // 2 + 1 + k, h - 6 - k, trunk)
            px_(img, m, w // 2, h - 5 - k, trunk)
        if snow:
            for k in range(3): px_(img, m, w // 2 - 1 - k, h - 7 - k, (240, 246, 252)); px_(img, m, w // 2 + 1 + k, h - 7 - k, (240, 246, 252))
        return Spr(img, m)
    ell_(img, m, w // 2, r + 1, r, r, shade(cvar, .86))
    ell_(img, m, w // 2 - 1, r, r - 1, r - 1, cvar)
    px_(img, m, w // 2 - 2, 2, shade(cvar, 1.25)); px_(img, m, w // 2 - 1, 1, shade(cvar, 1.2))
    if snow:
        for i in range(-r + 1, r): px_(img, m, w // 2 + i, 1 + abs(i) // 2, (244, 248, 252))
    return Spr(img, m)

def pine(snow=False, col=(34, 100, 58)):
    img, m = new(9, 13)
    rect_(img, m, 4, 10, 1, 3, (92, 64, 40))
    for k, (y, wd) in enumerate(((1, 3), (4, 5), (7, 7), (9, 9))):
        for r in range(3):
            sp = max(1, wd - 2 + r - (1 if r == 0 else 0))
            sp = min(9, wd if r == 2 else max(1, wd - 2 + r))
            xx = 4 - sp // 2
            c = (236, 244, 250) if (snow and r == 0) else (col if r % 2 == 0 else shade(col, .8))
            rect_(img, m, xx, y + r - 0, sp, 1, c)
    return Spr(img, m)

def palm(col=(40, 140, 60)):
    img, m = new(11, 13)
    for j in range(5, 13): px_(img, m, 5 + (1 if j < 9 else 0), j, (120, 88, 56))
    for (dx, dy) in ((-4, 1), (-3, 0), (-2, -0), (-4, 2), (4, 1), (3, 0), (2, 0), (4, 2), (0, -1), (-1, -1), (1, -1)):
        px_(img, m, 5 + dx + 1, 4 + dy + 1, col if dy < 2 else shade(col, .8))
    for dx in range(-3, 4): px_(img, m, 5 + dx + 1, 4, shade(col, .9))
    px_(img, m, 6, 5, (200, 150, 60))
    return Spr(img, m)

def sapling(col=(90, 170, 70)):
    img, m = new(5, 5)
    rect_(img, m, 2, 3, 1, 2, (96, 66, 40)); rect_(img, m, 1, 1, 3, 2, col); px_(img, m, 2, 0, shade(col, 1.2))
    return Spr(img, m)

def granary(wall=(196, 150, 96), roof=(150, 70, 52)):
    img, m = new(12, 12)
    rect_(img, m, 1, 5, 10, 7, wall); rect_(img, m, 1, 5, 1, 7, shade(wall, .8))
    for i in range(1, 11): px_(img, m, i, 5, shade(wall, 1.15))
    for r in range(5):
        sp = 12 - r * 2
        rect_(img, m, 6 - sp // 2, r, sp, 1, roof if r % 2 == 0 else shade(roof, .86))
    rect_(img, m, 5, 8, 3, 4, (84, 56, 40))
    return Spr(img, m)

def forge():
    img, m = new(13, 13)
    rect_(img, m, 1, 6, 11, 7, (130, 132, 140)); rect_(img, m, 1, 6, 1, 7, (100, 102, 112))
    rect_(img, m, 0, 4, 13, 2, (70, 62, 70)); rect_(img, m, 8, 0, 3, 6, (92, 86, 92))
    rect_(img, m, 3, 9, 4, 4, (255, 150, 40)); rect_(img, m, 4, 10, 2, 2, (255, 230, 120))
    return Spr(img, m)

def well():
    img, m = new(7, 6)
    rect_(img, m, 0, 3, 7, 3, (128, 130, 140)); rect_(img, m, 1, 4, 5, 1, (50, 120, 200))
    rect_(img, m, 0, 0, 1, 4, (110, 80, 50)); rect_(img, m, 6, 0, 1, 4, (110, 80, 50)); rect_(img, m, 0, 0, 7, 1, (150, 100, 60))
    return Spr(img, m)

def stall(col):
    img, m = new(9, 7)
    for i in range(9): px_(img, m, i, 1, col if i % 2 == 0 else (245, 245, 240)); px_(img, m, i, 2, col if i % 2 == 0 else (245, 245, 240))
    rect_(img, m, 0, 3, 1, 4, (110, 80, 50)); rect_(img, m, 8, 3, 1, 4, (110, 80, 50)); rect_(img, m, 1, 5, 7, 2, (170, 126, 80))
    px_(img, m, 3, 4, (220, 60, 50)); px_(img, m, 5, 4, (240, 190, 60))
    return Spr(img, m)

def boat():
    img, m = new(9, 6)
    rect_(img, m, 0, 3, 9, 2, (130, 86, 50)); rect_(img, m, 1, 5, 7, 1, (100, 66, 40))
    rect_(img, m, 4, 0, 1, 3, (110, 80, 50)); rect_(img, m, 5, 0, 3, 3, (240, 236, 220))
    rect_(img, m, 2, 2, 2, 1, (230, 190, 70))
    return Spr(img, m)

def cart():
    img, m = new(7, 5)
    rect_(img, m, 0, 1, 6, 2, (150, 100, 60)); rect_(img, m, 1, 0, 4, 1, (236, 200, 80))
    px_(img, m, 1, 3, (40, 36, 40)); px_(img, m, 4, 3, (40, 36, 40))
    return Spr(img, m)

def rack():
    img, m = new(8, 5)
    rect_(img, m, 0, 0, 8, 1, (110, 80, 50)); rect_(img, m, 0, 0, 1, 5, (110, 80, 50)); rect_(img, m, 7, 0, 1, 5, (110, 80, 50))
    for i in (2, 4, 6): rect_(img, m, i - 1, 1, 1, 2, (190, 70, 64))
    return Spr(img, m)

def rubble():
    img, m = new(8, 4)
    for (x, y, c) in ((1, 2, (110, 80, 50)), (2, 1, (90, 66, 44)), (4, 2, (130, 100, 70)), (5, 1, (80, 60, 40)), (6, 3, (110, 80, 50)), (3, 3, (60, 46, 34))):
        rect_(img, m, x, y, 2, 1, c)
    return Spr(img, m)

def stump():
    img, m = new(3, 2)
    rect_(img, m, 0, 0, 3, 2, (110, 78, 48)); px_(img, m, 1, 0, (176, 140, 96))
    return Spr(img, m)

def icon(rows, pal):
    h = len(rows); w = len(rows[0]); img, m = new(w, h)
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch in pal: px_(img, m, i, j, pal[ch])
    return Spr(img, m)

ICON = {
 'sun': icon([".Y.Y.Y.Y.", "..YYYYY..", "Y.YYYYY.Y", "..YYYYY..", ".Y.Y.Y.Y."], {'Y': (255, 214, 64)}),
 'flake': icon(["..W.W..", "W..W..W", ".W.W.W.", "WWWWWWW", ".W.W.W.", "W..W..W", "..W.W.."], {'W': (230, 244, 255)}),
 'leaf': icon(["....OO..", "..OOOOO.", ".OOROOOO", "OOORROO.", "OORRROO.", ".R.OO...", "R.......", "........"][:7], {'O': (236, 130, 40), 'R': (170, 70, 30)}),
 'flower': icon([".P.P.", "PPYPP", ".PYP.", "..G..", ".GG.."], {'P': (250, 150, 190), 'Y': (255, 220, 80), 'G': (60, 150, 60)}),
 'drop': icon(["...B...", "..BBB..", ".BBBBB.", "BBLBBBB", "BBLBBBB", ".BBBBB.", "..BBB.."], {'B': (70, 150, 240), 'L': (190, 226, 255)}),
 'cloud': icon([".WWW....", "WWWWWW..", "WWWWWWWW", ".WWWWWW."], {'W': (230, 236, 244)}),
 'no': icon(["..RRRRR..", ".RR...RR.", "RR.....RR", "R.R...R.R", "R..R.R..R", "R...R...R", "R..R.R..R", "R.R...R.R", "RR.....RR", ".RR...RR.", "..RRRRR.."], {'R': (240, 70, 60)}),
 'book': icon(["BBBBBBBBB", "BWWBBBWWB", "BWWBBBWWB", "BWWBBBWWB", "BWWBBBWWB", "BBBBBBBBB"], {'B': (90, 130, 220), 'W': (240, 240, 230)}),
 'link': icon(["GGGG.GGGG", "G..G.G..G", "G..GGGG.G", "G..G.G..G", "GGGG.GGGG"], {'G': (120, 220, 130)}),
 'crate': icon(["BBBBBBB", "BYYBYYB", "BYYBYYB", "BBBBBBB", "BYYBYYB", "BBBBBBB"], {'B': (150, 100, 56), 'Y': (220, 170, 90)}),
 'cycle': icon(["..AAAAA..", ".A.....A.", "A...A...A", "A..AAA..A", "A.......A", ".A.....A.", "..AAAAA.."], {'A': (250, 200, 70)}),
 'qm': icon(["..WWW..", ".W...W.", ".....W.", "...WW..", "...W...", ".......", "...W..."], {'W': (255, 255, 255)}),
 'warn': icon(["...Y...", "..YYY..", "..YKY..", ".YYKYY.", ".YYYYY.", "YYYKYYY", "YYYYYYY"], {'Y': (255, 210, 50), 'K': (40, 30, 30)}),
 'parachute': icon([".WWWWW.", "WRWRWRW", "W.W.W.W", ".W.W.W.", "..WWW..", "..CCC..", "..CCC.."], {'W': (240, 240, 240), 'R': (230, 60, 60), 'C': (170, 120, 70)}),
 'gear': icon([".G.G.G.", "GGGGGGG", ".GG.GG.", "GGG.GGG", ".GG.GG.", "GGGGGGG", ".G.G.G."], {'G': (190, 196, 210)}),
}
