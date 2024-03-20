#!/bin/bash
sudo pigpiod
sleep 15
/home/pi/telefotobox/dailer-venv/bin/python3 /home/pi/telefotobox/dailer.py start
