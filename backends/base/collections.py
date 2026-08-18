from abc import ABC, abstractmethod


class CollectionsBackend(ABC):

    @abstractmethod
    async def exists(self, collection_id: str):
        pass

    @abstractmethod
    async def fetch_all_collections(self):
        pass

    @abstractmethod
    async def create(self, data: dict):
        pass

    # get by id collection -----------
    @abstractmethod
    async def get(self, collection_id: str):
        pass

    @abstractmethod
    async def replace(self, collection_id: str, data: dict):
        pass

    @abstractmethod
    async def delete(self, collection_id: str):
        pass