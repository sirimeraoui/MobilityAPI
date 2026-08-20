from abc import ABC, abstractmethod

class MovingFeaturesBackend(ABC):
    @abstractmethod
    async def begin(self):
        pass
    @abstractmethod
    async def create(
        self,
        collection_id: str,
        data: dict,
    ):
        pass

    @abstractmethod
    async def get_items(
        self,
        collection_id: str,
        limit: int,
        bbox_coords=None,
        dt1=None,
        dt2=None,
        subTrajectory: bool = False,
    ):
        pass

# by feature id operations:
    @abstractmethod
    async def get_feature(
        self,
        collection_id: str,
        mfeature_id: str,
    ):
        pass
    @abstractmethod
    async def delete(
        self,
        collection_id: str,
        mfeature_id: str,
    ):
        pass

    @abstractmethod
    async def collection_exists(
        self,
        collection_id: str,
    ):
        pass

    @abstractmethod
    async def commit(self):
        pass
    @abstractmethod
    async def rollback(self):
        pass