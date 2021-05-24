from coxswain import *
from flask import Flask, request
from flask_cors import CORS
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Logging class init
LogSetup(app)

# Logger
Logger = logging.getLogger("app.access")

@app.route('/', methods = ["GET"])
def hello():
    return "Hello World", 200


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