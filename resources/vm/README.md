sudo apt-get install -y gcc wget build-essential autoconf zip traceroute
cd ~
wget https://github.com/YvesVanaubel/TNT/archive/refs/heads/master.zip && unzip master.zip
cd TNT-master/TNT/scamper-tnt-cvs-20180523a/
wget http://www.letemple.fr/sc_tnt.c
cp sc_tnt.c utils/sc_tnt/sc_tnt.c
./configure CFLAGS="-lpthread" && make
sudo make install
sudo chmod +x /usr/local/bin/scamper

#Créer le fichier run_script.sh dans ~

#!/bin/bash
mkdir /tmp/host_files
mount -t 9p -o trans=virtio,version=9p2000.L /hostshare /tmp/host_files

ip=$(cat /tmp/host_files/ip)

export LD_LIBRARY_PATH=/usr/local/lib
/usr/local/bin/scamper -D -P 12345
/usr/local/bin/sc_tnt -i "$ip" -p 12345 -o /tmp/host_files/out.warts

shutdown=$(cat /tmp/host_files/shutdown)
if [ "$shutdown" = "1" ]; then
    echo "shutdown"
    shutdown now
fi

#Fin du fichier

#Créer le fichier scamper.service dans le dossier /etc/systemd/system/

[Unit]
Description=scamper service
After=network.target

[Service]
Type=simple
ExecStart=/home/student/run_script.sh

[Install]
WantedBy=multi-user.target

#Fin du fichier

sudo systemctl enable scamper.service
sudo reboot
