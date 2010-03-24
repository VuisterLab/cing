AR3436A
AtT13
CGR26A
CtR69A
ET109Aox
ET109Ared
HR5537A
NeR103A
PGR122A
VpR247


set list = ( AR3436A AtT13 CGR26A CtR69A ET109Aox ET109Ared HR5537A NeR103A PGR122A VpR247 )
set baseDir = ~/CASD-NMR-CING

foreach x ( $list )
	echo $x
    set ch23 = ( `echo $x | cut -c2-3` )
    mkdir $baseDir/data/$x
    tar -czf $baseDir/data/$x/$x.tgz $x
end

