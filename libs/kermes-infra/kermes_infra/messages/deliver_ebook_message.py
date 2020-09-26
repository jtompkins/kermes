import json
from typing import Optional
from datetime import datetime, timezone


class DeliverEBookMessage:
    user_id: str
    ebook_id: str
    queue_date: datetime

    def __init__(self, user_id: str, ebook_id: str, queue_date: Optional[datetime] = None) -> None:
        self.user_id = user_id
        self.ebook_id = ebook_id
        self.queue_date = queue_date if queue_date is not None else datetime.now(tz=timezone.utc)

    def to_json(self) -> str:
        return json.dumps(
            {"user_id": self.user_id, "ebook_id": self.ebook_id, "queue_date": self.queue_date.timestamp()}
        )

    @classmethod
    def from_json(cls, json_data: str) -> "DeliverEBookMessage":
        data = json.loads(json_data)

        return DeliverEBookMessage(
            data["user_id"], data["ebook_id"], datetime.fromtimestamp(data["queue_date"], tz=timezone.utc)
        )
