#!/usr/bin/python

import optparse
import random
import subprocess


def generate_mac():
    address = [00, 0x1d, 0x7d]
    for i in range(3):
    	address.append(random.randrange(0, 255))
    mac = ":".join("%02x" % b for b in address)
    print mac
    return mac


def main():
    parser = optparse.OptionParser("%prog interface")
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("Need interface")
    subprocess.call(["ip", "link", "set", args[0], "address", generate_mac()])


if __name__ == "__main__":
    main()


