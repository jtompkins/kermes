from typing import Dict, Optional
import logging

import boto3
from botocore.exceptions import ClientError


class SQSProducer:
    def __init__(self, endpoint_url: str, queue_name: str, message_group_id: str, logger: logging.Logger) -> None:
        self.sqs = boto3.client("sqs", endpoint_url=endpoint_url)
        self.queue_url: str = self.sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
        self.message_group_id = message_group_id
        self.logger = logger

    def send_message(self, message: str) -> Optional[str]:
        try:
            self.logger.debug(f"attempting to produce message to SQS: {message}")

            response: Dict = self.sqs.send_message(
                QueueUrl=self.queue_url, MessageBody=message, MessageGroupId=self.message_group_id
            )

            if "MessageId" in response:
                return response["MessageId"]
            else:
                return None
        except ClientError as err:
            self.logger.error("error producing message to SQS", exc_info=True)
            return None
