#!/bin/tcsh -f

# Script for testing of FileUpload.py at the CGI server.
# Run: $CINGROOT/python/cing/cgi/test/testFileUpload.csh

set localTesting = 1

set machineUrl = nmr.cmbi.ru.nl
if ( $localTesting ) then
	set machineUrl = localhost
endif

# Full path to file to be uploaded.
#set uploadFile = $CINGROOT/Tests/data/ccpn/SRYBDNA.tgz # 2 Mb
set uploadFile = $CINGROOT/Tests/data/ccpn/1brv.tgz # 68 kb
#set uploadFile = CESG_Other/Brian/tmoc.zip # 47 Mb

# No changes below this line
####################################################

set url = $machineUrl/cgi-bin/iCing/FileUpload.py

echo "Uploading $uploadFile to: $url"

curl \
	-F Submit=OK \
    -F AccessKey=123456 \
    -F UserId=jd \
    -F UploadFile=@$uploadFile \
	$url
    
    
     