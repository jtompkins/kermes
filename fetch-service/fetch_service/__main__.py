from repositories import UserRepository, ArticleRepository, FileRepository
from repositories.aws_adapters import UserAdapter, ArticleAdapter, FileAdapter
from fetch_service import FetchService, SignalHandler

# from pathlib import Path

if __name__ == "__main__":
    user_repo = UserRepository(UserAdapter("users"))
    article_repo = ArticleRepository(ArticleAdapter("articles"))
    file_repo = FileRepository(FileAdapter("kermes-articles"))

    service = FetchService("kermes-fetch-article.fifo", SignalHandler(), user_repo, article_repo, file_repo)

    service.consume_from_queue()

    # in_path = Path.home() / "rbg.jpg"
    # out_path = Path.home() / "rbg_copy.jpg"

    # with in_path.open(mode="rb") as readfile:
    #     file_repo.put("rbg.jpg", readfile)

    # with out_path.open(mode="wb") as writefile:
    #     s3_stream = file_repo.get("rbg.jpg")

    #     writefile.write(s3_stream.read())

    # print("done")
