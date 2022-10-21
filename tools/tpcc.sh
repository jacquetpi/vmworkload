if (( "$#" != "3" )) 
then
  echo "Missing argument : ./tpcc.sh vm timeout rq/s"
  exit -1
fi
random_input=$( tr -dc A-Za-z0-9 </dev/urandom | head -c 13 ; echo '' )
config_file="/tmp/benchbase-${random_input}.xml"
vm_ip=$( virsh --connect=qemu:///system domifaddr "$1" | tail -n 2 | head -n 1 | awk '{ print $4 }' | sed 's/[/].*//' );
echo "$config_file"
cp /usr/local/src/benchbase/config/postgres/sample_tpcc_config.xml "$config_file"
echo "$config_file"
sed -i -- "s/localhost:5432/${vm_ip}:5432/g" "$config_file"
sed -i -- "s/<time>60/<time>${2}/g" "$config_file"
sed -i -- "s/<rate>10000/<rate>${3}/g" "$config_file"
echo "$config_file"
cd /usr/local/src/benchbase
java -jar /usr/local/src/benchbase/target/benchbase-postgres/benchbase.jar -b tpcc -c "$config_file" --execute=true
rm "$config_file"