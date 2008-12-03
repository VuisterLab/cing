#!/bin/csh -f
# Author: Jurgen F. Doreleijers 
# Redo the layout of the NRG-CING site

#set subl = ( `cat  ~/entries_todo_2008-12-2.csv`)
set subl = ( 1a4d )
#set subl = ( 1cfp 1vnd 2hqo 2hr9 2jz7 )

cd /Library/WebServer/Documents/NRG-CING
#cd /var/www/servlet_data/NRG_ccpn_tmp
# From:
#    $x.tgz
#    $x.cing
#    $x.log
#    $x
# To:
#    $ch23
#      $x
#        $x.tgz
#        $x.cing
#        $x.log
#        $x
echo "Doing" $#subl "pdb entries"
foreach x ( $subl )
   echo "Doing $x"
   set ch23 = ( `echo $x | cut -c2-3` )
   
   if ( ! -e $x.tgz ) then
        echo "DEBUG: $x already moved."
        continue
   endif
   if ( ! -e $ch23 ) then
        mkdir $ch23
   endif      
   if ( ! -e $ch23/$x ) then
   	    mkdir $ch23/$x
   endif
   
   mv $x.tgz  $ch23/$x
   mv $x.cing $ch23/$x
   mv $x.log  $ch23/$x
   
end

echo "Finished"


