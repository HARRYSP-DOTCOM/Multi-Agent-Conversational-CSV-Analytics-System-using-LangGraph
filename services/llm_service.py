import json
from ollama import chat

class LLMService:

    def __init__(self):
        self.model = "qwen2.5:1.5b"

    # ==================================================
    # CONVERSATIONAL MEMORY
    # ==================================================

    def check_conversational_memory(self, question, chat_history):
        if not chat_history or len(chat_history) <= 1:
            return None
        
        # Format history
        history_text = ""
        for msg in chat_history[:-1]: # Exclude the current question
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            if isinstance(content, dict):
                content = str(content.get("data", content))
            history_text += f"{role}: {content}\n"
            
        prompt = f"""You are a strict cache-checking AI. 
Read the Conversation History carefully. Does the history ALREADY contain the exact answer to the Latest Question?
If the Latest Question asks for something new (like a different quantity, a new list, or a new fact not present in the history), you MUST output "found": false.

Output ONLY valid JSON in this format:
{{"found": true/false, "answer": "the exact answer from history or null"}}

Conversation History:
{history_text}

Latest Question: "{question}"
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
        
        # Parse the JSON response
        import json, re
        
        # Try to extract json if it's wrapped in markdown code blocks
        match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
        else:
            match = re.search(r"```\n(.*?)\n```", content, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                
        try:
            parsed = json.loads(content)
            if parsed.get("found") is True and parsed.get("answer"):
                return str(parsed["answer"])
        except Exception:
            pass
            
        return None

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
        valid_keys = []
        try:
            if isinstance(contexts_json, str):
                import json
                schemas = json.loads(contexts_json)
            else:
                schemas = contexts_json
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
6. IMPORTANT: The key in datasets[...] MUST MATCH the subject of the question! If the question asks about "stocks", use datasets["stocks"]. Do NOT invent or substitute dataset keys like "sales_data" unless that exact key appears in the schema.
7. CRITICAL: You MUST use one of the following valid keys: {keys_str}. If the question is ambiguous, just pick the FIRST key from this list: {keys_str}.
8. CRITICAL: Column names are strictly CASE-SENSITIVE. You MUST use the exact capitalization shown in the schema (e.g. if the schema says "UNITS", do not use "Units" or "units").
9. IMPORTANT: When searching or filtering by text, default to partial case-insensitive matching with `.str.contains("query", case=False, na=False)`. HOWEVER, if the user asks for text that "starts with" a letter/word, you MUST use `.str.lower().str.startswith("query")`. If they ask for text that "ends with", use `.str.lower().str.endswith("query")`.
10. IMPORTANT: If filtering by a year (e.g. 2002) on a column that contains year-month as floats (e.g. 2002.03), you MUST use `df['ColumnName'].astype(int) == 2002` to match all months in that year.
11. CRITICAL: Never fetch web data, APIs, URLs, files outside `datasets`, or current market data. If the question contains web/current/external wording, answer only the uploaded CSV portion.
12. CRITICAL: Do not use undefined variables such as `stocks_df`. Always create variables from `datasets[...]`.
13. IMPORTANT: If your final answer is a raw number or single value, you MUST format it as a descriptive string that includes the name of the entity being queried. (e.g. use `result = f"The profit for Reliance is {{profit}}"` instead of `result = profit`).

Examples:

Question:
Show first 5 rows of data.

```python
# Assuming 'sales' is one of the keys in the provided schemas
df = datasets["sales"]
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

        forbidden_fragments = [
            "read_csv(",
            "read_json(",
            "read_html(",
            "read_xml(",
            "read_excel(",
            "requests.",
            "urllib",
            "http://",
            "https://",
            "api.",
            "open("
        ]

        # If it really violates, just let E2B sandbox handle it or fail!
        # The E2B sandbox is isolated. We should not blindly replace their code 
        # with a .describe() fallback because that ignores the user's question!
        for fragment in forbidden_fragments:
            if fragment.lower() in code.lower():
                # We'll just replace the forbidden fragment with a comment
                # to break it, so it will error and retry cleanly
                code = code.replace(fragment, f"# FORBIDDEN: {fragment} ")

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
6. ASSUME the data analysis result is the correct and complete answer to the user's question. For example, if the user asks "who are the HR employees?" and the result is "['Alice']", your response must be "The HR employee is Alice." Do NOT say the information is missing.
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

    def format_hybrid_response(
        self,
        question,
        csv_result,
        web_context
    ):

        prompt = f"""
You must combine two pieces of information to answer the user's question.

User Question: "{question}"

Fact 1 (From user's private CSV file):
{csv_result}

Fact 2 (From public web search):
{web_context}

Write a single, short response that explicitly states the information from Fact 1 and Fact 2. You MUST include the exact value from Fact 1. Do not ignore Fact 1.
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

        return response["message"]["content"].strip()

    def format_web_response(
        self,
        question,
        web_context
    ):
        q_lower = question.lower()
        if "time" in q_lower and ("current" in q_lower or "now" in q_lower or "what is" in q_lower):
            import datetime
            try:
                import zoneinfo
                tz_mapping = {
                    "ist": "Asia/Kolkata", "india": "Asia/Kolkata", "gmt": "GMT", "utc": "UTC",
                    "pst": "America/Los_Angeles", "est": "America/New_York", "america": "America/New_York",
                    "uk": "Europe/London", "japan": "Asia/Tokyo"
                }
                target_tz = None
                tz_name = ""
                
                for term, tz in tz_mapping.items():
                    if f"in {term}" in q_lower or f"for {term}" in q_lower or q_lower.endswith(term):
                        target_tz = tz
                        tz_name = term.upper()
                        break
                
                if not target_tz:
                    for tz_str in zoneinfo.available_timezones():
                        city = tz_str.split("/")[-1].lower().replace("_", " ")
                        if f"in {city}" in q_lower or f"for {city}" in q_lower or q_lower.endswith(city):
                            target_tz = tz_str
                            tz_name = city.title()
                            break

                if target_tz:
                    dt = datetime.datetime.now(zoneinfo.ZoneInfo(target_tz))
                    return f"The current time in {tz_name} is {dt.strftime('%A, %B %d, %Y %I:%M %p')}."
            except Exception:
                pass
                
            current_time_str = datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p (System Local Time)")
            return f"The current system time is {current_time_str}."

        import datetime
        current_time_str = datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p (System Local Time)")
        
        prompt = f"""
You are a direct question-answering assistant.
Current System Date & Time: {current_time_str}

USER QUESTION:
"{question}"

WEB SEARCH CONTEXT:
{web_context}

CRITICAL RULES:
1. Answer the question directly. Do NOT write meta-commentary like "The user asked..." or "The web search provided...".
2. Do NOT say "Based on the context" or "According to the search results". Just give the direct answer.
3. For time questions, use the 'Current System Date & Time' (which is IST / UTC+5:30) as your base, and calculate the requested timezone difference. Do NOT just repeat the system time if they ask for a different timezone!
4. If the context does not contain the answer (and it's not a time question), say "I could not find the answer in the web search results."
5. If it's a list, output the actual list items clearly.
6. Include source URLs at the bottom if they are available in the context.
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

        return response["message"]["content"].strip()
