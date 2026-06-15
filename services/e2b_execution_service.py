import os
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox

load_dotenv()


class E2BExecutionService:

    def __init__(self):

        api_key = os.getenv("E2B_API_KEY")

        print("E2B API KEY:", api_key)

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
                file
                for file in os.listdir(uploads_dir)
                if file.endswith(".csv")
            ]

            print("\n===== UPLOADING FILES =====")

            dataset_loading_code = """
import pandas as pd

datasets = {}

"""

            for file_name in csv_files:

                local_path = os.path.join(
                    uploads_dir,
                    file_name
                )

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

                dataset_name = os.path.splitext(
                    file_name
                )[0]

                dataset_loading_code += f'''
datasets["{dataset_name}"] = pd.read_csv("{file_name}")
'''

            full_code = (
                dataset_loading_code
                + "\n"
                + generated_code
            )

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

                output = "\n".join(stdout)

                return {
                    "type": "text",
                    "data": output
                }

            if execution.results:

                return {
                    "type": "text",
                    "data": "\n".join(
                        [
                            str(result)
                            for result in execution.results
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