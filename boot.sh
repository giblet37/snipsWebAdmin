#!/bin/sh

#delete all pyc files
find . -name \*.pyc -delete

#run web admin
python snipsFlask.py