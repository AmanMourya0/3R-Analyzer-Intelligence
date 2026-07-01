"""
Processing job repository.

Owns persistence operations for asynchronous processing job records.
"""

from datetime import datetime
from typing import Optional
from typing import List

from sqlalchemy.orm import Session

from app.constants import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
)
from app.database.processing_job_model import ProcessingJob
from app.repositories.repository_interface import RepositoryInterface


class JobRepository(RepositoryInterface):
    """
    Repository responsible for ProcessingJob persistence.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, data: ProcessingJob) -> None:
        """
        Persist a processing job instance.
        """

        self.session.add(data)

    def create(self, dataset_path: str) -> ProcessingJob:
        """
        Create a pending processing job.
        """

        job = ProcessingJob(
            dataset_path=dataset_path,
            status=JOB_STATUS_PENDING,
            message="Processing job queued."
        )

        self.save(job)
        self.session.flush()

        return job

    def get_by_id(self, job_id: str) -> Optional[ProcessingJob]:
        """
        Return one processing job by UUID string.
        """

        return (
            self.session.query(ProcessingJob)
            .filter(ProcessingJob.id == job_id)
            .one_or_none()
        )

    def list_all(self) -> List[ProcessingJob]:
        """
        Return processing jobs ordered newest first.
        """

        return (
            self.session.query(ProcessingJob)
            .order_by(ProcessingJob.created_at.desc())
            .all()
        )

    def mark_running(self, job: ProcessingJob) -> None:
        """
        Mark a job as running.
        """

        job.status = JOB_STATUS_RUNNING
        job.message = "Processing job running."
        job.started_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

    def mark_completed(
        self,
        job: ProcessingJob,
        processing_time_seconds: float,
        total_incidents: int,
        total_clusters: int,
        total_problem_candidates: int
    ) -> None:
        """
        Mark a job as completed with processing metrics.
        """

        job.status = JOB_STATUS_COMPLETED
        job.message = "Dataset processed successfully."
        job.processing_time_seconds = processing_time_seconds
        job.total_incidents = total_incidents
        job.total_clusters = total_clusters
        job.total_problem_candidates = total_problem_candidates
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

    def mark_failed(
        self,
        job: ProcessingJob,
        error_message: str
    ) -> None:
        """
        Mark a job as failed.
        """

        job.status = JOB_STATUS_FAILED
        job.message = "Dataset processing failed."
        job.error_message = error_message
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
