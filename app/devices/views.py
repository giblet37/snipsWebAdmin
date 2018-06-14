#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, May 11th 2018, 4:12:58 pm
# Author: Greg
# -----
# Last Modified: Thu Jun 14 2018
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
from . import devices
import assistant
import services
#from app import mqtt,mqttYaml,socketio
from app import mqtt,socketio
from flask_socketio import emit
#from utils import SSHConnect, YamlDB
from utils import SSHConnect
from app.apptoml import tomlDB
import os
import json
import subprocess
import string
import operator
from eventlet import monkey_patch
monkey_patch()

import socket

import logging
logger = logging.getLogger('snipsWebAdmin-Devices')

db = ''

@devices.route('/device')
def devicePage():
    global db
    db = tomlDB(current_app.config['APP_SETTINGS'])
    
    try:

        
        devicelist = db.get_toml_data("DEVICES")

        #if we delete all device items.. then the heading is left but lists no items
        if len(devicelist) == 0:
            socketio.on_event('scanDevices', scan_devices, namespace='/devices') #YES DEVICES..DONT CHANGE
            return render_template('device.html',firstrun="YES")

        devicelist.sort(key=operator.itemgetter('FUNCTION'))
        devs = []
        for i in devicelist:
            if "NAME" in i:
                d = {'text': "{} ({}) - {}".format(i['NAME'], i['HOSTNAME'], i['FUNCTION']), 'value': i['HOSTNAME']}
                devs.append(d)
            else:
                d = {'text': "{} - {}".format(i['HOSTNAME'], i['FUNCTION']), 'value': i['HOSTNAME']}
                devs.append(d)
            
        #devs.sort()
  
        socketio.on_event('loadDeviceData', load_device_data_handler, namespace='/device')
        socketio.on_event('refresh', load_device_syslog_handler, namespace='/device')
        socketio.on_event('installsnipsasrinjection', install_injection_handler, namespace='/device')
        socketio.on_event('runinjection', run_injection_handler, namespace='/device')

        socketio.on_event('updatesnips', updateSnips, namespace='/device')
        socketio.on_event('restartsnipsservices', restartSnipsServices, namespace='/device')

        socketio.on_event('refreshservice', refreshSnipsService, namespace='/device')
        socketio.on_event('startservice', startSnipsService, namespace='/device')
        socketio.on_event('disableservice', disableSnipsService, namespace='/device')
        
        socketio.on_event('reloadServicesTable', reloadServicesTable, namespace='/device')
        
        return render_template('devices.html',devicelist=devs,field="YES")
    except Exception as e:
        print(e)
        if mqtt.connected:
            socketio.on_event('scanDevices', scan_devices, namespace='/devices') #YES DEVICES..DONT CHANGE
            return render_template('device.html',firstrun="YES")
        else:
            return render_template('device.html',firstrun="MQTT")
       
def scan_devices(data):

    '''
    Here we try to connect to the mqtt server by ssh.. using default ssh user:pass
    get a list of all the clients connected via mqtt port - set in teh settings.toml file
    we then connect to each one and find out if they use snips servers and set as main or satellite deice
    '''
    devicesFound = []
    mqttBroker = current_app.config['MQTT_BROKER_URL']
    
    cmd = ';'.join(["{}".format(current_app.config['CMD_HOSTNAME']),
                    "netstat | grep :{} | awk \'{}\' | cut -d \":\" -f1".format(current_app.config['MQTT_BROKER_PORT'],"{print $5}")]) 
                    

    sshconnect = SSHConnect()
    error,output = sshconnect.connect(hoststring=mqttBroker, command=cmd)
    if error:
        logger.error("SSH connect failed to scan for mqtt connected clients: {}".format(error))
    else:
        stdout = list(output)
        for i in stdout:
            if i.rstrip() not in devicesFound:
                devicesFound.append(i.rstrip())
   
    items = []
    logger.info("devies listed: {}".format(devicesFound))
  
    if type(devicesFound) == list:
        #try:
            if 'localhost' in devicesFound:
                devicesFound.remove('localhost')

            logger.info("devies listed: {}".format(devicesFound))

            if len(devicesFound) > 0:
                
                cmd = ';'.join(['hostname',
                                'systemctl show -p LoadState snips-audio-server | sed \'s/LoadState=//g\'', 
                                'systemctl show -p ActiveState snips-asr | sed \'s/ActiveState=//g\'',
                                "uname"]) 
                for de in devicesFound:
                    try:
                        sshconnect = SSHConnect()
                        error,output = sshconnect.connect(hoststring=de, command=cmd)
        
                        if error:
                            logger.error("Error in sshconnect: {}".format(error))
                        else:
                            #only add devices where snips-audio-server is installed
                            stdout = list(output)
                            if stdout[2].startswith("active"):
                                items.append({"HOSTNAME":stdout[0].rstrip(), "OS":stdout[3].rstrip(), "FUNCTION": "Main", "USER":current_app.config['CLIENT_USER'], "PASSWORD":current_app.config['CLIENT_PASSWORD']}) 
                            elif stdout[1].startswith("loaded"):
                                items.append({"HOSTNAME":stdout[0].rstrip(), "OS":stdout[3].rstrip(), "FUNCTION": "Satellite", "USER":current_app.config['CLIENT_USER'], "PASSWORD":current_app.config['CLIENT_PASSWORD']}) 
                    except Exception as e:
                        logger.info('ERROR: {}'.format(e))

                
        #except Exception as e:
        #    logger.info('ERROR: {}'.format(e))
    
    global db        
    db.set_toml_data('DEVICES',items)
    db.save_toml_file()

    socketio.emit('scanComplete', "Scanning complete!", namespace='/devices') #YES DEVICES..DONT CHANGE

def load_device_data_handler(data):

    if isinstance(data['device'], basestring):
        commandsList = {"syslog":"tail -n 100 /var/log/syslog",
                        "toml":"cat {}".format(current_app.config['SNIPS_TOML']),
                        "info": "cat /etc/os-release | grep \"PRETTY_NAME\" | cut -d= -f2; lscpu;",
                        "snippets": "ls -1 {}".format(current_app.config['SNIPS_ASSISTANT_SNIPPETDIR']),
                        "snipsyaml": "cat {}".format(current_app.config['SNIPS_ASSISTANT_SNIPSFILE']),
                        "snipsjson": "cat {}".format(current_app.config['SNIPS_ASSISTANT_ASSISTANTFILE']),
                        "services": "dpkg-query -W -f=\'${binary:Package} ${Version}\n\' \'snips-*\'",
                        "caninject": "dpkg-query -W -f=\'${binary:Package} ${Version}\n\' snips-asr-injection",
                        "slots":"cat {}".format(current_app.config['SNIPS_ASSISTANT_TRAINEDASSISTANTFILE']) }

        returnedData = ''
        try:
            global db 
            devicelist = db.get_toml_data("DEVICES")
        
            dev = filter(lambda x : x['HOSTNAME'] == data['device'], devicelist) 
    
            sshconnect = SSHConnect()
            returnedData =  sshconnect.connectDevice(device=dev[0], commands=commandsList)
        except:
            pass
        


        if type(returnedData) == dict:
            returnedData['function'] = dev[0]['FUNCTION']
       
            if dev[0]['FUNCTION'] == "Main":
                slots = []
                #print(returnedData['slots'][1][0:-4])
                try:
                    data = json.loads(returnedData['slots'][1][0:-4])
                    for item in data["dataset_metadata"]["entities"]:
                        if "snips/" not in item:
                            slots.append(item)
                except:
                    logger.info("no assistant file installed")

                canInject = ""
              
                if len(returnedData['caninject'][0]) > 0:
                    #if "no packages found matching" in returnedData['caninject'][0][0]:
                    canInject = "NO"
                elif "error" in returnedData['caninject'][1]:
                    canInject = returnedData['caninject'][1]
                else:
                    canInject = "YES"

                from flask import get_template_attribute
                macro = get_template_attribute("_devicehelpers.html", 'render_info')
                #logger.info( macro("NO") )
                # macro uses global variable `global_key` 
                html = macro(canInject, slots)

                

               
                table_assistant, table_slots, table_snippets = assistant.get_assistant_table(returnedData['snippets'][1],returnedData['snipsyaml'][1],returnedData['snipsjson'][1])
                try:
                    socketio.emit('hereistheassistanttable', table_assistant.__html__().replace("&amp;lt;br/&amp;gt;","<br>"), namespace='/device')
                except:
                    socketio.emit('hereistheassistanttable', "No Assistant Installed", namespace='/device')

                try:
                    socketio.emit('hereistheskillstable', table_slots.__html__(), namespace='/device')
                except:
                    socketio.emit('hereistheskillstable', "", namespace='/device')

                try:
                    socketio.emit('hereisthesnippetstable', table_snippets.__html__(), namespace='/device')
                except:
                    socketio.emit('hereisthesnippetstable', "", namespace='/device')

               
                try:
                    socketio.emit('hereistheinjection', html, namespace='/device')
                except:
                    socketio.emit('hereistheinjection', "error", namespace='/device')
                
                
            #both Main and Satellite have services
            #  #table_services = services.get_snips_service_table(dev[0],returnedData['services'][1].split("<br>"))
            table_services = services.get_snips_service_table(dev[0],returnedData['services'][1])
            try:
                socketio.emit('hereistheservicestable', table_services.__html__(), namespace='/device')
            except:
                socketio.emit('hereistheservicestable', "error loading services info", namespace='/device')

                
                
                
            del returnedData["snippets"]
            del returnedData["services"]
            del returnedData["snipsyaml"]
            del returnedData["snipsjson"]
            del returnedData["slots"]
            socketio.emit('hereisthedeviceinfo', returnedData, namespace='/device')
        else:
            logger.info(returnedData)
            socketio.emit('hereisthedeviceinfoERROR',"Unable to connect to device", namespace='/device')

def load_device_syslog_handler(data):

    if isinstance(data['device'], basestring):
        commandsList = {'syslog':'tail -n 100 /var/log/syslog'}

        global db 
        devicelist = db.get_toml_data("DEVICES")
        dev = filter(lambda x : x['HOSTNAME'] == data['device'], devicelist) 
  
        sshconnect = SSHConnect()
        returnedData =  sshconnect.connectDevice(device=dev[0], commands=commandsList)

        socketio.emit('log', returnedData['syslog'], namespace='/device')

#backup the toml file without page refresh
@devices.route('/toml', methods=['POST'])
def backup():
    
    if request.method == "POST":
        #data = json.loads( request.data)
        #print (request.data['toml'])
        #print(request.data)
        json_data = request.get_json()
 
        #python_obj = json.loads(json_data)
        tomlcode = json_data["toml"]
        back =  json_data["backup"]
        device = json_data["device"]

   
        global db 
        devicelist = db.get_toml_data("DEVICES")
        dev = filter(lambda x : x['HOSTNAME'] == device, devicelist) 
        dev = dev[0]
        c=[]

        if back:
            #backup the snips.toml file to snips.toml.bak in the /etc/ folder
            #do this first before we write the file
            c.append('sudo -k cp /etc/snips.toml /etc/snips.toml.bak')
    

        #save new toml info
        c.append('sudo -k echo "{}" > "/home/pi/snips.ttt"'.format(tomlcode.rstrip()))
        c.append('sudo -k cp /home/pi/snips.ttt /etc/snips.toml')
        c.append('sudo -k rm /home/pi/snips.ttt')

        #restart snips
        c.append('sudo -k systemctl restart \"snips-*\"')

    
        returnObj = jsonify({'good':'Complete'})

        try:
            sshconnect = SSHConnect()
            stderr =  sshconnect.connectSudo(device=dev, commands=c)
            
            if stderr:
                returnObj = jsonify({'error':'{}'.format(stderr)})
   
        except Exception as e:
            returnObj = jsonify({'error':'{}'.format(e)})                  
    
    return returnObj

def install_injection_handler(data):
     if isinstance(data['device'], basestring):
        socketio.emit('updatingSnipsASRInjectionInstalling', 'Running...<br>apt-get -y update && sudo apt-get -y install snips-asr-injection<br><br>', namespace='/device')
        commandsList = ["sudo -k apt-get -y update", "sudo -k apt-get -y install snips-asr-injection"]

        global db 
        devicelist = db.get_toml_data("DEVICES")
        dev = filter(lambda x : x['HOSTNAME'] == data['device'], devicelist) 
        dev = dev[0]

        try:
            sshconnect = SSHConnect()
            stderr =  sshconnect.connectSudo(device=dev, commands=commandsList, socket=socketio, socketTopic='updatingSnipsASRInjectionInstalling',namespace='/device')
            
            if stderr:
                socketio.emit('updatingSnipsASRInjectionInstalling', '<br>Error installing snips-asr-injection<br>{}'.format(stderr), namespace='/device')   
   
        except Exception as e:
            socketio.emit('updatingSnipsASRInjectionInstalling', '<br>Error installing snips-asr-injection<br>{}'.format(e), namespace='/device')   


        #all done and finished.. show the close button   
        socketio.emit('installingComplete', "Done", namespace='/device')

def run_injection_handler(data):
    condition = data['condition']
    slot = data['slot']
    items = data['items']

    s = '\"{}\" : [ {} ] }} '.format(slot,items[0:-1])
    c = "[ \"{}\",{{".format(condition)

    d = "{\"operations\": ["
    e = " ] ] }"

    f = ''.join([d,c,s,e])

    mqtt.publish('hermes/asr/inject', payload=f)
    socketio.emit('injectionsComplete', "Done", namespace='/device')

def updateSnips(data):
    #return the apt-get update output info
    if isinstance(data['device'], basestring):
        socketio.emit('updatingSnipsLog', 'Running...<br>apt-get -y update && sudo apt-get -y upgrade<br><br>', namespace='/toml')
        
        commandsList = ["sudo -k apt-get -y update","sudo -k apt-get -y upgrade"]

        global db 
        devicelist = db.get_toml_data("DEVICES")
        dev = filter(lambda x : x['HOSTNAME'] == data['device'], devicelist) 
        dev = dev[0]

        try:
            sshconnect = SSHConnect()
            stderr =  sshconnect.connectSudo(device=dev, commands=commandsList, socket=socketio, socketTopic='updatingSnipsLog',namespace='/device')
            
            if stderr:
                socketio.emit('updatingSnipsLog', '<br>Error updating Snips<br>{}'.format(stderr), namespace='/device')   
   
        except Exception as e:
            socketio.emit('updatingSnipsLog', '<br>Error updating Snips<br>{}'.format(e), namespace='/device')   


        #all done and finished.. show the close button   
        socketio.emit('updatingSnipsComplete', "Update Upgrade Complete", namespace='/device')

def restartSnipsServices(data):
    if isinstance(data['device'], basestring):
        commandsList = ['sudo -S systemctl restart \"snips-*\"']

        global db 
        devicelist = db.get_toml_data("DEVICES")
        dev = filter(lambda x : x['HOSTNAME'] == data['device'], devicelist) 
        dev = dev[0]

        try:
            sshconnect = SSHConnect()
            stderr =  sshconnect.connectSudo(device=dev, commands=commandsList)
            
            if stderr:
                socketio.emit('restartServicesComplete', '<br>Error Restarting Snips Services<br>{}'.format(stderr), namespace='/device')
                
        except Exception as e:
            socketio.emit('restartServicesComplete', '<br>Error Restarting Snips Services<br>{}'.format(e), namespace='/device')   


        #all done and finished.. reload table view
        reloadServicesTable(data)
        # show the close button   

        socketio.emit('restartServicesComplete', 'Complete<br><br>', namespace='/device')

def reloadServicesTable(data):
    if isinstance(data['device'], basestring):
        commandsList = {"services": "dpkg-query -W -f=\'${binary:Package} ${Version}\n\' \'snips-*\'" }

        returnedData = ''
        try:
            global db 
            devicelist = db.get_toml_data("DEVICES")
        
            dev = filter(lambda x : x['HOSTNAME'] == data['device'], devicelist) 
    
            sshconnect = SSHConnect()
            returnedData =  sshconnect.connectDevice(device=dev[0], commands=commandsList)
        except:
            pass
        


        if type(returnedData) == dict:
            returnedData['function'] = dev[0]['FUNCTION']
            
            table_services = services.get_snips_service_table(dev[0],returnedData['services'][1])
            try:
                socketio.emit('hereistheservicestable', table_services.__html__(), namespace='/device')
            except:
                socketio.emit('hereistheservicestable', "error loading services info", namespace='/device')

def workservice(device, service, status):
    if isinstance(device, basestring):
        commandsList = [] #['sudo -S systemctl {} {}'.format(status, service)]

        if status == 'restart':
            commandsList = ['sudo -S systemctl restart {}'.format(service)]
        elif status == 'start':
            commandsList = ['sudo -S systemctl enable {}'.format(service),'sudo -S systemctl start {}'.format(service)]
        else:
            commandsList = ['sudo -S systemctl stop {}'.format(service),'sudo -S systemctl disable {}'.format(service)]


        print(commandsList)
        global db 
        devicelist = db.get_toml_data("DEVICES")
        dev = filter(lambda x : x['HOSTNAME'] == device, devicelist) 
        dev = dev[0]

        try:
            sshconnect = SSHConnect()
            stderr =  sshconnect.connectSudo(device=dev, commands=commandsList)
            
            if stderr:
                socketio.emit('restartServicesComplete', '<br>Error Restarting Snips Services<br>{}'.format(stderr), namespace='/device')
                
        except Exception as e:
            pass


        #all done and finished.. reload service table on the page   
        reloadServicesTable({'device': device})

def refreshSnipsService(data):
    workservice(data['device'], data['service'], 'restart')

def startSnipsService(data):
    workservice(data['device'], data['service'], 'start')

def disableSnipsService(data):
    workservice(data['device'], data['service'], 'disable')

