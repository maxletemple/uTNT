#!/bin/bash
set -eu

send() {
    echo "$@"
    sleep 1
}

cmds() {
    sleep 8
    send student
    send student
    send echo "student" | sudo -S date > "/dev/null"
    send "shutdown now"
}

qemu-system-x86_64 -s -smp 4,sockets=4,cores=1,threads=1 -device isa-debug-exit -cpu host --enable-kvm -m 2048 -hda "$PWD/ubuntu16.04.qcow2" -nographic

# -fsdev local,security_model=passthrough,id=fsdev0,path=/tmp/share -device virtio-9p-pci,id=fs0,fsdev=fsdev0,mount_tag=hostshare