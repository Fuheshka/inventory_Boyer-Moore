# inventory.py
import json
from search import boyer_moore_search, fuzzy_match


class Inventory:
    def __init__(self):
        # Загружаем предметы из файла items.json
        with open("items.json", "r", encoding="utf-8") as f:
            self.items_by_category = json.load(f)
        self.sort_ascending = True
        self.current_category = "Все"  # Текущая категория для фильтрации
        self.items = self.get_filtered_items()  # Текущий список предметов

    def get_filtered_items(self):
        if self.current_category == "Все":
            # Собираем все предметы из всех категорий
            all_items = []
            for category, items in self.items_by_category.items():
                all_items.extend(items)
            return sorted(all_items, reverse=not self.sort_ascending)
        else:
            # Возвращаем предметы только из выбранной категории
            items = self.items_by_category.get(self.current_category, [])
            return sorted(items, reverse=not self.sort_ascending)

    def search_items(self, query):
        found_items = []
        query = query.lower().strip()

        for item in self.items:  # Ищем только среди отфильтрованных предметов
            words = item.lower().split()
            for word in words:
                if boyer_moore_search(word, query):
                    found_items.append(item)
                    break
                if fuzzy_match(word, query):
                    found_items.append(item)
                    break

        return sorted(list(set(found_items)), reverse=not self.sort_ascending)

    def get_autocomplete_suggestion(self, query):
        if not query:
            return None
        query = query.lower().strip()
        for item in self.items:  # Ищем среди отфильтрованных предметов
            if item.lower().startswith(query):
                return item
        return None

    def toggle_sort(self):
        self.sort_ascending = not self.sort_ascending
        self.items = self.get_filtered_items()

    def set_category(self, category):
        self.current_category = category
        self.items = self.get_filtered_items()

    def get_items(self):
        return self.items

    def get_categories(self):
        return ["Все"] + list(self.items_by_category.keys())