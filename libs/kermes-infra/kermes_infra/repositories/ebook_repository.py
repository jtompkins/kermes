from typing import List, Optional

from kermes_infra.models import EBook
from kermes_infra.repositories.aws_adapters import EBookAdapter


class EBookRepository:
    def __init__(self, adapter: EBookAdapter) -> None:
        self.adapter = adapter

    def get(self, user_id: str, ebook_id: str) -> Optional[EBook]:
        return self.adapter.get(user_id, ebook_id)

    def get_all(self, user_id: str) -> List[EBook]:
        return self.adapter.get_all(user_id)

    def put(self, ebook: EBook) -> bool:
        return self.adapter.put(ebook)
