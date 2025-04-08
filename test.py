import pygame
pygame.init()

# Setup
screen = pygame.display.set_mode((500, 400))
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
CYLINDER_COLOR = (100, 150, 255, 180)
ELLIPSE_COLOR = (0, 100, 255, 180)

# Tile center and size
center_x = 250
center_y = 200
tile_width = 64
tile_height = 32
cylinder_height = 80  # How "tall" the object is

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # --- Draw isometric base tile (optional) ---
    top = (center_x, center_y - tile_height // 2)
    right = (center_x + tile_width // 2, center_y)
    bottom = (center_x, center_y + tile_height // 2)
    left = (center_x - tile_width // 2, center_y)
    pygame.draw.polygon(screen, LIGHT_GRAY, [top, right, bottom, left], 1)

    # --- Draw cylinder ---
    ellipse_w = tile_width * 0.8
    ellipse_h = tile_height * 0.4

    # Top ellipse
    top_ellipse_rect = pygame.Rect(0, 0, ellipse_w, ellipse_h)
    top_ellipse_rect.center = (center_x, center_y - cylinder_height)

    # Bottom ellipse
    bottom_ellipse_rect = pygame.Rect(0, 0, ellipse_w, ellipse_h)
    bottom_ellipse_rect.center = (center_x, center_y)

    # Side rectangle (simulate curved cylinder body)
    pygame.draw.polygon(
        screen,
        CYLINDER_COLOR,
        [
            (top_ellipse_rect.left, top_ellipse_rect.centery),
            (top_ellipse_rect.right, top_ellipse_rect.centery),
            (bottom_ellipse_rect.right, bottom_ellipse_rect.centery),
            (bottom_ellipse_rect.left, bottom_ellipse_rect.centery)
        ]
    )

    # Top and bottom ellipses
    pygame.draw.ellipse(screen, ELLIPSE_COLOR, top_ellipse_rect)
    pygame.draw.ellipse(screen, ELLIPSE_COLOR, bottom_ellipse_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
