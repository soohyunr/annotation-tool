#!/usr/bin/env bash

if [ "$1" = "start" ]
then
    echo "<-------- start flask -------->"
    source ENV/bin/activate
    export PYTHONPATH=.
    sudo pip install -r requirements.txt
	nohup python web/app.py > app.log 2>&1 &
    echo $! > save_pid.txt
else
    echo "<-------- stop flask -------->"
    source ENV/bin/activate
    kill -9 `cat save_pid.txt`
fi