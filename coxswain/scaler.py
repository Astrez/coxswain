from .kube import Kube
from .models import Database

from typing import TypeVar, Callable, Any

import logging
import statistics
import traceback
import time
import random
import math

F = TypeVar('F', bound=Callable[..., Any])
logger = logging.getLogger("app.scale")

DEPLOYMENT = 'flask-dev'

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
        self.scaleFlag = False
        self.skip = False
        self.data = list()
        # assert self.kube != None , "No connection to cluster"
        assert self.database != None , "No connection to database"

    def setReplicas(self) -> None:
        # Edit here
        logger.info("Initialised replica value in cache")
        self.database.replicaInit(3)
        # self.database.replicaInit(self.kube.getReplicaCount())
    
    def flag(self) -> bool:
        if self.scaleFlag:
            self.scaleFlag = False
            return True
        if not self.skip:
            return True
        return False

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
    
    def scale(self, replica : int):
        logger.warning(f"Scaling upto : {replica}")
        # self.kube.replaceDeploymentReplicas(DEPLOYMENT, replica)
        self.database.setReplicas(replica)
        self.data = list()
        self.scaleFlag = True

    def monitor(self, metric : float = 0.0) -> bool:
        # Get number of active replicas

        # active = self.kube.getReplicaNumber(DEPLOYMENT)
        active = self.database.getReplicas()

        final = self.calculate(metric)
        logger.debug(f"Calculated metric : required number of replicas : {final}")
        if final >= self.maxReplicas:
            if active < self.maxReplicas:
                logger.warning("Max replicas reached")
                self.scale(self.maxReplicas)
            elif active == self.maxReplicas:
                logger.warning("Cannot upscale max replicas already reached")
                self.flag() 
            else:
                self.scale(final)
        elif final < 1:
            if active == 1:
                logger.warning("Cannot downscale low margin reached")
            else: 
                self.scale(1)
                logger.warning("Min replicas reached")
        elif final == active:
            logger.debug("No scale")
        else:
            self.scale(final)
        
        # Stop the thread by checking database state
        return self.database.checkAbort()

    def calculate(self, metric : float):
        # calculate based on the current metrics and previous metrics

        # Load previous metrics
        desired = 1200
        originalmean = ean = statistics.geometric_mean(self.data) if self.data else None
        self.data.append(metric/desired)
        if len(self.data) > 5:
            self.data.pop(0)
        mean = statistics.geometric_mean(self.data)
        if originalmean : 
            if round(mean, 1) > round(originalmean, 1):
                self.skip = False
            else: 
                self.skip = True
        print(f"Mean : {mean}")
        return round((mean / 1.12 * self.database.getReplicas()))


def autoscaler(scaler : Scaler, maxReplicas : int = 5) -> None:
    try:
        count = 2
        logger.info("Auto Scaler initialised")

        # Initialise all flags in the database too

        # get current replica value from Kube object
        scaler.setup(maxReplicas)
        logger.info(f"Initialised max replicas as {maxReplicas}" )
        starttime = time.time()
        while True:
            # Get response time here in the metric instead of random time
            metric = random.randint(800, 1750)
            if scaler.monitor(metric):
                scaler.abort()
                break
            if not scaler.flag():
                count += 2
                if count > 10:
                    count = 10
            else:
                count = 2
            time.sleep(count - ((time.time() - starttime) % count))
    except Exception as e:
        logger.error(str(e) + traceback.format_exc())
        logger.critical("Autoscaler aborting....")
        scaler.abort()
    logger.warning("Autoscaler aborted")
    

if __name__ == "__main__":
    autoscaler(Scaler(Database()), 10)
