"""Create a lightweight animated GIF for Clear New Tab's wallpaper picker."""
from pathlib import Path
from PIL import Image, ImageDraw
import math

WIDTH, HEIGHT, FRAMES = 1280, 720, 32
background = (16, 17, 22)
images = []
for frame in range(FRAMES):
    image = Image.new('RGB', (WIDTH, HEIGHT), background)
    pen = ImageDraw.Draw(image)
    for x in range(WIDTH):
        wave = .5 + .5 * math.cos(x / WIDTH * math.tau * 2 - frame / FRAMES * math.tau)
        strength = .36 + .64 * wave
        r = round(background[0] + (255-background[0]) * strength)
        g = round(background[1] + (0-background[1]) * strength)
        b = round(background[2] + (81-background[2]) * strength)
        pen.line((x, 0, x, 5), fill=(r, g, b))
        for y in range(6, 19):
            blend = strength * .2 * math.exp(-(y-6)/5)
            pen.point((x, y), fill=(round(background[0]+239*blend), round(background[1]-17*blend), round(background[2]+59*blend)))
    images.append(image.quantize(colors=96, method=Image.Quantize.FASTOCTREE))
images[0].save(Path(__file__).with_name('Scarlet-Protocol-Animated.gif'), save_all=True, append_images=images[1:], duration=125, loop=0, disposal=2, optimize=True)
