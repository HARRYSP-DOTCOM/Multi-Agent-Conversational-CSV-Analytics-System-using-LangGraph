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
2. Store the final answer in a variable called `result`.
3. Do NOT import libraries.
4. Use only pandas operations.
5. You MUST enclose your Python code inside a ```python ... ``` markdown block. Do not output any conversational text or prefixes.
6. IMPORTANT: The key in datasets[...] MUST MATCH the subject of the question! If the question asks about "stocks", use datasets["stocks"]. If it asks about "employees", use datasets["employees"].
9. IMPORTANT: When searching or filtering by text (like names), ALWAYS use partial case-insensitive matching with `.str.contains("query", case=False, na=False)`.

Examples:

Question:
Show first 5 rows of users.

```python
df = datasets["users"]
result = df.head()
```

Question:
Which employee has the highest salary?

```python
df = datasets["employees"]
idx = df["Salary"].idxmax()
result = df.loc[idx]
```

Question:
Which stocks have a profit greater than 100?

```python
df = datasets["stocks"]
result = df[df["Profit"] > 100]
```

Question:
What is the average revenue in sales?

```python
df = datasets["sales"]
result = df["Revenue"].mean()
```

Question:
Top 5 items in catalog by amount.

```python
df = datasets["catalog"]
result = df.sort_values(
    "amount",
    ascending=False
).head(5)
```
"""

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        raw_content = response["message"]["content"]
        
        import re
        match = re.search(r"```python\n(.*?)\n```", raw_content, re.DOTALL)
        if match:
            code = match.group(1).strip()
        else:
            code = raw_content.replace("```python", "").replace("```", "").strip()
            if code.lower().startswith("code:"):
                code = code[5:].strip()

        print("\nGenerated Code:")
        print(code)

        return code

    # ==================================================
    # FORMAT RESPONSE
    # ==================================================

    def format_response(
        self,
        question,
        raw_result
    ):

        prompt = f"""
You are a helpful data assistant.
The user asked: "{question}"
The data analysis returned:
{raw_result}

Provide a clear, concise, natural-language response to answer the user's question based ONLY on the data provided.
Do NOT use markdown tables if the data is large, just summarize it clearly or provide the direct answer.
Do NOT output raw pandas representations like 'dtype: object'.
If the data is an error, politely state that you couldn't find the answer due to an error.
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

        content = response["message"]["content"].strip()
        return content