import pygame
import random
import math

pygame.init()

FPS = 60

WIDTH, HEIGHT = 800, 800
ROWS = 4
COLS = 4

RECT_WIDTH = WIDTH // COLS
RECT_HEIGHT = HEIGHT // ROWS

OUTLINE_COLOR = (200, 173, 200)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (225, 192, 225)
TEXT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 40, bold=True)
MOVE_VEL = 25
SCORE_COLOR = (119, 110, 101)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Game")

class Tile:
    COLORS = [
        (238, 228, 238),
        (237, 224, 220),
        (242, 177, 121),
        (245, 149, 199),
        (246, 124, 195),
        (246, 94, 159),
        (237, 207, 114),
        (237, 204, 197),
        (237, 200, 180),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT
        self.spawn_frame = 0  # Animation counter for spawn effect

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color_index = max(0, min(color_index, len(self.COLORS) - 1))
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        
        # Spawn animation: scale up from 0 to full size over 10 frames
        scale = min(1.0, self.spawn_frame / 10.0)
        
        # Calculate center for scaling effect
        center_x = self.x + RECT_WIDTH / 2
        center_y = self.y + RECT_HEIGHT / 2
        
        # Draw scaled tile
        scaled_width = RECT_WIDTH * scale
        scaled_height = RECT_HEIGHT * scale
        scaled_x = center_x - scaled_width / 2
        scaled_y = center_y - scaled_height / 2
        
        pygame.draw.rect(window, color, (scaled_x, scaled_y, scaled_width, scaled_height))
        pygame.draw.rect(window, OUTLINE_COLOR, (scaled_x, scaled_y, scaled_width, scaled_height), 2)
        
        # Draw text centered
        text = FONT.render(str(self.value), 1, TEXT_COLOR)
        window.blit(
            text,
            (
                center_x - text.get_width() / 2,
                center_y - text.get_height() / 2,
            ),
        )
        
        # Increment spawn frame for animation
        if self.spawn_frame < 10:
            self.spawn_frame += 1

    def set_pos(self, ceil = False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)

def draw(window, tiles, score=0):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)
    
    # Draw score at top-left corner
    score_text = SMALL_FONT.render(f"Score: {score}", 1, SCORE_COLOR)
    window.blit(score_text, (20, 20))

    pygame.display.update()

def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row} {col}" not in tiles:
            break

    return row, col


def move_tiles(window, tiles, clock, direction, score=0):
    updated = True
    blocks = set()

    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row} {tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        )
        ceil = True

    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row} {tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        )
        ceil = False

    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1} {tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        )
        ceil = True

    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1} {tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        )
        ceil = False


    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (
                tile.value == next_tile.value 
                and tile not in blocks 
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    score += next_tile.value  # Add merged value to score
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles, score)

    return end_move(tiles, score)

def end_move(tiles, score=0):
    if len(tiles) == 16:
        return "lost", score

    row, col = get_random_pos(tiles)
    new_tile = Tile(random.choice([2, 4]), row, col)
    new_tile.spawn_frame = 0  # Reset spawn animation for new tile
    tiles[f"{row} {col}"] = new_tile
    return "continue", score


def update_tiles(window, tiles, sorted_tiles, score=0):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row} {tile.col}"] = tile

    draw(window, tiles, score)

def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row} {col}"] = Tile(2, row, col)

    return tiles

def main(window):
    clock = pygame.time.Clock()
    run = True
    score = 0

    tiles = generate_tiles() 

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    status, score = move_tiles(window, tiles, clock, "left", score)
                elif event.key == pygame.K_RIGHT:
                    status, score = move_tiles(window, tiles, clock, "right", score)
                elif event.key == pygame.K_UP:
                    status, score = move_tiles(window, tiles, clock, "up", score)
                elif event.key == pygame.K_DOWN:
                    status, score = move_tiles(window, tiles, clock, "down", score)
                
                if status == "lost":
                    print(f"Game Over! Final Score: {score}")
                    run = False
                    break

        draw(window, tiles, score)

    pygame.quit()

if __name__ == "__main__":
    main(WINDOW)