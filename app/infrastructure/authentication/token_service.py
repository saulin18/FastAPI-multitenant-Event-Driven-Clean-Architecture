from app.domain.interfaces.token_service import ITokenService
from app.shared.config import Settings
from pwdlib import PasswordHash
import jwt
import time
from datetime import datetime, timezone, timedelta
from app.domain.entities.user import User

class TokenService(ITokenService):
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.algorithm = settings.encryption_algorithm
        self._password_hasher = None
    
    @property
    def password_hasher(self):
        """Lazy initialization of password hasher to ensure argon2 is available."""
        if self._password_hasher is None:
            try:
                self._password_hasher = PasswordHash.recommended()
            except Exception as e:
                raise RuntimeError(
                    "The argon2 hash algorithm is not available. "
                    "Are you sure it's installed? Try to run `pip install pwdlib[argon2]`."
                ) from e
        return self._password_hasher
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_hasher.verify(plain_password, hashed_password)
   
    def get_password_hash(self, password: str) -> str:
        return self.password_hasher.hash(password)
       
    def generate_token(self, user: User) -> str:
    
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            "role": user.role,
            "permissions": user.permissions,
            "type": "access",
            "exp": time.time() + (self.settings.access_token_expire_minutes * 60)
        }
        return jwt.encode(payload, self.settings.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user: User) -> str:
    
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "type": "refresh",
            "exp": time.time() + (self.settings.refresh_token_expire_minutes * 60)
        }
        return jwt.encode(payload, self.settings.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> bool:
        
        try:
            jwt.decode(token, self.settings.secret_key, algorithms=[self.algorithm])
            return True
        except jwt.InvalidTokenError:
            return False
    
    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.settings.secret_key, algorithms=[self.algorithm])
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def get_refresh_token_expires_at(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(minutes=self.settings.refresh_token_expire_minutes)
