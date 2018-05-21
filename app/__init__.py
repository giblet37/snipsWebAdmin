#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, April 27th 2018, 6:36:13 pm
# Author: Greg
# -----
# Last Modified: Sun May 20 2018
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




from flask import Flask
from flask_mqtt import Mqtt
from flask_yaml import Yaml
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from config import config


bootstrap = Bootstrap()
mqtt = Mqtt()
yaml = Yaml()
mqttYaml = Yaml()
csrf = CSRFProtect()
socketio = SocketIO(async_mode='eventlet', ping_timeout=30,
                    logger=False, engineio_logger=False)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    yaml.init_app(app)

    #load MQTT settigns to config to get mqtt working
    
    mqttYaml.init_app(app, './settings.yaml') #'USER_MQTT_SETTINGS'))
    mqttsettings = mqttYaml.get_yaml_data("MQTT")
    for key, value in mqttsettings.iteritems():
        if key.isupper():
            app.config[key] = value

    #tempYaml = None

    mqtt.init_app(app)
    
    #socketio = SocketIO(app)
    #socketio.init_app(app)
    #socketio = SocketIO(app, async_mode='eventlet',
    #                    ping_timeout=30, logger=True, engineio_logger=True)
    #socketio.debug = True
    socketio.init_app(app)

    bootstrap.init_app(app)
    csrf.init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from watch import watch as watch_blueprint
    app.register_blueprint(watch_blueprint)

    from devices import devices as devices_blueprint
    app.register_blueprint(devices_blueprint)

    from generator import generator as generator_blueprint
    app.register_blueprint(generator_blueprint)

    return app


def get_socketio():
    return socketio
