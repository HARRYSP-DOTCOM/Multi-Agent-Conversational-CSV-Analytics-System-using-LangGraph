import os
import pandas as pd

class DatasetLoader:

    def __init__(
        self,
        data_directory="uploads"
    ):

        self.data_directory = data_directory
        self.data_directory = data_directory
    def discover_csv_files(self):
        csv_files = []
        for file_name in os.listdir(self.data_directory):
            if file_name.endswith(".csv"):
                csv_files.append(file_name)
        return csv_files
    def load_datasets(self):
        datasets = {}
        csv_files = self.discover_csv_files()
        for file_name in csv_files:
            file_path = os.path.join(
                self.data_directory,
                file_name
            )
            dataset_name = os.path.splitext(file_name)[0]
            df = pd.read_csv(file_path)
            datasets[dataset_name] = df
        return datasets
    
    def get_dataset_summary(self, datasets):
        summaries = {}
        for name, df in datasets.items():
            summaries[name] = {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "column_names": list(df.columns)
            }
        return summaries