from logging.config import dictConfig
from flask.logging import default_handler

import logging

# Logger for errors
errLogger = logging.getLogger("app.logger")

class LogSetup(object):    

    '''Setup Logging system for error and request logging. 

    Constants:
        LOG_DIR = path to directory where log file is saved

        ERR_FILE = name of the file for logging errors

        REQ_FILE = name of the file for logging requests

        ERR_LOG_LEVEL = level of events that is to be logged DEBUG < INFO < WARNING < ERROR < CRITICAL

        REQ_LOG_LEVEL = level of events that is to be logged ( If changed from `INFO` please update the logger function call to appropriate level in main.py )
    '''

    LOG_DIR = "./"
    ERR_FILE = 'logs/app.log'
    REQ_FILE = 'logs/req.log'
    SCALER_FILE = 'logs/scale.log'
    ERR_LOG_LEVEL = 'DEBUG'
    REQ_LOG_LEVEL = 'INFO'
    SCALER_LOG_LEVEL = 'INFO'

    def __init__(self, app) -> None:
        '''Setup Logging system for error and request logging
        '''
        # Remove logging on command line which might be a problem while hosting
        app.logger.removeHandler(default_handler)

        appLog = "/".join([LogSetup.LOG_DIR, LogSetup.ERR_FILE])
        wwwLog = "/".join([LogSetup.LOG_DIR, LogSetup.REQ_FILE])
        scalerLog = "/".join([LogSetup.LOG_DIR, LogSetup.SCALER_FILE])
        loggingPolicy = "logging.handlers.WatchedFileHandler"

        # dictConfig 
        stdFormat = {
            "formatters": {
                "default": {
                    "format": "[%(asctime)s.%(msecs)03d] %(levelname)s %(name)s:%(funcName)s: %(message)s",
                    "datefmt": "%d/%b/%Y:%H:%M:%S",
                },
                "access": {"format": "%(message)s"},
            }
        }
        stdLogger = {
            "loggers": {
                "app.logger": {"level": LogSetup.ERR_LOG_LEVEL, "handlers": ["default"], "propagate": True},
                "app.access": {
                    "level": LogSetup.REQ_LOG_LEVEL,
                    "handlers": ["access_logs"],
                    "propagate": False,
                },
                "app.scale": {
                    "level": LogSetup.SCALER_LOG_LEVEL,
                    "handlers": ["scaler_logs"],
                    "propagate": False,
                },
                "root": {"level": LogSetup.ERR_LOG_LEVEL, "handlers": ["default"]},
            }
        }
        loggingHandler = {
                "handlers": {
                    "default": {
                        "level": LogSetup.ERR_LOG_LEVEL,
                        "class": loggingPolicy,
                        "filename": appLog,
                        "formatter": "default",
                        "delay": True,
                    },
                    "access_logs": {
                        "level": LogSetup.REQ_LOG_LEVEL,
                        "class": loggingPolicy,
                        "filename": wwwLog,
                        "formatter": "access",
                        "delay": True,
                    },
                    "scaler_logs": {
                        "level": LogSetup.SCALER_LOG_LEVEL,
                        "class": loggingPolicy,
                        "filename": scalerLog,
                        "formatter": "default",
                        "delay": True,
                    },
                }
            }
        log_config = {
            "version": 1,
            "formatters": stdFormat["formatters"],
            "loggers": stdLogger["loggers"],
            "handlers": loggingHandler["handlers"],
        }
        dictConfig(log_config)