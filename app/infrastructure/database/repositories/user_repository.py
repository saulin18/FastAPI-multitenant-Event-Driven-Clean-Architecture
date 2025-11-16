
from typing import List, Optional
from uuid import UUID
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.user import User
from app.domain.interfaces.user_repository import UserRepository
from app.infrastructure.database.models import User as UserModel

class UserRepositoryImpl(UserRepository):
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        
        db_user = UserModel(
            email=user.email,
            username=user.username,
            password=user.password,
            tenant_id=user.tenant_id,
            full_name=user.full_name,
            role=user.role,
            permissions=json.dumps(user.permissions) if user.permissions else "[]",
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        
        return User(
            user_id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            tenant_id=db_user.tenant_id,
            password=db_user.password,
            full_name=db_user.full_name,
            role=db_user.role,
            permissions=json.loads(db_user.permissions) if db_user.permissions else [],
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
     
        result = await self.session.get(UserModel, user_id)
  
        
        if not result:
            return None
        
        return User(
            user_id=result.id,
            email=result.email,
            username=result.username,
            tenant_id=result.tenant_id,
            password=result.password,
            full_name=result.full_name,
            role=result.role,
            permissions=json.loads(result.permissions) if result.permissions else [],
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at
        )
    
    async def get_by_email(self, email: str) -> Optional[User]:
      
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        return User(
            user_id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            tenant_id=db_user.tenant_id,
            password=db_user.password,
            full_name=db_user.full_name,
            role=db_user.role,
            permissions=json.loads(db_user.permissions) if db_user.permissions else [],
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def get_by_username(self, username: str) -> Optional[User]:
        
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        return User(
            user_id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            tenant_id=db_user.tenant_id,
            password=db_user.password,
            full_name=db_user.full_name,
            role=db_user.role,
            permissions=json.loads(db_user.permissions) if db_user.permissions else [],
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def update(self, user: User) -> Optional[User]:
       
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        db_user.email = user.email
        db_user.username = user.username
        db_user.full_name = user.full_name
        if user.password:
            db_user.password = user.password
        if user.tenant_id:
            db_user.tenant_id = user.tenant_id
        if user.role:
            db_user.role = user.role
        if user.permissions:
            db_user.permissions = json.dumps(user.permissions)
        db_user.updated_at = user.updated_at
        await self.session.commit()
        await self.session.refresh(db_user)
        
        return User(
            user_id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            tenant_id=db_user.tenant_id,
            password=db_user.password,
            full_name=db_user.full_name,
            role=db_user.role,
            permissions=json.loads(db_user.permissions) if db_user.permissions else [],
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def delete(self, user_id: UUID) -> bool:
       
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return False
        
        await self.session.delete(db_user)
        await self.session.commit()
        return True
    
    
    # TO DO: Implement cursor pagination
    async def list_all(self, skip: int = 0, limit: int = 15) -> List[User]:
       
        result = await self.session.execute(
            select(UserModel).offset(skip).limit(limit)
        )
        db_users = result.scalars().all()
        
        return [
            User(
                user_id=db_user.id,
                email=db_user.email,
                username=db_user.username,
                tenant_id=db_user.tenant_id,
                password=db_user.password,
                full_name=db_user.full_name,
                role=db_user.role,
                permissions=json.loads(db_user.permissions) if db_user.permissions else [],
                is_active=db_user.is_active,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
            for db_user in db_users
        ]

