#!/usr/bin/python
# Developer Saad Arshad <gaditek.saad@gmail.com>
# November 2018
# Python Eve

import os
import time
from flask import request, render_template, send_from_directory
from flask import Flask, redirect, url_for, session, flash, session, app
from functools import wraps
from eve import Eve
from pymongo import MongoClient
from flask import jsonify
import json
import datetime
import dateutil.parser
from bson.objectid import ObjectId

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

@app.route('/configuration')
@login_required
def configuration():
    return render_template('configuration.html')

@app.route('/help')
@login_required
def show_help():
    return render_template('tpl-help.html')

@app.route('/iteration-details')
@login_required
def iteration_details():
    return render_template('tpl-iteration-details.html')

@app.route('/customize-query')
@login_required
def customize_query():
    return render_template('customizequery1.html')

@app.route('/test-ratio-compare1')
@login_required
def customize_qu():
    return render_template('ratiocompare1.html')


@app.route('/test-iteration-details')
@login_required
def test_iteration_details():
    return render_template('testing_iteration-details.html')

@app.route('/test-ratio-compare')
@login_required
def test_ratio_compare():
    return render_template('ratiocompare.html')


@app.route('/country-list')
def country_list():
    import requests
    url = "http://tester.pointtoserver.com:5000/sre-country-list"
    headers = {
    'cache-control': "no-cache"
    }
    response = requests.request("GET", url, headers=headers)
    return json.loads(json.dumps(response.text))

@app.route('/list-iterations')
@app.route('/list-iterations/<iteration_id>')
@login_required
def list_iterations(iteration_id=False):
    data = {}
    error = []
    iterations = []
    if iteration_id:
        data['show_details'] = iteration_id
        host_machines = app.data.driver.db['host_machines']
        host_machine = host_machines.find_one({"_id":ObjectId(iteration_id)})

        data['host_machine'] = host_machine
        if host_machine is None:
            error.append('ID Not Found in Database')
        else:
            machine_iteration_obj   =   app.data.driver.db['machine_iterations']
            machine_iterations      =   machine_iteration_obj.find({"host_id":ObjectId(iteration_id)})


            for all_iterations in machine_iterations:
                iterations.append(all_iterations)

            data['iterations_list'] = iterations
    else:
        data_hosts = []
        host_machines = app.data.driver.db['host_machines']
        host_machine = host_machines.find()

        for hosts in host_machine:
            data_hosts.append(hosts)


        data['hosts'] = data_hosts
    return render_template('tpl-list-iterations.html', result=data)


@app.route('/update-record')
@login_required
def update_record():
    return render_template('tpl-update-iterations.html')


@app.route('/get-job-details/<jid>', methods=['GET', 'PUT'])
@login_required
def get_job_details(jid):
    if request.method == 'GET':
        datalist = db.machine_iterations.find({"_id":ObjectId(jid)})
        final ={}
        string = []
        for line in datalist:
            val = {}
            val['download_file_2'] = line['download_file_2']
            val['download_file_1'] = line['download_file_1']
            val['vpn_portocol'] = line['vpn_portocol']
            val['dest_address'] = line['dest_address']
	    val['dest_country'] = line['dest_country']
            val['vpn_provider'] = line['vpn_provider']
            val['vpn_port'] = line['vpn_port']
	    #if line['iperf_server']:
            	#val['iperf_server'] = line['iperf_server']
            #if line['iperf_sessions']: 
		#val['iperf_sessions'] = line['iperf_sessions']
            val['config'] = line['config']            
            string.append(val)
        final['jobdetails'] = string
        #print final
        return jsonify(final)
    elif request.method == 'PUT':
        content = []
        content=request.get_json()        
        res = db.machine_iterations.find_one_and_update(
            { '_id': ObjectId(jid)},
            { '$set': { 'download_file_1':content['download_file_1'], 'download_file_2':content['download_file_2'], 'vpn_portocol':content['vpn_portocol'], 'dest_address':content['dest_address'], 'vpn_port':content['vpn_port'], 'vpn_provider':content['vpn_provider'], 'config':content['config'], 'dest_country':content['dest_country'], 'iperf_server':content['iperf_server'], 'iperf_sessions':content['iperf_sessions'] } },
            upsert=True,
        )
        return json.dumps(True)



@app.route('/delete-job/<iid>')
@login_required
def delete_job(iid):
    machine_iterations = app.data.driver.db['machine_iterations']
    machine_iteration = machine_iterations.find_one({"_id":ObjectId(iid)})
    if machine_iteration is not None:
        delete_machine = machine_iterations.remove({"_id":ObjectId(iid)})
        # if delete_machine is not None:
        #     machine_iteration_obj   =   app.data.driver.db['machine_iterations']
        #     delete_iterations       =   machine_iteration_obj.remove({"host_id":ObjectId(iid)})
    flash('Record Successfully Deleted')        
    return redirect(url_for('list_iterations'))



@app.route('/delete-iterations/<iid>')
@login_required
def delete_iteration(iid):
    host_machines = app.data.driver.db['host_machines']
    host_machine = host_machines.find_one({"_id":ObjectId(iid)})
    if host_machine is not None:
        delete_machine = host_machines.remove({"_id":ObjectId(iid)})
        if delete_machine is not None:
            machine_iteration_obj   =   app.data.driver.db['machine_iterations']
            delete_iterations       =   machine_iteration_obj.remove({"host_id":ObjectId(iid)})

    return redirect(url_for('list_iterations'))

@app.route('/view-config/<iid>')
@login_required
def view_config(iid):
    data = {}
    machine_iteration_obj   =   app.data.driver.db['machine_iterations']
    config_file       =   machine_iteration_obj.find_one({"_id":ObjectId(iid)})
    data['config'] = config_file
    return render_template('tpl-view-config.html', result=data)

@app.route('/add-iteration', methods=['GET', 'POST'])
@login_required
def add_iteration():
    if request.method == 'POST':
        host_address        = request.form['host_ip_address']
        machine_notes         = request.form['machine_notes']
        vpn_provider        = request.form.getlist('vpn_provider[]')
        vpn_portocol        = request.form.getlist('vpn_protocol[]')
        dest_address       = request.form.getlist('dest_address[]')
        dest_country       = request.form.getlist('dest_country[]')
        vpn_port       = request.form.getlist('vpn_port[]')
        download_file_1       = request.form.getlist('download_file_1[]')
        download_file_2       = request.form.getlist('download_file_2[]')
	iperf_server	= request.form.getlist('iperf_server[]')
	iperf_sessions	= request.form.getlist('iperf_sessions[]')
        config       = request.form.getlist('config[]')
        
        host_machines = app.data.driver.db['host_machines']
        host_machine = host_machines.insert({
            "host_address":host_address,
            "machine_notes":machine_notes,
        });


        machine_iterations = app.data.driver.db['machine_iterations']
        for x in range(len(dest_address)):
            machine_iteration = machine_iterations.insert({
                "host_id":host_machine,
                "vpn_provider":vpn_provider[x],
                "vpn_portocol":vpn_portocol[x],
                "dest_address":dest_address[x],
                "dest_country":dest_country[x],
                "vpn_port":vpn_port[x],
                "download_file_1":download_file_1[x],
                "download_file_2":download_file_2[x],
		"iperf_server":iperf_server[x],
		"iperf_sessions":iperf_sessions[x],
                "config":config[x]
            });
        return redirect(url_for('list_iterations'))
    else:
        return render_template('tpl-add-iteration.html')


@app.route('/testing-endpoint', methods=['POST', 'GET'])
def testing_endpoint():
    content = []
    api2 = app.data.driver.db['api2']
    #ratioCom = app.data.driver.db['ratiocompare']

    content = request.json

    for k, v in content.items():
        if k == '_selectedCountry':
            srcCountry = v
        elif k == '_selectedCity':
            dstCountry = v
        elif k == '_stdate':
            startDate = v
            startDate = dateutil.parser.parse(startDate)

        elif k == '_endate':
            endDate = v
            endDate = dateutil.parser.parse(endDate)

    #try:
    api2 = app.data.driver.db['api2']
    #ratioCom = app.data.driver.db['ratiocompare']
    myquery = {"_updated": {"$gte": startDate, "$lte": endDate}}
    api  = api2.find(myquery)
    #print api
    final = {}
    string = []
    i = 0
    val = {}
    for line in api:
        val[i] = line

        for key in line:

          try:
            if line['SELF_IP'] == srcCountry:
                val1 = {}
                val1['SELF_IP'] = line['SELF_IP']

                if 'results_' in key:
#                        if line[key]['SOURCE_LOCATION'] == srcCountry and line[key]['DESTINATION_COUNTRY'] == dstCountry:
                    if line[key]['DESTINATION_COUNTRY'] == dstCountry:
                        val1['datetime'] = line['datetime']
                        val1['VENDER'] = line[key]['VENDER']
                        val1['SOURCE_LOCATION'] = line[key]['SOURCE_LOCATION']
                        val1['DESTINATION_COUNTRY'] = line[key]['DESTINATION_COUNTRY']
                        val1['BASE_DOWNLOAD_SPEED_STATIC_MB'] = line[key]['BASE_DOWNLOAD_SPEED_STATIC_MB']
                        val1['BASE_DOWNLOAD_SPEED_CDN_MB'] = line[key]['BASE_DOWNLOAD_SPEED_CDN_MB']
                        val1['DIALINGDNS'] = line[key]['DIALINGDNS']
                        val1['PING_LATENCY'] = line[key]['PING_LATENCY']
                        val1['SPEED_STATIC_MB'] = line[key]['SPEED_STATIC_MB']
                        val1['ratio_cdn_one'] = line[key]['ratio_cdn_one']
                        val1['SPEED_CACHE_MB'] = line[key]['SPEED_CACHE_MB']
                        val1['ratio_cdn_two'] = line[key]['ratio_cdn_two']
                        string.append(val1)
                         
                        # print type(string)
                        if type(string) == list: 
                            final['res'] = string
          except:
                pass

        i = i+1
    return jsonify(final)
    return json.dumps(True)


@app.route('/testing-endpoint1', methods=['POST', 'GET'])
def testing_endpoint1():
    content = []
    api2 = app.data.driver.db['ratiocompare']

    content = request.json
    #print content

    for k, v in content.items():
        if k == '_selectedCountry':
            srcCountry = v
        #elif k == '_selectedCity':
        #    dstCountry = v
        elif k == '_stdate':
            startDate = v
            startDate = dateutil.parser.parse(startDate)
            #print startDate

        elif k == '_endate':
            endDate = v
            endDate = dateutil.parser.parse(endDate)
            #print endDate

    #try:
    #api2 = app.data.driver.db['ratiocompare']
    #myquery = {"_updated": {"$gte": startDate, "$lte": endDate}}
    #api  = api2.find(myquery)
    ratcom = app.data.driver.db['ratiocompare']
    myquery = {"_updated":{"$gte": startDate, "$lte": endDate} }
    ratco = ratcom.find(myquery).sort('ratio_cdn_one', -1)
    #print ratco
    #print type(api)
    final = {}
    string = []
    i = 0
    val = {}
    for line in ratco:
        val[i] = line
        #if line['SOURCE_LOCATION'] == srcCountry:
           
        val1 = {}
        val1['_updated'] = line['_updated']
        val1['VENDOR'] = line['VENDOR']
        val1['SOURCE_LOCATION'] = line['SOURCE_LOCATION']
        val1['DESTINATION_COUNTRY'] = line['DESTINATION_COUNTRY']
        val1['BASE_DOWNLOAD_SPEED_STATIC_MB'] = line['BASE_DOWNLOAD_SPEED_STATIC_MB']
        val1['BASE_DOWNLOAD_SPEED_CDN_MB'] = line['BASE_DOWNLOAD_SPEED_CDN_MB']
        val1['DNS'] = line['DNS']
        val1['PING_LATENCY'] = line['PING_LATENCY']
        val1['Pure_Speed'] = line['Pure_Speed']
        val1['SPEED_STATIC_MB'] = line['SPEED_STATIC_MB']
        val1['ratio_cdn_one'] = line['ratio_cdn_one']
        val1['SPEED_CACHE_MB'] = line['SPEED_CACHE_MB']
        val1['ratio_cdn_two'] = line['ratio_cdn_two']
        string.append(val1)

        final['res'] = string

        i = i+1
    return jsonify(final)
    return json.dumps(True)


@app.route('/config/<ip>', methods=['GET'])
#@login_required
def get_config(ip):
    json = {}
    json['settings'] = {}
    json['settings']['jobs'] = {}

    host_machines = app.data.driver.db['host_machines']
    host_machine = host_machines.find_one({"host_address":ip})
    if host_machine is not None:
        json['status'] = True
        json['settings']['jobs'][host_machine['host_address']] = {}

        json['settings']['jobs'][host_machine['host_address']]['notes'] = host_machine['machine_notes']
        json['settings']['jobs'][host_machine['host_address']]['comparisions'] = []

        machine_iteration_obj   =   app.data.driver.db['machine_iterations']
        machine_iterations      =   machine_iteration_obj.find({"host_id":ObjectId(host_machine['_id'])})
        if machine_iterations is not None:
            for lines in machine_iterations:
                temp = {}
                temp['vendor'] = lines['vpn_provider']
		print temp['vendor']
                temp['dest_address'] = lines['dest_address']
		print temp['dest_address']
                temp['dest_country'] = lines['dest_country']
		print temp['dest_country']
                temp['proto'] = lines['vpn_portocol']
                temp['port'] = lines['vpn_port']
                temp['download_cdn'] = lines['download_file_1']
                temp['download_static'] = lines['download_file_2']
		temp['iperf_server'] = lines['iperf_server']
		temp['iperf_sessions'] = lines['iperf_sessions']
                temp['config'] = lines['config']
                json['settings']['jobs'][host_machine['host_address']]['comparisions'].append(temp)
    else:
        json['status'] = False
        json['error'] = 'Host not found',ip
    return jsonify(json)
    

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


# @app.route('/get-iterations', methods=['GET'])
# def graph_infrastats():
#     data = {}
#     result = db.pingapisources.distinct("country")
#     url = "/api"
#     querystring = {}
#     headers = {}
#     response = requests.request("GET", url, headers=headers, params=querystring)
#     if response.status_code==200:
#         json_data = json.loads(response.text)
#         data['status'] = True
#         data['production']      = int(json_data['body']['production'])
#         data['maintainence']    = int(json_data['body']['maintainence'])
#         data['trashed']         = int(json_data['body']['trashed'])
#     else:
#         data['status'] = False
#     return json.dumps(data)



@app.route('/ip-whitelist-panel')
@login_required
def ip_whitelist_panel():
    return render_template('tpl-ip-whitelist.html')


@app.route('/ip-whitelist', methods=['GET', 'POST'])
def ip_whitelist():
    import subprocess
    if request.method == 'POST':
        content = []
        content=request.get_json()
        host_ip_address = content['_ipaddress']
        if (content['_ipremove'] == '1'):
            p = subprocess.Popen(["iptables", "-D", "INPUT", "-s", host_ip_address ,"-p", "tcp", "-m", "tcp", "--dport", "5000" , "-j", "ACCEPT"], stdout=subprocess.PIPE)
        else:
            p = subprocess.Popen(["iptables", "-A", "INPUT", "-s", host_ip_address ,"-p", "tcp", "-m", "tcp", "--dport", "5000" , "-j", "ACCEPT"], stdout=subprocess.PIPE)
        p.communicate()
        return json.dumps(True)
    else:
        return render_template('tpl-ip-whitelist.html')


@app.route('/add-vendor', methods=['GET', 'POST'])
def add_vendor():
    if request.method == 'POST':
        host_id = request.args.get("id")
        host_address        = request.form['host_ip_address']
        vpn_provider        = request.form.getlist('vpn_provider[]')
        vpn_portocol        = request.form.getlist('vpn_protocol[]')
        dest_address       = request.form.getlist('dest_address[]')
        dest_country       = request.form.getlist('dest_country[]')
        vpn_port       = request.form.getlist('vpn_port[]')
        download_file_1       = request.form.getlist('download_file_1[]')
        download_file_2       = request.form.getlist('download_file_2[]')
	iperf_server 	= request.form.getlist('iperf_server[]')
	iperf_sessions = request.form.getlist('iperf_sessions[]')
        config       = request.form.getlist('config[]')

        res = db.host_machines.find_one_and_update(
            { '_id': ObjectId(host_id)},
            { '$set': { 'host_address':host_address } },
            upsert=True,
        )
        
        machine_iterations = app.data.driver.db['machine_iterations']
        
        for x in range(len(dest_address)):
            machine_iteration = machine_iterations.insert({
                "host_id":ObjectId(host_id),
                "vpn_provider":vpn_provider[x],
                "vpn_portocol":vpn_portocol[x],
                "dest_address":dest_address[x],
                "vpn_port":vpn_port[x],
                "download_file_1":download_file_1[x],
                "download_file_2":download_file_2[x],
		"iperf_server":iperf_server[x],
		"iperf_sessions":iperf_sessions[x],
                "config":config[x]
            });
        return redirect(url_for('list_iterations'))
    else:
        return render_template('tpl-add-vendor.html')




@app.route('/ip-edit', methods=['GET', 'POST'])
def ip_edit():
    if request.method == 'POST':
        host_id = request.form['name']
        host_address = request.form['value']
        res = db.host_machines.find_one_and_update(
            { '_id': ObjectId(host_id)},
            { '$set': { 'host_address':host_address } },
            upsert=True,
        )
        return json.dumps(True)
    else:
        return render_template('tpl-ip-whitelist.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
