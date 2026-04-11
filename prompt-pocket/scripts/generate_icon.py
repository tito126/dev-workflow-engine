from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)

size = 1024
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Background
margin = 72
bg_box = (margin, margin, size - margin, size - margin)
draw.rounded_rectangle(bg_box, radius=220, fill=(16, 28, 58, 255))

# Glow
shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
shadow_draw = ImageDraw.Draw(shadow)
shadow_draw.rounded_rectangle((150, 180, 874, 844), radius=180, fill=(79, 195, 247, 120))
shadow = shadow.filter(ImageFilter.GaussianBlur(38))
img = Image.alpha_composite(img, shadow)
draw = ImageDraw.Draw(img)

# Pocket body
pocket = (176, 248, 848, 810)
draw.rounded_rectangle(pocket, radius=168, fill=(79, 195, 247, 255))

# Pocket flap / depth
flap = [(176, 400), (336, 286), (688, 286), (848, 400), (848, 540), (176, 540)]
draw.polygon(flap, fill=(116, 213, 252, 255))

# Inner pocket shadow
inner = Image.new('RGBA', (size, size), (0, 0, 0, 0))
inner_draw = ImageDraw.Draw(inner)
inner_draw.rounded_rectangle((220, 330, 804, 760), radius=140, fill=(14, 52, 96, 160))
inner = inner.filter(ImageFilter.GaussianBlur(18))
img = Image.alpha_composite(img, inner)
draw = ImageDraw.Draw(img)

# Prompt card
card = (280, 430, 744, 730)
draw.rounded_rectangle(card, radius=72, fill=(245, 250, 255, 255))
draw.rounded_rectangle((320, 486, 646, 536), radius=24, fill=(79, 195, 247, 255))
draw.rounded_rectangle((320, 572, 704, 614), radius=20, fill=(185, 213, 236, 255))
draw.rounded_rectangle((320, 640, 620, 682), radius=20, fill=(209, 225, 241, 255))

# Spark
spark = [(746, 334), (780, 410), (856, 444), (780, 478), (746, 554), (712, 478), (636, 444), (712, 410)]
draw.polygon(spark, fill=(255, 219, 92, 255))

# Save outputs
png_path = ASSETS / 'icon.png'
ico_path = ASSETS / 'icon.ico'
img.save(png_path)
img.save(ico_path, format='ICO', sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])
print(f'Generated: {png_path}')
print(f'Generated: {ico_path}')
