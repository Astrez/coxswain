import psycopg2
import psycopg2.extras
from .entities import User
from ..constants import *
from functools import wraps

class SQLDatabase:
    def __init__(self):
        self.conn = psycopg2.connect(**POSTGRES_CREDENTIALS)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def _errorhandler(f):    
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                raise Exception
        return wrapper
