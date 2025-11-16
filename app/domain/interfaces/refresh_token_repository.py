from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from datetime import datetime


class RefreshTokenRepository(ABC):
    
    @abstractmethod
    async def create(self, user_id: UUID, token: str, expires_at: datetime) -> None:
        pass
    
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[dict]:
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        pass
    
    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def is_token_valid(self, token: str) -> bool:
        pass

