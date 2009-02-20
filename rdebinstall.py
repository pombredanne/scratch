
import subprocess
import os
import optparse


def dpkg_parsechangelog(fields, dirname):
    cmd = ["dpkg-parsechangelog"]
    f = subprocess.Popen(cmd, cwd=dirname, stdout=subprocess.PIPE).stdout
    values = {}
    for line in f:
        for field in fields:
            if line.startswith("%s: " % field):
                values[field] = line.split()[1]
    if len(values) == 0: 
        raise RuntimeError("fields %s not found in debian/changelog" % fields)
    else:
        return values


def get_debian_host_arch():
    cmd = ["dpkg-architecture", "-qDEB_HOST_ARCH"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().rstrip()


def find_deb_in_path(name, version, files):
    """
    >>> find_deb_in_path("bash", "3.2", ["a", "bash_3.2_i386.deb",
    ...    "bash_3.2_all.deb"]) 
    'bash_3.2_all.deb'
    """
    inarch_name = "%s_%s_all.deb" % (name, version)
    if inarch_name in files:
        return inarch_name
    arch_name = "%s_%s_%s.deb" % (name, version, get_debian_host_arch())
    if arch_name in files:
        return arch_name
    raise RuntimeError("couldn't find deb %s" % files)


def upload(dirpath, package_dir, name, target):
    fields = dpkg_parsechangelog(["Source", "Version"], package_dir)
    version = fields["Version"]
    if ":" in version:
        version = version.split(":", 1)[1]
    if name is None:
        name = fields["Source"]

    filename = find_deb_in_path(name, version, os.listdir(dirpath))
    filepath = os.path.join(dirpath, filename)
    subprocess.call(["scp", filepath, "%s:" % target])
    subprocess.call(["ssh", target, "dpkg", "-i", filename])


def main():
    parser = optparse.OptionParser("""\
%prog dest [name]

upload deb to dest
""")
    parser.add_option("--build-area", dest="build_area",
        help="Directory to find build files, defaults to ..",
        default="..")
    parser.add_option("--dir", dest="dir",
        help="Package directory, defaults to .",
        default=".")
    opts, args = parser.parse_args()
    if len(args) not in (1, 2):
        parser.error("Invalid number of arguments")
    if len(args) > 1:
        name = args[1]
    else:
        name = None
        
    
    upload(opts.build_area, opts.dir, name, args[0])
    

if __name__ == '__main__':
    main()

