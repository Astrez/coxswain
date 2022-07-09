from flask import Blueprint, request
import jwt
from ..persistance import *
from ..utils import *
from ..cert import *

model = NoSQL()

auth = Blueprint('auth', __name__)

@auth.route("/signin", methods = ["POST"])
# @cross_origin()
def signin():
    try:
        data = request.get_json()
        if data:
            username, password = data.get("username", None), data.get("password", None)
            if username and password:
                user = model.getUser(username)
                if user:
                    if user.compare(password):
                        token = jwt.encode({"username" : username, "role" : user.role}, SECRET, algorithm='HS256')
                        if type(token) == bytes:
                            token = token.decode("ascii")
                        return Response.responseFormat(token, status.success)
                    return Response.responseFormat("Password Wrong", status.unauthorized)
                return Response.responseFormat("No User Found", status.unauthorized)
            return Response.responseFormat("Request body incorrect", status.badrequest)
        return Response.responseFormat("No Request body", status.badrequest)
    except Exception as e:
        return Response.responseFormat(str(e) + traceback.format_exc(), status.error)

@auth.route("/", methods = ["GET"])
# @cross_origin()
def getUser():
    try:
        token = request.headers.get('Authorization')
        if token:
            data = jwt.decode(token, SECRET, algorithms=['HS256'])
            user = model.getUser(data.get("username", None))
            if user:
                return Response.responseFormat(user.getDict(), status.success)
            return Response.responseFormat("", status.failure)
        return Response.responseFormat("No Token", status.unauthorized)
    except Exception as e:
        return Response.responseFormat("Token invalid or expired or internal server error", status.unauthorized)

@auth.route("/signup", methods = ["post"])
def signup():
    try:
        token = request.headers.get('Authorization')
        if token:
            data = jwt.decode(token, SECRET, algorithms=['HS256'])
            userdata = request.get_json()
            if data.get("role") == "A":
                model.setUser(User(**userdata))
                return Response.responseFormat("", status.success)
            print(data)
            return Response.responseFormat("", status.unauthorized)
        return Response.responseFormat("No Token", status.unauthorized)
    except Exception as e:
        return Response.responseFormat("Token invalid or expired or internal server error", status.unauthorized)
