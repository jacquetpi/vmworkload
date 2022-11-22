#!/bin/bash
if (( "$#" != "2" )) 
then
  echo "Missing argument : ./tpch.sh vm rq/s"
  exit -1
fi
random_input=$( tr -dc A-Za-z0-9 </dev/urandom | head -c 13 ; echo '' )
config_file="/tmp/benchbase-${random_input}.xml"
fullip=$( tools/retrieveip.sh $1 );
if [[ ${fullip} == *":"* ]];
then
  ip=$(echo $fullip | cut -d : -f 1)
  port=$(echo $fullip | cut -d : -f 2)
else
  ip="$fullip"
  port="5432"
fi
cp /usr/local/src/benchbase/config/postgres/sample_tpch_config.xml "$config_file"
sed -i -- "s/localhost:5432/${ip}:"${port}"/g" "$config_file"
sed -i -- "s/<rate>unlimited/<rate>${2}/g" "$config_file"
location=$( pwd )
cd /usr/local/src/benchbase
output=$( java -jar /usr/local/src/benchbase/target/benchbase-postgres/benchbase.jar -b tpch -c "$config_file" --execute=true )
epoch=$( date +%s%N )
fileoutput="${1}-${epoch}-tpch.txt"
cd "$location"
printf "$output" > "dump/${fileoutput}"