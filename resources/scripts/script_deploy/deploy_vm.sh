#!/bin/bash
RESULTDIR=${1:-"../results/deploy"}

die () {
    echo "$1"
    exit 1
}

echo "t0: $(($(date +%s%N) / 1000000))" 1>> "$RESULTDIR/vm_output.txt"
/usr/bin/time -v vagrant up --provision 1>> "$RESULTDIR/vm_output.txt" 2>> "$RESULTDIR/vm_run_time.txt"
vagrant halt &> /dev/null || die "vagrant halt failed"
vagrant destroy -f  &> /dev/null || die "vagrant destroy failed"
vagrant box list | cut -f 1 -d ' ' | xargs -L 1 vagrant box remove -f &> /dev/null

#wget https://vagrantcloud.com/generic/boxes/ubuntu1604/versions/4.2.16/providers/libvirt.box &> /dev/null || die "wget failed"
#rm libvirt.box &> /dev/null || die "rm failed"