"""
Job Service for managing article generation jobs with free services.
"""

import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..core.database import get_session
from ..models.database import Job
from ..workers.orchestrator import ArticleOrchestrator
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing article generation jobs."""
    
    def __init__(self):
        self.orchestrator = ArticleOrchestrator()
    
    async def create_job(
        self,
        topic: str,
        desired_depth: str = "intermediate",
        max_length: int = 5000,
        include_visuals: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new article generation job.
        
        Args:
            topic: Article topic
            desired_depth: Target audience depth
            max_length: Maximum article length
            include_visuals: Whether to include visuals
            
        Returns:
            Job information with ID and status
        """
        try:
            # Generate unique job ID
            job_id = str(uuid.uuid4())
            
            # Create job record in database
            session = next(get_session())
            
            job = Job(
                id=job_id,
                topic=topic,
                parameters={
                    "desired_depth": desired_depth,
                    "max_length": max_length,
                    "include_visuals": include_visuals
                },
                status="created",
                created_at=datetime.utcnow()
            )
            
            session.add(job)
            session.commit()
            
            logger.info(f"Job created: {job_id} for topic: {topic}")
            
            # Start processing asynchronously
            asyncio.create_task(self._process_job_async(job_id, {
                "job_id": job_id,
                "topic": topic,
                "desired_depth": desired_depth,
                "max_length": max_length,
                "include_visuals": include_visuals
            }))
            
            return {
                "job_id": job_id,
                "status": "created",
                "topic": topic,
                "created_at": job.created_at.isoformat(),
                "estimated_completion": "3-5 minutes"
            }
            
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status information or None if not found
        """
        try:
            session = next(get_session())
            job = session.query(Job).filter(Job.id == job_id).first()
            
            if not job:
                return None
            
            result = {
                "job_id": job.id,
                "topic": job.topic,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "parameters": job.parameters or {}
            }
            
            if job.result:
                result["result"] = job.result
            
            if job.completed_at:
                result["completed_at"] = job.completed_at.isoformat()
            
            if job.error_message:
                result["error"] = job.error_message
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return None
    
    async def _process_job_async(self, job_id: str, job_data: Dict[str, Any]):
        """Process job asynchronously."""
        try:
            logger.info(f"Starting async processing for job {job_id}")
            
            # Process the job using the orchestrator
            result = await self.orchestrator.generate_article(job_data)
            
            # Update job with result
            session = next(get_session())
            job = session.query(Job).filter(Job.id == job_id).first()
            
            if job:
                job.status = "completed"
                job.result = result
                job.completed_at = datetime.utcnow()
                session.commit()
                
                logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job_id} processing failed: {e}")
            
            # Update job with error
            try:
                session = next(get_session())
                job = session.query(Job).filter(Job.id == job_id).first()
                
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    job.completed_at = datetime.utcnow()
                    session.commit()
            except Exception as db_error:
                logger.error(f"Failed to update job {job_id} with error: {db_error}")
    
    async def list_jobs(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        List recent jobs.
        
        Args:
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip
            
        Returns:
            List of jobs with pagination info
        """
        try:
            session = next(get_session())
            
            # Get total count
            total = session.query(Job).count()
            
            # Get jobs with pagination
            jobs = session.query(Job)\
                         .order_by(Job.created_at.desc())\
                         .offset(offset)\
                         .limit(limit)\
                         .all()
            
            job_list = []
            for job in jobs:
                job_info = {
                    "job_id": job.id,
                    "topic": job.topic,
                    "status": job.status,
                    "created_at": job.created_at.isoformat()
                }
                
                if job.completed_at:
                    job_info["completed_at"] = job.completed_at.isoformat()
                
                if job.error_message:
                    job_info["error"] = job.error_message
                
                job_list.append(job_info)
            
            return {
                "jobs": job_list,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
            
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return {
                "jobs": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "error": str(e)
            }
    
    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            session = next(get_session())
            job = session.query(Job).filter(Job.id == job_id).first()
            
            if job:
                session.delete(job)
                session.commit()
                logger.info(f"Job {job_id} deleted")
                return True
            else:
                logger.warning(f"Job {job_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
