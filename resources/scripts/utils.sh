TAP="virbr0"
TO_KB=$((1000))
TO_MB=$((1000 * TO_KB))

die(){
    echo "$1"
    exit 1
}

run_sudo_cmd(){
    echo "unikraft2023!" | sudo -S date > "/dev/null"
}