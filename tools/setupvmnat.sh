#!/bin/bash
if (( "$#" != "3" )) 
then
  echo "Missing argument : ./setupvmnat.sh vm workload hostport"
  exit -1
fi
case $2 in
  "idle" | "stressng")
    dport="22"
    ;;
  "wordpress")
    dport="22"
    ;;
  "dsb")
    dport="8080"
    ;;
  "tpcc" | "tpch")
    dport="5432"
    ;;
  *)
    echo -n "setupvmnat.sh : unknow workload $2 for $1"
    exit -1
    ;;
esac
while true;
do
  vm_ip=$( virsh --connect=qemu:///system domifaddr "$1" | tail -n 2 | head -n 1 | awk '{ print $4 }' | sed 's/[/].*//' );
  if [ -n "$vm_ip" ]; then #VAR is set to a non-empty string
    break
  fi
  sleep 10
done
sudo firewall-cmd --add-forward-port=port=$3:proto=tcp:toaddr=$vm_ip:toport=$dport
echo "setup nating for $1 on port $3 for $vm_ip:$dport on workload $2"
# cancel with:  sudo firewall-cmd --reload