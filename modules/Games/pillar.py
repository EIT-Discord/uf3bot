import numpy as np
from PIL import Image


class Pillar:
    """General Purpose Plotter with PIL"""

    def __init__(self, resolution: tuple, background_color: str = 'white', spacing: int = 0):
        self.resolution = resolution

        self.background_color = background_color
        self.spacing = spacing

        self.shape = (1, 1)

    def plot(self, matrix: np.array):
        self.shape = matrix.shape

        img = Image.new('RGBA', (self.resolution[0], self.resolution[1]), color=self.background_color)

        for idx, element in np.ndenumerate(matrix):
            if isinstance(element, Tile):
                try:
                    tile_img = element.get_img(idx).resize(self._tile_canvas_resolution())
                except ValueError:
                    raise ValueError('Tile Image is smaller than spacing')
                img.paste(tile_img, self._anchor(idx), mask=tile_img)

        return img

    def _anchor(self, idx):
        """Returns the anchor point (in pixels) for a given tile index."""
        return idx[0] * self._tile_resolution()[0] + self.spacing, idx[1] * self._tile_resolution()[1] + self.spacing

    def _tile_resolution(self):
        """Returns the resolution of 1 Tile (without spacing) as a tuple (x, y)."""
        return int(self.resolution[0] / self.shape[0]), int (self.resolution[1] / self.shape[1])

    def _tile_canvas_resolution(self):
        """Returns the resolution of 1 Tile (with spacing) as a tuple (x, y)."""
        return self._tile_resolution()[0] - (2 * self.spacing), self._tile_resolution()[1] - (2 * self.spacing)


class Tile:
    def get_img(self, idx):
        return Image.new('RGB', (50, 50), color='white')
