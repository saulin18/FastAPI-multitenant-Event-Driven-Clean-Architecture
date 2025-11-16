from datetime import datetime, timezone
from uuid import UUID, uuid4


class DomainEvent:
    def __init__(self, event_id: UUID = None, occurred_at: datetime = None, event_type: str = ""):
        self.event_id = event_id or uuid4()
        self.occurred_at = occurred_at or datetime.now(timezone.utc)
        self.event_type = event_type