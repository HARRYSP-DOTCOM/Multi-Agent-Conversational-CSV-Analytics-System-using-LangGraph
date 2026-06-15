import os


class UploadService:

    def __init__(self):

        self.upload_directory = "uploads"

        os.makedirs(
            self.upload_directory,
            exist_ok=True
        )

    def save_files(
        self,
        uploaded_files
    ):

        saved_paths = []

        for uploaded_file in uploaded_files:

            path = os.path.join(
                self.upload_directory,
                uploaded_file.name
            )

            with open(
                path,
                "wb"
            ) as file:

                file.write(
                    uploaded_file.getbuffer()
                )

            saved_paths.append(path)

        return saved_paths