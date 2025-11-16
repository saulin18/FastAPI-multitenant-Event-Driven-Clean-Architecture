from abc import ABC, abstractmethod
from typing import Any, Dict


class IMessageQueueService(ABC):
    
    @abstractmethod
    async def publish(self, routing_key: str, message: Dict[str, Any]) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def disconnect(self) -> None:
     raise NotImplementedError

