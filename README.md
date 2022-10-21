python3 -m vmworkload -c 768 -m 1024 -w20,60

apt-get install siege
git clone --depth 1 https://github.com/cmu-db/benchbase.git
cd benchbase
./mvnw clean package -P postgres
cd target
tar xvzf benchbase-postgres.tgz