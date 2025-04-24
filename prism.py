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
- Level Selection on startup (6 levels)
- Home button (top-left) to return to level select
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
BUTTON_FONT = pygame.font.SysFont("couriernew", 32)

# === Colors & Buttons ===
WHITE = additive_blend([REDD, GREEND, BLUED])
color_buttons = [
    (REDD, pygame.Rect(720, 150, 50, 50)),
    (GREEND, pygame.Rect(720, 250, 50, 50)),
    (BLUED, pygame.Rect(720, 350, 50, 50))
]

# === Load Assets ===
start_image = pygame.image.load("images/start.jpg")
instruction_image = pygame.image.load("images/instruction.png")
home_icon = pygame.image.load("images/home.png")
home_icon = pygame.transform.scale(home_icon, (40, 40))
home_icon_rect = home_icon.get_rect(topleft=(20, 20))

# === State Variables ===
selected_color = None
selected_plate = None
show_isometric = False
show_start_screen = True
show_instruction_screen = False
show_result_screen = False
show_level_select = True
result_text = ""
current_level = None
board = Board()
level = None

# === Level Selection Layout ===
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 60
LEVEL_COLS = 3
LEVEL_ROWS = 2
margin_x = 80
spacing_x = (SCREEN_WIDTH - 2*margin_x - LEVEL_COLS*BUTTON_WIDTH) // (LEVEL_COLS - 1)
margin_y = 200
spacing_y = 40
level_buttons = []
for lvl in range(1, LEVEL_COLS * LEVEL_ROWS + 1):
    idx = lvl - 1
    row = idx // LEVEL_COLS
    col = idx % LEVEL_COLS
    x = margin_x + col * (BUTTON_WIDTH + spacing_x)
    y = margin_y + row * (BUTTON_HEIGHT + spacing_y)
    rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    level_buttons.append((lvl, rect))

# === Instruction and Result Navigation ===
home_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 160, 150, 50)
enter_text_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 40)
next_text_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60, 120, 40)
back_text_rect = pygame.Rect(50, SCREEN_HEIGHT - 60, 120, 40)

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

# === Main Loop ===
running = True
while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if show_start_screen:
            if event.type == pygame.MOUSEBUTTONDOWN and enter_text_rect.collidepoint(event.pos):
                show_start_screen = False
                show_instruction_screen = True
            continue

        if show_instruction_screen:
            if event.type == pygame.MOUSEBUTTONDOWN and next_text_rect.collidepoint(event.pos):
                show_instruction_screen = False
                show_level_select = True
            continue

        # Level selection input
        if show_level_select:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for lvl, rect in level_buttons:
                    if rect.collidepoint(event.pos):
                        current_level = lvl
                        level = Level(current_level)
                        level.load(board)
                        show_level_select = False
                        show_result_screen = True
                        result_text = f"{level.level_name}"
                        button_text = "Start"
            if event.type == pygame.MOUSEBUTTONDOWN and back_text_rect.collidepoint(event.pos):
                show_level_select = False
                show_instruction_screen = True
            continue

        if event.type == pygame.MOUSEBUTTONDOWN:
            if home_icon_rect.collidepoint(event.pos):
                show_level_select = True
                show_result_screen = False
                show_isometric = False

        if show_result_screen:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if home_button.collidepoint(event.pos):
                    show_result_screen = False
                    if check_answer(board, current_level): show_level_select = True
            continue

        # Game input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                show_isometric = not show_isometric
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                show_result_screen = True
                result_text = "Win :D" if check_answer(board, current_level) else "Try again :("
                button_text = "Home" if check_answer(board, current_level) else "Back"

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

    # === Drawing ===
    if show_start_screen:
        screen.blit(pygame.transform.scale(start_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        txt = BUTTON_FONT.render("Enter the Game", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=enter_text_rect.center))

    elif show_instruction_screen:
        screen.blit(pygame.transform.scale(instruction_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        txt = BUTTON_FONT.render("Next>", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=next_text_rect.center))

    elif show_level_select:
        screen.fill(WHITE)
        title_surf = FONT.render("Select Level", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surf, title_rect)
        for lvl, rect in level_buttons:
            pygame.draw.rect(screen, LIGHT_GRID, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            txt = instr = pygame.font.SysFont("couriernew", 24).render(f"{Level.level_names[lvl-1]}", True, (0, 0, 0))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)
        back_txt = BUTTON_FONT.render("<Back", True, (0, 0, 0))
        screen.blit(back_txt, back_txt.get_rect(center=back_text_rect.center))

    elif show_result_screen:
        screen.fill(WHITE)
        level.draw_level_icon(screen, (0, -100), (800, 600))
        txt = FONT.render(result_text, True, (0, 0, 0))
        screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)))
        pygame.draw.rect(screen, LIGHT_GRID, home_button)
        pygame.draw.rect(screen, (0, 0, 0), home_button, 2)
        txt = BUTTON_FONT.render(button_text, True, (0, 0, 0))
        screen.blit(txt, txt.get_rect(center=home_button.center))

    else:
        screen.fill(WHITE)
        screen.blit(home_icon, home_icon_rect)
        if show_isometric:
            iso_board = IsoBoard(board.plates)
            iso_proj = IsoProjection(board.plates, scale=1.8, offset=(10, 80))
            iso_board.draw_board(screen)
            iso_board.draw_grid()
            iso_proj.draw_projection(screen, blit_position=(400, 0))
            instr = pygame.font.SysFont("couriernew", 24).render(
                "SPACE: Toggle view | ENTER: Check solution", True, (255, 255, 255)
            )
            screen.blit(instr, instr.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))
            level.draw_level_icon(screen)
            ttt = pygame.font.SysFont("couriernew", 18).render(
                "Target Shape", True, (255, 255, 255)
            )
            screen.blit(ttt, ttt.get_rect(center=(105, 20)))
        else:
            board.draw_grid(screen)
            board.draw_board(screen)
            draw_color_buttons()
            instr = pygame.font.SysFont("couriernew", 24).render(
                "SPACE: Toggle view | ENTER: Check solution", True, (0, 0, 0)
            )
            screen.blit(instr, instr.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))
            if selected_color:
                color_name = "Red" if selected_color == REDD else "Green" if selected_color == GREEND else "Blue"
                instrSelect = pygame.font.SysFont("couriernew", 16).render(
                f"Drag controller to move shape | Click controller to color {color_name}", True, (0, 0, 0)
            )
            else:
                instrSelect = pygame.font.SysFont("couriernew", 16).render(
                f"Drag controller to move shape | Select color to assign", True, (0, 0, 0)
            )
            screen.blit(instrSelect, instrSelect.get_rect(center=(SCREEN_WIDTH // 2 + 70, 40)))

    pygame.display.flip()

pygame.quit()
sys.exit()
