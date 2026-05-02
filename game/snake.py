import json
import os
import random
import sys
from datetime import datetime

import pygame

pygame.init()

WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
LEADERBOARD_FILE = "leaderboard.json"
MAX_LEADERBOARD_ITEMS = 5

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
GRAY = (80, 80, 80)
ORANGE = (230, 130, 0)
BLUE = (70, 130, 220)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake with Leaderboard and Obstacles")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)


def draw_text(text, color, x, y, small=False):
    selected_font = small_font if small else font
    image = selected_font.render(text, True, color)
    screen.blit(image, (x, y))


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
        json.dump(leaderboard, file, indent=4, ensure_ascii=False)


def add_score_to_leaderboard(score):
    leaderboard = load_leaderboard()
    leaderboard.append({
        "score": score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    leaderboard.sort(key=lambda item: item["score"], reverse=True)
    leaderboard = leaderboard[:MAX_LEADERBOARD_ITEMS]
    save_leaderboard(leaderboard)
    return leaderboard


def random_cell():
    x = random.randrange(0, WIDTH, CELL_SIZE)
    y = random.randrange(0, HEIGHT, CELL_SIZE)
    return [x, y]


def random_free_cell(blocked_cells):
    while True:
        position = random_cell()
        if position not in blocked_cells:
            return position


def create_obstacles(snake, amount=8):
    obstacles = []
    blocked_cells = snake.copy()

    for _ in range(amount):
        obstacle = random_free_cell(blocked_cells)
        obstacles.append(obstacle)
        blocked_cells.append(obstacle)

    return obstacles


def draw_rect_cell(position, color):
    pygame.draw.rect(
        screen,
        color,
        pygame.Rect(position[0], position[1], CELL_SIZE, CELL_SIZE)
    )


def draw_snake(snake):
    for index, segment in enumerate(snake):
        draw_rect_cell(segment, GREEN if index == 0 else DARK_GREEN)


def draw_obstacles(obstacles):
    for obstacle in obstacles:
        draw_rect_cell(obstacle, GRAY)


def draw_leaderboard(x=410, y=35):
    leaderboard = load_leaderboard()
    draw_text("Leaderboard", BLUE, x, y, small=True)

    if not leaderboard:
        draw_text("No records yet", WHITE, x, y + 25, small=True)
        return

    for index, item in enumerate(leaderboard, start=1):
        text = f"{index}. {item['score']} pts"
        draw_text(text, WHITE, x, y + 20 + index * 22, small=True)


def game_over_screen(score):
    leaderboard = add_score_to_leaderboard(score)

    while True:
        screen.fill(BLACK)
        draw_text("Game Over!", WHITE, WIDTH // 2 - 70, 60)
        draw_text(f"Your score: {score}", WHITE, WIDTH // 2 - 80, 100)
        draw_text("Top scores:", BLUE, WIDTH // 2 - 65, 145)

        for index, item in enumerate(leaderboard, start=1):
            draw_text(
                f"{index}. {item['score']} pts | {item['date']}",
                WHITE,
                WIDTH // 2 - 150,
                150 + index * 28,
                small=True
            )

        draw_text("R - restart", WHITE, WIDTH // 2 - 70, 320)
        draw_text("Q - quit", WHITE, WIDTH // 2 - 55, 350)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


def main():
    snake = [[100, 100], [80, 100], [60, 100]]
    direction = "RIGHT"
    next_direction = direction
    score = 0
    speed = 10

    obstacles = create_obstacles(snake, amount=8)
    food = random_free_cell(snake + obstacles)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != "DOWN":
                    next_direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    next_direction = "DOWN"
                elif event.key == pygame.K_LEFT and direction != "RIGHT":
                    next_direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    next_direction = "RIGHT"

        direction = next_direction

        head_x, head_y = snake[0]
        if direction == "UP":
            head_y -= CELL_SIZE
        elif direction == "DOWN":
            head_y += CELL_SIZE
        elif direction == "LEFT":
            head_x -= CELL_SIZE
        elif direction == "RIGHT":
            head_x += CELL_SIZE

        new_head = [head_x, head_y]

        hit_wall = head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT
        hit_self = new_head in snake
        hit_obstacle = new_head in obstacles

        if hit_wall or hit_self or hit_obstacle:
            game_over_screen(score)

        snake.insert(0, new_head)

        if new_head == food:
            score += 1
            food = random_free_cell(snake + obstacles)

            if score % 5 == 0:
                speed += 1
                obstacles.append(random_free_cell(snake + obstacles + [food]))
        else:
            snake.pop()

        screen.fill(BLACK)
        draw_rect_cell(food, RED)
        draw_obstacles(obstacles)
        draw_snake(snake)
        draw_text(f"Score: {score}", WHITE, 10, 10)
        draw_text(f"Obstacles: {len(obstacles)}", ORANGE, 10, 35, small=True)
        draw_leaderboard()

        pygame.display.update()
        clock.tick(speed)


if __name__ == "__main__":
    main()
