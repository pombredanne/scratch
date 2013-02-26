#!/bin/sh

Xephyr -ac -screen 1280x768 -br -reset -terminate 2>/dev/null :10 &
sleep 1

export DISPLAY=:10.0
metacity &
METACITY_PID=$!

"$@"

kill $METACITY_PID
wait

