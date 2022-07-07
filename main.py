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

@app.route('/', methods = ["GET"])
def hello():
    return "Hello World", 200

@app.route('/deployment/create', methods = ["POST"])
def createDeployment():
    '''
    Create new deployment
    {
        "deploymentName" : "name",
        "containerName" : "container name",
        "containerImage" : "image name from dockerhub",
        "port" : 8080,
        "targetPort" : 5000,
        "replicas" : 1,
        "deploymentNamespace" : "default",
    }
    '''
    body = request.get_json()
    try:
        replicas = body.get('replicas')
        if replicas > 5:
            replicas = 5 
        elif replicas < 1:
            replicas = 1 
        
        deploymentNameSpace = body.get('deploymentNamespace')
        if deploymentNameSpace == "":
            deploymentNameSpace = "default"
        kubeConnection.createDeployment(body.get('deploymentName'), body.get('containerName'), body.get('containerImage'), body.get('port'), body.get('targetPort'), replicas, deploymentNameSpace)
        return Response.responseFormat("", status.success)
    except Exception as e:
        return Response.responseFormat("", status.error)

@app.route('/deployment/create/yaml', methods = ["POST"])
def createDeploymentYaml():
    '''
    '''
    try:
        if 'file' not in request.files:
            raise Exception("no file")
        if request.files['file'].filename.split(".")[-1] in ['yml', 'yaml']:
            file = request.files['file']
            kubeConnection.createDeploymentByYamlFile(yaml.load_all(file.stream, Loader=yaml.FullLoader))
        else:
            raise Exception("Wrong format")
        # kubeConnection.createDeployment(body.get('deploymentName'), body.get('containerName'), body.get('containerImage'), body.get('port'), body.get('targetPort'), replicas, deploymentNameSpace)
        return Response.responseFormat("", status.success)
    except Exception as e:
        return Response.responseFormat(str(e), status.error)

@app.route('/deployment/update', methods = ["POST"])
def updateImage():
    '''
    update image
    {
        "name" : "deployment name",
        "image" : "image name",
        "namespace" : "image name"
    }
    '''
    body = request.get_json()
    deploymentNameSpace = body.get('deploymentNameSpace')
    if deploymentNameSpace == "":
        deploymentNameSpace = "default"
    if (result := kubeConnection.updateDeploymentImage(body.get('name'), body.get('image'), deploymentNameSpace)):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)


@app.route('/deployment/delete', methods = ["POST"])
def deleteDeployment():
    '''
    delete deployment
    {
        "name" : "deployment name",
        "namespace" : "image name"
    }
    '''
    body = request.get_json()
    deploymentNameSpace = body.get('deploymentNameSpace')
    if deploymentNameSpace == "":
        deploymentNameSpace = "default"
    if (result := kubeConnection.deleteDeployment(body.get('name'), deploymentNameSpace)):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)

@app.route('/metrics', methods = ["GET"])
def metrics():
    if (result := kubeConnection.getPodsMetrics()):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)

@app.route('/deployment', methods = ["GET"])
def allDeployments():
    if (result := kubeConnection.listAllDeployments()):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)

@app.route('/pods', methods = ["GET"])
def allPods():
    if (result := kubeConnection.listPods(sendall=True)):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)

@app.route('/autometrics', methods = ["GET"])
def ml():
    if (result := kubeConnection.getMetricsForML()):
        return Response.responseFormat(round(result/1600), status.success)
    return Response.responseFormat("", status.failure)

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