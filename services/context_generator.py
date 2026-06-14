import json
import os
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

class ContextGenerator:
    """
    Generates dataset metadata/context.
    """

    def __init__(self, output_directory="contexts"):
        self.output_directory = output_directory

    def detect_datatype(self, series):
        """
        Convert pandas dtypes into simpler types.
        """
        if is_bool_dtype(series):
            return "boolean"
        if is_numeric_dtype(series):
            if pd.api.types.is_integer_dtype(series):
                return "int"
            return "float"
        if is_datetime64_any_dtype(series):
            return "date"
        return "string"
    
    def profile_column(self, series):
        """
        Generate metadata for a single column.
        """
        datatype = self.detect_datatype(series)
        profile = {
            "name": series.name,
            "datatype": datatype,
            "missing_values": int(series.isna().sum()),
        }
        if datatype in ["int", "float"]:
            profile["min"] = float(series.min())
            profile["max"] = float(series.max())
            profile["mean"] = float(series.mean())
        elif datatype == "string":
             is_date, parsed_dates = self.try_parse_date(series)
             if is_date:
                profile["datatype"] = "date"
                profile["format"] = "YYYY-MM-DD"
                profile["min"] = str(parsed_dates.min().date())
                profile["max"] = str(parsed_dates.max().date())
                return profile
             unique_values = series.dropna().nunique()
             profile["unique_count"] = int(unique_values)
             profile["top_values"] = (
                series.dropna()
                .value_counts()
                .head(5)
                .index.tolist()
            )
        return profile
    
    def try_parse_date(self, series):
        """
        Check whether a string column looks like dates.
        """
        try:
            parsed = pd.to_datetime(
                series.dropna(),
                errors="raise"
            )
            return True, parsed
        except Exception:
            return False, None
        
    def generate_context(self, dataset_name, dataframe):
        """
        Generate metadata for an entire dataset.
        """
        context = {
            "dataset": dataset_name,
            "row_count": int(dataframe.shape[0]),
            "column_count": int(dataframe.shape[1]),
            "columns": [],
        }
        for column in dataframe.columns:

            profile = self.profile_column(
                dataframe[column]
            )
            context["columns"].append(profile)

        return context

    def save_context(self, context):
        """
        Persist context to disk.
        """
        os.makedirs(
            self.output_directory,
            exist_ok=True
        )
        filename = (
            f"{context['dataset']}_context.json"
        )
        filepath = os.path.join(
            self.output_directory,
            filename,
        )
        with open(filepath, "w") as file:
            json.dump(
                context,
                file,
                indent=4,
            )
        return filepath