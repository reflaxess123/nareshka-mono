# Конфигурация для связывания топиков MindMap с реальными категориями контента

# Конфигурация центральных узлов для разных технологий
TECHNOLOGY_CENTERS = {
    "javascript": {
        "title": "JavaScript Skills",
        "description": "Изучение JavaScript",
        "icon": "⚡",
        "color": "#F7DF1E",
        "mainCategory": "JS",
    },
    "react": {
        "title": "React Skills",
        "description": "Изучение React",
        "icon": "⚛️",
        "color": "#61DAFB",
        "mainCategory": "REACT",
    },
    "typescript": {
        "title": "TypeScript Skills",
        "description": "Изучение TypeScript",
        "icon": "🔷",
        "color": "#3178C6",
        "mainCategory": "TS",
    },
}

# Маппинг ключей топиков MindMap к категориям ContentBlocks для JavaScript
JAVASCRIPT_TOPICS = {
    "objects": {
        "mainCategory": "JS",
        "subCategory": "Objects",
        "title": "Объекты",
        "icon": "📦",
        "color": "#84CC16",
        "description": "Работа с объектами и их свойствами",
    },
    "arrays": {
        "mainCategory": "JS",
        "subCategory": "Array",
        "title": "Массивы",
        "icon": "📝",
        "color": "#F59E0B",
        "description": "Работа с массивами и их методами",
    },
    "strings": {
        "mainCategory": "JS",
        "subCategory": "Strings",
        "title": "Строки",
        "icon": "🔤",
        "color": "#8B5CF6",
        "description": "Обработка строк и регулярные выражения",
    },
    "closures": {
        "mainCategory": "JS",
        "subCategory": "Zamiki",  # Замыкания в базе называются "Zamiki"
        "title": "Замыкания",
        "icon": "🔒",
        "color": "#8B5CF6",
        "description": "Функции и области видимости",
    },
    "promises": {
        "mainCategory": "JS",
        "subCategory": "Promise",
        "title": "Промисы",
        "icon": "🔄",
        "color": "#06B6D4",
        "description": "Асинхронная работа и промисы",
    },
    "classes": {
        "mainCategory": "JS",
        "subCategory": "Classes",
        "title": "Классы",
        "icon": "🏗️",
        "color": "#10B981",
        "description": "ООП и классы в JavaScript",
    },
    "custom_functions": {
        "mainCategory": "JS",
        "subCategory": "Custom method and function",  # Точное название из БД
        "title": "Кастомные методы и функции",
        "icon": "⚡",
        "color": "#3B82F6",
        "description": "Создание собственных функций и методов",
    },
    "numbers": {
        "mainCategory": "JS",
        "subCategory": "Numbers",
        "title": "Числа",
        "icon": "🔢",
        "color": "#EF4444",
        "description": "Работа с числами и математикой",
    },
}

# Маппинг топиков для React (используем реальные данные из БД)
REACT_TOPICS = {
    "hooks": {
        "mainCategory": "REACT",
        "subCategory": "Hooks",
        "title": "Хуки",
        "icon": "🎣",
        "color": "#61DAFB",
        "description": "useState, useEffect, кастомные хуки",
    },
    "refactor": {
        "mainCategory": "REACT",
        "subCategory": "Refactor",
        "title": "Рефакторинг",
        "icon": "🔄",
        "color": "#20B2AA",
        "description": "Улучшение и оптимизация React кода",
    },
    "rerender": {
        "mainCategory": "REACT",
        "subCategory": "Rerender",
        "title": "Ререндеринг",
        "icon": "🔁",
        "color": "#FF6B6B",
        "description": "Оптимизация перерисовки компонентов",
    },
    "mini_app": {
        "mainCategory": "REACT",
        "subCategory": "React mini app",
        "title": "Мини-приложения",
        "icon": "📱",
        "color": "#4ECDC4",
        "description": "Небольшие React приложения",
    },
}

# Маппинг топиков для TypeScript (используем реальные данные из БД)
TYPESCRIPT_TOPICS = {
    "tasks": {
        "mainCategory": "TS",
        "subCategory": "Задачи",
        "title": "Задачи",
        "icon": "📋",
        "color": "#3178C6",
        "description": "Практические задачи по TypeScript",
    },
    "utility_types": {
        "mainCategory": "TS",
        "subCategory": "Утилитные типы",
        "title": "Утилитные типы",
        "icon": "🛠️",
        "color": "#007ACC",
        "description": "Pick, Omit, Partial, Record и другие",
    },
}

# Объединенный маппинг всех технологий
TECHNOLOGY_TOPICS = {
    "javascript": JAVASCRIPT_TOPICS,
    "react": REACT_TOPICS,
    "typescript": TYPESCRIPT_TOPICS,
}

# Для обратной совместимости
MINDMAP_TO_CATEGORIES = JAVASCRIPT_TOPICS


def get_technology_center(technology: str):
    """Получить конфигурацию центрального узла для технологии"""
    return TECHNOLOGY_CENTERS.get(technology)


def get_technology_topics(technology: str):
    """Получить все топики для конкретной технологии"""
    return TECHNOLOGY_TOPICS.get(technology, {})


def get_topic_config(topic_key: str, technology: str = "javascript"):
    """Получить конфигурацию топика по ключу и технологии"""
    topics = get_technology_topics(technology)
    return topics.get(topic_key)


def get_category_filters(topic_key: str, technology: str = "javascript"):
    """Получить фильтры категорий для топика"""
    config = get_topic_config(topic_key, technology)
    if not config:
        return None

    return {
        "mainCategory": config["mainCategory"],
        "subCategory": config["subCategory"],
    }


def get_all_topics(technology: str = "javascript"):
    """Получить все доступные топики для технологии"""
    return get_technology_topics(technology)


def get_available_technologies():
    """Получить список доступных технологий"""
    return list(TECHNOLOGY_CENTERS.keys()) 


