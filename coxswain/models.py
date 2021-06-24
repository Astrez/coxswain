import redis
from .kube import Kube
import statistics
import logging

logger = logging.getLogger("app.scale")


class Database():

    def __init__(self) -> None:
        self.__redis = redis.Redis()

        assert self.__redis.ping(), "Connection Error"

        # Setup basic details like replica count on database

    @property
    def redis(self):
        # For custom queries
        return self.__redis

    def compare(self, cred : dict) -> bool:
        if self._exists(cred['username']):
            if self.__redis.get(cred['username']) == cred['password']:
                return True
        return False

    def _exists(self, username : str) -> bool:
        return self.__redis.exists(username)

    def newUser(self, username : str, password : str) -> None:
        pass

    def setReplicas(self, count : int):
        pass

    def getReplicas(self):
        pass


class Scaler(Database):

    def __init__(self, kube : Kube = None) -> None:
        super().__init__()
        self.kube = kube
        assert self.kube != None , "No connection to cluster"

    
    def setReplicas(self, no : int) -> None:
        # Set replicas on the database
        pass
    

    def setup(self, maxReplicas : int = 5) -> None:
        # Setup current number of replicas running on db
        # Setup max replicas
        self.maxReplicas = maxReplicas
        pass

    def _exception(self):
        pass

    def monitor(self):
        # Get number of active replicas
        # if replicas == max replicas, raise warning and do nothing
        # else calculate the increemnt required
        # Stop the thread with exception
        pass