import redis
import hashlib
import os
import logging
import traceback

from typing import Tuple, TypeVar, Callable, Any

F = TypeVar('F', bound=Callable[..., Any])
logger = logging.getLogger("app.logger")

class NoSQLDatabase():

    def _errorHandler(func : F) -> F:
        def wrapper(self, *args, **kwargs) -> Any:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.error(str(e) + '\n' + traceback.format_exc())
                raise e
        return wrapper

    @_errorHandler
    def __init__(self) -> None:
        self.__redis = redis.Redis()

        assert self.__redis.ping(), "Connection Error"
    
    def __enter__(self):
        return self
    
    def __exit__(self, ex_type, ex_obj, traceback_obj):
        if ex_obj:
            logger.error(str(ex_obj) + '\n' + traceback.format_exc())
        return True

    @property
    def redis(self):
        # For custom queries
        return self.__redis

    @_errorHandler
    def compare(self, cred : dict) -> bool:
        if self._exists(cred.get('username')):
            password = self.__redis.get(cred['username']).decode("utf-8")
            hashed = hashlib.pbkdf2_hmac('sha256', cred['password'].encode('utf-8'), bytes.fromhex(password[:64]), 100000)
            if hashed.hex() == password[64:]:
                return True
        return False

    @_errorHandler
    def _exists(self, username : str) -> bool:
        return self.__redis.exists(username)


    @_errorHandler
    def newUser(self, username : str, password : str) -> None:
        if self._exists(username):
            return False
        salt = os.urandom(32)
        hashed = salt.hex() + hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()
        self.__redis.set(username, hashed)
        return True
    

    @_errorHandler
    def replicaInit(self, count : int) -> None:
        self.__redis.set("scaler", count)


    @_errorHandler
    def setReplicas(self, count : int) -> None:
        # if count > 0:
        #     self.__redis.incrby("scaler", count)
        # else:
        #     self.__redis.decrby("scaler", abs(count))
        self.__redis.set("scaler", abs(count))


    @_errorHandler
    def getReplicas(self) -> int:
        return int(self.__redis.get("scaler"))

    def initScaler(self) -> Tuple[bool, bool]:
        flag = False
        if self._exists("scalerState"):
            flag = True
            if self.__redis.get("scalerState").decode("utf-8").lower() == "on":
                return False, False                
        self.__redis.set("scalerState", "on")
        return True, flag
            
    
    def endScaler(self) -> None:
        if self._exists("scalerState"):
            self.__redis.set("scalerState", "off")
        else:
            raise Exception("Invalid state")       

    
    def checkAbort(self):
        if self._exists("scalerState"):
            if self.__redis.get("scalerState").decode("utf-8").lower() == "on":
                return False
            else:
                return True
        else:
            raise Exception("Invalid state")