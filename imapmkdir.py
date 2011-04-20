#!/usr/bin/python

import imaplib
import optparse
import pprint

def main():
    username, password = raw_input().split(':')
    parser = optparse.OptionParser('%prog server mailbox ...')
    options, args = parser.parse_args()
    if len(args) == 0:
        parser.error('Incorrect arguments')
    conn = imaplib.IMAP4_SSL(args[0])
    conn.login(username, password)
    pprint.pprint(conn.list())
    for mailbox in args[1:]:
        conn.create(mailbox)


if __name__ == '__main__':
    main()

