#!/bin/bash
PATH_UTNT=${1:-"../../apps/uTNT/build/app-utnt_qemu-x86_64"}
PATH_VM=${2:-"../../../../unikraft/.vagrant.d/boxes/generic-VAGRANTSLASH-ubuntu1604/4.2.16/libvirt/box.img"}

source utils.sh

RESULTDIR="../results"
FILESIZE="size_all.csv"

echo "name;MB" > "$RESULTDIR/$FILESIZE"
{
    echo -n "docker;" 
    b=$(docker image inspect docker.io/gaulthiergain/scamper_tnt:0.1 --format='{{.Size}}')|| die "docker daemon is not running or image not found"
    echo $(( b / TO_MB ))
    echo -n "utnt;"
    b=$(stat "${PATH_UTNT}"|grep "Size:"|awk '{print $2}')
    echo "0.$(( b / TO_KB ))"
    echo -n "vm;"
    b=$(stat "${PATH_VM}"|grep "Size:"|awk '{print $2}')
    echo $(( b / TO_MB ))

} >> "$RESULTDIR/$FILESIZE"

echo "File size saved in $RESULTDIR/$FILESIZE"