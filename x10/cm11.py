#!/usr/bin/python

import os
import subprocess
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    args = sys.argv[1:]
    if len(args) == 2:
        send_x10(*args)
        sys.exit(0)
    sys.exit("invalid args %s" % args)


address_re = re.compile("^(?P<housecode>[A-F])[1-9]$")
commands_map = {"on": "J", "off": "K"}
def send_x10(address, command):
    address = address.upper()
    command = command.lower()
    m = address_re.match(address)
    if m is not None and command in commands_map:
        cmd = ["perl", "-I", DIR, os.path.join(DIR, "eg_cm11.plx"),
            "/dev/ttyUSB1"]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        p.stdin.write("%s\n" % address)
        p.stdin.write("%s%s\n" % (m.group("housecode"),
            commands_map[command]))
        p.stdin.close()
        p.wait()
        return
    else:
        raise ValueError("invalid args %s" % (address, command))


if __name__ == "__main__":
    main()
