#!/bin/sh
set -e

export DISPLAY=:0.0
 
STATUS="$(xset -q | grep "Monitor is" | awk '{print $3}')"
if [ "$STATUS" = On ]; then
    xset dpms force off
else
    xset s reset
    xset dpms force on
fi
