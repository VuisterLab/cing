#!/bin/csh -f
# Author: Jurgen F. Doreleijers 

set subl = ( `cat  ~/entryCodeList-Oceans14.csv`)
set subl = ( 1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e )
#set subl = ( 1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e )

cd /Library/WebServer/Documents/NRG-CING
#cd /var/www/servlet_data/NRG_ccpn_tmp

@ sublMin = 0

echo "Doing" $#subl "pdb entries"
@ count = 0
foreach x ( $subl )
   @ count = $count + 1
   if ( $count < $sublMin ) then
            continue
   endif
   echo "Doing $x $count"

   if ( -e $x.tgz ) then
        echo "DEBUG: $x.tgz already present."
        continue
   endif
   
#    scp -P 39676 $x/$x.tgz  jd@localhost-nmr:/Library/WebServer/Documents/NRG-CING
#    scp jurgen@restraintsgrid.bmrb.wisc.edu:/var/www/servlet_data/NRG_ccpn_tmp/$x/$x.tgz .
#    wget http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp/$x/$x.tgz 
    #wget http://nmr.cmbi.ru.nl/NRG-CING/$x.tgz
    scp -P 39676 jd@localhost-nmr:/Library/WebServer/Documents/NRG-CING/$x.tgz . 
end

echo "Finished"
