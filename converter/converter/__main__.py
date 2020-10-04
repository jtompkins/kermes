import os
import logging

from kermes_infra.queues import SignalHandler, SQSConsumer, SQSProducer
from kermes_infra.repositories import FileRepository, UserRepository, EBookRepository
from kermes_infra.repositories.aws_adapters import FileAdapter, UserAdapter, EBookAdapter

from .converter import Converter

if __name__ == "__main__":
    endpoint_url = os.environ.get("KERMES_AWS_ENDPOINT_URL") or "http://localhost:4566"
    users_table = os.environ.get("KERMES_USERS_TABLE") or "users"
    ebooks_table = os.environ.get("KERMES_EBOOKS_TABLE") or "ebooks"
    content_bucket = os.environ.get("KERMES_CONTENT_BUCKET") or "kermes-content"
    convert_ebook_queue = os.environ.get("KERMES_CONVERT_EBOOK_QUEUE") or "kermes-convert-ebook.fifo"
    deliver_ebook_queue = os.environ.get("KERMES_DELIVER_EBOOK_QUEUE") or "kermes-deliver-ebook.fifo"
    kermes_message_group = os.environ.get("KERMES_MESSAGE_GROUP") or "kermes"

    max_articles_fetched_from_queue = os.environ.get("KERMES_MAX_ARTICLES_FETCHED_FROM_QUEUE") or 1
    wait_time_between_queue_fetches = os.environ.get("KERMES_WAIT_TIME_BETWEEN_QUEUE_FETCHES") or 1

    logging.basicConfig(level=logging.INFO)

    service = Converter(
        UserRepository(UserAdapter(endpoint_url, users_table, logging.getLogger("user_adapter"))),
        EBookRepository(EBookAdapter(endpoint_url, ebooks_table, logging.getLogger("ebook_adapter"))),
        FileRepository(FileAdapter(endpoint_url, content_bucket, logging.getLogger("file_adapter"))),
        SQSProducer(
            endpoint_url, deliver_ebook_queue, kermes_message_group, logging.getLogger("postmaster_sqs_producer")
        ),
        logging.getLogger("converter"),
    )

    sqs_consumer = SQSConsumer(
        endpoint_url,
        convert_ebook_queue,
        int(max_articles_fetched_from_queue),  # if this was retrieved from an env var, it will be a string, not an int
        int(wait_time_between_queue_fetches),  # if this was retrieved from an env var, it will be a string, not an int
        SignalHandler(logging.getLogger("signal_handler")),
        service,
        logging.getLogger("sqs_consumer"),
    )

    sqs_consumer.consume_from_queue()
