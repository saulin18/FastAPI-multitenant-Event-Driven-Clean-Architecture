from typing import TypeVar, List, Optional, Any
from pydantic import BaseModel, Field
import base64
import json
from app.shared.pagination import PaginationDirection, CursorPagedResult, ICursorPaginationHelper

T = TypeVar('T')

class PaginationRequest(BaseModel):
    
    page_number: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)
    
    def __init__(self, **data):
        super().__init__(**data)
        
        if self.page_number < 1:
            self.page_number = 1
        
        if self.page_size > 50:
            self.page_size = 50
        elif self.page_size < 1:
            self.page_size = 10



class CursorPaginationRequest(BaseModel):
  
    cursor: Optional[str] = None
    page_size: int = Field(default=10, ge=1, le=50)
    direction: PaginationDirection = PaginationDirection.FORWARD
    
    def __init__(self, **data):
        super().__init__(**data)
       
        if self.page_size > 50:
            self.page_size = 50
        elif self.page_size < 1:
            self.page_size = 10


class CursorPaginationHelper(ICursorPaginationHelper):
   
    @staticmethod
    def encode_cursor(value: Any) -> str:
        try:
            json_str = json.dumps(value, default=str)
            bytes_data = json_str.encode('utf-8')
            return base64.b64encode(bytes_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to encode cursor: {e}")
    
    @staticmethod
    def decode_cursor(cursor: str, target_type: type = None) -> Any:
        try:
            bytes_data = base64.b64decode(cursor.encode('utf-8'))
            json_str = bytes_data.decode('utf-8')
            if target_type is not None:
                return json.loads(json_str, object_hook=lambda d: target_type(**d))
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Failed to decode cursor: {e}")
    

    @staticmethod
    def build_cursor_query(
        base_query,
        model_class,
        key_selector: str,
        cursor: Optional[str] = None,
        page_size: int = 10,
        direction: PaginationDirection = PaginationDirection.FORWARD
    ):
        
        if cursor:
            try:
                cursor_value = CursorPaginationHelper.decode_cursor(cursor)
                if direction == PaginationDirection.FORWARD:
                    base_query = base_query.where(getattr(model_class, key_selector) > cursor_value)
                else:
                    base_query = base_query.where(getattr(model_class, key_selector) < cursor_value)
            except ValueError:
                raise ValueError(f"Invalid cursor: {cursor}")
        
        if direction == PaginationDirection.FORWARD:
            base_query = base_query.order_by(getattr(model_class, key_selector))
        else:
            base_query = base_query.order_by(getattr(model_class, key_selector).desc())
        
        base_query = base_query.limit(page_size + 1)
        
        return base_query

    @staticmethod
    def apply_cursor_pagination_to_query_result(
        items: List[T],
        key_selector: str,
        cursor: Optional[str] = None,
        page_size: int = 10,
        direction: PaginationDirection = PaginationDirection.FORWARD
    ) -> CursorPagedResult[T]:
        
        if not items:
            return CursorPagedResult[T](
                items=[],
                next_cursor=None,
                previous_cursor=None,
                has_next_page=False,
                has_previous_page=False,
                page_size=page_size
            )
        
        has_next_page = len(items) > page_size
        
        paginated_items = items[:page_size]
        
        next_cursor = None
        previous_cursor = None
        
        if paginated_items:
            last_item_key = getattr(paginated_items[-1], key_selector)
            first_item_key = getattr(paginated_items[0], key_selector)
            
            next_cursor = CursorPaginationHelper.encode_cursor(last_item_key) if has_next_page else None
            previous_cursor = CursorPaginationHelper.encode_cursor(first_item_key) if cursor else None
        
        return CursorPagedResult[T](
            items=paginated_items,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            has_next_page=has_next_page,
            has_previous_page=bool(cursor),
            page_size=page_size
        )