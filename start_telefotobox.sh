#!/bin/bash
npm start &
sleep 3
/usr/bin/chromium-browser --kiosk --disable-restore-session-state http://localhost:8000