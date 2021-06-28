from coxswain import *

from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_cors import CORS
from datetime import datetime
from threading import Thread
from functools import wraps

import logging
import jwt

NAME = "fancy-pants"

app = Flask(__name__)
app.secret_key = 'any random string'

# Logging class init
LogSetup(app)

model = Database()
CORS(app)
kubeConnection = Kube("config.yaml")


# Logger
Logger = logging.getLogger("app.access")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = dict(session).get('username', None)
        if user:
            return f(*args, **kwargs)
        return redirect('/auth/signin')
    return decorated_function

@app.route('/dashboard', methods = ["GET"])
def dashboard():
    '''
    Dashboard route
    '''
    # get details of pods and other specs from the server
    if (result := kubeConnection.listPods(sendall=True)):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)

@app.route('/deployment/create', methods = ["GET"])
def deploymentUpdateGet():
    return render_template("create.html")

@app.route('/deployment/create', methods = ["POST"])
def createDeployment():
    '''
    Ceate new deployment
    {
        "deploymentName" : "name",
        "containerName" : "container name",
        "containerImage" : "image name from dockerhub"
    }
    '''
    global NAME
    body = request.form.to_dict()
    NAME = body.get('deploymentName')
    try:
        kubeConnection.createDeployment(body.get('deploymentName'), body.get('containerName'), body.get('containerImage'))
        return "hello world"
    except Exception as e:
        return Response.responseFormat("", status.error)


@app.route('/deployment/imageupdate', methods = ["POST"])
def updateImage():
    body = request.form.to_dict()
    if (result := kubeConnection.updateDeploymentImage(NAME, body.get('image'))):
        # redirect to dashboard
        return redirect("/deployment/details")
    return Response.responseFormat("", status.failure)

@app.route('/deployment/details', methods = ["GET"])
@login_required
def getDeploymentDetails():
    '''
    deployment details
    '''
    body = "fancy-pants"
    if (result := kubeConnection.getDeploymentInfo(body)):
        return render_template("update.html", deployment=result)
    return render_template("update.html", deployment=None)

@app.route('/deployment/replicas', methods = ["POST"])
def replicas():
    '''
    Number of active replicas
    '''
    body = request.get_json()
    if (result := kubeConnection.getReplicaNumber(NAME)):
        return Response.responseFormat(result, status.success)
    return Response.responseFormat("", status.failure)


@app.route('/deployment/scale', methods = ["GET"])
def scaleGet():
    if (result := kubeConnection.getReplicaNumber(NAME)):
        return render_template("scale.html", replicas = result)
    return render_template("scale.html", replicas = None)
    


@app.route('/deployment/scale', methods = ["POST"])
def scale():

    body = request.form.to_dict()
    if (result := kubeConnection.updateDeploymentReplicas(NAME, int(body.get('factor')))):
        return redirect('/deployment/scale')
    return redirect('/deployment/scale')


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

@app.route('/deployment/create', methods = ["GET"])
def createDeploymentGet():
    return render_template("deployment.html")












# _______________________________AUTH_____________________________________
# Signin route

@app.route('/auth/signin', methods = ["GET"])
def getSignin():
    return render_template('signin.html')

@app.route('/auth/signin', methods = ["POST"])
def signin():
    body = request.form.to_dict()
    if model.compare(body):
        token = {"username" : body.get("username")}
        token = jwt.encode(token, key= "SECRET KEY", algorithm="HS256")
        if type(token) == bytes:
            token.decode("utf-8")
        session['username'] = 'exists'    
        return "Hello World"
    return Response.responseFormat("", status.unauth)


@app.route('/auth/signup', methods = ["GET"])
def getSignup():
    return render_template('signup.html')

@app.route('/auth/signup', methods = ["POST"])
def signup():
    body = request.form.to_dict()
    if body.get('username') != "" or body.get('password') != "":
        if model.newUser(body.get('username'), body.get('password')):
            token = {"username" : body.get("username")}
            token = jwt.encode(token, key= "SECRET KEY", algorithm="HS256")
            if type(token) == bytes:
                token.decode("utf-8")
            return redirect("/deployment/create")
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