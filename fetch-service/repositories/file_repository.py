from .aws_adapters import FileAdapter
from typing import Optional, IO


class FileRepository:
    def __init__(self, adapter: FileAdapter) -> None:
        self.adapter = adapter

    def get(self, key: str) -> Optional[IO[bytes]]:
        return self.adapter.get(key)

    def put(self, key: str, content: IO[bytes]) -> bool:
        return self.adapter.put(key, content)
