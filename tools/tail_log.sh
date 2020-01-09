#!/usr/bin/env bash

DOMAIN=$1
FILENAME=$2

./exec_in_container.sh $DOMAIN "tail -f /usr/share/docassemble/log/$FILENAME"
