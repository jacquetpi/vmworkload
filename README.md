## Example 

python3 -m vmworkload -c 768 -m 1024 -s -w20,60,4

## Requirements
apt-get install siege
docker pull pjacquet/dsb-socialnetwork-wrk2
git clone --depth 1 https://github.com/cmu-db/benchbase.git
cd benchbase
./mvnw clean package -P postgres
cd target
tar xvzf benchbase-postgres.tgz
With basic scripts : sudo docker in visudo