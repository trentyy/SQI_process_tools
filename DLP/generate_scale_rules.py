# generate scale rules, cowork with chatgpt
from PIL import Image, ImageDraw, ImageFont
import os

# Image size
W, H = 1280, 1024
background_color = (0, 0, 0)  # black

# Ruler properties
ruler_width = 20
ruler_color = 255  # white rulers
tick_color = 255  # white ticks/labels
small_tick_len = 10
large_tick_len = 20
small_tick_step = 20  # 20 px
large_tick_step = 100  # still major markers every 100px
left_margin = 80
right_margin = 00
step = 160

# Compute ruler positions
positions = []
x = left_margin
while x + ruler_width <= W - right_margin:
    positions.append(x)
    x += step

# Create image
img = Image.new("1", (W, H), 0)
# img = Image.new("RGB", (W, H), background_color)
draw = ImageDraw.Draw(img)

# Load font
try:
    font = ImageFont.truetype("Arial.ttf", 16)
except Exception:
    font = ImageFont.load_default()

# Draw
for rx in positions:
    # ruler
    draw.rectangle([rx, 0, rx + ruler_width - 1, H - 1], fill=ruler_color)

    tick_x_right = rx - 2  # ticks to left

    for y in range(0, H, small_tick_step):
        # label index: start bottom = 0, up = +20, +40, ...
        label_val = y // 20 * 20

        if y % large_tick_step == 0:
            tick_x_left = tick_x_right - large_tick_len
            draw.line([(tick_x_left, y), (tick_x_right, y)], fill=tick_color)
            label = str(label_val)
            bbox = font.getbbox(label)  # (x0, y0, x1, y1)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            label_x = tick_x_left - 6 - tw
            label_y = y - th / 2
            if label_y < 0: label_y = 0
            if label_y + th > H: label_y = H - th
            draw.text((label_x, label_y), label, fill=tick_color, font=font)
        else:
            tick_x_left = tick_x_right - small_tick_len
            draw.line([(tick_x_left, y), (tick_x_right, y)], fill=tick_color)

# Save output
out_path = "./output_bmp/rulers.bmp"
img.save(out_path)