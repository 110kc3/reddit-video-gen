#!/bin/bash
env > /home/ubuntu/logs/reddit-video-gen/env.log
export DISPLAY=:99
Xvfb :99 -screen 0 1280x1024x24 &
sleep 3
python3 main.py
killall Xvfb