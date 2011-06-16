

cd $D/NRG-CING
set diskId = Tetra
set diskId = Terad
set listLog = listInvalidTgz$diskId.log
grep    ERROR $listLog | gawk '{print $2}' | cut -c6-9 > entry_list_bad_tgz_$diskId.csv
wc entry_list_*_tgz_*.csv
set list = ( `grep ERROR $D/NRG-CING/$listLog | gawk '{print $2}' `)
echo "Found $#list entries"

# find tgz entries:
cd $D/NRG-CING/data
find . -maxdepth 3 -name "*.tgz" | cut -c 6-9

# Check signature of last logs coming in. Replace XXXX
cd /Library/WebServer/Documents/tmp/vCingSlave/vCingXXXX/log
ls -tr | tail | gawk '{printf " %s", $0}' | xargs grep cores

jd:nmr/D/ wc ~/entr*.csv
     397     397    1985 /Users/jd/entry_list_bad_tgz.csv
    4796    4797   23980 /Users/jd/entry_list_good_tgz.csv
    5193    5194   25965 total

Busy with:

jd:nmr/tmpNRG-CING/ jobs
[1]  + Running                       sudo rsync -avr $D/NRG-CING $D/ >>& ~/rsyncNRG-CING.log
[3]    Running                       sudo rsync -avr $D/pgdata $D/ >>& ~/rsyncpgdata.log
sudo rsync -ave ssh jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/D /Volumes/D/ >>& rsyncD.log

snmr
cd $D
rsync -ave ssh jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/D . >>& rsyncD.log