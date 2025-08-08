import os
import hashlib
import json
import re
from typing import List, Tuple, Dict, Iterable, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from umap import UMAP  # type: ignore
from keybert import KeyBERT  # type: ignore
from rapidfuzz import process, fuzz  # type: ignore
import hdbscan  # type: ignore
from sentence_transformers import SentenceTransformer
import seaborn as sns
import matplotlib.pyplot as plt


DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'sobes-data', 'datasets', 'interview_questions_BAZA.csv')
OUT_DIR = os.path.join(os.path.dirname(__file__), 'out')
EMB_CACHE_PATH = os.path.join(OUT_DIR, 'embeddings.npy')
INDEX_CACHE_PATH = os.path.join(OUT_DIR, 'index.csv')
COMPANY_CANON_PATH = os.path.join(os.path.dirname(__file__), '..', 'sobes-data', 'data', 'front-full-companies-from-json.json')
COMPANY_NORM_OUT = os.path.join(OUT_DIR, 'company_normalization.csv')

MODEL_NAME = 'intfloat/multilingual-e5-base'

# Clustering (agglomerative) defaults
AGG_DISTANCE_THRESHOLD = 0.35  # cosine distance; ~ similarity 0.65
AGG_LINKAGE = 'complete'       # complete linkage is robust to chaining

# Clustering (HDBSCAN) defaults
HDBSCAN_MIN_CLUSTER_SIZE = 8
HDBSCAN_MIN_SAMPLES = 2
# Use euclidean on L2-normalized embeddings (equivalent to cosine-based separation)
HDBSCAN_METRIC = 'euclidean'

# UMAP before HDBSCAN
USE_UMAP = True
UMAP_N_NEIGHBORS = 30
UMAP_N_COMPONENTS = 15
UMAP_MIN_DIST = 0.0
UMAP_METRIC = 'cosine'

# HDBSCAN parameter sweep (minimize noise, tie-breaker maximize clusters)
HDBSCAN_SWEEP_MIN_CLUSTER_SIZE = [6, 8, 10, 12]
HDBSCAN_SWEEP_MIN_SAMPLES = [1, 2, 3]

# Duplicates
K_NEIGHBORS = 20
EMBED_DUP_THRESHOLD = 0.95
CHAR_TFIDF_DUP_THRESHOLD = 0.90

# Reporting
MIN_CLUSTER_SIZE_FOR_HEATMAP = 8
HEATMAP_TOP_CLUSTERS = 30
TOP_LABEL_WORDS = 3
MERGE_CENTROID_SIM_THRESHOLD = 0.91
TOP_CLUSTERS_REVIEW_COUNT = 50
REVIEW_EXAMPLES_PER_CLUSTER = 5
COMPANY_PROFILE_TOP_N = 10

# RU/EN stop words for interview phrasing fillers (extend as needed)
STOP_WORDS_RU_EN = {
    # Russian fillers
    'что', 'как', 'почему', 'зачем', 'какие', 'какой', 'какая', 'каков', 'какова',
    'такое', 'такова', 'объясните', 'расскажите', 'перечислите', 'опишите', 'приведите',
    'пример', 'нужно', 'нужен', 'нужна', 'можно', 'следует', 'для', 'в', 'на', 'и', 'или',
    'это', 'этот', 'эта', 'этом', 'будет', 'бы', 'есть', 'ли', 'когда', 'где', 'чем',
    'поясните', 'пояснить', 'сравните', 'разница', 'различия', 'отличие', 'расскажите',
    'про', 'об', 'о', 'какие', 'какова', 'каковы', 'нужно ли', 'можно ли', 'зачем нужен', 'зачем нужна',
    # English fillers
    'what', 'how', 'why', 'explain', 'describe', 'list', 'give', 'example', 'examples', 'should',
    'is', 'are', 'was', 'were', 'be', 'to', 'of', 'in', 'for', 'and', 'or'
}

# Patterns to normalize question phrasing for better labels
TEMPLATE_PATTERNS = [
    (r'^что\s+такое\s+', ''),
    (r'^зачем\s+нужен\s+', ''),
    (r'^зачем\s+нужна\s+', ''),
    (r'^для\s+чего\s+нужен\s+', ''),
    (r'^для\s+чего\s+нужна\s+', ''),
    (r'^в\s+ч[её]м\s+разница\s+между\s+', ''),
    (r'^в\s+ч[её]м\s+разница\s+', ''),
    (r'^какая\s+разница\s+между\s+', ''),
    (r'^какая\s+разница\s+', ''),
    (r'^чего\s+', ''),
    (r'^расскажите\s+про\s+', ''),
    (r'^объясните\s+', ''),
    (r'^объясни\s+', ''),
    (r'^расскажи\s+про\s+', ''),
    (r'^почему\s+', ''),
    (r'^как\s+работает\s+', ''),
    (r'^как\s+используется\s+', ''),
]


def ensure_out_dir() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def read_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Basic normalization
    df['question_text'] = df['question_text'].astype(str).str.replace('\s+', ' ', regex=True).str.strip()
    # Company normalization: remove leading numeric/stage prefixes, legal forms, stray dashes
    df['company'] = (
        df['company']
        .astype(str)
        # remove leading dashes/spaces
        .str.replace('^[-\s]*', '', regex=True)
        # remove numeric prefixes like "06 ", "10-", "07_" etc.
        .str.replace(r'^[0-9]{1,3}[\s\-_.–—]+', '', regex=True)
        # remove common legal forms
        .str.replace(r'\b(ООО|ПАО|АО|ЗАО|OAO|ZAO|OOO|LLC|Inc|JSC|АО «|ООО «|ПАО «)\b', '', regex=True, case=False)
        # collapse spaces/dashes
        .str.replace('[\s\-–—_]+', ' ', regex=True)
        .str.strip()
    )
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


def cluster_agglomerative(emb: np.ndarray, distance_threshold: float, linkage: str = 'complete') -> List[int]:
    """
    Perform Agglomerative clustering with cosine metric and a distance threshold.
    Returns a list of cluster labels in range [0..C-1]. Noise is not explicitly modeled.
    """
    # AgglomerativeClustering with distance_threshold requires n_clusters=None
    model = AgglomerativeClustering(
        n_clusters=None,
        metric='cosine',
        linkage=linkage,
        distance_threshold=distance_threshold,
    )
    labels = model.fit_predict(emb)
    # Reindex labels to 0..C-1
    unique = {}
    next_id = 0
    remapped = []
    for lab in labels:
        if lab not in unique:
            unique[lab] = next_id
            next_id += 1
        remapped.append(unique[lab])
    return remapped


def cluster_hdbscan(
    emb: np.ndarray,
    min_cluster_size: int = HDBSCAN_MIN_CLUSTER_SIZE,
    min_samples: int = HDBSCAN_MIN_SAMPLES,
    metric: str = HDBSCAN_METRIC,
) -> Tuple[List[int], List[bool]]:
    """
    Cluster with HDBSCAN. Returns remapped labels and a list indicating noise points.
    Noise in HDBSCAN is labeled as -1; we keep a boolean mask and remap only non-noise clusters to 0..C-1.
    """
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, metric=metric)
    labels = clusterer.fit_predict(emb)
    is_noise = (labels == -1)
    # Remap non-noise labels to 0..C-1
    unique = {}
    next_id = 0
    remapped = []
    for lab in labels:
        if lab == -1:
            remapped.append(-1)
            continue
        if lab not in unique:
            unique[lab] = next_id
            next_id += 1
        remapped.append(unique[lab])
    return remapped, is_noise.tolist()


def label_clusters(df: pd.DataFrame, cluster_col: str = 'cluster_id') -> pd.DataFrame:
    labels: Dict[int, str] = {}
    # Prepare TF-IDF vectorizer for fallback
    vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), stop_words=STOP_WORDS_RU_EN, min_df=1)
    # KeyBERT model for better keyphrases
    kb = KeyBERT(model=MODEL_NAME)

    for cid, sub in df.groupby(cluster_col):
        # Skip labeling for noise cluster if present
        if cid == -1:
            labels[cid] = 'noise'
            continue
        texts_raw = sub['question_text'].astype(str).tolist()
        texts = [normalize_for_label(t) for t in texts_raw]
        if not texts:
            labels[cid] = 'misc'
            continue

        sample_texts = texts[:80]
        base_label = ''

        # Try KeyBERT first
        try:
            doc = ' \n'.join(sample_texts)
            keywords = kb.extract_keywords(
                doc,
                keyphrase_ngram_range=(1, 2),
                stop_words=list(STOP_WORDS_RU_EN),
                use_maxsum=True,
                nr_candidates=40,
                top_n=TOP_LABEL_WORDS,
            )
            key_terms = [kw for kw, _ in keywords if kw.strip()]
            base_label = ' / '.join(key_terms)
        except Exception:
            base_label = ''

        # Fallback to TF-IDF
        if not base_label:
            try:
                X = vectorizer.fit_transform(sample_texts)
                if X.shape[1] > 0:
                    feature_names = np.array(vectorizer.get_feature_names_out())
                    scores = np.asarray(X.mean(axis=0)).ravel()
                    top_idx = np.argsort(scores)[::-1][:TOP_LABEL_WORDS]
                    top_terms = [feature_names[i] for i in top_idx]
                    base_label = ' / '.join(top_terms)
            except Exception:
                base_label = ''

        labels[cid] = f"{cid}: {base_label if base_label else 'misc'}"

    label_df = pd.DataFrame([(cid, label) for cid, label in labels.items()], columns=[cluster_col, 'cluster_label'])
    return label_df


def build_heatmap(df: pd.DataFrame, out_path: str) -> None:
    # Filter small clusters to reduce noise
    # Exclude noise if present
    if 'is_noise' in df.columns:
        df = df[~df['is_noise']].copy()
    cluster_sizes = df.groupby('cluster_id')['row_id'].count().rename('size')
    big_clusters = cluster_sizes[cluster_sizes >= MIN_CLUSTER_SIZE_FOR_HEATMAP].sort_values(ascending=False)
    if big_clusters.empty:
        print('No clusters pass size threshold for heatmap; skipping heatmap.')
        return

    top_cluster_ids = big_clusters.head(HEATMAP_TOP_CLUSTERS).index
    df_big = df[df['cluster_id'].isin(top_cluster_ids)].copy()

    pivot = df_big.pivot_table(index='company', columns='cluster_label', values='row_id', aggfunc='count', fill_value=0)
    # Normalize per company (row-wise) for comparability
    pivot_norm = pivot.div(pivot.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)

    plt.figure(figsize=(max(10, pivot_norm.shape[1] * 0.6), max(6, pivot_norm.shape[0] * 0.3)))
    sns.heatmap(pivot_norm, cmap='YlGnBu')
    plt.title('Company × Topic (normalized per company, top topics)')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def build_heatmap_variants(df: pd.DataFrame, base_path: str) -> None:
    # Exclude noise
    data = df[~df.get('is_noise', False)].copy()
    if data.empty:
        return
    # Limit to top clusters
    cluster_sizes = data.groupby('cluster_id')['row_id'].count().sort_values(ascending=False)
    top_ids = cluster_sizes.head(HEATMAP_TOP_CLUSTERS).index
    data = data[data['cluster_id'].isin(top_ids)]
    pivot = data.pivot_table(index='company', columns='cluster_label', values='row_id', aggfunc='count', fill_value=0)
    if pivot.empty:
        return

    # Absolute counts
    plt.figure(figsize=(max(10, pivot.shape[1] * 0.6), max(6, pivot.shape[0] * 0.3)))
    sns.heatmap(pivot, cmap='YlGnBu')
    plt.title('Company × Topic (absolute)')
    plt.tight_layout()
    plt.savefig(base_path.replace('.png', '_abs.png'), dpi=200)
    plt.close()

    # Row-wise normalization
    row_norm = pivot.div(pivot.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
    plt.figure(figsize=(max(10, row_norm.shape[1] * 0.6), max(6, row_norm.shape[0] * 0.3)))
    sns.heatmap(row_norm, cmap='YlGnBu')
    plt.title('Company × Topic (row-wise normalized)')
    plt.tight_layout()
    plt.savefig(base_path.replace('.png', '_row.png'), dpi=200)
    plt.close()

    # Col-wise normalization
    col_norm = pivot.div(pivot.sum(axis=0).replace(0, np.nan), axis=1).fillna(0)
    plt.figure(figsize=(max(10, col_norm.shape[1] * 0.6), max(6, col_norm.shape[0] * 0.3)))
    sns.heatmap(col_norm, cmap='YlGnBu')
    plt.title('Company × Topic (col-wise normalized)')
    plt.tight_layout()
    plt.savefig(base_path.replace('.png', '_col.png'), dpi=200)
    plt.close()


def build_monthly_trends(df: pd.DataFrame, out_csv: str) -> None:
    data = df[~df.get('is_noise', False)].copy()
    if data.empty:
        pd.DataFrame(columns=['month', 'cluster_label', 'count']).to_csv(out_csv, index=False)
        return
    data['month'] = data['date'].dt.to_period('M').dt.to_timestamp()
    # Limit to top topics
    top = data['cluster_id'].value_counts().head(HEATMAP_TOP_CLUSTERS).index
    sub = data[data['cluster_id'].isin(top)]
    trends = sub.groupby(['month', 'cluster_label']).size().reset_index(name='count').sort_values(['month', 'count'], ascending=[True, False])
    trends.to_csv(out_csv, index=False)


def build_cooccurrence(df: pd.DataFrame, out_csv: str) -> None:
    data = df[~df.get('is_noise', False)].copy()
    if data.empty:
        pd.DataFrame(columns=['cluster_label_a', 'cluster_label_b', 'count']).to_csv(out_csv, index=False)
        return
    # Limit to top topics
    top = data['cluster_id'].value_counts().head(HEATMAP_TOP_CLUSTERS).index
    sub = data[data['cluster_id'].isin(top)]
    pairs: Dict[Tuple[int, int], int] = {}
    for _, group in sub.groupby('interview_id'):
        clusts = sorted(set(group['cluster_id'].tolist()))
        for i in range(len(clusts)):
            for j in range(i + 1, len(clusts)):
                key = (clusts[i], clusts[j])
                pairs[key] = pairs.get(key, 0) + 1
    if not pairs:
        pd.DataFrame(columns=['cluster_label_a', 'cluster_label_b', 'count']).to_csv(out_csv, index=False)
        return
    # Map ids to labels
    id_to_label = sub[['cluster_id', 'cluster_label']].drop_duplicates().set_index('cluster_id')['cluster_label'].to_dict()
    rows = [(id_to_label.get(a, str(a)), id_to_label.get(b, str(b)), c) for (a, b), c in pairs.items()]
    df_pairs = pd.DataFrame(rows, columns=['cluster_label_a', 'cluster_label_b', 'count']).sort_values('count', ascending=False)
    df_pairs.to_csv(out_csv, index=False)


def export_company_profiles(df: pd.DataFrame, out_csv: str, top_n: int = COMPANY_PROFILE_TOP_N) -> None:
    data = df[~df.get('is_noise', False)].copy()
    if data.empty:
        pd.DataFrame(columns=['company', 'rank', 'cluster_id', 'cluster_label', 'count', 'share']).to_csv(out_csv, index=False)
        return
    counts = (
        data.groupby(['company', 'cluster_id', 'cluster_label']).size().reset_index(name='count')
    )
    totals = counts.groupby('company')['count'].sum().rename('total')
    counts = counts.merge(totals, on='company', how='left')
    counts['share'] = (counts['count'] / counts['total']).fillna(0.0)
    # rank within company
    counts['rank'] = counts.groupby('company')['count'].rank(method='first', ascending=False)
    top = counts[counts['rank'] <= top_n].sort_values(['company', 'rank'])
    top[['company', 'rank', 'cluster_id', 'cluster_label', 'count', 'share']].to_csv(out_csv, index=False)


def export_cluster_size_hist(df: pd.DataFrame, out_png: str) -> None:
    data = df[~df.get('is_noise', False)].copy()
    if data.empty:
        return
    sizes = data.groupby('cluster_id').size()
    plt.figure(figsize=(8, 4))
    sns.histplot(sizes, bins=40)
    plt.title('Cluster size distribution (non-noise)')
    plt.xlabel('Cluster size')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()


def reduce_with_umap(emb: np.ndarray) -> np.ndarray:
    reducer = UMAP(
        n_neighbors=UMAP_N_NEIGHBORS,
        n_components=UMAP_N_COMPONENTS,
        min_dist=UMAP_MIN_DIST,
        metric=UMAP_METRIC,
        random_state=42,
    )
    return reducer.fit_transform(emb)


def normalize_for_label(text: str) -> str:
    t = text.strip()
    for pattern, repl in TEMPLATE_PATTERNS:
        try:
            t = re.sub(pattern, repl, t, flags=re.IGNORECASE)
        except re.error:
            continue
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def generate_duplicates(
    df: pd.DataFrame,
    emb: np.ndarray,
    k: int = K_NEIGHBORS,
    embed_threshold: float = EMBED_DUP_THRESHOLD,
    char_threshold: float = CHAR_TFIDF_DUP_THRESHOLD,
    out_path: str = None,
) -> pd.DataFrame:
    """Generate candidate duplicate pairs using embedding similarity and confirm with char TF-IDF."""
    n = emb.shape[0]
    # Neighbors on embeddings
    nn = NearestNeighbors(n_neighbors=min(k + 1, n), metric='cosine')
    nn.fit(emb)
    dist, idx = nn.kneighbors(emb, return_distance=True)
    sim = 1.0 - dist

    # Char TF-IDF for robustness to casing/punctuation; 3-5 char n-grams
    char_vec = TfidfVectorizer(analyzer='char', ngram_range=(3, 5), min_df=2)
    X_char = char_vec.fit_transform(df['question_text'].astype(str))

    pairs = []
    for i in range(n):
        for j_pos in range(1, idx.shape[1]):  # skip self
            j = int(idx[i, j_pos])
            s = float(sim[i, j_pos])
            if s < embed_threshold:
                continue
            # Compute char similarity for candidate pair
            c_sim = float(cosine_similarity(X_char[i], X_char[j]).ravel()[0])
            if c_sim < char_threshold:
                continue
            if i < j:  # keep one direction
                pairs.append((i, j, s, c_sim))

    dup_df = pd.DataFrame(pairs, columns=['row_id_1', 'row_id_2', 'sim_embed', 'sim_char'])
    if dup_df.empty:
        if out_path:
            pd.DataFrame(columns=['row_id_1', 'row_id_2', 'sim_embed', 'sim_char']).to_csv(out_path, index=False)
        return dup_df

    # Join context
    left = df[['row_id', 'id', 'question_text', 'company', 'date']].rename(columns={
        'row_id': 'row_id_1', 'id': 'id_1', 'question_text': 'question_text_1', 'company': 'company_1', 'date': 'date_1'
    })
    right = df[['row_id', 'id', 'question_text', 'company', 'date']].rename(columns={
        'row_id': 'row_id_2', 'id': 'id_2', 'question_text': 'question_text_2', 'company': 'company_2', 'date': 'date_2'
    })
    dup_df = dup_df.merge(left, on='row_id_1', how='left').merge(right, on='row_id_2', how='left')

    if out_path:
        dup_df.to_csv(out_path, index=False)
    return dup_df


def merge_close_clusters(df: pd.DataFrame, emb: np.ndarray, threshold: float = MERGE_CENTROID_SIM_THRESHOLD) -> pd.DataFrame:
    # Use only non-noise
    data = df[~df.get('is_noise', False)].copy()
    if data.empty:
        return df
    # Compute centroids per cluster_id
    centroids = []
    ids = []
    for cid, sub in data.groupby('cluster_id'):
        vec = emb[sub['row_id'].values]
        centroids.append(vec.mean(axis=0))
        ids.append(cid)
    centroids = np.vstack(centroids)
    # cosine similarity via dot (embeddings are normalized or UMAP; normalize centroids)
    centroids = centroids / (np.linalg.norm(centroids, axis=1, keepdims=True) + 1e-9)
    sim = centroids @ centroids.T
    n = sim.shape[0]
    parent = {cid: cid for cid in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            if sim[i, j] >= threshold:
                union(ids[i], ids[j])

    # Build mapping old -> root
    root_map = {cid: find(cid) for cid in ids}
    df = df.copy()
    df['cluster_id'] = df['cluster_id'].apply(lambda x: root_map.get(x, x))
    return df


def export_top_clusters_review(df: pd.DataFrame, out_csv: str, top_n: int = TOP_CLUSTERS_REVIEW_COUNT, examples_per: int = REVIEW_EXAMPLES_PER_CLUSTER) -> None:
    data = df[~df.get('is_noise', False)].copy()
    if data.empty:
        pd.DataFrame(columns=['cluster_id', 'cluster_label', 'example_question']).to_csv(out_csv, index=False)
        return
    counts = data['cluster_id'].value_counts().head(top_n).index
    rows = []
    for cid in counts:
        sub = data[data['cluster_id'] == cid]
        label = sub['cluster_label'].iloc[0]
        examples = sub['question_text'].head(examples_per).tolist()
        for ex in examples:
            rows.append((cid, label, ex))
    pd.DataFrame(rows, columns=['cluster_id', 'cluster_label', 'example_question']).to_csv(out_csv, index=False)

def main():
    ensure_out_dir()

    print('Reading data...')
    df = read_data(DATA_PATH)

    print('Loading model...')
    model = build_model()

    print('Computing embeddings...')
    emb = compute_or_load_embeddings(model, df['question_text'].tolist())

    print('Normalizing companies with canonical list (if available)...')
    try:
        with open(COMPANY_CANON_PATH, 'r', encoding='utf-8') as f:
            canon_raw = json.load(f)
        if isinstance(canon_raw, list):
            canonical = [str(x).strip() for x in canon_raw]
        elif isinstance(canon_raw, dict):
            canonical = list(set([str(k).strip() for k in canon_raw.keys()]))
        else:
            canonical = []
    except Exception:
        canonical = []
    if canonical:
        from rapidfuzz import process, fuzz  # local import safeguard
        unique_companies = sorted(set(df['company'].astype(str)))
        mapping = []
        norm_map = {}
        for comp in unique_companies:
            match = process.extractOne(comp, canonical, scorer=fuzz.WRatio)
            if match:
                best, score, _ = match
                if score >= 92:
                    norm_map[comp] = best
                else:
                    norm_map[comp] = comp
                mapping.append((comp, norm_map[comp], score))
            else:
                norm_map[comp] = comp
                mapping.append((comp, comp, 0))
        df['company_original'] = df['company']
        df['company'] = df['company'].map(norm_map).fillna(df['company'])
        pd.DataFrame(mapping, columns=['original', 'normalized', 'score']).to_csv(COMPANY_NORM_OUT, index=False)

    print('Clustering (UMAP + HDBSCAN sweep)...')
    emb_for_clustering = reduce_with_umap(emb) if True else emb
    # Sweep
    best_labels = None
    best_noise = None
    best_stats = {'noise': 10**9, 'clusters': -1, 'mcs': -1, 'ms': -1}
    for mcs in [6, 8, 10, 12]:
        for ms in [1, 2, 3]:
            labels, is_noise = cluster_hdbscan(emb_for_clustering, min_cluster_size=mcs, min_samples=ms, metric=HDBSCAN_METRIC)
            noise = int(np.sum(is_noise))
            clusters_num = len(set([l for l in labels if l != -1]))
            if (noise < best_stats['noise']) or (noise == best_stats['noise'] and clusters_num > best_stats['clusters']):
                best_labels, best_noise = labels, is_noise
                best_stats = {'noise': noise, 'clusters': clusters_num, 'mcs': mcs, 'ms': ms}
    print(f"Selected HDBSCAN params: min_cluster_size={best_stats['mcs']}, min_samples={best_stats['ms']}, noise={best_stats['noise']}, clusters={best_stats['clusters']}")
    clusters, is_noise = best_labels, best_noise
    df['cluster_id'] = clusters
    df['is_noise'] = is_noise

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

    print('Merging close clusters...')
    df_merged = merge_close_clusters(df, emb)
    # Recompute labels after merge (fast TF-IDF/KeyBERT on merged)
    label_df_merged = label_clusters(df_merged)
    df_merged = df_merged.drop(columns=['cluster_label'], errors='ignore').merge(label_df_merged, on='cluster_id', how='left')

    print('Saving outputs...')
    df_merged.to_csv(os.path.join(OUT_DIR, 'questions_with_clusters.csv'), index=False)
    (
        df_merged.groupby(['cluster_id', 'cluster_label'])
        .agg(count=('row_id', 'count'), companies=('company', pd.Series.nunique), first_seen=('date', 'min'), last_seen=('date', 'max'))
        .reset_index()
        .sort_values('count', ascending=False)
    ).to_csv(os.path.join(OUT_DIR, 'cluster_stats.csv'), index=False)
    (
        df_merged.groupby(['company', 'cluster_id', 'cluster_label']).size().reset_index(name='count').sort_values(['company', 'count'], ascending=[True, False])
    ).to_csv(os.path.join(OUT_DIR, 'company_cluster_counts.csv'), index=False)

    print('Generating duplicates...')
    generate_duplicates(
        df=df,
        emb=emb,
        k=K_NEIGHBORS,
        embed_threshold=EMBED_DUP_THRESHOLD,
        char_threshold=CHAR_TFIDF_DUP_THRESHOLD,
        out_path=os.path.join(OUT_DIR, 'duplicates.csv'),
    )

    print('Building heatmaps...')
    base_heatmap = os.path.join(OUT_DIR, 'company_topic_heatmap.png')
    build_heatmap(df_merged, base_heatmap)
    build_heatmap_variants(df_merged, base_heatmap)

    print('Building monthly trends and co-occurrences...')
    build_monthly_trends(df_merged, os.path.join(OUT_DIR, 'topic_trends_monthly.csv'))
    build_cooccurrence(df_merged, os.path.join(OUT_DIR, 'topic_cooccurrence.csv'))

    print('Exporting top clusters review...')
    export_top_clusters_review(df_merged, os.path.join(OUT_DIR, 'top_clusters_review.csv'))

    print('Exporting company profiles and QC plots...')
    export_company_profiles(df_merged, os.path.join(OUT_DIR, 'company_profiles_top.csv'))
    export_cluster_size_hist(df_merged, os.path.join(OUT_DIR, 'cluster_size_hist.png'))

    print('Done.')


if __name__ == '__main__':
    main()
