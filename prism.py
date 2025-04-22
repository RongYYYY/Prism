"""
Luminara Game

Plate: A single shape unit defined by:
- type (polygon or circle)
- location (grid coordinate)
- relative coordinates (local shape points)
- color (modifiable via UI)

Board: A container for plates that:
- manages rendering all plates on a grid
- allows selection and dragging of individual plates
- supports snapping to a defined grid layout

Level: Represents a game level:
- defines which plates to load onto the board

(TBA) Round: Represents a game round, containing:
- a `Board`
- a target number or condition
- logic to check for completion (e.g., goal state)

Interface Features:
- Grid Dimensions: 40x30 (with cell size = 15px)
- Plate Color: White by default, change via color buttons
- Toggle View: Switch between 2D and isometric projection using SPACE
- Plate Dragging: Move plates by dragging the small black handle
"""


# main.py

import pygame
import sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, LIGHT_GRID, REDD, GREEND, BLUED
from utils import additive_blend
from models.board import Board
from models.level import Level
from models.iso_board import IsoBoard
from models.iso_projection import IsoProjection

# === Initialize pygame ===
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Luminara Demo")
FONT = pygame.font.SysFont("couriernew", 24)

# === Define Colors & Buttons ===
WHITE = additive_blend([REDD, GREEND, BLUED])
color_buttons = [
    (REDD, pygame.Rect(720, 150, 50, 50)),
    (GREEND, pygame.Rect(720, 250, 50, 50)),
    (BLUED, pygame.Rect(720, 350, 50, 50))
]

selected_color = None
selected_plate = None
show_isometric = False

# === Initialize Board and Level ===
board = Board()
current_level = 6
level = Level(current_level)
level.load(board)

def draw_color_buttons():
    for color, rect in color_buttons:
        pygame.draw.rect(screen, color, rect)

def check_answer(board, current_level):
    answer = Level.level_answer[current_level]
    initial = answer[0][2]
    for plate in board.plates:
        if plate.plate_xys == initial:
            ini = plate.plate_location
    for plate in board.plates:
        curr = False
        for (loc, color, xys) in answer:
            if xys == plate.plate_xys:
                if color == plate.plate_color and loc == (
                    plate.plate_location[0] - ini[0],
                    plate.plate_location[1] - ini[1]
                ):
                    curr = True
        if not curr:
            return False
    return True

# === Game Loop ===
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                show_isometric = not show_isometric

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for color, rect in color_buttons:
                if rect.collidepoint(event.pos):
                    selected_color = color
                    break
            else:
                selected_plate = board.get_plate_at(event.pos)
                if selected_plate:
                    if selected_color:
                        selected_plate.plate_color = selected_color
                        selected_color = None
                    else:
                        selected_plate.dragging = True
                        board.bring_to_top(selected_plate)

        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_plate:
                x = round((event.pos[0] - 100) / 15)
                y = round((event.pos[1] - 75) / 15)
                selected_plate.plate_location = (x, y)
                selected_plate.xy_to_coordinates()
                selected_plate.dragging = False
                selected_plate = None

        elif event.type == pygame.MOUSEMOTION and selected_plate and selected_plate.dragging:
            x = (event.pos[0] - 100) / 15
            y = (event.pos[1] - 75) / 15
            selected_plate.plate_location = (x, y)
            selected_plate.xy_to_coordinates()

    # === Draw ===
    if show_isometric:
        if check_answer(board, current_level):
            print("Win!")

        isoBoard = IsoBoard(board.plates)
        isoProjection = IsoProjection(board.plates, scale=1.8, offset=(10, 80))
        isoBoard.draw_board(screen)
        isoBoard.draw_grid()
        isoProjection.draw_projection(screen, blit_position=(400, 0))

        LIGHT = (255, 255, 100, 80)
        light_source = (80, 300)
        all_corners = [pt for plate in isoBoard.isoPlates for pt in plate[2] if plate[2]]

        if all_corners:
            top_point = min(all_corners, key=lambda p: p[1])
            bottom_point = max(all_corners, key=lambda p: p[1])
            light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(light_surface, LIGHT, [light_source, top_point, bottom_point])
            screen.blit(light_surface, (0, 0))
    else:
        board.draw_grid(screen)
        board.draw_board(screen)
        draw_color_buttons()
        instruction_text = FONT.render("Press SPACE to toggle view", True, (0, 0, 0))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT - 60))

    pygame.display.flip()

pygame.quit()
sys.exit()
