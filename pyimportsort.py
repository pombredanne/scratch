#!/usr/bin/python

import StringIO
import ast
import optparse
import re
import unittest


UNSORTED = """
import sys
import os.path
from string import letters

import optparse
import subprocess

print "a line"

''' a docstring '''
import re

"""

SORTED = """
from string import letters
import os.path
import sys

import optparse
import subprocess

print "a line"

''' a docstring '''
import re

"""


class Test(unittest.TestCase):
    
    def test(self):
        self.assertEqual(importsort(StringIO.StringIO(UNSORTED)), SORTED)


class ImportFinder(ast.NodeVisitor):
    
    def __init__(self):
        self.ranges = []

    def visit_Import(self, node):
        lineno = node.lineno - 1 # ast is 1 indexed
        if len(self.ranges) == 0 or self.ranges[-1][-1] != lineno - 1:
            self.ranges.append([lineno, lineno])
        else:
            self.ranges[-1][-1] = lineno
        
    def visit_ImportFrom(self, node):
        self.visit_Import(node)


def importsort(f):
    data = f.read()
    node = ast.parse(data)
    import_finder = ImportFinder()
    import_finder.visit(node)
    lines = data.split("\n")
    for start, end in import_finder.ranges:
        end += 1
        lines[start:end] = sorted(lines[start:end])
    return "\n".join(lines)

    
if __name__ == "__main__":
#    unittest.main()
    parser = optparse.OptionParser()
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("Need input file")
    try:
        f = open(args[0], "r+")
    except IOError:
        parser.error('Couldn\'t open "%s"' % args[0])
    else:
        try:
            sorted_f = importsort(f)
            f.seek(0)
            f.write(sorted_f)
        finally:
            f.close()

