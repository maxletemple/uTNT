#!/bin/bash


#build
docker build -t scamper_tnt:0.1 .

#run
/usr/bin/time -v docker run --rm --name scamper_tnt -v /tmp/:/tmp/ scamper_tnt:0.1

docker image inspect docker.io/library/scamper_tnt:0.1 --format='{{.Size}}'
