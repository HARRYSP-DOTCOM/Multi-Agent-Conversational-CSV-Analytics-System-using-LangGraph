class EmbeddingPreparation:
    """
    Responsible for identifying embeddable values.
    """

    def __init__(self):
        pass

    def is_identifier_column(
        self,
        series,
        profile
    ):
        """
        Determine whether a column is an identifier.
        """
        if profile["datatype"] != "string":
            return False
        total_rows = len(series)
        if total_rows == 0:
            return False
        unique_values = series.dropna().nunique()
        uniqueness_ratio = (
            unique_values / total_rows
        )
        return uniqueness_ratio > 0.7
    
    def is_categorical_column(
        self,
        series,
        profile
    ):
        """
        Determine whether a column is categorical.
        """
        if profile["datatype"] != "string":
            return False
        total_rows = len(series)
        if total_rows == 0:
            return False
        unique_values = (
            series.dropna().nunique()
        )
        uniqueness_ratio = (
            unique_values / total_rows
        )
        return uniqueness_ratio <= 0.7
    

    def get_embeddable_columns(
        self,
        dataframe,
        context
    ):
        """
        Identify columns suitable for embeddings.
        """
        embeddable_columns = []
        for profile in context["columns"]:
            column_name = profile["name"]
            series = dataframe[column_name]
            if self.is_identifier_column(
                series,
                profile
            ):
                embeddable_columns.append({
                    "column": column_name,
                    "type": "identifier"
                })
            elif self.is_categorical_column(
                series,
                profile
            ):
                embeddable_columns.append({
                    "column": column_name,
                    "type": "categorical"
                })
        return embeddable_columns
    
    def extract_values(
        self,
        dataframe,
        dataset_name,
        embeddable_columns
    ):
        """
        Extract unique values and metadata.
        """
        records = []
        for column_info in embeddable_columns:
            column = column_info["column"]
            column_type = column_info["type"]
            values = (
                dataframe[column]
                .dropna()
                .unique()
            )
            for value in values:
                records.append({
                    "value": str(value),
                    "table": dataset_name,
                    "column": column,
                    "column_type": column_type
                })
        return records