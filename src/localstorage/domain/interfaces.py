import abc
import io


class IStorageRepository(abc.ABC):
    @abc.abstractmethod
    def put_file(self, filename: str, file_body: io.BytesIO) -> None: ...

    @abc.abstractmethod
    def read_file(self, filename: str) -> io.BytesIO: ...

    @abc.abstractmethod
    def delete_file(self, filename: str) -> None: ...
