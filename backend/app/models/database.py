"""
SQLAlchemy database models for the AI Article Generation System.
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.core.database import Base


class Job(Base):
    """Job tracking table."""
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    topic = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="queued")
    desired_depth = Column(String(20), default="intermediate")
    max_length = Column(Integer, default=5000)
    include_visuals = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    sources = relationship("Source", back_populates="job", cascade="all, delete-orphan")
    final_article = relationship("FinalArticle", back_populates="job", uselist=False)
    feedback = relationship("Feedback", back_populates="job", cascade="all, delete-orphan")


class Source(Base):
    """Source URLs and metadata."""
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    domain = Column(String(255), nullable=False)
    credibility_score = Column(Float, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    content_hash = Column(String(64), nullable=True)  # For deduplication

    # Relationships
    job = relationship("Job", back_populates="sources")
    snippets = relationship("Snippet", back_populates="source", cascade="all, delete-orphan")

    __table_args__ = (
        {"schema": None}  # Explicitly no schema
    )


class Snippet(Base):
    """Extracted text snippets from sources."""
    __tablename__ = "snippets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False)
    text = Column(Text, nullable=False)
    relevance_score = Column(Float, nullable=False)
    start_offset = Column(Integer, nullable=True)
    end_offset = Column(Integer, nullable=True)
    contains_code = Column(Boolean, default=False)
    section_topic = Column(String(255), nullable=True)  # Which section this snippet is for
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source = relationship("Source", back_populates="snippets")


class FinalArticle(Base):
    """Final generated articles."""
    __tablename__ = "final_articles"

    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), primary_key=True)
    title = Column(Text, nullable=False)
    executive_summary = Column(Text, nullable=False)
    markdown_content = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=False)
    
    # JSON fields for complex data
    visual_aids = Column(JSONB, default=list)  # List of visual aid objects
    bibliography = Column(JSONB, default=list)  # List of source objects
    qa_report = Column(JSONB, default=dict)  # Quality assurance report
    generation_metadata = Column(JSONB, default=dict)  # Processing metadata
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="final_article")


class Feedback(Base):
    """User feedback on generated articles."""
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    article_job_id = Column(UUID(as_uuid=True), ForeignKey("final_articles.job_id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 scale
    comment = Column(Text, nullable=True)
    feedback_type = Column(String(50), default="general")
    
    # Optional fields for specific feedback
    highlighted_text = Column(Text, nullable=True)  # Text user highlighted
    suggested_correction = Column(Text, nullable=True)  # User's suggestion
    
    # Metadata
    user_ip = Column(String(45), nullable=True)  # For anonymous feedback tracking
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="feedback")


class ProcessingLog(Base):
    """Detailed logging of processing steps."""
    __tablename__ = "processing_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    agent_type = Column(String(100), nullable=False)
    step_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # started, completed, failed
    
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class SourceCredibilityCache(Base):
    """Cache for source credibility scores."""
    __tablename__ = "source_credibility_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    domain = Column(String(255), nullable=False, unique=True)
    base_credibility_score = Column(Float, nullable=False)
    
    # Factors contributing to credibility
    domain_authority = Column(Float, nullable=True)
    has_https = Column(Boolean, default=True)
    is_academic = Column(Boolean, default=False)
    is_official_docs = Column(Boolean, default=False)
    content_quality_score = Column(Float, nullable=True)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    evaluation_count = Column(Integer, default=1)  # How many times we've evaluated this domain
