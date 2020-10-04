from typing import Optional, Dict, List
from uuid import uuid4
from datetime import datetime, timezone


class EBook:
    user_id: str
    ebook_id: str
    content_key: Optional[str]
    kindle_content_key: Optional[str]
    article_ids: List[str]
    created_date: datetime
    sent: bool
    sent_date: Optional[datetime]

    @classmethod
    def from_dynamo(cls, item: Dict[str, str]) -> "EBook":
        ebook = EBook(item["user_id"])
        ebook.ebook_id = item["ebook_id"]
        ebook.article_ids = item["article_ids"]
        ebook.created_date = datetime.fromtimestamp(float(item["created_date"]), timezone.utc)

        if "content_key" in item:
            ebook.content_key = item["content_key"]

        if "kindle_content_key" in item:
            ebook.kindle_content_key = item["kindle_content_key"]

        if "sent" in item:
            ebook.sent = bool(item["sent"])

        if "sent_date" in item:
            ebook.sent_date = datetime.fromtimestamp(float(item["sent_date"]), timezone.utc)

        return ebook

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.ebook_id = str(uuid4())
        self.content_key = None
        self.kindle_content_key = None
        self.article_ids = []
        self.created_date = datetime.now(tz=timezone.utc)
        self.sent = False
        self.sent_date = None

    def to_dynamo(self) -> Dict[str, str]:
        dynamo_dict = {
            "user_id": self.user_id,
            "ebook_id": self.ebook_id,
            "article_ids": self.article_ids,
            "created_date": str(self.created_date.timestamp()),
            "sent": self.sent,
        }

        if self.content_key is not None:
            dynamo_dict["content_key"] = self.content_key

        if self.kindle_content_key is not None:
            dynamo_dict["kindle_content_key"] = self.kindle_content_key

        if self.sent_date is not None:
            dynamo_dict["sent_date"] = str(self.sent_date.timestamp())

        return dynamo_dict
