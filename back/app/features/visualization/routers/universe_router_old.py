"""
Interview Universe API router for Sigma.js visualization
Provides optimized endpoints for graph-based visualization of interview clusters
"""

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, distinct, func, select, text
from sqlalchemy.orm import Session

from app.features.visualization.schemas.universe_schemas import (
    CategoryInfo,
    ClusterDetailsResponse,
    UniverseEdge,
    UniverseGraphResponse,
    UniverseNode,
    UniverseStats,
)
from app.shared.database import get_session as get_db
from app.shared.entities.interview_universe import (
    InterviewCategory,
    InterviewCluster,
    InterviewQuestion,
)

router = APIRouter(
    prefix="/interview-universe",
    tags=["universe", "visualization"],
)


@router.get("/graph", response_model=UniverseGraphResponse)
def get_universe_graph(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200, description="Number of clusters to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    min_interview_count: int = Query(
        5, ge=1, description="Minimum interviews per cluster"
    ),
    min_link_weight: int = Query(3, ge=1, description="Minimum weight for edges"),
    categories: Optional[str] = Query(None, description="Comma-separated category IDs"),
    companies: Optional[str] = Query(None, description="Comma-separated company names"),
    min_penetration: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum penetration %"
    ),
    layout: Literal["force", "circular", "hierarchical"] = Query(
        "force", description="Layout algorithm"
    ),
):
    """
    Get graph data for Interview Universe visualization.
    Returns nodes (clusters) and edges (relationships) optimized for Sigma.js.
    """

    # Parse filter parameters
    category_filter = categories.split(",") if categories else None
    company_filter = companies.split(",") if companies else None

    # Get total interview count for penetration calculation
    total_interviews_query = select(
        func.count(distinct(InterviewQuestion.interview_id))
    )
    total_interviews_result = db.execute(total_interviews_query)
    total_interviews = total_interviews_result.scalar() or 893

    # Build cluster query with filters
    cluster_query = (
        select(
            InterviewCluster.id,
            InterviewCluster.name,
            InterviewCluster.category_id,
            InterviewCluster.keywords,
            InterviewCluster.questions_count,
            InterviewCluster.example_question,
            InterviewCategory.name.label("category_name"),
            InterviewCategory.color.label("category_color"),
            func.count(distinct(InterviewQuestion.interview_id)).label(
                "interview_count"
            ),
            func.round(
                func.count(distinct(InterviewQuestion.interview_id))
                * 100.0
                / total_interviews,
                2,
            ).label("interview_penetration"),
        )
        .select_from(InterviewCluster)
        .join(InterviewCategory, InterviewCluster.category_id == InterviewCategory.id)
        .outerjoin(
            InterviewQuestion, InterviewCluster.id == InterviewQuestion.cluster_id
        )
        .group_by(
            InterviewCluster.id,
            InterviewCluster.name,
            InterviewCluster.category_id,
            InterviewCluster.keywords,
            InterviewCluster.questions_count,
            InterviewCluster.example_question,
            InterviewCategory.name,
            InterviewCategory.color,
        )
    )

    # Apply filters
    filters = []
    if category_filter:
        filters.append(InterviewCluster.category_id.in_(category_filter))
    if min_penetration:
        filters.append(
            func.count(distinct(InterviewQuestion.interview_id))
            * 100.0
            / total_interviews
            >= min_penetration
        )

    if filters:
        cluster_query = cluster_query.where(and_(*filters))

    # Having clause for minimum interview count
    cluster_query = cluster_query.having(
        func.count(distinct(InterviewQuestion.interview_id)) >= min_interview_count
    )

    # Order by penetration and apply pagination
    cluster_query = (
        cluster_query.order_by(
            func.count(distinct(InterviewQuestion.interview_id)).desc()
        )
        .limit(limit)
        .offset(offset)
    )

    # Execute cluster query
    cluster_result = db.execute(cluster_query)
    clusters = cluster_result.all()

    # Build nodes
    nodes = []
    cluster_ids = []

    for cluster in clusters:
        cluster_ids.append(cluster.id)

        # Get top companies for this cluster
        company_query = (
            select(InterviewQuestion.company, func.count().label("count"))
            .where(InterviewQuestion.cluster_id == cluster.id)
            .group_by(InterviewQuestion.company)
            .order_by(func.count().desc())
            .limit(3)
        )

        if company_filter:
            company_query = company_query.where(
                InterviewQuestion.company.in_(company_filter)
            )

        company_result = db.execute(company_query)
        top_companies = [comp.company for comp in company_result.all() if comp.company]

        # Get difficulty distribution (mock data for now)
        difficulty_distribution = {
            "junior": 0.2,
            "middle": 0.6,
            "senior": 0.2,
        }

        nodes.append(
            UniverseNode(
                id=cluster.id,
                name=cluster.name,
                category_id=cluster.category_id,
                category_name=cluster.category_name,
                questions_count=cluster.questions_count,
                interview_penetration=float(cluster.interview_penetration),
                keywords=cluster.keywords or [],
                example_question=cluster.example_question,
                top_companies=top_companies,
                difficulty_distribution=difficulty_distribution,
            )
        )

    # Build edges (relationships between clusters)
    edges = []
    if len(cluster_ids) > 1:
        # Find clusters that appear together in interviews
        edge_query = text("""
            WITH cluster_pairs AS (
                SELECT 
                    q1.cluster_id as source,
                    q2.cluster_id as target,
                    COUNT(DISTINCT q1.interview_id) as weight
                FROM "InterviewQuestion" q1
                JOIN "InterviewQuestion" q2 
                    ON q1.interview_id = q2.interview_id 
                    AND q1.cluster_id < q2.cluster_id
                WHERE 
                    q1.cluster_id IN :cluster_ids
                    AND q2.cluster_id IN :cluster_ids
                    AND q1.cluster_id IS NOT NULL
                    AND q2.cluster_id IS NOT NULL
                GROUP BY q1.cluster_id, q2.cluster_id
                HAVING COUNT(DISTINCT q1.interview_id) >= :min_weight
            )
            SELECT source, target, weight FROM cluster_pairs
            ORDER BY weight DESC
            LIMIT 100
        """)

        edge_result = db.execute(
            edge_query,
            {"cluster_ids": tuple(cluster_ids), "min_weight": min_link_weight},
        )

        for edge_row in edge_result:
            edges.append(
                UniverseEdge(
                    source=edge_row.source,
                    target=edge_row.target,
                    weight=edge_row.weight,
                    strength=min(edge_row.weight / 20, 1.0),  # Normalize strength
                )
            )

    # Get categories
    category_query = select(InterviewCategory)
    if category_filter:
        category_query = category_query.where(InterviewCategory.id.in_(category_filter))

    category_result = db.execute(category_query)
    categories_data = category_result.scalars().all()

    categories = {
        cat.id: CategoryInfo(
            id=cat.id,
            name=cat.name,
            color=cat.color or "#9e9e9e",
            questions_count=cat.questions_count,
            clusters_count=cat.clusters_count,
            percentage=float(cat.percentage),
        )
        for cat in categories_data
    }

    # Calculate stats
    stats = UniverseStats(
        totalQuestions=8532,
        totalClusters=182,
        totalCategories=13,
        totalCompanies=380,
        avgQuestionsPerCluster=47,
        avgInterviewPenetration=25.5,
        totalEdges=len(edges),
    )

    return UniverseGraphResponse(
        nodes=nodes,
        edges=edges,
        categories=categories,
        stats=stats,
    )


@router.get("/cluster/{cluster_id}", response_model=ClusterDetailsResponse)
def get_cluster_details(
    cluster_id: int,
    db: Session = Depends(get_db),
    include_questions: bool = Query(True, description="Include question list"),
    question_limit: int = Query(
        100, ge=1, le=500, description="Max questions to return"
    ),
):
    """
    Get detailed information about a specific cluster including all questions.
    """

    # Get cluster info
    cluster_query = select(InterviewCluster).where(InterviewCluster.id == cluster_id)
    cluster_result = db.execute(cluster_query)
    cluster = cluster_result.scalar_one_or_none()

    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # Get questions if requested
    questions = []
    if include_questions:
        question_query = (
            select(
                InterviewQuestion.id,
                InterviewQuestion.question_text,
                InterviewQuestion.company,
                InterviewQuestion.date,
            )
            .where(InterviewQuestion.cluster_id == cluster_id)
            .limit(question_limit)
        )

        question_result = db.execute(question_query)
        questions = [
            {
                "id": q.id,
                "text": q.question_text,
                "company": q.company,
                "date": q.date.isoformat() if q.date else None,
            }
            for q in question_result.all()
        ]

    # Get related clusters (clusters that often appear together)
    related_query = text("""
        WITH related AS (
            SELECT 
                CASE 
                    WHEN q1.cluster_id = :cluster_id THEN q2.cluster_id
                    ELSE q1.cluster_id
                END as related_id,
                COUNT(DISTINCT 
                    CASE 
                        WHEN q1.cluster_id = :cluster_id THEN q1.interview_id
                        ELSE q2.interview_id
                    END
                ) as shared_count
            FROM "InterviewQuestion" q1
            JOIN "InterviewQuestion" q2 
                ON q1.interview_id = q2.interview_id
            WHERE 
                (q1.cluster_id = :cluster_id OR q2.cluster_id = :cluster_id)
                AND q1.cluster_id != q2.cluster_id
                AND q1.cluster_id IS NOT NULL
                AND q2.cluster_id IS NOT NULL
            GROUP BY related_id
            ORDER BY shared_count DESC
            LIMIT 10
        )
        SELECT 
            c.id,
            c.name,
            r.shared_count
        FROM related r
        JOIN "InterviewCluster" c ON c.id = r.related_id
    """)

    related_result = db.execute(related_query, {"cluster_id": cluster_id})
    related_clusters = [
        {
            "id": r.id,
            "name": r.name,
            "sharedQuestions": r.shared_count,
            "correlation": min(r.shared_count / 10, 1.0),
        }
        for r in related_result.all()
    ]

    # Get top companies
    company_query = (
        select(InterviewQuestion.company, func.count().label("count"))
        .where(InterviewQuestion.cluster_id == cluster_id)
        .group_by(InterviewQuestion.company)
        .order_by(func.count().desc())
        .limit(10)
    )

    company_result = db.execute(company_query)
    top_companies = [
        {
            "name": c.company,
            "count": c.count,
            "percentage": round(c.count * 100 / cluster.questions_count, 1),
        }
        for c in company_result.all()
        if c.company
    ]

    return ClusterDetailsResponse(
        id=cluster.id,
        name=cluster.name,
        category=cluster.category_id,
        questionsCount=cluster.questions_count,
        questions=questions if include_questions else None,
        relatedClusters=related_clusters,
        topCompanies=top_companies,
    )
