#!/usr/bin/python

from __future__ import print_function

import collections
import datetime
import distutils.dir_util
import os

BASEDIR = os.path.expanduser("~/pan")

# 2009-05-24 21:25:51,916 gnome-terminal fish  ~/src/netbeans

# 2009-05-24 12:06:07,011 gthumb sdskljdf3-nmd.jpg  (2/2730)
def parse_line(parts):
    """
    >>> parse_line("2009-05-24 12:06:07,011 gthumb sdskljdf3-nmd.jpg  (2/2730)")
    datetime.datetime(2009, 5, 24, 12, 6, 7), 'gthumb', 'sdskljdf3-nmd.jpg  (2/2730)'
    """
    try:
        date, time_, name, title = parts
        dt = datetime.datetime.strptime("%s %s" % (date, time_.split(",", 1)[0]),
            "%Y-%m-%d %H:%M:%S")
        return dt, name, title
    except:
        print(parts)
        raise


def parse_title(title):
    """
    >>> parse_title("sdskljdf3-nmd.jpg  (2/2730)")
    'sdskljdf3-nmd.jpg'
    """
    return title.rsplit("  ", 1)[0]


# read file in reverse
# filename -> last access time

def main():
    d = collections.defaultdict(lambda: datetime.datetime.utcfromtimestamp(0))
    for line in open(os.path.expanduser("~/.wnck.log")):
        parts = line.split(" ", 3)
        if len(parts) > 2 and parts[2] == "gthumb":
            time_, name, title = parse_line(parts)
            filename = parse_title(title)
            if filename is not None:
                d[filename] = max(d[filename], time_)
    cutoff = datetime.datetime.now() - datetime.timedelta(days=60)
    for time_, filename in sorted((value, name) for name, value in d.iteritems()):
        if time_ < cutoff:
            filepath = os.path.join(BASEDIR, filename)
            if os.path.exists(filepath):
                dest = os.path.join(BASEDIR, "%04d%02d" %
                    (time_.year, time_.month), filename)
                distutils.dir_util.mkpath(os.path.dirname(dest))
                os.rename(filepath, dest)
                #print("mv %s %s" % (filename, dest))

if __name__ == "__main__":
    main()
