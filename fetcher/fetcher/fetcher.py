from io import BytesIO
from urllib.parse import urlparse

import requests
from lxml import etree
from readability import Document

from kermes_infra.messages import AddArticleMessage, ArticleFetchCompleteMessage
from kermes_infra.models import Article, RelatedContent
from kermes_infra.queues import SQSProducer
from kermes_infra.repositories import ArticleRepository, FileRepository, UserRepository


class Fetcher:
    def __init__(
        self,
        user_repository: UserRepository,
        article_repository: ArticleRepository,
        file_repository: FileRepository,
        finished_queue_producer: SQSProducer,
    ) -> None:
        self.user_repository = user_repository
        self.article_repository = article_repository
        self.file_repository = file_repository
        self.finished_queue_producer = finished_queue_producer

    @classmethod
    def get_filename_from_url(cls, url: str) -> str:
        parsed_url = urlparse(url)
        return parsed_url.path.rpartition("/")[-1]

    def process_message(self, message_json: str) -> bool:
        # parse the JSON SQS message
        add_article_msg = AddArticleMessage.from_json(message_json)

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
        self.finished_queue_producer.send_message(
            ArticleFetchCompleteMessage(article.user_id, article.article_id).to_json()
        )

        return True
