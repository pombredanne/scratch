#!/bin/sh
set -e

#echo "$(date) off" >> /home/stan/log
#exit 0

export DISPLAY=:0.0
 
STATUS="$(xset -q | grep "Monitor is" | awk '{print $3}')"
if [ "$STATUS" = On ]; then
    xset dpms force off
else
    xset dpms force on
#    xset s reset
fi

exit 0

