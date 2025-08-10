import pandas as pd
import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

# Загружаем полный датасет
print('Загружаем полный датасет...')
df = pd.read_csv('../datasets/interview_questions_BAZA.csv')
print(f'Всего вопросов: {len(df)}')

# Быстрая оценка через TF-IDF
texts = df['question_text'].astype(str).fillna('').tolist()
vectorizer = TfidfVectorizer(max_features=300, stop_words='english')
vectors = vectorizer.fit_transform(texts).toarray()

print('Тестируем HDBSCAN параметры...')

# Тест с оптимальными параметрами
clusterer = HDBSCAN(
    min_cluster_size=3,
    min_samples=2, 
    metric='euclidean',
    cluster_selection_method='eom'
)

cluster_labels = clusterer.fit_predict(vectors)

# Анализ результатов
unique_labels = set(cluster_labels)
n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
n_noise = list(cluster_labels).count(-1)
coverage = (len(texts) - n_noise) / len(texts) * 100

print(f'=== РЕЗУЛЬТАТЫ ===')
print(f'Кластеров найдено: {n_clusters}')
print(f'Покрытие: {coverage:.1f}%')
print(f'Noise points: {n_noise}')

# Размеры кластеров
cluster_sizes = Counter([label for label in cluster_labels if label != -1])
if cluster_sizes:
    sizes = sorted(cluster_sizes.values(), reverse=True)
    print(f'Топ-20 размеров: {sizes[:20]}')
    print(f'Максимальный размер: {max(sizes)}')
    print(f'Кластеров >50: {len([s for s in sizes if s > 50])}')
    print(f'Кластеров 5-50: {len([s for s in sizes if 5 <= s <= 50])}')
    print(f'Кластеров <5: {len([s for s in sizes if s < 5])}')
    
    # Сколько кластеров нужно обработать GPT
    clusters_for_gpt = len([s for s in sizes if s >= 5])  # min_size = 5
    clusters_for_gpt = min(clusters_for_gpt, 50)  # top_k = 50
    print(f'')
    print(f'КЛАСТЕРОВ ДЛЯ GPT: {clusters_for_gpt}')
    print(f'Запросов к GPT: {clusters_for_gpt * 3} (по 3 на кластер)')
    print(f'Примерная стоимость: ${clusters_for_gpt * 3 * 0.003:.2f}')