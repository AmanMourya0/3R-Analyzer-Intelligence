"""
Application service for processing job lifecycle operations.
"""

from typing import List
from typing import Optional

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.processing_job_model import ProcessingJob
from app.repositories.job_repository import JobRepository
from app.services.scheduler_service import SchedulerService
from app.utils.logger import logger


class JobService:
    """
    Coordinates processing job persistence and scheduling.
    """

    def __init__(
        self,
        scheduler_service: SchedulerService
    ) -> None:
        """
        Initialize the service.
        """

        self.scheduler_service = scheduler_service

    def create_processing_job(
        self,
        dataset_path: str
    ) -> ProcessingJob:
        """
        Create a queued processing job and schedule background execution.
        """

        session: Session = SessionLocal()

        try:

            repository = JobRepository(
                session
            )

            job = repository.create(
                dataset_path
            )

            session.commit()
            session.refresh(
                job
            )

            self.scheduler_service.schedule_processing_job(
                job.id
            )

            logger.info(
                "Created processing job %s.",
                job.id
            )

            session.expunge(
                job
            )

            return job

        except Exception:

            session.rollback()

            logger.exception(
                "Unable to create processing job."
            )

            raise

        finally:

            session.close()

    def list_jobs(self) -> List[ProcessingJob]:
        """
        Return all processing jobs.
        """

        session: Session = SessionLocal()

        try:

            return JobRepository(
                session
            ).list_all()

        except Exception:

            logger.exception(
                "Unable to list processing jobs."
            )

            raise

        finally:

            session.close()

    def get_job(
        self,
        job_id: str
    ) -> Optional[ProcessingJob]:
        """
        Return one processing job by UUID string.
        """

        session: Session = SessionLocal()

        try:

            return JobRepository(
                session
            ).get_by_id(
                job_id
            )

        except Exception:

            logger.exception(
                "Unable to fetch processing job %s.",
                job_id
            )

            raise

        finally:

            session.close()
