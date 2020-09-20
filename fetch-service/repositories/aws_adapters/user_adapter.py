import boto3
from botocore.exceptions import ClientError
from typing import Optional
from models import User


class UserAdapter:
    def __init__(self, table_name: str) -> None:
        self.dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:4566")
        self.table = self.dynamodb.Table(table_name)

    def get(self, user_id: str) -> Optional[User]:
        try:
            item = self.table.get_item(Key={"user_id": user_id})

            return User.from_dynamo(item["Item"])
        except ClientError:
            return None

    def put(self, user: User) -> bool:
        try:
            self.table.put_item(Item=user.to_dynamo())
            return True
        except ClientError:
            return False
