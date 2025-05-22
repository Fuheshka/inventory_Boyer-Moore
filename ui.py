# ui.py
import pygame

def wrap_text(text, font, max_width):
    """Переносит текст на несколько строк, если он превышает заданную ширину"""
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())

    return lines

def draw_ui(window, inventory, input_box, input_text, active, clear_button, items_scroll_y, results_scroll_y,
            category_scroll_x, results, selected_message, autocomplete_suggestion, hovered_item_index,
            hovered_result_index, selected_item_index, selected_result_index, item_heights, result_heights,
            item_positions, result_positions):
    # Цвета
    BACKGROUND_COLOR = (240, 240, 240)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (180, 180, 180)
    DARK_GRAY = (120, 120, 120)
    RED = (255, 0, 0)
    BLUE = (0, 120, 255)
    GREEN = (0, 200, 0)

    # Шрифты
    FONT = pygame.font.Font(None, 36)
    SMALL_FONT = pygame.font.Font(None, 28)
    TINY_FONT = pygame.font.Font(None, 24)

    # Константы
    BASE_ITEM_HEIGHT = 20
    MAX_VISIBLE_ITEMS = 12
    CATEGORY_BUTTON_WIDTH = 90
    LIST_WIDTH = 360
    # Отступы для метки "Выбрано"
    SELECTED_LABEL_OFFSET_ITEMS = 50  # Для списка "Все предметы"
    SELECTED_LABEL_OFFSET_RESULTS = 90  # Для списка "Результаты поиска"

    # Отрисовка
    window.fill(BACKGROUND_COLOR)

    # Поле ввода (с индикацией активности)
    pygame.draw.rect(window, BLUE if active else BLACK, input_box, 2)
    input_surface = FONT.render(input_text, True, BLACK)
    window.blit(input_surface, (input_box.x + 5, input_box.y + 5))

    # Отображение автодополнения
    if autocomplete_suggestion and active:
        suggestion_text = SMALL_FONT.render(f"Tab: {autocomplete_suggestion}", True, GRAY)
        window.blit(suggestion_text, (50, 90))

    # Кнопка "Очистить"
    pygame.draw.rect(window, RED, clear_button)
    clear_text = TINY_FONT.render("Очистить", True, WHITE)
    window.blit(clear_text, (clear_button.x + 10, clear_button.y + 10))

    # Кнопки категорий
    categories = inventory.get_categories()
    category_buttons = []
    total_category_width = len(categories) * (CATEGORY_BUTTON_WIDTH + 10)
    max_category_scroll = max(0, total_category_width - 900)
    category_scroll_x = min(category_scroll_x, max_category_scroll)

    for i, category in enumerate(categories):
        x = 50 + i * (CATEGORY_BUTTON_WIDTH + 10) - category_scroll_x
        if category == "Аксессуары":
            button = pygame.Rect(x, 120, 110, 30)
        elif category == "Разное":
            button = pygame.Rect(x+20, 120, CATEGORY_BUTTON_WIDTH, 30)
        else:
            button = pygame.Rect(x, 120, CATEGORY_BUTTON_WIDTH, 30)
        pygame.draw.rect(window, BLUE if inventory.current_category == category else DARK_GRAY, button)
        category_text = TINY_FONT.render(category, True, WHITE)
        window.blit(category_text, (button.x + 5, button.y + 5))
        category_buttons.append((button, category))

    # Заголовок
    title = FONT.render("Поиск предметов в инвентаре", True, BLACK)
    window.blit(title, (50, 10))

    # Список всех предметов (с прокруткой и выделением)
    items_title = SMALL_FONT.render("Все предметы:", True, BLACK)
    window.blit(items_title, (50, 170))
    items = inventory.get_items()
    pygame.draw.rect(window, GRAY, (45, 195, LIST_WIDTH, MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2 + 10), 1)

    # Отрисовка предметов
    for i, (item, item_height, pos_y) in enumerate(zip(items, item_heights, item_positions)):
        y = pos_y - items_scroll_y
        if 200 <= y <= 200 + MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2:
            is_hovered = i == hovered_item_index
            is_selected = i == selected_item_index
            lines = wrap_text(item, SMALL_FONT, LIST_WIDTH - 10)
            for j, line in enumerate(lines):  # Убрано ограничение на 2 строки
                item_text = SMALL_FONT.render(line, True, BLACK)
                window.blit(item_text, (50, y + j * BASE_ITEM_HEIGHT))
            if is_hovered or is_selected:
                pygame.draw.rect(window, BLUE, (45, y - 2, LIST_WIDTH, item_height + 4), 2)
            # Добавляем метку "Выбрано" напротив выбранного предмета
            if is_selected:
                selected_text = SMALL_FONT.render("Выбрано", True, GREEN)
                window.blit(selected_text, (LIST_WIDTH - SELECTED_LABEL_OFFSET_ITEMS, y))

    # Результаты поиска (с прокруткой и выделением)
    results_title = SMALL_FONT.render("Результаты поиска:", True, BLACK)
    window.blit(results_title, (420, 170))
    pygame.draw.rect(window, GRAY, (415, 195, LIST_WIDTH, MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2 + 10), 1)

    # Отрисовка результатов
    if results:
        for i, (result, result_height, pos_y) in enumerate(zip(results, result_heights, result_positions)):
            y = pos_y - results_scroll_y
            if 200 <= y <= 200 + MAX_VISIBLE_ITEMS * BASE_ITEM_HEIGHT * 2:
                is_hovered = i == hovered_result_index
                is_selected = i == selected_result_index
                lines = wrap_text(result, SMALL_FONT, LIST_WIDTH - 10)
                for j, line in enumerate(lines):  # Убрано ограничение на 2 строки
                    result_text = SMALL_FONT.render(line, True, BLACK)
                    window.blit(result_text, (420, y + j * BASE_ITEM_HEIGHT))
                if is_hovered or is_selected:
                    pygame.draw.rect(window, BLUE, (415, y - 2, LIST_WIDTH, result_height + 4), 2)
                # Добавляем метку "Выбрано" напротив выбранного результата
                if is_selected:
                    selected_text = SMALL_FONT.render("Выбрано", True, GREEN)
                    window.blit(selected_text, (415 + LIST_WIDTH - SELECTED_LABEL_OFFSET_RESULTS, y))
    else:
        no_results = SMALL_FONT.render("Предметы не найдены", True, GRAY)
        window.blit(no_results, (420, 200))

    # Кнопки сортировки
    sort_asc_button = pygame.Rect(730, 115, 120, 40)
    sort_desc_button = pygame.Rect(860, 115, 120, 40)
    pygame.draw.rect(window, BLUE, sort_asc_button)
    pygame.draw.rect(window, BLUE, sort_desc_button)
    sort_asc_text = SMALL_FONT.render("Сорт. А-Я", True, WHITE)
    sort_desc_text = SMALL_FONT.render("Сорт. Я-А", True, WHITE)
    window.blit(sort_asc_text, (sort_asc_button.x + 5, sort_asc_button.y + 5))
    window.blit(sort_desc_text, (sort_desc_button.x + 5, sort_desc_button.y + 5))

    return sort_asc_button, sort_desc_button, category_buttons