import pandas as pd
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox

from services.dataset_loader import DatasetLoader

load_dotenv()


class E2BExecutionService:

    def __init__(self):

        loader = DatasetLoader()

        self.datasets = loader.load_datasets()

    def execute(
        self,
        code
    ):

        sandbox = None

        try:

            # ==========================================
            # Create Sandbox
            # ==========================================

            sandbox = Sandbox.create()

            # ==========================================
            # Upload datasets
            # ==========================================

            for dataset_name, df in self.datasets.items():

                csv_content = df.to_csv(
                    index=False
                )

                sandbox.files.write(
                    f"{dataset_name}.csv",
                    csv_content
                )

            # ==========================================
            # Rebuild datasets dictionary
            # ==========================================

            bootstrap_code = """
import pandas as pd

datasets = {}
"""

            for dataset_name in self.datasets.keys():

                bootstrap_code += f"""
datasets["{dataset_name}"] = pd.read_csv(
    "{dataset_name}.csv"
)
"""

            # ==========================================
            # Final code executed in E2B
            # ==========================================

            final_code = (
                bootstrap_code
                + "\n"
                + code
            )

            print("\n===== E2B CODE =====")
            print(final_code)

            # ==========================================
            # Execute
            # ==========================================

            execution = sandbox.run_code(
                final_code
            )

            print("\n===== E2B EXECUTION =====")
            print(execution)

            # ==========================================
            # STDOUT
            # ==========================================

            output = ""

            try:

                if hasattr(execution, "logs"):

                    stdout_logs = (
                        execution.logs.stdout
                    )

                    output = "\n".join(
                        str(log)
                        for log in stdout_logs
                    )

            except Exception:

                pass

            # If print(result) exists
            if output.strip():

                return {

                    "type": "text",

                    "data": output
                }

            # ==========================================
            # Fallback: execution results
            # ==========================================

            try:

                if hasattr(
                    execution,
                    "results"
                ):

                    results = (
                        execution.results
                    )

                    if results:

                        return {

                            "type": "text",

                            "data": str(results)
                        }

            except Exception:

                pass

            # ==========================================
            # Nothing returned
            # ==========================================

            return {

                "type": "text",

                "data":
                    "No output returned."
            }

        except Exception as error:

            return {

                "type": "error",

                "data": str(error)
            }

        finally:

            try:

                if sandbox:

                    sandbox.kill()

            except Exception:

                pass