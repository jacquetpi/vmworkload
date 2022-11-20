#!/bin/bash
if (( "$#" != "3" )) 
then
  echo "siege.sh Missing argument : ./siege.sh vm timeout concurrent"
  exit -1
fi
vm_ip=$( tools/retrieveip.sh $1 );
timeout="$2"
concurrent="$3"
siege --time="$timeout"s --concurrent="$concurrent" --delay=1 http://"$vm_ip"/