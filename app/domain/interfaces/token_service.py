from abc import ABC, abstractmethod
from app.domain.entities.user import User


class ITokenService(ABC):
    
    @abstractmethod
    def generate_token(self, user: User) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def generate_refresh_token(self, user: User) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def verify_token(self, token: str) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def decode_token(self, token: str) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        raise NotImplementedError