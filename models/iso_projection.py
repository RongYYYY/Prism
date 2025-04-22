# models/iso_projection.py

import pygame
import numpy
import math
from models.iso_board import IsoBoard

class IsoProjection:
    def __init__(self, plates, scale=2, offset=(500, 100)):
        self.isoPlates = IsoBoard.compute_iso_plates(plates, scale=scale, offset=offset)
        self.scale = scale
        self.offset = offset

    def draw_projection(self, screen, blit_position=(500, 0)):
        width, height = screen.get_size()
        blended_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        rgb_sum = numpy.zeros((width, height, 3), dtype=numpy.float32)
        count = numpy.zeros((width, height), dtype=numpy.uint8)

        for plate in self.isoPlates:
            shape_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(shape_surface, plate[1], plate[2])
            shape_array = pygame.surfarray.pixels3d(shape_surface)
            alpha_mask = pygame.surfarray.array_alpha(shape_surface)
            active = alpha_mask > 0
            rgb_sum[active] += shape_array[active]
            count[active] += 1

        max_vals = rgb_sum.max(axis=2)
        scale = numpy.ones_like(max_vals)
        overflow = max_vals > 255
        scale[overflow] = 255.0 / max_vals[overflow]

        for c in range(3):
            rgb_sum[:, :, c] *= scale

        numpy.clip(rgb_sum, 0, 255, out=rgb_sum)
        result_array = rgb_sum.astype(numpy.uint8)

        final_surface = pygame.surfarray.make_surface(result_array)
        final_surface.set_alpha(255)
        screen.blit(final_surface, blit_position)
