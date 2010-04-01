set list = ( AR3436A AtT13 CGR26A CtR69A ET109Aox ET109Ared HR5537A NeR103A PGR122A VpR247 )
set baseDir = ~/CASD-NMR-CING

foreach x ( $list )
	echo $x
    set ch23 = ( `echo $x | cut -c2-3` )
    mkdir $baseDir/data/$x
    tar -czf $baseDir/data/$x/$x.tgz $x
end

cd /Users/jd/CASD-NMR-CING
tar -cvf dataTgz.tar data/*/*/*.tgz
scp -P 39676 dataTgz.tar localhost-nmr:/Users/jd/CASD-NMR-CING

cd /Users/jd/CASD-NMR-CING/data
\ls -1l */*/log_doAnn*/*.log
grep "Aborting" */*/log_doAnn*/*.log

CGR26ACheshire
CGR26AFrankfurt
CGR26ALyon
CGR26APiscataway
CGR26ASeattle4
CGR26ASeattle5
CGR26AUtrecht2
PGR122ACheshire
PGR122APiscataway
PGR122ASeattle4
PGR122AUtrecht
ET109AoxSeattle
ET109AoxUtrecht2
ET109AredCheshire
ET109AredParis
ET109AredSeattle
ET109AredUtrecht2
