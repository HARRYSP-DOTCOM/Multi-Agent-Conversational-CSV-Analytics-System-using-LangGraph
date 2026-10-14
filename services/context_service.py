"""
Context Service for loading serialized dataset metadata.

Demonstrates:
- Subclassing `BaseService`
- Dictionary comprehension for batch deserialization
- Modern filesystem access with `pathlib.Path`
- Type hinting with `Dict`, `Any`, `Union`
"""

import json
from pathlib import Path
from typing import Dict, Any, Union
from core.base_service import BaseService


class ContextService(BaseService):
    """
    Manages loading and querying persisted dataset context profiles.
    """

    def __init__(self, context_directory: Union[str, Path] = "contexts") -> None:
        super().__init__(service_name="context_service")
        self._context_directory = Path(context_directory)
        self._context_directory.mkdir(parents=True, exist_ok=True)
        self._initialized = True

    @property
    def context_directory(self) -> Path:
        """Returns the context storage directory."""
        return self._context_directory

    def load_contexts(self) -> Dict[str, Any]:
        """
        Loads all context JSON files into memory.
        Demonstrates dictionary comprehension and pathlib traversal.

        Returns:
            Dictionary mapping dataset name to its parsed JSON metadata.
        """
        if not self._context_directory.exists():
            return {}

        contexts: Dict[str, Any] = {}
        for json_file in self._context_directory.glob("*.json"):
            dataset_name = json_file.stem.replace("_context", "")
            try:
                with json_file.open("r", encoding="utf-8") as f:
                    contexts[dataset_name] = json.load(f)
            except (json.JSONDecodeError, OSError) as err:
                self._logger.warning(f"Failed to read context file {json_file.name}: {err}")

        return contexts

    def get_context(self, dataset_name: str) -> Dict[str, Any]:
        """Fetches metadata for a specific dataset or empty dict if not found."""
        all_contexts = self.load_contexts()
        return all_contexts.get(dataset_name, {})

    def health_check(self) -> Dict[str, Any]:
        """BaseService health check."""
        return {
            "service": self.service_name,
            "status": "HEALTHY",
            "context_files_loaded": len(list(self._context_directory.glob("*.json"))),
        }