from coxswain import *
from flask import Flask, request
from flask_cors import CORS
import logging
from datetime import datetime

app = Flask(__name__)
# Logging class init
LogSetup(app)

model = Database()
CORS(app)
kubeConnection = Kube()

# Logger
Logger = logging.getLogger("app.access")

@app.route('/', methods = ["GET"])
def hello():
    return "Hello World", 200

# Signin route
@app.route('/auth/signin', methods = ["POST"])
def signin():
    body = request.get_json()
    if model.compare(body):
        return "Hello World", 200
    return "Not Authorized", 403


@app.route('/auth/signup', methods = ["POST"])
def signup():
    body = request.get_json()
    if model.newUser(body):
        return "Hello World", 200
    return "Database Error", 500


@app.after_request
def after_request(response):
    """
    This function runs after request is served. Logging is done after
    """    
    params = '&'.join([i + '=' + j for i, j in request.args.items()])
    Logger.info(
        '%s - - [%s] "%s %s%s %s" %s - %s %s %s',
        request.remote_addr,
        datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
        request.method,
        request.path,
        '?' + params if params else '',
        request.scheme.upper(),
        response.status,
        response.content_length,
        request.referrer,
        request.user_agent,
    )
    return response


if __name__ == "__main__":
    app.run(debug=True)