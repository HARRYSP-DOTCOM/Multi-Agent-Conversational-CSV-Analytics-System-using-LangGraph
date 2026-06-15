from services.python_execution_service import (
    PythonExecutionService
)

executor = PythonExecutionService()

code = """
df = datasets["stocks"]

result = df[
    ["Stock Name", "Profit"]
].head()
"""

response = executor.execute(
    code
)

print(response)