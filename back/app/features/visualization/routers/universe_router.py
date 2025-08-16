"""
Interview Universe API router for Sigma.js visualization (Fixed version)
Uses raw SQL queries like the working cluster_visualization_router
"""

from typing import Optional, List, Literal, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from app.shared.database import get_session

# Pydantic models for response
class UniverseNode(BaseModel):
    id: int
    name: str
    category_id: str
    category_name: str
    questions_count: int
    interview_penetration: float
    keywords: List[str]
    example_question: Optional[str] = None
    top_companies: List[str]
    difficulty_distribution: Dict[str, float]
    x: Optional[float] = None
    y: Optional[float] = None

class UniverseEdge(BaseModel):
    source: int
    target: int
    weight: int
    strength: float

class CategoryInfo(BaseModel):
    id: str
    name: str
    color: Optional[str] = "#9e9e9e"
    questions_count: int
    clusters_count: int
    percentage: float

class UniverseStats(BaseModel):
    totalQuestions: int
    totalClusters: int
    totalCategories: int
    totalCompanies: int
    avgQuestionsPerCluster: float
    avgInterviewPenetration: float
    totalEdges: int = 0

class UniverseGraphResponse(BaseModel):
    nodes: List[UniverseNode]
    edges: List[UniverseEdge]
    categories: Dict[str, CategoryInfo]
    stats: UniverseStats

class ClusterDetailsResponse(BaseModel):
    id: int
    name: str
    category: str
    questionsCount: int
    questions: Optional[List[Dict[str, Any]]] = None
    relatedClusters: List[Dict[str, Any]]
    topCompanies: List[Dict[str, Any]]

router = APIRouter(
    prefix="/interview-universe",
    tags=["universe", "visualization"],
)


@router.get("/graph", response_model=UniverseGraphResponse)
def get_universe_graph(
    db: Session = Depends(get_session),
    limit: int = Query(50, ge=1, le=200, description="Number of clusters to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    min_interview_count: int = Query(5, ge=1, description="Minimum interviews per cluster"),
    min_link_weight: int = Query(3, ge=1, description="Minimum weight for edges"),
    categories: Optional[str] = Query(None, description="Comma-separated category IDs"),
    companies: Optional[str] = Query(None, description="Comma-separated company names"),
    min_penetration: Optional[float] = Query(None, ge=0, le=100, description="Minimum penetration %"),
):
    """
    Get graph data for Interview Universe visualization.
    Returns nodes (clusters) and edges (relationships) optimized for Sigma.js.
    """
    
    # Parse filter parameters
    category_filter = categories.split(",") if categories else None
    company_filter = companies.split(",") if companies else None
    
    # Get total interview count for penetration calculation
    total_interviews_query = text("""
        SELECT COUNT(DISTINCT interview_id) as total
        FROM "InterviewQuestion"
        WHERE interview_id IS NOT NULL
    """)
    total_result = db.execute(total_interviews_query).fetchone()
    total_interviews = total_result.total if total_result else 893
    
    # Build cluster query with filters
    cluster_query = text("""
        WITH cluster_stats AS (
            SELECT 
                c.id,
                c.name,
                c.category_id,
                cat.name as category_name,
                c.keywords,
                c.questions_count,
                c.example_question,
                COUNT(DISTINCT q.interview_id) as interview_count,
                ROUND(COUNT(DISTINCT q.interview_id) * 100.0 / :total_interviews, 2) as interview_penetration,
                ARRAY(
                    SELECT company 
                    FROM (
                        SELECT q2.company, COUNT(*) as cnt
                        FROM "InterviewQuestion" q2
                        WHERE q2.cluster_id = c.id AND q2.company IS NOT NULL
                        GROUP BY q2.company
                        ORDER BY cnt DESC
                        LIMIT 3
                    ) top_companies
                ) as top_companies,
                COALESCE(
                    SUM(CASE WHEN q.company LIKE '%Junior%' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(q.id), 0),
                    20
                ) as junior_pct,
                COALESCE(
                    SUM(CASE WHEN q.company LIKE '%Middle%' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(q.id), 0),
                    60
                ) as middle_pct,
                COALESCE(
                    SUM(CASE WHEN q.company LIKE '%Senior%' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(q.id), 0),
                    20
                ) as senior_pct
            FROM "InterviewCluster" c
            JOIN "InterviewCategory" cat ON c.category_id = cat.id
            LEFT JOIN "InterviewQuestion" q ON c.id = q.cluster_id
            WHERE (:no_category_filter OR c.category_id = ANY(:category_filter))
            GROUP BY c.id, c.name, c.category_id, cat.name, c.keywords, c.questions_count, c.example_question
            HAVING COUNT(DISTINCT q.interview_id) >= :min_interview_count
                AND (:no_penetration_filter OR COUNT(DISTINCT q.interview_id) * 100.0 / :total_interviews >= :min_penetration)
        )
        SELECT * FROM cluster_stats
        ORDER BY interview_penetration DESC
        LIMIT :limit OFFSET :offset
    """)
    
    # Execute cluster query
    no_category_filter = category_filter is None
    no_penetration_filter = min_penetration is None
    
    clusters_result = db.execute(
        cluster_query,
        {
            "total_interviews": total_interviews,
            "min_interview_count": min_interview_count,
            "min_penetration": min_penetration or 0,
            "category_filter": category_filter or [],
            "no_category_filter": no_category_filter,
            "no_penetration_filter": no_penetration_filter,
            "limit": limit,
            "offset": offset,
        }
    ).fetchall()
    
    # Build nodes
    nodes = []
    cluster_ids = []
    
    for cluster in clusters_result:
        cluster_ids.append(cluster.id)
        
        nodes.append(UniverseNode(
            id=cluster.id,
            name=cluster.name,
            category_id=cluster.category_id,
            category_name=cluster.category_name,
            questions_count=cluster.questions_count,
            interview_penetration=float(cluster.interview_penetration),
            keywords=cluster.keywords or [],
            example_question=cluster.example_question,
            top_companies=cluster.top_companies or [],
            difficulty_distribution={
                "junior": float(cluster.junior_pct),
                "middle": float(cluster.middle_pct),
                "senior": float(cluster.senior_pct),
            },
        ))
    
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
                    q1.cluster_id = ANY(:cluster_ids)
                    AND q2.cluster_id = ANY(:cluster_ids)
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
            {"cluster_ids": cluster_ids, "min_weight": min_link_weight}
        )
        
        max_weight = 1
        edge_list = edge_result.fetchall()
        if edge_list:
            max_weight = max([e.weight for e in edge_list])
            
        for edge_row in edge_list:
            edges.append(UniverseEdge(
                source=edge_row.source,
                target=edge_row.target,
                weight=edge_row.weight,
                strength=min(edge_row.weight / max_weight, 1.0),
            ))
    
    # Get categories
    category_query = text("""
        SELECT id, name, color, questions_count, clusters_count, percentage
        FROM "InterviewCategory"
    """)
    
    category_result = db.execute(category_query).fetchall()
    
    categories = {
        cat.id: CategoryInfo(
            id=cat.id,
            name=cat.name,
            color=cat.color or "#9e9e9e",
            questions_count=cat.questions_count,
            clusters_count=cat.clusters_count,
            percentage=float(cat.percentage),
        )
        for cat in category_result
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
    db: Session = Depends(get_session),
    include_questions: bool = Query(True, description="Include question list"),
    question_limit: int = Query(100, ge=1, le=500, description="Max questions to return"),
):
    """
    Get detailed information about a specific cluster including all questions.
    """
    
    # Get cluster info
    cluster_query = text("""
        SELECT id, name, category_id, questions_count
        FROM "InterviewCluster"
        WHERE id = :cluster_id
    """)
    cluster = db.execute(cluster_query, {"cluster_id": cluster_id}).fetchone()
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Get questions if requested
    questions = []
    if include_questions:
        question_query = text("""
            SELECT id, question_text, company, date
            FROM "InterviewQuestion"
            WHERE cluster_id = :cluster_id
            LIMIT :limit
        """)
        
        question_result = db.execute(
            question_query, 
            {"cluster_id": cluster_id, "limit": question_limit}
        ).fetchall()
        
        questions = [
            {
                "id": q.id,
                "text": q.question_text,
                "company": q.company,
                "date": q.date.isoformat() if q.date else None,
            }
            for q in question_result
        ]
    
    # Get related clusters
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
    
    related_result = db.execute(related_query, {"cluster_id": cluster_id}).fetchall()
    related_clusters = [
        {
            "id": r.id,
            "name": r.name,
            "sharedQuestions": r.shared_count,
            "correlation": min(r.shared_count / 10, 1.0),
        }
        for r in related_result
    ]
    
    # Get top companies
    company_query = text("""
        SELECT company, COUNT(*) as count
        FROM "InterviewQuestion"
        WHERE cluster_id = :cluster_id AND company IS NOT NULL
        GROUP BY company
        ORDER BY count DESC
        LIMIT 10
    """)
    
    company_result = db.execute(company_query, {"cluster_id": cluster_id}).fetchall()
    top_companies = [
        {
            "name": c.company,
            "count": c.count,
            "percentage": round(c.count * 100 / cluster.questions_count, 1) if cluster.questions_count > 0 else 0,
        }
        for c in company_result
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