
#papscan - a scanner script
#Copyright (C) 2004 Tristan Hill (tristan@cehill.co.uk)
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA

function die {
  echo 1>2 "$@"
  exit 1
}

function my_scanadf() {
  execheck scanadf which sort tr || exit 1

  local opts
  local j=0
#  opt=""
  for i in "$@"; do
    if [ "$i" == "--source" ]; then
      source="next"
    elif [ "$source" == "next" ]; then
      source="$i"
      opt="$opt --source \"'$source'\""
      opts[$((j++))]=--source
      opts[$((j++))]="$source"
    elif [ "$i" == "--duplex" ]; then
      duplex="next"
    elif [ "$duplex" == "next" ]; then
      duplex="$i"
      opt="$opt --duplex $duplex"
    elif [ "$i" == "--pdfgroup" ]; then
      pdfgroup="next"
    elif [ "$pdfgroup" == "next" ]; then
      pdfgroup="$i"
    elif [ "$i" == "--scan-script" ]; then
      script="next"
    elif [ "$i" == "-S" ]; then
      script="next"
    elif [ "$script" == "next" ]; then
      execheck $i || die "scan-script not found"
      script="$(which $i)"
      opt="$opt --scan-script $script"
      opts[$((j++))]=--scan-script
      opts[$((j++))]="$script"
    else
      opt="$opt $i"
      opts[$((j++))]="$i"
    fi
  done
 
  if [ "$source" == "next" ]; then
    die "$FUNCNAME: --source missing argument"
  fi
  if [ "$duplex" == "next" ]; then
    die "$FUNCNAME: --duplex missing argument"
  fi
  if [ "$pdfgroup" == "next" ]; then
    die "$FUNCNAME: --pdfgroup missing argument"
  fi

  # exported for adf page count incrementer
  export source
  export duplex

  if [ -z "$(echo $opt | grep scan-script)" ]; then
    opt="$opt --scan-script $(which scan-script)"
    opts[${#opts}]=--scan-script
    opts[${#opts}]="$(which scan-script)"
  fi

#  scanadf $opt -x 210 -y 297 -o "%d" --script-wait
  scanadf "${opts[@]}" -x 210 -y 297 -o "%d" --script-wait

  if [ $? != 0 ]; then
    if [ -n "$SCSI_PROBE" ]; then
      $SCSI_PROBE
    fi
    die "$FUNCNAME: scanadf failed"
  fi

  if [ "$pdfgroup" == "group" ]; then
    renamekeepext $(pdfgroup $(ls *.pdf | sort -n | tr '\n' ' ')) $FILE_PREFIX
  else
    renamekeepext *.pdf $FILE_PREFIX
  fi
}

function scsi_probe {
  echo "scsi add-single-device $1 $2 $3 $4" > /proc/scsi/scsi
  die "scsi probed, please try again"
}

CONFIG="$(dirname $0)/config.sh"
PRESET=$1

if [ $# -lt 1 ]; then
 die "Usage: $0 preset"
fi

if [ ! -f $CONFIG ]; then
  die "Couldn't load configuration"
fi

TEMP="$(mktemp -d)"
trap "rm -rf $TEMP" EXIT

cd $TEMP || die "Couldn't change to temporary directory"

BASEDIR="$(dirname $0)"
export PATH="$BASEDIR/bin:$PATH"

# now do the real work based on the config presets
source "$CONFIG"

