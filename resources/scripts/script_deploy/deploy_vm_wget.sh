#!/bin/bash
#Used to substract the time of the wget command from the total time of the vm deployment
wget https://vagrantcloud.com/generic/boxes/ubuntu1604/versions/4.2.16/providers/libvirt.box &> /dev/null && rm libvirt.box
