#!/usr/bin/python

"""%prog svn://example.org/trunk project/subproject

export svn://example.org/trunk/project/subproject to project/subproject 
i.e. keep directory structure
"""


import os
import subprocess
import sys

if __name__ == '__main__':
    svn_root = sys.argv[1]
    path = sys.argv[2]
    subprocess.call(["svn", "export", os.path.join(svn_root, path), path])
