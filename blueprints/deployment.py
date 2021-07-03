# Blueprint for managing deployment

from flask import Blueprint, request

deployment = Blueprint('deployment', __name__)

@deployment.route('/create')
def createDeployment():
    return "Hello World", 200