from src.core.config import settings
from pathlib import Path
import io

from src.tasks.domain.interfaces.task_result_storage import ITaskStorageRepository
from src.localstorage.domain.exceptions import FileNotFoundError


class LocalStorageRepository(ITaskStorageRepository):
    storage_path = Path(settings.LOCAL_STORAGE_PATH)

    def put_file(self, filename: str, file_body: io.BytesIO) -> None:
        with open(self.storage_path / filename, 'wb') as f:
            while True:
                chunk = file_body.read(1024)
                if not chunk:
                    break
                f.write(chunk)

    def read_file(self, filename: str) -> io.BytesIO:
        if not (self.storage_path / filename).exists():
            raise FileNotFoundError(filename)
        with open(self.storage_path / filename, "rb") as f:
            return io.BytesIO(f.read())

    def delete_file(self, filename: str) -> None:
        if not (self.storage_path / filename).exists():
            raise FileNotFoundError(filename)
        (self.storage_path / filename).unlink()
