
import urllib2
from BeautifulSoup import BeautifulSoup
import subprocess

# dpkg-query -W -f '${Source} ${Status}\n' | grep '^[^ ].*installed' | cut -f1 -d' ' | sort -u
# dpkg-query -W -f '${Source} ${Packages}\n'
if __name__ == "__main__":
    response = urllib2.urlopen("http://udd.debian.org/bugs.cgi?release=wheezy&merged=ign&fnewerval=7&rc=1&sortby=source&sorto=asc")
    html = response.read()
#    html = open('/home/stan/Downloads/Debian Bugs Search @ UDD.html').read()
    soup = BeautifulSoup(html)

    table = soup.findAll("table", "buglist")[2]
    rc_packages = set()
    for row in table.findAll("tr")[1:]:
        package = row.findAll("a")[-1].text
        if package.startswith("src:"):
            package = package[len("src:"):]
        rc_packages.add(package)

    # dpkg-query seems funny - dpkg-query on xml-core shows as having no source package??
    p = subprocess.Popen(["dpkg-query", "-W", "-f", "${Source} ${Package} ${Status}\n"], stdout=subprocess.PIPE)
    installed_packages = set()
    for line in p.stdout:
        if "installed" in line:
            if line.startswith(" "):
                line = line[1:]
            installed_packages.add(line.split(' ', 1)[0])
    
    print "\n".join(sorted(installed_packages.intersection(rc_packages)))

