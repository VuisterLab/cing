#!/bin/tcsh -f

# Script for testing of FileUpload.py at the CGI server.
# Run: $CINGROOT/python/cing/iCing/test/testiCingServer.csh

set localTesting = 1

set machineUrl = nmr.cmbi.ru.nl
if ( $localTesting ) then
	set machineUrl = localhost:8000
endif

# No changes below this line
####################################################

set url = $machineUrl

echo "Curling to: $url"

curl \
	-F Action=Run \
    -F AccessKey=123456 \
    -F UserId=jd \
	$url
    
    
     