from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class PaginationDirection(str, Enum):
    FORWARD = "forward"
    BACKWARD = "backward"


class CreateTenantRequest(BaseModel):
    name: str
    domain: str
    

class UpdateTenantRequest(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    is_active: Optional[bool] = None

class TenantResponse(BaseModel):
    id: UUID
    name: str
    domain: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
class PagedTenantResponse(BaseModel):
    items: List[TenantResponse]
    total_count: int
    page_number: int
    page_size: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None
    
class CursorPagedTenantResponse(BaseModel):
    items: List[TenantResponse]
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None
    has_next_page: bool
    has_previous_page: bool
    page_size: int
    
class CursorPagedTenantRequest(BaseModel):
    cursor: Optional[str] = None
    page_size: int = 10
    direction: PaginationDirection = PaginationDirection.FORWARD