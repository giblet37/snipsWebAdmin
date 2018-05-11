#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, April 27th 2018, 8:35:06 pm
# Author: Greg
# -----
# Last Modified: Fri May 11 2018
# Modified By: Greg
# -----
# Copyright (c) 2018 Greg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
### **************************************************************************** ###




from flask import render_template, redirect, url_for, current_app, jsonify,request,Response
from flask_table import Table, Col, html 
from . import main
from app import mqtt,mqttYaml,socketio
from flask_socketio import emit
import utils
import os
import json
from shutil import copyfile
import subprocess
import string


class ActiveInactiveCol(Col):

    def td(self, item, attr):
        content = self.td_contents(item, self.get_attr_list(attr))
        if item.isActive == 'Active':
            return html.element(
                'td',
                content=content,
                escape_content=False,
                attrs={'class': 'serviceActive'})
        else:
            if item.isActive == 'Inactive':
                return html.element(
                    'td',
                    content=content,
                    escape_content=False,
                    attrs={'class': 'serviceInactive'})
            else:
                return html.element(
                    'td',
                    content=content,
                    escape_content=False,
                    attrs={'class': 'serviceNone'})
            

    

class serviceItem(object):
    def __init__(self, name, version, isActive):
        self.name = name
        self.version = version
        self.isActive = isActive


class serviceItemTable(Table):
    no_items = 'No Snips services installed'
    classes = ['table']
    name = Col('Snips Service',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )
    version = Col('Version',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )
    isActive = ActiveInactiveCol('Status',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )


class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

class ItemTable(Table):
    no_items = 'Nothing to show'
    classes = ['table']
    name = Col(
        'Config Setting',
        # Apply this class to both the th and all tds in this column
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )
    description = Col(
        'Value', 
        # Apply these to both
        column_html_attrs={
            'data-something': 'my-data',
            'class': 'my-description-class'},
        # Apply this to just the th
        th_html_attrs={'class': 'table-active'},
        # Apply this to just the td - note that this will things from
        # overwrite column_html_attrs.
        td_html_attrs={'data-something': 'my-td-only-data'},
        
    )

def refreshSysLog(data):
    #send the newest tail of /var/log/syslog to the page to show
    socketio.emit('log', loadsyslog(), namespace='/toml')


def updateSnips(data):
    #return the apt-get update output info
    command = 'echo "{}\n" | sudo -S apt-get -y update && sudo apt-get -y upgrade'.format(current_app.config['SUDO_PASSWORD'])

    socketio.emit('updatingSnipsLog', 'Running...<br>apt-get -y update && sudo apt-get -y upgrade<br><br>', namespace='/toml')
    
    #, universal_newlines=True
    p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    while True:
        line = p.stdout.readline()
        if line != '':
            text = line.rstrip() + "<br>"
            socketio.emit('updatingSnipsLog', text, namespace='/toml')
        else:
            break

    output, error = p.communicate()  
    if p.returncode != 0:
        socketio.emit('updatingSnipsLog', '<br>Error updating Snips<br>{}'.format(error), namespace='/toml')
    else:
        socketio.emit('updatingSnipsLog', output + "<br>" + error.replace("\n","<br>"), namespace='/toml')
       
    #all done and finished.. show the close button   
    socketio.emit('updatingSnipsComplete', command, namespace='/toml')

def restartSnipsServices(data):
    command = 'echo "{}\n" | sudo -S systemctl restart \"snips-*\"'.format(current_app.config['SUDO_PASSWORD'])

    p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    output, error = p.communicate()  
    if p.returncode != 0:
        socketio.emit('restartServicesComplete', '<br>Error Restarting Snips Services<br>{}'.format(error), namespace='/toml')
    else:
        socketio.emit('restartServicesComplete', 'Complete<br><br>Refresh page to view any changes', namespace='/toml')


@main.route('/')
def index():

    socketio.on_event('refresh', refreshSysLog, namespace='/toml')
    socketio.on_event('updatesnips', updateSnips, namespace='/toml')
    socketio.on_event('restartsnipsservices', restartSnipsServices, namespace='/toml')

    connected = 'NO'
    if mqtt.connected:
        connected = 'YES'

    #load the snips.toml config file
    fileText = 'Snips TOML file not found at {}'.format(current_app.config['SNIPS_TOML'])
    if os.path.isfile(current_app.config['SNIPS_TOML']):
        file = open(current_app.config['SNIPS_TOML'] , "r")
        fileText = file.read() 



    #tail of teh /var/log/syslog to display
    syslogfile = loadsyslog()

    table_assistant, table_slots = get_assistant_table()
    servicesTable = get_snips_service_status()

    return render_template('index.html', table=get_mqtt_table(), connected=connected, fileText=fileText, servicesTable=servicesTable, table_assistant=table_assistant, table_slots=table_slots, syslogfile=syslogfile)

def get_mqtt_table():
    items = []
    mqttsettings = mqttYaml.get_yaml_data("MQTT")
    for key, value in mqttsettings.iteritems():
        if key.isupper():
            if not value == '':
                items.append(Item(key, value))
    table = ItemTable(items)
    return table

def get_assistant_table():
    #slots
    #base info from file
    assitantdict = utils.get_assistant_info_(current_app.config['SNIPS_ASSISTANT_SNIPSFILE'])
    #print(assitantdict)
    assistant_items = []
    assistant_slots = []
    for key, value in assitantdict.items():
        if key == "slots":
            assistant_slots.append(value)
        elif value != '':
            assistant_items.append(Item(key, value))


    table_assistant = ItemTable(assistant_items)
    table_slots = ItemTable([])
    table_slots.no_items = "No Skills have been included in the assistant file"
    return table_assistant, table_slots

def get_snips_service_status():
    read = subprocess_read('dpkg-query -W -f=\'${binary:Package} ${Version}\n\' snips-*')
    read = read.split('<br>')
    listItems =[]
    for item in read:
        service = item.split(' ')
        version = ''
        if len(service) > 1:
            version = service[1]
       
        is_Service = subprocess_read('systemctl show -p LoadState {} | sed \'s/LoadState=//g\''.format(service[0]))
       
        if is_Service == "loaded<br>":
            is_active = subprocess_read('systemctl show -p ActiveState {} | sed \'s/ActiveState=//g\''.format(service[0]))
            listItems.append(serviceItem(service[0], version ,is_active.replace("<br>","").capitalize()))
        else:
            listItems.append(serviceItem(service[0], version ,''))
        

    return serviceItemTable(listItems)
    

#backup the toml file without page refresh
@main.route('/toml', methods=['POST'])
def backup():
    
    if request.method == "POST":
        #data = json.loads( request.data)
        #print (request.data['toml'])
        #print(request.data)
        json_data = request.get_json()
        #python_obj = json.loads(json_data)
        toml = json_data["toml"]
        back =  json_data["backup"]
    
        if back:
            #backup the snips.toml file to snips.toml.bak in the /etc/ folder
            #do this first before we write the file
            #copyfile(current_app.config['SNIPS_TOML'], current_app.config['SNIPS_TOML_BACKUP'])
            c = 'echo "{}\n" | sudo -S cp /etc/snips.toml /etc/snips.toml.bak'.format(current_app.config['SUDO_PASSWORD'])
            p = subprocess.Popen([c], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, error = p.communicate()  

        #write the toml to the file
        #tomlfile = open(current_app.config['SNIPS_TOML'], "w")

        tomlfile = open('/home/pi/dgdifninidvndoivndfivndf.toml', "w")
        tomlfile.write(toml) 
        tomlfile.close()

        c = 'echo "{}\n" | sudo -S cp /home/pi/dgdifninidvndoivndfivndf.toml /etc/snips.toml'.format(current_app.config['SUDO_PASSWORD'])
        p = subprocess.Popen([c], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, error = p.communicate()

        #os.remove('/home/pi/dgdifninidvndoivndfivndf.toml')
    
        #restart snips services
        command = 'echo "{}\n" | sudo -S systemctl restart \"snips-*\"'.format(current_app.config['SUDO_PASSWORD'])
        p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, error = p.communicate()  
        if p.returncode != 0:
            return jsonify({'error':'Error restarting Snips services<br>{}'.format(error)}) 
        #else:
        #    return jsonify({'good':'Error restarting Snips services<br>{}'.format(error)})                     
    
  
    return jsonify({'good':output})

@main.route('/syslog', methods=['POST'])
def getsyslog():
    return loadsyslog()


def loadsyslog():
    return subprocess_read('tail -n 100 /var/log/syslog')

def subprocess_read(command):
    text = ''
    p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        line = p.stdout.readline()
        if line != '':
            text += line.rstrip() + "<br>"
        else:
            break
    
    output, error = p.communicate()
    if p.returncode != 0:
        return 'error: Error with Syslog {}'.format(error)

    return text


