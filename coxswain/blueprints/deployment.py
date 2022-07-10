# Blueprint for managing deployment

import os
from flask import Blueprint, request
from ..utils import *
from ..kube import Kube

import yaml
from copy import copy, deepcopy

deployment = Blueprint('deployment', __name__)
kubeConnection = Kube()

# Metrics page

@deployment.route("/metrics", methods = ["GET"])
def dashboard():
    try:
        details = kubeConnection.getPodsMetrics()
        return Response.responseFormat(details, status.success)
    except Exception as e:
        # print(str(e) + traceback.format_exc())
        return Response.responseFormat(str(e) + traceback.format_exc(), status.error)

# Deployment details page

@deployment.route('/get', methods = ["GET"])
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
            details = kubeConnection.updateDeploymentImage(name, image, container, namespace=namespace)

            return Response.responseFormat(details, status.success)
        return Response.responseFormat("", status.badrequest)
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
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
@deployment.route('/pod/get', methods = ["GET"])
def getpods():
    try:
        details = kubeConnection.listPods(sendall=True)
        return Response.responseFormat(details, status.success)
    except Exception as e:
        print(str(e) + traceback.format_exc())
        return Response.responseFormat("", status.error)






@deployment.route('/create', methods = ["POST"])
def createDeployment():
    # 
    try:
        body = request.get_json()
        # Deployment
        with open(os.path.join(os.getcwd(), "coxswain", 'yamltemplates', "deployment-template.yaml")) as deploymentyaml:
            deployment = yaml.safe_load(deploymentyaml)
        
        deployment['metadata']['name'] = body['deploymentName']
        deployment['metadata']['labels']['app'] = body['label']
        deployment['spec']['replicas'] = int(body['replicas'])
        deployment['spec']['selector']['matchLabels']['app'] = body['label']
        deployment['spec']['template']['metadata']['labels']['app'] = body['label']
        containerObj = deployment['spec']['template']['spec']['containers'].pop()
        for container in body.get('containers'):
            containerObj = deepcopy(containerObj)
            containerObj['name'] = container['containerName']
            containerObj['image'] = container['containerImage']
            # containerObj['resources']['requests']['memory'] = str(container['memoryResourceRequest']) + "Mi"
            # containerObj['resources']['requests']['cpu'] = str(container['cpuResourceRequest']) + "m"
            # containerObj['resources']['limits']['memory'] = str(container['memoryResourceLimit']) + "Mi"
            # containerObj['resources']['limits']['cpu'] = str(container['cpuResourceLimit']) + "m"
            containerObj['ports'][-1]['containerPort'] = container['containerPort']
        
            deployment['spec']['template']['spec']['containers'].append(containerObj)
        

        # Service
        with open(os.path.join(os.getcwd(), "coxswain", 'yamltemplates', "service-template.yaml")) as serviceyaml:
            service = yaml.safe_load(serviceyaml)
        service['metadata']['name'] = body['serviceName']
        service['spec']['selector']['app'] = body['label']
        service['spec']['type'] = body['type']
        service['spec']['ports'][-1]['protocol'] = body['protocol']
        service['spec']['ports'][-1]['port'] = body['containers'][0]["containerPort"]
        service['spec']['ports'][-1]['targetPort'] = body['containers'][0]["containerPort"]

        with open("test.yaml", "w") as infile:
            yaml.safe_dump(deployment, infile)
        with open("test.yaml", "r") as outfile:
            kubeConnection.createByYamlFile(dep=yaml.load(outfile, Loader=yaml.FullLoader), dtype = "Deployment")
        
        with open("test.yaml", "w") as infile:
            yaml.safe_dump(service, infile)
        with open("test.yaml", "r") as outfile:
            kubeConnection.createByYamlFile(dep=yaml.load(outfile, Loader=yaml.FullLoader), dtype = "Service")

        return Response.responseFormat("", status.success)
    except Exception as e:
        return Response.responseFormat(str(e) + traceback.format_exc(), status.error)

@deployment.route('/create/yaml', methods = ["POST"])
def createDeploymentYaml():
    try:
        # if 'file' not in request.files:
        #     raise Exception("no file")
        if request.files['deployment'].filename.split(".")[-1] in ['yml', 'yaml']:
            file = request.files['deployment']
            kubeConnection.createByYamlFile(yaml.load(file.stream, Loader=yaml.FullLoader))
        else:
            raise Exception("Wrong format")
        
        if request.files['service'].filename.split(".")[-1] in ['yml', 'yaml']:
            file = request.files['service']
            kubeConnection.createByYamlFile(yaml.load(file.stream, Loader=yaml.FullLoader))
        else:
            raise Exception("Wrong format")
        return Response.responseFormat("", status.success)
    except Exception as e:
        return Response.responseFormat(str(e), status.error)