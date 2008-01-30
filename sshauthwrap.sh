#!/bin/bash
set -e

check_key() {
    local log="$1"
    local socks="$(find /tmp/ssh-* -type s -user $(id -u) -name agent.\*)"
    if [ -z "$socks" ]; then
        [ -z "$log" ] || echo "No ssh agent sockets found" 1>&2
        return 1
    fi
    local sock
    for sock in $socks; do
        export SSH_AUTH_SOCK="$sock"
        if ssh-add -L &>/dev/null; then
            return 0
        fi
    done
    [ -z "$log" ] || echo "No ssh keys loaded" 1>&2
    return 1
}

TIMES="$1"
shift
case "$TIMES" in
    1) check_key log
    ;;
    -) while true; do check_key && break; sleep 30; done
    ;;
esac

exec "$@"

