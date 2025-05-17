import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)
COLORS = [
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (255, 165, 0),  # Orange
    (0, 0, 255),    # Blue
    (0, 255, 0),    # Green
    (255, 0, 0),    # Red
    (128, 0, 128)   # Purple
]

# Shapes and their rotations
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

# Grid dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Play area dimensions
PLAY_AREA_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_AREA_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# Sidebar dimensions
SIDEBAR_WIDTH = SCREEN_WIDTH - PLAY_AREA_WIDTH
SIDEBAR_X = PLAY_AREA_WIDTH

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load a custom font
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)


def create_grid(locked_positions={}):
    """Create a grid with locked positions."""
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid


def draw_grid(surface, grid):
    """Draw the grid on the screen."""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    for y in range(GRID_HEIGHT):
        pygame.draw.line(surface, LIGHT_GRAY, (0, y * BLOCK_SIZE), (PLAY_AREA_WIDTH, y * BLOCK_SIZE), 1)
    for x in range(GRID_WIDTH):
        pygame.draw.line(surface, LIGHT_GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, PLAY_AREA_HEIGHT), 1)


def draw_sidebar(surface, next_piece, score, level):
    """Draw the sidebar with next piece preview, score, and level."""
    pygame.draw.rect(surface, GRAY, (SIDEBAR_X, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))

    # Draw "Next Piece"
    next_piece_text = font.render("Next Piece:", True, WHITE)
    surface.blit(next_piece_text, (SIDEBAR_X + 10, 20))

    # Draw the next piece preview
    preview_x = SIDEBAR_X + SIDEBAR_WIDTH // 2 - len(next_piece[0]) * BLOCK_SIZE // 4
    preview_y = 80
    for y, row in enumerate(next_piece):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, COLORS[random.randint(0, len(COLORS) - 1)],
                                 (preview_x + x * BLOCK_SIZE // 2, preview_y + y * BLOCK_SIZE // 2,
                                  BLOCK_SIZE // 2, BLOCK_SIZE // 2), 0)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(score_text, (SIDEBAR_X + 10, 200))

    # Draw level
    level_text = font.render(f"Level: {level}", True, WHITE)
    surface.blit(level_text, (SIDEBAR_X + 10, 250))


def draw_window(surface, grid, next_piece, score, level):
    """Draw the entire game window."""
    surface.fill(BLACK)
    draw_grid(surface, grid)
    draw_sidebar(surface, next_piece, score, level)
    pygame.display.update()


def draw_game_over(surface):
    """Draw the game over screen."""
    game_over_text = game_over_font.render("GAME OVER", True, WHITE)
    restart_text = font.render("Press SPACE to Restart", True, WHITE)
    surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    pygame.display.update()


def valid_space(shape, grid, offset):
    """Check if the current shape position is valid."""
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = x + off_x
                new_y = y + off_y
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or (new_x, new_y) in grid:
                    return False
    return True


def clear_rows(grid, locked_positions):
    """Clear completed rows and shift everything above down."""
    cleared = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if all((x, y) in locked_positions for x in range(GRID_WIDTH)):
            cleared += 1
            del_keys = [(x, y) for x in range(GRID_WIDTH)]
            for key in del_keys:
                del locked_positions[key]
            for ky in range(y, 0, -1):
                for kx in range(GRID_WIDTH):
                    if (kx, ky - 1) in locked_positions:
                        locked_positions[(kx, ky)] = locked_positions.pop((kx, ky - 1))
    return cleared


def main():
    """Main game loop."""
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = random.choice(SHAPES)
    current_color = random.choice(COLORS)
    next_piece = random.choice(SHAPES)
    next_color = random.choice(COLORS)
    piece_x, piece_y = GRID_WIDTH // 2 - len(current_piece[0]) // 2, 0
    fall_time = 0
    fall_speed = 0.3
    score = 0
    level = 1

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Automatic falling
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            piece_y += 1
            if not valid_space(current_piece, grid, (piece_x, piece_y)) and piece_y > 0:
                piece_y -= 1
                change_piece = True

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    piece_x -= 1
                    if not valid_space(current_piece, grid, (piece_x, piece_y)):
                        piece_x += 1
                if event.key == pygame.K_RIGHT:
                    piece_x += 1
                    if not valid_space(current_piece, grid, (piece_x, piece_y)):
                        piece_x -= 1
                if event.key == pygame.K_DOWN:
                    piece_y += 1
                    if not valid_space(current_piece, grid, (piece_x, piece_y)):
                        piece_y -= 1
                if event.key == pygame.K_UP:
                    rotated_piece = list(zip(*current_piece[::-1]))
                    if valid_space(rotated_piece, grid, (piece_x, piece_y)):
                        current_piece = rotated_piece

        # Add current piece to the grid
        shape_pos = []
        for y, row in enumerate(current_piece):
            for x, cell in enumerate(row):
                if cell:
                    shape_pos.append((piece_x + x, piece_y + y))

        for x, y in shape_pos:
            if y >= 0:
                grid[y][x] = current_color

        # Change piece if it lands
        if change_piece:
            for pos in shape_pos:
                locked_positions[pos] = current_color
            current_piece = next_piece
            current_color = next_color
            next_piece = random.choice(SHAPES)
            next_color = random.choice(COLORS)
            piece_x, piece_y = GRID_WIDTH // 2 - len(current_piece[0]) // 2, 0
            change_piece = False
            cleared_rows = clear_rows(grid, locked_positions)
            score += cleared_rows * 10
            if cleared_rows > 0:
                level = max(1, score // 100 + 1)
                fall_speed = 0.3 - (level - 1) * 0.02

        draw_window(screen, grid, next_piece, score, level)

        # Check for game over
        if any((x, 0) in locked_positions for x in range(GRID_WIDTH)):
            draw_game_over(screen)
            waiting_for_restart = True
            while waiting_for_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        waiting_for_restart = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            locked_positions.clear()
                            score = 0
                            level = 1
                            fall_speed = 0.3
                            piece_x, piece_y = GRID_WIDTH // 2 - len(current_piece[0]) // 2, 0
                            waiting_for_restart = False

    pygame.quit()


if __name__ == "__main__":
    main()