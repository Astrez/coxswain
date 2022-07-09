# Blueprint for monitering

from flask import Blueprint, request
from ..kube import Kube
from ..utils import *

deployment = Blueprint('deployment', __name__)
kubeConnection = Kube()

autoscale = Blueprint('autoscale', __name__)

@autoscale.route('/get')
def ml():
    if (result := kubeConnection.getMetricsForML()):
        return Response.responseFormat(round(result/1600), status.success)
    return Response.responseFormat("", status.failure)