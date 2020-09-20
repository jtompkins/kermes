import json


class AddArticleMessage:
    user_id: str
    url: str

    def __init__(self, user_id: str, url: str) -> None:
        self.user_id = user_id
        self.url = url

    def to_json(self) -> str:
        return json.dumps(
            {
                "user_id": self.user_id,
                "url": self.url,
            }
        )

    @classmethod
    def from_json(cls, json_data: str) -> "AddArticleMessage":
        data = json.loads(json_data)

        return AddArticleMessage(data["user_id"], data["url"])
