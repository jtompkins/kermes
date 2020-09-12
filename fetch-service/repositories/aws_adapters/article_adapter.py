from typing import Optional

import boto3
from botocore.exceptions import ClientError

from models import Article


class ArticleAdapter:
    def __init__(self) -> None:
        self.dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:4566")
        self.table = self.dynamodb.Table("articles")

    def get(self, user_id: str, article_id: str) -> Optional[Article]:
        try:
            item = self.table.get_item(
                Key={"user_id": user_id, "article_id": article_id}
            )

            return Article.from_dynamo(item["Item"])
        except ClientError:
            return None

    def get_all(self, user_id: str):
        pass

    def put(self, article: Article) -> bool:
        try:
            self.table.put_item(Item=article.to_dynamo())
            return True
        except ClientError:
            return False
