#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, April 27th 2018, 8:35:06 pm
# Author: Greg
# -----
# Last Modified: Mon Jun 04 2018
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




from flask import render_template, current_app, jsonify,request
from flask_table import Table, Col, html 
from . import main
#from app import mqtt,mqttYaml,socketio
from app import mqtt, socketio
#from flask_socketio import emit
#import utils
import os
import json
#from shutil import copyfile
import subprocess
import string
import toml
from collections import OrderedDict
import operator
from app.apptoml import tomlDB
from app.devices.utils import SSHConnect


class Item(object):
    def __init__(self, name, description=None):
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

class DeviceItem(object):
    def __init__(self, hostname, deviceos, devicefunction):
        self.hostname = hostname
        self.deviceos = deviceos
        self.devicefunction = devicefunction
        self.delete = ""

class DeviceItemTable(Table):
    no_items = 'No devices to list'
    classes = ['table']
    hostname = Col(
        'Device',
        column_html_attrs={'class': 'my-name-class'},
        th_html_attrs={'class': 'table-active'},
    )
    deviceos = Col(
        'OS',
        column_html_attrs={
            'data-something': 'my-data',
            'class': 'my-description-class'},
        # Apply this to just the th
        th_html_attrs={'class': 'table-active'},
        # Apply this to just the td - note that this will things from
        # overwrite column_html_attrs.
        td_html_attrs={'data-something': 'my-td-only-data'},
    )
    devicefunction = Col(
        'Role',
        column_html_attrs={
            'data-something': 'my-data',
            'class': 'my-description-class'},
        # Apply this to just the th
        th_html_attrs={'class': 'table-active'},
        # Apply this to just the td - note that this will things from
        # overwrite column_html_attrs.
        td_html_attrs={'data-something': 'my-td-only-data'},
    )
    delete = Col(
        '',
        th_html_attrs={'class': 'table-active'},
        td_html_attrs={'class': 'deletebox'},)
  

def git_version():
    c = "git rev-list --pretty=format:'<b>Last Updated:</b> '%ad --max-count=1 --date=relative `git rev-parse HEAD`"
    p = subprocess.Popen([c], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = p.communicate()
    if p.returncode == 0:
        return output.replace("commit ","<b>Version:</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;").replace("\n","<br>")
    else:
        return 'unknown error getting version info'

@main.route('/info')
def index():

    connected = 'NO'
    if mqtt.connected:
        connected = 'YES'

    socketio.on_event('deleteHost', deleteHost, namespace='/info')
    socketio.on_event('justaddHost', justaddHost, namespace='/info')
    socketio.on_event('installsnips', installsnips, namespace='/info')

    return render_template('info.html', table=get_mqtt_table(),devicestable=get_device_table(), connected=connected,  version=git_version())

def get_mqtt_table():
    items = []
    #mqttsettings = mqttYaml.get_yaml_data("MQTT")
    mqttsettings = toml.load(current_app.config['APP_SETTINGS'], _dict=OrderedDict)
    for key, value in mqttsettings['MQTT'].iteritems():
        items.append(Item(key, value))

    #for key, value in mqttsettings.iteritems():
    #    if key.isupper():
    #        if not value == '':
    #            items.append(Item(key, value))
    table = ItemTable(items)
    return table

def get_device_table():
    items = []
   
    try:
        devicesettings = toml.load(current_app.config['APP_SETTINGS'])
        devicesettings = devicesettings['DEVICES']
        #newlist = sorted(devicesettings, key=itemgetter('FUNCTION')) #, reverse=True)
        devicesettings.sort(key=operator.itemgetter('FUNCTION'))
        for item in devicesettings:
            if "NAME" in item:
                items.append(DeviceItem("{} ({})".format(item['HOSTNAME'], item['NAME']), item['OS'], item['FUNCTION']))
            else:
                items.append(DeviceItem(item['HOSTNAME'], item['OS'], item['FUNCTION']))
    except:
        pass
    
    table = DeviceItemTable(items)
    return table

def deleteHost(data):

    if " " in data['hostname']:
        data = data['hostname'].split(" ")[0]
    else:
        data = data['hostname']

    db = tomlDB(current_app.config['APP_SETTINGS'])
    db.delete_by_hostname(data)
    pass

def addDeviceInfoToDB(data):
    db = tomlDB(current_app.config['APP_SETTINGS'])
    items = db.get_toml_data("DEVICES")
    if "SNIPSNAME" in data:
        del data["SNIPSNAME"]
    items.append(data)
    db.set_toml_data("DEVICES",items)
    db.save_toml_file()

def justaddHost(data):
    data = data['data']
    addDeviceInfoToDB(data)
    socketio.emit('addComplete', "add complete!", namespace='/info')

def installsnips(data):
    data = data['data']

    ostype = data["OS"]
    if ".local" in data["HOSTNAME"]:
        data["HOSTNAME"] = data["HOSTNAME"].split(".local")[0]
    user = data["USER"]
    password = data["PASSWORD"]
    installType = data["FUNCTION"]

    print(data)

    #connectSudo(self, device, commands=[], socket=None, socketTopic="", namespace=None):
    cmds = [] #install commands

    cmds.append("sudo apt-get update")
    cmds.append("sudo apt-get install -y dirmngr")
    cmds.append("sudo bash -c  'echo \"deb https://raspbian.snips.ai/$(lsb_release -cs) stable main\" > /etc/apt/sources.list.d/snips.list'")
    cmds.append("sudo apt-key adv --keyserver pgp.mit.edu --recv-keys D4F50CDCA10A2849")
    cmds.append("sudo apt-key adv --keyserver pgp.surfnet.nl --recv-keys D4F50CDCA10A2849")
    cmds.append("sudo apt-get update")
    cmds.append("sudo apt-get install -y snips-platform-voice")

    if installType == "Main":
        #full setup install
        cmds.append("sudo apt-get install -y snips-platform-voice")

    else:
        #just snips-audio-server
        cmds.append("sudo apt-get install -y snips-audio-server")

    #change hostname
    cmds.append("sudo raspi-config nonint do_hostname {}".format(data['SNIPSNAME']))
    cmds.append("sudo reboot")
    
    try:
        sshconnect = SSHConnect()
        stderr =  sshconnect.connectSudo(device=data,commands=cmds,socket=socketio,socketTopic="log",namespace="/info")
        
        if stderr:
            socketio.emit('installError', '<br>Error installing Snips<br>{}'.format(stderr), namespace='/info')   
        else:
            #all good
            data["HOSTNAME"] = data['SNIPSNAME'] #cause it changed
            addDeviceInfoToDB(data)
            socketio.emit('installComplete', "install complete!", namespace='/info')

    except Exception as e:
        socketio.emit('installError', '<br>Error installing Snips<br>{}'.format(e), namespace='/info')   





'''
    dict['FUNCTION'] = setuptype;
    dict['HOSTNAME'] = $("#inputHostname").val();
    dict['OS'] = $("input:radio[name=grpRadios1]:checked").val();
    dict['USER'] = $("#inputUsername").val();
    dict['PASSWORD'] = $("#inputPassword").val();
    dict['SNIPSNAME'] = $("#inputSnipsName").val();

'''