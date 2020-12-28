#!/bin/bash
# start flask server

PYTHONPATH=/opt/blinkapp
export PYTHONPATH

cd /opt/blinkapp/blinkapp

FLASK_APP=start.py
export FLASK_APP

# start server
python -m flask run --host=0.0.0.0