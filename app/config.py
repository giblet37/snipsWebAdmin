#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, April 27th 2018, 6:42:34 pm
# Author: Greg
# -----
# Last Modified: Tue Jun 05 2018
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
import platform

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    #DEBUG = False
    #DEBUG_LOG = 'logs/debug.log'
    #ERROR_LOG = 'logs/error.log'
    WTF_CSRF_ENABLED = False
    SECRET_KEY='Q5G94WB6RVRP4TO85RGI2Y6TM7HYY0P'
    SSL_REDIRECT = False

    TOMLFILE = os.path.join(basedir,"data/db.toml")

    SNIPS_DIR = os.environ.get('SNIPS_DIR', '/usr/share/snips/assistant')
    SNIPS_TOML = "/etc/snips.toml"
    SNIPS_TOML_DUMMY = os.path.join(os.path.dirname(basedir),"snips.toml")
    SNIPS_TOML_BACKUP = "/etc/snips.toml.bak"
    SNIPS_ASSISTANT_SNIPSFILE = os.path.join(SNIPS_DIR,"Snipsfile.yaml")
    SNIPS_ASSISTANT_ASSISTANTFILE = os.path.join(SNIPS_DIR,"assistant.json")
    SNIPS_ASSISTANT_TRAINEDASSISTANTFILE = os.path.join(SNIPS_DIR,"trained_assistant.json")
    SNIPS_ASSISTANT_SNIPPETDIR = os.path.join(SNIPS_DIR,"snippets")
    
    APP_SETTINGS = os.path.join(os.path.dirname(basedir),"settings.toml")
    
    CMD_HOSTNAME = "hostname"

    installedDevice = platform.system()
    #print(installedDevice)
    if installedDevice == "Ubuntu":
        CMD_HOSTNAME = "hostname -I"
    #elif installedDevice == "Darwin":
    #     CMD_HOSTNAME = "hostname"
    


    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    #DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
      
        
        credentials = None
        secure = None

    

config = {
    'production': ProductionConfig,
    'default': ProductionConfig
}