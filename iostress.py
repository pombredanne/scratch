#!/usr/bin/python

import os
import pwd
import shutil
import signal
import tempfile


class AbcFile(object):

    def __init__(self, size):
        self._size = size

    def read(self, length):
        if self._size > 0:
            s = "abc"
            div, mod = divmod(length, len(s))
            self._size -= length
            return s * div + s[:mod]
        else:
            return None


def main():
    tempdir = tempfile.mkdtemp(dir=pwd.getpwuid(os.getuid()).pw_dir)
    try:
        shutil.copyfileobj(AbcFile(1 * 1024 * 1024), open(os.path.join(tempdir, "a"), "w"))
        pids = []
        for i in range(10):
            pid = os.fork()
            if pid == 0:
                while True:
                    shutil.copyfileobj(open(os.path.join(tempdir, "a")),
                        open(os.path.join(tempdir, str(i)), "w"))
            else:
                pids.append(pid)
        try:
            for pid in pids:
                os.waitpid(pid, 0)
        finally:
            for pid in pids:
                os.kill(pid, signal.SIGTERM)
    finally:
        shutil.rmtree(tempdir)



if __name__ == "__main__":
    main()
