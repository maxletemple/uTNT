#!/bin/bash
RESULTDIR=${1:-"../../results/deploy"}
TAP=${2:-"virbr0"}

die () {
    echo "$1"
    exit 1
}

wget https://people.montefiore.uliege.be/gain/public/app-utnt_qemu-x86_64 &> /dev/null || die "wget failed"
echo "t0: $(($(date +%s%N) / 1000000))" 1>> "$RESULTDIR/utnt_output.txt"
sudo /usr/bin/time -v qemu-system-x86_64 -s -netdev bridge,id=en1,br="$TAP" -device virtio-net-pci,netdev=en1 -device isa-debug-exit -kernel "app-utnt_qemu-x86_64" -append "netdev.ipv4_addr=10.0.122.2 netdev.ipv4_gw_addr=10.0.122.1 netdev.ipv4_subnet_mask=255.255.255.0 -- 10.0.122.2 sc_tnt -i 1.1.1.1 -p 12345 -o out.warts" -cpu host --enable-kvm -m 8 -no-acpi -display none -nographic 1>> "$RESULTDIR/utnt_output.txt" 2>> "$RESULTDIR/utnt_run_time.txt"
rm app-utnt_qemu-x86_64  &> /dev/null || die "wget failed"