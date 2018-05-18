#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, April 27th 2018, 6:42:34 pm
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




import os
from flask_yaml import Yaml

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = False
    DEBUG_LOG = 'logs/debug.log'
    ERROR_LOG = 'logs/error.log'
    SECRET_KEY='Q5G94WB6RVRP4TO85RGI2Y6TM7HYY0P'
    SUDO_PASSWORD = 'raspberry'
    SSL_REDIRECT = False
    YAMLFILE = os.path.join(basedir,"data/db.yaml")
    VERSION = "0.1"
    SNIPS_TOML = "/etc/snips.toml"
    SNIPS_TOML_BACKUP = "/etc/snips.toml.bak"
    SNIPS_ASSISTANT_SNIPSFILE = '/usr/share/snips/assistant/Snipsfile.yaml'
    SNIPS_ASSISTANT_ASSISTANTFILE = '/usr/share/snips/assistant/assistant.json'
    WTF_CSRF_ENABLED = False
    USER_MQTT_SETTINGS = os.path.join(os.path.dirname(basedir),"settings.yaml")



    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
      
      
        

        import logging
        credentials = None
        secure = None
       
        ## log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

       


config = {
    'production': ProductionConfig,
    'default': ProductionConfig
}