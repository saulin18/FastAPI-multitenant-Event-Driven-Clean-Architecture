from typing import Generic, Optional, TypeVar

T = TypeVar('T')

class Result(Generic[T]):
    def __init__(self, value: T, error: Optional[Exception] = None):
        self.value = value
        self.error = error
        
    def is_success(self) -> bool:
        return self.error is None
    
    def is_failure(self) -> bool:
        return self.error is not None
    
    def get_value(self) -> T:
        return self.value
    
    def get_error(self) -> Exception:
        return self.error