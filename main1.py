import pygame
import sys

# Инициализация Pygame
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Патрулирующий враг")
clock = pygame.time.Clock()

# Цвета
BACKGROUND_COLOR = (30, 30, 30)
ENEMY_COLOR = (255, 0, 0)
POINT_COLOR = (0, 255, 0)

# Точки патрулирования
patrol_points = [(100, 300),(500,200) ,(700, 300)]
enemy_pos = list(patrol_points[0])
enemy_speed = 2
current_target = 1
moving_forward = True

# Функция движения к цели
def move_towards(target, current, speed):
    dx = target[0] - current[0]
    dy = target[1] - current[1]
    distance = (dx**2 + dy**2) ** 0.5

    if distance < speed:
        return list(target)  # Цель достигнута

    # Вычисляем нормализованное направление и перемещаем
    return [
        current[0] + dx / distance * speed,
        current[1] + dy / distance * speed
    ]

# Главный игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновляем позицию врага
    enemy_pos = move_towards(patrol_points[current_target], enemy_pos, enemy_speed)

    # Проверка достижения цели
    if tuple(map(int, enemy_pos)) == patrol_points[current_target]:
        if moving_forward:
            current_target += 1
            if current_target >= len(patrol_points):
                current_target = len(patrol_points) - 2  # Возвращаемся
                moving_forward = False
        else:
            current_target -= 1
            if current_target < 0:
                current_target = 1  # Переходим на следующий путь
                moving_forward = True

    # Отрисовка
    screen.fill(BACKGROUND_COLOR)

    # Враг
    pygame.draw.circle(screen, ENEMY_COLOR, (int(enemy_pos[0]), int(enemy_pos[1])), 20)

    # Точки патрулирования
    for point in patrol_points:
        pygame.draw.circle(screen, POINT_COLOR, point, 6)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
