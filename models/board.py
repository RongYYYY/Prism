# models/board.py

import pygame
from constants import LIGHT_GRID, CELL_SIZE
from models.plate import Plates

class Board:
    def __init__(self):
        self.le = 40
        self.he = 30
        self.plates = []
        self.boardStartX = 100
        self.boardStartY = 60
        self.width = 600
        self.height = 450
        self.cellWidth = CELL_SIZE

    def draw_grid(self, screen):
        for x in range(41):
            pygame.draw.line(screen, LIGHT_GRID, 
                             (self.boardStartX + x*self.cellWidth, self.boardStartY), 
                             (self.boardStartX + x*self.cellWidth, self.height + self.boardStartY))
        for y in range(31):
            pygame.draw.line(screen, LIGHT_GRID, 
                             (self.boardStartX, self.boardStartY + y*self.cellWidth), 
                             (self.boardStartX + self.width, self.boardStartY + y*self.cellWidth))

    def draw_board(self, screen):
        for plate in self.plates:
            plate.draw_plate(screen)

    def get_plate_at(self, pos):
        for plate in reversed(self.plates):
            if plate.button_rect.collidepoint(pos):
                return plate
        return None

    def add_plate(self, plate):
        self.plates.append(plate)

    def bring_to_top(self, plate):
        if plate in self.plates:
            self.plates.remove(plate)
            self.plates.append(plate)
