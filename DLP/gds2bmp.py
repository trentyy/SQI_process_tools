# cowork with chatgpi

import os
import gdstk
import numpy as np
from PIL import Image, ImageDraw

# ---------- scale setup ----------
img_width_px = 1280
img_height_px = 1024

DLP_res = (1280, 1024)

# calibration need to be update
calibration={
    2.5: 2.07035,
    5: 1.05932,
    10: 0.53475,
    20: 0.26385,
    50: 0.10526,
    100: 0.05291
}

"""
曝光範圍 ：
物鏡  2.5X   2320x1440
物鏡  5X   1160x720
物鏡  10X   560x360
物鏡  20X   280x180
物鏡  50X   110x70
物鏡  100X   60x35  單位：µm
"""

# ---------- 設定 ----------
gds_file = "./gds_files/SQI Lab 114 mask_03_Global 12_outer.GDS"
# 拆檔名
fname_ext = os.path.basename(gds_file)
fname = os.path.splitext(fname_ext)[0]
img_width_px = 1280
img_height_px = 1024

# 設定DLP物鏡倍率
ol = 5  # objective lens
pixel_size_um = calibration[ol]  # 1 pixel 對應多少 µm

# ---------- 讀 GDS ----------
try:
    lib = gdstk.read_gds(gds_file)
except OSError:
    print(f"cwd: {os.getcwd()}, cannot open {gds_file}")
    raise OSError
cell = lib.top_level()[0]
print("file: ", fname, "loaded")
print(f"gds unit={lib.unit}")

# ---------- 計算全局 bounding box ----------
def full_bounding_box(cell):
    boxes = []
    for p in cell.polygons:
        boxes.append(p.points)
    for ref in cell.references:
        ref_box = full_bounding_box(ref.cell)
        ref_box = ref_box + np.array(ref.origin)
        boxes.append(ref_box)
    if not boxes:
        return np.array([[0,0],[1,1]])
    all_pts = np.vstack(boxes)
    xmin, ymin = np.min(all_pts, axis=0)
    xmax, ymax = np.max(all_pts, axis=0)
    return np.array([[xmin, ymin],[xmax, ymax]])

bbox = full_bounding_box(cell)
xmin, ymin = bbox[0]
xmax, ymax = bbox[1]

print(f"xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}")

gds_width_um = xmax - xmin
gds_height_um = ymax - ymin
print(f"gds_width_um={gds_width_um}")

# ---------- 計算初步 pixel 尺寸 ----------
gds_width_px = gds_width_um / pixel_size_um
gds_height_px = gds_height_um / pixel_size_um

# 最終總縮放（GDS單位 -> pixel）
final_scale = 1 / pixel_size_um

# 偏移量，使 pattern 置中
offset_x = (img_width_px - gds_width_px) / 2 - xmin * final_scale
offset_y = (img_height_px - gds_height_px) / 2 - ymin * final_scale

# ---------- 建立黑底白圖 ----------
# DLP軟體只讀24bit的BMP檔，顏色只有(0,0,0), (255,255,255)
img = Image.new("RGB", (img_width_px, img_height_px), color=(0,0,0))
draw = ImageDraw.Draw(img)

# ---------- 繪製 GDS polygons ----------
def draw_cell_to_image(c, draw):
    for p in c.polygons:
        pts = p.points * final_scale
        pts[:,0] += offset_x
        pts[:,1] += offset_y
        polygon_pts = [(x, img_height_px - y) for x, y in pts]  # y軸翻轉
        draw.polygon(polygon_pts, fill=(255,255,255))
    for ref in c.references:
        draw_cell_to_image(ref.cell, draw)

draw_cell_to_image(cell, draw)

# ---------- 儲存 BMP ----------
img.save(f"./output_bmp/{fname}-{ol}x.bmp", format="BMP")
print(f"Saved BMP image: {fname}-{ol}x.bmp")
print(f"Scaling info: 1 pixel = {pixel_size_um} µm, final scale factor = {final_scale:.3f}")
