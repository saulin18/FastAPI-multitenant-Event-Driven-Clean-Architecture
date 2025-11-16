from typing import List, Optional

class TenantApplicationError(Exception):
    reason: str
    def __init__(self, reason: str):
        self.reason = reason

class TenantAlreadyExistsError(TenantApplicationError):
    def __init__(self, reason: str):
        super().__init__(reason)

class TenantNotFoundError(TenantApplicationError):
    def __init__(self, reason: str):
        super().__init__(reason)

class TenantInvalidDataError(TenantApplicationError):
    fields_with_errors: Optional[List[str]] = None
    def __init__(self, reason: str, fields_with_errors: List[str]):
        self.fields_with_errors = fields_with_errors
        super().__init__(reason)

