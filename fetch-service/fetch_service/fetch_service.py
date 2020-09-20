import boto3
from signal import signal, SIGINT, SIGTERM
from repositories import UserRepository, ArticleRepository, FileRepository


class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"handling signal {signal}, exiting gracefully")
        self.received_signal = True


class FetchService:
    def __init__(
        self,
        signal_handler: SignalHandler,
        user_repository: UserRepository,
        article_repository: ArticleRepository,
        file_repository: FileRepository,
    ) -> None:
        self.sqs = boto3.client("sqs", endpoint_url="http://localhost:4566")
        self.queue_url: str = self.sqs.get_queue_url(QueueName="kermes-fetch-article.fifo")["QueueUrl"]
        self.signal_handler = signal_handler
        self.user_repository = user_repository
        self.article_repository = article_repository
        self.file_repository = file_repository

    def consume_from_queue(self):
        while not self.signal_handler.received_signal:
            print("waiting for up to 20 seconds to receive messages")

            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=1,
            )

            if "Messages" not in response:
                print("received no messages from queue")
                continue

            messages = response["Messages"]

            print(f"received {len(messages)} messages from sqs queue")

            for message in messages:
                try:
                    print(f"received message from queue: {repr(message)}")

                    self.process_message(message["Body"])
                except Exception as e:
                    print(f"exception while processing message: {repr(e)}")
                    continue

                print("deleting message")

                self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message["ReceiptHandle"])

    def process_message(self, message):
        print(f"processing message: {repr(message)}")
