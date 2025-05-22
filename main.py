# main.py
import pygame
import sys
from inventory import Inventory
from ui import draw_ui, wrap_text

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки окна
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Инвентарь с поиском (Бойер-Мур)")

# Загрузка звуков
try:
    click_sound = pygame.mixer.Sound("click.wav")
    button_sound = pygame.mixer.Sound("button.wav")
    search_sound = pygame.mixer.Sound("search.wav")
except FileNotFoundError:
    print("Звуковые файлы не найдены. Создайте файлы click.wav, button.wav и search.wav или отключите звуки.")
    click_sound = button_sound = search_sound = None

# Поле ввода
input_box = pygame.Rect(50, 50, 800, 40)
input_text = ""
active = False

# Кнопка "Очистить"
clear_button = pygame.Rect(860, 50, 100, 40)

# Инвентарь и результаты
inventory = Inventory()
results = []

# Переменные для прокрутки
items_scroll_y = 0
results_scroll_y = 0
category_scroll_x = 0
BASE_ITEM_HEIGHT = 20
MAX_VISIBLE_ITEMS = 12
LIST_WIDTH = 360

# Переменные для выделения
hovered_item_index = None
hovered_result_index = None
selected_item_index = None
selected_result_index = None

# Переменные для автодополнения
autocomplete_suggestion = None

# Переменные для зажатия Backspace
backspace_held = False
backspace_timer = 0
BACKSPACE_INITIAL_DELAY = 500
BACKSPACE_REPEAT_DELAY = 250

# Переменные для зажатия букв
key_held = False
key_timer = 0
last_key = None
KEY_INITIAL_DELAY = 500
KEY_REPEAT_DELAY = 150

# Шрифт для расчёта высоты
SMALL_FONT = pygame.font.Font(None, 28)

# Основной цикл
clock = pygame.time.Clock()
running = True

while running:
    delta_time = clock.tick(60)

    # Получаем позицию курсора для выделения
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Сбрасываем индексы наведения
    hovered_item_index = None
    hovered_result_index = None

    # Вычисляем высоту каждого элемента в списке "Все предметы"
    items = inventory.get_items()
    item_heights = []
    item_positions = []
    current_y = 200
    for item in items:
        lines = wrap_text(item, SMALL_FONT, LIST_WIDTH - 10)
        num_lines = len(lines)  # Учитываем все строки
        item_height = BASE_ITEM_HEIGHT * num_lines
        item_heights.append(item_height)
        item_positions.append(current_y)
        current_y += item_height

    # Вычисляем высоту каждого результата в списке "Результаты поиска"
    result_heights = []
    result_positions = []
    current_y = 200
    for result in results:
        lines = wrap_text(result, SMALL_FONT, LIST_WIDTH - 10)
        num_lines = len(lines)  # Учитываем все строки
        result_height = BASE_ITEM_HEIGHT * num_lines
        result_heights.append(result_height)
        result_positions.append(current_y)
        current_y += result_height

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Обработка ввода
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False

            # Нажатие на кнопку "Очистить"
            if clear_button.collidepoint(event.pos):
                input_text = ""
                results = []
                key_held = False
                last_key = None
                backspace_held = False
                selected_item_index = None
                selected_result_index = None
                if button_sound:
                    button_sound.play()

            # Нажатие на кнопки сортировки
            if sort_asc_button.collidepoint(event.pos):
                if not inventory.sort_ascending:
                    inventory.toggle_sort()
                    results = inventory.search_items(input_text) if input_text else []
                    if button_sound:
                        button_sound.play()
            if sort_desc_button.collidepoint(event.pos):
                if inventory.sort_ascending:
                    inventory.toggle_sort()
                    results = inventory.search_items(input_text) if input_text else []
                    if button_sound:
                        button_sound.play()

            # Нажатие на кнопки категорий
            for button, category in category_buttons:
                if button.collidepoint(event.pos):
                    # Сохраняем текущий выбранный предмет (если есть)
                    selected_item = None
                    if selected_item_index is not None and selected_item_index < len(items):
                        selected_item = items[selected_item_index]
                    selected_result = None
                    if selected_result_index is not None and selected_result_index < len(results):
                        selected_result = results[selected_result_index]

                    # Переключаем категорию
                    inventory.set_category(category)
                    results = inventory.search_items(input_text) if input_text else []
                    items_scroll_y = 0
                    if button_sound:
                        button_sound.play()

                    # Обновляем список предметов после смены категории
                    new_items = inventory.get_items()
                    new_results = results

                    # Проверяем, остался ли выбранный предмет в списке "Все предметы"
                    if selected_item is not None:
                        try:
                            selected_item_index = new_items.index(selected_item)
                        except ValueError:
                            selected_item_index = None  # Сбрасываем выбор, если предмета больше нет

                    # Проверяем, остался ли выбранный результат в списке "Результаты поиска"
                    if selected_result is not None:
                        try:
                            selected_result_index = new_results.index(selected_result)
                        except ValueError:
                            selected_result_index = None  # Сбрасываем выбор, если результата больше нет
                    break

            # Проверка клика на предметы в списке "Все предметы"
            for i, (item, item_height, pos_y) in enumerate(zip(items, item_heights, item_positions)):
                y = pos_y - items_scroll_y
                if 50 <= mouse_x <= 410 and y <= mouse_y <= y + item_height and 200 <= y <= 200 + MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2:
                    selected_item_index = i
                    selected_result_index = None
                    if click_sound:
                        click_sound.play()
                    break

            # Проверка клика на предметы в списке "Результаты поиска"
            for i, (result, result_height, pos_y) in enumerate(zip(results, result_heights, result_positions)):
                y = pos_y - results_scroll_y
                if 420 <= mouse_x <= 780 and y <= mouse_y <= y + result_height and 200 <= y <= 200 + MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2:
                    selected_result_index = i
                    selected_item_index = None
                    if click_sound:
                        click_sound.play()
                    break

        # Прокрутка
        if event.type == pygame.MOUSEWHEEL:
            # Прокрутка категорий
            if 90 <= mouse_y <= 150:
                category_scroll_x -= event.x * 20
                category_scroll_x = max(0, category_scroll_x)
            # Прокрутка списка "Все предметы"
            elif 50 <= mouse_x <= 410:
                items_scroll_y -= event.y * 20
                items_scroll_y = max(0, min(items_scroll_y,
                                            max(0, sum(item_heights) - MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2)))
            # Прокрутка списка "Результаты поиска"
            elif 420 <= mouse_x <= 780:
                results_scroll_y -= event.y * 20
                results_scroll_y = max(0, min(results_scroll_y,
                                              max(0, sum(result_heights) - MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2)))

        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    if input_text:
                        results = inventory.search_items(input_text)
                        if search_sound:
                            search_sound.play()
                elif event.key == pygame.K_BACKSPACE:
                    backspace_held = True
                    backspace_timer = 0
                    if input_text:
                        input_text = input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    input_text = ""
                    results = []
                    key_held = False
                    last_key = None
                    backspace_held = False
                    selected_item_index = None
                    selected_result_index = None
                elif event.key == pygame.K_TAB and autocomplete_suggestion:
                    input_text = autocomplete_suggestion
                    results = inventory.search_items(input_text)
                    if search_sound:
                        search_sound.play()
                else:
                    key_held = True
                    key_timer = 0
                    last_key = event
                    input_text += event.unicode

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                backspace_held = False
            elif event.key != pygame.K_ESCAPE:
                key_held = False
                last_key = None

    # Обработка зажатия Backspace
    if active and backspace_held:
        backspace_timer += delta_time
        if backspace_timer >= (BACKSPACE_INITIAL_DELAY if backspace_timer == delta_time else BACKSPACE_REPEAT_DELAY):
            if input_text:
                input_text = input_text[:-1]
            backspace_timer = 0

    # Обработка зажатия букв
    if active and key_held and last_key:
        key_timer += delta_time
        if key_timer >= (KEY_INITIAL_DELAY if key_timer == delta_time else KEY_REPEAT_DELAY):
            input_text += last_key.unicode
            key_timer = 0

    # Автодополнение
    autocomplete_suggestion = inventory.get_autocomplete_suggestion(input_text)

    # Проверка наведения на предметы в списке "Все предметы"
    for i, (item, item_height, pos_y) in enumerate(zip(items, item_heights, item_positions)):
        y = pos_y - items_scroll_y
        if 50 <= mouse_x <= 410 and y <= mouse_y <= y + item_height and 200 <= y <= 200 + MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2:
            hovered_item_index = i
            break

    # Проверка наведения на предметы в списке "Результаты поиска"
    for i, (result, result_height, pos_y) in enumerate(zip(results, result_heights, result_positions)):
        y = pos_y - results_scroll_y
        if 420 <= mouse_x <= 780 and y <= mouse_y <= y + result_height and 200 <= y <= 200 + MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2:
            hovered_result_index = i
            break

    # Отрисовка интерфейса
    sort_asc_button, sort_desc_button, category_buttons = draw_ui(
        WINDOW, inventory, input_box, input_text, active, clear_button,
        items_scroll_y, results_scroll_y, category_scroll_x, results, "",
        autocomplete_suggestion, hovered_item_index, hovered_result_index,
        selected_item_index, selected_result_index, item_heights, result_heights,
        item_positions, result_positions
    )

    pygame.display.flip()

pygame.quit()
sys.exit()