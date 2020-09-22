from repositories import UserRepository, ArticleRepository, FileRepository
from repositories.aws_adapters import UserAdapter, ArticleAdapter, FileAdapter
from queues import SQSProducer, SQSConsumer, SignalHandler
from fetch_service import FetchService

# from pathlib import Path

if __name__ == "__main__":
    service = FetchService(
        UserRepository(UserAdapter("users")),
        ArticleRepository(ArticleAdapter("articles")),
        FileRepository(FileAdapter("kermes-articles")),
        SQSProducer("kermes-fetch-completed.fifo", "1"),
    )

    sqs_consumer = SQSConsumer("kermes-fetch-article.fifo", 1, 1, SignalHandler(), service)
    sqs_consumer.consume_from_queue()

    # in_path = Path.home() / "rbg.jpg"
    # out_path = Path.home() / "rbg_copy.jpg"

    # with in_path.open(mode="rb") as readfile:
    #     file_repo.put("rbg.jpg", readfile)

    # with out_path.open(mode="wb") as writefile:
    #     s3_stream = file_repo.get("rbg.jpg")

    #     writefile.write(s3_stream.read())

    # print("done")
