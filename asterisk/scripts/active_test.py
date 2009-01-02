#!/usr/bin/python
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

import unittest

import active

def format_events(s):
    return [t.replace("\n", "\r\n") for t in s.strip().split("\n\n")]


class TestProcessEvents(unittest.TestCase):

    def test_sip_to_asterisk(self):
        events = """
Event: Status
Privilege: Call
Channel: SIP/stan-081f0f80
CallerID: 831037
CallerIDName: Tristan Hill
Account: 
State: Up
Context: stan
Extension: 1499
Priority: 2
Seconds: 30
Uniqueid: asterisk-2386-1173894756.52

Event: Status
Privilege: Call
Channel: SIP/stan-081f0f81
CallerID: 831037
CallerIDName: Tristan Hill
Account: 
State: Up
Context: stan
Extension: 1499
Priority: 2
Seconds: 3
Uniqueid: asterisk-2386-1173894756.51
"""
        events = format_events(events)
        calls = active.process_events(events)
        calls.sort()
        self.assertEqual(calls,
                    [active.Call("3", "SIP/stan-081f0f81", None, active.Out),
                     active.Call("30", "SIP/stan-081f0f80", None, active.Out)])

    def test_sip_to_zap(self):
        events = """
Event: Status
Privilege: Call
Channel: Zap/1-1
CallerID: 9123
CallerIDName: <unknown>
Account: 
State: Up
Link: SIP/stan-081e9a78
Uniqueid: asterisk-2386-1173988031.83

Event: Status
Privilege: Call
Channel: SIP/stan-081e9a78
CallerID: 831037
CallerIDName: Tristan Hill
Account: 
State: Up
Context: macro-dialout
Extension: s
Priority: 1
Seconds: 11
Link: Zap/1-1
Uniqueid: asterisk-2386-1173988031.82
"""
        events = format_events(events)
        calls = active.process_events(events)
        calls.sort()
        self.assertEqual(calls,
                  [active.Call("11", "SIP/stan-081e9a78", "9123", active.Out),
                   active.Call("11", "Zap/1-1", "831037", active.In)])

    def test_zap_to_sip(self):
        events = """
Event: Status
Privilege: Call
Channel: SIP/stan-08204008
CallerID: 831037
CallerIDName: <unknown>
Account: 
State: Up
Link: Zap/2-1
Uniqueid: asterisk-2386-1173904233.58

Event: Status
Privilege: Call
Channel: Zap/2-1
CallerID: 750933
CallerIDName: Hill Tristan Home
Account: 
State: Up
Context: macro-cisco7960_3
Extension: s
Priority: 3
Seconds: 18
Link: SIP/stan-08204008
Uniqueid: asterisk-2386-1173904233.57
"""
        events = format_events(events)
        calls = active.process_events(events)
        calls.sort()
        self.assertEqual(calls,
                 [active.Call("18", "SIP/stan-08204008", "750933", active.In),
                  active.Call("18", "Zap/2-1", "831037", active.Out)])

    def test_sip_to_sip_ringing(self):
        events = """
Event: Status
Privilege: Call
Channel: SIP/nats-081fe528
CallerID: 831031
CallerIDName: <unknown>
Account: 
State: Ringing
Uniqueid: asterisk-2386-1173990555.85

Event: Status
Privilege: Call
Channel: SIP/stan-081f6a28
CallerID: 831037
CallerIDName: Tristan Hill
Account: 
State: Ring
Context: macro-cisco7960_3
Extension: s
Priority: 3
Seconds: 4
Uniqueid: asterisk-2386-1173990555.84
"""
        events = format_events(events)
        calls = active.process_events(events)
        calls.sort()
        self.assertEqual(calls,
                     [active.Call(None, "SIP/nats-081fe528", None, active.In),
                      active.Call("4", "SIP/stan-081f6a28", None, active.Out)])

    def test_sip_to_sip(self):
        events = """
Event: Status
Privilege: Call
Channel: SIP/nats-081f65d8
CallerID: 831031
CallerIDName: <unknown>
Account: 
State: Up
Link: SIP/stan-081f0f48
Uniqueid: asterisk-2386-1174066927.119

Event: Status
Privilege: Call
Channel: SIP/stan-081f0f48
CallerID: 831037
CallerIDName: Tristan Hill
Account: 
State: Up
Context: macro-cisco7960_3
Extension: s
Priority: 3
Seconds: 21
Link: SIP/nats-081f65d8
Uniqueid: asterisk-2386-1174066927.118
"""
        events = format_events(events)
        calls = active.process_events(events)
        calls.sort()
        self.assertEqual(calls,
                [active.Call("21", "SIP/nats-081f65d8", "831037", active.In),
                 active.Call("21", "SIP/stan-081f0f48", "831031", active.Out)])


class TestCmp(unittest.TestCase):
    def test_cmp(self):
        x = active.Call(0, None, None, None)
        y = active.Call(None, None, None, None)
        self.assertEqual(active.cmp_longest_call(y, x), 1)


class TestCall(unittest.TestCase):
    def test_sip(self):
        a = active.Call(None, "SIP/stan-abc", None, None)
        self.assertEqual(a.get_channel_prefix(), "SIP/stan")

    def test_zap(self):
        b = active.Call(None, "Zap/1-1", None, None)
        self.assertEqual(b.get_channel_prefix(), "Zap/1")


if __name__ == "__main__":
    unittest.main()
