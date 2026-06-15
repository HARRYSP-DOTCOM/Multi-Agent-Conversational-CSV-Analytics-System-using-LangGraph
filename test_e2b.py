from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
import os

load_dotenv()

print("API Key:", os.getenv("E2B_API_KEY"))

sandbox = Sandbox.create()

print("Sandbox Created!")
print("Sandbox ID:", sandbox.sandbox_id)

execution = sandbox.run_code("""
result = 10 + 20
print(result)
""")

print("\nExecution Result:")
print(execution)

sandbox.kill()

print("\nSandbox Closed.")