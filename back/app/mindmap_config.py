# Конфигурация для связывания топиков MindMap с реальными категориями контента

# Маппинг ключей топиков MindMap к категориям ContentBlocks
MINDMAP_TO_CATEGORIES = {
    'objects': {
        'mainCategory': 'JS',
        'subCategory': 'Objects',
        'title': 'Объекты',
        'icon': '📦',
        'color': '#84CC16',
        'description': 'Работа с объектами и их свойствами'
    },
    'arrays': {
        'mainCategory': 'JS',
        'subCategory': 'Array',
        'title': 'Массивы',
        'icon': '📝',
        'color': '#F59E0B',
        'description': 'Работа с массивами и их методами'
    },
    'strings': {
        'mainCategory': 'JS',
        'subCategory': 'Strings',
        'title': 'Строки',
        'icon': '🔤',
        'color': '#8B5CF6',
        'description': 'Обработка строк и регулярные выражения'
    },
    'closures': {
        'mainCategory': 'JS',
        'subCategory': 'Zamiki',  # Замыкания в базе называются "Zamiki"
        'title': 'Замыкания',
        'icon': '🔒',
        'color': '#8B5CF6',
        'description': 'Функции и области видимости'
    },
    'promises': {
        'mainCategory': 'JS',
        'subCategory': 'Promise',
        'title': 'Промисы',
        'icon': '🔄',
        'color': '#06B6D4',
        'description': 'Асинхронная работа и промисы'
    },
    'classes': {
        'mainCategory': 'JS',
        'subCategory': 'Classes',
        'title': 'Классы',
        'icon': '🏗️',
        'color': '#10B981',
        'description': 'ООП и классы в JavaScript'
    },
    'custom_functions': {
        'mainCategory': 'JS',
        'subCategory': 'Custom method and function',  # Точное название из БД
        'title': 'Кастомные методы и функции',
        'icon': '⚡',
        'color': '#3B82F6',
        'description': 'Создание собственных функций и методов'
    },
    'numbers': {
        'mainCategory': 'JS',
        'subCategory': 'Numbers',
        'title': 'Числа',
        'icon': '🔢',
        'color': '#EF4444',
        'description': 'Работа с числами и математикой'
    },
    # Временно убираем топики которых нет в БД
    # 'throttle_debounce': {
    #     'mainCategory': 'JS',
    #     'subCategory': 'Performance',
    #     'title': 'Тротлы и дебаунсы',
    #     'icon': '⏱️',
    #     'color': '#F97316',
    #     'description': 'Оптимизация производительности'
    # },
    # 'time': {
    #     'mainCategory': 'JS',
    #     'subCategory': 'Time',
    #     'title': 'Часовая',
    #     'icon': '🕐',
    #     'color': '#06B6D4',
    #     'description': 'Работа с временем и датами'
    # },
    # 'matrices': {
    #     'mainCategory': 'JS',
    #     'subCategory': 'Matrices',
    #     'title': 'Матрицы',
    #     'icon': '🔢',
    #     'color': '#EF4444',
    #     'description': 'Двумерные массивы и матрицы'
    # }
}

def get_topic_config(topic_key: str):
    """Получить конфигурацию топика по ключу"""
    return MINDMAP_TO_CATEGORIES.get(topic_key)

def get_category_filters(topic_key: str):
    """Получить фильтры категорий для топика"""
    config = get_topic_config(topic_key)
    if not config:
        return None
    
    return {
        'mainCategory': config['mainCategory'],
        'subCategory': config['subCategory']
    }

def get_all_topics():
    """Получить все доступные топики"""
    return MINDMAP_TO_CATEGORIES 