#!/bin/bash
RUN_BENCH=${1:-"all"}
NB_RUNS=${2:-"30"}

RESULTDIR="../results/cpu"
RESULTDIR_TMP="/tmp/cpu"
CPU_DATA_FILE="/tmp/cpu_usage"

source utils.sh

run_utnt(){
    echo "Run utnt benchmark with $NB_RUNS runs"
    ip link show "$TAP" &> /dev/null || die "$TAP not found"
    rm "$RESULTDIR"/utnt* &> /dev/null
    run_sudo_cmd 
    for i in $(seq 1 ${NB_RUNS}); do
        echo "Running test $i/$NB_RUNS..."
        sar -o "$CPU_DATA_FILE" -u 1 &> /dev/null &
        ./script_deploy/deploy_utnt.sh "${RESULTDIR_TMP}/" "$TAP" &> "/dev/null"
        kill -2 $(pgrep sar) && sleep 0.2
        sar -f "$CPU_DATA_FILE" >> "$RESULTDIR/utnt_cpu.txt"
        rm "$CPU_DATA_FILE"
    done
}

run_vm(){
    echo "Run vm benchmark with $NB_RUNS runs"
    run_sudo_cmd && (sudo systemctl start libvirtd.service || die "libvirtd start failed")
    rm "$RESULTDIR"/vm* &> /dev/null
    cp ../vagrant/Vagrantfile . || die "cp failed"
    for i in $(seq 1 ${NB_RUNS}); do
        echo "Running test $i/$NB_RUNS..."
        sar -o "$CPU_DATA_FILE" -u 1 &> /dev/null &
        ./script_deploy/deploy_vm.sh "${RESULTDIR_TMP}/" &> "/dev/null"
        kill -2 $(pgrep sar) && sleep 0.2
        sar -f "$CPU_DATA_FILE" >> "$RESULTDIR/vm_cpu.txt"
        rm "$CPU_DATA_FILE"
    done
    rm Vagrantfile || die "rm Vagrantfile failed"
    rm -rf .vagrant || die "rm vagrand folder failed"
}

run_docker(){
    echo "Run docker benchmark with $NB_RUNS runs"
    run_sudo_cmd && (sudo service docker start || die "docker start failed")
    rm "$RESULTDIR"/docker* &> /dev/null
    for i in $(seq 1 ${NB_RUNS}); do
        echo "Running test $i/$NB_RUNS..."
        sar -o "$CPU_DATA_FILE" -u 1 &> /dev/null &
        ./script_deploy/deploy_docker.sh "${RESULTDIR_TMP}/" &> "/dev/null"
        kill -2 $(pgrep sar) && sleep 0.2
        sar -f "$CPU_DATA_FILE" >> "$RESULTDIR/docker_cpu.txt"
        rm "$CPU_DATA_FILE"
    done
}

mkdir -p "$RESULTDIR" "${RESULTDIR_TMP}" || die "mkdir failed"

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
rm -rf "${RESULTDIR_TMP}"
