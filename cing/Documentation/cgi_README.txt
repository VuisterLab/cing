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


