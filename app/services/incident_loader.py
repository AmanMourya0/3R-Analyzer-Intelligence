"""
Incident dataset loader.
"""

from pathlib import Path

import pandas as pd

from app.utils.logger import logger


class IncidentLoader:

    def __init__(self, filepath: str):

        self.filepath = filepath

    def load(self) -> pd.DataFrame:

        try:

            extension = Path(self.filepath).suffix.lower()

            if extension == ".csv":

                df = pd.read_csv(self.filepath)

            elif extension in [".xlsx", ".xls"]:

                df = pd.read_excel(self.filepath)

            else:

                raise ValueError(
                    f"Unsupported file type: {extension}"
                )

            logger.info(
                "Loaded %s incidents.",
                len(df)
            )

            return df

        except Exception:

            logger.exception(
                "Failed to load dataset."
            )

            raise