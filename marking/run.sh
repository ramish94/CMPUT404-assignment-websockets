ps aux | fgrep 'python -m SimpleHTTPServer' | awk '{print $2}' | xargs kill
python -m SimpleHTTPServer 8118 &
ID=$!
for file in html/*.html
do
echo "#################################"
echo $file
echo "#################################"
bash one-run.sh $file
#docker run -u=me -i -t cmput404 /bin/bash /home/me/arb.sh  `perl 2txt.pl "$file" | perl grepgh.pl` | tee $file.out
done
kill $ID
