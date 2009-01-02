#!/usr/bin/python
# search.cgi - a cmxml search script
# Copyright (C) 2006 C.E. Hill & Co. (UK) Ltd. (tristan@cehill.co.uk)
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

import cgi
#import cgitb; cgitb.enable()
import csv
import math
import os
import sys


class CsvDirectory(object):
    """
    csv file format:
    "0123456789","A Name"
     (without "" seems to work aswell)
    """
    def __init__(self, filename):
        self.entries = []
        for row in csv.reader(file(filename)):
            try:
                self.entries.append((row[1], row[0]))
            except IndexError:
                pass

    def search(self, query):
        query = query.lower()
        if query == ".":
            return self.entries
        matches = []
        for name, number in self.entries:
            if name.lower()[:len(query)] == query:
                matches.append((name, number))
        return matches


def getmatches(filename, query, page):
    try:
        allmatches = CsvDirectory(filename).search(query)
        num_of_pages = int(math.ceil(float(len(allmatches)) / MAX_PAGE_ENTRIES))
        next_page = page + 1
        if next_page == num_of_pages:
            next_page = 0
        matches = allmatches[MAX_PAGE_ENTRIES*page:MAX_PAGE_ENTRIES*(page+1)]
        return matches, next_page, num_of_pages, len(allmatches)
    except IOError, e:
        OUT.write("Content-type: text/xml\n\n")    
        OUT.write("<!-- I/O error(%s): %s -->\n" % e)
        sys.exit(0)


def search(filename, query, page):
    matches, next_page, num_of_pages, total_entries = getmatches(filename,
                                                                 query, page)
    OUT.write("Refresh: 0; url=%s?query=%s&page=%d\n" % \
              (SCRIPT_URL, query, next_page))
    OUT.write("Content-type: text/xml\n\n")
    OUT.write("<CiscoIPPhoneDirectory>\n")
    OUT.write("  <Title>Search results</Title>\n")
    if len(matches) == 1:
        OUT.write("  <Prompt>page 1 of 1 (1 entry)</Prompt>\n")
    elif num_of_pages == 1:
        OUT.write("  <Prompt>page 1 of 1 (%d entries)</Prompt>\n" %
                  len(matches))
    else:
        OUT.write("  <Prompt>page %d of %d (%d entries)</Prompt>\n" %
                  (page+1, num_of_pages, total_entries))
    for name, number in matches:
        OUT.write("  <DirectoryEntry>\n")
        OUT.write("    <Name>%s</Name>\n" % cgi.escape(name))
        OUT.write("    <Telephone>%s</Telephone>\n" % cgi.escape(number))
        OUT.write("  </DirectoryEntry>\n")
    OUT.write("</CiscoIPPhoneDirectory>\n")


def query(form, filename):
    if "query" in form:
        query = form.getfirst("query")
        page = int(form.getfirst("page"))
        search(filename, query, page)
    else:
        OUT.write("""Content-type: text/xml\n
<CiscoIPPhoneInput>
    <Title>Search</Title>
<!--  <Prompt>Enter the first three letters</Prompt> -->
    <URL>%s</URL>
    <InputItem>
        <DisplayName>Name </DisplayName>
        <QueryStringParam>query</QueryStringParam>
        <DefaultValue></DefaultValue>
        <InputFlags>A</InputFlags>
    </InputItem>
    <InputItem>
        <QueryStringParam>page</QueryStringParam>
        <DefaultValue>0</DefaultValue>
    </InputItem>
</CiscoIPPhoneInput>
""" % SCRIPT_URL)


if __name__ == "__main__":
    OUT = sys.stdout
    SCRIPT_URL = "http://%s%s" % (os.environ["HTTP_HOST"],
                                  os.environ["SCRIPT_NAME"])
    MAX_PAGE_ENTRIES = 32                                 
    form = cgi.FieldStorage()
    query(form, "/home/fs/cehillco/admin/telephone/list/directory.csv")

