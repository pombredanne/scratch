#!/usr/bin/python

import getpass
import sys
import optparse

import keyring
import pexpect

PASSWORD_KEY = 'ecryptfsstarter'

def main():
    parser = optparse.OptionParser('%prog host')
    parser.add_option('--set-password', dest='set_password', action='store_true')
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('Incorrect arguments')
    host = args[0]
    
    if options.set_password:
        password = getpass.getpass('EcryptFS password: ')
        keyring.set_password(PASSWORD_KEY, host, password)
    else:
        password = keyring.get_password(PASSWORD_KEY, host)
        if password is None:
           parser.error('password not set, run with --set-password first')
        child = pexpect.spawn('ssh', ['-t', host, 'sudo', 'cehill-ecryptfs-start'])
        child.logfile_read = sys.stdout
        child.expect('Passphrase:')
        child.sendline(password)
        child.wait()


if __name__ == '__main__':
    main()
