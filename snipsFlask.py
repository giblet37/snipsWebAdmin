#!/usr/bin/env python2
# -*- coding:utf-8 -*-

### **************************************************************************** ###
# 
# Project: Snips Web Admin
# Created Date: Friday, April 27th 2018, 7:12:41 pm
# Author: Greg
# -----
# Last Modified: Sat May 12 2018
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

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

import sys
import click

from app import create_app, get_socketio

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
sock = get_socketio()


#@app.context_processor
#def inject_version():
#    return dict(version=app.config['VERSION'])


@app.cli.command()
@click.option('--length', default=25,
              help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None,
              help='Directory where profiler data files are saved.')
def profile(length, profile_dir):   
    sock.run(app, host='0.0.0.0', port=5000, log_output=True)
   