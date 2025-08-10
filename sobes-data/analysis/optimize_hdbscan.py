import pandas as pd
import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

def test_hdbscan_params(csv_path):
    """Находим оптимальные параметры HDBSCAN"""
    df = pd.read_csv(csv_path)
    texts = df['question_text'].astype(str).fillna('').tolist()
    
    # TF-IDF векторизация для теста
    vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
    vectors = vectorizer.fit_transform(texts).toarray()
    
    # Тестируем разные комбинации параметров
    params_to_test = [
        {"min_cluster_size": 3, "min_samples": 2},   # Либеральные
        {"min_cluster_size": 5, "min_samples": 3},   # Умеренные  
        {"min_cluster_size": 8, "min_samples": 4},   # Строгие
        {"min_cluster_size": 12, "min_samples": 6},  # Очень строгие
    ]
    
    results = []
    
    for params in params_to_test:
        clusterer = HDBSCAN(
            min_cluster_size=params["min_cluster_size"],
            min_samples=params["min_samples"],
            metric='euclidean',
            cluster_selection_method='eom'
        )
        
        cluster_labels = clusterer.fit_predict(vectors)
        
        # Анализ
        unique_labels = set(cluster_labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = list(cluster_labels).count(-1)
        coverage = (len(texts) - n_noise) / len(texts) * 100
        
        cluster_sizes = Counter([label for label in cluster_labels if label != -1])
        max_size = max(cluster_sizes.values()) if cluster_sizes else 0
        avg_size = np.mean(list(cluster_sizes.values())) if cluster_sizes else 0
        
        result = {
            **params,
            "n_clusters": n_clusters,
            "coverage_percent": round(coverage, 1),
            "max_cluster_size": max_size,
            "avg_cluster_size": round(avg_size, 1),
            "noise_points": n_noise
        }
        results.append(result)
        
        print(f"Параметры: {params}")
        print(f"  Кластеров: {n_clusters}")
        print(f"  Покрытие: {coverage:.1f}%")
        print(f"  Макс размер: {max_size}")
        print(f"  Средний размер: {avg_size:.1f}")
        print(f"  Noise: {n_noise}")
        print()
    
    # Находим лучший баланс
    best = max(results, key=lambda r: r["coverage_percent"] - (r["max_cluster_size"] / 100))
    print(f"🎯 РЕКОМЕНДУЕМЫЕ ПАРАМЕТРЫ: {best}")
    return results

if __name__ == "__main__":
    test_hdbscan_params('sample_1000.csv')