#!/usr/bin/python

import os
import sys

import gtk
import vte


def vte_commit(term, arg1, arg2):
    if arg1 == "\r":
        gtk.main_quit()


def on_child_exit(term):
    status = term.get_child_exit_status()
    if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
        gtk.main_quit()
    else:
        term.connect("commit", vte_commit)


if __name__ == "__main__":
    term = vte.Terminal()
    term.connect("child-exited", on_child_exit)
    term.fork_command(sys.argv[1], sys.argv[1:])
    window = gtk.Window()
    window.add(term)
    window.connect("delete-event", lambda window, event: gtk.main_quit())
    window.show_all()
    gtk.main()

