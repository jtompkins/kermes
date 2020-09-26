from datetime import datetime, timezone
from typing import Optional
import json


class ArticleFetchCompleteMessage:
    user_id: str
    article_id: str
    queue_date: datetime

    def __init__(self, user_id: str, article_id: str, queue_date: Optional[datetime] = None) -> None:
        self.user_id = user_id
        self.article_id = article_id
        self.queue_date = queue_date if queue_date is not None else datetime.now(tz=timezone.utc)

    def to_json(self) -> str:
        return json.dumps(
            {
                "user_id": self.user_id,
                "article_id": self.article_id,
                "queue_date": self.queue_date.timestamp(),
            }
        )

    @classmethod
    def from_json(cls, json_data: str) -> "ArticleFetchCompleteMessage":
        data = json.loads(json_data)

        return ArticleFetchCompleteMessage(
            data["user_id"], data["article_id"], datetime.fromtimestamp(data["queue_date"], tz=timezone.utc)
        )
