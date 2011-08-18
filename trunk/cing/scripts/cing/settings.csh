#!/bin/csh -f
# Author: Jurgen F. Doreleijers

setenv UJ           /home/jurgenfd
setenv WS           $UJ/workspace

set localSettingsFile = $0:h/localSettings.csh
if ( -e $localSettingsFile ) then
    echo "DEBUG: in CING settings.csh; Now picking up $localSettingsFile."
    source $localSettingsFile
else
    echo "DEBUG: in CING settings.csh; No file: $localSettingsFile."
endif

echo "DEBUG: UJ                  $UJ"
echo "DEBUG: WS                  $WS"

