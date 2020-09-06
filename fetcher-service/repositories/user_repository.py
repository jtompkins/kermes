class UserRepository:
    def __init__(self, adapter):
        self.adapter = adapter

    def create_table(self):
        return self.adapter.create_table()

    def get(self, key):
        return self.adapter.get(key)

    def put(self, user):
        return self.adapter.put(user)
