
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.user import User


class UserRepository(ABC):
    
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> Optional[User]:
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def list_all(self, cursor: str = None, limit: int = 100) -> List[Optional[User]]:
        pass

