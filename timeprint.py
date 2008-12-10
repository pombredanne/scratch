#!/usr/bin/python

import os
import stat
import sys
import time


def nice_time(t):
    return time.strftime("%Y%m%d-%H%M%S", time.gmtime(t))


if __name__ == "__main__":
    for root, dirs, files in os.walk(sys.argv[1]):
        for name in files:
	    path = os.path.join(root, name)
	    print nice_time(os.stat(path)[stat.ST_MTIME]), path


