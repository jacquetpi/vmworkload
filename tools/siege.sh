#!/bin/bash
if (( "$#" != "2" )) 
then
  echo "Missing argument : ./siege.sh vm delay"
  exit -1
fi
vm_ip=$( virsh --connect=qemu:///system domifaddr "$1" | tail -n 2 | head -n 1 | awk '{ print $4 }' | sed 's/[/].*//' );
echo vmurl
ssh vmtornado@"${vm_ip}" -o StrictHostKeyChecking=no "./changewpip.sh ${vm_ip}"
siege --time=10s --concurrent=4 --delay="$delay" http://"$vm_ip"/