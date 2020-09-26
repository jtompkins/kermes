from typing import Optional

import boto3
from botocore.exceptions import ClientError

from kermes_infra.models import Article


class ArticleAdapter:
    def __init__(self, endpoint_url: str, table_name: str) -> None:
        self.dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
        self.table = self.dynamodb.Table(table_name)

    def get(self, user_id: str, article_id: str) -> Optional[Article]:
        try:
            item = self.table.get_item(Key={"user_id": user_id, "article_id": article_id})

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
