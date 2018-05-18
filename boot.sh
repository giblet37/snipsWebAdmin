#!/bin/sh

#delete all pyc files
find . -name \*.pyc -delete

#run web admin
#exec gunicorn -b :5000 --worker-class gevent -w 1 snipsFlask:app
python snipsFlask.py