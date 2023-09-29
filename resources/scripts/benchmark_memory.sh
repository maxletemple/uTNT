#!/bin/bash
RUN_BENCH=${1:-"all"}

RESULTDIR="../results/memory"

source utils.sh

run_utnt(){
    echo "Run utnt benchmark"
    local csvfile="memory_utnt.csv"
    run_sudo_cmd
    echo "date,memory_kb" > "$RESULTDIR/$csvfile"
    sudo watch -n 1 ./smap_parser -d "$RESULTDIR/$csvfile" -n qemu-system-x86_64 -m 8 &> "/dev/null" &
    current=$(pwd)
    cd "../../apps/uTNT/"||die "uTNT not found"
    sudo qemu-system-x86_64 -s -netdev bridge,id=en1,br=$TAP -device virtio-net-pci,netdev=en1 -device isa-debug-exit -kernel "build/app-utnt_qemu-x86_64" -append "netdev.ipv4_addr=10.0.122.2 netdev.ipv4_gw_addr=10.0.122.1 netdev.ipv4_subnet_mask=255.255.255.0 -- 10.0.122.2 sc_tnt -i 1.1.1.1 -p 12345 -o out.warts" -cpu host --enable-kvm -m 8 -no-acpi -display none -nographic | sudo tee "$current/utnt.log" &> "/dev/null"
    cd "$current"||die "cd failed"
    sleep 1
    sudo  killall watch
    sudo chown -R "$USER" "$RESULTDIR/$csvfile" "$current/utnt.log"
    echo "File written to $RESULTDIR/$csvfile"
}

run_vm(){
    echo "Run vm benchmark"
    local csvfile="memory_vm.csv"
    run_sudo_cmd
    echo "date,memory_kb" > "$RESULTDIR/$csvfile"
    sudo watch -n 1 ./smap_parser -d "$RESULTDIR/$csvfile" -n qemu-system-x86_64 -m 1024 &> "/dev/null" &
    current=$(pwd)
    cd "../vagrant/"||die "vagrant not found"
    vagrant up --provision > "$current/vm.log" ||die "vagrant failed"
    vagrant halt
    cd "$current"||die "cd failed"
    sleep 1
    sudo  killall watch
    sudo chown -R "$USER" "$RESULTDIR/$csvfile" "$current/vm.log"
    echo "File written to $RESULTDIR/$csvfile"
}

run_docker(){
    echo "Run docker benchmark"
    local csvfile="memory_docker.csv"
    echo "date,memory_kb" > "$RESULTDIR/$csvfile"
    
    formatted_date=$(date -u +"%Y-%m-%dT%H:%M:%S.%1NZ")
    echo "$formatted_date,0 " >> "$RESULTDIR/$csvfile"

    echo "formatted_date=$(date -u +"%Y-%m-%dT%H:%M:%S.%1NZ")" > /tmp/script.sh
    echo "echo -n \$formatted_date, >> "$RESULTDIR/$csvfile"" >> /tmp/script.sh
    echo "cat /proc/\$(pgrep docker|tail -n 1)/smaps_rollup|grep "Rss:"|awk '{ print \$2}' >> "$RESULTDIR/$csvfile"" >> /tmp/script.sh
    chmod +x /tmp/script.sh
    watch -n 1 /tmp/script.sh &> "/dev/null" &
    docker run --rm --name scamper -v /tmp:/tmp gaulthiergain/scamper_tnt:0.1 &> "docker.log"
    sleep 1
    killall watch
    rm /tmp/script.sh &> "/dev/null"
    echo "File written to $RESULTDIR/$csvfile"
}

mkdir -p "$RESULTDIR" || die "mkdir failed"

if [ "$RUN_BENCH" == "all" ]; then
    run_utnt
    run_vm
    run_docker
elif [ "$RUN_BENCH" == "utnt" ]; then
    run_utnt
elif [ "$RUN_BENCH" == "vm" ]; then
    run_vm
elif [ "$RUN_BENCH" == "docker" ]; then
    run_docker
else
    echo "Unknown benchmark"
fi
