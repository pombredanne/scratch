#!/usr/bin/python
# status.cgi - an asterisk status retriever script
# Copyright (C) 2004 C.E. Hill & Co. (UK) Ltd. (tristan@cehill.co.uk)
#
# This library/program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import ast, cgi, sys, csv
#import cgitb; cgitb.enable()

#dir = [['User 1', '201', 'SIP/user1', 'SIP/user2'],
#       ['User A', '202', 'SIP/usera']]

def dirload():
    dir = list()
    f = file("/home/cehillco/admin/telephone/internal_directory.csv", 'r')
    reader = csv.reader(f)
    for row in reader:
        entry = list()
        for i in range(0, len(row)):
            entry.append(row[i])
    
        dir.append(entry)

    f.close()
    return dir


# 'Channel: SIP/stan1-997f'
"""
received call looks like this
 ['Event: Status',
  'Channel: SIP/stan1-563c',
  'CallerID: 231',
  'State: Up',
  'Link: Zap/1-1',
  'Uniqueid: 1078506259.9',
  'ActionID: 1'],
"""

"""
outgoing call looks like this
 ['Event: Status',
  'Channel: SIP/stan1-1262',
  'CallerID: "Tristan Hill" <225>',
  'State: Up',
  'Context: stan',
  'Extension: 231',
  'Priority: 1',
  'Link: Zap/4-1',
  'Uniqueid: 1078506511.11',
  'ActionID: 1'],
"""

# from, to, direction
"""
status
  channel = 'SIP/stan1'
  status[channel] = (outgoing_call, identifier)
#  calls = [(True, '231'),(False, 231)]
  call = (True, '231')
"""

def dictify(event):
    d = dict()
    for line in event:
        l = line.split(': ', 1)
        if len(l) == 2:
            d[l[0]] = l[1]
        else:
            print "=== %s" % line
      
    if d.has_key('Channel'):
        d['Channel'] = d['Channel'][:d['Channel'].find('-')]

    return d 

def examine(statusList):
    status = dict()
    for eventList in statusList:
        e = dictify(eventList)
        if e.has_key('Event') and e['Event'] == 'Status':
            if e.has_key('Extension'): # outgoing
                status[e['Channel']] = (True, e['Extension'])
            elif e.has_key('CallerID'): # incoming
                name = ast.callerid(e['CallerID']).preferName()
                status[e['Channel']] = (False, name)

    return status

print "Content: text/xml"
print "Refresh: 10"
print


try:
    dir = dirload()
    m = ast.manager('scat.pa.cehill.co.uk', 5038)
    m.login('test', 'pass')
    slist = m.status()
#print slist
    status = examine(slist)
    m.logoff()
except:
    print "<!-- Exception: %s, %s -->" % \
            (sys.exc_info()[0], sys.exc_info()[1])
    dir = list()
    status = dict()

    
print "<CiscoIPPhoneDirectory>"
print "<Title>Internal Numbers</Title>"
print "<Prompt>%d numbers</Prompt>" % len(dir)

for row in dir:
    name = row[0]
    for channel in row[2:]:
        if status.has_key(channel):
            call = status[channel]
            if call[0]:
                name += "->%s" % (call[1])
            else:
                name += "<-%s" % (call[1])

    print "<DirectoryEntry>"
    print "  <Name>%s</Name>" % cgi.escape(name)
    print "  <Telephone>%s</Telephone>" % row[1]
    print "</Directory>"
    

print "</CiscoIPPhoneDirectory>"

