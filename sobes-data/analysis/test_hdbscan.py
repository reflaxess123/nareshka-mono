import pandas as pd
import numpy as np
from sklearn.cluster import HDBSCAN
from collections import Counter

def test_hdbscan_clustering(csv_path, min_cluster_size=5, min_samples=3, max_cluster_size=50):
    """Тест HDBSCAN без GPT - только кластеризация"""
    print(f"=== ТЕСТ HDBSCAN ===")
    print(f"min_cluster_size={min_cluster_size}, min_samples={min_samples}, max_cluster_size={max_cluster_size}")
    
    # Загружаем данные
    df = pd.read_csv(csv_path)
    texts = df['question_text'].astype(str).fillna('').tolist()
    print(f"Загружено вопросов: {len(texts)}")
    
    # Симуляция эмбеддингов через TF-IDF (для быстрого теста)
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
    vectors = vectorizer.fit_transform(texts).toarray()
    
    print(f"Размерность векторов: {vectors.shape}")
    
    # HDBSCAN кластеризация
    clusterer = HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric='euclidean',
        cluster_selection_method='eom'
    )
    
    cluster_labels = clusterer.fit_predict(vectors)
    
    # Анализ результатов
    unique_labels = set(cluster_labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
    n_noise = list(cluster_labels).count(-1)
    
    print(f"Кластеров найдено: {n_clusters}")
    print(f"Noise points: {n_noise}")
    
    # Размеры кластеров
    cluster_sizes = Counter([label for label in cluster_labels if label != -1])
    if cluster_sizes:
        sizes = list(cluster_sizes.values())
        print(f"Размеры кластеров: {sorted(sizes, reverse=True)[:10]}")
        print(f"Максимальный размер: {max(sizes)}")
        print(f"Кластеров >max_cluster_size ({max_cluster_size}): {len([s for s in sizes if s > max_cluster_size])}")
        print(f"Кластеров размером 1: {len([s for s in sizes if s == 1])}")
    else:
        print("Кластеров не найдено!")
    
    print()
    return cluster_labels

# Тестируем разные параметры
test_hdbscan_clustering('sample_1000.csv', min_cluster_size=5, min_samples=3, max_cluster_size=50)
test_hdbscan_clustering('sample_1000.csv', min_cluster_size=10, min_samples=5, max_cluster_size=50)  
test_hdbscan_clustering('sample_1000.csv', min_cluster_size=15, min_samples=10, max_cluster_size=50)