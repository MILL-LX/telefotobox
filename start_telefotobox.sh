#!/bin/bash
killall python node
sleep 5
npm start &
sleep 3
/usr/bin/chromium-browser --kiosk --disable-restore-session-state http://localhost:8000