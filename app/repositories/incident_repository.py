"""
Incident Repository

Responsible only for persisting Incident records.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from typing import List

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.constants import (
    INCIDENT_NUMBER,
    SHORT_DESCRIPTION,
    DESCRIPTION,
    CATEGORY,
    SUBCATEGORY,
    PRIORITY,
    STATE,
    ASSIGNMENT_GROUP,
    CONFIGURATION_ITEM,
    BUSINESS_SERVICE,
    REGION,
    CREATED_DATE,
    RESOLVED_DATE,
    CLUSTER_ID
)
from app.database.incident_model import Incident
from app.repositories.repository_interface import RepositoryInterface
from app.utils.logger import logger


class IncidentRepository(RepositoryInterface):
    """
    Repository responsible for Incident persistence.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, dataframe: pd.DataFrame) -> None:
        """
        Persist processed incidents into PostgreSQL.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Processed dataframe containing cluster assignments.
        """
        try:
            logger.info("Persisting %d incidents...", len(dataframe))

            incident_records: List[Incident] = []

            for _, row in dataframe.iterrows():

                incident_records.append(
                    Incident(
                        incident_number=row[INCIDENT_NUMBER],
                        short_description=row[SHORT_DESCRIPTION],
                        description=row[DESCRIPTION],
                        category=row[CATEGORY],
                        subcategory=row[SUBCATEGORY],
                        priority=row[PRIORITY],
                        state=row[STATE],
                        assignment_group=row[ASSIGNMENT_GROUP],
                        configuration_item=row[CONFIGURATION_ITEM],
                        business_service=row[BUSINESS_SERVICE],
                        region=row[REGION],
                        created_date=row[CREATED_DATE],
                        resolved_date=row[RESOLVED_DATE],
                        cluster_id=(
                            None
                            if row[CLUSTER_ID] == -1
                            else int(row[CLUSTER_ID])
                        ),
                    )
                )

            self.session.bulk_save_objects(incident_records)

            logger.info(
                "Successfully persisted %d incidents.",
                len(incident_records)
            )

        except Exception:
            logger.exception("Failed to persist incidents.")
            raise

    def get_total_incidents(self) -> int:
        """Return the total number of processed incidents."""

        try:

            return (
                self.session.query(func.count(Incident.id))
                .scalar()
                or 0
            )

        except Exception:

            logger.exception(
                "Unable to fetch total incidents."
            )

            raise


    def get_incidents_by_cluster(
        self,
        cluster_id: int
    ) -> int:
        """
        Return number of incidents for a cluster.
        """

        try:

            return (

                self.session.query(func.count(Incident.id))

                .filter(
                    Incident.cluster_id == cluster_id
                )

                .scalar()

                or 0

            )

        except Exception:

            logger.exception(
                "Unable to fetch incident count."
            )

            raise

    def get_average_cluster_size(self) -> float:
        """
        Return average number of incidents per non-noise cluster.
        """

        try:

            cluster_counts = (
                self.session.query(
                    Incident.cluster_id,
                    func.count(Incident.id).label("incident_count")
                )
                .filter(Incident.cluster_id.is_not(None))
                .group_by(Incident.cluster_id)
                .subquery()
            )

            value = (
                self.session.query(
                    func.avg(cluster_counts.c.incident_count)
                )
                .scalar()
            )

            return round(float(value), 2) if value else 0.0

        except Exception:

            logger.exception(
                "Unable to fetch average cluster size."
            )

            raise

    def delete_all(self) -> None:
        """
        Delete all processed incidents.
        """

        try:

            deleted = self.session.query(Incident).delete()

            logger.info(
            "Deleted %d incident records.",
            deleted
            )

        except Exception:

            logger.exception(
                "Unable to delete incidents."
            )

            raise
