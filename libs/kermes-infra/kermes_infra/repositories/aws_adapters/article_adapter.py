from typing import Optional
import logging

import boto3
from botocore.exceptions import ClientError

from kermes_infra.models import Article


class ArticleAdapter:
    def __init__(self, endpoint_url: str, table_name: str, logger: logging.Logger) -> None:
        self.dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
        self.table = self.dynamodb.Table(table_name)
        self.logger = logger

    def get(self, user_id: str, article_id: str) -> Optional[Article]:
        try:
            item = self.table.get_item(Key={"user_id": user_id, "article_id": article_id})

            return Article.from_dynamo(item["Item"])
        except ClientError:
            self.logger.error(
                f"error while getting record from Dynamo: user_id {user_id}, article_id {article_id}", exc_info=True
            )
            return None

    def get_all(self, user_id: str):
        pass

    def put(self, article: Article) -> bool:
        try:
            self.table.put_item(Item=article.to_dynamo())
            return True
        except ClientError:
            self.logger.error(
                f"error while writing record to Dynamo: user_id {article.user_id}, article_id {article.article_id}",
                exc_info=True,
            )
            return False
