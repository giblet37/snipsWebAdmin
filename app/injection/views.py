#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, May 11th 2018, 4:12:58 pm
# Author: Greg
# -----
# Last Modified: Fri May 25 2018
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
from . import injection
from app import socketio,mqtt
from flask_socketio import emit
import utils
import os
import json
import subprocess
import string


@injection.route('/injection')
def injectionPage():

    socketio.on_event('installsnipsasrinjection', install_injection_handler, namespace='/injection')
    socketio.on_event('runinjection', run_injection_handler, namespace='/injection')

    canInject = has_injection_app()
    slots = []

    if canInject == "YES":
        #get a list of slot items to use
        try:
            with open(current_app.config['SNIPS_ASSISTANT_TRAINEDASSISTANTFILE']) as f:
                data = json.load(f)
                for item in data["dataset_metadata"]["entities"]:
                    slots.append(item)
        except:
           canInject = "File not found - {}".format(current_app.config['SNIPS_ASSISTANT_TRAINEDASSISTANTFILE'])

    return render_template('injection.html', canInject=canInject, slots=slots)

def has_injection_app():
    #is the snips-asr-injection service install??
    read = subprocess_read('dpkg-query -W -f=\'${binary:Package} ${Version}\n\' snips-asr-injection')
    
    if "no packages found matching" in read:
        return "NO"
    elif "error" in read:
        return read
    else:
        return "YES"

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
        return 'Error: {}'.format(error)

    return text

   
def install_injection_handler(data):
    command = 'echo "{}\n" | sudo -S apt-get -y update && sudo apt-get -y install snips-asr-injection'.format(current_app.config['SUDO_PASSWORD'])

    socketio.emit('updatingSnipsASRInjectionInstalling', 'Running...<br>apt-get -y update && sudo apt-get -y install snips-asr-injection<br><br>', namespace='/injection')
    
    #, universal_newlines=True
    p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    while True:
        line = p.stdout.readline()
        if line != '':
            text = line.rstrip() + "<br>"
            socketio.emit('updatingSnipsASRInjectionInstalling', text, namespace='/injection')
        else:
            break

    output, error = p.communicate()  
    if p.returncode != 0:
        socketio.emit('updatingSnipsASRInjectionInstalling', '<br>Error installing snips-asr-injection<br>{}'.format(error), namespace='/injection')
    else:
        socketio.emit('updatingSnipsASRInjectionInstalling', output + "<br>" + error.replace("\n","<br>"), namespace='/injection')
       
    #all done and finished.. show the close button   
    socketio.emit('installingComplete', command, namespace='/injection')

    
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
    socketio.emit('injectionsComplete', "Done", namespace='/injection')

