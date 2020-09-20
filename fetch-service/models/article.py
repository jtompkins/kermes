from typing import List, Dict, Optional, Union
from datetime import datetime, timezone
from uuid import uuid4

DynamoArticleDict = Dict[str, Union[str, List[Dict[str, str]]]]


class RelatedContent:
    @classmethod
    def from_dynamo(cls, item: Dict[str, str]) -> "RelatedContent":
        return RelatedContent(item["mime_type"], item["content_key"])

    def __init__(self, mime_type: str, content_key: str) -> None:
        self.mime_type = mime_type
        self.content_key = content_key

    def to_dynamo(self) -> Dict[str, str]:
        return {
            "mime_type": self.mime_type,
            "content_key": self.content_key,
        }


class Article:
    user_id: str
    article_id: str
    url: Optional[str]
    title: Optional[str]
    content_key: Optional[str]
    related_content: List[RelatedContent]
    created_date: datetime

    @classmethod
    def from_dynamo(cls, item: DynamoArticleDict) -> "Article":
        article = Article(item["user_id"])
        article.article_id = item["article_id"]

        if "url" in item:
            article.url = item["url"]

        if "title" in item:
            article.title = item["title"]

        if "content_key" in item:
            article.content_key = item["content_key"]

        article.related_content = [RelatedContent.from_dynamo(r) for r in item["related_content"]]
        article.created_date = datetime.fromtimestamp(float(item["created_date"]), timezone.utc)

        return article

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.article_id = str(uuid4())
        self.title = None
        self.url = None
        self.content_key = None
        self.related_content = []
        self.created_date = datetime.now(tz=timezone.utc)

    def to_dynamo(self) -> DynamoArticleDict:
        dynamo_dict = {
            "user_id": self.user_id,
            "article_id": self.article_id,
            "related_content": [r.to_dynamo() for r in self.related_content],
            "created_date": str(self.created_date.timestamp()),
        }

        if self.url is not None:
            dynamo_dict["url"] = self.url

        if self.title is not None:
            dynamo_dict["title"] = self.title

        if self.content_key is not None:
            dynamo_dict["content_key"] = self.content_key

        return dynamo_dict
