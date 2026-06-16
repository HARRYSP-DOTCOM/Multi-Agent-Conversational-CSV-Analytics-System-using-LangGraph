import os
import json
import pandas as pd
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
import json
import pandas as pd
import numpy as np

def format_result(res):
    try:
        if isinstance(res, pd.DataFrame):
            data_json = res.to_json(orient="records", date_format="iso")
            return json.dumps({"type": "dataframe", "data": json.loads(data_json)})
        elif isinstance(res, pd.Series):
            data_json = res.to_json(date_format="iso")
            return json.dumps({"type": "series", "data": json.loads(data_json)})
        elif isinstance(res, (int, float, np.integer, np.floating)):
            return json.dumps({"type": "number", "data": float(res)})
        else:
            return json.dumps({"type": "text", "data": str(res)})
    except Exception as e:
        return json.dumps({"type": "error", "data": str(e)})

print("E2B_RESULT:" + format_result(result))
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
            
            e2b_result_json = None

            if (
                execution.logs
                and execution.logs.stdout
            ):

                for line in execution.logs.stdout:
                    line_str = str(line)
                    if "E2B_RESULT:" in line_str:
                        json_str = line_str.split("E2B_RESULT:", 1)[1].strip()
                        try:
                            parsed = json.loads(json_str)
                            
                            res_type = parsed.get("type")
                            res_data = parsed.get("data")
                            
                            if res_type == "dataframe":
                                e2b_result_json = {"type": "dataframe", "data": pd.DataFrame(res_data)}
                            elif res_type == "series":
                                e2b_result_json = {"type": "series", "data": pd.Series(res_data)}
                            elif res_type in ["number", "text", "error"]:
                                e2b_result_json = {"type": res_type, "data": res_data}
                                
                        except Exception as e:
                            print("Failed to parse E2B_RESULT:", e)
                    else:
                        stdout.append(line_str)

            if e2b_result_json is not None:
                return e2b_result_json

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