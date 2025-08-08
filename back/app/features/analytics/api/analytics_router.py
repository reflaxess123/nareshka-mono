from __future__ import annotations

import csv
import os
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Query


router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_out_dir() -> str:
    # back/app/features/analytics/api/analytics_router.py → repo root
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
    out_dir = os.path.join(repo_root, "sobes-analysis", "out")
    if not os.path.isdir(out_dir):
        raise HTTPException(status_code=500, detail=f"Out directory not found: {out_dir}")
    return out_dir


_CSV_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


def read_csv(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"File not found: {os.path.basename(path)}")
    # Cache by mtime to avoid re-reading for every request
    try:
        mtime = os.path.getmtime(path)
    except Exception:
        mtime = -1.0
    cache_entry = _CSV_CACHE.get(path)
    if cache_entry and cache_entry[0] == mtime:
        return cache_entry[1]
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(row) for row in reader]
    _CSV_CACHE[path] = (mtime, rows)
    return rows


def read_questions() -> List[Dict[str, Any]]:
    out_dir = get_out_dir()
    path = os.path.join(out_dir, "questions_with_clusters.csv")
    return read_csv(path)


# ==== Pydantic models for OpenAPI typings ====
class TopicRowModel(BaseModel):
    cluster_id: str
    cluster_label: str
    count: int
    companies: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None


class CompanyProfileRowModel(BaseModel):
    company: str
    rank: int
    cluster_id: str
    cluster_label: str
    count: int
    share: Optional[float] = None


class TrendRowModel(BaseModel):
    month: str
    cluster_label: str
    count: int


class CooccurrenceRowModel(BaseModel):
    cluster_label_a: str
    cluster_label_b: str
    count: int


class DuplicateRowModel(BaseModel):
    row_id_1: str
    row_id_2: str
    sim_embed: float
    sim_char: float
    id_1: str
    question_text_1: str
    company_1: str
    date_1: str
    id_2: str
    question_text_2: str
    company_2: str
    date_2: str


class CompanyCountModel(BaseModel):
    company: str
    count: int


class QuestionFrequencyRowModel(BaseModel):
    question_text: str
    total_count: int
    companies: List[CompanyCountModel]


class CompanyQuestionItemModel(BaseModel):
    question_text: str
    count: int


class CompanyQuestionsRowModel(BaseModel):
    company: str
    total_questions: int
    items: List[CompanyQuestionItemModel]


class HeatmapResponseModel(BaseModel):
    companies: List[str]
    topics: List[str]
    values: List[List[float]]


class TopQuestionExtendedRowModel(BaseModel):
    question_text: str
    total_count: int
    normalized_score: float
    unique_companies: int


class TopicTopRowModel(BaseModel):
    cluster_label: str
    total_count: int
    normalized_score: float
    company_count: int


class CompanyDiversityRowModel(BaseModel):
    company: str
    total_count: int
    distinct_topics: int
    entropy: float


class SimilarCompanyItemModel(BaseModel):
    company: str
    similarity: float


class CompanySimilarResponseModel(BaseModel):
    company: str
    similar: List[SimilarCompanyItemModel]


@router.get("/topics", response_model=List[TopicRowModel])
def get_topics(limit: int = Query(100, ge=1, le=1000)) -> List[Dict[str, Any]]:
    out_dir = get_out_dir()
    rows = read_csv(os.path.join(out_dir, "cluster_stats.csv"))
    # cluster_id,cluster_label,count,companies,first_seen,last_seen
    for r in rows:
        try:
            r["count"] = int(r.get("count", 0))
        except Exception:
            r["count"] = 0
        # rank не нужен здесь
    rows.sort(key=lambda r: r.get("count", 0), reverse=True)
    return rows[:limit]


@router.get("/company-profiles", response_model=List[CompanyProfileRowModel])
def get_company_profiles(company: Optional[str] = None, top: int = Query(10, ge=1, le=50)) -> List[Dict[str, Any]]:
    out_dir = get_out_dir()
    rows = read_csv(os.path.join(out_dir, "company_profiles_top.csv"))
    # company,rank,cluster_id,cluster_label,count,share
    if company:
        rows = [r for r in rows if r.get("company") == company]
    # Ensure rank limit per company
    result: List[Dict[str, Any]] = []
    by_company: Dict[str, int] = {}
    for r in rows:
        c = r.get("company", "")
        # Cast numeric fields
        try:
            r["rank"] = int(r.get("rank", 0))
        except Exception:
            r["rank"] = 0
        try:
            r["count"] = int(r.get("count", 0))
        except Exception:
            r["count"] = 0
        try:
            r["share"] = float(r.get("share", 0)) if r.get("share") not in (None, "") else None
        except Exception:
            r["share"] = None
        by_company[c] = by_company.get(c, 0) + 1
        if by_company[c] <= top:
            result.append(r)
    return result


@router.get("/trends", response_model=List[TrendRowModel])
def get_trends(limit: int = Query(10000, ge=1)) -> List[Dict[str, Any]]:
    out_dir = get_out_dir()
    rows = read_csv(os.path.join(out_dir, "topic_trends_monthly.csv"))
    # month,cluster_label,count
    for r in rows:
        try:
            r["count"] = int(r.get("count", 0))
        except Exception:
            r["count"] = 0
    return rows[:limit]


@router.get("/cooccurrence", response_model=List[CooccurrenceRowModel])
def get_cooccurrence(limit: int = Query(500, ge=1)) -> List[Dict[str, Any]]:
    out_dir = get_out_dir()
    rows = read_csv(os.path.join(out_dir, "topic_cooccurrence.csv"))
    # cluster_label_a,cluster_label_b,count
    for r in rows:
        try:
            r["count"] = int(r.get("count", 0))
        except Exception:
            r["count"] = 0
    rows.sort(key=lambda r: r.get("count", 0), reverse=True)
    return rows[:limit]


@router.get("/duplicates", response_model=List[DuplicateRowModel])
def get_duplicates(limit: int = Query(500, ge=1, le=5000)) -> List[Dict[str, Any]]:
    out_dir = get_out_dir()
    rows = read_csv(os.path.join(out_dir, "duplicates.csv"))
    # row_id_1,row_id_2,sim_embed,sim_char,id_1,question_text_1,company_1,date_1,id_2,question_text_2,company_2,date_2
    # Sort by sim_embed desc
    for r in rows:
        try:
            r["sim_embed"] = float(r.get("sim_embed", 0))
        except Exception:
            r["sim_embed"] = 0.0
        try:
            r["sim_char"] = float(r.get("sim_char", 0))
        except Exception:
            r["sim_char"] = 0.0
    rows.sort(key=lambda r: r.get("sim_embed", 0.0), reverse=True)
    return rows[:limit]


@router.get("/heatmap", response_model=HeatmapResponseModel)
def get_heatmap(normalization: str = Query("row", regex="^(none|row|col)$")) -> Dict[str, Any]:
    """
    Return heatmap matrix derived from company_cluster_counts.csv
    normalization: none|row|col
    Output: { companies: [...], topics: [...], values: [[...]] }
    """
    out_dir = get_out_dir()
    rows = read_csv(os.path.join(out_dir, "company_cluster_counts.csv"))
    # Build pivot: company x cluster_label -> count
    companies: List[str] = sorted(list({r["company"] for r in rows}))
    topics: List[str] = sorted(list({r["cluster_label"] for r in rows}))
    topic_index = {t: i for i, t in enumerate(topics)}
    company_index = {c: i for i, c in enumerate(companies)}
    values: List[List[float]] = [[0.0 for _ in topics] for _ in companies]
    for r in rows:
        c = r["company"]
        t = r["cluster_label"]
        try:
            count = float(r.get("count", 0))
        except Exception:
            count = 0.0
        values[company_index[c]][topic_index[t]] = count

    if normalization == "row":
        for i in range(len(values)):
            s = sum(values[i])
            values[i] = [v / s if s > 0 else 0.0 for v in values[i]]
    elif normalization == "col":
        for j in range(len(topics)):
            s = sum(values[i][j] for i in range(len(companies)))
            for i in range(len(companies)):
                values[i][j] = (values[i][j] / s) if s > 0 else 0.0

    return {"companies": companies, "topics": topics, "values": values}


@router.get("/questions-frequencies", response_model=List[QuestionFrequencyRowModel])
def get_questions_frequencies(
    min_count: int = Query(1, ge=1),
    limit: int = Query(1000, ge=1, le=20000),
    question_contains: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """
    Aggregate by exact question_text. Output rows sorted by total_count desc:
    [{ question_text, total_count, companies: [{ company, count }] }]
    """
    rows = read_questions()
    # When called internally (not via FastAPI), question_contains may be a Query object
    if not isinstance(question_contains, (str, type(None))):
        question_contains = None
    if isinstance(question_contains, str) and question_contains:
        q = question_contains.lower()
        rows = [r for r in rows if q in str(r.get("question_text", "")).lower()]

    agg: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        question = r.get("question_text", "").strip()
        company = r.get("company", "").strip()
        if not question:
            continue
        entry = agg.setdefault(question, {"question_text": question, "total_count": 0, "companies": {}})
        entry["total_count"] += 1
        entry["companies"][company] = entry["companies"].get(company, 0) + 1

    result: List[Dict[str, Any]] = []
    for question, data in agg.items():
        if data["total_count"] < min_count:
            continue
        companies_list = [
            {"company": c, "count": cnt} for c, cnt in sorted(data["companies"].items(), key=lambda x: x[1], reverse=True)
        ]
        result.append({"question_text": question, "total_count": data["total_count"], "companies": companies_list})

    result.sort(key=lambda x: x["total_count"], reverse=True)
    return result[:limit]


@router.get("/top-questions", response_model=List[QuestionFrequencyRowModel])
def get_top_questions(limit: int = Query(200, ge=1, le=10000), min_count: int = Query(2, ge=1)) -> List[Dict[str, Any]]:
    rows = get_questions_frequencies(min_count=min_count, limit=10_000)
    return rows[:limit]


@router.get("/companies-questions", response_model=List[CompanyQuestionsRowModel])
def get_companies_questions(
    company: Optional[str] = Query(None),
    min_count: int = Query(1, ge=1),
    limit_per_company: int = Query(500, ge=1, le=10000),
) -> List[Dict[str, Any]]:
    """
    Return per-company list of questions with counts:
    [{ company, total_questions, items: [{ question_text, count }] }]
    """
    rows = read_questions()

    by_company: Dict[str, Dict[str, int]] = {}
    for r in rows:
        c = str(r.get("company", "")).strip()
        q = str(r.get("question_text", "")).strip()
        if not c or not q:
            continue
        if company and c != company:
            continue
        by_company.setdefault(c, {})
        by_company[c][q] = by_company[c].get(q, 0) + 1

    result: List[Dict[str, Any]] = []
    for c, qmap in by_company.items():
        items = [{"question_text": q, "count": cnt} for q, cnt in qmap.items() if cnt >= min_count]
        items.sort(key=lambda x: x["count"], reverse=True)
        result.append({"company": c, "total_questions": sum(i["count"] for i in items), "items": items[:limit_per_company]})

    result.sort(key=lambda r: r["company"])  # alphabetical
    return result


@router.get("/top-questions-extended", response_model=List[TopQuestionExtendedRowModel])
def get_top_questions_extended(limit: int = Query(100, ge=1, le=1000), min_count: int = Query(1, ge=1)) -> List[Dict[str, Any]]:
    """
    Compute absolute and normalized score for each exact question_text.
    Normalized score is sum over companies of (count(question, company) / total_questions_in_company).
    """
    rows = read_questions()
    # company totals
    totals_by_company: Dict[str, int] = {}
    for r in rows:
        c = str(r.get("company", "")).strip()
        if not c:
            continue
        totals_by_company[c] = totals_by_company.get(c, 0) + 1

    # question -> company -> count
    q_map: Dict[str, Dict[str, int]] = {}
    for r in rows:
        q = str(r.get("question_text", "")).strip()
        c = str(r.get("company", "")).strip()
        if not q or not c:
            continue
        m = q_map.setdefault(q, {})
        m[c] = m.get(c, 0) + 1

    result: List[Dict[str, Any]] = []
    for q, cmap in q_map.items():
        total = sum(cmap.values())
        if total < min_count:
            continue
        normalized = 0.0
        for c, cnt in cmap.items():
            denom = totals_by_company.get(c, 0) or 1
            normalized += cnt / float(denom)
        result.append(
            {
                "question_text": q,
                "total_count": total,
                "normalized_score": normalized,
                "unique_companies": len(cmap),
            }
        )

    result.sort(key=lambda x: (x["normalized_score"], x["total_count"]), reverse=True)
    return result[:limit]


@router.get("/topics-top", response_model=List[TopicTopRowModel])
def get_topics_top(limit: int = Query(50, ge=1, le=1000)) -> List[Dict[str, Any]]:
    """
    Top topics by absolute count and normalized score (sum over companies of count/company_total).
    """
    out_dir = get_out_dir()
    rows = read_csv(os.path.join(out_dir, "company_cluster_counts.csv"))

    # company totals
    totals_by_company: Dict[str, int] = {}
    for r in rows:
        c = r["company"]
        try:
            cnt = int(r.get("count", 0))
        except Exception:
            cnt = 0
        totals_by_company[c] = totals_by_company.get(c, 0) + cnt

    # topic aggregates
    agg: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        t = r["cluster_label"]
        c = r["company"]
        try:
            cnt = int(r.get("count", 0))
        except Exception:
            cnt = 0
        a = agg.setdefault(t, {"total_count": 0, "normalized_score": 0.0, "company_count": 0})
        a["total_count"] += cnt
        if cnt > 0:
            a["company_count"] += 1
            denom = totals_by_company.get(c, 0) or 1
            a["normalized_score"] += cnt / float(denom)

    rows_out: List[Dict[str, Any]] = []
    for t, a in agg.items():
        rows_out.append(
            {
                "cluster_label": t,
                "total_count": int(a["total_count"]),
                "normalized_score": float(a["normalized_score"]),
                "company_count": int(a["company_count"]),
            }
        )

    rows_out.sort(key=lambda x: (x["normalized_score"], x["total_count"]), reverse=True)
    return rows_out[:limit]


@router.get("/company-diversity", response_model=List[CompanyDiversityRowModel])
def get_company_diversity(top: int = Query(50, ge=1, le=1000), order: str = Query("entropy", regex="^(entropy|distinct|total)$")) -> List[Dict[str, Any]]:
    """
    Compute per-company diversity of topics using entropy and distinct topic count.
    """
    import math

    out_dir = get_out_dir()
    rows = read_csv(os.path.join(out_dir, "company_cluster_counts.csv"))

    by_company: Dict[str, Dict[str, int]] = {}
    for r in rows:
        c = r["company"]
        t = r["cluster_label"]
        try:
            cnt = int(r.get("count", 0))
        except Exception:
            cnt = 0
        if cnt <= 0:
            continue
        m = by_company.setdefault(c, {})
        m[t] = m.get(t, 0) + cnt

    result: List[Dict[str, Any]] = []
    for c, tmap in by_company.items():
        total = sum(tmap.values())
        if total <= 0:
            continue
        probs = [v / float(total) for v in tmap.values()]
        entropy = -sum(p * math.log(p, 2) for p in probs if p > 0)
        result.append(
            {
                "company": c,
                "total_count": total,
                "distinct_topics": len(tmap),
                "entropy": float(entropy),
            }
        )

    if order == "entropy":
        result.sort(key=lambda x: (x["entropy"], x["distinct_topics"]), reverse=True)
    elif order == "distinct":
        result.sort(key=lambda x: (x["distinct_topics"], x["total_count"]), reverse=True)
    else:
        result.sort(key=lambda x: x["total_count"], reverse=True)

    return result[:top]


@router.get("/companies-similar", response_model=CompanySimilarResponseModel)
def get_companies_similar(company: str = Query(...), top: int = Query(10, ge=1, le=100)) -> Dict[str, Any]:
    """
    Find companies most similar by topic distribution (cosine similarity on company x topic counts).
    """
    from math import sqrt

    out_dir = get_out_dir()
    rows = read_csv(os.path.join(out_dir, "company_cluster_counts.csv"))

    # Build topic set and company vectors
    topics = sorted({r["cluster_label"] for r in rows})
    topic_index = {t: i for i, t in enumerate(topics)}
    vectors: Dict[str, List[float]] = {}
    for r in rows:
        c = r["company"]
        v = vectors.setdefault(c, [0.0] * len(topics))
        try:
            cnt = float(r.get("count", 0))
        except Exception:
            cnt = 0.0
        v[topic_index[r["cluster_label"]]] += cnt

    if company not in vectors:
        raise HTTPException(status_code=404, detail=f"Company not found: {company}")

    def cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = sqrt(sum(x * x for x in a))
        nb = sqrt(sum(y * y for y in b))
        return (dot / (na * nb)) if na > 0 and nb > 0 else 0.0

    base = vectors[company]
    sims: List[Dict[str, Any]] = []
    for c, v in vectors.items():
        if c == company:
            continue
        sims.append({"company": c, "similarity": float(cosine(base, v))})

    sims.sort(key=lambda x: x["similarity"], reverse=True)
    return {"company": company, "similar": sims[:top]}
