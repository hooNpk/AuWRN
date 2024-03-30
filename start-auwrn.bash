#!/bin/bash

source auwrn-venv/bin/activate
nohup python app.py > shellscript_app.out &
#ngrok http 3000 --log=stdout > ngrok.log &