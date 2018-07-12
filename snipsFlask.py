#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, April 27th 2018, 7:12:41 pm
# Author: Greg
# -----
# Last Modified: Thu Jul 12 2018
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
import sys
from shutil import copyfile
import logging


if os.path.isfile('./settings.toml') == False:
    copyfile('./settings.toml.conf', './settings.toml')

#if os.path.isfile('./app/data/db.toml') == False:
#    copyfile('./app/data/db.toml.conf', './app/data/db.toml')

if os.path.isfile('./app/data/db-en.toml') == False:
    copyfile('./app/data/db-en.conf', './app/data/db-en.toml')

if os.path.isfile('./app/data/db-de.toml') == False:
    copyfile('./app/data/db-de.conf', './app/data/db-de.toml')


from app import create_app, get_socketio

logging.basicConfig(level=logging.INFO)

app = create_app('default')
#app.config['FLASK_LOG_LEVEL'] = 'ERROR'
app.logger.setLevel(logging.ERROR)


sock = get_socketio()

#log only "errors" for these items
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('paramiko').setLevel(logging.ERROR)


sock.run(app, host='0.0.0.0', port=5000, log_output=False) #, use_reloader=True)

