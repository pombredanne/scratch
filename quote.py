#!/usr/bin/python

import sys
import textwrap


def main():
    for wrapped_lines in textwrap.wrap(sys.stdin.read(), replace_whitespace=False):
        for line in wrapped_lines.split("\n"):
            sys.stdout.write("> %s\n" % line)


if __name__ == "__main__":
    main()


