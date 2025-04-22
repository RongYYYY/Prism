# models/plate.py

import pygame
from constants import CELL_SIZE

class Plates:
    def __init__(self, plate_type, plate_color, plate_location, plate_xys):
        self.plate_type = plate_type
        self.plate_color = plate_color
        self.plate_location = plate_location
        self.plate_xys = plate_xys
        self.plate_coordinates = [(0, 0)] * len(plate_xys)
        self.button_rect = pygame.Rect(0, 0, 10, 10)
        self.dragging = False
        self.xy_to_coordinates()

    def draw_plate(self, screen):
        temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        if self.plate_type == 1:
            pygame.draw.polygon(temp_surface, self.plate_color, self.plate_coordinates)
        elif self.plate_type == 2:
            center = ((self.plate_location[0] * CELL_SIZE) + 100,
                      (self.plate_location[1] * CELL_SIZE) + 75)
            radius = self.plate_xys[0][0] * CELL_SIZE
            pygame.draw.circle(temp_surface, self.plate_color, center, radius)
        screen.blit(temp_surface, (0, 0))
        pygame.draw.rect(screen, (0, 0, 0), self.button_rect)

    def xy_to_coordinates(self):
        self.plate_coordinates = [
            ((x + self.plate_location[0]) * CELL_SIZE + 100,
             (y + self.plate_location[1]) * CELL_SIZE + 75)
            for x, y in self.plate_xys
        ]
        self.update_button_position()

    def update_button_position(self):
        self.button_rect.topleft = (
            self.plate_location[0] * CELL_SIZE + 100 - 5,
            self.plate_location[1] * CELL_SIZE + 75 - 5
        )
