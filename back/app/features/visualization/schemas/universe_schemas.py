"""
Pydantic schemas for Interview Universe visualization
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class UniverseNode(BaseModel):
    """Node representation for graph visualization"""
    id: int
    name: str
    category_id: str
    category_name: str
    questions_count: int
    interview_penetration: float = Field(..., ge=0, le=100)
    keywords: List[str]
    example_question: Optional[str] = None
    top_companies: List[str]
    difficulty_distribution: Dict[str, float]
    
    # Optional layout coordinates
    x: Optional[float] = None
    y: Optional[float] = None


class UniverseEdge(BaseModel):
    """Edge representation for graph connections"""
    source: int
    target: int
    weight: int
    strength: float = Field(..., ge=0, le=1)


class CategoryInfo(BaseModel):
    """Category information"""
    id: str
    name: str
    color: str
    questions_count: int
    clusters_count: int
    percentage: float


class UniverseStats(BaseModel):
    """Statistics for the universe visualization"""
    totalQuestions: int
    totalClusters: int
    totalCategories: int
    totalCompanies: int
    avgQuestionsPerCluster: float
    avgInterviewPenetration: float
    totalEdges: int = 0


class UniverseGraphResponse(BaseModel):
    """Response for universe graph endpoint"""
    nodes: List[UniverseNode]
    edges: List[UniverseEdge]
    categories: Dict[str, CategoryInfo]
    stats: UniverseStats


class QuestionInfo(BaseModel):
    """Question information for cluster details"""
    id: str
    text: str
    company: Optional[str]
    date: Optional[str]
    difficulty: Optional[str] = None


class RelatedCluster(BaseModel):
    """Related cluster information"""
    id: int
    name: str
    sharedQuestions: int
    correlation: float


class CompanyStats(BaseModel):
    """Company statistics for a cluster"""
    name: str
    count: int
    percentage: float


class ClusterDetailsResponse(BaseModel):
    """Response for cluster details endpoint"""
    id: int
    name: str
    category: str
    questionsCount: int
    questions: Optional[List[Dict[str, Any]]] = None
    relatedClusters: List[Dict[str, Any]]
    topCompanies: List[Dict[str, Any]]
    trendData: Optional[List[Dict[str, Any]]] = None