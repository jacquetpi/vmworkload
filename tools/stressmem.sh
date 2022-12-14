#!/bin/bash
if (( "$#" != "3" )) 
then
  echo "stressmem.sh Missing argument : ./stressmem.sh vm timeout percent"
  exit -1
fi
# remote with stress-ng --vm-bytes $(awk '/MemAvailable/{printf "%d\n", $2 * 0.9;}' < /proc/meminfo)k --vm-keep -m 1
vm=$1
timeout=$2
percent=$3
config=$( virsh --connect=qemu:///system dommemstat $1 | awk '/actual/{printf "%d\n", $2;}' )
quantity=$( python3 -c "print(${config}*${percent})" )
#echo "$config $percent $quantity"
tools/sshvm.sh $vm "stress-ng --timeout ${timeout} --vm-bytes ${quantity}k --vm-keep -m 1"