from typing import Protocol


class SupportsConsumption(Protocol):
    def process_message(self, message: str) -> bool:
        ...
