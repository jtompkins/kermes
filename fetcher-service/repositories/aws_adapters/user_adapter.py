import boto3


class UserAdapter:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:4566")

    def get(self, key):
        pass

    def put(self, user):
        pass
