#!/usr/bin/env bash

DOMAIN=$1

./exec_in_container.sh $DOMAIN "ls /usr/share/docassemble/log"
