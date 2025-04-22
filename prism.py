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


import pygame 
import sys
import math
import numpy

class Plates:
    def __init__(self, plate_type, plate_color, plate_location, plate_xys):
        self.plate_type = plate_type
        self.plate_color = plate_color
        self.plate_location = plate_location 
        self.plate_xys = plate_xys
        self.plate_coordinates = [(0, 0) for _ in range(len(plate_xys))]
        self.button_rect = pygame.Rect(0, 0, 10, 10)  # Move handle
        self.xy_to_coordinates()
        self.dragging = False
        self.update_button_position()

    def draw_plate(self, screen):
        # Create a transparent surface
        temp_surface = pygame.Surface((800, 600), pygame.SRCALPHA)

        if self.plate_type == 1:
            pygame.draw.polygon(temp_surface, self.plate_color, self.plate_coordinates)
        elif self.plate_type == 2:
            center = (self.plate_location[0]*15 + 100, self.plate_location[1]*15 + 75)
            radius = self.plate_xys[0][0]*15
            pygame.draw.circle(temp_surface, self.plate_color, center, radius)

        # Blit the shape onto the screen with transparency
        screen.blit(temp_surface, (0, 0))

        # Draw the tiny move button (opaque)
        pygame.draw.rect(screen, (0, 0, 0), self.button_rect)

    def xy_to_coordinates(self):
        for i in range(len(self.plate_xys)):
            self.plate_coordinates[i] = (
                (self.plate_xys[i][0] + self.plate_location[0]) * 15 + 100,
                (self.plate_xys[i][1] + self.plate_location[1]) * 15 + 75
            )
        self.update_button_position()

    def update_button_position(self):
        x = self.plate_location[0] * 15 + 100 - 5
        y = self.plate_location[1] * 15 + 75 - 5
        self.button_rect.topleft = (x, y)

class Board:
    def __init__(self):
        self.le = 40
        self.he = 30
        self.plates = []
        
        self.boardStartX = 100
        self.boardStartY = 60
        self.width = 600
        self.height = 450
        self.cellWidth = 15

    def draw_grid(self):
        for x in range(41):
            pygame.draw.line(screen, LIGHT_GRID, (self.boardStartX + x*self.cellWidth, self.boardStartY), (self.boardStartX + x*self.cellWidth, self.height + self.boardStartY), 1)
        for y in range(31):
            pygame.draw.line(screen, LIGHT_GRID, (self.boardStartX, self.boardStartY + y*self.cellWidth), (self.boardStartX + self.width, self.boardStartY + y*self.cellWidth), 1)

    def add_plate(self, plate):
        self.plates.append(plate)

    def draw_board(self, screen):
        for plate in self.plates:
            plate.draw_plate(screen)

    def get_plate_at(self, pos):
        for plate in reversed(self.plates):
            if plate.button_rect.collidepoint(pos):
                return plate
        return None

    def bring_to_top(self, plate):
        if plate in self.plates:
            self.plates.remove(plate)
            self.plates.append(plate)

class IsoBoard: 
    startX = 160
    startY = 180

    def __init__(self, plates):
        self.plates = plates
        self.isoPlates = self.compute_iso_plates(plates, scale=1, offset=(IsoBoard.startX, IsoBoard.startY))

    @staticmethod
    def compute_iso_plates(plates, scale=1, offset=(0, 0)):
        """Shared method to generate isometric plate data"""
        def conversion(x, y):
            ex = scale * (x + 4.5 * x) + offset[0]
            ey = scale * (y + 5 * y + 2 * x) + offset[1]
            return (ex, ey)

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

        # Track RGB sum and number of contributions
        rgb_sum = numpy.zeros((width, height, 3), dtype=numpy.float32)
        count = numpy.zeros((width, height), dtype=numpy.uint8)

        for plate in self.isoPlates:
            shape_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(shape_surface, plate[1], plate[2])
            shape_array = pygame.surfarray.pixels3d(shape_surface)
            mask = pygame.surfarray.array_alpha(shape_surface)

            # Only update pixels where the alpha is non-zero
            active_pixels = mask > 0
            rgb_sum[active_pixels] += shape_array[active_pixels]
            count[active_pixels] += 1

        # Prevent division by zero
        count[count == 0] = 1

        # Average the contributions for smoother color blending
        result_array = (rgb_sum / count[..., None])
        numpy.clip(result_array, 0, 255, out=result_array)
        result_array = result_array.astype(numpy.uint8)

        final_surface = pygame.surfarray.make_surface(result_array)
        final_surface.set_alpha(255)
        screen.blit(final_surface, blit_position)


    def draw_grid(self):
        for x in range(0, 41, 5):
            pygame.draw.line(screen, LIGHT_GRID, self.conversion(x, 0), self.conversion(x, 30), 1)
        for y in range(0, 31, 5):
            pygame.draw.line(screen, LIGHT_GRID, self.conversion(0, y), self.conversion(40, y), 1)

    @staticmethod
    def conversion(x, y):
        return IsoBoard.compute_conversion(x, y, 1, (IsoBoard.startX, IsoBoard.startY))

    @staticmethod
    def compute_conversion(x, y, scale, offset):
        ex = scale * (x + 4.5 * x) + offset[0]
        ey = scale * (y + 5 * y + 2 * x) + offset[1]
        return (ex, ey)

class IsoProjection:
    def __init__(self, plates, scale=2, offset=(500, 100)):
        self.isoPlates = IsoBoard.compute_iso_plates(plates, scale=scale, offset=offset)
        self.scale = scale
        self.offset = offset

    def draw_projection(self, screen, blit_position=(500, 0)):
        width, height = screen.get_size()
        blended_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Track RGB light sum and count of overlapping plates
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

        # Clamp max channel value per pixel to 255 (white light)
        max_vals = rgb_sum.max(axis=2)
        scale = numpy.ones_like(max_vals)

        # Scale only if a pixel’s RGB intensity would exceed white
        overflow = max_vals > 255
        scale[overflow] = 255.0 / max_vals[overflow]

        # Apply per-pixel scaling to avoid washout, preserve color balance
        for c in range(3):
            rgb_sum[:, :, c] *= scale

        # Final: clip, convert, blit
        numpy.clip(rgb_sum, 0, 255, out=rgb_sum)
        result_array = rgb_sum.astype(numpy.uint8)

        final_surface = pygame.surfarray.make_surface(result_array)
        final_surface.set_alpha(255)
        screen.blit(final_surface, blit_position)

class Level:
    # Define level data
    GRAY   = (100, 100, 100, 160)
    REDD    = (239, 72, 60, 160)
    GREEND  = (25, 115, 23, 160)
    BLUED   = (25, 115, 192, 160)
    level_answer = {
        1: [
            [(0, 0), GREEND, [(7, 7)]],
            [(-3, 0), BLUED, [(10, 10)]]
        ],
        2: [
            [(0, 0), BLUED, [(0, 0), (12, 0), (12, 12), (0, 12)]],
            [(3, 12), REDD, [(3, 3)]],
            [(7, 12), REDD, [(5, 5)]]
        ],
        3: [
            [(0, 0), REDD, [(0, 0), (8, 8), (16, 0), (8, -8)]],
            [(4, -4), REDD, [(5.656854249492381, 5.656854249492381)]],
            [(12, -4), REDD, [(5.656854249492381, 5.656854249492381)]]
        ],
        4: [
            [(0, 0), BLUED, [(4, 4)]],
            [(0, 0), REDD, [(7, 7)]],
            [(0, 0), GREEND, [(10, 10)]]
        ],
        5: [
            [(0, 0), REDD, [(0, 0), (13, 0), (13, 10), (0, 10)]],
            [(4, 2), GREEND, [(0, 0), (5, 3), (0, 6)]],
            [(4, 2), BLUED, [(0, 0), (5, 3), (0, 6)]]
        ],
        6: [
            [(0, 0), BLUED, [(10, 10)]],
            [(-8, 6), BLUED, [(0, 0), (8, 8), (16, 0)]],
            [(0, 0), REDD, [(5.656854249492381, 5.656854249492381)]],
            [(0, 0), GREEND, [(5.656854249492381, 5.656854249492381)]]
        ]
    }

    level_data = {
        1: [ # Moon
            {'type':2, 'color':GRAY, 'location':(20,20), 'xys':[(7,7)]},
            {'type':2, 'color':GRAY, 'location':(15,15), 'xys':[(10,10)]}
        ],
        2: [ # Cloud
            {'type':1, 'color':GRAY, 'location':(5,12),   'xys':[(0,0),(12,0),(12,12),(0,12)]},
            {'type':2, 'color':GRAY, 'location':(20,10), 'xys':[(3,3)]},
            {'type':2, 'color':GRAY, 'location':(25,15), 'xys':[(5,5)]}
        ],
        3: [ # Heart
            {'type':1, 'color':GRAY, 'location':(10,10),'xys':[(0,0),(8,8),(16,0),(8,-8)]},
            {'type':2, 'color':GRAY, 'location':(20,20),'xys':[(4*2**0.5,4*2**0.5)]},
            {'type':2, 'color':GRAY, 'location':(15,15),'xys':[(4*2**0.5,4*2**0.5)]}
        ],
        4: [ # Target
            {'type':2, 'color':GRAY, 'location':(30,20),'xys':[(4,4)]},
            {'type':2, 'color':GRAY, 'location':(10,10),'xys':[(7,7)]},
            {'type':2, 'color':GRAY, 'location':(20,15),'xys':[(10,10)]}
        ],
        5: [ # YouTube
            {'type':1, 'color':GRAY, 'location':(5,5),  'xys':[(0,0),(13,0),(13,10),(0,10)]},
            {'type':1, 'color':GRAY, 'location':(20,15),'xys':[(0,0),(5,3),(0,6)]},
            {'type':1, 'color':GRAY, 'location':(10,20),'xys':[(0,0),(5,3),(0,6)]}
        ],
        6: [ # Map
            {'type':1, 'color':GRAY, 'location':(17,5), 'xys':[(0,0),(8,8),(16,0)]},
            {'type':2, 'color':GRAY, 'location':(20,19),'xys':[(10,10)]},
            {'type':2, 'color':GRAY, 'location':(7,7),  'xys':[(4*2**0.5,4*2**0.5)]},
            {'type':2, 'color':GRAY, 'location':(8,15), 'xys':[(4*2**0.5,4*2**0.5)]}
        ]}

    def __init__(self, level_id):
        self.level_id = level_id
        self.plate_definitions = Level.level_data[level_id]
        self.answer = Level.level_answer[level_id]

    def load(self, board):
        # Clear existing plates
        board.plates.clear()
        # Instantiate Plates per definition
        for spec in self.plate_definitions:
            plate = Plates(
                spec['type'],
                spec.get('color', GRAY),
                tuple(spec['location']),
                spec['xys']
            )
            board.add_plate(plate)      


# Initialize Pygame and constants
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Luminara Demo")
FONT = pygame.font.SysFont("couriernew", 24)

# Semi-transparent Color Palatte
# LIGHT_GRID = (230, 230, 230, 255)
# WHITE  = (255, 255, 255, 255)
# GRAY   = (220, 220, 220, 160)
# REDD    = (239, 72, 60, 160)
# GREEND  = (25, 115, 23, 160)
# BLUED   = (25, 115, 192, 160)

LIGHT_GRID = (230, 230, 230, 255)
# WHITE  = (255, 255, 255, 255)
GRAY   = (100, 100, 100, 160)
REDD    = (239, 72, 60, 160)
GREEND  = (25, 115, 23, 160)
BLUED   = (25, 115, 192, 160)

# get whtie color
def additive_blend(colors):
    r, g, b = 0, 0, 0

    for cr, cg, cb, ca in colors:
        alpha = ca / 255.0
        r += cr * alpha
        g += cg * alpha
        b += cb * alpha

    # Clamp to 255 max
    r = min(int(r), 255)
    g = min(int(g), 255)
    b = min(int(b), 255)
    return (r, g, b, 255)

WHITE  = (additive_blend([REDD, GREEND, BLUED]))

# Color Selection Buttons
color_buttons = [(REDD, pygame.Rect(720, 150, 50, 50)),
                 (GREEND, pygame.Rect(720, 250, 50, 50)),
                 (BLUED, pygame.Rect(720, 350, 50, 50))]
selected_color = None

def draw_color_buttons():
    for color, rect in color_buttons:
        pygame.draw.rect(screen, color, rect)

board = Board()


# Load the desired level
current_level = 6
level = Level(current_level)
level.load(board)

def check_answer(board, current_level):
    answer = Level.level_answer[current_level]
    initial = answer[0][2]
    for plate in board.plates:
        if plate.plate_xys == initial:
            ini = plate.plate_location
    print("Initial:", initial)
    for plate in board.plates:
        curr = False
        for (loc, color, xys) in answer:
            if xys == plate.plate_xys:
                print(loc, (plate.plate_location[0] - ini[0], plate.plate_location[1] - ini[1]))
                if color == plate.plate_color and loc == (plate.plate_location[0] - ini[0], plate.plate_location[1] - ini[1]):
                    curr = True
        if not curr:
            return False
    return True



selected_plate = None

# Start in 2D view
show_isometric = False


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Change to press space bar to toggle view
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                show_isometric = not show_isometric

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # if toggle_button.collidepoint(event.pos):
            #     show_isometric = not show_isometric

            # Check if a color button is clicked
            for color, rect in color_buttons:
                if rect.collidepoint(event.pos):
                    selected_color = color
                    break
            else:
                # If no color is selected, check for a plate
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
                # Snap to nearest grid
                x = round((event.pos[0] - 100) / 15)
                y = round((event.pos[1] - 75) / 15)
                selected_plate.plate_location = (x, y)
                selected_plate.xy_to_coordinates()
                selected_plate.dragging = False
                selected_plate = None

        elif event.type == pygame.MOUSEMOTION and selected_plate and selected_plate.dragging:
            # Update position while dragging
            x = (event.pos[0] - 100) / 15
            y = (event.pos[1] - 75) / 15
            selected_plate.plate_location = (x, y)
            selected_plate.xy_to_coordinates()


    if show_isometric:
        if check_answer(board, current_level):
            print("win")


    
        isoBoard = IsoBoard(board.plates)
        isoProjection = IsoProjection(board.plates, scale=1.8, offset=(10, 80))
        isoBoard.draw_board(screen)      # Draw plates
        isoBoard.draw_grid()             # Draw grid on top
        isoProjection.draw_projection(screen, blit_position=(400, 0))

        # Light visualization
        LIGHT = (255, 255, 100, 80)
        light_source = (80, 300)

        all_corners = []
        for plate in isoBoard.isoPlates:
            points = plate[2]
            if points:
                all_corners.extend(points)

        if all_corners:
            top_point = min(all_corners, key=lambda p: p[1])
            bottom_point = max(all_corners, key=lambda p: p[1])

            # Create a transparent surface for light effect
            light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(light_surface, LIGHT, [light_source, top_point, bottom_point])

            screen.blit(light_surface, (0, 0))

    else:
        screen.fill(WHITE)
        board.draw_grid()           # Draw grid
        board.draw_board(screen)    # Draw plates
        draw_color_buttons()        # Optional color buttons
        
        # Draw text instruction at bottom of screen
        instruction_text = FONT.render("Press SPACE to toggle view", True, (0, 0, 0))
        screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 60))


    pygame.display.flip()


pygame.quit()
sys.exit()