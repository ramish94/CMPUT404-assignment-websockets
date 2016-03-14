#!/bin/bash
REPO=$1
git clone $1 ass5
cd ass5
mv freetests.py freetests.py.student
mv runtests.sh runtests.sh.student
wget /usr/bin/wget http://172.17.42.1:8118/freetests.py
wget /usr/bin/wget http://172.17.42.1:8118/run.py
wget /usr/bin/wget http://172.17.42.1:8118/drun.sh
wget /usr/bin/wget http://172.17.42.1:8118/runtests.sh
echo "###############################"
bash runtests.sh
echo "###############################"
echo So those were the tests
echo Now run the server!
pgrep gunicorn | xargs -i kill -9 {} || echo OK
bash drun.sh
