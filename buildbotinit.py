
import sys
import subprocess
import ConfigParser
import pwd
import os


class Init(object):

    def __init__(self, prefixcmd=None, basedir=None, options=None, user=None):
        self.daemon = "/usr/bin/buildbot"
        self.prefixcmd = prefixcmd
        self.basedir = basedir
        self.options = options
        self.user = user

    def run(self, command):
        bb_cmd = [self.daemon, command, self.basedir]
        if self.options is not None:
            bb_cmd.append(self.options)
        cmd = []
        if self.prefixcmd is not None:
            cmd = self.prefixcmd.split()
        cmd.extend(["su", "-s", "/bin/sh", "-c", " ".join(bb_cmd), "-",
            self.user])
        print cmd

    def start(self):
        self.run("start")
        
    def stop(self):
        self.run("stop")
        
    def restart(self):
        self.run("restart")

    def reload(self):
        self.run("sighup")


class InitGroup(object):
    
    def __init__(self, inits):
        self.inits = inits
        
    @classmethod
    def make_from_config(cls, config_parser, sections):
        inits = []
        for section in sections:
            kwargs = dict(config_parser.items(section))
            try:
                inits.append(Init(**kwargs))
            except TypeError, e:
                sys.exit('Invalid section "%s": %s' % (section, e))
        return cls(inits)

    def run(self, command):
        if command in ("start", "stop", "restart", "reload"):
            for init in self.inits:
                getattr(init, command)()
        else:
            sys.exit('Unknown command "%s"' % command)


def main(args):
    if len(args) in (2, 3):
        config_filepath = args[0]
        command = args[1]
        if len(args) == 3:
            section = args[2]
        else:
            section = None
        cp = ConfigParser.SafeConfigParser()
        cp.read(config_filepath)
        if section is not None:
            InitGroup.make_from_config(cp, [section]).run(command)
        else:
            InitGroup.make_from_config(cp, cp.sections()).run(command)
    else:
        sys.exit("Usage: builtbotinit config command [section]")


if __name__ == "__main__":
    main(sys.argv[1:])
