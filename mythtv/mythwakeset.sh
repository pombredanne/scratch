#!/bin/sh
set -e

# set as nvram-wakeup command in mythwelcome -s

if [ "$#" != 2 ]; then
    echo "Usage $0 --settime epoch" 1>&2
    echo "or" 1>&2
    echo "Usage $0 YYYYMMDD MM:HH:SS" 1>&2
    exit 1
fi

if [ "$1" = --settime ]; then
    INPUT_TIME="@$2"
else
    INPUT_TIME="$1 $2"
fi
    
TIME_WITH_TIMEZONE="$(date --date "$INPUT_TIME" "+%F %T %z")"
UTC_TIME="$(date --utc --date "$TIME_WITH_TIMEZONE" "+%F %T")"
echo "$UTC_TIME" > /proc/acpi/alarm


