#!/usr/bin/python

import cProfile
import errno
import os
import sys


def create_file(basename):
    for i in range(100):
        filename = "%s.pstats.%03d" % (basename, i)
        try:
            fd = os.open(filename, os.O_EXCL|os.O_CREAT)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        else:
            os.close(fd)
            return filename
    else:
        sys.exit("delete some %s.pstats.* files" % basename)


if __name__ == "__main__":
    target = sys.argv[1]
    filename = create_file(os.path.basename(target))
    sys.argv.pop(0)
    cProfile.run("execfile(%r)" % target, filename)
