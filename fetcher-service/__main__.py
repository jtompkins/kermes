from repositories.user_repository import UserRepository
from repositories.aws_adapters.user_adapter import UserAdapter

if __name__ == "__main__":
    repo = UserRepository(UserAdapter())
    repo.create_table()
    print("hello there")
