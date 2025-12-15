"""Queue manager for job submission and status tracking.

This module uses Redis + RQ for job queue management.
For production, this can be replaced with Celery if needed.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import redis
    from rq import Queue
    from rq.job import Job
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from backend.schemas.base import JobStatus, JobResponse, DemoResult

logger = logging.getLogger(__name__)


class QueueManager:
    """Manages job queue operations."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize queue manager.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self._redis_conn = None
        self._queue = None
        
        if REDIS_AVAILABLE:
            try:
                self._redis_conn = redis.from_url(redis_url)
                self._queue = Queue(connection=self._redis_conn, default_timeout=300)
                logger.info(f"Connected to Redis at {redis_url}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                logger.warning("Running in mock mode without Redis")
        else:
            logger.warning("Redis/RQ not available, running in mock mode")
        
        # Mock storage for when Redis is not available
        self._mock_jobs: Dict[str, Dict[str, Any]] = {}
    
    def submit_job(
        self,
        job_id: str,
        demo_id: str,
        parameters: Dict[str, Any]
    ) -> None:
        """
        Submit a job to the queue.
        
        Args:
            job_id: Unique job identifier
            demo_id: Demo to execute
            parameters: Validated parameters
        """
        if self._queue:
            try:
                # Enqueue job with RQ
                job = self._queue.enqueue(
                    'backend.worker.executor.execute_demo_in_container',
                    job_id=job_id,
                    demo_id=demo_id,
                    parameters=parameters,
                    job_id=job_id,  # RQ job ID same as our job ID
                    timeout=300,
                    result_ttl=3600  # Keep results for 1 hour
                )
                logger.info(f"Job {job_id} enqueued with RQ")
            except Exception as e:
                logger.error(f"Failed to enqueue job {job_id}: {e}")
                # Fallback to mock
                self._submit_mock_job(job_id, demo_id, parameters)
        else:
            # Mock mode
            self._submit_mock_job(job_id, demo_id, parameters)
    
    def _submit_mock_job(
        self,
        job_id: str,
        demo_id: str,
        parameters: Dict[str, Any]
    ) -> None:
        """Submit job in mock mode (for development without Redis)."""
        self._mock_jobs[job_id] = {
            "job_id": job_id,
            "demo_id": demo_id,
            "parameters": parameters,
            "status": JobStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None
        }
        logger.info(f"Job {job_id} created in mock mode")
    
    def get_job_status(self, job_id: str) -> Optional[JobResponse]:
        """
        Get the current status of a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job information or None if not found
        """
        if self._queue:
            try:
                job = Job.fetch(job_id, connection=self._redis_conn)
                return self._job_to_response(job)
            except Exception as e:
                logger.debug(f"Job {job_id} not found in RQ: {e}")
                # Check mock storage as fallback
                return self._get_mock_job_status(job_id)
        else:
            return self._get_mock_job_status(job_id)
    
    def _job_to_response(self, job: 'Job') -> JobResponse:
        """Convert RQ Job to JobResponse."""
        # Map RQ status to our JobStatus
        status_map = {
            'queued': JobStatus.PENDING,
            'started': JobStatus.RUNNING,
            'finished': JobStatus.COMPLETED,
            'failed': JobStatus.FAILED,
            'stopped': JobStatus.TIMEOUT,
        }
        
        status = status_map.get(job.get_status(), JobStatus.PENDING)
        
        # Parse result if available
        result = None
        if job.result:
            result = DemoResult(**job.result)
        
        return JobResponse(
            job_id=job.id,
            demo_id=job.kwargs.get('demo_id', 'unknown'),
            status=status,
            created_at=job.created_at or datetime.utcnow(),
            started_at=job.started_at,
            completed_at=job.ended_at,
            result=result
        )
    
    def _get_mock_job_status(self, job_id: str) -> Optional[JobResponse]:
        """Get job status from mock storage."""
        job_data = self._mock_jobs.get(job_id)
        if not job_data:
            return None
        
        result = None
        if job_data.get("result"):
            result = DemoResult(**job_data["result"])
        
        return JobResponse(
            job_id=job_data["job_id"],
            demo_id=job_data["demo_id"],
            status=JobStatus(job_data["status"]),
            created_at=datetime.fromisoformat(job_data["created_at"]),
            started_at=datetime.fromisoformat(job_data["started_at"]) if job_data.get("started_at") else None,
            completed_at=datetime.fromisoformat(job_data["completed_at"]) if job_data.get("completed_at") else None,
            result=result
        )
    
    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update job status (used by worker).
        
        Args:
            job_id: Job identifier
            status: New status
            result: Execution result (if completed)
        """
        if job_id in self._mock_jobs:
            now = datetime.utcnow().isoformat()
            self._mock_jobs[job_id]["status"] = status.value
            
            if status == JobStatus.RUNNING and not self._mock_jobs[job_id]["started_at"]:
                self._mock_jobs[job_id]["started_at"] = now
            
            if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.TIMEOUT]:
                self._mock_jobs[job_id]["completed_at"] = now
                if result:
                    self._mock_jobs[job_id]["result"] = result


# Global queue manager instance
_queue_manager: Optional[QueueManager] = None


def get_queue_manager() -> QueueManager:
    """Get the global queue manager instance."""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = QueueManager()
    return _queue_manager
