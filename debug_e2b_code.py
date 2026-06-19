
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


datasets["stocks"] = pd.read_csv("stocks.csv")
for col in datasets["stocks"].columns:
    if datasets["stocks"][col].dtype == "object":
        try:
            # Attempt to strip commas/dollar signs and convert to numeric
            cleaned = datasets["stocks"][col].astype(str).str.replace(r"[$,]", "", regex=True)
            datasets["stocks"][col] = pd.to_numeric(cleaned)
        except:
            pass

if datasets:
    df = list(datasets.values())[0]

# Assuming 'stocks' is one of the keys in the provided schemas
df = datasets["stocks"]

result = df.loc[df['Profit'].idxmax()]['Stock Name']
result += ', ' + result.split(' ')[1]

result += ' (Owner: ' + df.loc[df['Profit'].idxmax(), 'Ticker'] + ')'
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
