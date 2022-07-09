# Blueprint for managing deployment

from flask import Blueprint, request
from ..utils import *
from ..kube import Kube

import yaml

deployment = Blueprint('deployment', __name__)
kubeConnection = Kube()

# Metrics page

@deployment.route("/metrics", methods = ["GET"])
def dashboard():
    try:
        details = kubeConnection.getPodsMetrics()
        return Response.responseFormat(details, status.success)
    except Exception as e:
        return Response.responseFormat("", status.error)

# Deployment details page

@deployment.route('/deployments', methods = ["GET"])
def getDeployments():
    try:
        details = kubeConnection.listAllDeployments()
        return Response.responseFormat(details, status.success)
    except Exception as e:
        return Response.responseFormat("", status.error)

@deployment.route('/update/replicas', methods = ["POST"])
def replaceReplicas():
    try:
        body = request.get_json()
        name, namespace, replicas = body.get("name", None), body.get("namespace", None), int(body.get("replicas", None))
        if name and namespace and replicas:
            details = kubeConnection.replaceDeploymentReplicas(name, replicas, namespace=namespace)
            return Response.responseFormat(details, status.success)
        return Response.responseFormat("", status.badrequest)
    except Exception as e:
        return Response.responseFormat("", status.error)

@deployment.route('/update/image', methods = ["POST"])
def replaceImage():
    try:
        body = request.get_json()
        name, namespace, container, image = body.get("name", None), body.get("namespace", None), body.get("container", None), body.get("image", None)
        if name and namespace and container and image:
            # TODO: Change here
            details = kubeConnection.updateDeploymentImage(name, image, namespace=namespace)

            return Response.responseFormat(details, status.success)
        return Response.responseFormat("", status.badrequest)
    except Exception as e:
        return Response.responseFormat("", status.error)

@deployment.route('/delete', methods = ["POST"])
def deleteDeployment():
    try:
        body = request.get_json()
        name, namespace = body.get("name", None), body.get("namespace", None)
        if name and namespace:
            details = kubeConnection.deleteDeployment(name, namespace)
            return Response.responseFormat(details, status.success)
        return Response.responseFormat("", status.badrequest)
    except Exception as e:
        return Response.responseFormat("", status.error)

# Pod details
@deployment.route('/pod/details', methods = ["GET"])
def getpods():
    try:
        details = kubeConnection.listPods(sendall=True)
        return Response.responseFormat(details, status.success)
    except Exception as e:
        return Response.responseFormat("", status.error)






@deployment.route('/create', methods = ["POST"])
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

@deployment.route('/create/yaml', methods = ["POST"])
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