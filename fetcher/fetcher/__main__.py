import os
import logging

from kermes_infra.queues import SignalHandler, SQSConsumer, SQSProducer
from kermes_infra.repositories import ArticleRepository, FileRepository, UserRepository
from kermes_infra.repositories.aws_adapters import ArticleAdapter, FileAdapter, UserAdapter

from .fetcher import Fetcher

if __name__ == "__main__":
    endpoint_url = os.environ.get("KERMES_AWS_ENDPOINT_URL") or "http://localhost:4566"
    users_table = os.environ.get("KERMES_USERS_TABLE") or "users"
    articles_table = os.environ.get("KERMES_ARTICLES_TABLE") or "articles"
    articles_bucket = os.environ.get("KERMES_ARTICLES_BUCKET") or "kermes-articles"
    fetch_completed_queue = os.environ.get("KERMES_FETCH_COMPLETED_QUEUE") or "kermes-fetch-completed.fifo"
    fetch_completed_message_group = os.environ.get("KERMES_FETCH_COMPLETED_MESSAGE_GROUP") or "kermes"
    fetch_article_queue = os.environ.get("KERMES_FETCH_ARTICLE_QUEUE") or "kermes-fetch-article.fifo"

    max_articles_fetched_from_queue = os.environ.get("KERMES_MAX_ARTICLES_FETCHED_FROM_QUEUE") or 1
    wait_time_between_queue_fetches = os.environ.get("KERMES_WAIT_TIME_BETWEEN_QUEUE_FETCHES") or 1

    logging.basicConfig(level=logging.DEBUG)

    service = Fetcher(
        UserRepository(UserAdapter(endpoint_url, users_table, logging.getLogger("user_adapter"))),
        ArticleRepository(ArticleAdapter(endpoint_url, articles_table, logging.getLogger("article_adapter"))),
        FileRepository(FileAdapter(endpoint_url, articles_bucket, logging.getLogger("file_adapter"))),
        SQSProducer(
            endpoint_url, fetch_completed_queue, fetch_completed_message_group, logging.getLogger("sqs_producer")
        ),
        logging.getLogger("fetcher"),
    )

    sqs_consumer = SQSConsumer(
        endpoint_url,
        fetch_article_queue,
        int(max_articles_fetched_from_queue),  # if this was retrieved from an env var, it will be a string, not an int
        int(wait_time_between_queue_fetches),  # if this was retrieved from an env var, it will be a string, not an int
        SignalHandler(logging.getLogger("signal_handler")),
        service,
        logging.getLogger("sqs_consumer"),
    )

    sqs_consumer.consume_from_queue()
