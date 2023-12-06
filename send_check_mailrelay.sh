#!/bin/bash

EPOCH=$(date +%s)
FROM=$1
RECIPIENT=$2
TAG=JP-RELAY-TEST
BODY="$TAG to (${RECIPIENT}:${EPOCH})"

USAGE="USAGE: send_check_mailrelay.sh [FROM] [RECIPIENT]"

if [[ -z "$FROM" || -z "$RECIPIENT" ]]; then
    echo $USAGE
    exit 1
fi


echo "$BODY" | mail -r "$FROM" -s "$BODY" "$RECIPIENT"
