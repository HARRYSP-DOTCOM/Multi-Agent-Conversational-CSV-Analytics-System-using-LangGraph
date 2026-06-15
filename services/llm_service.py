import json
from ollama import chat


class LLMService:

    def __init__(self):
        self.model = "qwen2.5:1.5b"

    # ==================================================
    # QUERY UNDERSTANDING
    # ==================================================

    def understand_query(
        self,
        question,
        contexts=None
    ):

        prompt = f"""
You are a query understanding agent.

Convert the user's question into JSON.

Choose intent ONLY from:

- aggregation
- ranking
- comparison
- count
- filter
- unknown

Choose operation ONLY from:

- sum
- max
- min
- compare
- count
- filter
- average

Return ONLY valid JSON.

Schema:

{{
    "intent": "",
    "metric": null,
    "entities": [],
    "operation": null,
    "filters": [],
    "time_period": null
}}

Examples:

Question:
Which company has highest profit?

Output:
{{
    "intent": "ranking",
    "metric": "Profit",
    "entities": [],
    "operation": "max",
    "filters": [],
    "time_period": null
}}

Question:
Which company has lowest profit?

Output:
{{
    "intent": "ranking",
    "metric": "Profit",
    "entities": [],
    "operation": "min",
    "filters": [],
    "time_period": null
}}

Question:
Compare Reliance and TCS profits.

Output:
{{
    "intent": "comparison",
    "metric": "Profit",
    "entities": ["Reliance", "TCS"],
    "operation": "compare",
    "filters": [],
    "time_period": null
}}

Question:
How many employees are there?

Output:
{{
    "intent": "count",
    "metric": null,
    "entities": [],
    "operation": "count",
    "filters": [],
    "time_period": null
}}

Question:
What is the average salary of employees?

Output:
{{
    "intent": "aggregation",
    "metric": "Salary",
    "entities": [],
    "operation": "average",
    "filters": [],
    "time_period": null
}}

Question:
Show employees from HR.

Output:
{{
    "intent": "filter",
    "metric": null,
    "entities": [],
    "operation": "filter",
    "filters": [
        {{
            "column": "Department",
            "value": "HR"
        }}
    ],
    "time_period": null
}}

Question:
Tell me a joke.

Output:
{{
    "intent": "unknown",
    "metric": null,
    "entities": [],
    "operation": null,
    "filters": [],
    "time_period": null
}}

Question:
{question}
"""

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = (
            response["message"]["content"]
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            parsed = json.loads(content)

            print("\nParsed JSON:")
            print(parsed)

            return parsed

        except Exception:

            print("\nLLM JSON Parse Failed:")
            print(content)

            return {
                "intent": "unknown",
                "metric": None,
                "entities": [],
                "operation": None,
                "filters": [],
                "time_period": None
            }

    # ==================================================
    # E2B PYTHON GENERATION
    # ==================================================

    def generate_python(
        self,
        question,
        contexts
    ):

        prompt = f"""
You are a Python data analyst.

Available datasets and schemas:

{contexts}

A variable called datasets already exists.

datasets is a dictionary of pandas DataFrames.

Rules:

1. Generate ONLY executable Python code.
2. Store the final answer in a variable called result.
3. Do NOT import libraries.
4. Do NOT explain anything.
5. Do NOT use markdown fences.
6. Use only pandas operations.
7. Use ONLY datasets and columns that exist in the provided schemas.
8. If calculating averages, sums, maxima, or minima, use ONLY the relevant numeric column.
9. NEVER perform aggregations on the entire DataFrame.
10. If the answer is tabular, assign the DataFrame to result.
11. If the answer is scalar/text, assign the value to result.

Examples:

Question:
Show first 5 rows of stocks.

Code:
df = datasets["stocks"]
result = df.head()

Question:
Show first 3 rows of sales.

Code:
df = datasets["sales"]
result = df.head(3)

Question:
Which employee has the highest salary?

Code:
df = datasets["employees"]
idx = df["Salary"].idxmax()
result = df.loc[idx]

Question:
What is the average salary of employees?

Code:
df = datasets["employees"]
result = df["Salary"].mean()

Question:
What is the average revenue in sales?

Code:
df = datasets["sales"]
result = df["Revenue"].mean()

Question:
Which company has the highest profit?

Code:
df = datasets["stocks"]
idx = df["Profit"].idxmax()
result = df.loc[idx]

Question:
Which company has the lowest profit?

Code:
df = datasets["stocks"]
idx = df["Profit"].idxmin()
result = df.loc[idx]

Question:
Top 5 companies by profit.

Code:
df = datasets["stocks"]
result = df.sort_values(
    "Profit",
    ascending=False
).head(5)

Question:
{question}
"""

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        code = (
            response["message"]["content"]
            .replace("```python", "")
            .replace("```", "")
            .strip()
        )

        print("\nGenerated Code:")
        print(code)

        return code