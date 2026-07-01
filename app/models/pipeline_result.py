"""
Pipeline Result Domain Model

Represents the complete output of the AI pipeline.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from dataclasses import dataclass
from typing import List

import pandas as pd

from app.models.cluster_summary import ClusterSummary
from app.models.recurrence_result import RecurrenceResult


@dataclass(slots=True)
class PipelineResult:
    """
    Represents the complete AI processing result.
    """

    dataframe: pd.DataFrame

    cluster_summaries: List[ClusterSummary]

    recurrence_results: List[RecurrenceResult]