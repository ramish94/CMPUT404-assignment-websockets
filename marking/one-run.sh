#!/bin/bash
ps aux | fgrep 'python -m SimpleHTTPServer' | awk '{print $2}' | xargs kill
python -m SimpleHTTPServer 8118 &
ID=$!
repo=$1
two=$2
docker run -u=me -p 127.0.0.1:8000:8000 -i -t cmput404ass5 /bin/bash /home/me/arb.sh  $repo $two 
kill $ID
