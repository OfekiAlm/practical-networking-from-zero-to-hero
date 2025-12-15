"""Job submission and status endpoints."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, BackgroundTasks

from backend.schemas.base import JobRequest, JobResponse, JobStatus
from backend.demos.registry import get_registry
from backend.worker.queue_manager import get_queue_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_job(job_request: JobRequest, background_tasks: BackgroundTasks):
    """
    Submit a new demo execution job.
    
    The job is added to the queue and will be executed asynchronously
    by a worker process. Returns immediately with a job_id that can
    be used to check status and retrieve results.
    
    Args:
        job_request: Demo ID and parameters
        
    Returns:
        Job response with job_id and initial status
    """
    try:
        # Validate demo exists
        registry = get_registry()
        if not registry.demo_exists(job_request.demo_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Demo '{job_request.demo_id}' not found"
            )
        
        # Validate parameters
        demo = registry.get_demo(job_request.demo_id)
        try:
            demo.validate_params(job_request.parameters)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid parameters: {str(e)}"
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Submit to queue
        queue_manager = get_queue_manager()
        queue_manager.submit_job(
            job_id=job_id,
            demo_id=job_request.demo_id,
            parameters=job_request.parameters
        )
        
        logger.info(f"Job {job_id} submitted for demo {job_request.demo_id}")
        
        return JobResponse(
            job_id=job_id,
            demo_id=job_request.demo_id,
            status=JobStatus.PENDING,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            result=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting job: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit job"
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """
    Get the status and results of a job.
    
    Args:
        job_id: The unique job identifier
        
    Returns:
        Job status, execution details, and results (if completed)
    """
    try:
        queue_manager = get_queue_manager()
        job_info = queue_manager.get_job_status(job_id)
        
        if job_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job '{job_id}' not found"
            )
        
        return job_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job status"
        )
