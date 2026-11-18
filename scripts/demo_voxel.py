"""Demo + uji kecepatan voxel.py: kapal kontainer voxel di laut, kamera mengitari. Pakai: python3 demo_voxel.py out_dir"""
import sys, os, math, time, cv2
sys.path.insert(0, os.path.dirname(__file__))
from voxel import *

out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/voxel_demo'
os.makedirs(out, exist_ok=True)
ship, tug = make_ship(18, 5), make_tug()
times = [0.0, 1.0, 2.0]
t0 = time.time()
for i, T in enumerate(times):
    sc = Scene()
    water_grid(sc, T, -40, 40, -40, 60, step=2.5)
    sc.add(ship, (0, 0, 0), yaw=8 * math.sin(T), roll=2 * math.sin(T * 1.7))
    sc.add(tug, (9, 0, -4), yaw=-60)
    ang = math.radians(25 + 20 * T)
    cam = Camera((30 * math.sin(ang), 16, -30 * math.cos(ang)), (0, 2, 0), fov=55)
    img = render(sc, cam, 1080, 1920, fog=((190, 225, 255), 40, 110), pixel=3, outline=.25)
    cv2.imwrite(f'{out}/frame{i}.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
print('%.2fs per frame' % ((time.time() - t0) / len(times)))
