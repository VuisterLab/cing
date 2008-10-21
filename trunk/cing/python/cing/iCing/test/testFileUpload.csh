#!/bin/tcsh -f

# Script for testing of FileUpload.py at the CGI server.
# Run: $CINGROOT/python/cing/iCing/test/testFileUpload.csh

set localTesting = 1

set machineUrl = nmr.cmbi.ru.nl
set rpcUrl = iCing/cgi-bin/iCingServer.py

if ( $localTesting ) then
#	set machineUrl = localhost:8000
	set machineUrl = localhost
	set rpcUrl     = iCing/cgi-bin/iCingByCgi.py
endif

# Full path to file to be uploaded.
#set uploadFile = $CINGROOT/Tests/data/ccpn/SRYBDNA.tgz # 2 Mb
set uploadFile = $CINGROOT/Tests/data/ccpn/1brv.tgz # 68 kb
#set uploadFile = CESG_Other/Brian/tmoc.zip # 47 Mb
#set uploadFile = ~/.forward

# No changes below this line
####################################################

set url = $machineUrl/$rpcUrl

echo "Uploading $uploadFile to: $url"

# No idea why I set the submit field?
curl \
	-F Action=Save \
	-F Submit=OK \
    -F AccessKey=123456 \
    -F UserId=jd \
    -F UploadFile=@$uploadFile \
	$url
    
    
     