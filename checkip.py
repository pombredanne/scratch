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
        struct.pack('256s', bytes(ifname[:15]))
    )[20:24])

if __name__ == '__main__':
    address = get_ip_address(sys.argv[1])
    print("""<html><head><title>Current IP Check</title></head><body>Current IP Address: %s</body></html>""" % address)

