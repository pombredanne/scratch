#!/bin/bash

LOG="$HOME/papscan.log"

#SHELL="/bin/bash -x"
SHELL="/bin/bash"

while true; do
  setleds +num
  read -sn 1 INPUT_KEY
  $SHELL "$(dirname $0)/scan.sh" "$INPUT_KEY" 2>&1 \
    | tee -a "$LOG"
  printf "\a"
done



