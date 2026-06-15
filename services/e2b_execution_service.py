import os
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox

load_dotenv()


class E2BExecutionService:

    def __init__(self):

        self.sandbox = Sandbox.create()

        print("E2B EXECUTOR READY")

    def execute(
        self,
        generated_code
    ):

        try:

            uploads_dir = os.path.join(
                os.getcwd(),
                "uploads"
            )

            csv_files = [
                "employees.csv",
                "sales.csv",
                "stocks.csv"
            ]

            print("\n===== UPLOADING FILES =====")

            for file_name in csv_files:

                local_path = os.path.join(
                    uploads_dir,
                    file_name
                )

                if os.path.exists(local_path):

                    with open(
                        local_path,
                        "rb"
                    ) as f:

                        self.sandbox.files.write(
                            file_name,
                            f.read()
                        )

                    print(
                        f"Uploaded: {local_path}"
                    )

                else:

                    print(
                        f"WARNING: {local_path} not found."
                    )

            full_code = """
import pandas as pd

datasets = {}

datasets["employees"] = pd.read_csv("employees.csv")
datasets["sales"] = pd.read_csv("sales.csv")
datasets["stocks"] = pd.read_csv("stocks.csv")

"""

            full_code += generated_code

            full_code += """

print(result)
"""

            print("\n===== E2B CODE =====\n")
            print(full_code)

            print("\n===== E2B EXECUTION =====")

            execution = self.sandbox.run_code(
                full_code
            )

            print(execution)

            if execution.error:

                return {
                    "type": "error",
                    "data": (
                        f"{execution.error.name}: "
                        f"{execution.error.value}"
                    )
                }

            stdout = []

            if (
                execution.logs
                and execution.logs.stdout
            ):

                for line in execution.logs.stdout:

                    stdout.append(str(line))

            if stdout:

                return {
                    "type": "text",
                    "data": "\n".join(stdout)
                }

            if execution.results:

                return {
                    "type": "text",
                    "data": "\n".join(
                        [
                            str(r)
                            for r in execution.results
                        ]
                    )
                }

            return {
                "type": "text",
                "data": "No output returned."
            }

        except Exception as e:

            print("\n===== E2B ERROR =====")
            print(e)

            return {
                "type": "error",
                "data": str(e)
            }