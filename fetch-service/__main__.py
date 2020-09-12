from repositories import UserRepository
from repositories.aws_adapters import UserAdapter
from models import User

from uuid import uuid4

if __name__ == "__main__":
    repo = UserRepository(UserAdapter())
    user = User(str(uuid4()))

    repo.put(user)

    item = repo.get(user.user_id)

    print(item)
