from abc import ABC, abstractmethod
from typing import Any, List, Optional, Type, Generic, TypeVar
from pydantic import BaseModel, Field
from enum import Enum

T = TypeVar("T")


class PaginationDirection(str, Enum):
    FORWARD = "forward"
    BACKWARD = "backward"


class ICursorPaginationHelper(ABC):
    """Interface for cursor-based pagination operations."""

    @abstractmethod
    def encode_cursor(self, value: Any) -> str:
        """Encode a value into a cursor string."""
        pass

    @abstractmethod
    def decode_cursor(self, cursor: str) -> Any:
        """Decode a cursor string back to its original value."""
        pass

    @abstractmethod
    def build_cursor_query(
        self,
        query: Any,
        model_class: Type[Any],
        key_selector: str,
        cursor: Optional[str] = None,
        page_size: int = 10,
        direction: PaginationDirection = PaginationDirection.FORWARD,
    ) -> Any:
        """Build a query with cursor-based pagination."""
        pass

    @abstractmethod
    def apply_cursor_pagination_to_query_result(
        self,
        items: List[Any],
        key_selector: str,
        cursor: Optional[str] = None,
        page_size: int = 10,
        direction: PaginationDirection = PaginationDirection.FORWARD,
    ) -> Any:
        """Apply cursor pagination logic to query results."""
        pass


class CursorPagedResult(BaseModel, Generic[T]):
    items: List[T] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None
    has_next_page: bool = False
    has_previous_page: bool = False
    page_size: int = 10

    @staticmethod
    def from_entity(
        entity: T,
        key_selector: str = "id",
        cursor_helper: ICursorPaginationHelper = None,
    ) -> "CursorPagedResult[T]":
        cursor_value = getattr(entity, key_selector)
        if cursor_helper is None:
            raise ValueError("Cursor helper is required")
        return CursorPagedResult(
            items=[entity],
            next_cursor=cursor_helper.encode_cursor(cursor_value),
            previous_cursor=cursor_helper.encode_cursor(cursor_value),
            has_next_page=False,
            has_previous_page=False,
            page_size=1,
        )


class PagedResult(BaseModel, Generic[T]):
    items: List[T] = Field(default_factory=list)
    total_count: int = 0
    page_number: int = 1
    page_size: int = 10

    @property
    def total_pages(self) -> int:
        return (self.total_count + self.page_size - 1) // self.page_size

    @property
    def has_next_page(self) -> bool:
        return self.page_number < self.total_pages

    @property
    def has_previous_page(self) -> bool:
        return self.page_number > 1
