import json
from typing import Optional
from datetime import datetime, timezone


class AddArticleMessage:
    user_id: str
    url: str
    queue_date: datetime

    def __init__(self, user_id: str, url: str, queue_date: Optional[datetime] = None) -> None:
        self.user_id = user_id
        self.url = url
        self.queue_date = queue_date if queue_date is not None else datetime.now(tz=timezone.utc)

    def to_json(self) -> str:
        return json.dumps({"user_id": self.user_id, "url": self.url, "queue_date": self.queue_date.timestamp()})

    @classmethod
    def from_json(cls, json_data: str) -> "AddArticleMessage":
        data = json.loads(json_data)

        return AddArticleMessage(
            data["user_id"], data["url"], datetime.fromtimestamp(data["queue_date"], tz=timezone.utc)
        )
