if (( "$#" != "3" )) 
then
  echo "Missing argument : ./wrk2.sh vm timeout rq/s"
  exit -1
fi
vm_ip=$( virsh --connect=qemu:///system domifaddr "$1" | tail -n 2 | head -n 1 | awk '{ print $4 }' | sed 's/[/].*//' )
#( sudo docker run --net=host pjacquet/dsb-socialnetwork-wrk2 -D exp -t 1 -c 20 -d "$2" -L -s ./scripts/social-network/read-home-timeline.lua http://"${vm_ip}":8080/wrk2-api/home-timeline/read -R $3 | tee "/home/pijacque/sched-vm${vm}-${i}" ) &
( sudo docker run --net=host pjacquet/dsb-socialnetwork-wrk2 -D exp -t 2 -c 20 -d "$2" -L -s ./scripts/social-network/read-home-timeline.lua http://"${vm_ip}":8080/wrk2-api/home-timeline/read -R $3 ) &