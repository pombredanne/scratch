#!/bin/bash

LOG="$HOME/papscan.log"

SHELL="/bin/bash"
SHELL="/bin/bash -x"

# easiest way of passing absolute path to scan.sh
cd "$(dirname $0)"

while true; do
  #setleds +num
  read -sn 1 INPUT_KEY
  $SHELL $PWD/scan.sh "$INPUT_KEY" 2>&1 \
    | tee -a "$LOG"
  printf "\a"
done



