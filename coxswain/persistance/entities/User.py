from typing import Tuple, Union


class User:

    def __init__(self, name, email, username, password, role) -> None:
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.role = role
        self.userId = None

    
    def getInsertSql(self, data : Union[list, tuple]) -> Tuple[str, tuple]:
        returnData = []
        for user in data:
            # Validate user
            if not user:
                raise Exception("Invalid or Incomplete User Details")
            returnData.extend(user)
    
        sql = 'INSERT into users (name, email, username, password, role) VALUES ' + ", ".join(["(%s, %s, %s, %s, %s)" for _ in data])

        return sql, tuple(returnData)
    
    @staticmethod
    def getUserTable() -> str:
        return """DROP TABLE IF EXISTS users;
        CREATE TABLE users(
            userId SERIAL,
            userUUID VARCHAR(15),
            name VARCHAR(100),
            email VARCHAR(100),
            username VARCHAR(100),
            password VARCHAR(128),
            role VARCHAR(20)
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

    
