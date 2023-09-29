#!/bin/bash
set -e

POSITIONAL_ARGS=()

CREATE_INTERFACE=false
CLEAN_INTERFACE=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --create)
      CREATE_INTERFACE=true
      shift # past argument
      ;;
    --clean)
      CLEAN_INTERFACE=true
      shift # past argument
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

CHAIN_NAME=$(echo "$1" | awk '{print toupper($0)}')

if [ $CLEAN_INTERFACE = true ]; then
    sudo ip link set dev $1 down
    sudo brctl delbr $1

    sudo iptables -t nat -D POSTROUTING -j $CHAIN_NAME
    sudo iptables -t nat -F $CHAIN_NAME
    sudo iptables -t nat -X $CHAIN_NAME

    exit 0
fi

if [ $CREATE_INTERFACE = true ]; then
    sudo sysctl -w net.ipv4.ip_forward=1

    sudo modprobe br_netfilter
    sudo sysctl -p /etc/sysctl.conf
    # Ensure IP tables does not prevent packets from being forwarded through the bridge
    sudo sysctl -w net.bridge.bridge-nf-call-arptables=0
    sudo sysctl -w net.bridge.bridge-nf-call-ip6tables=0
    sudo sysctl -w net.bridge.bridge-nf-call-iptables=0

    echo "allow all" | sudo tee /etc/qemu/bridge.conf

    sudo brctl addbr $1

    sudo ip link set dev $1 up
    sudo ip addr add 10.0.122.1/24 dev $1

    sudo iptables -t nat -N $CHAIN_NAME
    sudo iptables -t nat -A $CHAIN_NAME -s 10.0.122.0/24 ! -d 10.0.122.0/24 -j MASQUERADE

    sudo iptables -t nat -A POSTROUTING -j $CHAIN_NAME

fi

echo "t0=$(($(date +%s%N) / 1000000))"
#sudo qemu-system-x86_64 -s -netdev bridge,id=en1,br=$1 -device virtio-net-pci,netdev=en1 -device isa-debug-exit -kernel "build/app-utnt_qemu-x86_64" -append "netdev.ipv4_addr=10.0.122.2 netdev.ipv4_gw_addr=10.0.122.1 netdev.ipv4_subnet_mask=255.255.255.0 -- 10.0.122.2 sc_tnt -i 1.1.1.1 -p 12345 -o out.warts" -cpu host --enable-kvm -m 16 -no-acpi -display none -nographic -fsdev local,id=myid,path=$(pwd)/fs0,security_model=none -device virtio-9p-pci,fsdev=myid,mount_tag=fs0,disable-modern=on,disable-legacy=off
sudo qemu-system-x86_64  -s -netdev bridge,id=en1,br=$1 -device virtio-net-pci,netdev=en1 -device isa-debug-exit -kernel "build/app-utnt_qemu-x86_64" -append "netdev.ipv4_addr=10.0.122.2 netdev.ipv4_gw_addr=10.0.122.1 netdev.ipv4_subnet_mask=255.255.255.0 -- 10.0.122.2 sc_tnt -i 1.1.1.1 -p 12345 -o out.warts" -cpu host --enable-kvm -m 8 -no-acpi -display none -nographic
