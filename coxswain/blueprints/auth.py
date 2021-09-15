from flask import Blueprint, request
import jwt
from ..persistance import *
from ..utils import *

model = NoSQLDatabase()

auth = Blueprint('auth', __name__)

@auth.route('/signin', methods = ["POST"])
def signin():
    body = request.get_json()
    with NoSQLDatabase() as model:
        if model.compare(body):
            token = {"username" : body.get("username")}
            token = jwt.encode(token, key= "SECRET KEY", algorithm="HS256")
            if type(token) == bytes:
                token.decode("utf-8")
            return Response.responseFormat(token, status.success)
        else:
            return Response.responseFormat("", status.unauth)
    return Response.responseFormat("", status.error)


@auth.route('/auth/signup', methods = ["POST"])
def signup():
    body = request.get_json()
    if model.newUser(body.get('username'), body.get('password')):
        token = {"username" : body.get("username")}
        token = jwt.encode(token, key= "SECRET KEY", algorithm="HS256")
        if type(token) == bytes:
            token.decode("utf-8")
        return Response.responseFormat(token, status.success)
    return Response.responseFormat("Database Error: User already exists", status.error)

