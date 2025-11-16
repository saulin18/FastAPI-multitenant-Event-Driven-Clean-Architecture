from typing import Optional, List


class UserApplicationError(Exception):
    reason: str
    def __init__(self, reason: str):
        self.reason = reason

class UserAlreadyExistsError(UserApplicationError):
    def __init__(self, reason: str):
        super().__init__(reason)


class UserNotFoundError(UserApplicationError):
    def __init__(self, reason: str):
        super().__init__(reason)


class InvalidUserDataError(UserApplicationError):
    fields_with_errors = Optional[List[str]]
    def __init__(self, reason: str):
        super().__init__(reason)

