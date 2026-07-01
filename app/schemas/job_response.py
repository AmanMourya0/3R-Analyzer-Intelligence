"""
Processing job response schema.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class JobResponse(BaseModel):
    """
    Response model for asynchronous processing jobs.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    dataset_path: str

    status: str

    message: str

    processing_time_seconds: Optional[float] = Field(
        default=None,
        ge=0
    )

    total_incidents: Optional[int] = Field(
        default=None,
        ge=0
    )

    total_clusters: Optional[int] = Field(
        default=None,
        ge=0
    )

    total_problem_candidates: Optional[int] = Field(
        default=None,
        ge=0
    )

    error_message: Optional[str] = None

    created_at: datetime

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    updated_at: datetime
