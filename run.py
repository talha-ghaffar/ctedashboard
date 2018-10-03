#!/usr/bin/python
#
import os
import time
from flask import request, render_template, send_from_directory
from flask import Flask, redirect, url_for, session, flash, session, app
from functools import wraps
from eve import Eve
from pymongo import MongoClient
from flask import jsonify
import json

client = MongoClient('localhost', 27017);
db = client.benchmark;


template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
public_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')
app = Eve(template_folder=template_dir, static_folder=public_dir)
app.secret_key = "VPN@dmin2016+!"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #print session['is_logged_in']
        if 'is_logged_in' in session:
        	if session['is_logged_in'] != 'loggedin':
        		return redirect('/login')
        else:
        	session['is_logged_in'] = 'loggedout'
        return f(*args, **kwargs)
    return decorated_function

@app.route('/request-logout', methods=['GET'])
def logout():
	#del session['is_logged_in']
	session['is_logged_in'] = 'loggedout'
	return redirect('/login')

@app.route('/home')
@login_required
def homepage():
    return render_template('main.html')

@app.route('/iteration-details')
@login_required
def iteration_details():
    return render_template('tpl-iteration-details.html')

    

@app.route('/login', methods=['GET', 'POST'])
def loginpage():
	error = False
	if request.method == 'POST':
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
			session['is_logged_in'] = 'loggedin'
			return redirect('/home')
		else:
			error = 'Invalid Credentials'
	else:
		if 'is_logged_in' in session:
			if session['is_logged_in'] == 'loggedin':
				return redirect('/home')
	return render_template('login.html', error=error)


@app.route('/get-iterations', methods=['GET'])
def graph_infrastats():

    data = {}
    result = db.pingapisources.distinct("country")
    url = "/api"
    querystring = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code==200:
        json_data = json.loads(response.text)
        data['status'] = True
        data['production']      = int(json_data['body']['production'])
        data['maintainence']    = int(json_data['body']['maintainence'])
        data['trashed']         = int(json_data['body']['trashed'])
    else:
        data['status'] = False
    return json.dumps(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)