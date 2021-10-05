from typing import Tuple, Union
import os
import hashlib
import uuid


class User:

    def __init__(self, name, email, username, password, role, userId = None) -> None:
        self.name = name
        self.email = email
        self.username = username
        self._hashPassword(password)
        self.role = role
        if userId:
            self.userUUID = None
        else:
            self.userUUID = uuid.uuid4()
        self.verified = False

    def _hashPassword(self, rawPassword: str) -> None: 
        salt = os.urandom(32)
        hashed = hashlib.pbkdf2_hmac("SHA256", rawPassword.encode('utf-8'), salt, 100000)
        self.password = salt + hashed

    
    def getInsertSql(self) -> Tuple[str, tuple]:
        data = (self.name, self.email, self.username, self.password, self.role, self.userId)
        sql = 'INSERT into users (name, email, username, password, role, userUUID) VALUES (%s, %s, %s, %s, %s);'
        return sql, data
    
    @classmethod
    def fromUUID(cls, key : str, sqlMethod : function):
        data = sqlMethod(key)
        if data:
            return cls(*data)
        return None
    
    @staticmethod
    def getUserTable() -> str:
        return """DROP TABLE IF EXISTS users;
        CREATE TABLE users(
            userId SERIAL PRIMARY KEY,
            userUUID VARCHAR(15) UNIQUE NOT NULL,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(128) UNIQUE NOT NULL,
            role VARCHAR(20) NOT NULL,
            verified BOOLEAN
        )
            """
    
    @staticmethod
    def getRoleTable() -> str:
        return """DROP TABLE IF EXISTS roles;
        CREATE TABLE roles(
            roleId SERIAL,
            roleUUID VARCHAR(15),
            roleName VARCHAR(20)
        )
            """

    
