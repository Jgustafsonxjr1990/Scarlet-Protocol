"""Regenerate the bundled static Chrome tab and toolbar textures. Requires Pillow."""
from pathlib import Path
from PIL import Image
import math

OUT = Path(__file__).parent / 'images'
OUT.mkdir(exist_ok=True)
BASE = (16, 17, 22)
SCARLET = (255, 0, 81)


def blend(a, b, n):
    return tuple(round(x * (1 - n) + y * n) for x, y in zip(a, b))


def texture(name, kind):
    im = Image.new('RGB', (2048, 128), BASE)
    pixels = im.load()
    for y in range(128):
        for x in range(2048):
            if kind == 'tabs':
                # Chrome clips this band to each native tab shape. Every tab gets the same scarlet edge.
                core = .98 if y < 3 else .9 if y < 6 else .74 * math.exp(-(y - 6) / 17) if y < 50 else 0
                shade = .86 + .12 * math.cos(x * .019)
                strength = max(0, core * shade)
            elif kind == 'toolbar':
                strength = .84 if y < 2 else .5 if y < 5 else .28 * math.exp(-(y - 5) / 11) if y < 43 else 0
            elif kind == 'frame':
                strength = .05 * math.exp(-y / 24)
            else:
                strength = 0
            # Fine contact marks repeat along the static illuminated surface.
            if kind == 'tabs' and y in (1, 2) and x % 192 < 20:
                pixels[x, y] = blend(BASE, (255, 148, 175), .85)
            elif kind == 'toolbar' and y == 3 and x % 192 in range(28, 43):
                pixels[x, y] = blend(BASE, (255, 99, 137), .65)
            else:
                pixels[x, y] = blend(BASE, SCARLET, strength)
    im.save(OUT / name, optimize=True)


if __name__ == '__main__':
    texture('tabs.png', 'tabs')
    texture('toolbar.png', 'toolbar')
    texture('frame.png', 'frame')
    texture('window-controls.png', 'controls')
