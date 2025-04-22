# models/iso_board.py

import pygame
import math
import numpy
from constants import LIGHT_GRID

class IsoBoard:
    startX = 160
    startY = 180

    def __init__(self, plates):
        self.plates = plates
        self.isoPlates = self.compute_iso_plates(plates, scale=1, offset=(IsoBoard.startX, IsoBoard.startY))

    @staticmethod
    def compute_conversion(x, y, scale, offset):
        ex = scale * (x + 4.5 * x) + offset[0]
        ey = scale * (y + 5 * y + 2 * x) + offset[1]
        return (ex, ey)

    @staticmethod
    def compute_iso_plates(plates, scale=1, offset=(0, 0)):
        def conversion(x, y):
            return IsoBoard.compute_conversion(x, y, scale, offset)

        isoPlates = []

        for plate in plates:
            if plate.plate_type == 1:
                isoP = []
                for (x, y) in plate.plate_xys:
                    ex = plate.plate_location[0] + x
                    ey = plate.plate_location[1] + y
                    isoP.append(conversion(ex, ey))
                isoPlates.append((1, plate.plate_color, isoP))
            elif plate.plate_type == 2:
                cx, cy = plate.plate_location
                radius = plate.plate_xys[0][0]

                A = conversion(cx - radius, cy - radius)
                B = conversion(cx + radius, cy - radius)
                C = conversion(cx - radius, cy + radius)
                D = conversion(cx + radius, cy + radius)

                def bilinear_map(u, v):
                    x = (1 - u) * (1 - v) * A[0] + u * (1 - v) * B[0] + (1 - u) * v * C[0] + u * v * D[0]
                    y = (1 - u) * (1 - v) * A[1] + u * (1 - v) * B[1] + (1 - u) * v * C[1] + u * v * D[1]
                    return (x, y)

                points = []
                resolution = 60
                for i in range(resolution):
                    angle = 2 * math.pi * i / resolution
                    u = 0.5 + 0.5 * math.cos(angle)
                    v = 0.5 + 0.5 * math.sin(angle)
                    points.append(bilinear_map(u, v))

                isoPlates.append((2, plate.plate_color, points))

        return isoPlates

    def draw_board(self, screen, blit_position=(0, 0)):
        width, height = screen.get_size()
        blended_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        rgb_sum = numpy.zeros((width, height, 3), dtype=numpy.float32)
        count = numpy.zeros((width, height), dtype=numpy.uint8)

        for plate in self.isoPlates:
            shape_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(shape_surface, plate[1], plate[2])
            shape_array = pygame.surfarray.pixels3d(shape_surface)
            mask = pygame.surfarray.array_alpha(shape_surface)
            active_pixels = mask > 0
            rgb_sum[active_pixels] += shape_array[active_pixels]
            count[active_pixels] += 1

        count[count == 0] = 1
        result_array = (rgb_sum / count[..., None])
        numpy.clip(result_array, 0, 255, out=result_array)
        result_array = result_array.astype(numpy.uint8)

        final_surface = pygame.surfarray.make_surface(result_array)
        final_surface.set_alpha(255)
        screen.blit(final_surface, blit_position)

    def draw_grid(self):
        for x in range(0, 41, 5):
            pygame.draw.line(
                pygame.display.get_surface(), LIGHT_GRID,
                self.conversion(x, 0),
                self.conversion(x, 30),
                1
            )
        for y in range(0, 31, 5):
            pygame.draw.line(
                pygame.display.get_surface(), LIGHT_GRID,
                self.conversion(0, y),
                self.conversion(40, y),
                1
            )

    @staticmethod
    def conversion(x, y):
        return IsoBoard.compute_conversion(x, y, 1, (IsoBoard.startX, IsoBoard.startY))
