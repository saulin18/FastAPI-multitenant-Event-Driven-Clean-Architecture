from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, not_

from app.domain.interfaces.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.database.models import RefreshToken as RefreshTokenModel


class RefreshTokenRepositoryImpl(RefreshTokenRepository):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user_id: UUID, token: str, expires_at: datetime) -> None:
        db_token = RefreshTokenModel(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_revoked=False
        )
        self.session.add(db_token)
        await self.session.commit()
    
    async def get_by_token(self, token: str) -> Optional[dict]:
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        db_token = result.scalar_one_or_none()
        
        if not db_token:
            return None
        
        return {
            "id": db_token.id,
            "user_id": db_token.user_id,
            "token": db_token.token,
            "expires_at": db_token.expires_at,
            "is_revoked": db_token.is_revoked,
            "created_at": db_token.created_at
        }
    
    async def revoke_token(self, token: str) -> bool:
    
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        db_token = result.scalar_one_or_none()
        
        if not db_token:
            return False
        
        db_token.is_revoked = True
        db_token.revoked_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True
    
    async def revoke_all_user_tokens(self, user_id: UUID) -> bool:
        result = await self.session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.user_id == user_id,
                not_(RefreshTokenModel.is_revoked)
            )
        )
        db_tokens = result.scalars().all()
        
        if not db_tokens:
            return False
        
        for db_token in db_tokens:
            db_token.is_revoked = True
            db_token.revoked_at = datetime.now(timezone.utc)
        
        await self.session.commit()
        return True
    
    async def is_token_valid(self, token: str) -> bool:
    
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        db_token = result.scalar_one_or_none()
        
        if not db_token:
            return False
        
        if db_token.is_revoked:
            return False
        
        if db_token.expires_at < datetime.now(timezone.utc):
            return False
        
        return True

