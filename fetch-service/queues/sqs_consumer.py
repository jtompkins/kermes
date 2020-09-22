import boto3

from .signal_handler import SignalHandler
from .supports_consumption import SupportsConsumption


class SQSConsumer:
    def __init__(
        self,
        queue_name: str,
        max_retrieved: int,
        wait_time_seconds: int,
        signal_handler: SignalHandler,
        consumer: SupportsConsumption,
    ) -> None:
        self.sqs = boto3.client("sqs", endpoint_url="http://localhost:4566")
        self.queue_url: str = self.sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
        self.max_retrieved = max_retrieved
        self.wait_time_seconds = wait_time_seconds
        self.signal_handler = signal_handler
        self.consumer = consumer

    def consume_from_queue(self):
        while not self.signal_handler.received_signal:
            print("waiting for up to 20 seconds to receive messages")

            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=self.max_retrieved,
                WaitTimeSeconds=self.wait_time_seconds,
            )

            if "Messages" not in response:
                print("received no messages from queue")
                continue

            messages = response["Messages"]

            print(f"received {len(messages)} messages from sqs queue")

            for message_data in messages:
                try:
                    print(f"received message from queue: {repr(message_data)}")

                    if self.consumer.process_message(message_data["Body"]):
                        print("deleting message")

                        self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message_data["ReceiptHandle"])
                except Exception as e:
                    print(f"exception while processing message: {repr(e)}")
                    continue
