import pyxel
from PIL import Image

class ColorPalette:
    MaxColors = 200
    DaySky = 0
    NightSky = 0
    StatusBg = 0
    StatusFg = 0
    
    def __init__(self, paths):
        self.initial_colors = pyxel.colors.to_list()
        colors = pyxel.colors.to_list()
        ColorPalette.DaySky = len(colors)
        colors.append(0x4fefff)
        ColorPalette.NightSky = len(colors)
        colors.append(0x19194f)
        ColorPalette.StatusBg = len(colors)
        colors.append(0xa7fbff)
        ColorPalette.StatusFg = len(colors)
        colors.append(0xd25e7f)
        colors.extend(self.from_images(paths))
        pyxel.colors.from_list(colors)

    def from_images(self, paths):
        cols = []
        for path in paths:
            image = Image.open(path)
            cols.extend(image.getcolors(maxcolors = self.MaxColors))
        cols = set(cols)
        if len(cols) > self.MaxColors: raise
        pal_cols = []
        for col in cols:
            r, g, b, _ = col[1]
            pal_cols.append(r * 65536 + g * 256 + b)
        return pal_cols
