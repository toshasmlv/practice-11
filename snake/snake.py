import pygame
import sys
import random

pygame.init()

# ── размеры и настройки ───────────────────────
CELL   = 20          # размер одной клетки в пикселях
COLS   = 30          # количество столбцов
ROWS   = 30          # количество строк
WIDTH  = CELL * COLS
HEIGHT = CELL * ROWS
INFO_H = 40          # высота панели счёта сверху

# ── цвета ─────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GREEN      = (0,   200, 0)
DARK_GREEN = (0,   140, 0)
GRAY       = (40,  40,  40)
WALL_COLOR = (80,  80,  80)

# ── типы еды: цвет, очки, время жизни (мс) ───
FOOD_TYPES = {
    "normal": {"color": (220, 0,   0),   "points": 10, "time": 8000},  # красная, 8 сек
    "gold":   {"color": (255, 215, 0),   "points": 30, "time": 5000},  # золотая, 5 сек
    "purple": {"color": (180, 0,   180), "points": 50, "time": 3000},  # фиолетовая, 3 сек
}

# ── направления ───────────────────────────────
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

# ── настройки уровней ─────────────────────────
FOOD_PER_LEVEL = 3   # сколько еды нужно съесть для нового уровня
BASE_SPEED     = 8   # начальная скорость (кадров в секунду)
SPEED_STEP     = 2   # увеличение скорости за уровень

# ── окно ──────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT + INFO_H))
pygame.display.set_caption("Snake — Practice 11")
clock  = pygame.time.Clock()

font       = pygame.font.SysFont("Verdana", 18)
font_big   = pygame.font.SysFont("Verdana", 36)
font_small = pygame.font.SysFont("Verdana", 22)


def cell_rect(col, row):
    """Возвращает pygame.Rect для клетки (col, row) с учётом панели сверху."""
    return pygame.Rect(col * CELL, INFO_H + row * CELL, CELL, CELL)


def build_walls():
    """Создаёт множество координат стен по периметру поля."""
    walls = set()
    for c in range(COLS):
        walls.add((c, 0))
        walls.add((c, ROWS - 1))
    for r in range(ROWS):
        walls.add((0, r))
        walls.add((COLS - 1, r))
    return walls


def spawn_food(walls, snake):
    """
    Выбирает случайную свободную клетку для еды.
    Тип еды выбирается случайно с весами:
      normal — 70%, gold — 20%, purple — 10%.
    Возвращает: (позиция, тип, время спавна).
    """
    occupied = walls | set(snake)
    free = [
        (c, r)
        for c in range(1, COLS - 1)
        for r in range(1, ROWS - 1)
        if (c, r) not in occupied
    ]
    if not free:
        return None, "normal", 0

    # случайный тип с весами
    food_type = random.choices(
        ["normal", "gold", "purple"],
        weights=[70, 20, 10]
    )[0]

    pos        = random.choice(free)
    spawn_time = pygame.time.get_ticks()  # запоминаем время появления
    return pos, food_type, spawn_time


def draw_field(walls, snake, food, food_type):
    """Рисует стены, змейку и еду на экране."""
    screen.fill(GRAY)

    # стены
    for (c, r) in walls:
        pygame.draw.rect(screen, WALL_COLOR, cell_rect(c, r))

    # еда — кружок цвета соответствующего типа
    if food:
        color = FOOD_TYPES[food_type]["color"]
        pygame.draw.ellipse(screen, color, cell_rect(*food))

    # змейка — голова темнее тела
    for i, (c, r) in enumerate(snake):
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(screen, color, cell_rect(c, r))
        pygame.draw.rect(screen, BLACK, cell_rect(c, r), 1)


def draw_info(score, level, food_type, food_spawn_time):
    """Рисует панель с очками, уровнем и таймером еды."""
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, INFO_H))

    # очки слева
    score_surf = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surf, (10, 10))

    # уровень справа
    level_surf = font.render(f"Level: {level}", True, (255, 215, 0))
    screen.blit(level_surf, (WIDTH - level_surf.get_width() - 10, 10))

    # таймер еды по центру — показывает сколько секунд осталось
    elapsed   = pygame.time.get_ticks() - food_spawn_time
    time_left = max(0, (FOOD_TYPES[food_type]["time"] - elapsed) // 1000)
    color     = FOOD_TYPES[food_type]["color"]
    timer_surf = font.render(f"Food: {time_left}s", True, color)
    screen.blit(timer_surf, (WIDTH // 2 - timer_surf.get_width() // 2, 10))


def show_game_over(score):
    """
    Показывает экран окончания игры.
    Возвращает True если игрок хочет играть снова, иначе выходит.
    """
    screen.fill(BLACK)
    over  = font_big.render("GAME OVER", True, (220, 0, 0))
    sc    = font_small.render(f"Score: {score}", True, WHITE)
    again = font.render("R — restart    Q — quit", True, GRAY)
    screen.blit(over,  over.get_rect(center=(WIDTH // 2, 200)))
    screen.blit(sc,    sc.get_rect(center=(WIDTH // 2, 270)))
    screen.blit(again, again.get_rect(center=(WIDTH // 2, 330)))
    pygame.display.update()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return True   # рестарт
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()


def reset_game(walls):
    """Сбрасывает все переменные игры в начальное состояние."""
    snake     = [(5, 5), (4, 5), (3, 5)]  # начальная позиция змейки
    direction = RIGHT
    food, food_type, food_time = spawn_food(walls, snake)
    score  = 0
    level  = 1
    eaten  = 0
    speed  = BASE_SPEED
    return snake, direction, food, food_type, food_time, score, level, eaten, speed


# ── главный цикл ──────────────────────────────
walls = build_walls()
snake, direction, food, food_type, food_time, score, level, eaten, speed = reset_game(walls)
next_dir = direction  # буфер направления (чтобы не разворачиваться назад)

while True:

    # обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # смена направления — нельзя идти прямо назад
            if event.key == pygame.K_UP    and direction != DOWN:  next_dir = UP
            if event.key == pygame.K_DOWN  and direction != UP:    next_dir = DOWN
            if event.key == pygame.K_LEFT  and direction != RIGHT: next_dir = LEFT
            if event.key == pygame.K_RIGHT and direction != LEFT:  next_dir = RIGHT

    direction = next_dir

    # ── проверяем таймер еды ──────────────────
    # если еда не съедена вовремя — спавним новую
    elapsed = pygame.time.get_ticks() - food_time
    if food and elapsed > FOOD_TYPES[food_type]["time"]:
        food, food_type, food_time = spawn_food(walls, snake)

    # ── движение змейки ───────────────────────
    head     = snake[0]
    new_head = (head[0] + direction[0], head[1] + direction[1])

    # столкновение со стеной
    if new_head in walls:
        if show_game_over(score):
            snake, direction, food, food_type, food_time, score, level, eaten, speed = reset_game(walls)
            next_dir = direction
        continue

    # столкновение с собой
    if new_head in snake:
        if show_game_over(score):
            snake, direction, food, food_type, food_time, score, level, eaten, speed = reset_game(walls)
            next_dir = direction
        continue

    # добавляем новую голову
    snake.insert(0, new_head)

    # ── поедание еды ─────────────────────────
    if new_head == food:
        pts    = FOOD_TYPES[food_type]["points"]  # очки зависят от типа еды
        score += pts
        eaten += 1

        # проверяем переход на новый уровень
        if eaten >= FOOD_PER_LEVEL:
            level += 1
            eaten  = 0
            speed += SPEED_STEP  # увеличиваем скорость

        # спавним новую еду
        food, food_type, food_time = spawn_food(walls, snake)
    else:
        snake.pop()  # убираем хвост если еда не съедена

    # ── отрисовка ────────────────────────────
    draw_field(walls, snake, food, food_type)
    draw_info(score, level, food_type, food_time)
    pygame.display.update()
    clock.tick(speed)