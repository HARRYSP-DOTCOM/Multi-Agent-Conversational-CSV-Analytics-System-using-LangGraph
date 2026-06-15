import io
import contextlib
import pandas as pd

from services.dataset_loader import DatasetLoader


class PythonExecutionService:

    def __init__(self):

        loader = DatasetLoader()

        self.datasets = loader.load_datasets()

    def execute(
        self,
        code
    ):

        namespace = {

            "pd": pd,

            "datasets": self.datasets
        }

        stdout = io.StringIO()

        try:

            with contextlib.redirect_stdout(
                stdout
            ):

                exec(
                    code,
                    namespace
                )

            output = stdout.getvalue()

            result = namespace.get(
                "result",
                None
            )

            # DataFrame output
            if isinstance(
                result,
                pd.DataFrame
            ):

                return {

                    "type": "dataframe",

                    "data": result
                }

            # Series output
            if isinstance(
                result,
                pd.Series
            ):

                return {

                    "type": "series",

                    "data": result
                }

            # Scalar/text output
            return {

                "type": "text",

                "data":
                    str(result)
                    if result is not None
                    else output
            }

        except Exception as error:

            return {

                "type": "error",

                "data": str(error)
            }