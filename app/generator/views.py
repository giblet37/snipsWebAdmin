#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, May 11th 2018, 4:12:58 pm
# Author: Greg
# -----
# Last Modified: Sat May 19 2018
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
from . import generator
from app import socketio
from flask_socketio import emit
import utils
import os
import json
import subprocess
import string
from utils import YamlDB
import random
import itertools

db = ''

@generator.route('/generator')
def generatorPage():
    global db

    socketio.on_event('generate', generate, namespace='/generator')
    socketio.on_event('saveslot', saveslot, namespace='/generator')
    socketio.on_event('savenewslot', savenewslot, namespace='/generator')
    socketio.on_event('getSlotDropdownList', getSlotDropdownList, namespace='/generator')

    db = YamlDB(current_app)
    a = db.get_yaml_data('Buildin')
    
    stg = ''
    for item in a:
        stg += "<li><a class='dropdown-item' href='#' onClick='dropClicked(this)' data-value='" + item + "'>" + item + "</a></li>"

    stg += "<li><div class='dropdown-divider'></div></li>"

    a = db.get_yaml_data('Custom')
    print(a)
    for item in a:
        stg += "<li><a class='dropdown-item' href='#' onClick='dropClicked(this)' data-value='" + item + "'>" + item + "</a></li>"
      
    
    return render_template('generator.html', slotsList=stg)

def getSlotDropdownList(data):
    global db

    #save the new slot info that came in
    savenewslot(data)
    a = db.get_yaml_data('Buildin')
    
    stg = ''
    for item in a:
        stg += "<li><a class='dropdown-item' href='#' onClick='dropClicked(this)' data-value='" + item + "'>" + item + "</a></li>"

    stg += "<li><div class='dropdown-divider'></div></li>"

    a = db.get_yaml_data('Custom')
  
    for item in a:
        stg += "<li><a class='dropdown-item' href='#' onClick='dropClicked(this)' data-value='" + item + "'>" + item + "</a></li>"

    socketio.emit('slotsDropDownList', {"html":stg}, namespace='/generator')


@generator.route('/slotValues', methods=['POST'])
def getData():
    if request.method == "POST":
        global db
        #data = json.loads( request.data)
        #print (request.data['toml'])
        #print(request.data)
        json_data = request.get_json()
        print(json_data)
        #python_obj = json.loads(json_data)
        heading = json_data["heading"]
        print(heading)

    
        a = db.get_yaml_data(heading)  
        s = ''
        for item in a:
            s += "{}\n".format(item)
        return jsonify({'good':s})               
    
  
    return jsonify({'good':'ok'})


def generate(data):
    global db

    sentences = data['sentences'].split("\n")
    sentences = filter(None, sentences)
    items = {}
    built = []
    stg = ''
    slotvalues = ''
    slotvalues = '<br>*********************************************************<br>'
    slotvalues += '     edit each slot [Owner] and paste this into each       <br>'
    slotvalues += '*********************************************************<br><br>'
    consoletext = '*********************************************************<br>'
    consoletext += '       copy and paste this into the slots import         <br>'
    consoletext += '*********************************************************<br>'
    slotcontents = '*********************************************************<br>'
    slotcontents += '     copy and paste this into the Training Examples       <br>'
    slotcontents += '*********************************************************<br>'
    colors = {}

    for key,value in data.iteritems():
        if type(value) == dict:
            vls = []
            v = db.get_yaml_data(value['slot'])
            if value['slot'].startswith("snips/") == False:
                slotvalues += '<b>[{}]</b><br>'.format(value['slot'])
                for l in v:
                    slotvalues += "{}<br>".format(l) 
                slotvalues += "<br>"
            random.shuffle(v)
            for l in v:
                p = l.split(",")
                for h in p:
                    vls.append(h)

            items[value['label']] = vls
            colors[value['label']] = value['color']
            consoletext += '{}, {}'.format(value['label'],value['slot'])
            if value['required'] == 'true':
                consoletext += ", true"
                if len(value['text']) > 0:
                    consoletext += ", {}".format(value['text'])
            consoletext += '<br>'



    keys, values = zip(*items.items())
    for v in itertools.product(*values):
        experiment = dict(zip(keys, v))
        built.append(experiment)

    random.shuffle(built)

    consoletext = "{}{}<br>{}".format(consoletext,slotvalues,slotcontents)

    # {"color":td1.id, "label":td2.value, "slot":slotval, "required":c.checked, "text":t };
    #[text](slotName) 
    #date, snips/datetime, true, whats the date
    dictcheck = []
    for builtitems in built:
        for sent in sentences:
            temp1 = sent
            temp2 = sent
            for key, value in builtitems.iteritems():
                #print("{} : {}".format(key,value))
                f = "${}".format(key)
                m = "<span style='background-color: " + colors[key] + "'>" + value + "</span>"
                c = "[{}]({})".format(value,key)
                temp1 = temp1.replace(f,c)
                temp2 = temp2.replace(f,m)
            
            if temp1 not in dictcheck:
                dictcheck.append(temp1)
                stg += temp2 + "<br>"
                consoletext += temp1 + "<br>"


    socketio.emit('resultscode', {"code":consoletext,"html":stg, "count":len(dictcheck)}, namespace='/generator')

def saveslot(data):
    global db
    #heading:editingSlotName, slotinfo:ed.value 
   
    db.set_yaml_data(data['heading'],data['slotinfo'].split("\n"))

    db.save_yaml_file()

def savenewslot(data):
    global db

    cus = db.get_yaml_data('Custom')

    cus.append(data['heading'])


    db.set_yaml_data('Custom',cus)

    db.set_yaml_data(data['heading'],data['slotinfo'].split("\n"))

    db.save_yaml_file()