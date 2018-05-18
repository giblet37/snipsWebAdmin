#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, May 11th 2018, 4:12:58 pm
# Author: Greg
# -----
# Last Modified: Thu May 17 2018
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
from . import devices
from app import mqtt,mqttYaml,socketio
from flask_socketio import emit
import utils
import os
import json
import subprocess
import string



@devices.route('/devices')
def devicePage():
    
    return render_template('devices.html')

@devices.route('/deviceslist', methods=['GET'])
def devicePageList():
    
    return "<p>greg</p>"

'''
poprn 

#ip's of devices connected to port 1883 - multiples of same name for use is not key add to dict
netstat | grep :1883 | awk '{print $5}' | cut -d ":" -f1


'''