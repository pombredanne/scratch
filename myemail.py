#!/usr/bin/python

import os
import socket
import fcntl
import struct


# http://code.activestate.com/recipes/439094/
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def get_default_route_ifname():
    for line in open("/proc/net/route"):
        split = line.split()
        if split[1] == "00000000":
            return split[0]


def main():
    ifname = get_default_route_ifname()
    if ifname is not None:
        print "%s@%s" % (os.environ["USER"], socket.gethostbyaddr(get_ip_address(ifname))[0])


# from iotop/netlink.py - GPLv2
def recv(self):
    contents, (nlpid, nlgrps) = iotop.netlink._nl_recv(self.descriptor)
    # XXX: python doesn't give us message flags, check
    #      len(contents) vs. msglen for TRUNC
    msgs = []
    while len(contents) > 0:
        msglen, msg_type, flags, seq, pid = struct.unpack("IHHII",
                                                          contents[:16])
        msg = iotop.netlink.Message(msg_type, flags, seq, contents[16:msglen])
        msg.pid = pid
        if msg.type == iotop.netlink.NLMSG_ERROR:
            import os
            errno = -struct.unpack("i", msg.payload[:4])[0]
            if errno != 0:
                err = OSError("Netlink error: %s (%d)" % (
                    os.strerror(errno), errno))
                err.errno = errno
                raise err
        msgs.append(msg)
        assert len(contents) >= msglen
        contents = contents[msglen:]
    return msgs


def getrtattrs(data):
    while len(data) > 0:
        length, type_ = struct.unpack("BB", data[:2])
        print "attr", length, type_
        data = data[length:]


def cycle(f):
    while True:
        for i in f():
            yield i



if __name__ == "__main__":
    main()
#    s = socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM, socket.NETLINK_ROUTE)
#    s.bind((os.getpid(), 0))
#    s.sendto("", (0, 0))
#    print repr(s.recv(4096))
#    print "end"
    import iotop.netlink

    c = iotop.netlink.Connection(socket.NETLINK_ROUTE)
    # type
    RTM_NEWADDR = 20 # see rtnetlink.h
    RTM_GETADDR = 22 # see rtnetlink.h
    # flags
    NLM_F_ROOT = 0x100 # see netlink.h
    NLM_F_MATCH = 0x200 # set netlink.h
    NLM_F_REQUEST = iotop.netlink.NLM_F_REQUEST

    payload=struct.pack("B", socket.AF_INET)
    m = iotop.netlink.Message(RTM_GETADDR, NLM_F_ROOT|NLM_F_MATCH|NLM_F_REQUEST, payload=payload)
    m.send(c)
    #m = recv(c)
    for m in cycle(lambda: recv(c)):
        if m.type == iotop.netlink.NLMSG_DONE:
            break
        print "msg", len(m.payload), m.type
        print repr(m.payload)
        getrtattrs(m.payload)
        #m = recv(c)


    # struct ifaddrmsg
    # BBBBi, socket.AF_INET, 0, 0, 0, 0
