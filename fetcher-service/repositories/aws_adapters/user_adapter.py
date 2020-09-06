import boto3
import boto3.dynamodb.types as types


class UserAdapter:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:4566")

    def create_table(self):
        return self.dynamodb.create_table(
            TableName="Users",
            KeySchema=[
                {
                    "AttributeName": "user_id",
                    "KeyType": "HASH",
                },
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "user_id",
                    "AttributeType": types.STRING,
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )

    def get(self, key):
        pass

    def put(self, user):
        pass
