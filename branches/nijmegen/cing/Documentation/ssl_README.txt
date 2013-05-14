* Doing https on mac:
	- Ask Wilmar Teunissen's help
	- Study http://www.madboa.com/geek/openssl/#cert-request
	  and http://www.ru.nl/uci/diensten_voor/medewerkers/ict-beveiliging/
	- Generated a key:
		"""[mini:etc/apache2/extra] root# openssl req -new -newkey rsa:1024 -nodes -keyout nmrkey.pem -out nmr_request.pem
Generating a 1024 bit RSA private key
......++++++
......++++++
writing new private key to 'nmrkey.pem'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:NL
State or Province Name (full name) [Some-State]:Gelderland
Locality Name (eg, city) []:Nijmegen
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Radboud Universiteit Nijmegen
Organizational Unit Name (eg, section) []:CMBI
Common Name (eg, YOUR name) []:nmr.cmbi.ru.nl
Email Address []:

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:
		"""

		
Setup a secure iCing server at:

https://nmr.cmbi.umcn.nl/icing
equals:
/Library/WebServer/Documents/icing

Network layout:

mini						www.cmbi.ru.nl	world
apache 80					apache 443
tomcat 8080 (TODO:)


Www has an official requested certificate thru university.
The www machine does url rewriting as shown below.
Internal trafic is not secured.


CONFIGURATION:

/private/etc/apache2
in files:
httpd.conf
extra/httpd-ssl.conf

LOG:
DocumentRoot "/Library/WebServer/Documents/iCing" 
ServerName mini.cmbi.umcn.nl:443
ServerAdmin jurgenfd@gmail.com
ErrorLog "/private/var/log/apache2/error_ssl_log"
TransferLog "/private/var/log/apache2/access_ssl_log"


NOT USED:
SSLCertificateFile "/private/etc/apache2/mini.crt"
SSLCertificateKeyFile "/private/etc/apache2/mini.key"


# Config file for the nmr.cmbi.ru.nl server

<VirtualHost 131.174.88.168:80>
      ServerName nmr.cmbi.ru.nl
      Loglevel warn
      RewriteEngine On
      RewriteRule ^/icing(.*) https://nmr.cmbi.ru.nl/icing/$1 [L,R]
#       RewriteLog /var/log/httpd/nmr.cmbi.ru.nl-rewrite_log
     <Location />
          ProxyPass http://mini.cmbi.umcn.nl/
          ProxyPassReverse http://mini.cmbi.umcn.nl/
  </Location>
  ErrorLog /var/log/httpd/nmr.cmbi.ru.nl-error_log
  CustomLog /var/log/httpd/nmr.cmbi.ru.nl-access_log combined
</VirtualHost>

<VirtualHost 131.174.88.168:443>
  ServerName nmr.cmbi.ru.nl
  ServerAdmin postmaster@cmbi.ru.nl
      Loglevel warn
 SSLEngine on
#       SSLProxyEngine on
  <Location />
         ProxyPass http://nmr.cmbi.umcn.nl/
         ProxyPassReverse http://nmr.cmbi.umcn.nl/
  </Location>

  ErrorLog /var/log/httpd/nmr.cmbi.ru.nl_sec-error_log
  CustomLog /var/log/httpd/nmr.cmbi.ru.nl_sec-access_log combined

  SSLCertificateFile /etc/pki/tls/certs/nmr_cert07102008.pem
  SSLCertificateKeyFile /etc/pki/tls/private/nmr.key
  SSLCertificateChainFile /etc/pki/tls/certs/nmrcachainfile07102008.crt
</VirtualHost>		