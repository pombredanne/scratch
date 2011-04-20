#!/usr/bin/python

import sys

#import glib
#import gtk
import ctypes
import os
import subprocess


def main():
    argv = sys.argv[1:]
#    pid, stdin, stdout, stderr = glib.spawn_async(argv,
#        flags=glib.SPAWN_SEARCH_PATH|glib.SPAWN_DO_NOT_REAP_CHILD)
#    glib.child_watch_add(pid, lambda pid, condition: gtk.main_quit())
    
#    import warnings
#    warnings.filterwarnings('error')
    
#    gtk.main()
    
    libx11 = ctypes.cdll.LoadLibrary("libX11.so.6")
    display = libx11.XOpenDisplay(os.environ["DISPLAY"])
    ERROR_HANDLER = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_int))
    
    p = subprocess.Popen(argv)
    def py_error_handler(display):
        p.terminate()
        p.wait()
        print "error handler"
#        sys.exit(0)
        return 0
    error_handler = ERROR_HANDLER(py_error_handler)
    libx11.XSetIOErrorHandler(error_handler)
    while True:
        libx11.XNextEvent(display, None)
#    raw_input()

#    import socket
#    s = socket.socket(socket.AF_UNIX)
#    s.connect("/tmp/.X11-unix/X0")
#    import select
#    print select.select([], [], [s])
#    raw_input()
    
    
if __name__ == "__main__":
    main()


