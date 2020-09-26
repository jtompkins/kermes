from kermes_infra.queues import SignalHandler, SQSConsumer, SQSProducer
from kermes_infra.repositories import ArticleRepository, FileRepository, UserRepository
from kermes_infra.repositories.aws_adapters import ArticleAdapter, FileAdapter, UserAdapter

from .fetcher import Fetcher

if __name__ == "__main__":
    ENDPOINT_URL = "http://localhost:4566"

    service = Fetcher(
        UserRepository(UserAdapter(ENDPOINT_URL, "users")),
        ArticleRepository(ArticleAdapter(ENDPOINT_URL, "articles")),
        FileRepository(FileAdapter(ENDPOINT_URL, "kermes-articles")),
        SQSProducer(ENDPOINT_URL, "kermes-fetch-completed.fifo", "1"),
    )

    sqs_consumer = SQSConsumer(ENDPOINT_URL, "kermes-fetch-article.fifo", 1, 1, SignalHandler(), service)
    sqs_consumer.consume_from_queue()
