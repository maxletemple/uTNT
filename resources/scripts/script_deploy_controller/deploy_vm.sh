#!/bin/bash

die () {
    echo "$1"
    exit 1
}

echo "t0: $(($(date +%s%N) / 1000000))"
vagrant up --provision
vagrant halt
vagrant destroy -f
vagrant box list | cut -f 1 -d ' ' | xargs -L 1 vagrant box remove -f
