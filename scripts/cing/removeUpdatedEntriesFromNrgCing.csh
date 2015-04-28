#!/bin/tcsh -f
# execute like:
# $CINGROOT/scripts/cing/removeUpdatedEntriesFromNrgCing.csh 2kqu
#
# Something like below:
# cat 2010*/modified*; cat 2010*/obsolete*; | sort -u > $D/t.csv
#set subl = (`cat $D/t.csv`)

set nrgCingDir = /Library/WebServer/Documents/NRG-CING

# Get argument pdb code if it exists.
if ( $1 != "" ) then
    set subl = (  `echo $1 | sed 's/,/ /'g`  )
endif

@ count = 0
echo "==>     DOING" $#subl "pdb entries"
foreach x ( $subl )
	cd $nrgCingDir
    echo "==>      DOING $x"
    set ch23 = ( `echo $x | cut -c2-3` )

	set inputDir = data/$ch23/$x
	if ( ! -e $inputDir ) then
		continue
	endif
	cd $inputDir

	echo "Removing cing data (not the logs) from: $inputDir"
	set removedSomething = 0
	foreach el ( $x.cing $x.cing.tgz $x $x.tgz )
		if ( ! -e $el ) then
			continue
		endif
		rm -rf $el
		set removedSomething = 1
	end
	if ( $removedSomething ) then
		@ count = $count + 1
	endif
end

echo "==> DONE with removing CING files for number of entries: $count out of $#subl"