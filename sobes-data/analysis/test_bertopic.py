#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый запуск BERTopic для проверки работоспособности
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 50)
print("ТЕСТ BERTOPIC")
print("=" * 50)

# Проверка импортов
try:
    print("1. Проверка импортов...")
    from bertopic import BERTopic
    print("   ✓ BERTopic")
    from sentence_transformers import SentenceTransformer
    print("   ✓ SentenceTransformer")
    from umap import UMAP
    print("   ✓ UMAP")
    from hdbscan import HDBSCAN
    print("   ✓ HDBSCAN")
    import pandas as pd
    print("   ✓ pandas")
except Exception as e:
    print(f"   ✗ Ошибка импорта: {e}")
    sys.exit(1)

# Загрузка данных
print("\n2. Загрузка данных...")
try:
    df = pd.read_csv("../datasets/interview_questions_BAZA.csv", encoding='utf-8-sig')
    print(f"   ✓ Загружено {len(df)} записей")
    
    # Берем только первые 100 вопросов для теста
    test_texts = df['question_text'].astype(str).head(100).tolist()
    print(f"   ✓ Используем первые 100 вопросов для теста")
except Exception as e:
    print(f"   ✗ Ошибка загрузки: {e}")
    sys.exit(1)

# Создание модели
print("\n3. Создание модели BERTopic...")
try:
    # Простая модель для теста
    topic_model = BERTopic(
        language='multilingual',
        min_topic_size=5,  # Маленький размер для теста
        verbose=True
    )
    print("   ✓ Модель создана")
except Exception as e:
    print(f"   ✗ Ошибка создания модели: {e}")
    sys.exit(1)

# Анализ
print("\n4. Запуск анализа...")
try:
    topics, probs = topic_model.fit_transform(test_texts)
    print(f"   ✓ Анализ завершен!")
    print(f"   ✓ Найдено тем: {len(set(topics))}")
    print(f"   ✓ Выбросы: {topics.count(-1)}")
except Exception as e:
    print(f"   ✗ Ошибка анализа: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Результаты
print("\n5. Результаты:")
topic_info = topic_model.get_topic_info()
print(topic_info.head(10))

print("\n" + "=" * 50)
print("ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
print("=" * 50)