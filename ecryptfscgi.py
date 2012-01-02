#!/usr/bin/python

import cgi
import os
import socket
import sys

import pexpect


def write_header():
    sys.stdout.write("""Content-type: text/html\n
<html>
<head><title>Unlock %s</title></head>
<body>
""" % socket.gethostname())


def write_page(contents):
    write_header()
    sys.stdout.write("""%s
</body>
</html>
""" % contents)


def unlock(form, is_unlocked, mount_script):
    if "password" in form:
        password = form.getfirst("password")
        if len(password) > 16: # sanity check
            write_header()
            sys.stdout.write("<pre>")
            child = pexpect.spawn("sudo", [mount_script])
            child.logfile_read = sys.stdout
            child.expect('Passphrase:')
            child.sendline(password)
            child.wait()
            sys.stdout.write("</pre></body></html>")
        else:
            write_page("<h2>Password too short</h2>")
    elif is_unlocked():
        write_page("<h2>Already Unlocked</h2>")
    else:
        write_page("""
<p>
Some folders on the file server remain encrypted until a password is supplied.  Enter that password and any username below.
<p />
<form method="POST">
Username: <input type="text" name="username" /> <br />
Password: <input type="password" name="password" />
<input type="submit" value="Unlock" />
</form>
""")


if __name__ == "__main__":
    form = cgi.FieldStorage()
    def is_unlocked():
        return not os.path.isdir("/home/.ecryptfs2/Private")
    unlock(form, is_unlocked, "cehill-ecryptfs-start")


