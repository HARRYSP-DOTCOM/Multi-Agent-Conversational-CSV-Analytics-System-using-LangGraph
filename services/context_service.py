import json
import os

class ContextService:

    def __init__(
        self,
        context_directory="contexts"
    ):
        self.context_directory = context_directory

    def load_contexts(self):

        contexts = {}

        for file_name in os.listdir(
            self.context_directory
        ):

            if file_name.endswith(".json"):

                path = os.path.join(
                    self.context_directory,
                    file_name
                )

                with open(path) as file:

                    contexts[
                        file_name.replace(
                            "_context.json",
                            ""
                        )
                    ] = json.load(file)

        return contexts