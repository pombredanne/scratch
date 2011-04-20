#!/usr/bin/python

import sys
import socket
import struct
import re
import math


def inet_aton(string):
    """
    Convert dotted ip to number.
    """
    return struct.unpack("!L", socket.inet_aton(string))[0]


def inet_ntoa(integer):
    """
    Convert number to dotted ip string.
    >>> inet_ntoa(inet_aton("192.168.0.1"))
    '192.168.0.1'
    """
    return socket.inet_ntoa(struct.pack("!L", integer))


def get_max_netmask(ips):
    """
    Generate the largest netmask to make all the ips in the same network.
    >>> get_max_netmask(['192.168.0.1', '192.168.0.253'])
    '255.255.255.0'
    >>> get_max_netmask(['192.168.1.2', '192.168.4.2'])
    '255.255.248.0'
    >>> get_max_netmask(['10.54.67.198', '10.54.67.202'])
    '255.255.255.240'
    >>> get_max_netmask(['192.168.1.3'])
    '255.255.255.255'
    >>> get_max_netmask([])
    Traceback (most recent call last):
    ...
    ValueError: need at least one IP
    """
    if len(ips) == 0:
        raise ValueError("need at least one IP")
    min_ = inet_aton("255.255.255.255")
    max_ = inet_aton("0.0.0.0")
    for ip in ips:
        i = inet_aton(ip)
        min_ &= i
        max_ |= i
    xor = min_ ^ max_
    i = 0
    while xor >> i != 0:
        i += 1
    return inet_ntoa(2**32 - 2**i)


class InvalidNetmask(Exception):
    pass


def inet_atocidr(ip, netmask):
    """
    Convert dotted netmask notation to cidr format.
    >>> inet_atocidr("192.168.0.1", "255.255.255.128")
    '192.168.0.1/25'
    >>> inet_atocidr("192.168.0.1", "255.255.1.0")
    Traceback (most recent call last):
    ...
    InvalidNetmask: Invalid netmask
    """
    def netmaskconv(netmask):
        i = math.log(2**32 - inet_aton(netmask), 2)
        if i % 1 != 0:
            raise InvalidNetmask("Invalid netmask")
        return int(32 - i)
    return "%s/%d" % (ip, netmaskconv(netmask))


def main():
    network_re = re.compile(r"^inetnum:\s+([.\d]+)\s+-\s+([.\d]+)$")
    for line in sys.stdin:
        m = network_re.match(line)
        if m:
             netmask = get_max_netmask([m.group(1), m.group(2)])
             print inet_atocidr(m.group(1), netmask)


if __name__ == "__main__":
    main()


