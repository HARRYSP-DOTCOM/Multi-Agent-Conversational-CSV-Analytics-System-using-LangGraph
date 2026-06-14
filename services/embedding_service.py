import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """
    Handles embedding generation
    and vector search.
    """

    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        vector_directory="vector_store"
    ):

        self.model = SentenceTransformer(
            model_name
        )

        self.vector_directory = vector_directory

        self.index = None

        self.metadata = []

    def generate_embeddings(
        self,
        records
    ):
        """
        Convert values into vectors.
        """
        texts = [
            record["value"]
            for record in records
        ]
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        )
        return embeddings
    

    def build_index(
        self,
        embeddings,
        records
    ):
        """
        Build FAISS vector index.
        """
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(
            dimension
        )
        embeddings = embeddings.astype(
            "float32"
        )
        self.index.add(embeddings)
        self.metadata = records

    def save_index(self):
        """
        Persist index and metadata.
        """
        os.makedirs(
        self.vector_directory,
        exist_ok=True
    )

        faiss.write_index(
        self.index,
        os.path.join(
            self.vector_directory,
            "faiss.index"
        )
    )

        with open(
        os.path.join(
            self.vector_directory,
            "metadata.json" 
        ),
        "w"
        ) as file:

         json.dump(
            self.metadata,
            file,
            indent=4
        )

    def load_index(self):
        """
        Load persisted index.
        """

        self.index = faiss.read_index(
            os.path.join(
                self.vector_directory,
                "faiss.index"
            )
        )

        with open(
            os.path.join(
                self.vector_directory,
                "metadata.json"
            )
        ) as file:

            self.metadata = json.load(file)

    def search(
        self,
        query,
        top_k=5
    ):
        """
        Search nearest values.
        """

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )

        query_embedding = query_embedding.astype(
            "float32"
        )

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            result = (
                self.metadata[index]
                .copy()
            )

            result["distance"] = float(
                distance
            )

            results.append(result)

        return results