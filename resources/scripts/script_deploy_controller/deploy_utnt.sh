#!/bin/bash
TAP=${2:-"virbr0"}

mkdir -p "$RESULTDIR"

die () {
    echo "$1"
    exit 1
}

sudo sysctl -w net.ipv4.ip_forward=1

sudo modprobe br_netfilter

sudo sysctl -p /etc/sysctl.conf
# Ensure IP tables does not prevent packets from being forwarded through the bridge
sudo sysctl -w net.bridge.bridge-nf-call-arptables=0
sudo sysctl -w net.bridge.bridge-nf-call-ip6tables=0
sudo sysctl -w net.bridge.bridge-nf-call-iptables=0

echo "allow all" | sudo tee /etc/qemu/bridge.conf

CHAIN_NAME="VIRBR0"
sudo brctl addbr virbr0

sudo ip link set dev virbr0 up
sudo ip addr add 10.0.122.1/24 dev virbr0

sudo iptables -t nat -N $CHAIN_NAME
sudo iptables -t nat -A $CHAIN_NAME -s 10.0.122.0/24 ! -d 10.0.122.0/24 -j MASQUERADE

sudo iptables -t nat -A POSTROUTING -j $CHAIN_NAME

wget http://letemple.fr/app-utnt_qemu-x86_64 || die "wget failed"
echo "t0: $(($(date +%s%N) / 1000000))"
echo "unikraft2023!" | sudo -S echo ""
sudo qemu-system-x86_64 -s -netdev bridge,id=en1,br="$TAP" -device virtio-net-pci,netdev=en1 -device isa-debug-exit -kernel "app-utnt_qemu-x86_64" -append "netdev.ipv4_addr=10.0.122.2 netdev.ipv4_gw_addr=10.0.122.1 netdev.ipv4_subnet_mask=255.255.255.0 -- 10.0.122.2 sc_tnt -i 10.0.122.1 -p 12345 -o out.warts" -cpu host --enable-kvm -m 8 -no-acpi -display none -nographic
rm app-utnt_qemu-x86_64  &> /dev/null || die "wget failed"
