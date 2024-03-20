#!/bin/bash
sudo pigpiod
sleep 15
/home/pi/telefotobox/dialer-venv/bin/python3 /home/pi/telefotobox/dialer.py start
