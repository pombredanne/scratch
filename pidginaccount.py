#!/usr/bin/python

import optparse
import sys

import dbus


def main():
    parser = optparse.OptionParser("%prog account")
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("Only 1 argument")

    bus = dbus.SessionBus()
    obj = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
    purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

    for account in purple.PurpleAccountsGetAllActive():
        account_name = purple.PurpleAccountGetUsername(account)
        if args[0] in account_name:
            print "account %s disabled" % account_name
            purple.PurpleAccountSetEnabled(account, "gtk-gaim", False)


if __name__ == "__main__":
    main()


