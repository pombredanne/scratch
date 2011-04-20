#!/usr/bin/python

import optparse
import sys
import time

import gobject
import gtk
import hamster.keybinder as keybinder 
import wnck


BINDINGS = [("<Super>1", "chromium-browser"),
            ("<Super>2", "Terminal"),
            ("<Super>3", "."), # eclipse
            ("<Super>4", "gedit"),
           ] 


windows = []


def window_opened(window, data):
    windows.append(window)


def window_closed(window, data):
    windows.remove(window)


def get_workspace_windows(screen):
    active_workspace = screen.get_active_workspace() # workspace stuff doesn't
    # work with compiz?
    for window in reversed(screen.get_windows_stacked()):
        if window.is_on_workspace(active_workspace):
            yield window
        

def on_keybinding_activated((screen, name)):
    for window in get_workspace_windows(screen):
        if window.get_application().get_name() == name:
            window.activate(int(time.time()))
            return


def list_windows(screen):
    print screen.get_workspaces()
    for window in get_workspace_windows(screen):
        if window.get_window_type() == wnck.WINDOW_NORMAL:
            print window.get_application().get_name(), window.get_workspace().get_name()

    gtk.main_quit()


def main():
    parser = optparse.OptionParser()
    parser.add_option("--list", action="store_true")
    options, args = parser.parse_args()
    screen = wnck.screen_get_default()
    if options.list:
        gobject.idle_add(list_windows, screen)
    else:
        global windows
#        windows = screen.get_windows()
#        screen.connect("window-opened", window_opened)
#        screen.connect("window-closed", window_closed)
        for key, name in BINDINGS:
            keybinder.bind(key, on_keybinding_activated, (screen, name))
    gtk.main()


if __name__ == "__main__":
    main()
