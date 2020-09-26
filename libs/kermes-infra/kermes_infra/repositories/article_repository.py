from typing import List, Optional

from kermes_infra.models import Article
from kermes_infra.repositories.aws_adapters import ArticleAdapter


class ArticleRepository:
    def __init__(self, adapter: ArticleAdapter) -> None:
        self.adapter = adapter

    def get(self, user_id: str, article_id: str) -> Optional[Article]:
        return self.adapter.get(user_id, article_id)

    def get_all(self, user_id: str) -> List[Article]:
        return self.adapter.get_all(user_id)

    def put(self, article: Article) -> bool:
        return self.adapter.put(article)
