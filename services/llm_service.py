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

    def generate_python(self, question, contexts_json, error_message=None, previous_code=None):
        
        # Extract valid dataset keys
        try:
            import json
            schemas = json.loads(contexts_json)
            valid_keys = list(schemas.keys())
            keys_str = ", ".join(f'"{k}"' for k in valid_keys)
        except:
            keys_str = "the keys provided in the schema"

        prompt = f"""
You are a Python data analyst. You have access to a dictionary called `datasets` containing pandas DataFrames.
The available datasets and their columns are:
{contexts_json}

Your task is to write ONLY Python code to answer the user's question.

RULES:
1. Generate ONLY executable Python code.
2. Store the final answer in a variable called `result`.
3. Do NOT import libraries.
4. Use only pandas operations.
5. You MUST enclose your Python code inside a ```python ... ``` markdown block. Do not output any conversational text or prefixes.
6. IMPORTANT: The key in datasets[...] MUST MATCH the subject of the question! If the question asks about "stocks", use datasets["stocks"].
7. CRITICAL: You MUST use one of the following valid keys: {keys_str}. If the question is ambiguous, just pick the FIRST key from this list: {keys_str}.
8. CRITICAL: Column names are strictly CASE-SENSITIVE. You MUST use the exact capitalization shown in the schema (e.g. if the schema says "UNITS", do not use "Units" or "units").
9. IMPORTANT: When searching or filtering by text, default to partial case-insensitive matching with `.str.contains("query", case=False, na=False)`. HOWEVER, if the user asks for text that "starts with" a letter/word, you MUST use `.str.lower().str.startswith("query")`. If they ask for text that "ends with", use `.str.lower().str.endswith("query")`.
10. IMPORTANT: If filtering by a year (e.g. 2002) on a column that contains year-month as floats (e.g. 2002.03), you MUST use `df['ColumnName'].astype(int) == 2002` to match all months in that year.

Examples:

Question:
Show first 5 rows of data.

```python
# Assuming 'sales_data' is one of the keys in the provided schemas
df = datasets["sales_data"]
result = df.head()
```

Question:
Which person has the highest salary?

```python
# Assuming 'employees' is one of the keys in the provided schemas
df = datasets["employees"]
result = df.loc[df['salary'].idxmax()]
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

        if error_message:
            prompt += f"""
CRITICAL FEEDBACK:
Your previous code failed with the following error:
{error_message}

Previous code you generated:
```python
{previous_code}
```

Please analyze the error, fix the mistake, and generate the corrected Python code.
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
        # Try to find ```python ... ``` or just ``` ... ```
        match = re.search(r"```(?:python)?\n(.*?)\n```", raw_content, re.DOTALL | re.IGNORECASE)
        if match:
            code = match.group(1).strip()
        else:
            # Fallback if the AI completely forgot markdown blocks
            code = raw_content.replace("```python", "").replace("```", "").strip()
            if code.lower().startswith("code:"):
                code = code[5:].strip()
            
            # If the code contains conversational text, try to extract just the python lines
            lines = code.split("\n")
            python_lines = []
            for line in lines:
                if "=" in line or line.startswith("df") or line.startswith("result"):
                    python_lines.append(line)
            
            if python_lines:
                code = "\n".join(python_lines)
            else:
                # Complete hallucination: no valid python lines found
                code = "result = 'Error: The AI failed to generate valid Python code.'"

        # UNCONDITIONAL CHECK: If the AI forgot to assign to 'result', force the last line to be the result
        if "result" not in code:
            lines = code.split("\n")
            lines[-1] = "result = " + lines[-1]
            code = "\n".join(lines)

        # Auto-fix float year filtering if the AI ignored Rule 10
        import re
        code = re.sub(r"\[\s*['\"]?Period['\"]?\s*\]\s*==\s*(\d{4})", r"['Period'].astype(int) == \1", code, flags=re.IGNORECASE)
        code = re.sub(r"df\s*\.\s*Period\s*==\s*(\d{4})", r"df['Period'].astype(int) == \1", code, flags=re.IGNORECASE)

        # Auto-fix common LLM syntax error where it puts .sum() or .count() inside the df[] brackets
        # e.g., df[df['Name'].str.startswith('Z').sum()] -> df['Name'].str.startswith('Z').sum()
        import re
        code = re.sub(r"df\[(df\[.*?\](?:\.[a-zA-Z_]\w*(?:\([^)]*\))?)*\.(?:sum|count)\(\))\]", r"\1", code)

        # Deterministic safeguard: If the user asked for "starts with", aggressively convert contains to startswith
        # to prevent the 1.5B LLM from stubbornly ignoring the prompt instructions
        q_lower = question.lower()
        if "start with" in q_lower or "starts with" in q_lower or "starting with" in q_lower:
            code = code.replace(".str.contains(", ".str.startswith(")
        elif "end with" in q_lower or "ends with" in q_lower or "ending with" in q_lower:
            code = code.replace(".str.contains(", ".str.endswith(")

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
The data analysis returned EXACTLY:
{raw_result}

Provide a clear, concise, natural-language response to answer the user's question based ONLY on the data provided.

CRITICAL RULES:
1. DO NOT ALTER, CONVERT, OR "CORRECT" ANY NUMBERS, DATES, OR VALUES.
2. You MUST copy the values EXACTLY as they appear in the data analysis result. If the raw data says a value is "rgb(0,50,0)", you MUST output "rgb(0,50,0)" and NEVER hallucinate standard knowledge like "(0,255,0)".
3. Do NOT use markdown tables if the data is large, just summarize it clearly or provide the direct answer.
4. Do NOT output raw pandas representations like 'dtype: object' or 'Name: RGB'.
5. If the data is an error, politely state that you couldn't find the answer due to an error.
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