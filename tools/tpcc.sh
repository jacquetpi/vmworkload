#!/bin/bash
if (( "$#" != "3" )) 
then
  echo "Missing argument : ./tpcc.sh vm timeout rq/s"
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
cp /usr/local/src/benchbase/config/postgres/sample_tpcc_config.xml "$config_file"
sed -i -- "s/localhost:5432/${ip}:"${port}"/g" "$config_file"
sed -i -- "s/<time>60/<time>${2}/g" "$config_file"
sed -i -- "s/<rate>10000/<rate>${3}/g" "$config_file"
location=$( pwd )
cd /usr/local/src/benchbase
output=$( java -jar /usr/local/src/benchbase/target/benchbase-postgres/benchbase.jar -b tpcc -c "$config_file" --execute=true )
epoch=$( date +%s%N )
fileoutput="${1}-${epoch}-tpcc.txt"
cd "$location"
printf "$output" > "dump/${fileoutput}"
