import pymongo
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional, Dict, Any

class HistoryService:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="analytics_agent", collection_name="history"):
        self.client = pymongo.MongoClient(
            uri, 
            serverSelectionTimeoutMS=1000,
            connectTimeoutMS=1000,
            socketTimeoutMS=1000
        )
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        # Load the model for embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _cosine_similarity(self, vec1, vec2):
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def save_interaction(self, question: str, response: Dict[str, Any]):
        """Save a new question-response pair with its embedding."""
        try:
            embedding = self.model.encode(question).tolist()
            doc = {
                "question": question,
                "response": response,
                "embedding": embedding
            }
            self.collection.insert_one(doc)
        except Exception as e:
            print(f"Warning: Failed to save to MongoDB: {e}")

    def find_similar_interaction(self, question: str, threshold: float = 0.95) -> Optional[Dict[str, Any]]:
        """
        Find a previously answered question that is semantically similar to the new question.
        Returns the response dict if found, otherwise None.
        """
        try:
            # Encode the new question
            query_embedding = self.model.encode(question).tolist()
            
            # Retrieve all history
            best_match_response = None
            highest_score = -1.0

            for doc in self.collection.find({}, {"question": 1, "response": 1, "embedding": 1}):
                if "embedding" in doc:
                    score = self._cosine_similarity(query_embedding, doc["embedding"])
                    if score > highest_score:
                        highest_score = score
                        best_match_response = doc["response"]

            if highest_score >= threshold:
                print(f"Found match in history with score: {highest_score:.2f}")
                return best_match_response
            
            return None
        except Exception as e:
            print(f"Warning: Failed to read from MongoDB: {e}")
            return None
