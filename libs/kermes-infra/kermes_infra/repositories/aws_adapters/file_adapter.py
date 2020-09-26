from typing import Optional, IO
import logging

import boto3
from botocore.exceptions import ClientError


class FileAdapter:
    def __init__(self, endpoint_url: str, bucket: str, logger: logging.Logger) -> None:
        self.s3 = boto3.client("s3", endpoint_url=endpoint_url)
        self.bucket = bucket
        self.logger = logger

    def get(self, key: str) -> Optional[IO[bytes]]:
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)

            return response["Body"]
        except ClientError:
            self.logger.error(f"error while getting file from S3: key {key}", exc_info=True)
            return None

    def put(self, key: str, content: IO[bytes]) -> bool:
        try:
            self.s3.put_object(Bucket=self.bucket, Key=key, Body=content)

            return True
        except ClientError:
            self.logger.error(f"error while writing file to S3: key {key}", exc_info=True)
            return False
