from src.localstorage.domain.interfaces import IStorageRepository
from src.localstorage.infrastructure.repository import LocalStorageRepository


def get_local_storage_repository() -> IStorageRepository:
    return LocalStorageRepository()
