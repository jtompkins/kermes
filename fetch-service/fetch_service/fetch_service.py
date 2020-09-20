from signal import SIGINT, SIGTERM, signal
from io import BytesIO
from urllib.parse import urlparse

import boto3
import requests
from readability import Document
from lxml import etree

from messages import AddArticleMessage
from models import Article, RelatedContent
from repositories import ArticleRepository, FileRepository, UserRepository


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
        queue_name: str,
        signal_handler: SignalHandler,
        user_repository: UserRepository,
        article_repository: ArticleRepository,
        file_repository: FileRepository,
    ) -> None:
        self.sqs = boto3.client("sqs", endpoint_url="http://localhost:4566")
        self.queue_url: str = self.sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
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

    @classmethod
    def get_filename_from_url(cls, url: str) -> str:
        parsed_url = urlparse(url)
        return parsed_url.path.rpartition("/")[-1]

    def process_message(self, message):
        print(f"processing message: {repr(message)}")

        # parse the JSON SQS message
        add_article_msg = AddArticleMessage.from_json(message)

        # fetch the content from the URL in the message
        resp = requests.get(add_article_msg.url)
        readable_content = Document(resp.text)

        parser = etree.HTMLParser()
        content_dom = etree.fromstring(readable_content.summary(), parser)

        # create an Article model
        article = Article(add_article_msg.user_id)
        article.url = resp.url

        # extract the title from the content
        article.title = readable_content.title()

        # extract the images from the content
        for image in content_dom.iter("img"):
            # fetch the image by the URL
            img_resp = requests.get(image.get("src"))
            img_key = f"{article.user_id}/{article.article_id}/{FetchService.get_filename_from_url(img_resp.url)}"

            # save the images to S3
            self.file_repository.put(img_key, BytesIO(resp.content))

            # create RelatedContent models for each image and add to the Article
            article.related_content.append(RelatedContent(resp.headers["Content-Type"], img_key))

            # re-write the content HTML to point to the new image URL
            image.set("src", img_key)

        # write the content to S3
        content_key = f"{article.user_id}/{article.article_id}/content.html"
        self.file_repository.put(
            content_key, BytesIO(etree.tostring(content_dom.getroottree(), pretty_print=True, method="html"))
        )

        # update the Article with the content key
        article.content_key = content_key

        # write the Article to Dynamo
        self.article_repository.put(article)

        # send a completed message to SQS
