#!/usr/bin/python
# Copyright (c) 2004 C.E. Hill & Co. (UK) Ltd. (tristan@cehill.co.uk)
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

import socket, string, re

class InvalidReply(Exception):
    pass

class manager(object):

    def __init__(self, host, port):
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__recvlineBuf = ""
        self.__recvlineText = ""

        self.__s.settimeout(2.0)
        self.__s.connect((host, port))
        connectReply = self.__s.recv(30)
        LOGIN_MESSAGE = 'Asterisk Call Manager/1.0'
        if connectReply[0:len(LOGIN_MESSAGE)] != LOGIN_MESSAGE:
            print connectReply
            raise InvalidReply

    
    def login(self, userName, password):

        loginString = "Action: Login\r\n" + \
                      "UserName: " + userName + "\r\n" \
                      "Secret: " + password + "\r\n\r\n"
                 
        self.__s.send(loginString)
        loginReply = self.__getEvent()
        return [loginReply]


    def logoff(self):

        logoffString = "Action: Logoff\r\n\r\n"
        self.__s.send(logoffString)
        
        logoffReply = self.__getEvent()
        self.__s.close()
        return [logoffReply]


    def command(self, commandName):

        commandString = "Action: Command\r\n" + \
                        "Command: " + commandName + "\r\n\r\n"


        self.__s.send(commandString)
        commandReply = self.__s.recv(100)
        commandReply += self.__s.recv(100)
        commandReply += self.__s.recv(100)
        print "command: " + commandReply

    def originate(self, origin, destination, context):

        originateString = "Action: Originate\r\n" + \
                          "Channel: " + origin + "\r\n" + \
                          "Exten: " + destination + "\r\n" + \
                          "Context: " + context + "\r\n" + \
                          "Priority: 1\r\n\r\n"

        self.__s.send(originateString)
        originateReply = self.processReply()
        originateReply += self.__s.recv(100)
    #    originateReply += s.recv(1024)
        print "originate: " + originateReply
    

    def __getEvent(self):
        eventText = list()
        while self.__recvline():
            eventText.append(self.__recvlineText)
        
        return eventText

    def __recvline(self):

        index = string.find(self.__recvlineBuf, "\r\n")
        printv("=== index = %d" % index)
        if index == 0:
            printv("== end of message")
            self.__recvlineBuf = self.__recvlineBuf[index+2:]
            return False
        elif index == -1:
            printv("=== getting more data from socket")
            self.__recvlineBuf = self.__s.recv(1024)
            return self.__recvline()
        else:
            self.__recvlineText = self.__recvlineBuf[:index]
            printv("== %s" % self.__recvlineText)
            self.__recvlineBuf = self.__recvlineBuf[index+2:]
            printv("=== left in buffer = \"%s\"" % self.__recvlineBuf)
#            print "remaining buf = \"%s\"" % self.recvlineBuf
            return True
        
    def status(self):
       
        statusString = "Action: Status\r\n" + \
                       "ActionID: 1\r\n\r\n"

        end = "Event: StatusComplete"
        self.__s.send(statusString)
   
        statusReply = list()
        event = self.__getEvent()
        while event[0][:len(end)] != end:
            statusReply.append(event)
            event = self.__getEvent()
        
        statusReply.append(event)
        return statusReply
#        statusReply = self.s.recv(100)
#        statusReply += self.s.recv(100)
#        statusReply += self.s.recv(100)
#print "Entering processReply"
#        print self.processReply2("Status", "StatusComplete")
#        print "status:", statusReply 

def printv(s):
    if debug:
        print s
   
debug = False
#m = Manager()
#pprint.pprint(m.login('test', 'pass'))
#m.command('show uptime')
#m.originate('SIP/test', '100', 'demo')
#pprint.pprint(m.status())
#pprint.pprint(m.logoff())

class callerid(object):
    def __init__(self, calleridString):
         self.name = ""
         self.number = ""
         m = re.match("^([0-9]+)$", calleridString)
         if m:
              self.name = ""
              (self.number,) = m.groups()
         else:
              m = re.match("^\"([^\"]+)\" <([0-9]+)>$", calleridString)
              if m:
                   (self.name, self.number) = m.groups()

    def preferName(self):
         if len(self.name) > 0:
             return self.name
         else:
             return self.number



