"""
Incident Processing Service

Coordinates loading, AI processing and persistence layer.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""


import time

from sqlalchemy.orm import Session

from app.enums import JobStatus
from app.database.database import SessionLocal

from app.services.incident_loader import IncidentLoader

from app.pipelines.incident_pipeline import IncidentPipeline

from app.repositories.incident_repository import IncidentRepository

from app.repositories.cluster_repository import ClusterRepository

from app.repositories.job_repository import JobRepository

from app.repositories.recurrence_repository import RecurrenceRepository

from app.models.pipeline_result import PipelineResult

from app.utils.logger import logger


class ProcessService:

    def __init__(

        self,

        pipeline: IncidentPipeline

    ):

        self.pipeline = pipeline

    def process_dataset(
    self,
    dataset_path: str
) -> PipelineResult:
        """
        Execute the complete AI pipeline and persist the latest
        analysis into PostgreSQL.

        Every processing run replaces the previous analytical
        snapshot while preserving processing job history.
        """

        session: Session = SessionLocal()

        try:

            logger.info("=" * 80)
            logger.info("Starting incident processing...")
            logger.info("Dataset : %s", dataset_path)

            loader = IncidentLoader(
                dataset_path
            )

            dataframe = loader.load()

            logger.info(
                "Loaded %d incidents.",
                len(dataframe)
            )

            result = self.pipeline.run(
                dataframe
            )

            incident_repository = IncidentRepository(session)

            cluster_repository = ClusterRepository(session)

            recurrence_repository = RecurrenceRepository(session)

            # --------------------------------------------------
            # Remove previous analytical snapshot
            # --------------------------------------------------

            logger.info(
                "Clearing previous analytical results..."
            )

            recurrence_repository.delete_all()

            incident_repository.delete_all()

            cluster_repository.delete_all()

            session.flush()

            logger.info(
                "Persisting latest analytical snapshot..."
            )

            cluster_repository.save(
                result.cluster_summaries
            )

            incident_repository.save(
                result.dataframe
            )

            recurrence_repository.save(
                result.recurrence_results
            )

            session.commit()

            logger.info("=" * 80)
            logger.info("Processing completed successfully.")
            logger.info("Incidents : %d",len(result.dataframe))
            logger.info(
            "Clusters : %d",
            len(result.cluster_summaries)
        )

            return result

        except Exception:

            session.rollback()

            logger.exception(
            "Processing failed."
        )

            raise

        finally:

            session.close()
            

    def process_job(

        self,

        job_id: str

    ) -> None:
        """
        Process a queued job and update its PostgreSQL status.

        Parameters
        ----------
        job_id : str
            UUID string for the queued processing job.
        """

        session: Session = SessionLocal()

        try:

            repository = JobRepository(
                session
            )

            job = repository.get_by_id(
                job_id
            )

            if job is None:

                logger.error(
                    "Processing job %s was not found.",
                    job_id
                )

                return

            if job.status == JobStatus.RUNNING.value:

                logger.info(
                    "Processing job %s is already running.",
                    job_id
                )

                return

            repository.mark_running(
                job
            )

            session.commit()

            start_time = time.perf_counter()

            result = self.process_dataset(
                job.dataset_path
            )

            processing_time = round(
                time.perf_counter() - start_time,
                2
            )

            repository.mark_completed(
                job,
                processing_time_seconds=processing_time,
                total_incidents=len(result.dataframe),
                total_clusters=len(result.cluster_summaries),
                total_problem_candidates=sum(
                    item.problem_candidate
                    for item in result.recurrence_results
                )
            )

            session.commit()

            logger.info(
                "Processing job %s completed successfully.",
                job_id
            )

        except Exception as ex:

            session.rollback()

            try:

                repository = JobRepository(
                    session
                )

                job = repository.get_by_id(
                    job_id
                )

                if job is not None:

                    repository.mark_failed(
                        job,
                        str(ex)
                    )

                    session.commit()

            except Exception:

                session.rollback()

                logger.exception(
                    "Unable to mark processing job %s as failed.",
                    job_id
                )

            logger.exception(
                "Processing job %s failed.",
                job_id
            )

        finally:

            session.close()
