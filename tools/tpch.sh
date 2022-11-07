if (( "$#" != "2" )) 
then
  echo "Missing argument : ./tpch.sh vm rq/s"
  exit -1
fi
random_input=$( tr -dc A-Za-z0-9 </dev/urandom | head -c 13 ; echo '' )
config_file="/tmp/benchbase-${random_input}.xml"
vm_ip=$( virsh --connect=qemu:///system domifaddr "$1" | tail -n 2 | head -n 1 | awk '{ print $4 }' | sed 's/[/].*//' );
cp /usr/local/src/benchbase/config/postgres/sample_tpch_config.xml "$config_file"
sed -i -- "s/localhost:5432/${vm_ip}:5432/g" "$config_file"
sed -i -- "s/<rate>unlimited/<rate>${2}/g" "$config_file"
echo "$config_file"
cd /usr/local/src/benchbase
( java -jar /usr/local/src/benchbase/target/benchbase-postgres/benchbase.jar -b tpch -c "$config_file" --execute=true ) &