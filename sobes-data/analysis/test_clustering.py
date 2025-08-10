import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import networkx as nx

def test_clustering_threshold(csv_path, threshold):
    df = pd.read_csv(csv_path)
    print(f'=== ТЕСТ ПОРОГА {threshold} ===')
    print(f'Загружено вопросов: {len(df)}')
    
    # Симуляция - используем hash для быстрого теста
    texts = df['question_text'].astype(str).fillna('').tolist()
    
    # Простая симуляция похожести через длины текстов (для быстрого теста)
    lengths = np.array([len(t) for t in texts]).reshape(-1, 1)
    
    # Нормализация
    lengths_norm = (lengths - lengths.mean()) / (lengths.std() + 1e-8)
    
    # Граф связей
    nn = NearestNeighbors(n_neighbors=min(20, len(lengths_norm)), metric='euclidean')
    nn.fit(lengths_norm)
    distances, indices = nn.kneighbors(lengths_norm)
    
    g = nx.Graph()
    g.add_nodes_from(range(len(lengths_norm)))
    
    # Используем threshold как similarity threshold (1 - distance)
    for i in range(len(lengths_norm)):
        for dist, j in zip(distances[i], indices[i]):
            if i != j:
                sim = 1.0 / (1.0 + float(dist))  # similarity от distance
                if sim >= threshold:
                    g.add_edge(int(i), int(j), weight=sim)
    
    # Кластеры
    components = list(nx.connected_components(g))
    sizes = [len(c) for c in components]
    
    print(f'Всего кластеров: {len(components)}')
    print(f'Размеры топ-10: {sorted(sizes, reverse=True)[:10]}')
    print(f'Одиночек: {len([s for s in sizes if s == 1])}')
    print(f'Больших (>5): {len([s for s in sizes if s > 5])}')
    print()

# Тестируем разные пороги
test_clustering_threshold('sample_1000.csv', 0.9)
test_clustering_threshold('sample_1000.csv', 0.8)
test_clustering_threshold('sample_1000.csv', 0.7)
test_clustering_threshold('sample_1000.csv', 0.6)