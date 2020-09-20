# from repositories import UserRepository, ArticleRepository
# from repositories.aws_adapters import UserAdapter, ArticleAdapter
# from fetch_service import FetchService, SignalHandler

from repositories import FileRepository
from repositories.aws_adapters import FileAdapter

from pathlib import Path

if __name__ == "__main__":
    # user_repo = UserRepository(UserAdapter())
    # article_repo = ArticleRepository(ArticleAdapter())

    # service = FetchService(SignalHandler(), user_repo, article_repo)

    # service.consume_from_queue()

    file_repo = FileRepository(FileAdapter("kermes-articles"))

    in_path = Path.home() / "rbg.jpg"
    out_path = Path.home() / "rbg_copy.jpg"

    with in_path.open(mode="rb") as readfile:
        file_repo.put("rbg.jpg", readfile)

    with out_path.open(mode="wb") as writefile:
        s3_stream = file_repo.get("rbg.jpg")

        writefile.write(s3_stream.read())

    print("done")
