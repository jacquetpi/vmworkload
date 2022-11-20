#!/bin/bash
if (( "$#" != "3" )) 
then
  echo "Missing argument : ./wrk2.sh vm timeout rq/s"
  exit -1
fi
fullip=$( tools/retrieveip.sh $1 );
if [[ ${fullip} == *":"* ]];
then
  ip=$(echo $fullip | cut -d : -f 1)
  port=$(echo $fullip | cut -d : -f 2)
else
  ip="$fullip"
  port="8080"
fi
sudo docker run --net=host pjacquet/dsb-socialnetwork-wrk2 -D exp -t 2 -c 20 -d "$2" -L -s ./scripts/social-network/read-home-timeline.lua http://"${ip}":"${port}"/wrk2-api/home-timeline/read -R $3