#!/usr/bin/python

import optparse
import subprocess
import time

import pyinotify


class Restarter(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.start()
        self.time_between_events = 1
        self.last_time = time.time()
        
    def start(self):
        self.p = subprocess.Popen(self.cmd)
        
    def process(self, event):
        print event
        if time.time() - self.last_time > self.time_between_events:
            print "Restarting"
            self.stop()
            self.start()
        self.last_time = time.time()

    def stop(self):
        self.p.terminate()
        tries = 10
        for i in range(tries):
            if self.p.poll() is not None:
                break
            time.sleep(0.1)
        else:
            self.p.kill()
        self.p.wait()


def main():
    parser = optparse.OptionParser("%prog dir -- cmd [cmdargs ...]")
    options, args = parser.parse_args()
    if len(args) < 2:
        parser.error("Insufficient arguements")

    wm = pyinotify.WatchManager()
    wm.add_watch(args[0], pyinotify.IN_MODIFY|pyinotify.IN_CREATE)

    restarter = Restarter(args[1:])
    notifier = pyinotify.Notifier(wm, restarter.process)
    try:
        notifier.loop()
    finally:
        restarter.stop()

if __name__ == "__main__":
    main()



