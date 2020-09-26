import logging

import boto3

from kermes_infra.queues.signal_handler import SignalHandler
from kermes_infra.queues.supports_consumption import SupportsConsumption


class SQSConsumer:
    def __init__(
        self,
        endpoint_url: str,
        queue_name: str,
        max_retrieved: int,
        wait_time_seconds: int,
        signal_handler: SignalHandler,
        consumer: SupportsConsumption,
        logger: logging.Logger,
    ) -> None:
        self.sqs = boto3.client("sqs", endpoint_url=endpoint_url)
        self.queue_url: str = self.sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
        self.max_retrieved = max_retrieved
        self.wait_time_seconds = wait_time_seconds
        self.signal_handler = signal_handler
        self.consumer = consumer
        self.logger = logger

    def consume_from_queue(self) -> None:
        while not self.signal_handler.received_signal:
            self.logger.info(f"waiting for up to {self.wait_time_seconds} to receive messages from SQS")

            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=self.max_retrieved,
                WaitTimeSeconds=self.wait_time_seconds,
            )

            if "Messages" not in response:
                self.logger.info("received no messages from queue")
                continue

            messages = response["Messages"]

            self.logger.debug(f"received {len(messages)} from SQS queue")

            for message_data in messages:
                try:
                    self.logger.debug(f"received message from queue: {repr(message_data)}")

                    if self.consumer.process_message(message_data["Body"]):
                        self.logger.info(f"deleting message {message_data['MessageId']}")

                        self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message_data["ReceiptHandle"])
                except Exception as e:
                    self.logger.error(f"exception while processing message", exc_info=True)

                    # TODO: don't just continue here, move the message to the dead letter queue so other consumers won't hit it
                    continue
