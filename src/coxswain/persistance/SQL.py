import psycopg2
import psycopg2.extras
from .entities import User
from ..constants import *
from functools import wraps

class SQLDatabase:
    def __init__(self):
        self.conn = psycopg2.connect(**POSTGRES_CREDENTIALS)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            self.cur.execute(User.getUserTable())
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            self.conn.commit()

    def _errorhandler(f):    
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                raise Exception
        return wrapper
    
    def addNewUser(self, user : User) -> None:
        """Add New user to the database

        Args:
            user (User): User Object from entities
        """        
        # Check parameter datatype
        assert type(user) == User, "Wrong parameter datatype"

        sql, data = user.getInsertSql()
        try:
            self.cur.execute(sql, data)
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            self.conn.commit
    
    def getUser(self, userId : str) -> dict:
        """Get User Details

        Args:
            userId (str): user UUID

        Returns:
            dict: userdata
        """        

        # Check parameter datatype
        assert type(userId) == str, "Wrong parameter datatype"

        sql = 'SELECT name, email, username, password, role, userUUID FROM users WHERE userUUID = %s'
        self.cur.execute(sql, (userId, ))
        data = self.cur.fetchone()
        if data:
            return dict(data)
        return None
