#!/bin/tcsh -f
# Author: Jurgen F. Doreleijers
# Test like:
# $C/scripts/vcing/settings.csh

set isProduction = 1 # causes sleep and certainly no svn update.

#setenv TARGET_SDIR 'jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/tmp/cingTmp'
#setenv TARGET_SDIR 'jd@nmr.cmbi.umcn.nl:/Users/jd/tmp/cingTmp'
setenv TARGET_SDIR 'jd@dodos.dyndns.org:/Users/jd/tmp/cingTmp'
#setenv TARGET_SDIR 'jd@nmr.cmbi.umcn.nl:/Users/jd/tmp/cingTmp'
setenv TARGET_PORT ''

echo 'Now in $C/scripts/vcing/settings.csh version 0.0.1'
if ( ! $isProduction ) then
    setenv TARGET_SDIR 'jd@localhost-nmr:/Users/jd/tmp/cingTmp'
    setenv TARGET_PORT '-P 39676'
endif

setenv vcingScriptDir $0:h
if ( -e $vcingScriptDir/localConstants.csh ) then
    echo 'DEBUG: getting local vcing settings.'
    source $vcingScriptDir/localConstants.csh
else
    echo 'DEBUG: found no local vcing settings.'
endif


echo "DEBUG: TARGET_SDIR                 : $TARGET_SDIR"
echo "DEBUG: TARGET_PORT (might be empty): $TARGET_PORT"
