import argparse
import json
import os
from typing import List, Dict, Any

import pandas as pd


def _find_latest_labels_jsonl(base_dir: str) -> str:
    candidates: List[str] = [
        os.path.join(base_dir, name)
        for name in os.listdir(base_dir)
        if name.startswith("labels_") and name.endswith(".jsonl")
    ]
    if not candidates:
        raise SystemExit(f"Не найден labels_*.jsonl в {base_dir}")
    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates[0]


def _load_labels_jsonl(path: str) -> pd.DataFrame:
    records: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                # Нормализуем типы
                rec["cluster_id"] = int(rec.get("cluster_id"))
                topics = rec.get("topics")
                if isinstance(topics, list):
                    rec["topics"] = topics
                else:
                    rec["topics"] = []
                records.append(rec)
            except Exception:
                continue
    if not records:
        raise SystemExit(f"Файл пуст или испорчен: {path}")
    df = pd.DataFrame(records)
    # Drop duplicates by cluster_id, keeping the last occurrence
    df = df.drop_duplicates(subset=["cluster_id"], keep="last")
    # Precompute stringified topics for convenience
    df["topics_str"] = df["topics"].apply(lambda xs: ", ".join(xs) if isinstance(xs, list) else "")
    return df[[
        "cluster_id",
        "canonical_question",
        "topics",
        "topics_str",
        "topic_confidence",
    ]]


def enrich(base_dir: str, labels_jsonl: str | None = None) -> None:
    q_path = os.path.join(base_dir, "questions_with_clusters.csv")
    if not os.path.exists(q_path):
        raise SystemExit(f"Не найден {q_path}")

    if labels_jsonl:
        j_path = labels_jsonl if os.path.isabs(labels_jsonl) else os.path.join(base_dir, labels_jsonl)
    else:
        j_path = _find_latest_labels_jsonl(base_dir)

    df_questions = pd.read_csv(q_path)
    df_labels = _load_labels_jsonl(j_path)

    # Merge by cluster_id (left join keeps all questions)
    enriched = df_questions.merge(df_labels, on="cluster_id", how="left")

    # Save enriched questions
    enriched_out = os.path.join(base_dir, "enriched_questions.csv")
    enriched.to_csv(enriched_out, index=False)
    print(f"Saved: {enriched_out}")

    # Top topics by unique interviews
    topics_exploded = enriched.explode("topics")
    topics_exploded = topics_exploded.dropna(subset=["topics"])  # drop rows where topics is NaN after explode
    if not topics_exploded.empty:
        top_topics = (
            topics_exploded
            .drop_duplicates(subset=["interview_id", "topics"])  # count topic once per interview
            .groupby("topics")["interview_id"].nunique()
            .reset_index(name="interviews_count")
            .sort_values("interviews_count", ascending=False)
        )
    else:
        top_topics = pd.DataFrame(columns=["topics", "interviews_count"])  # empty but with columns
    top_topics_out = os.path.join(base_dir, "top_topics_enriched.csv")
    top_topics.to_csv(top_topics_out, index=False)
    print(f"Saved: {top_topics_out}")

    # Top clusters (by unique interviews and companies)
    if "company_norm" not in enriched.columns:
        # Backward compatibility: try to derive from company
        enriched["company_norm"] = (enriched.get("company") or enriched.get("company_norm") or "").astype(str)
    top_clusters = (
        enriched
        .groupby(["cluster_id", "canonical_question"], dropna=False)
        .agg(interviews_count=("interview_id", "nunique"),
             company_count=("company_norm", "nunique"))
        .reset_index()
        .sort_values(["interviews_count", "company_count"], ascending=False)
    )
    top_clusters_out = os.path.join(base_dir, "top_clusters_enriched.csv")
    top_clusters.to_csv(top_clusters_out, index=False)
    print(f"Saved: {top_clusters_out}")


def main():
    parser = argparse.ArgumentParser(description="Enrich clustered questions with labels and build simple reports")
    parser.add_argument("--base", default="sobes-data/analysis/outputs_mini", help="Базовая директория с outputs")
    parser.add_argument("--jsonl", default="", help="Имя/путь JSONL с лейблами (по умолчанию берём последний labels_*.jsonl в base)")
    args = parser.parse_args()

    enrich(base_dir=args.base, labels_jsonl=(args.jsonl or None))


if __name__ == "__main__":
    main()


