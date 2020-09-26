from typing import Optional, Dict
from datetime import datetime, timezone


class User:
    user_id: str
    email: Optional[str]
    delivery_email: Optional[str]
    prefer_kindle: bool
    send_threshhold: Optional[int]
    send_day: Optional[int]
    created_date: datetime

    @classmethod
    def from_dynamo(cls, item: Dict[str, str]) -> "User":
        user = User(item["user_id"])
        user.email = item.get("email", None)
        user.delivery_email = item.get("delivery_email", None)
        user.prefer_kindle = bool(item.get("prefer_kindle", False))

        if "send_threshhold" in item:
            user.send_threshhold = int(item["send_threshhold"])

        if "send_day" in item:
            user.send_day = int(item["send_day"])

        user.created_date = datetime.fromtimestamp(float(item["created_date"]), timezone.utc)

        return user

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.email = None
        self.delivery_email = None
        self.prefer_kindle = False
        self.send_threshhold = None
        self.send_day = None
        self.created_date = datetime.now(tz=timezone.utc)

    def to_dynamo(self) -> Dict[str, str]:
        dynamo_dict = {
            "user_id": self.user_id,
            "prefer_kindle": str(self.prefer_kindle),
            "created_date": str(self.created_date.timestamp()),
        }

        if self.email is not None:
            dynamo_dict["email"] = self.email

        if self.delivery_email is not None:
            dynamo_dict["delivery_email"] = self.delivery_email

        if self.send_threshhold is not None:
            dynamo_dict["send_threshhold"] = self.send_threshhold

        if self.send_day is not None:
            dynamo_dict["send_day"] = self.send_day

        return dynamo_dict
