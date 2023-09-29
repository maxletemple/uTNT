#!/bin/bash

die () {
    echo "$1"
    exit 1
}

docker pull gaulthiergain/scamper_tnt:0.1
echo "t0: $(($(date +%s%N) / 1000000))"
echo ""
docker run --rm --name scamper -v /tmp:/tmp gaulthiergain/scamper_tnt:0.1
docker image rm gaulthiergain/scamper_tnt:0.1 & 
pid=$!
wait $pid
echo "end"
exit 0