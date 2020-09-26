from typing import Optional

from kermes_infra.models import User
from kermes_infra.repositories.aws_adapters import UserAdapter


class UserRepository:
    def __init__(self, adapter: UserAdapter) -> None:
        self.adapter = adapter

    def get(self, user_id: str) -> Optional[User]:
        return self.adapter.get(user_id)

    def put(self, user: User) -> bool:
        return self.adapter.put(user)
