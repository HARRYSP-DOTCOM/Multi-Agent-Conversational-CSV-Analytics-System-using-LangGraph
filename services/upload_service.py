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

        # ==========================================
        # Remove previously uploaded CSVs
        # ==========================================

        for file_name in os.listdir(
            self.upload_directory
        ):

            if file_name.lower().endswith(".csv"):

                old_file_path = os.path.join(
                    self.upload_directory,
                    file_name
                )

                try:

                    os.remove(old_file_path)

                    print(
                        f"Deleted old upload: "
                        f"{old_file_path}"
                    )

                except Exception as e:

                    print(
                        f"Could not delete "
                        f"{old_file_path}: {e}"
                    )

        # ==========================================
        # Save newly uploaded files
        # ==========================================

        saved_paths = []

        for uploaded_file in uploaded_files:

            save_path = os.path.join(
                self.upload_directory,
                uploaded_file.name
            )

            with open(
                save_path,
                "wb"
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )

            saved_paths.append(
                save_path
            )

            print(
                f"Saved upload: "
                f"{save_path}"
            )

        return saved_paths