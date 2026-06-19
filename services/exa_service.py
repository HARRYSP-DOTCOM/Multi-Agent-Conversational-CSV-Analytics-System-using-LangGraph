import os
from dotenv import load_dotenv
from exa_py import Exa

load_dotenv()


class ExaService:
    def __init__(self):
        api_key = os.getenv("EXA_API_KEY")

        if not api_key:
            raise ValueError(
                "EXA_API_KEY not found in .env"
            )

        self.exa = Exa(api_key)

    def search(self, query, num_results=5):
        results = self.exa.search_and_contents(
            query,
            num_results=num_results
        )

        return results
