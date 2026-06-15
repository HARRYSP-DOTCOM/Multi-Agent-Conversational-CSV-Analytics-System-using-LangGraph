from services.dataset_loader import DatasetLoader
from services.context_generator import ContextGenerator
from services.embedding_preparation import EmbeddingPreparation
from services.embedding_service import EmbeddingService


class RebuildService:

    def rebuild(self):

        print("Loading datasets...")

        loader = DatasetLoader()

        datasets = loader.load_datasets()

        print("Generating contexts...")

        generator = ContextGenerator()

        for dataset_name, dataframe in datasets.items():

          context = generator.generate_context(
           dataset_name,
           dataframe
    )

          generator.save_context(
          context
    )

        print("Preparing records...")

        preparer = EmbeddingPreparation()
        records = []
        generator = ContextGenerator()

        for dataset_name, dataframe in datasets.items():

             context = generator.generate_context(
              dataset_name,
              dataframe
    )

             embeddable_columns = (
               preparer.get_embeddable_columns(
                dataframe,
                context
        )
    )

             dataset_records = (
                preparer.extract_values(
                 dataframe,
                 dataset_name,
                 embeddable_columns
        )
    )

             records.extend(
              dataset_records
    )

        print(
        f"{len(records)} records extracted."
)

        print("Generating embeddings...")

        embedding_service = EmbeddingService()

        embeddings = (
            embedding_service.generate_embeddings(
                records
            )
        )

        print("Building FAISS...")

        embedding_service.build_index(
            embeddings,
            records
        )

        embedding_service.save_index()

        print("Rebuild complete.")