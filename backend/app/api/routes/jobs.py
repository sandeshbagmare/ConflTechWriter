"""
Job management endpoints for article generation.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
import structlog
import json
from typing import AsyncGenerator

from app.core.database import get_db
from app.models.schemas import (
    ArticleGenerationRequest, 
    JobResponse, 
    JobStatusResponse, 
    ArticleResponse,
    FeedbackRequest,
    JobStatus
)
from app.workers.orchestrator import start_article_generation
from app.services.job_service import JobService

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/", response_model=JobResponse)
async def create_job(
    request: ArticleGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new article generation job.
    
    This endpoint accepts a topic and configuration, creates a job record,
    and starts the multi-agent processing pipeline in the background.
    """
    try:
        job_service = JobService(db)
        
        # Create job record
        job_id = uuid4()
        await job_service.create_job(
            job_id=job_id,
            topic=request.topic,
            desired_depth=request.desired_depth,
            max_length=request.max_length,
            include_visuals=request.include_visuals
        )
        
        # Start processing in background
        background_tasks.add_task(start_article_generation, job_id, request.dict())
        
        logger.info("Article generation job created", job_id=str(job_id), topic=request.topic)
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            message="Article generation job created and queued for processing"
        )
        
    except Exception as e:
        logger.error("Failed to create job", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create article generation job")


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current status of an article generation job.
    """
    try:
        job_service = JobService(db)
        job = await job_service.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Calculate progress percentage based on status
        progress_map = {
            JobStatus.QUEUED: 0,
            JobStatus.RUNNING: 50,
            JobStatus.REFINING: 80,
            JobStatus.COMPLETED: 100,
            JobStatus.FAILED: 0
        }
        
        return JobStatusResponse(
            job_id=job_id,
            status=job.status,
            current_step=f"Processing: {job.status}",
            progress_percentage=progress_map.get(job.status, 0),
            error_message=job.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job status", job_id=str(job_id), error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve job status")


@router.get("/{job_id}/events")
async def get_job_events(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Server-Sent Events endpoint for real-time job progress updates.
    """
    
    async def event_stream() -> AsyncGenerator[str, None]:
        """Generate SSE events for job progress."""
        job_service = JobService(db)
        
        while True:
            try:
                job = await job_service.get_job(job_id)
                if not job:
                    yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                    break
                
                event_data = {
                    "job_id": str(job_id),
                    "status": job.status,
                    "timestamp": job.updated_at.isoformat() if job.updated_at else None
                }
                
                yield f"data: {json.dumps(event_data)}\n\n"
                
                # Stop streaming if job is complete or failed
                if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    break
                
                # Wait before next update
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error("Error in event stream", job_id=str(job_id), error=str(e))
                yield f"data: {json.dumps({'error': 'Stream error'})}\n\n"
                break
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/{job_id}/artifacts", response_model=ArticleResponse)
async def get_job_artifacts(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve the final article and related artifacts for a completed job.
    """
    try:
        job_service = JobService(db)
        job = await job_service.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Job not completed. Current status: {job.status}"
            )
        
        article = await job_service.get_final_article(job_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return ArticleResponse(
            article=article,
            generation_metadata={
                "job_id": str(job_id),
                "processing_time": (job.completed_at - job.created_at).total_seconds() if job.completed_at else None,
                "status": job.status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job artifacts", job_id=str(job_id), error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve article")


@router.post("/{job_id}/feedback")
async def submit_feedback(
    job_id: UUID,
    feedback: FeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit user feedback for a generated article.
    """
    try:
        job_service = JobService(db)
        
        # Verify job exists and is completed
        job = await job_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Cannot provide feedback for incomplete job")
        
        # Store feedback
        await job_service.create_feedback(
            job_id=job_id,
            rating=feedback.rating,
            comment=feedback.comment,
            feedback_type=feedback.feedback_type
        )
        
        logger.info("Feedback submitted", job_id=str(job_id), rating=feedback.rating)
        
        return {"message": "Feedback submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit feedback", job_id=str(job_id), error=str(e))
        raise HTTPException(status_code=500, detail="Failed to submit feedback")
