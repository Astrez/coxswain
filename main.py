from coxswain import *

from flask import Flask, request
from flask_cors import CORS
from datetime import datetime
from threading import Thread

import logging
import jwt
import yaml

app = Flask(__name__)
# Logging class init
LogSetup(app)

CORS(app)
kubeConnection = Kube()

# Logger
Logger = logging.getLogger("app.access")

app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(deployment, url_prefix='/api/deployment')
app.register_blueprint(auth)


@app.route('/', methods = ["GET"])
def hello():
    return "Hello World", 200

# @app.after_request
# def after_request(response):
#     """
#     This function runs after request is served. Logging is done after
#     """    
#     params = '&'.join([i + '=' + j for i, j in request.args.items()])
#     Logger.info(
#         '%s - - [%s] "%s %s%s %s" %s - %s %s %s',
#         request.remote_addr,
#         datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
#         request.method,
#         request.path,
#         '?' + params if params else '',
#         request.scheme.upper(),
#         response.status,
#         response.content_length,
#         request.referrer,
#         request.user_agent,
#     )
#     return response


if __name__ == "__main__":
    app.run(debug=True)