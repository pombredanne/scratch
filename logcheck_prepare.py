#!/usr/bin/python

# Feb  5 19:02:05 tiber sshd[15413]: Received disconnect from 192.168.201.6: 11: disconnected by user
import re
import sys

def main():
    out = []

    for line in sys.stdin:
        m = re.match(r"^\w{3} [ :0-9]{11} [\w._-]+ (\w+)(\[\d+\])?: (.*)", line)
        if m:
            if m.group(2):
            	pid_re = r"\[[[:digit:]]+\]"
            else:
            	pid_re = ""
            out.append(r"^\w{3} [ :0-9]{11} [._[:alnum:]-]+ %s%s: %s$" % (m.group(1), pid_re, m.group(3)))

    print "\n".join(out)


if __name__ == "__main__":
    main()

