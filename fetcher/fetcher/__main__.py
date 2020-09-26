from kermes_infra.queues import SignalHandler, SQSConsumer, SQSProducer
from kermes_infra.repositories import ArticleRepository, FileRepository, UserRepository
from kermes_infra.repositories.aws_adapters import ArticleAdapter, FileAdapter, UserAdapter

from .fetcher import Fetcher

if __name__ == "__main__":
    service = Fetcher(
        UserRepository(UserAdapter("users")),
        ArticleRepository(ArticleAdapter("articles")),
        FileRepository(FileAdapter("kermes-articles")),
        SQSProducer("kermes-fetch-completed.fifo", "1"),
    )

    sqs_consumer = SQSConsumer("kermes-fetch-article.fifo", 1, 1, SignalHandler(), service)
    sqs_consumer.consume_from_queue()
