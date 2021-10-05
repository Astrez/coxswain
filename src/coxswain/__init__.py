import json
from posix import EX_CANTCREAT


from .utils import *
from .constants import DB_CRED

# Subpackages
from .logger import *
from .persistance import *
from .autoscaler import *
from .kube import *
from .blueprints import *
from .security import *

def initialize(config_file : str = None):
    # Receive postgresql credentials
    # Receive redis credentials
    # Receive config file for kubernetes cluster and setup connection
    # Setup private and public keys for jwt
    if config_file:
        initializer = Initializer(config_file)
        


class Initializer:
    def __init__(self, data : dict, *args, **kwargs) -> None:
        # Load details from configFile
        pass

    @classmethod
    def fromConfigFile(cls, filePath : str):
        if os.path.exists(filePath):
            with open(filePath, 'r') as infile:
                data = json.loads(infile.read())
        else:
            raise Exception("No config file found")
        return cls(data)