import sys
import flask
from flask import request
from flask import Response
from flask import jsonify
from flask import render_template
from flask import redirect
from flask import g
from flask_sslify import SSLify
import jwt
from datetime import datetime, timedelta
from copy import copy
from threading import Thread
import grocery_coupons
from configparser import RawConfigParser

app = flask.Flask(__name__)
sslify = SSLify(app)

data = {} # In-memory session.

secret = 'x0Wm5hfk78cBaG2MkM1d' # Token secret key.
version = 2.95

@app.before_request
def before_request():
    g.error = None

    # Validate a token before each api request.
    if '/api' in request.path:
        token = request.args.get('token', type = str) or request.headers.get('token', type = str)
        if token:
            try:
                # Set the request context to include the payload from the token.
                g.payload = jwt.decode(token, secret, algorithms=['HS256'])
            except Exception as e:
                g.error = 'Invalid token.'
                g.exception = e
        else:
            g.error = 'Missing token.'
            g.exception = ''

@app.route('/api/login', methods = ['POST'])
def login():
    token = None

    content = request.json
    if content:
        username = content['username'] if 'username' in content else None
        password = content['password'] if 'password' in content else None

        if username and password:
            # Generate a token.
            token = jwt.encode({ 'username': username, 'exp': datetime.utcnow() + timedelta(minutes = 10) }, secret, algorithm = 'HS256')

            # Set user in session variable.
            data[username] = {
                'username': username,
                'password': password,
                'startDate': datetime.now(),
                'status': 'IDLE',
                'count': 0,
                'existingCount': 0
            }

            # Collect coupons.
            onCollect(username, password)

    return jsonify({ 'token': token.strip() }) if token else jsonify({ 'error': 'Invalid username or password.' }), 200 if token else 401

@app.route('/api/coupons', methods = ['POST'])
def coupons():
    error = None
    message = None
    noData = False

    if not g.error:
        payload = g.payload
        username = payload['username']

        password = data[username]['password'] if username in data else None

        # Collect coupons.
        error = onCollect(username, password)
        noData = True if error and 'No data' in error else False
    else:
        error = 'Invalid token.'
        message = str(g.exception)

    return apiResult('Running', error, message, noData)

@app.route('/api/status')
def status():
    result = None
    error = None
    message = None
    noData = False

    if not g.error:
        try:
            payload = g.payload
            username = payload['username']

            # Get the data to return, make a copy so we can remove sensitive info (pass) before sending to client.
            result = copy(data[username]) if username in data else None
            if result:
                del result['password']

            error = None if result else 'No data for ' + username
            noData = True if error else False
        except Exception as e:
            error = 'Invalid token.'
            message = str(e)
    else:
        error = g.error
        message = str(g.exception)

    return apiResult(result, error, message, noData)

@app.route('/api/status', methods = ['DELETE'])
def delete():
    error = None
    message = None
    noData = False

    if not g.error:
        payload = g.payload
        username = payload['username']

        error = None if username in data and data.pop(username) else 'No data for ' + username
        noData = True if error else False
    else:
        error = g.error
        message = str(g.exception) if 'exception' in g else None

    return apiResult('Deleted', error, message, noData)

@app.route('/login')
def loginView():
    return render_template('login.html', version=version)

@app.route('/')
def index():
    return render_template('index.html', version=version) if not g.error else redirect('/login')

def onCollect(username, password):
    error = None

    if username and password:
        if username in data:
            if data[username]['status'] != 'RUNNING':
                # Launch the Selenium coupon collection process asynchronously.
                data[username]['status'] = 'RUNNING'
                thread = Thread(target=grocery_coupons.shoprite, args=(username, password, None, 10, onStatus))
                thread.start()
            else:
                error = 'Already running.'
        else:
            error = 'No data for ' + username
    else:
        error = 'Invalid username or password.'

    return error

def onStatus(status):
    global data

    # Get the key for the user.
    username = status['email']

    # Update status.
    if username in data:
        data[username]['count'] = status['count']
        data[username]['existingCount'] = status['existingCount']
        data[username]['screenshot'] = status['screenshot']
        data[username]['message'] = status['message']
        data[username]['lastUpdate'] = datetime.now()
        if data[username]['message'] in ('Complete!', 'Error'):
            data[username]['status'] = 'IDLE'
            data[username]['endDate'] = datetime.now()
            data[username]['error'] = status['error'] if 'error' in status else None

    print(status['message'])

def apiResult(payload, error, message, noData):
    if type(payload) is str:
        payload = { 'status': payload }

    return jsonify(payload) if not error else jsonify({ 'error': error, 'message': message }), 200 if not error else 404 if noData else 401

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)