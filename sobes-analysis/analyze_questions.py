import os
import hashlib
from typing import List, Tuple, Dict

import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import seaborn as sns
import matplotlib.pyplot as plt


DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'sobes-data', 'datasets', 'interview_questions_BAZA.csv')
OUT_DIR = os.path.join(os.path.dirname(__file__), 'out')
EMB_CACHE_PATH = os.path.join(OUT_DIR, 'embeddings.npy')
INDEX_CACHE_PATH = os.path.join(OUT_DIR, 'index.csv')

MODEL_NAME = 'intfloat/multilingual-e5-base'
K_NEIGHBORS = 10
SIM_THRESHOLD = 0.88
MIN_CLUSTER_SIZE_FOR_HEATMAP = 8
TOP_LABEL_WORDS = 3


def ensure_out_dir() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def read_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Basic normalization
    df['question_text'] = df['question_text'].astype(str).str.replace('\s+', ' ', regex=True).str.strip()
    df['company'] = df['company'].astype(str).str.replace('^[-\s]*', '', regex=True).str.strip()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # Local row id
    df['row_id'] = np.arange(len(df))
    return df


def build_model() -> SentenceTransformer:
    model = SentenceTransformer(MODEL_NAME)
    return model


def compute_or_load_embeddings(model: SentenceTransformer, texts: List[str]) -> np.ndarray:
    ensure_out_dir()
    if os.path.exists(EMB_CACHE_PATH) and os.path.exists(INDEX_CACHE_PATH):
        idx_df = pd.read_csv(INDEX_CACHE_PATH)
        if len(idx_df) == len(texts) and os.path.exists(EMB_CACHE_PATH):
            emb = np.load(EMB_CACHE_PATH)
            if emb.shape[0] == len(texts):
                return emb
    # E5 style prefix for passages
    prefixed = [f"passage: {t}" for t in texts]
    emb = model.encode(prefixed, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
    np.save(EMB_CACHE_PATH, emb)
    pd.DataFrame({'row_id': np.arange(len(texts))}).to_csv(INDEX_CACHE_PATH, index=False)
    return emb


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1


def cluster_by_similarity(emb: np.ndarray, k: int, threshold: float) -> List[int]:
    n = emb.shape[0]
    nn = NearestNeighbors(n_neighbors=min(k + 1, n), metric='cosine')
    nn.fit(emb)
    distances, indices = nn.kneighbors(emb, return_distance=True)
    # cosine distance -> similarity
    similarities = 1.0 - distances

    uf = UnionFind(n)
    for i in range(n):
        for j_idx in range(1, indices.shape[1]):  # skip self at j_idx 0
            j = indices[i, j_idx]
            sim = similarities[i, j_idx]
            if sim >= threshold:
                uf.union(i, int(j))

    roots = [uf.find(i) for i in range(n)]
    # Reindex cluster ids to 0..C-1
    root_to_cluster: Dict[int, int] = {}
    next_id = 0
    clusters = []
    for r in roots:
        if r not in root_to_cluster:
            root_to_cluster[r] = next_id
            next_id += 1
        clusters.append(root_to_cluster[r])
    return clusters


def label_clusters(df: pd.DataFrame, cluster_col: str = 'cluster_id') -> pd.DataFrame:
    labels = {}
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))

    for cid, sub in df.groupby(cluster_col):
        texts = sub['question_text'].tolist()
        if len(texts) == 0:
            labels[cid] = 'misc'
            continue
        X = vectorizer.fit_transform(texts)
        feature_names = np.array(vectorizer.get_feature_names_out())
        scores = np.asarray(X.mean(axis=0)).ravel()
        top_idx = np.argsort(scores)[::-1][:TOP_LABEL_WORDS]
        top_terms = [feature_names[i] for i in top_idx]
        labels[cid] = ' / '.join(top_terms)

    label_df = pd.DataFrame([(cid, label) for cid, label in labels.items()], columns=[cluster_col, 'cluster_label'])
    return label_df


def build_heatmap(df: pd.DataFrame, out_path: str) -> None:
    # Filter small clusters to reduce noise
    cluster_sizes = df.groupby('cluster_id')['row_id'].count().rename('size')
    big_clusters = cluster_sizes[cluster_sizes >= MIN_CLUSTER_SIZE_FOR_HEATMAP].index
    df_big = df[df['cluster_id'].isin(big_clusters)].copy()

    if df_big.empty:
        print('No clusters pass size threshold for heatmap; skipping heatmap.')
        return

    pivot = df_big.pivot_table(index='company', columns='cluster_label', values='row_id', aggfunc='count', fill_value=0)
    # Normalize per company (row-wise) for comparability
    pivot_norm = pivot.div(pivot.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)

    plt.figure(figsize=(max(8, pivot_norm.shape[1] * 0.5), max(6, pivot_norm.shape[0] * 0.3)))
    sns.heatmap(pivot_norm, cmap='YlGnBu')
    plt.title('Company × Topic (normalized per company)')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def main():
    ensure_out_dir()

    print('Reading data...')
    df = read_data(DATA_PATH)

    print('Loading model...')
    model = build_model()

    print('Computing embeddings...')
    emb = compute_or_load_embeddings(model, df['question_text'].tolist())

    print('Clustering...')
    clusters = cluster_by_similarity(emb, k=K_NEIGHBORS, threshold=SIM_THRESHOLD)
    df['cluster_id'] = clusters

    print('Labeling clusters...')
    label_df = label_clusters(df)
    df = df.merge(label_df, on='cluster_id', how='left')

    print('Aggregating stats...')
    # Per-cluster stats
    cluster_stats = (
        df.groupby(['cluster_id', 'cluster_label'])
          .agg(count=('row_id', 'count'), companies=('company', pd.Series.nunique), first_seen=('date', 'min'), last_seen=('date', 'max'))
          .reset_index()
          .sort_values('count', ascending=False)
    )

    # Company × Cluster counts
    company_cluster = (
        df.groupby(['company', 'cluster_id', 'cluster_label'])
          .size()
          .reset_index(name='count')
          .sort_values(['company', 'count'], ascending=[True, False])
    )

    print('Saving outputs...')
    df.to_csv(os.path.join(OUT_DIR, 'questions_with_clusters.csv'), index=False)
    cluster_stats.to_csv(os.path.join(OUT_DIR, 'cluster_stats.csv'), index=False)
    company_cluster.to_csv(os.path.join(OUT_DIR, 'company_cluster_counts.csv'), index=False)

    print('Building heatmap...')
    build_heatmap(df, os.path.join(OUT_DIR, 'company_topic_heatmap.png'))

    print('Done.')


if __name__ == '__main__':
    main()
