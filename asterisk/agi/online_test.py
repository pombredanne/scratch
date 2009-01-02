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

import StringIO
import unittest

import online

class Tests(unittest.TestCase):

    def test_online(self):
        out = StringIO.StringIO()
        class Counter(object):
            def __init__(self):
                self.count = 0
            def call(self, hostname):
                self.count += 1
                return self.count % 2 == 0
        counter = Counter()
        online.main(out, counter.call, ["one", "two"])
        self.assertEqual(out.getvalue(), """\
verbose "one offline"
verbose "two online"
set variable "ONLINE_STATUS" "ONLINE"
""")
        out.close()
        self.assertEqual(counter.count, 2)

    def test_offline(self):
        out = StringIO.StringIO()
        online.main(out, lambda x: False, ["one", "two"])
        self.assertEqual(out.getvalue(), """\
verbose "one offline"
verbose "two offline"
set variable "ONLINE_STATUS" "OFFLINE"
verbose "Hosts offline"
""")
        out.close()

    def test_openport(self):
        self.assert_(online.openport("localhost", 22))
        self.assertFalse(online.openport("localhost", 23))
        self.assert_(online.openport("www.google.com", 22))

if __name__ == "__main__":
    unittest.main()
