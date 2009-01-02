#!/usr/bin/python
# displays active calls via cmxml
#
# Copyright (C) 2007 Tristan Hill (stan@saticed.me.uk)
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import cgi
import sys
import telnetlib


Out = 1
In = 2


def ami(t, action, parameters):
    """ Asterisk Manager Interface helper """
    if len(parameters) % 2 != 0:
       raise ValueError
    s = ""
    for parameter in [("Action", action)] + \
                      zip(parameters[::2], parameters[1::2]):
        s += "%s: %s\r\n" % parameter
    s += "\r\n"
    t.write(s)
    return t.read_until("\r\n\r\n")[:-len("\r\n\r\n")].split("\r\n")


def retrieve(hostname, username, password):
    t = telnetlib.Telnet(hostname, 5038)
    if 'Response: Success' in ami(t, "Login", ("Username", username, "Secret",
                                               password, "Events", "off")):
        ami(t, "Status", ())
        events = t.read_until("Event: StatusComplete\r\n\r\n").\
                                                         split("\r\n\r\n")[:-2]
        ami(t, "Logoff", ())
        t.read_all()
        t.close()
        return events
    

def make_events_dict(events):
    def dictify_event(event):
        d = {}
        for line in event.split("\r\n"):
            l = line.split(': ', 1)
            if len(l) == 2:
                d[l[0]] = l[1]
        return d 
    d = {}
    for event in events:
        event = dictify_event(event)
        d[event["Channel"]] = event
    return d


class Call(object):
    def __init__(self, seconds, channel, destination, direction):
        self.seconds = seconds
        self.channel = channel
        self.destination = destination
        self.direction = direction

    def get_channel_prefix(self):
        return self.channel.split("-", 1)[0]

    def __cmp__(self, other):
        return cmp((self.seconds, self.channel, self.destination,
                    self.direction),
                   (other.seconds, other.channel, other.destination,
                    other.direction))

    def __repr__(self):
        if self.direction == In:
            direction = "In"
        elif self.direction == Out:
            direction = "Out"
        else:
            direction = self.direction
        return "Call(%s, %s, %s, %s)" % (self.seconds, self.channel,
                                         self.destination, direction)

def process_events(events):
    """
    process status events
    
    assume CallerID always present but Seconds might not be
    """
    events = make_events_dict(events)
    active = []
    for channel, event in events.iteritems():
        try:
            if "Context" in event:
                seconds = event.get("Seconds")
                if "Link" in event:
                    destination = events[event["Link"]].get("CallerID")
                else:
                    destination = None
                active.append(Call(seconds, channel, destination, Out))
            else:
                if "Link" in event:
                    seconds = events[event["Link"]].get("Seconds")
                    destination = events[event["Link"]]["CallerID"]
                else:
                    seconds = None
                    destination = None
                active.append(Call(seconds, channel, destination, In))
        except KeyError:
            # event with Link to missing other event
            pass
    return active


def cmp_longest_call(x, y):
    return cmp(y.seconds, x.seconds)


def display(out, calls, directory):
    out("Content-type: text/xml\n")
    out("Refresh: 10\n\n")
    out("<CiscoIPPhoneDirectory>\n")
    out("<Title>Active Calls</Title>\n")
    if len(calls) == 1:
        out("<Prompt>1 active call</Prompt>\n")
    else:
        out("<Prompt>%d active calls</Prompt>\n" % len(calls))
    for call in calls:
        source, telephone = directory[call.get_channel_prefix()]
        out("<DirectoryEntry>\n")
        if call.destination == None:
            destination = ""
        else:
            destination = call.destination
        if call.direction == In:
            direction = "<-"
        elif call.direction == Out:
            direction = "->"
        out("  <Name>%s</Name>\n" % cgi.escape("%s%s%s" % (source, direction,
                                                            destination)))
        out("  <Telephone>%s</Telephone>\n" % telephone)
        out("</DirectoryEntry>\n")
    out("</CiscoIPPhoneDirectory>\n")


directory = {"SIP/stan": ("Tristan Hill", "831037"),
             "SIP/username": ("Name", "Number"),
             "SIP/test": ("Name", "Number")}


if __name__ == "__main__":
    events = retrieve("hostname", "username", "password")
    calls = []
    for call in process_events(events):
        if call.get_channel_prefix() in directory:
            calls.append(call)
    calls.sort(cmp_longest_call)
    display(sys.stdout.write, calls, directory)


    




