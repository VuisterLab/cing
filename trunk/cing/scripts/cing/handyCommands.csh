set list = ( AR3436A AtT13 CGR26A CtR69A ET109Aox ET109Ared HR5537A NeR103A PGR122A VpR247 )
set baseDir = ~/CASD-NMR-CING

foreach x ( $list )
    echo $x
    set ch23 = ( `echo $x | cut -c2-3` )
    mkdir $baseDir/data/$x
    tar -czf $baseDir/data/$x/$x.tgz $x
end

# Sync ALL to production
cd /Users/jd/CASD-NMR-CING
tar -cvf dataTgz.tar      data/*/*/*.tgz
tar -cvzf dataAnnoLog.tgz data/*/*/log_doAnnotateCasdNmr/*.log
scp -P 39676 dataAnnoLog.tgz localhost-nmr:/Users/jd/CASD-NMR-CING
scp -P 39676 dataTgz.tar     localhost-nmr:/Users/jd/CASD-NMR-CING

cd /Users/jd/CASD-NMR-CING/data
\ls -1l */*/log_doAnn*/*.log

# Copy single entry to production: without the need to decompress on production.
cd ~/CASD-NMR-CING
set x = ET109AoxParis
set ch23 = ( `echo $x | cut -c2-3` )
set dirEntry = data/$ch23/$x
scp -P 39676 $dirEntry/$x.tgz localhost-nmr:/Users/jd/CASD-NMR-CING/$dirEntry

scp -r -P 39676 list Overview Overview.numbers localhost-nmr:/Users/jd/CASD-NMR-CING

# Copy all for processing
scp -vr CASD-NMR-CING jd@nmr:/Users/jd

cd $D/CASD-NMR-CING
scp -r -P 39676 list  localhost-nmr:/Library/WebServer/Documents/CASD-NMR-CING

# Check logs
cd $D/CASD-NMR-CING/data
grep ERROR */*/log_validateEntry/*.log

# Clean the CS Rosetta 'PDB files'. E.g. AtT13Utrecht
grep -v complete atc_pdb_org | grep -v '\-\-\-' > atc.pdb
# and then do the below.


# Insert model records.
cat PGR122A_total_pdb_org | gawk 'BEGIN{i=1;;printf "MODEL       %2d\n", i}\
{print}/^END/ {i = i + 1;printf "MODEL       %2d\n", i}' | grep -v REMARK > PGR122A_total.pdb
#and by hand remove the last
# Or based on a TER record:
cat top10_CTR69A.tmp | gawk 'BEGIN{i=1;;printf "MODEL       %2d\n", i}\
{print}/^TER/ {i = i + 1;printf "MODEL       %2d\n", i}' | grep -v REMARK > top10_CTR69A.pdb
#and by hand remove the last

# Copy from development to production

#ON PRODUCTION
cd $D/CASD-NMR-CING/dataPrep
#\rm -rf */*/Nijmegen/*
\rm -rf */*/Author/*
( cd /Volumes/jd/CASD-NMR-CING/data && tar -cpBf - */*/Author/* ) | ( tar -xpvf - )

# DEVelopmental
set results_base = $D/devNRG-CING
mkdir $results_base
cd $results_base
mkdir -p recoordSync input list log index nrgPlus pgsql plot prep vCing data cmbi8/comments


set list = ( 1brv 1cjg 1d3z 1hue 1ieh 1iv6 2rop 2jmx 2kz0 2kib )
set list = ( 1b4y 1brv 1bus 1c2n 1cjg 1d3z 1hkt 1hue 1ieh 1iv6 1mo7 1mo8 1ozi 1p9j 1pd7 1qjt 1vj6 1y7n 2f05 2fws 2fwu 2jmx 2jsx 2k0e 2kib 2kz0 2rop )

set bDir = /Volumes/Toby/Backups.backupdb/Stella/Latest/Stella
set bDir = /
set eDir = /Users/jd/wattosTestingPlatform/bmrb/ftp.bmrb.wisc.edu/pub/bmrb/entry_directories

set x = 1brv
foreach x ( $list )
    \cp -rf $bDir/$D/NRG-CING/recoordSync/$x $results_base/recoordSync
end

set blist = ( 53 1646 4020 4046 4046 4047 4400 4491 4813 4969 5131 5317 5576 5577 5762 5801 5808 6113 6457 7008 7009 7009 11041 15072 15381 16995 20074 )
set y = 4020
foreach y ( $blist )
    \cp -rf $bDir/$eDir/bmr$y $eDir
end

psql pdbmlplus pdbj
 create user devnrgcing1;
select count(*) from nrgcing.cingentry;

python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py devnrgcing $CINGROOT/python/cing/NRG/sql/createDB-CING_psql.sql    .

find . -name "*_21.str" | xargs grep -H "chemical shifts'" > ~/BMRB_CS_counts.txt

find $D/devNRG-CING/data -name "*.log" | xargs grep "DEBUG: nucleus: 1"
find $D/devNRG-CING/data -name "*.log" | xargs grep "ERROR: "

set archive_id = CASD-NMR-CING
set archive_id = NRG-CING
set cmd = ("rsync -av /Volumes/tria3/$archive_id/ /Volumes/tria4/$archive_id")
$cmd | & mail -s rsync.log jd &
