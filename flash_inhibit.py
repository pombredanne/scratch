#!/usr/bin/python

import os
import subprocess
import sys
import time

import gtop


flash_process_time = None
FLASH_ACTIVE_TIME = 50

def is_flash(pid):
    for arg in gtop.proc_args(pid):
        if arg.endswith("/libflashplayer.so"):
            return True
    return False        


def flash_running():
    global flash_process_time
    flash_process_times = []
    for pid in gtop.proclist(gtop.PROCLIST_EXCLUDE_SYSTEM | 
                             gtop.PROCLIST_KERN_PROC_UID, os.getuid()):
        if is_flash(pid):
            flash_pid = pid
            flash_process_times.append(gtop.proc_time(pid).dict()["rtime"])
    if flash_process_times:
        old_flash_process_time = flash_process_time
        flash_process_time = max(flash_process_times)
        if old_flash_process_time:
            return flash_process_time - FLASH_ACTIVE_TIME > old_flash_process_time        
    return False


def main():
    p = None
    try:
        while True:
            now_running = flash_running()
            if now_running and p is None:
                 p = subprocess.Popen(["gnome-screensaver-command", "-i"])
                 print "starting screensaver inhibit"
            elif not now_running and p is not None:
                 p.kill()
                 p.wait()
                 p = None
                 print "stopping screensaver inhibit"
            time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        if p is not None:
            p.kill()


if __name__ == "__main__":
    main()



