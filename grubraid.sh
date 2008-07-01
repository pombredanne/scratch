#!/bin/sh
# Install GRUB on your drive.
#   Copyright (C) 1999,2000,2001,2002,2003,2004 Free Software Foundation, Inc.
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

set -e

# from grub-install
getraid_mdadm() {
	device=$1
	mdadm=$(mdadm -D "$device") || {
		echo "$PROG: mdadm -D $device failed" >&2
		exit 1
	}
	eval "$(
		echo "$mdadm" | awk '
			$1 == "Number" && $2 == "Major" { start = 1; next }
			$1 == "UUID" { print "uuid=" $3; start = 0; next }
			!start { next }
			$2 == 0 && $3 == 0 { next }
			{ devices = devices "\n" $NF }
			END { print "devices='\''" devices "'\''" }
		'
	)"

	# Convert RAID devices list into a list of disks
	tmp_disks=`echo "$devices" | sed -e 's%\([sh]d[a-z]\)[0-9]*$%\1%' \
					 -e 's%\(d[0-9]*\)p[0-9]*$%\1%' \
					 -e 's%\(fd[0-9]*\)$%\1%' \
					 -e 's%/part[0-9]*$%/disc%' \
					 -e 's%\(c[0-7]d[0-9]*\).*$%\1%' \
					 -e '/^$/d' |
				     sed -n '1h;2,$H;${g;s/\n/ /g;p}'`
     
    echo $tmp_disks
}


getraid_sysfs() {
    local device="$(basename $1)"
    ls -1 /sys/block/"$device"/slaves
}

    
install_grubraid() {
    for device in "$@"; do
        echo "device (hd0) $device"
        echo "root (hd0,0)"
        echo "setup (hd0)"
    done | grub --batch --no-floppy 
}



install_grubraid $(getraid_mdadm "$1")

# see also 
# http://gentoo-wiki.com/HOWTO_Gentoo_Install_on_Software_RAID#Installing_Grub_onto_both_MBRs


