from coxswain import *
from flask import Flask, request
from flask_cors import CORS
import logging
import jwt
from datetime import datetime
from threading import Thread

app = Flask(__name__)
# Logging class init
LogSetup(app)

model = Database()
CORS(app)
kubeConnection = Kube("config.yaml")

# Logger
Logger = logging.getLogger("app.access")

@app.route('/', methods = ["GET"])
def hello():
    return "Hello World", 200


@app.route('/dashboard', methods = ["GET"])
def dashboard():
    '''
    Dashboard route
    '''
    # get details of pods and other specs from the server
    if (result := kubeConnection.getDashboard()):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)

@app.route('/deployment/imageupdate', methods = ["POST"])
def updateImage():
    '''
    update image
    {
        "image" : "image name"
    }
    '''
    body = request.get_json()
    if (result := kubeConnection.updateImage(body.get('image'))):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)

@app.route('/deployment/details', methods = ["GET"])
def getDeploymentDetails():
    '''
    deployment details
    '''
    if (result := kubeConnection.getDeploymentDetails()):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)

@app.route('/deployment/replicas', methods = ["GET"])
def replicas():
    '''
    Number of active replicas
    '''
    if (result := kubeConnection.getReplicas()):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)

@app.route('/deployment/scale', methods = ["POST"])
def scale():
    '''
    up/down scale
    {
        "factor" : -5 to 5
    }
    '''
    body = request.get_json()
    if (result := kubeConnection.scale(body.get('factor'))):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)


@app.route('/autoscaler/on', methods = ["GET"])
def startAutoScaler():
    '''
    Start Autoscaler
    '''
    thread = Thread(target = autoscaler, args = (Scaler(model, kubeConnection), 5))
    thread.start()
    return Response.responseFormat("", status.success)

@app.route('/autoscaler/off', methods = ["GET"])
def stopAutoScaler():
    '''
    Stop autoscaler
    '''
    model.endScaler()
    return Response.responseFormat("", status.success)

# _______________________________AUTH_____________________________________
# Signin route
@app.route('/auth/signin', methods = ["POST"])
def signin():
    body = request.get_json()
    if model.compare(body):
        token = {"username" : body.get("username")}
        token = jwt.encode(token, key= "SECRET KEY", algorithm="HS256")
        if type(token) == bytes:
            token.decode("utf-8")
        return Response.responseFormat(token, status.success)
    return Response.responseFormat("", status.unauth)


@app.route('/auth/signup', methods = ["POST"])
def signup():
    body = request.get_json()
    if model.newUser(body.get('username'), body.get('password')):
        token = {"username" : body.get("username")}
        token = jwt.encode(token, key= "SECRET KEY", algorithm="HS256")
        if type(token) == bytes:
            token.decode("utf-8")
        return Response.responseFormat(token, status.success)
    return Response.responseFormat("Database Error: User already exists", status.error)


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