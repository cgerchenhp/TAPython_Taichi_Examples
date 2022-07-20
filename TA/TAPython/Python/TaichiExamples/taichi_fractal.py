import unreal
import taichi as ti
from Utilities.Utils import Singleton


ti.init(arch=ti.gpu)

n = 120
pixels = ti.field(dtype=float, shape=(n * 2, n))


@ti.func
def complex_sqr(z):
    return ti.Vector([z[0]**2 - z[1]**2, z[1] * z[0] * 2])


@ti.kernel
def paint(t: float):
    for i, j in pixels:  # Parallelized over all pixels
        c = ti.Vector([-0.8, ti.cos(t) * 0.2])
        z = ti.Vector([i / n - 1, j / n - 0.5]) * 2
        iterations = 0
        while z.norm() < 20 and iterations < 50:
            z = complex_sqr(z) + c
            iterations += 1
        pixels[i, j] = 1 - iterations * 0.02


class Taichi_fractal(metaclass=Singleton):
    def __init__(self, jsonPath:str):
        self.jsonPath = jsonPath
        self.data = unreal.PythonBPLib.get_chameleon_data(self.jsonPath)
        self.ui_image = "taichi_fractal_image"
        self.colors =  [unreal.LinearColor(1, 1, 1, 1) for _ in range(2 * n * n)]
        self.tick_count = 0

    def on_tick(self):
        paint(self.tick_count * 0.03)
        x_np = pixels.to_numpy()
        width = 2 * n
        height = n

        for x, v in enumerate(x_np):
            for y, c in enumerate(v):
                index = y * width + x
                self.colors[index].r = self.colors[index].g = self.colors[index].b = float(c)
        self.data.set_image_pixels(self.ui_image, self.colors, width, height)
        self.tick_count += 1

    def on_button_click(self):
        self.tick_count = 0
