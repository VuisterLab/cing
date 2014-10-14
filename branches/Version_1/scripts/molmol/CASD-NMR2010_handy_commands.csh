set list = ( 2kif 2kj6 2kk1 2kkx 2kky 2knr 2kmm 2kpm 2kpt 2kru )
set listy = ( VpR247 AR3436A HR5537A ET109Ared ET109Aox AtT13 PgR122A NeR103A CgR26A CtR69A )
set x = 2kif
@ count = 1
foreach x ( $list )
    set ch23 = ( `echo $x | cut -c2-3` )
    gunzip -c $PDBZ2/$ch23/pdb$x.ent.gz > $x"_all".pdb
    splitpdb modelnum=1 $x"_all".pdb
    mv $x"_all_001".pdb $x.pdb
    $C/scripts/molmol/molmol_hires_image.csh $x      
end    

@ count = 1
foreach x ( $list )
    set y = $listy[$count]
    cp $x.gif renamed/$y.gif
    @ count = $count + 1    
end    

@ count = 1
foreach x ( $list )
    set y = $listy[$count]
    convert renamed/$y.gif reformatted/$y.png
    @ count = $count + 1    
end    

@ count = 1
foreach x ( $list )
    set y = $listy[$count]
    echo "Doing $x $y"
    set ch23 = ( `echo $x | cut -c2-3` )
#    set newName = $count"_"$y
    set newName = $y
    scp i@nmr.cmbi.ru.nl:/\$D/NRG-CING/data/$ch23/$x/$x.cing/$x/HTML/mol.gif $newName.gif
    @ count = $count + 1    
end


