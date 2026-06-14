from ollama import chat

response = chat(
    model="qwen3:4b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly OK"
        }
    ]
)

print(response["message"]["content"])