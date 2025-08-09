import argparse
import json
import math
import os
import re
import time
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
from tqdm import tqdm

# Third-party ML
from sklearn.neighbors import NearestNeighbors
import networkx as nx

# OpenAI SDK (works with ProxyAPI-compatible base_url)
from openai import OpenAI


DEFAULT_TAXONOMY = [
    # JavaScript Core
    "JS: типы и приведение типов",
    "JS: замыкания и область видимости",
    "JS: this/bind/call/apply",
    "JS: прототипы и классы",
    "JS: модули (ESM/CJS)",
    "JS: методы массивов/объектов",
    # Async
    "Async: event loop и микрозадачи",
    "Async: промисы/async-await",
    "Async: таймеры/AbortController/отмена",
    # TypeScript
    "TS: типы vs интерфейсы",
    "TS: generics и infer",
    "TS: utility/conditional/mapped types",
    "TS: any/unknown/never/void",
    "TS: overloads/satisfies/decorators",
    # React
    "React: основы/JSX/VDOM/reconciliation",
    "React: хуки useState/useEffect",
    "React: хуки useMemo/useCallback",
    "React: useRef/forwardRef/useLayoutEffect",
    "React: ключи/рендер/батчинг/оптимизация",
    "React: контекст/порталы/формы",
    # State Management
    "State: Redux и middleware",
    "State: Context/Reducer",
    "State: Effector/MobX",
    "State: Zustand/Valtio",
    # Browser
    "Browser: DOM/события/всплытие/погружение",
    "Browser: рендеринг/перфоманс (LCP/CLS)",
    "Browser: storage/cookies/session/local",
    "Browser: Web APIs (Workers/ServiceWorker/IDB)",
    # Network & Security
    "Net: HTTP/HTTPS/HTTP2/HTTP3",
    "Net: кэширование/ETag/CDN",
    "Security: CORS/CSRF",
    "Security: JWT/OAuth/авторизация",
    # Tooling / Architecture / Dev
    "Tooling: бандлеры (webpack/vite/rollup)",
    "Tooling: оптимизация бандла/код-сплиттинг",
    "Testing: unit/integration/e2e",
    "CI/CD и DevOps (Docker)",
    "Архитектура/SOLID/KISS/DRY/YAGNI",
    "Паттерны проектирования",
    "Node.js/SSR/Next.js",
    "API дизайн: REST/GraphQL/WebSocket",
    # HTML/CSS/Accessibility
    "HTML: семантика/доступность (ARIA)",
    "CSS: БЭМ/Flex/Grid/каскад/перфоманс",
    # Алгоритмы/Задачи
    "Алгоритмы: структуры данных/Big-O",
    "Алгоритмы: строки/массивы",
    "Алгоритмы: деревья/графы",
    "Алгоритмы: DP/поиск/сортировки",
    "Кодинг-задачи (JS/React)",
    # Поведенческие/Процессы
    "Поведенческие/процессы/коммуникации",
]


@dataclass
class ClusterLabel:
    cluster_id: int
    canonical_question: str
    topics: List[str]
    topic_confidence: Dict[str, float]
    rationale_short: str


def normalize_company(name: str) -> str:
    if not isinstance(name, str):
        return ""
    norm = name.strip()
    # Remove leading dashes and extra spaces
    norm = re.sub(r"^[-–—\s]+", "", norm)
    # Collapse multiple spaces
    norm = re.sub(r"\s+", " ", norm)
    return norm


def load_df(input_csv: str) -> pd.DataFrame:
    df = pd.read_csv(input_csv)
    required_cols = {"id", "question_text", "company", "date", "interview_id"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df["company_norm"] = df["company"].apply(normalize_company)
    df["question_text_norm"] = (
        df["question_text"].astype(str).str.strip().str.replace("\s+", " ", regex=True)
    )
    return df


def batched(iterable, batch_size: int):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i : i + batch_size]


def _make_cache_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _hash_texts(texts: List[str]) -> str:
    h = hashlib.sha1()
    for t in texts:
        h.update((t + "\n").encode("utf-8"))
    return h.hexdigest()


def compute_embeddings(
    client: OpenAI,
    texts: List[str],
    model: str,
    batch_size: int = 256,
    cache_dir: Optional[str] = None,
    max_retries: int = 3,
    request_timeout: float = 120.0,
) -> np.ndarray:
    cache_path: Optional[Path] = None
    if cache_dir:
        _make_cache_dir(cache_dir)
        cache_name = f"embeddings_{model}_{_hash_texts(texts)}.npy"
        cache_path = Path(cache_dir) / cache_name
        if cache_path.exists():
            return np.load(cache_path)

    embeddings: List[List[float]] = []
    for batch in tqdm(list(batched(texts, batch_size)), desc="Embeddings", unit="batch"):
        for attempt in range(1, max_retries + 1):
            try:
                resp = client.embeddings.create(model=model, input=batch, timeout=request_timeout)
                break
            except Exception:
                if attempt == max_retries:
                    raise
                time.sleep(1.5 * attempt)
        for item in resp.data:
            embeddings.append(item.embedding)
    arr = np.array(embeddings, dtype=np.float32)
    if cache_path:
        np.save(cache_path, arr)
    return arr


def build_similarity_graph(
    vectors: np.ndarray,
    cosine_threshold: float = 0.88,
    n_neighbors: int = 20,
) -> nx.Graph:
    # Normalize vectors to unit length for cosine
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    unit = vectors / norms

    nn = NearestNeighbors(n_neighbors=min(n_neighbors, len(unit)), metric="cosine", algorithm="auto")
    nn.fit(unit)
    distances, indices = nn.kneighbors(unit)

    g = nx.Graph()
    g.add_nodes_from(range(len(unit)))
    for i in range(len(unit)):
        for dist, j in zip(distances[i], indices[i]):
            if i == j:
                continue
            sim = 1.0 - float(dist)
            if sim >= cosine_threshold:
                g.add_edge(int(i), int(j), weight=sim)
    return g


def connected_components_clusters(graph: nx.Graph) -> Dict[int, int]:
    mapping: Dict[int, int] = {}
    for cid, comp in enumerate(nx.connected_components(graph), start=1):
        for idx in comp:
            mapping[int(idx)] = int(cid)
    return mapping


def merge_clusters_by_centroid(
    vectors: np.ndarray,
    idx_to_cluster: Dict[int, int],
    threshold: float,
) -> Dict[int, int]:
    if threshold <= 0.0:
        return idx_to_cluster
    # Compute centroids per cluster
    cluster_to_indices: Dict[int, List[int]] = defaultdict(list)
    for idx, cid in idx_to_cluster.items():
        cluster_to_indices[cid].append(idx)
    cluster_ids = sorted(cluster_to_indices.keys())
    centroids: Dict[int, np.ndarray] = {}
    for cid in cluster_ids:
        mat = vectors[cluster_to_indices[cid]]
        c = mat.mean(axis=0)
        n = np.linalg.norm(c)
        centroids[cid] = c / (n if n != 0.0 else 1.0)
    # Build cluster graph by centroid cosine
    g = nx.Graph()
    g.add_nodes_from(cluster_ids)
    arr = np.stack([centroids[cid] for cid in cluster_ids], axis=0)
    # brute-force cosine sim of centroids (clusters count is hundreds)
    sims = arr @ arr.T
    for i, cid_i in enumerate(cluster_ids):
        for j, cid_j in enumerate(cluster_ids):
            if j <= i:
                continue
            if sims[i, j] >= threshold:
                g.add_edge(cid_i, cid_j)
    # New cluster ids by components
    cluster_cc_map: Dict[int, int] = {}
    for new_cid, comp in enumerate(nx.connected_components(g), start=1):
        for old_cid in comp:
            cluster_cc_map[old_cid] = new_cid
    # Remap indices -> new cluster ids
    remapped: Dict[int, int] = {}
    for idx, old_cid in idx_to_cluster.items():
        remapped[idx] = cluster_cc_map.get(old_cid, old_cid)
    return remapped


def extract_representatives(
    df: pd.DataFrame,
    cluster_col: str,
    max_examples_per_cluster: int = 10,
) -> Dict[int, List[str]]:
    reps: Dict[int, List[str]] = {}
    grouped = df.groupby(cluster_col)
    for cid, g in grouped:
        examples = (
            g["question_text_norm"].dropna().astype(str).str.strip().str[:300].tolist()
        )
        # Deduplicate within cluster examples
        seen = set()
        deduped: List[str] = []
        for t in examples:
            k = t.lower()
            if k not in seen:
                seen.add(k)
                deduped.append(t)
        reps[int(cid)] = deduped[:max_examples_per_cluster]
    return reps


def ensure_json(s: str) -> Optional[dict]:
    try:
        return json.loads(s)
    except Exception:
        pass
    # Try to find the first JSON object in text
    m = re.search(r"\{[\s\S]*\}", s)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


def gpt_label_cluster_once(
    client: OpenAI,
    model: str,
    cluster_id: int,
    examples: List[str],
    taxonomy: List[str],
    temperature: float = 0.2,
    max_retries: int = 3,
    request_timeout: float = 120.0,
) -> Optional[ClusterLabel]:
    system = (
        "Ты — точный аналитик вопросов собеседований. "
        "Твоя задача: объединить перефразированные формулировки, присвоить темы из фиксированной таксономии и сформулировать краткий канонический вопрос. "
        "Отвечай строго одним JSON-объектом, соответствующим заданной схеме."
    )
    schema_hint = {
        "type": "object",
        "properties": {
            "cluster_id": {"type": "integer"},
            "canonical_question": {"type": "string"},
            "topics": {"type": "array", "items": {"type": "string"}},
            "topic_confidence": {"type": "object"},
            "rationale_short": {"type": "string"},
        },
        "required": [
            "cluster_id",
            "canonical_question",
            "topics",
            "topic_confidence",
            "rationale_short",
        ],
        "additionalProperties": False,
    }
    user = {
        "инструкция": (
            "Дан кластер перефразированных вопросов собеседований. Верни: "
            "- canonical_question: 1–2 строки, ёмко отражающие суть кластера; "
            "- topics: подмножество разрешённой таксономии (на русском); "
            "- topic_confidence: словарь тема->число от 0 до 1; "
            "- rationale_short: краткое обоснование (до 30 слов)."
        ),
        "cluster_id": cluster_id,
        "taxonomy_allowed": taxonomy,
        "examples": examples,
        "json_schema_hint": schema_hint,
        "output_format": {
            "cluster_id": cluster_id,
            "canonical_question": "string",
            "topics": ["string"],
            "topic_confidence": {"тема": 0.0},
            "rationale_short": "string",
        },
    }
    for attempt in range(1, max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
                ],
                response_format={"type": "json_object"},
                timeout=request_timeout,
            )
            break
        except Exception:
            if attempt == max_retries:
                return None
            time.sleep(1.5 * attempt)
    content = resp.choices[0].message.content or ""
    data = ensure_json(content)
    if not data:
        return None
    try:
        topics = [t for t in data.get("topics", []) if t in set(taxonomy)]
        conf = data.get("topic_confidence", {})
        conf_valid = {k: float(v) for k, v in conf.items() if k in set(taxonomy)}
        return ClusterLabel(
            cluster_id=int(data.get("cluster_id", cluster_id)),
            canonical_question=str(data.get("canonical_question", "")).strip(),
            topics=topics,
            topic_confidence=conf_valid,
            rationale_short=str(data.get("rationale_short", "")).strip(),
        )
    except Exception:
        return None


def majority_vote_labels(labels: List[ClusterLabel], taxonomy: List[str]) -> ClusterLabel:
    if not labels:
        return ClusterLabel(
            cluster_id=-1,
            canonical_question="",
            topics=[],
            topic_confidence={},
            rationale_short="",
        )
    cluster_id = labels[0].cluster_id
    # Canonical question: choose the most frequent non-empty, fallback to the longest
    canon_counter = Counter([l.canonical_question for l in labels if l.canonical_question])
    if canon_counter:
        canonical_question, _ = canon_counter.most_common(1)[0]
    else:
        canonical_question = max((l.canonical_question for l in labels), key=lambda x: len(x or ""), default="")

    # Topics: frequency threshold >= 2 votes
    topic_counter = Counter()
    conf_accum: Dict[str, List[float]] = defaultdict(list)
    for l in labels:
        for t in l.topics:
            if t in taxonomy:
                topic_counter[t] += 1
                if t in l.topic_confidence:
                    conf_accum[t].append(l.topic_confidence[t])
    topics: List[str] = []
    topic_conf: Dict[str, float] = {}
    for t, cnt in topic_counter.items():
        if cnt >= 2:  # majority across 3 runs
            topics.append(t)
            vals = conf_accum.get(t, [0.6])
            topic_conf[t] = float(np.mean(vals))

    return ClusterLabel(
        cluster_id=cluster_id,
        canonical_question=canonical_question,
        topics=topics,
        topic_confidence=topic_conf,
        rationale_short="",
    )


def _labels_jsonl_path(outdir: str, model: str, cosine: float, neighbors: int, merge_t: float) -> Path:
    _make_cache_dir(outdir)
    name = f"labels_{model}_ct{cosine:.2f}_nn{neighbors}_mc{merge_t:.2f}.jsonl"
    return Path(outdir) / name


def _load_existing_labels(jsonl_path: Path) -> Dict[int, ClusterLabel]:
    results: Dict[int, ClusterLabel] = {}
    if not jsonl_path.exists():
        return results
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                cid = int(d["cluster_id"])
                results[cid] = ClusterLabel(
                    cluster_id=cid,
                    canonical_question=d.get("canonical_question", ""),
                    topics=d.get("topics", []) or [],
                    topic_confidence=d.get("topic_confidence", {}) or {},
                    rationale_short=d.get("rationale_short", ""),
                )
            except Exception:
                continue
    return results


def _append_label(jsonl_path: Path, label: ClusterLabel) -> None:
    rec = {
        "cluster_id": label.cluster_id,
        "canonical_question": label.canonical_question,
        "topics": label.topics,
        "topic_confidence": label.topic_confidence,
        "rationale_short": label.rationale_short,
    }
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def label_all_clusters(
    client: OpenAI,
    model: str,
    cluster_to_examples: Dict[int, List[str]],
    taxonomy: List[str],
    self_consistency_runs: int = 3,
    temperature: float = 0.2,
    outdir_for_labels: Optional[str] = None,
    cosine: float = 0.88,
    neighbors: int = 20,
    merge_t: float = 0.0,
    max_retries: int = 3,
    request_timeout: float = 120.0,
    label_workers: int = 1,
) -> Dict[int, ClusterLabel]:
    # Load existing labels (resume capability)
    jsonl_path = _labels_jsonl_path(outdir_for_labels or "sobes-data/analysis/outputs", model, cosine, neighbors, merge_t)
    existing = _load_existing_labels(jsonl_path)

    def process_cluster(cid: int, examples: List[str]) -> Tuple[int, ClusterLabel]:
        if cid in existing and existing[cid].canonical_question:
            return cid, existing[cid]
        runs: List[ClusterLabel] = []
        for _ in range(self_consistency_runs):
            lab = gpt_label_cluster_once(
                client=client,
                model=model,
                cluster_id=cid,
                examples=examples,
                taxonomy=taxonomy,
                temperature=temperature,
                max_retries=max_retries,
                request_timeout=request_timeout,
            )
            if lab:
                runs.append(lab)
        voted = majority_vote_labels(runs, taxonomy)
        _append_label(jsonl_path, voted)
        return cid, voted

    items = list(cluster_to_examples.items())
    results: Dict[int, ClusterLabel] = dict(existing)
    if label_workers > 1:
        with ThreadPoolExecutor(max_workers=label_workers) as ex:
            futures = [ex.submit(process_cluster, cid, exs) for cid, exs in items]
            for fut in tqdm(as_completed(futures), total=len(futures), desc="Labeling clusters", unit="cluster"):
                try:
                    cid, lab = fut.result()
                    results[cid] = lab
                except Exception:
                    continue
    else:
        for cid, exs in tqdm(items, desc="Labeling clusters", unit="cluster"):
            try:
                _, lab = process_cluster(cid, exs)
                results[cid] = lab
            except Exception:
                continue
    return results


def aggregates(
    df: pd.DataFrame,
    cluster_col: str,
    topics_map: Dict[int, List[str]],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Top clusters globally (by distinct interviews)
    top_clusters = (
        df.groupby(cluster_col)["interview_id"].nunique().reset_index(name="interviews_count")
    )
    top_clusters["company_count"] = df.groupby(cluster_col)["company_norm"].nunique().values
    top_clusters = top_clusters.sort_values(["interviews_count", "company_count"], ascending=False)

    # Topics per interview (distinct)
    topic_rows: List[Tuple[str, str]] = []  # (interview_id, topic)
    for _, row in df.iterrows():
        cid = int(row[cluster_col])
        iv = str(row["interview_id"])
        for t in topics_map.get(cid, []):
            topic_rows.append((iv, t))
    topics_df = pd.DataFrame(topic_rows, columns=["interview_id", "topic"]).drop_duplicates()
    top_topics = topics_df.groupby("topic")["interview_id"].nunique().reset_index(name="interviews_count")
    top_topics = top_topics.sort_values("interviews_count", ascending=False)

    # By company: top clusters
    by_company_clusters = (
        df.groupby(["company_norm", cluster_col])["interview_id"].nunique().reset_index(name="interviews_count")
    )
    by_company_clusters = by_company_clusters.sort_values(["company_norm", "interviews_count"], ascending=[True, False])

    return top_clusters, top_topics, by_company_clusters


def save_outputs(
    outdir: str,
    df_with_clusters: pd.DataFrame,
    cluster_labels: Dict[int, ClusterLabel],
    top_clusters: pd.DataFrame,
    top_topics: pd.DataFrame,
    by_company_clusters: pd.DataFrame,
) -> None:
    os.makedirs(outdir, exist_ok=True)

    # Clusters assignment
    df_with_clusters.to_csv(os.path.join(outdir, "questions_with_clusters.csv"), index=False)

    # Cluster labels
    labels_rows = []
    for cid, lab in cluster_labels.items():
        labels_rows.append({
            "cluster_id": cid,
            "canonical_question": lab.canonical_question,
            "topics": ", ".join(lab.topics),
            "topic_confidence": json.dumps(lab.topic_confidence, ensure_ascii=False),
        })
    pd.DataFrame(labels_rows).to_csv(os.path.join(outdir, "cluster_labels.csv"), index=False)

    # Aggregates
    top_clusters.to_csv(os.path.join(outdir, "top_clusters_global.csv"), index=False)
    top_topics.to_csv(os.path.join(outdir, "top_topics_global.csv"), index=False)
    by_company_clusters.to_csv(os.path.join(outdir, "by_company_top_clusters.csv"), index=False)


def main():
    parser = argparse.ArgumentParser(description="Interview questions analytics pipeline (ProxyAPI-compatible)")
    parser.add_argument("--input", required=True, help="Path to CSV (with id, question_text, company, date, interview_id)")
    parser.add_argument("--outdir", default="sobes-data/analysis/outputs", help="Output directory")
    parser.add_argument("--embedding-model", default="text-embedding-3-large", help="Embedding model name")
    parser.add_argument("--chat-model", default="gpt-4.1-mini", help="Chat model for labeling")
    parser.add_argument("--neighbors", type=int, default=50, help="Nearest neighbors per point for graph")
    parser.add_argument("--cosine-threshold", type=float, default=0.85, help="Cosine similarity threshold for edges")
    parser.add_argument("--self-consistency-runs", type=int, default=3, help="Number of GPT runs per cluster")
    parser.add_argument("--max-examples-per-cluster", type=int, default=8, help="Max examples sent to GPT per cluster")
    parser.add_argument("--merge-centroid-threshold", type=float, default=0.0, help="Optional extra merge step by centroid cosine (e.g., 0.92). 0 disables.")
    parser.add_argument("--cache-dir", default="sobes-data/analysis/cache", help="Directory to cache embeddings and intermediates")
    parser.add_argument("--max-retries", type=int, default=3, help="Max retries for API calls")
    parser.add_argument("--request-timeout", type=float, default=120.0, help="Timeout (s) for API calls")
    parser.add_argument("--label-workers", type=int, default=1, help="Parallel workers for labeling (use with care vs ProxyAPI limits)")
    parser.add_argument("--proxyapi-config", default="sobes-data/analysis/.proxyapi.json", help="Path to local ProxyAPI config JSON {base_url, api_key}")
    parser.add_argument("--proxyapi-base-url", default=os.getenv("PROXYAPI_BASE_URL", ""), help="(Optional) Proxy API base URL env/flag fallback")
    parser.add_argument("--proxyapi-api-key", default=os.getenv("PROXYAPI_API_KEY", ""), help="(Optional) Proxy API key env/flag fallback")
    args = parser.parse_args()

    # Load ProxyAPI config (prefer local JSON), then fall back to env/flags
    cfg_base_url = ""
    cfg_api_key = ""
    if args.proxyapi_config and os.path.exists(args.proxyapi_config):
        try:
            with open(args.proxyapi_config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                cfg_base_url = str(cfg.get("base_url", "")).strip()
                cfg_api_key = str(cfg.get("api_key", "")).strip()
        except Exception as e:
            raise SystemExit(f"Failed to read proxy config {args.proxyapi_config}: {e}")
    base_url = cfg_base_url or args.proxyapi_base_url
    api_key = cfg_api_key or args.proxyapi_api_key
    if not api_key or not base_url:
        raise SystemExit("ProxyAPI credentials required. Create sobes-data/analysis/.proxyapi.json with {\"base_url\":\"...\",\"api_key\":\"...\"}")

    # Initialize client for ProxyAPI-compatible endpoint
    client = OpenAI(api_key=api_key, base_url=base_url)

    df = load_df(args.input)

    # Compute embeddings
    texts = df["question_text_norm"].astype(str).tolist()
    emb = compute_embeddings(
        client,
        texts,
        model=args.embedding_model,
        batch_size=256,
        cache_dir=args.cache_dir,
        max_retries=args.max_retries,
        request_timeout=args.request_timeout,
    )

    # Graph clustering via cosine threshold
    graph = build_similarity_graph(emb, cosine_threshold=args.cosine_threshold, n_neighbors=args.neighbors)
    idx_to_cluster = connected_components_clusters(graph)
    # Optional merge by centroids to reduce over-segmentation
    if args.merge_centroid_threshold and args.merge_centroid_threshold > 0.0:
        idx_to_cluster = merge_clusters_by_centroid(emb, idx_to_cluster, threshold=args.merge_centroid_threshold)
    df["cluster_id"] = df.index.map(lambda i: idx_to_cluster.get(int(i), -1))

    # Representatives for labeling
    reps = extract_representatives(df, cluster_col="cluster_id", max_examples_per_cluster=args.max_examples_per_cluster)

    # Label clusters with GPT (self-consistency)
    cluster_labels = label_all_clusters(
        client=client,
        model=args.chat_model,
        cluster_to_examples=reps,
        taxonomy=DEFAULT_TAXONOMY,
        self_consistency_runs=args.self_consistency_runs,
        temperature=0.2,
        outdir_for_labels=args.outdir,
        cosine=args.cosine_threshold,
        neighbors=args.neighbors,
        merge_t=args.merge_centroid_threshold or 0.0,
        max_retries=args.max_retries,
        request_timeout=args.request_timeout,
        label_workers=args.label_workers,
    )

    # Map topics for aggregates
    topics_map: Dict[int, List[str]] = {cid: lab.topics for cid, lab in cluster_labels.items()}

    # Aggregates
    top_clusters, top_topics, by_company_clusters = aggregates(df, cluster_col="cluster_id", topics_map=topics_map)

    # Save
    save_outputs(
        outdir=args.outdir,
        df_with_clusters=df[["id", "question_text", "company", "date", "interview_id", "company_norm", "question_text_norm", "cluster_id"]],
        cluster_labels=cluster_labels,
        top_clusters=top_clusters,
        top_topics=top_topics,
        by_company_clusters=by_company_clusters,
    )

    print(f"Done. Outputs saved to: {args.outdir}")


if __name__ == "__main__":
    main()


