#!/bin/bash
if (( "$#" != "3" )) 
then
  echo "siege.sh Missing argument : ./siege.sh vm timeout concurrent"
  exit -1
fi
timeout="$2"
concurrent="$3"
fullip=$( tools/retrieveip.sh $1 );
sed -i -- "s/true/false/g" ${HOME}/.siege/siege.conf
siege --time="$timeout"s --concurrent="$concurrent" --delay=1 http://${fullip}/