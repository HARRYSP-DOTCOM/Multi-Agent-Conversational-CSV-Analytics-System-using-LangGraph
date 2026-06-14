from services.dataset_loader import DatasetLoader
from services.context_generator import ContextGenerator
from services.embedding_preparation import EmbeddingPreparation
from services.embedding_service import EmbeddingService

class Day1Pipeline:
    def __init__(self):
        self.loader = DatasetLoader()
        self.context_generator = ContextGenerator()
        self.embedding_preparation = (
            EmbeddingPreparation()
        )
        self.embedding_service = (
            EmbeddingService()
        )
    def initialize_semantic_memory(self):
        datasets = (
            self.loader.load_datasets()
        )
        all_records = []
        print("\nLoading datasets...")
        for (
            dataset_name,
            dataframe
        ) in datasets.items():
            print(
                f"\nProcessing {dataset_name}"
            )
            context = (
                self.context_generator
                .generate_context(
                    dataset_name,
                    dataframe
                )
            )
            self.context_generator.save_context(
                context
            )
            embeddable_columns = (
                self.embedding_preparation
                .get_embeddable_columns(
                    dataframe,
                    context
                )
            )
            records = (
                self.embedding_preparation
                .extract_values(
                    dataframe,
                    dataset_name,
                    embeddable_columns
                )
            )
            all_records.extend(records)
            print(
            f"\nTotal Records: "
            f"{len(all_records)}"
        )
        embeddings = (
            self.embedding_service
            .generate_embeddings(
                all_records
            )
        )
        print(
            f"Embeddings Shape: "
            f"{embeddings.shape}"
        )
        
        self.embedding_service.build_index(
            embeddings,
            all_records
        )
        self.embedding_service.save_index()

        print(
            "\nSemantic memory initialized."
        )
        return {
            "datasets": len(datasets),
            "records": len(all_records),
            "embedding_shape": embeddings.shape,
        }