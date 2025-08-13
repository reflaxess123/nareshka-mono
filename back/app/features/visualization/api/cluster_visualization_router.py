"""
Cluster Visualization API Router (feature: visualization)
Endpoints для визуализации кластеров в виде созвездий
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from app.shared.database import get_session
from app.shared.dependencies import get_current_user_optional


class ClusterNode(BaseModel):
    id: int
    name: str
    category_id: str
    category_name: str
    questions_count: int
    interview_penetration: float
    keywords: List[str]
    example_question: str
    size: float
    top_companies: List[str]
    difficulty_distribution: Dict[str, float]

class ClusterLink(BaseModel):
    source: int
    target: int
    weight: int
    strength: float

class ClusterConstellationResponse(BaseModel):
    nodes: List[ClusterNode]
    links: List[ClusterLink]
    categories: Dict[str, str]
    stats: Dict[str, Any]


router = APIRouter(
    prefix="/cluster-visualization",
    tags=["visualization"],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/constellation",
    response_model=ClusterConstellationResponse,
    summary="Получить данные для визуализации созвездия кластеров",
    description="Возвращает узлы и связи для D3.js / ReactFlow графа"
)
async def get_cluster_constellation(
    min_interview_count: int = Query(5, description="Минимальное количество интервью для кластера"),
    min_link_weight: int = Query(3, description="Минимальный вес связи для отображения"),
    category_filter: List[str] | None = Query(default=None, description="Фильтр по категориям"),
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user_optional)
):
    """Получение данных для визуализации созвездия кластеров"""
    # 1) Кластеры и их метрики
    cluster_query = text(
        """
        WITH total_interviews AS (
            SELECT COALESCE(NULLIF(COUNT(DISTINCT interview_id),0),1) AS total
            FROM "InterviewQuestion" WHERE interview_id IS NOT NULL
        ), cluster_stats AS (
            SELECT 
                c.id,
                c.name,
                c.category_id,
                cat.name as category_name,
                c.keywords,
                c.questions_count,
                c.example_question,
                COUNT(DISTINCT q.interview_id) as interview_count,
                ROUND(COUNT(DISTINCT q.interview_id) * 100.0 / (SELECT total FROM total_interviews), 2) as interview_penetration,
                ARRAY(
                    SELECT q2.company 
                    FROM "InterviewQuestion" q2
                    WHERE q2.cluster_id = c.id AND q2.company IS NOT NULL
                    GROUP BY q2.company 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 3
                ) as top_companies,
                COALESCE(ROUND(AVG(CASE WHEN ir.position ILIKE '%junior%' OR ir.position ILIKE '%стажер%' THEN 1.0 ELSE 0.0 END) * 100, 1),0) as junior_pct,
                COALESCE(ROUND(AVG(CASE WHEN ir.position ILIKE '%middle%' OR ir.position ILIKE '%средний%' THEN 1.0 ELSE 0.0 END) * 100, 1),0) as middle_pct,
                COALESCE(ROUND(AVG(CASE WHEN ir.position ILIKE '%senior%' OR ir.position ILIKE '%ведущий%' OR ir.position ILIKE '%тимлид%' THEN 1.0 ELSE 0.0 END) * 100, 1),0) as senior_pct
            FROM "InterviewCluster" c
            LEFT JOIN "InterviewQuestion" q ON c.id = q.cluster_id
            LEFT JOIN "InterviewRecord" ir ON q.interview_id = ir.id
            LEFT JOIN "InterviewCategory" cat ON c.category_id = cat.id
            WHERE (
                :no_filter = TRUE 
                OR c.category_id = ANY(:category_filter)
            )
            GROUP BY c.id, c.name, c.category_id, cat.name, c.keywords, c.questions_count, c.example_question
            HAVING COUNT(DISTINCT q.interview_id) >= :min_interview_count
        )
        SELECT * FROM cluster_stats
        ORDER BY interview_penetration DESC
        """
    )

    no_filter = category_filter is None or len(category_filter) == 0

    clusters_result = session.execute(
        cluster_query,
        {
            "min_interview_count": min_interview_count,
            "category_filter": category_filter if not no_filter else [],
            "no_filter": no_filter,
        }
    ).fetchall()

    # 2) Связи между кластерами (через пары из массива кластеров в интервью)
    links_query = text(
        """
        WITH base AS (
            SELECT interview_id, ARRAY_AGG(DISTINCT cluster_id) as clusters
            FROM "InterviewQuestion"
            WHERE interview_id IS NOT NULL AND cluster_id IS NOT NULL
            GROUP BY interview_id
        ), pairs AS (
            SELECT (clusters)[i] AS c1, (clusters)[j] AS c2
            FROM base,
            LATERAL generate_subscripts(clusters,1) i,
            LATERAL generate_subscripts(clusters,1) j
            WHERE i < j
        ), agg AS (
            SELECT c1, c2, COUNT(*) AS shared_interviews
            FROM pairs
            GROUP BY c1, c2
            HAVING COUNT(*) >= :min_link_weight
        )
        SELECT * FROM agg ORDER BY shared_interviews DESC
        """
    )

    links_result = session.execute(links_query, {"min_link_weight": min_link_weight}).fetchall()

    # 3) Формируем узлы
    nodes: List[ClusterNode] = []
    cluster_ids = set()
    max_questions = max([r.questions_count for r in clusters_result]) if clusters_result else 1
    for cluster in clusters_result:
        cluster_ids.add(cluster.id)
        nodes.append(ClusterNode(
            id=cluster.id,
            name=cluster.name,
            category_id=cluster.category_id,
            category_name=cluster.category_name,
            questions_count=cluster.questions_count,
            interview_penetration=float(cluster.interview_penetration),
            keywords=cluster.keywords if cluster.keywords else [],
            example_question=cluster.example_question or "",
            size=cluster.questions_count / max_questions,
            top_companies=cluster.top_companies if cluster.top_companies else [],
            difficulty_distribution={
                "junior": float(cluster.junior_pct),
                "middle": float(cluster.middle_pct),
                "senior": float(cluster.senior_pct)
            }
        ))

    # 4) Формируем связи
    links: List[ClusterLink] = []
    max_weight = max([l.shared_interviews for l in links_result]) if links_result else 1
    for link in links_result:
        if link.c1 in cluster_ids and link.c2 in cluster_ids:
            links.append(ClusterLink(
                source=link.c1,
                target=link.c2,
                weight=link.shared_interviews,
                strength=link.shared_interviews / max_weight
            ))

    # 5) Категории
    categories_rows = session.execute(text('SELECT id, name FROM "InterviewCategory"'))
    categories = {row.id: row.name for row in categories_rows}

    # 6) Статистика
    stats = {
        "total_clusters": len(nodes),
        "total_links": len(links),
        "avg_penetration": (sum(n.interview_penetration for n in nodes) / len(nodes)) if nodes else 0,
        "max_cluster_size": max([n.questions_count for n in nodes]) if nodes else 0,
        "strongest_link": max([l.weight for l in links]) if links else 0,
    }

    return ClusterConstellationResponse(nodes=nodes, links=links, categories=categories, stats=stats)


@router.get("/cluster/{cluster_id}/questions")
async def get_cluster_questions(
    cluster_id: int,
    session: Session = Depends(get_session)
):
    """Получение всех вопросов для кластера"""
    query = text(
        """
        SELECT 
            q.question_text,
            q.company,
            ir.position,
            ir.company_name,
            ir.interview_date,
            ir.duration_minutes,
            c.name as cluster_name,
            cat.name as category_name
        FROM "InterviewQuestion" q
        LEFT JOIN "InterviewRecord" ir ON q.interview_id = ir.id
        LEFT JOIN "InterviewCluster" c ON q.cluster_id = c.id
        LEFT JOIN "InterviewCategory" cat ON c.category_id = cat.id
        WHERE q.cluster_id = :cluster_id
        ORDER BY 
            CASE WHEN q.company IS NOT NULL THEN 0 ELSE 1 END,
            q.company ASC,
            q.question_text ASC
        LIMIT 500
        """
    )
    result = session.execute(query, {"cluster_id": cluster_id}).fetchall()
    if not result:
        return {"error": "Кластер не найден", "questions": []}

    cluster_name = result[0].cluster_name or "Неизвестный кластер"
    category_name = result[0].category_name or "Неизвестная категория"

    questions = []
    for row in result:
        questions.append({
            "question_text": row.question_text,
            "company": row.company,
            "position": row.position,
            "company_name": row.company_name,
            "interview_date": row.interview_date.isoformat() if row.interview_date else None,
            "duration_minutes": row.duration_minutes,
        })

    return {
        "cluster_id": cluster_id,
        "cluster_name": cluster_name,
        "category_name": category_name,
        "total_questions": len(questions),
        "questions": questions,
    }

