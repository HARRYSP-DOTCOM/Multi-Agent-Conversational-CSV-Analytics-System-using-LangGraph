from pipelines.day1_pipeline import (
    Day1Pipeline
)

pipeline = Day1Pipeline()
summary = (
    pipeline.initialize_semantic_memory()
)

print("\nSummary:")

print(summary)