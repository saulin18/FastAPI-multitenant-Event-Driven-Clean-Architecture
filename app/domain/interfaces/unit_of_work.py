from abc import ABC, abstractmethod
from ast import List
from typing import Any 

class IUnitOfWork(ABC):
    
    @abstractmethod
    async def commit(self) -> None:
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        pass
    
    repositories: List[Any]