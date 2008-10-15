    /private/etc/apache2/httpd.conf
		
    In last conf file:
    
ScriptAliasMatch ^/cgi-bin/((?!(?i:webobjects)).*$) "/Library/WebServer/CGI-Executables/$1"

<Directory "/Library/WebServer/CGI-Executables">
    AllowOverride None
    Options None
    Order allow,deny
    Allow from all
</Directory>

So that the following url is available:
http://localhost/cgi-bin/iCing/FileUpload.py?AccessKey=123456&UserId=jd&UploadFile=abracadabrasesameopen
http://localhost:8000/ttt?q=ABC+DEF

http://stella.cmbi.umcn.nl/cgi-bin/fileUpload.py?name=jfd&addr=test
See: python/cgi/test/testFileUpload.csh


Add settings to /private/etc/apache2/httpd.conf  like:
SetEnv  xplorPath /usr/local/bin/xplor
SetEnv  procheckPath /Users/jd/progs/procheck/procheck_nmr.scr
SetEnv  aqpcPath /Users/jd/progs/aquad/scripts/aqpc
SetEnv  whatifPath /home/vriend/whatif/DO_WHATIF.COM
SetEnv  dsspPath /home/vriend/whatif/dssp/DSSP.EXE
SetEnv  convertPath /sw/bin/convert
SetEnv  ghostscriptPath /sw/bin/gs
SetEnv  ps2pdfPath /sw/bin/ps2pdf14
SetEnv  molmolPath /Users/jd/progs/molmolM/molmol
SetEnv  povrayPath /sw/bin/povray
# To home a .matplot directory with settings will be added.
SetEnv  HOME /Library/WebServer/Documents/cgi-cing-home
SetEnv  CINGROOT /Users/jd/workspace34/cing
# Make sure the CING python directory referenced in the simpleCgiServer.py is
# rwx to world.


ProxyPass         /cgi-bin/iCing http://localhost:8888/
ProxyPassReverse  /cgi-bin/iCing http://localhost:8888/

