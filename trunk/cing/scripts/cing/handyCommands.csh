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
tar -cvf dataTgz.tar data/*/*/*.tgz
scp -P 39676 dataTgz.tar localhost-nmr:/Users/jd/CASD-NMR-CING

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
cd /Volumes/tera4/CASD-NMR-CING/dataPrep
#\rm -rf */*/Nijmegen/*
\rm -rf */*/Author/*
( cd /Volumes/jd/CASD-NMR-CING/data && tar -cpBf - */*/Author/* ) | ( tar -xpvf - )

