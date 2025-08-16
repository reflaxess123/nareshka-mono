"""
Models for Interview Universe visualization
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Date, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.sql import func
from app.shared.database import Base


class InterviewCategory(Base):
    __tablename__ = "InterviewCategory"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    questions_count = Column(Integer, nullable=False, default=0)
    clusters_count = Column(Integer, nullable=False, default=0)
    percentage = Column(Float, nullable=False, default=0)
    color = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    
    # 3D coordinates
    galaxy_x = Column(Float, default=0)
    galaxy_y = Column(Float, default=0)
    galaxy_z = Column(Float, default=0)
    spiral_arm_angle = Column(Float, default=0)
    luminosity = Column(Float, default=1.0)
    last_activity_date = Column(DateTime, nullable=True)
    
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())


class InterviewCluster(Base):
    __tablename__ = "InterviewCluster"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category_id = Column(String, ForeignKey("InterviewCategory.id"), nullable=False)
    keywords = Column(PG_ARRAY(String), nullable=False, default=[])
    questions_count = Column(Integer, nullable=False, default=0)
    example_question = Column(Text, nullable=True)
    
    # 3D coordinates
    star_x = Column(Float, nullable=True)
    star_y = Column(Float, nullable=True)
    star_z = Column(Float, nullable=True)
    temperature = Column(Integer, nullable=True)  # difficulty 1-10
    mass = Column(Float, nullable=True)  # importance
    orbit_radius = Column(Float, nullable=True)
    orbit_speed = Column(Float, nullable=True)
    embedding_vector = Column(PG_ARRAY(Float), nullable=True)
    
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())


class InterviewQuestion(Base):
    __tablename__ = "InterviewQuestion"
    
    id = Column(String, primary_key=True)
    question_text = Column(Text, nullable=False)
    company = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    cluster_id = Column(Integer, ForeignKey("InterviewCluster.id"), nullable=True)
    category_id = Column(String, ForeignKey("InterviewCategory.id"), nullable=True)
    topic_name = Column(String, nullable=True)
    canonical_question = Column(Text, nullable=True)
    original_question_id = Column(String(10), nullable=True)
    interview_id = Column(String(100), nullable=True)
    
    # Satellite coordinates
    satellite_orbit_angle = Column(Float, nullable=True)
    satellite_distance = Column(Float, nullable=True)
    glow_intensity = Column(Float, nullable=True)
    last_asked_date = Column(Date, nullable=True)
    
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ClusterConnections(Base):
    __tablename__ = "ClusterConnections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_cluster_id = Column(Integer, ForeignKey("InterviewCluster.id", ondelete="CASCADE"))
    target_cluster_id = Column(Integer, ForeignKey("InterviewCluster.id", ondelete="CASCADE"))
    connection_weight = Column(Float, nullable=True)
    connection_type = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())