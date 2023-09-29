#!/bin/bash
RESULTDIR=${1:-"../results/deploy"}

die () {
    echo "$1"
    exit 1
}

docker pull gaulthiergain/scamper_tnt:0.1 &> /dev/null || die "docker pull failed"
echo "t0: $(($(date +%s%N) / 1000000))" 1>> "$RESULTDIR/docker_output.txt"
/usr/bin/time -v docker run --rm --name scamper -v /tmp:/tmp gaulthiergain/scamper_tnt:0.1 1>> "$RESULTDIR/docker_output.txt" 2>> "$RESULTDIR/docker_run_time.txt"
docker image rm gaulthiergain/scamper_tnt:0.1 &> /dev/null || die "docker image rm failed"