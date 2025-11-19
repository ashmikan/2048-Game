import pygame
import random
import math

pygame.init()

FPS = 60

WIDTH, HEIGHT = 800, 600
ROWS = 4
COLS = 4

RECT_WIDTH = WIDTH // COLS
RECT_HEIGHT = HEIGHT // ROWS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
TEXT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 20

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Game")

def main(window):
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

    pygame.quit()

if __name__ == "__main__":
    main(WINDOW)