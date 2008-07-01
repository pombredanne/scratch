#!/bin/sh

TMP="$(mktemp dotview.XXXXXX)"
trap "rm -f $TMP" EXIT
dot -Tsvg > "$TMP"
eog "$TMP"

