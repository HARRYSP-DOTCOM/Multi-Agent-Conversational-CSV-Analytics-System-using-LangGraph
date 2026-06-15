from services.e2b_execution_service import (
    E2BExecutionService
)

executor = E2BExecutionService()

code = """
df = datasets["stocks"]

print(df.head())
"""

response = executor.execute(
    code
)

print(response)