#!/bin/tcsh -f
# Author: Jurgen F. Doreleijers

set isProduction = 0 # causes sleep and certainly no svn update.

#setenv TARGET_SDIR 'jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/tmp/cingTmp'
setenv TARGET_SDIR 'jd@nmr.cmbi.umcn.nl:/Users/jd/tmp/cingTmp'
setenv TARGET_PORT ''

if ( ! $isProduction ) then
    setenv TARGET_SDIR 'jd@localhost-nmr:/Users/jd/tmp/cingTmp'
    setenv TARGET_PORT '-P 39676'
endif
