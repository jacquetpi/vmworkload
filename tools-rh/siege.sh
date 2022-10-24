#!/bin/bash
if (( "$#" != "3" ))
then
  echo "siege.sh Missing argument : ./siege.sh vm timeout concurrent"
  exit -1
fi
vm_ip=$( virsh --connect=qemu:///system domifaddr "$1" | tail -n 2 | head -n 1 | awk '{ print $4 }' | sed 's/[/].*//' );
timeout="$2"
concurrent="$3"
siege --time="$timeout"s --concurrent="$concurrent" --delay=1 http://"$vm_ip"/