from typing import Optional
import logging

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

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
                f"get: error while getting article record from Dynamo: user_id {user_id}, article_id {article_id}",
                exc_info=True,
            )
            return None

    def get_all(self, user_id: str):
        try:
            response = self.table.query(KeyConditionExpression=Key("user_id").eq(user_id))

            return [Article.from_dynamo(item) for item in response["Items"]]
        except ClientError:
            self.logger.exception(f"get_all: error while getting article records from Dynamo: user_id {user_id}")

    def put(self, article: Article) -> bool:
        try:
            self.table.put_item(Item=article.to_dynamo())
            return True
        except ClientError:
            self.logger.error(
                f"put: rror while writing article record to Dynamo: user_id {article.user_id}, article_id {article.article_id}",
                exc_info=True,
            )
            return False
