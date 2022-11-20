#!/bin/bash
fullip=$( tools/retrieveip.sh $1 );
if [[ ${fullip} == *":"* ]];
then
  ip=$(echo $fullip | cut -d : -f 1)
  port=$(echo $fullip | cut -d : -f 2)
else
  ip="$fullip"
  port="22"
fi
echo "$ip $port"
ssh vmtornado@"${ip}" -p "$port" -o StrictHostKeyChecking=no "$2" 