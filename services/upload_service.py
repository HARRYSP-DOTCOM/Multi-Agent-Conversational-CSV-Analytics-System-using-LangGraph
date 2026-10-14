"""
Upload Service for managing CSV file ingestion and storage.

Demonstrates:
- Subclassing `BaseService`
- Modern filesystem handling with `pathlib.Path`
- Defensive file handling and error containment
- Resource management using `with` context managers
- Complete compatibility with Streamlit `UploadedFile` objects
"""

from pathlib import Path
from typing import List, Any, Union, Dict
from core.base_service import BaseService


class UploadService(BaseService):
    """
    Manages safe reception, storage, and lifecycle of uploaded CSV files.
    """

    def __init__(self, upload_directory: Union[str, Path] = "uploads") -> None:
        super().__init__(service_name="upload_service")
        self._upload_directory = Path(upload_directory)
        self._upload_directory.mkdir(parents=True, exist_ok=True)
        self._initialized = True

    @property
    def upload_directory(self) -> Path:
        """Returns upload directory path."""
        return self._upload_directory

    def clean_old_uploads(self) -> int:
        """
        Removes previously uploaded CSV files from the directory.
        Demonstrates `pathlib.Path.glob` and error containment with `try...except...else`.

        Returns:
            Count of deleted files.
        """
        deleted_count = 0
        for file_path in self._upload_directory.glob("*.csv"):
            try:
                file_path.unlink()
                deleted_count += 1
                self._logger.info(f"Deleted old upload: {file_path.name}")
            except OSError as err:
                self._logger.warning(f"Could not delete {file_path.name}: {err}")
        return deleted_count

    def save_files(self, uploaded_files: List[Any]) -> List[str]:
        """
        Saves incoming uploaded file streams to disk.
        Cleans previously uploaded CSVs before writing new ones.

        Args:
            uploaded_files: Iterable of file-like objects (e.g. Streamlit UploadedFile)

        Returns:
            List of saved absolute file path strings.
        """
        self.clean_old_uploads()

        saved_paths: List[str] = []
        for uploaded_file in uploaded_files:
            file_name = getattr(uploaded_file, "name", "uploaded_data.csv")
            save_path = self._upload_directory / file_name

            # Stream buffer safely to disk
            with save_path.open("wb") as destination:
                if hasattr(uploaded_file, "getbuffer"):
                    destination.write(uploaded_file.getbuffer())
                elif hasattr(uploaded_file, "read"):
                    destination.write(uploaded_file.read())

            saved_paths.append(str(save_path))
            self._logger.info(f"Saved upload: {save_path}")

        return saved_paths

    def health_check(self) -> Dict[str, Any]:
        """BaseService health check."""
        return {
            "service": self.service_name,
            "status": "HEALTHY",
            "directory": str(self._upload_directory),
            "files_present": len(list(self._upload_directory.glob("*.csv"))),
        }