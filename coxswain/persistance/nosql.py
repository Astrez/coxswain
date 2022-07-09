import redis
from .models import *


class NoSQL:
    def __init__(self, host=u'localhost', password='', port=6379) -> None:
        self.r = redis.Redis(host=host, password=password, port=port)
        assert self.r.ping(), "Connection Error"

    def getUser(self, username : str) -> User:
        user = self.r.hgetall(username)
        if user:
            print({i.decode("ascii") : j.decode("ascii") for i, j in user.items()})
            return User(**{i.decode("ascii") : j.decode("ascii") for i, j in user.items()})
        return None

    def setUser(self, user : User) -> None:
        self.r.hmset(user.username, user.save())

    def exists(self, username : str) -> bool:
        return self.r.exists(username) == 1
