import json
from ollama import chat
class LLMService:
    def __init__(self):
        self.model = "qwen3:4b"
    def understand_query(
        self,
        question,
        contexts
    ): 
        prompt = f"""
You are a query understanding agent.

Available dataset contexts:

{json.dumps(contexts, indent=2)}

Extract the user's intent.

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
           