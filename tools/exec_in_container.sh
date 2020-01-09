#!/usr/bin/env bash

DOMAIN=$1
COMMAND=$2

ssh azureuser@$DOMAIN 'bash -s' << EOF
CONTAINER_IMAGE_ID="\$(sudo docker ps --latest --quiet --filter 'status=running')"
sudo docker exec "\$CONTAINER_IMAGE_ID" /bin/bash -c "$COMMAND"
EOF
