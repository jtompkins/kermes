from typing import Optional
import logging

import boto3
from botocore.exceptions import ClientError

from kermes_infra.models import EBook


class EBookAdapter:
    def __init__(self, endpoint_url: str, table_name: str, logger: logging.Logger) -> None:
        self.dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
        self.table = self.dynamodb.Table(table_name)
        self.logger = logger

    def get(self, user_id: str, ebook_id: str) -> Optional[EBook]:
        try:
            item = self.table.get_item(Key={"user_id": user_id, "ebook_id": ebook_id})

            return EBook.from_dynamo(item["Item"])
        except ClientError:
            self.logger.exception(f"error while getting record from Dynamo: user_id {user_id}, ebook_id {ebook_id}")
            return None

    def get_all(self, user_id: str):
        pass

    def put(self, ebook: EBook) -> bool:
        try:
            self.table.put_item(Item=ebook.to_dynamo())
            return True
        except ClientError:
            self.logger.exception(
                f"error while writing record to Dynamo: user_id {ebook.user_id}, ebook_id {ebook.ebook_id}",
            )
            return False
