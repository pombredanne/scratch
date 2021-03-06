#!/usr/bin/python

import os
import socket
import subprocess
import sys


def ipcheck(dirname, account_filename, *args):
    subprocess.call(["python", "ipcheck.py"] + list(args) + 
                    ["--acctfile", account_filename], cwd=dirname)


def get_default_route_iface():
    f = open("/proc/net/route")
    try:
        f.next()
        for line in f:
            split = line.split()
            if len(split) > 2 and split[1] == "00000000":
                return split[0]
    finally:
        f.close()


def main(dirname, account_filename):
    hostname = open(os.path.join(dirname, account_filename)).read().split()[-1]
    raw_input(socket.gethostbyname(hostname))
    if socket.gethostbyname(hostname) == "127.0.0.1":
#        ipcheck(dirname, account_filename, "-r", "http://192.168.1.254"
#        "/cgi/b/is/_ethoa_/ov/?ce=1&be=0&l0=1&l1=1&name=RoutedEthoA")
        ipcheck(dirname, account_filename, "-i", get_default_route_iface())
    else:
        ipcheck(dirname, account_filename, "-a", "127.0.0.1")


if __name__ == "__main__":
    main(os.path.abspath(os.path.dirname(sys.argv[0])), "acct")
    raw_input()
