#!/usr/bin/python
# Copyright (C) 2007 Tristan Hill (stan@saticed.me.uk)
#
# This library/program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; withOUT even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

""" agi script to check online status of machines """

import signal
import socket
import sys


def openport(host, port):
    original_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, lambda signum, stack: None)
    signal.alarm(1)
    try:
        try:
            address = socket.gethostbyname(host)
        except socket.error:
            # return true if dns isn't working
            return True
    finally:
        signal.alarm(0) # turn off alarm
        signal.signal(signal.SIGALRM, original_handler)
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect((address, port))
        s.close()
        return True
    except socket.error:
        return False
             

def main(out, test, hostnames):
    for hostname in hostnames:
        if test(hostname):
            out.write('verbose "%s online"\n' % hostname)
            out.write('set variable "ONLINE_STATUS" "ONLINE"\n')
            break
        else:
            out.write('verbose "%s offline"\n' % hostname)
    else:
        out.write('set variable "ONLINE_STATUS" "OFFLINE"\n')
        out.write('verbose "Hosts offline"\n')


if __name__ == "__main__":
    def smbping(hostname):
        return openport(hostname, 445)
    main(sys.stdout, smbping, sys.argv[1:])

