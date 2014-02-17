#!/usr/bin/python3

import fcntl
import socket
import struct
import sys

# http://code.activestate.com/recipes/439094-get-the-ip-address-associated-with-a-network-inter/
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], 'utf8'))
    )[20:24])

if __name__ == '__main__':
    if sys.argv[1] == 'eth2' and sys.argv[2] == 'dhcp4-change':
        address = get_ip_address(sys.argv[1])
        with open('/var/www/checkip.html', 'w') as f:
            f.write("""<html><head><title>Current IP Check</title></head><body>Current IP Address: %s</body></html>""" % address)

