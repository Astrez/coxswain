"""
File to manage User service, Auth and token validation
"""

from flask import Flask, request
import coxswain
from coxswain import Response, status

from flask_cors import CORS

import logging
import jwt

app = Flask(__name__)
coxswain.LogSetup(app)

mosql = coxswain.NoSQLDatabase()
sql = coxswain.SQLDatabase()
CORS(app)

key = coxswain.readKey.getPrivate()

# Logger
Logger = logging.getLogger("app.access")

# Validate token
@app.route("/auth/validate")
def validate():
    try:
        token = request.headers.get("Authorization")
        if token:
            payload = jwt.decode(token, key, algorithms=['RS256']) 
            user = coxswain.User.fromUUID(payload.get("UserId"), sql.getUser)
            if user:
                return Response.responseFormat("", status.success)
            return Response.responseFormat("No user found", status.unauth)
        return Response.responseFormat("No token in headers", status.bad_request)
    except Exception as e:
        return Response.responseFormat(str(e), status.unauth)

# TODO: Refresh token
@app.route("/auth/refresh", methods=["POST"])
def refresh():
    try:
        data = request.get_json()
        if (refToken := data.get("refreshToken")):
            pass
        return Response.responseFormat("No token in headers", status.bad_request)
    except Exception as e:
        return Response.responseFormat(str(e), status.unauth)