from typing import Optional
import logging

import boto3
from botocore.exceptions import ClientError
from kermes_infra.models import User


class UserAdapter:
    def __init__(self, endpoint_url: str, table_name: str, logger: logging.Logger) -> None:
        self.dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
        self.table = self.dynamodb.Table(table_name)
        self.logger = logger

    def get(self, user_id: str) -> Optional[User]:
        try:
            item = self.table.get_item(Key={"user_id": user_id})

            return User.from_dynamo(item["Item"])
        except ClientError:
            self.logger.error(f"error while getting record from Dynamo: user_id {user_id}", exc_info=True)
            return None

    def put(self, user: User) -> bool:
        try:
            self.table.put_item(Item=user.to_dynamo())
            return True
        except ClientError:
            self.logger.error(
                f"error while writing record to Dynamo: user_id {user.user_id}",
                exc_info=True,
            )
            return False
