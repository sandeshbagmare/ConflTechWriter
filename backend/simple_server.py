"""
Simple FastAPI server for article generation with free services.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our services
try:
    from app.services.job_service import JobService
    logger.info("Successfully imported job service")
except ImportError as e:
    logger.error(f"Failed to import job service: {e}")
    JobService = None

app = FastAPI(
    title="Content Creation API",
    description="Free AI article generation service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ArticleRequest(BaseModel):
    topic: str
    desired_depth: str = "intermediate"
    max_length: int = 5000
    include_visuals: bool = True

class JobResponse(BaseModel):
    job_id: str
    status: str
    topic: str
    created_at: str
    estimated_completion: str

# Initialize job service
job_service = None
if JobService:
    try:
        job_service = JobService()
        logger.info("Job service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize job service: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Content Creation API",
        "status": "running",
        "version": "1.0.0",
        "services": {
            "job_service": job_service is not None
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "api": "running",
            "job_service": "available" if job_service else "unavailable"
        }
    }

@app.post("/v1/jobs", response_model=JobResponse)
async def create_job(request: ArticleRequest):
    """Create a new article generation job"""
    if not job_service:
        # Fallback response when job service is not available
        import uuid
        from datetime import datetime
        
        job_id = str(uuid.uuid4())
        return JobResponse(
            job_id=job_id,
            status="created",
            topic=request.topic,
            created_at=datetime.utcnow().isoformat(),
            estimated_completion="5-10 minutes (fallback mode)"
        )
    
    try:
        result = await job_service.create_job(
            topic=request.topic,
            desired_depth=request.desired_depth,
            max_length=request.max_length,
            include_visuals=request.include_visuals
        )
        
        return JobResponse(
            job_id=result["job_id"],
            status=result["status"],
            topic=result["topic"],
            created_at=result["created_at"],
            estimated_completion=result["estimated_completion"]
        )
        
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail=f"Job creation failed: {str(e)}")

@app.get("/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and result"""
    if not job_service:
        # Fallback response
        return {
            "job_id": job_id,
            "status": "completed",
            "result": {
                "success": True,
                "article": {
                    "title": "Sample Article",
                    "content": "# Sample Article\n\nThis is a sample article generated in fallback mode.",
                    "summary": "This is a sample article summary.",
                    "word_count": 20
                },
                "metadata": {
                    "generation_method": "fallback",
                    "note": "Generated in demo mode - services not fully configured"
                }
            }
        }
    
    try:
        result = await job_service.get_job_status(job_id)
        if not result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@app.get("/v1/jobs")
async def list_jobs(limit: int = 10, offset: int = 0):
    """List recent jobs"""
    if not job_service:
        return {
            "jobs": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "has_more": False,
            "note": "Job service not available"
        }
    
    try:
        return await job_service.list_jobs(limit=limit, offset=offset)
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

if __name__ == "__main__":
    logger.info("Starting Content Creation API server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
