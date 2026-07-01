"""
Incident Processing Pipeline

This module orchestrates the complete preprocessing pipeline
for historical incidents.

Pipeline Flow:
    Load Dataset
        ↓
    Preprocess Dataset
        ↓
    Generate Embeddings
        ↓
    Return Processed DataFrame

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from typing import Optional

import pandas as pd

from app.services.incident_loader import IncidentLoader
from app.services.preprocessing import Preprocessor
from app.clustering.embedding import SemanticEmbeddingGenerator
from app.clustering.cluster import SemanticClusterer
from app.constants import (
    EMBEDDING,
    COMBINED_TEXT,
    CLUSTER_ID
)
from app.clustering.cluster_analyzer import ClusterAnalyzer
from app.clustering.recurrence import RecurrenceDetector
from app.models.pipeline_result import PipelineResult

from app.utils.logger import logger

class IncidentPipeline:
    """
    End-to-end pipeline for incident processing.
    """

    def __init__(
        self,
        dataset_path: Optional[str] = None
    ) -> None:
        """
        Initialize all required pipeline components.

        Parameters
        ----------
        dataset_path : Optional[str]
            Backward-compatible dataset path for older callers. New service
            code should pass a dataframe to ``run``.
        """

        self.dataset_path = dataset_path

        self.preprocessor = Preprocessor()

        self.embedding_generator = SemanticEmbeddingGenerator()

        self.cluster_generator = SemanticClusterer()

        self.cluster_analyzer = ClusterAnalyzer()

        self.recurrence_detector = RecurrenceDetector()

    def run(
        self,
        dataframe: Optional[pd.DataFrame] = None
    ) -> PipelineResult:
        """
        Execute the complete pipeline.

        Parameters
        ----------
        dataframe : Optional[pd.DataFrame]
            Incident dataframe supplied by the service layer. If omitted, the
            optional constructor dataset path is used for backward compatibility.

        Returns
        -------
        PipelineResult
            Complete pipeline result containing processed data and analysis.
        """

        try:

            logger.info("=" * 60)
            logger.info("Starting Incident Processing Pipeline")
            logger.info("=" * 60)

            if dataframe is None:
                if not self.dataset_path:
                    raise ValueError(
                        "A dataframe or dataset_path is required."
                    )

                dataframe = IncidentLoader(
                    self.dataset_path
                ).load()

            
            # -------------------------------------------------
            # Step 1 : Clean Dataset
            # -------------------------------------------------

            df = self.preprocessor.clean(dataframe)

            # -------------------------------------------------
            # Step 2 : Generate Embeddings
            # -------------------------------------------------

            embeddings = self.embedding_generator.generate_embeddings(
                df[COMBINED_TEXT].tolist()
            )

            # -------------------------------------------------
            # Step 3 : Store embeddings
            # -------------------------------------------------

            df[EMBEDDING] = embeddings.tolist()

            # -------------------------------------------------
            # Step 4 : Generate Semantic Clusters
            # -------------------------------------------------

            labels = self.cluster_generator.generate(embeddings)
            
            # Store generated cluster labels
            df[CLUSTER_ID] = labels

            # -------------------------------------------------
            # Step 5 : Generate Cluster Summaries
            # -------------------------------------------------

            cluster_summaries = self.cluster_analyzer.analyze(df)

            # -------------------------------------------------
            # Step 6 : Generate Recurrence Results
            # -------------------------------------------------

            recurrence_results = self.recurrence_detector.detect(cluster_summaries)

            logger.info("Cluster analysis completed.")

            logger.info("Pipeline completed successfully.")

            return PipelineResult(
                dataframe=df,
                cluster_summaries=cluster_summaries,
                recurrence_results=recurrence_results
                )

        except Exception:

            logger.exception(
                "Incident pipeline execution failed."
            )

            raise
