from flask import Blueprint, request
import jwt
from ..coxswain import *

model = Database()

auth = Blueprint('auth', __name__)

@auth.route('/signin', methods = ["POST"])
def signin():
    body = request.get_json()
    if model.compare(body):
        token = {"username" : body.get("username")}
        token = jwt.encode(token, key= "SECRET KEY", algorithm="HS256")
        if type(token) == bytes:
            token.decode("utf-8")
        return Response.responseFormat(token, status.success)
    return Response.responseFormat("", status.unauth)


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

