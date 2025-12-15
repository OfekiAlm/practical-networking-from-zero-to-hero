"""Base schemas for the platform."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class DemoResult(BaseModel):
    """Structure for demo execution results."""
    success: bool = Field(..., description="Whether execution succeeded")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Demo-specific output data"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Execution metadata"
    )
    execution_time_ms: Optional[float] = Field(
        None, description="Execution time in milliseconds"
    )


class DemoRecipe(BaseModel):
    """Definition of a demo recipe."""
    id: str = Field(..., description="Unique demo identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Demo description")
    category: str = Field(..., description="Demo category (layer2, layer3, etc)")
    max_runtime: int = Field(
        30, description="Maximum execution time in seconds", ge=1, le=300
    )
    requires_network: bool = Field(
        False, description="Whether demo requires network access"
    )
    requires_root: bool = Field(
        False, description="Whether demo requires elevated privileges"
    )
    parameters_schema: Dict[str, Any] = Field(
        ..., description="JSON schema for parameters"
    )


class JobRequest(BaseModel):
    """Request to execute a demo."""
    demo_id: str = Field(..., description="Demo identifier")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Demo parameters"
    )


class JobResponse(BaseModel):
    """Response containing job information."""
    job_id: str = Field(..., description="Unique job identifier")
    demo_id: str = Field(..., description="Demo identifier")
    status: JobStatus = Field(..., description="Current job status")
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    result: Optional[DemoResult] = Field(None, description="Execution result")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
