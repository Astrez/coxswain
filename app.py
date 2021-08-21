from flask.helpers import url_for
from coxswain import *

from flask import Flask, request
from flask_cors import CORS
from datetime import datetime
from threading import Thread

import logging
import jwt

app = Flask(__name__)
# Logging class init
LogSetup(app)

model = Database()
CORS(app)
# kubeConnection = Kube("config.yaml")

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(deployment, url_prefix='/deployment')
app.register_blueprint(details, url_prefix='/details')

# Logger
Logger = logging.getLogger("app.access")

# @app.route('/', methods = ["GET"])
# def hello():
#     with Database() as db:
#         a = 5/0
#         return "No error", 200
#     return "Error", 500


# @app.route('/dashboard', methods = ["GET"])
# def dashboard():
#     '''
#     Dashboard route
#     '''
#     # get details of pods and other specs from the server
#     if (result := kubeConnection.listPods(sendall=True)):
#         return Response.responseFormat(result, status.success)
#     return Response.responseFormat("", status.failure)

# @app.route('/deployment/imageupdate', methods = ["POST"])
# def updateImage():
#     '''
#     update image
#     {
#         "name" : "deployment name",
#         "image" : "image name"
#     }
#     '''
#     body = request.get_json()
#     if (result := kubeConnection.updateDeploymentImage(body.get('name'), body.get('image'))):
#         return Response.responseFormat(result, status.success)
#     return Response.responseFormat("", status.failure)

# @app.route('/deployment/details', methods = ["POST"])
# def getDeploymentDetails():
#     '''
#     deployment details
#     '''
#     body = request.get_json()
#     if (result := kubeConnection.getDeploymentInfo(body.get('name'))):
#         return Response.responseFormat(result, status.success)
#     return Response.responseFormat("", status.failure)

# @app.route('/deployment/replicas', methods = ["POST"])
# def replicas():
#     '''
#     Number of active replicas
#     '''
#     body = request.get_json()
#     if (result := kubeConnection.getReplicaNumber(body.get('name'))):
#         return Response.responseFormat(result, status.success)
#     return Response.responseFormat("", status.failure)

# @app.route('/deployment/scale', methods = ["POST"])
# def scale():
#     '''
#     up/down scale
#     {
#         "name" : "deployment name",
#         "factor" : -5 to 5
#     }
#     '''
#     body = request.get_json()
#     if (result := kubeConnection.updateDeploymentReplicas(body.get('name'), body.get('factor'))):
#         return Response.responseFormat(result, status.success)
#     return Response.responseFormat("", status.failure)


# @app.route('/autoscaler/on', methods = ["GET"])
# def startAutoScaler():
#     '''
#     Start Autoscaler
#     '''
#     thread = Thread(target = autoscaler, args = (Scaler(model, kubeConnection), 5))
#     thread.start()
#     return Response.responseFormat("", status.success)

# @app.route('/autoscaler/off', methods = ["GET"])
# def stopAutoScaler():
#     '''
#     Stop autoscaler
#     '''
#     model.endScaler()
#     return Response.responseFormat("", status.success)

# @app.route('/deployment/create', methods = ["POST"])
# def createDeployment():
#     '''
#     Ceate new deployment
#     {
#         "deploymentName" : "name",
#         "containerName" : "container name",
#         "containerImage" : "image name from dockerhub"
#     }
#     '''
#     body = request.get_json()
#     try:
#         kubeConnection.createDeployment(body.get('deploymentName'), body.get('containerName'), body.get('containerImage'))
#         return Response.responseFormat("", status.success)
#     except Exception as e:
#         return Response.responseFormat("", status.error)

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