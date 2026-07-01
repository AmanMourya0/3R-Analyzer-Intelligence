"""
Dataset preprocessing.
"""

import pandas as pd
from app.constants import (
    ASSIGNMENT_GROUP,
    BUSINESS_SERVICE,
    CATEGORY,
    COMBINED_TEXT,
    CONFIGURATION_ITEM,
    DESCRIPTION,
    INCIDENT_NUMBER,
    PRIORITY,
    REGION,
    RESOLUTION_NOTES,
    SHORT_DESCRIPTION,
    STATE,
    SUBCATEGORY,
)


from app.utils.logger import logger


class Preprocessor:

    COLUMN_MAPPING = {

        "Incident Number": "incident_number",

        "Short Description": "short_description",

        "Description": "description",

        "Category": "category",

        "Subcategory": "subcategory",

        "Priority": "priority",

        "State": "state",

        "Assignment Group": "assignment_group",

        "Configuration Item (Application)": "configuration_item",

        "Business Service": "business_service",

        "Region": "region",

        "Created Date": "created_date",

        "Resolved Date": "resolved_date",

        "Resolution Notes": "resolution_notes",

        "Problem Candidate": "problem_candidate"

    }

    REQUIRED_COLUMNS = [

        SHORT_DESCRIPTION,

        DESCRIPTION

    ]

    TEXT_COLUMNS = [

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

        RESOLUTION_NOTES

    ]

    def clean(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        try:

            df.rename(
                columns=self.COLUMN_MAPPING,
                inplace=True
            )

            for column in self.TEXT_COLUMNS:

                if column in df.columns:

                    df[column] = df[column].fillna("")

            for column in self.REQUIRED_COLUMNS:

                df[column] = (

                    df[column]

                    .astype(str)

                    .str.lower()

                    .str.strip()

                )

            df[COMBINED_TEXT] = (

                df["short_description"]

                + " "

                + df["description"]

                + " "

                + df["category"]

                + " "

                + df["subcategory"]

                + " "

                + df["configuration_item"]

            )

            logger.info(
                "Preprocessing completed."
            )

            return df

        except Exception:

            logger.exception(
                "Preprocessing failed."
            )

            raise
