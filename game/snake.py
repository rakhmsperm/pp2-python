import pygame
import random
import sys



pygame.init()



WIDTH = 600
HEIGHT = 400


CELL_SIZE = 20


BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)



screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка на Python")



clock = pygame.time.Clock()



font = pygame.font.SysFont("Arial", 28)


def draw_text(text, color, x, y):
    """
    Рисует текст на экране.
    """
    image = font.render(text, True, color)
    screen.blit(image, (x, y))


def random_food_position():
    """
    Возвращает случайную позицию еды.
    Позиция всегда кратна CELL_SIZE, чтобы еда была ровно в клетке.
    """
    x = random.randrange(0, WIDTH, CELL_SIZE)
    y = random.randrange(0, HEIGHT, CELL_SIZE)
    return [x, y]


def draw_snake(snake):
    """
    Рисует змейку.
    snake — это список клеток.
    Каждая клетка выглядит как [x, y].
    """
    for index, segment in enumerate(snake):
        color = GREEN if index == 0 else DARK_GREEN
        pygame.draw.rect(
            screen,
            color,
            pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE)
        )


def draw_food(food):
    """
    Рисует еду.
    """
    pygame.draw.rect(
        screen,
        RED,
        pygame.Rect(food[0], food[1], CELL_SIZE, CELL_SIZE)
    )


def game_over_screen(score):
    """
    Экран после проигрыша.
    """
    screen.fill(BLACK)

    draw_text("Игра окончена!", WHITE, WIDTH // 2 - 110, HEIGHT // 2 - 70)
    draw_text(f"Счет: {score}", WHITE, WIDTH // 2 - 50, HEIGHT // 2 - 30)
    draw_text("R - начать заново", WHITE, WIDTH // 2 - 120, HEIGHT // 2 + 20)
    draw_text("Q - выйти", WHITE, WIDTH // 2 - 70, HEIGHT // 2 + 60)

    pygame.display.update()

    while True:
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
    """
    Главная функция игры.
    Здесь происходит основной игровой цикл.
    """

    # Начальная позиция змейки
    snake = [
        [100, 100],
        [80, 100],
        [60, 100]
    ]

    # Начальное направление движения
    direction = "RIGHT"
    next_direction = direction

    # Позиция еды
    food = random_food_position()

    
    score = 0

    
    speed = 10

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


        head_x = snake[0][0]
        head_y = snake[0][1]

        
        if direction == "UP":
            head_y -= CELL_SIZE
        elif direction == "DOWN":
            head_y += CELL_SIZE
        elif direction == "LEFT":
            head_x -= CELL_SIZE
        elif direction == "RIGHT":
            head_x += CELL_SIZE

        new_head = [head_x, head_y]

        
        if (
            head_x < 0 or
            head_x >= WIDTH or
            head_y < 0 or
            head_y >= HEIGHT
        ):
            game_over_screen(score)

        
        if new_head in snake:
            game_over_screen(score)

        
        snake.insert(0, new_head)

        
        if new_head == food:
            score += 1
            food = random_food_position()

            
            if score % 5 == 0:
                speed += 1
        else:
            
            snake.pop()

        
        screen.fill(BLACK)

        draw_food(food)
        draw_snake(snake)

        draw_text(f"Счет: {score}", WHITE, 10, 10)

        
        pygame.display.update()

        
        clock.tick(speed)



main()