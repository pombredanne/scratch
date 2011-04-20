
#!/usr/bin/python

import datetime
import os
import sys


DURATION = datetime.timedelta(seconds=30)


def _parse_log_datetime(line):
    date_string, time_string, rest = line.split(" ", 2)
    return datetime.datetime.strptime("%s %s" % (date_string, time_string.split(",", 1)[0]), "%Y-%m-%d %H:%M:%S")


def readlog(filepath):
    f = open(filepath)
    previous_line = f.next()
    previous_datetime = _parse_log_datetime(previous_line)
    for line in f:
        datetime_ = _parse_log_datetime(line)
        yield previous_datetime, previous_line, datetime_, line
        previous_line = line
        previous_datetime = datetime_
    f.close()


def main():
    pass

    for previous_datetime, previous_line, current_datetime, current_line in readlog(os.path.expanduser(sys.argv[1])):
        if (current_datetime - DURATION) >= previous_datetime:
            print previous_line,


if __name__ == "__main__":
    main()


