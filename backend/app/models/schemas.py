"""
Pydantic models for API requests, responses, and internal data structures.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    RUNNING = "running"
    REFINING = "refining"
    FAILED = "failed"
    COMPLETED = "completed"


class FeedbackType(str, Enum):
    """Feedback type enumeration."""
    INACCURACY = "inaccuracy"
    UNCLEAR = "unclear"
    SUGGESTION = "suggestion"
    GENERAL = "general"


# Request Models
class ArticleGenerationRequest(BaseModel):
    """Request model for article generation."""
    topic: str = Field(..., min_length=10, max_length=500, description="Article topic")
    desired_depth: Literal["beginner", "intermediate", "expert"] = Field(
        default="intermediate", 
        description="Target audience depth"
    )
    max_length: Optional[int] = Field(
        default=5000, 
        ge=1000, 
        le=15000, 
        description="Maximum article length in words"
    )
    include_visuals: bool = Field(default=True, description="Include diagrams and charts")


class FeedbackRequest(BaseModel):
    """Request model for user feedback."""
    rating: int = Field(..., ge=1, le=5, description="Article rating (1-5)")
    comment: Optional[str] = Field(None, max_length=1000, description="User comment")
    feedback_type: FeedbackType = Field(default=FeedbackType.GENERAL)


# Core Data Models
class ResearchQuestion(BaseModel):
    """Individual research question within a section."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    question: str = Field(..., description="Specific research question")
    priority: int = Field(default=1, ge=1, le=5, description="Question priority")


class ArticleSection(BaseModel):
    """Article section with research questions."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., description="Section title")
    order: int = Field(..., ge=0, description="Section order in article")
    research_questions: List[ResearchQuestion] = Field(
        default_factory=list, 
        description="Research questions for this section"
    )


class ResearchPlan(BaseModel):
    """Complete research plan for an article."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    topic: str = Field(..., description="Article topic")
    target_audience: str = Field(..., description="Target audience")
    sections: List[ArticleSection] = Field(..., description="Article sections")
    estimated_word_count: int = Field(..., description="Estimated total word count")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Source(BaseModel):
    """Web source information."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    url: HttpUrl = Field(..., description="Source URL")
    title: Optional[str] = Field(None, description="Page title")
    domain: str = Field(..., description="Domain name")
    credibility_score: float = Field(..., ge=0.0, le=1.0, description="Credibility score")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class Snippet(BaseModel):
    """Extracted text snippet from a source."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str = Field(..., description="Source ID")
    text: str = Field(..., min_length=10, description="Extracted text")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    start_offset: Optional[int] = Field(None, description="Start position in source")
    end_offset: Optional[int] = Field(None, description="End position in source")
    contains_code: bool = Field(default=False, description="Contains code snippets")


class Citation(BaseModel):
    """Citation linking text to source."""
    snippet_id: str = Field(..., description="Referenced snippet ID")
    source_url: HttpUrl = Field(..., description="Source URL")
    source_title: Optional[str] = Field(None, description="Source title")


class DraftSection(BaseModel):
    """Draft section with citations."""
    section_id: str = Field(..., description="Section ID")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    citations: List[Citation] = Field(default_factory=list, description="Citations")
    word_count: int = Field(..., description="Word count")
    verification_status: Literal["draft", "verified", "needs_revision"] = Field(
        default="draft"
    )


class VisualAid(BaseModel):
    """Visual aid (diagram, chart, table)."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: Literal["mermaid", "table", "chart"] = Field(..., description="Visual aid type")
    title: str = Field(..., description="Visual aid title")
    content: str = Field(..., description="Visual aid content (Mermaid syntax, Markdown table, etc.)")
    section_id: Optional[str] = Field(None, description="Associated section ID")


class QAReport(BaseModel):
    """Quality assurance report."""
    fact_check_passed: bool = Field(..., description="Fact check status")
    criticism_addressed: bool = Field(..., description="Criticism addressed status")
    editorial_complete: bool = Field(..., description="Editorial review complete")
    issues_found: List[str] = Field(default_factory=list, description="Issues identified")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class FinalArticle(BaseModel):
    """Complete final article."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: UUID = Field(..., description="Associated job ID")
    title: str = Field(..., description="Article title")
    executive_summary: str = Field(..., description="Executive summary")
    content: str = Field(..., description="Full article content")
    visual_aids: List[VisualAid] = Field(default_factory=list, description="Visual aids")
    bibliography: List[Source] = Field(default_factory=list, description="Source bibliography")
    qa_report: QAReport = Field(..., description="Quality assurance report")
    word_count: int = Field(..., description="Total word count")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Response Models
class JobResponse(BaseModel):
    """Job creation response."""
    job_id: UUID = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="Job status")
    message: str = Field(..., description="Status message")


class JobStatusResponse(BaseModel):
    """Job status response."""
    job_id: UUID = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="Job status")
    current_step: Optional[str] = Field(None, description="Current processing step")
    progress_percentage: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class ArticleResponse(BaseModel):
    """Article retrieval response."""
    article: FinalArticle = Field(..., description="Generated article")
    generation_metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Generation metadata"
    )


# Agent Communication Models
class AgentTask(BaseModel):
    """Task for agent execution."""
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_type: str = Field(..., description="Target agent type")
    input_data: Dict[str, Any] = Field(..., description="Task input data")
    priority: int = Field(default=1, description="Task priority")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentResult(BaseModel):
    """Result from agent execution."""
    task_id: str = Field(..., description="Original task ID")
    agent_type: str = Field(..., description="Agent type")
    status: Literal["success", "error", "retry"] = Field(..., description="Execution status")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Task output data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    completed_at: datetime = Field(default_factory=datetime.utcnow)
