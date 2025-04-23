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
- defines the win/lose logic of each level

Interface Features:
- Grid Dimensions: 40x30 (with cell size = 15px)
- Plate Color: Gray by default, change via color buttons
- Plate Dragging: Move plates by dragging the small black handle
- Press SPACE to toggle view (switch between 2D and isometric projection)
- Press ENTER to check solution and view result screen
"""

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
FONT = pygame.font.SysFont("couriernew", 48)

# === Define Colors & Buttons ===
WHITE = additive_blend([REDD, GREEND, BLUED])
color_buttons = [
    (REDD, pygame.Rect(720, 150, 50, 50)),
    (GREEND, pygame.Rect(720, 250, 50, 50)),
    (BLUED, pygame.Rect(720, 350, 50, 50))
]

# === State Variables ===
selected_color = None
selected_plate = None
show_isometric = False
show_result_screen = False
result_text = ""

# === Initialize Board and Level ===
board = Board()
current_level = 1
level = Level(current_level)
level.load(board)

# === Helpers ===
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
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                show_isometric = not show_isometric
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                show_result_screen = not show_result_screen
                if check_answer(board, current_level):
                    result_text = "Win! :)"
                else:
                    result_text = "Lose :("

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

    # Drawing
    if show_result_screen:
        # Display win/lose message
        screen.fill(WHITE)
        text_surf = FONT.render(result_text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text_surf, text_rect)

    else:
        screen.fill(WHITE)
        if show_isometric:
            iso_board = IsoBoard(board.plates)
            iso_proj = IsoProjection(board.plates, scale=1.8, offset=(10, 80))
            iso_board.draw_board(screen)
            iso_board.draw_grid()
            iso_proj.draw_projection(screen, blit_position=(400, 0))
            instr = pygame.font.SysFont("couriernew", 24).render(
                "SPACE: Toggle view | ENTER: Check solution", True, (255, 255, 255)
            )
            screen.blit(
                instr,
                (
                    SCREEN_WIDTH // 2 - instr.get_width() // 2,
                    SCREEN_HEIGHT - 50
                )
            )
        else:
            board.draw_grid(screen)
            board.draw_board(screen)
            draw_color_buttons()
            instr = pygame.font.SysFont("couriernew", 24).render(
                "SPACE: Toggle view | ENTER: Check solution", True, (0, 0, 0)
            )
            screen.blit(
                instr,
                (
                    SCREEN_WIDTH // 2 - instr.get_width() // 2,
                    SCREEN_HEIGHT - 50
                )
            )

    pygame.display.flip()

pygame.quit()
sys.exit()
