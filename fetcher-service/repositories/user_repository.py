class UserRepository:
    def __init__(self, adapter):
        self.adapter = adapter

    def get(self, key):
        return self.adapter.get(key)

    def put(self, user):
        return self.adapter.put(user)
