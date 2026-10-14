"""
Rebuild Service orchestrating dataset indexing, profiling, and semantic vector store generation.

Demonstrates:
- Subclassing `BaseService`
- Custom Context Manager `BenchmarkTimer`
- Standard library `shutil` and `pathlib.Path`
- Service orchestration pattern
"""

import shutil
from pathlib import Path
from typing import Dict, Any, Union

from core.base_service import BaseService
from core.context_managers import BenchmarkTimer
from services.dataset_loader import DatasetLoader
from services.context_generator import ContextGenerator
from services.embedding_preparation import EmbeddingPreparation
from services.embedding_service import EmbeddingService


class RebuildService(BaseService):
    """
    Coordinates end-to-end dataset profile rebuilding and vector database re-indexing.
    """

    def __init__(
        self,
        contexts_dir: Union[str, Path] = "contexts",
        vector_store_dir: Union[str, Path] = "vector_store",
    ) -> None:
        super().__init__(service_name="rebuild_service")
        self._contexts_dir = Path(contexts_dir)
        self._vector_store_dir = Path(vector_store_dir)
        self._initialized = True

    def clean_cache_directories(self) -> None:
        """Purges old metadata and vector store files safely."""
        for target_dir in [self._contexts_dir, self._vector_store_dir]:
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)
            target_dir.mkdir(parents=True, exist_ok=True)

    def rebuild(self) -> Dict[str, Any]:
        """
        Executes end-to-end pipeline:
        1. Directory cleanup
        2. Concurrent dataset loading
        3. Parallel context profiling
        4. Entity extraction
        5. Embedding generation and FAISS indexing
        """
        with BenchmarkTimer(label="Full_System_Rebuild") as timer:
            self._logger.info("Starting system rebuild...")
            self.clean_cache_directories()

            loader = DatasetLoader()
            datasets = loader.load_datasets()

            generator = ContextGenerator(output_directory=self._contexts_dir)
            for dataset_name, df in datasets.items():
                context = generator.generate_context(dataset_name, df)
                generator.save_context(context)

            preparer = EmbeddingPreparation()
            records = []
            for dataset_name, df in datasets.items():
                context = generator.generate_context(dataset_name, df)
                embeddable_cols = preparer.get_embeddable_columns(df, context)
                dataset_records = preparer.extract_values(df, dataset_name, embeddable_cols)
                records.extend(dataset_records)

            if records:
                embedding_service = EmbeddingService()
                embeddings = embedding_service.generate_embeddings(records)
                embedding_service.build_index(embeddings, records)
                embedding_service.save_index()
                self._logger.info(f"Indexed {len(records)} records in vector store.")
            else:
                self._logger.info("No records available to embed.")

        self._logger.info(f"Rebuild completed successfully in {timer.elapsed_seconds:.2f}s")
        return {
            "status": "SUCCESS",
            "duration_sec": timer.elapsed_seconds,
            "datasets_indexed": list(datasets.keys()),
            "records_count": len(records),
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "service": self.service_name,
            "status": "HEALTHY",
            "contexts_dir": str(self._contexts_dir),
            "vector_store_dir": str(self._vector_store_dir),
        }