set list = ( `grep ERROR ~/listInvalidTgz.log | gawk '{print $2}' `)
echo "Found $#list bad files"
set entryList = $D/NRG-CING/entry_list_bad_transfer.csv
\rm $entryList >& /dev/null
foreach x ( $list )
    echo $x | cut -c6-9 >> $entryList
end

# From Duvel
scp jd@dodos.dyndns.org:\$D/NRG-CING/entry_list_bad_transfer.csv $D/NRG-CING


## And finally when absolutely certain and triple backups were made
echo $list | xargs ls -ltr $list
rm $list

# Check signature of last logs coming in. Replace XXXX
cd /Library/WebServer/Documents/tmp/vCingSlave/vCingXXXX/log
ls -tr | tail | gawk '{printf " %s", $0}' | xargs grep cores


foreach try in ( 0 1 2 )
    