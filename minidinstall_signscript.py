#!/usr/bin/python

import os
import subprocess
import sys

try:
    os.unlink("Release.gpg")
except OSError:
    pass
subprocess.check_call(["gpg", "--armor", "--detach-sign", "-o", "Release.gpg",
    sys.argv[1]])

#, "--secret-keyring", "~/archive.gpg",


