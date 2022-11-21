#!/bin/bash
if (( "$#" != "3" )) 
then
  echo "siege.sh Missing argument : ./siege.sh vm timeout concurrent"
  exit -1
fi
timeout="$2"
concurrent="$3"
fullip=$( tools/retrieveip.sh $1 );
if [[ ${fullip} == *":"* ]];
then
  ip=$(echo $fullip | cut -d : -f 1)
  port=$(echo $fullip | cut -d : -f 2)
  # temporary workaround
  ssh vmtornado@"${ip}" -p "$port" -o StrictHostKeyChecking=no -L ${port}:localhost:80 "sleep ${timeout}" 
  siege --time="$timeout"s --concurrent="$concurrent" --delay=1 http://localhost:${port}/
else
  ip="$fullip"
  port="5432"
  siege --time="$timeout"s --concurrent="$concurrent" --delay=1 http://"$vm_ip"/
fi