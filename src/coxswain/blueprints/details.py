# Blueprint for monitering

from flask import Blueprint, request

details = Blueprint('details', __name__)

@details.route('/get')
def getDetails():
    return "Hello World", 200