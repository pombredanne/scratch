#!/usr/bin/python

import optparse
import os
import tempfile

def main():
    parser = optparse.OptionParser("%prog target")
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("Incorrect argument")
    target = args[0]
    if os.path.isfile(target):
        basename = os.path.basename(target)
        tempdir = tempfile.mkdtemp(prefix=basename, dir=os.path.dirname(target))
        temppath = os.path.join(tempdir, basename)
        os.rename(target, temppath)
        os.mkdir(target)
        os.rename(temppath, os.path.join(target, basename))
        os.rmdir(tempdir)
    else:
        parser.error("Invalid argument")

if __name__ == "__main__":
    main()

