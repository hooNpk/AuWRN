#!/bin/bash

source auwrn-venv/bin/activate
nohup python app.py > shellscript_app.out &
nohup ngrok http 3000 > shellscript_ngrok.out &
