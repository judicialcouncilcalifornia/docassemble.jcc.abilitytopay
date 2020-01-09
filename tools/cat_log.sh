#!/usr/bin/env bash

DOMAIN=$1
FILENAME=$2

./exec_in_container.sh $DOMAIN "cat /usr/share/docassemble/log/$FILENAME"
