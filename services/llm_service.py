import json
from ollama import chat


class LLMService:

    def __init__(self):
        self.model = "qwen2.5:1.5b"

    def understand_query(
        self,
        question,
        contexts=None
    ):

        prompt = f"""
You are a query understanding agent.

Convert the user's question into JSON.

Allowed intents:
- aggregation
- ranking
- comparison
- count
- filter
- unknown

Allowed operations:
- sum
- max
- min
- compare
- count
- filter

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

Examples:

Question:
What is the profit of Reliance?

Output:
{{
    "intent": "aggregation",
    "metric": "Profit",
    "entities": ["Reliance"],
    "operation": "sum",
    "filters": [],
    "time_period": null
}}

Question:
Which stock has the highest profit?

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

        content = response["message"]["content"].strip()

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