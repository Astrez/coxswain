from .kube import Kube
from .models import Database

from typing import TypeVar, Callable, Any

import logging
import statistics
import traceback
import time


F = TypeVar('F', bound=Callable[..., Any])
logger = logging.getLogger("app.scale")

class Scaler():

    def _errorHandler(func : F) -> F:
        def wrapper(self, *args, **kwargs) -> Any:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.error(str(e) + '\n' + traceback.format_exc())
                raise e
        return wrapper

    @_errorHandler
    def __init__(self, database : Database = None, kube : Kube = None) -> None:
        self.kube = kube
        self.database = database
        assert self.kube != None , "No connection to cluster"
        assert self.database != None , "No connection to database"

    def setReplicas(self) -> None:
        # Edit here
        logger.info("Initialised replica value in cache")
        self.database.replicaInit(1)
        # self.database.replicaInit(self.kube.getReplicaCount())
    

    def setup(self, maxReplicas : int = 5) -> None:
        logger.info("Checking state of scaler on cache")
        statusInit = self.database.initScaler()
        if not statusInit[0]:
            raise Exception("Invalid state in database. Abort scaler")
        if statusInit[1]:
            logger.warning("Restarting autoscaler! Data in database will be replaced with fresh values")
        logger.info("Initialised state in the database")
        # Setup current number of replicas running on db
        self.setReplicas()
        # Setup max replicas
        self.maxReplicas = maxReplicas

    def abort(self):
        logger.warning("Stopping autoscaler!")
        self.database.endScaler()
        logger.warning("Scaler state changed")

    def monitor(self) -> bool:
        # Get number of active replicas
        # if replicas == max replicas, raise warning and do nothing
        # else calculate the increemnt required
        # Stop the thread with exception
        logger.info("Calculate...")
        return self.database.checkAbort()




def autoscaler(scaler : Scaler, maxReplicas : int = 5) -> None:
    try:
        logger.info("Auto Scaler initialised")

        # Initialise all flags in the database too

        # get current replica value from Kube object
        scaler.setup(maxReplicas)
        logger.info(f"Initialised max replicas as {maxReplicas}" )
        starttime = time.time()
        while True:
            if scaler.monitor():
                scaler.abort()
                break
            time.sleep(5.0 - ((time.time() - starttime) % 5.0))
    except Exception as e:
        logger.error(str(e) + traceback.format_exc())
        logger.critical("Autoscaler aborting....")
    
    logger.critical("Autoscaler aborting....")
    