"""
Tests for asynchronous processing job API and repository behavior.
"""

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.jobs import get_job
from app.api.jobs import list_jobs
from app.api.process import process_dataset
from app.constants import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
)
from app.database.base import Base
from app.database.processing_job_model import ProcessingJob
from app.repositories.job_repository import JobRepository
from app.schemas import ProcessRequest
from app.schemas import JobResponse


class FakeJobService:
    """
    Lightweight job service used by API tests.
    """

    def __init__(self):
        self.job = ProcessingJob(
            id="11111111-1111-1111-1111-111111111111",
            dataset_path="dataset/incidents.csv",
            status=JOB_STATUS_PENDING,
            message="Processing job queued.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def create_processing_job(self, dataset_path: str):
        self.job.dataset_path = dataset_path
        return self.job

    def list_jobs(self):
        return [self.job]

    def get_job(self, job_id: str):
        if job_id == self.job.id:
            return self.job

        return None


def test_process_endpoint_queues_job():
    service = FakeJobService()

    response = process_dataset(
        request=ProcessRequest(
            dataset_path="dataset/incidents.csv"
        ),
        service=service
    )

    assert response.status == JOB_STATUS_PENDING
    assert response.dataset_path == "dataset/incidents.csv"


def test_jobs_endpoints_return_jobs():
    service = FakeJobService()

    list_response = list_jobs(
        service=service
    )
    detail_response = get_job(
        job_id="11111111-1111-1111-1111-111111111111",
        service=service
    )

    assert len(list_response) == 1
    assert detail_response.id == "11111111-1111-1111-1111-111111111111"


def test_job_repository_updates_statuses():
    engine = create_engine(
        "sqlite:///:memory:"
    )
    TestingSession = sessionmaker(
        bind=engine
    )
    Base.metadata.create_all(
        bind=engine
    )

    session = TestingSession()
    repository = JobRepository(
        session
    )

    job = repository.create(
        "dataset/incidents.csv"
    )
    session.commit()

    repository.mark_running(
        job
    )

    assert job.status == JOB_STATUS_RUNNING

    repository.mark_completed(
        job,
        processing_time_seconds=1.25,
        total_incidents=10,
        total_clusters=2,
        total_problem_candidates=1
    )

    assert job.status == JOB_STATUS_COMPLETED
    assert job.total_incidents == 10

    response = JobResponse.model_validate(
        job
    )

    assert str(response.id) == job.id

    session.close()
