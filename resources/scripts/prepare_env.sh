#!/bin/bash

sudo apt-get install -y vagrant libvirt-clients libvirt-daemon-system libvirt-daemon virtinst bridge-utils qemu-kvm docker.io



USER="debian"   


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

vagrant plugin install vagrant-libvirt

sudo usermod -a -G libvirt $USER

sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker