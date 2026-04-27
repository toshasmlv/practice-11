import pygame
import sys
import math

pygame.init()

# ── размеры окна ──────────────────────────────
WIDTH  = 800
HEIGHT = 600
PANEL_H = 60  # высота панели инструментов снизу

# ── цвета палитры ─────────────────────────────
PALETTE = [
    (0,   0,   0),    # чёрный
    (255, 255, 255),  # белый
    (255, 0,   0),    # красный
    (0,   200, 0),    # зелёный
    (0,   0,   255),  # синий
    (255, 255, 0),    # жёлтый
    (255, 165, 0),    # оранжевый
    (128, 0,   128),  # фиолетовый
    (0,   255, 255),  # голубой
    (255, 105, 180),  # розовый
    (139, 69,  19),   # коричневый
    (128, 128, 128),  # серый
]

# ── названия инструментов ─────────────────────
TOOL_PENCIL = "pencil"    # карандаш (из практики 10)
TOOL_RECT   = "rect"      # прямоугольник (из практики 10)
TOOL_CIRCLE = "circle"    # круг (из практики 10)
TOOL_ERASER = "eraser"    # ластик (из практики 10)
# новые инструменты практики 11:
TOOL_SQUARE = "square"    # квадрат
TOOL_RTRI   = "r.tri"     # прямоугольный треугольник
TOOL_ETRI   = "e.tri"     # равносторонний треугольник
TOOL_RHOMBUS = "rhombus"  # ромб

# ── настройка окна ────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT + PANEL_H))
pygame.display.set_caption("Paint — Practice 11")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Verdana", 12)

# холст — отдельная поверхность для рисования
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))  # белый фон

# ── начальные значения ────────────────────────
current_color = (0, 0, 0)    # текущий цвет — чёрный
current_tool  = TOOL_PENCIL  # текущий инструмент — карандаш
brush_size    = 5             # размер кисти
drawing       = False         # зажата ли кнопка мыши
start_pos     = None          # начальная точка фигуры


def draw_shape(surface, tool, color, p1, p2, size):
    """
    Рисует фигуру на surface от точки p1 до p2.
    Работает как для холста (финальный результат),
    так и для экрана (превью во время рисования).
    """
    x1, y1 = p1
    x2, y2 = p2

    if tool == TOOL_RECT:
        # прямоугольник: верхний левый угол + ширина/высота
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        pygame.draw.rect(surface, color, (x, y, w, h), size)

    elif tool == TOOL_SQUARE:
        # квадрат: берём меньшую из сторон чтобы получился квадрат
        side = min(abs(x2 - x1), abs(y2 - y1))
        # направление по x и y (куда тянем мышь)
        sx = x1 + (1 if x2 >= x1 else -1) * side
        sy = y1 + (1 if y2 >= y1 else -1) * side
        x  = min(x1, sx)
        y  = min(y1, sy)
        pygame.draw.rect(surface, color, (x, y, side, side), size)

    elif tool == TOOL_CIRCLE:
        # круг/эллипс: центр между p1 и p2
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        rx = abs(x2 - x1) // 2
        ry = abs(y2 - y1) // 2
        if rx > 0 and ry > 0:
            pygame.draw.ellipse(surface, color, (cx - rx, cy - ry, rx * 2, ry * 2), size)

    elif tool == TOOL_RTRI:
        # прямоугольный треугольник:
        # прямой угол в левом нижнем углу
        # вершины: левый нижний, левый верхний, правый нижний
        pts = [(x1, y2), (x1, y1), (x2, y2)]
        pygame.draw.polygon(surface, color, pts, size)

    elif tool == TOOL_ETRI:
        # равносторонний треугольник:
        # основание внизу, вершина вычисляется по формуле высоты
        base   = abs(x2 - x1)
        h_eq   = base * math.sqrt(3) / 2  # высота равностороннего треугольника
        # вершина треугольника — над центром основания
        direction = 1 if y2 >= y1 else -1
        tip_y  = int(y2 - direction * h_eq)
        mid_x  = (x1 + x2) // 2
        pts    = [(x1, y2), (x2, y2), (mid_x, tip_y)]
        pygame.draw.polygon(surface, color, pts, size)

    elif tool == TOOL_RHOMBUS:
        # ромб: 4 точки — верх, право, низ, лево
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        pts = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        pygame.draw.polygon(surface, color, pts, size)


def draw_toolbar():
    """Рисует панель инструментов внизу экрана."""
    pygame.draw.rect(screen, (220, 220, 220), (0, HEIGHT, WIDTH, PANEL_H))
    pygame.draw.line(screen, (150, 150, 150), (0, HEIGHT), (WIDTH, HEIGHT), 2)

    # ── палитра цветов ────────────────────────
    for i, color in enumerate(PALETTE):
        x    = 10 + i * 36
        y    = HEIGHT + 10
        rect = pygame.Rect(x, y, 30, 30)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)
        # выделяем выбранный цвет жирной рамкой
        if color == current_color:
            pygame.draw.rect(screen, (0, 0, 0), rect, 3)

    # ── кнопки инструментов ───────────────────
    tools = [
        TOOL_PENCIL, TOOL_RECT,   TOOL_CIRCLE, TOOL_ERASER,
        TOOL_SQUARE, TOOL_RTRI,   TOOL_ETRI,   TOOL_RHOMBUS,
    ]
    for i, tool in enumerate(tools):
        x    = 460 + i * 43
        y    = HEIGHT + 15
        rect = pygame.Rect(x, y, 40, 25)
        # выбранный инструмент подсвечен синим
        col  = (160, 160, 255) if tool == current_tool else (200, 200, 200)
        pygame.draw.rect(screen, col, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)
        lbl = font.render(tool, True, (0, 0, 0))
        screen.blit(lbl, (x + 2, y + 6))

    # размер кисти справа
    size_lbl = font.render(f"size:{brush_size}", True, (0, 0, 0))
    screen.blit(size_lbl, (WIDTH - 70, HEIGHT + 22))


def toolbar_click(mx, my):
    """Обрабатывает клик по панели инструментов."""
    global current_color, current_tool

    # клик по палитре
    for i, color in enumerate(PALETTE):
        x = 10 + i * 36
        y = HEIGHT + 10
        if x <= mx <= x + 30 and y <= my <= y + 30:
            current_color = color
            return

    # клик по инструментам
    tools = [
        TOOL_PENCIL, TOOL_RECT,   TOOL_CIRCLE, TOOL_ERASER,
        TOOL_SQUARE, TOOL_RTRI,   TOOL_ETRI,   TOOL_RHOMBUS,
    ]
    for i, tool in enumerate(tools):
        x = 460 + i * 43
        y = HEIGHT + 15
        if x <= mx <= x + 40 and y <= my <= y + 25:
            current_tool = tool
            return


# ── главный цикл ──────────────────────────────
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # скролл колёсиком — меняем размер кисти
        if event.type == pygame.MOUSEWHEEL:
            brush_size = max(1, min(50, brush_size + event.y))

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos

                if my > HEIGHT:
                    # клик по панели — выбор цвета/инструмента
                    toolbar_click(mx, my)
                else:
                    # начинаем рисовать на холсте
                    drawing   = True
                    start_pos = (mx, my)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                mx, my  = event.pos
                my      = min(my, HEIGHT - 1)  # не выходим за холст
                end_pos = (mx, my)

                # фигуры рисуются при отпускании кнопки мыши
                shape_tools = [
                    TOOL_RECT, TOOL_CIRCLE, TOOL_SQUARE,
                    TOOL_RTRI, TOOL_ETRI,   TOOL_RHOMBUS,
                ]
                if current_tool in shape_tools and start_pos:
                    draw_shape(canvas, current_tool, current_color,
                               start_pos, end_pos, brush_size)

                drawing   = False
                start_pos = None

        if event.type == pygame.KEYDOWN:
            # C — очистить холст
            if event.key == pygame.K_c:
                canvas.fill((255, 255, 255))

    # ── карандаш и ластик работают пока зажата кнопка ──
    if drawing and current_tool in (TOOL_PENCIL, TOOL_ERASER):
        mx, my = pygame.mouse.get_pos()
        if my < HEIGHT:
            color = (255, 255, 255) if current_tool == TOOL_ERASER else current_color
            pygame.draw.circle(canvas, color, (mx, my), brush_size)

    # ── отрисовка ────────────────────────────
    # сначала холст
    screen.blit(canvas, (0, 0))

    # превью фигуры во время рисования (на экране, не на холсте)
    if drawing and start_pos:
        mx, my = pygame.mouse.get_pos()
        my = min(my, HEIGHT - 1)
        shape_tools = [
            TOOL_RECT, TOOL_CIRCLE, TOOL_SQUARE,
            TOOL_RTRI, TOOL_ETRI,   TOOL_RHOMBUS,
        ]
        if current_tool in shape_tools:
            # тонкая линия превью — 1px
            draw_shape(screen, current_tool, current_color,
                       start_pos, (mx, my), 1)

    # панель инструментов поверх всего
    draw_toolbar()
    pygame.display.update()
    clock.tick(60)