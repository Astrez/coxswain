from .utils import *
from .constants import DB_CRED

# Subpackages
from .logger import *
from .persistance import *
from .autoscaler import *
from .kube import *
from .blueprints import *
from .security import *

def initialize():
    # Receive postgresql credentials
    # Receive redis credentials
    # Receive config file for kubernetes cluster and setup connection
    pass