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

from pandas.core.strings.accessor import StringMethods

# Monkey-patch pandas to make column access case-insensitive if exact match fails
_original_getitem = pd.DataFrame.__getitem__
def _case_insensitive_getitem(self, key):
    if isinstance(key, str) and key not in self.columns:
        lower_cols = {str(c).lower(): c for c in self.columns}
        if key.lower() in lower_cols:
            return _original_getitem(self, lower_cols[key.lower()])
    return _original_getitem(self, key)
pd.DataFrame.__getitem__ = _case_insensitive_getitem

# Monkey-patch pandas Series equality to make all string comparisons case-insensitive
_original_eq = pd.Series.__eq__
def _case_insensitive_eq(self, other):
    if isinstance(other, str):
        return _original_eq(self.astype(str).str.lower(), other.lower())
    return _original_eq(self, other)
pd.Series.__eq__ = _case_insensitive_eq

# Monkey-patch StringMethods for case-insensitivity
_original_startswith = StringMethods.startswith
def _case_insensitive_startswith(self, pat, na=None):
    if isinstance(pat, str):
        lower_series = self._parent.astype(str).str.lower()
        return _original_startswith(lower_series.str, pat.lower(), na=na)
    return _original_startswith(self, pat, na=na)
StringMethods.startswith = _case_insensitive_startswith

_original_endswith = StringMethods.endswith
def _case_insensitive_endswith(self, pat, na=None):
    if isinstance(pat, str):
        lower_series = self._parent.astype(str).str.lower()
        return _original_endswith(lower_series.str, pat.lower(), na=na)
    return _original_endswith(self, pat, na=na)
StringMethods.endswith = _case_insensitive_endswith

_original_contains = StringMethods.contains
def _case_insensitive_contains(self, pat, case=True, flags=0, na=None, regex=True):
    return _original_contains(self, pat, case=False, flags=flags, na=na, regex=regex)
StringMethods.contains = _case_insensitive_contains

class SafeDatasetDict(dict):
    def __getitem__(self, key):
        if key not in self and len(self) > 0:
            # If the AI hallucinates a dataset name like "uploaded_file" or "users",
            # gracefully fall back to the first available dataset instead of crashing.
            return list(self.values())[0]
        return super().__getitem__(key)

datasets = SafeDatasetDict()

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
for col in datasets["{dataset_name}"].columns:
    if datasets["{dataset_name}"][col].dtype == "object":
        try:
            # Attempt to strip commas/dollar signs and convert to numeric
            cleaned = datasets["{dataset_name}"][col].astype(str).str.replace(r"[$,]", "", regex=True)
            datasets["{dataset_name}"][col] = pd.to_numeric(cleaned)
        except:
            pass
'''

            dataset_loading_code += """
if datasets:
    df = list(datasets.values())[0]
"""

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

try:
    _final_res = result
except NameError:
    _final_res = "Error: The AI wrote code but forgot to assign the final answer to the 'result' variable."

print("E2B_RESULT:" + format_result(_final_res))
"""

            print("\n===== E2B CODE =====\n")
            print(full_code)

            print("\n===== E2B EXECUTION =====")

            with open(os.path.join(os.getcwd(), "debug_e2b_code.py"), "w") as f:
                f.write(full_code)

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