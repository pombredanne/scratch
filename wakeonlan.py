#!/usr/bin/python

import cgi
import subprocess
import sys
import re
import StringIO as io


lease_start_re = re.compile("^ *lease .* *{ *$")
lease_end_re = re.compile("^ *} *$")


# apt_pkg from python-apt didn't like syntax of file (see examples/configisc.py)
def get_leases():
    in_lease = False
    mac = None
    hostname = None
    macs = {}
    for line in open("/var/lib/dhcp3/dhcpd.leases"):
        if in_lease:
            if lease_end_re.match(line):
                in_lease = False
                if mac and hostname:
                    macs[mac] = hostname
                mac = None
                hostname = None
            else:
                split = line.split()
                if split[:2] == ["hardware", "ethernet"]:
                    mac = split[-1].rstrip(";")
                elif split[:1] == ["client-hostname"]:
                    hostname = split[-1].strip('";"')
        elif lease_start_re.match(line):
            in_lease = True
    return macs.items()


sample_dnsmasq_leases = """1392375688 00:ff:8f:17:d6:ff 192.168.121.23 ethan 01:00:1e:8c:17:d6:ce
1392375624 10:0b:a9:ee:ee:ee 192.168.124.138 t420 01:10:0b:a9:38:a1:e8"""

def get_dnsmasq_leases(leases):
    macs = {}
    for line in leases:
        split = line.split(' ')
        if len(split[3]) > 1:
            macs[split[1]] = split[3]
    return list(macs.items())

assert set(get_dnsmasq_leases(io.StringIO(sample_dnsmasq_leases))) == set([('00:ff:8f:17:d6:ff', 'ethan'), ('10:0b:a9:ee:ee:ee', 't420')])

write = sys.stdout.write


def main():
    leases = get_dnsmasq_leases(open('/var/lib/misc/dnsmasq.leases'))
    form = cgi.FieldStorage()
    sent_hostname = form.getfirst("hostname")
    for mac, hostname in leases:
        if hostname == sent_hostname:
            subprocess.call(["wakeonlan", "-i", "192.168.121.255", mac])
    write("Content-Type: text/html\n\n")
    write("<html><head><title>Wake On Lan</title></head><body>\n")
    write("<form method='POST'>\n<ul>\n")
    hostnames = list(set([hostname for mac, hostname in leases]))
    hostnames.sort()
    for hostname in hostnames:
        write("<li><input type='submit' name='hostname' value='%s'></li>\n" % hostname)
    write("</ul>\n</form></body></html>\n")


if __name__ == "__main__":
    main()



