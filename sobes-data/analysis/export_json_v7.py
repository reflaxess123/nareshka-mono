import argparse
import json
import os
import re
from typing import Dict, List

import pandas as pd


def slugify_company(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\-_.]+", "", s)
    return s or "unknown"


def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def load_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


def export_json(base: str, out_dir: str) -> List[str]:
    written: List[str] = []
    ensure_dir(out_dir)

    # Core inputs
    enr = load_csv(os.path.join(base, "enriched_questions_fixed.csv"))
    topics_q = load_csv(os.path.join(base, "topics_by_questions_fixed.csv"))
    topics_i = load_csv(os.path.join(base, "top_topics_fixed.csv"))
    top_clusters_q = load_csv(os.path.join(base, "top_clusters_by_questions_fixed.csv"))
    top_clusters = load_csv(os.path.join(base, "top_clusters_fixed.csv"))
    by_company_topics = load_csv(os.path.join(base, "topics_by_company_fixed.csv"))
    by_company_clusters = load_csv(os.path.join(base, "company_top_clusters_fixed.csv"))
    pivot_ct = load_csv(os.path.join(base, "company_topic_pivot.csv"))

    # Metrics
    total_questions = int(len(enr)) if not enr.empty else 0
    total_interviews = int(enr["interview_id"].nunique()) if not enr.empty else 0
    total_companies = int(enr["company_norm"].nunique()) if not enr.empty else 0
    metrics = {
        "version": os.path.basename(base),
        "total_questions": total_questions,
        "total_interviews": total_interviews,
        "total_companies": total_companies,
    }
    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    written.append("metrics.json")

    # Themes volume (by questions)
    if not topics_q.empty:
        total_q = int(topics_q["questions_count"].sum())
        tv = topics_q.copy()
        tv["share"] = tv["questions_count"].astype(float) / (total_q or 1)
        data = tv.rename(columns={"topics": "topic"}).to_dict(orient="records")
        with open(os.path.join(out_dir, "themes_volume.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        written.append("themes_volume.json")

    # Themes coverage (by interviews)
    if not topics_i.empty and not enr.empty:
        total_iv = int(enr["interview_id"].nunique())
        tc = topics_i.copy()
        tc["share"] = tc["interviews_count"].astype(float) / (total_iv or 1)
        data = tc.rename(columns={"topics": "topic"}).to_dict(orient="records")
        with open(os.path.join(out_dir, "themes_coverage.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        written.append("themes_coverage.json")

    # Top questions by questions_count (enrich with interviews/company counts if present)
    if not top_clusters_q.empty:
        tcq = top_clusters_q.copy()
        # optional enrich
        if not top_clusters.empty:
            tcq = tcq.merge(
                top_clusters[["cluster_id", "interviews_count", "company_count"]],
                on="cluster_id",
                how="left",
            )
        data = tcq.to_dict(orient="records")
        with open(os.path.join(out_dir, "top_questions.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        written.append("top_questions.json")

    # Companies index
    companies_index: List[Dict] = []
    if not enr.empty:
        iv_by_company = enr.groupby("company_norm")["interview_id"].nunique().sort_values(ascending=False)
        # top topics per company (rank up to 3)
        top_topics_by_company = {}
        if not by_company_topics.empty:
            for company, g in by_company_topics.groupby("company_norm"):
                g_sorted = g.sort_values(["rank", "interviews_count"], ascending=[True, False])
                top_topics_by_company[company] = g_sorted.head(3)[["topics", "interviews_count", "share", "rank"]].rename(columns={
                    "topics": "topic"
                }).to_dict(orient="records")
        # top question per company
        top_q_by_company = {}
        if not by_company_clusters.empty:
            for company, g in by_company_clusters.groupby("company_norm"):
                g_sorted = g.sort_values(["rank", "interviews_count"], ascending=[True, False])
                row = g_sorted.head(1)
                if not row.empty:
                    r = row.iloc[0]
                    top_q_by_company[company] = {
                        "cluster_id": int(r["cluster_id"]),
                        "canonical_question": str(r["canonical_question"]),
                        "interviews_count": int(r["interviews_count"]),
                        "share": float(r.get("share", 0.0)),
                        "rank": int(r.get("rank", 1)),
                    }
        for company, cnt in iv_by_company.items():
            companies_index.append({
                "company_norm": company,
                "slug": slugify_company(company),
                "interviews": int(cnt),
                "top_topics": top_topics_by_company.get(company, []),
                "top_question": top_q_by_company.get(company),
            })
    with open(os.path.join(out_dir, "companies_index.json"), "w", encoding="utf-8") as f:
        json.dump(companies_index, f, ensure_ascii=False, indent=2)
    written.append("companies_index.json")

    # Per-company JSON
    comp_dir = os.path.join(out_dir, "company")
    ensure_dir(comp_dir)
    if not companies_index:
        companies_index = []
    # Build quick lookups
    topics_by_comp = {}
    if not by_company_topics.empty:
        for company, g in by_company_topics.groupby("company_norm"):
            topics_by_comp[company] = g.sort_values(["rank", "interviews_count"], ascending=[True, False])["topics"].tolist()
    if not by_company_topics.empty:
        topics_rows = by_company_topics
    else:
        topics_rows = pd.DataFrame(columns=["company_norm", "topics", "interviews_count", "share", "rank"])
    if not by_company_clusters.empty:
        clusters_rows = by_company_clusters
    else:
        clusters_rows = pd.DataFrame(columns=["company_norm", "cluster_id", "canonical_question", "interviews_count", "share", "rank"])
    for ci in companies_index:
        company = ci["company_norm"]
        slug = ci["slug"]
        topics_list = topics_rows[topics_rows["company_norm"] == company]
        clusters_list = clusters_rows[clusters_rows["company_norm"] == company]
        payload = {
            "company_norm": company,
            "slug": slug,
            "interviews": ci["interviews"],
            "topics": topics_list.rename(columns={"topics": "topic"}).to_dict(orient="records"),
            "questions": clusters_list.to_dict(orient="records"),
        }
        path = os.path.join(comp_dir, f"{slug}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        written.append(os.path.join("company", f"{slug}.json"))

    # Per-cluster JSON (basic + examples)
    cl_dir = os.path.join(out_dir, "cluster")
    ensure_dir(cl_dir)
    if not top_clusters.empty:
        # Build examples map from enriched
        examples_map: Dict[int, List[str]] = {}
        if not enr.empty:
            for cid, g in enr.groupby("cluster_id"):
                examples_map[int(cid)] = g["question_text"].astype(str).head(20).tolist()
        for _, row in top_clusters.iterrows():
            cid = int(row["cluster_id"])
            payload = {
                "cluster_id": cid,
                "canonical_question": str(row["canonical_question"]),
                "interviews_count": int(row["interviews_count"]),
                "company_count": int(row["company_count"]),
                "examples": examples_map.get(cid, []),
            }
            path = os.path.join(cl_dir, f"{cid}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            written.append(os.path.join("cluster", f"{cid}.json"))

    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Папка с CSV (outputs_mini_vX)")
    ap.add_argument("--out", default=None, help="Куда писать JSON (по умолчанию base/json)")
    args = ap.parse_args()
    out = args.out or os.path.join(args.base, "json")
    files = export_json(args.base, out)
    print("Written:")
    for p in files:
        print(" -", p)


if __name__ == "__main__":
    main()


