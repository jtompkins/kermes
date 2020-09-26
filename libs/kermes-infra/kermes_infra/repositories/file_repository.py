from typing import IO, Optional

from kermes_infra.repositories.aws_adapters import FileAdapter


class FileRepository:
    def __init__(self, adapter: FileAdapter) -> None:
        self.adapter = adapter

    def get(self, key: str) -> Optional[IO[bytes]]:
        return self.adapter.get(key)

    def put(self, key: str, content: IO[bytes]) -> bool:
        return self.adapter.put(key, content)
