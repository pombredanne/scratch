#!/bin/sh

# run after K25hwclock.sh, e.g. K26acpialarm.sh

. /lib/lsb/init-functions

case "$1" in
    start)
        ;;
    stop|restart|reload|force-reload)
        echo "$(cat /proc/acpi/alarm)" > /proc/acpi/alarm
        ;;
    *)
        log_success_msg "Usage: acpialarm.sh {start|stop|reload|force-reload}"
        return 1
        ;;
esac
