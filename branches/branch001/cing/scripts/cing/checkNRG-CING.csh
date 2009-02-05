#!/bin/csh -f
# Author: Jurgen F. Doreleijers 

set subl = ( `cat  ~/entries_todo_2008-12-2.csv`)
set subl = ( 1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e )
#set subl = ( 1cfp 1vnd 2hqo 2hr9 2jz7 )

cd /Library/WebServer/Documents/NRG-CING
#cd /var/www/servlet_data/NRG_ccpn_tmp

echo "Doing" $#subl "pdb entries"
foreach x ( $subl )
   echo "Doing $x"
   if ( -e $x.tgz ) then
        echo "DEBUG: $x.tgz already present."
        continue
   endif
   tail -4 $x.log
end

echo "Finished"


