import json
from ollama import chat


class LLMService:

    def __init__(self):

        self.model = "qwen2.5:1.5b"

    # ==========================================
    # Existing JSON Query Understanding
    # ==========================================
    def understand_query(
        self,
        question,
        contexts=None
    ):

        prompt = f"""
You are a query understanding agent.

Convert the user's question into JSON.

Return ONLY valid JSON.

Schema:

{{
    "intent": "",
    "metric": "",
    "entities": [],
    "operation": "",
    "filters": [],
    "time_period": null
}}

If unrelated to the datasets, return:

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
            .strip()
        )

        try:

            content = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            return json.loads(content)

        except Exception:

            return {
                "intent": "unknown",
                "metric": None,
                "entities": [],
                "operation": None,
                "filters": [],
                "time_period": None,
                "raw_response": content
            }

    # ==========================================
    # NEW: Python Generation
    # ==========================================
    def generate_python(
        self,
        question,
        contexts
    ):

        prompt = f"""
You are a Python data analyst.

Available datasets and their schemas:

{contexts}

A variable called datasets already exists.

datasets is a dictionary of pandas DataFrames.

Rules:
1. Generate ONLY executable Python code.
2. Store the final answer in a variable named result.
3. Do NOT import libraries.
4. Do NOT explain anything.
5. Do NOT use markdown fences.
6. Use only pandas operations.
7. Use only datasets and columns that exist in the provided contexts.
8. If the answer should be a table, assign the DataFrame to result.
9. If the answer should be a scalar/text value, assign it to result.
10. Always print(result) as the final line of the code.

Examples:

Question:
Show first 5 rows of stocks.

Code:
df = datasets["stocks"]
result = df.head()
print(result)

Question:
Which employee has the highest salary?

Code:
df = datasets["employees"]
idx = df["Salary"].idxmax()
result = df.loc[idx]

Question:
What is the average age of employees?

Code:
df = datasets["employees"]
result = df["Age"].mean()

Question:
Top 5 products by sales.

Code:
df = datasets["sales"]
result = df.sort_values(
    "Sales",
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

        return code