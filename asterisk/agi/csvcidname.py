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

"""
agi script to lookup numbers in a csv file and set the name in the 
callerid if found
"""

import csv
import os
import sys


class CsvDirectory(object):

    # csv file format:
    #"0123456789","A Name"
    # (without "" seems to work aswell)

    def __init__(self, filename):
        self.entries = []
        for row in csv.reader(file(filename)):
            try:
                self.entries.append((row[1], row[0]))
            except IndexError:
                pass

    def lookup(self, query):
        if not isinstance(query, str):
            raise ValueError("need number in string format")
        for name, number in self.entries:
	    if number == query:
	        return name
        return None


def main(stdin, stdout, filename):
    if not os.path.exists(filename):
        stdout.write('verbose "couldn\'t find csv file %s"\n' % filename)
        return 1
    callerid = None
    # avoid for line in file's buffer
    while True:
        line = stdin.readline()
        if line == "\n":
            break
        elif line.startswith("agi_callerid: "):
            callerid = line[len("agi_callerid: "):].rstrip()
    if callerid:
        directory = CsvDirectory(filename)
        name = directory.lookup(callerid)
        if name != None:
            name = name.replace("<", "")
            name = name.replace(">", "")
            newcid = '%s<%s>' % (name, callerid)
            stdout.write('verbose "Changing CallerID to %s"\n' % newcid)
            stdout.write('set callerid "%s"\n' % newcid)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'verbose "need filename of csv file"\n'
        sys.exit(1)
    sys.exit(main(sys.stdin, sys.stdout, sys.argv[1]))

