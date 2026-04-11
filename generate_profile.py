"""Generate a techy profile picture as PNG using Pillow."""

import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SIZE = 400
BG = (6, 13, 19)
CYAN = (0, 255, 204)
CYAN_DIM = (0, 180, 140)
CYAN_FAINT = (0, 80, 60)

img = Image.new("RGB", (SIZE, SIZE), BG)
draw = ImageDraw.Draw(img)


# ── Grid ──────────────────────────────────────────────────────────────────────
for i in range(0, SIZE, 40):
    draw.line([(i, 0), (i, SIZE)], fill=(0, 40, 30), width=1)
    draw.line([(0, i), (SIZE, i)], fill=(0, 40, 30), width=1)


# ── Circuit traces ─────────────────────────────────────────────────────────────
traces = [
    # top-left
    [(40,40),(40,80),(80,80),(80,120),(120,120)],
    [(80,40),(80,60),(120,60),(120,40)],
    # bottom-right
    [(360,360),(360,320),(320,320),(320,280),(280,280)],
    [(320,360),(320,340),(280,340),(280,360)],
    # top-right
    [(360,40),(320,40),(320,80),(280,80),(280,120)],
    # bottom-left
    [(40,360),(80,360),(80,320),(120,320),(120,280)],
]
for trace in traces:
    draw.line(trace, fill=CYAN_DIM, width=2)

# nodes
nodes = [
    (40,80),(80,80),(80,120),(120,120),(80,60),(120,60),
    (360,320),(320,320),(320,280),(280,280),(320,340),(280,340),
    (320,80),(280,80),(280,120),
    (80,320),(120,320),(120,280),
]
for nx, ny in nodes:
    draw.ellipse([(nx-4, ny-4),(nx+4, ny+4)], fill=CYAN_DIM)
    draw.ellipse([(nx-2, ny-2),(nx+2, ny+2)], fill=CYAN)


# ── Outer ring ────────────────────────────────────────────────────────────────
cx, cy, r = 200, 200, 115
draw.ellipse([(cx-r, cy-r),(cx+r, cy+r)], outline=CYAN_FAINT, width=2)

# tick marks at 0 / 90 / 180 / 270 and diagonals
ticks = [0, 45, 90, 135, 180, 225, 270, 315]
for angle in ticks:
    rad = math.radians(angle)
    x1 = cx + (r) * math.sin(rad)
    y1 = cy - (r) * math.cos(rad)
    x2 = cx + (r + 10) * math.sin(rad)
    y2 = cy - (r + 10) * math.cos(rad)
    draw.line([(x1, y1),(x2, y2)], fill=CYAN_DIM, width=2)


# ── Inner dark fill ───────────────────────────────────────────────────────────
mask = Image.new("L", (SIZE, SIZE), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.ellipse([(cx-r+2, cy-r+2),(cx+r-2, cy+r-2)], fill=255)
dark = Image.new("RGB", (SIZE, SIZE), (6, 10, 15))
img = Image.composite(dark, img, mask)
draw = ImageDraw.Draw(img)

# redraw ring on top
draw.ellipse([(cx-r, cy-r),(cx+r, cy+r)], outline=CYAN_DIM, width=2)
for angle in ticks:
    rad = math.radians(angle)
    x1 = cx + (r) * math.sin(rad)
    y1 = cy - (r) * math.cos(rad)
    x2 = cx + (r + 10) * math.sin(rad)
    y2 = cy - (r + 10) * math.cos(rad)
    draw.line([(x1, y1),(x2, y2)], fill=CYAN_DIM, width=2)


# ── Glow layer for DH ─────────────────────────────────────────────────────────
glow_layer = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
glow_draw = ImageDraw.Draw(glow_layer)

try:
    font_large = ImageFont.truetype("cour.ttf", 110)
    font_small = ImageFont.truetype("cour.ttf", 13)
    font_tiny  = ImageFont.truetype("cour.ttf", 10)
except OSError:
    try:
        font_large = ImageFont.truetype("C:/Windows/Fonts/cour.ttf", 110)
        font_small = ImageFont.truetype("C:/Windows/Fonts/cour.ttf", 13)
        font_tiny  = ImageFont.truetype("C:/Windows/Fonts/cour.ttf", 10)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_tiny  = ImageFont.load_default()

# draw glow (blurred cyan)
bbox = glow_draw.textbbox((0, 0), "DH", font=font_large)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
glow_draw.text((cx - tw//2, cy - th//2 - 10), "DH", font=font_large, fill=(0, 180, 120))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=12))

img = Image.blend(img, glow_layer, alpha=0.7)
draw = ImageDraw.Draw(img)


# ── DH monogram ───────────────────────────────────────────────────────────────
bbox = draw.textbbox((0, 0), "DH", font=font_large)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
draw.text((cx - tw//2, cy - th//2 - 10), "DH", font=font_large, fill=CYAN)


# ── DEV label ─────────────────────────────────────────────────────────────────
label = "D  E  V"
bbox2 = draw.textbbox((0, 0), label, font=font_small)
lw = bbox2[2] - bbox2[0]
draw.text((cx - lw//2, cy + 62), label, font=font_small, fill=CYAN_DIM)


# ── Terminal prompt ───────────────────────────────────────────────────────────
prompt = "$ python claude_buddy.py"
bbox3 = draw.textbbox((0, 0), prompt, font=font_tiny)
pw = bbox3[2] - bbox3[0]
draw.text((cx - pw//2, cy + 88), prompt, font=font_tiny, fill=CYAN_FAINT)

# cursor
draw.rectangle([(cx + pw//2 + 4, cy + 88),(cx + pw//2 + 10, cy + 99)], fill=CYAN_DIM)


# ── Hex corner labels ─────────────────────────────────────────────────────────
corners = [
    ((8, 6), "0x4448"),
    ((310, 6), "0xA1B2"),
    ((8, 386), "0xFF00"),
    ((308, 386), "0x7E3C"),
]
for pos, text in corners:
    draw.text(pos, text, font=font_tiny, fill=CYAN_FAINT)


# ── Save ──────────────────────────────────────────────────────────────────────
out = "profile.png"
img.save(out)
print(f"Saved: {out}")
