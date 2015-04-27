# Premisses #

  * Install curl (not needed in future)
  * Install CING (only iCingRobot.py really needed)
  * Rip out the CING dependencies in iCingRobot.py:
```
from cing import cingDirTestsData 
from cing import verbosityDebug
from cing.Libs.NTutils import NTmessage
from cing.Libs.forkoff import do_cmd
```

# Run #

In order to start a full run you need to upload a file and start the run:
```
    doSave  = 1
    doRun   = 1
    doStatus= 0
    doLog   = 0
    doPname = 0
    doPurge = 0
```

Each step produces a response from the iCing web service. For the first step I get:
```
Firing up the iCing robot; aka CCPN Analysis example interface to CING
Curling to: https://nmr.cmbi.ru.nl/icing/serv/iCingServlet
DEBUG: Doing command: curl -F UserId=jd -F AccessKey=123456 -F Action=Save -F UploadFile=@/Users/jd/workspace34/cing/Tests/data/ccpn/1a4d.tgz https://nmr.cmbi.ru.nl/icing/serv/iCingServlet
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed

  0  101k    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100  101k    0    59  100  101k    196   338k --:--:-- --:--:-- --:--:--  845k
{"Action":"Save","Result":"101.00 kb","ExitCode":"Success"}
```

The last string in curly brackets is a dictionary in JSON (javascript object notation). For any request to the service you will get at least these 3 key/value pairs back. Below are the other ones when successful.

```
{"Action":"Run","Result":"started","ExitCode":"Success"}
{"Action":"Status","Result":"notDone","ExitCode":"Success"}
{"Action":"Log","Result":"\n=== .... ===\nCreating Whatif html\n","ExitCode":"Success"}
{"Action":"ProjectName","Result":"1a4d","ExitCode":"Success"}
{"Action":"Purge","Result":"Removed project: /Library/WebServer/Documents/tmp/cing/jd/123456","ExitCode":"Success"}
```

# Retrieve the results #

iCing redirects you to a result frame which contains the links to:
  * The index of the html pages.
  * The zip file with the html pages.
  * The directory containing all input/output data, the CING log, and a zip file with the html pages.

When you use the web service you need to construct these urls yourself. Perhaps using the following code from:
```
http://code.google.com/p/cing/source/browse/trunk/cing/python/cing/Scripts/iCingRobot.py?r=460#75
```
I had to obsolete that code because I couldn't get the secure submit working in python. Tim should be able to do that hopefully;-)

Anyway here it is:
```
    # Fetch output e.g.
#    http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1
    resultBaseUrl = os.path.join(iCingServerBaseUrl, 'tmp/cing', userId, accessKey)
    
    # The entryId is derived from the filename of the deposited ccpn project .tgz file.
    # http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1/1brv.cing/index.html also redirects to:
    # http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1/1brv.cing/1brv/HTML/index.html but the 2nd url
    # might change in the future... use the first and accept the redirect if possible..
    resultHtmlUrl = os.path.join(resultBaseUrl, entryId + ".cing", "index.html")
    # CING validation log file.
    # http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1/cingRun.log
    resultLogUrl = os.path.join(resultBaseUrl, "cingRun.log")
    # Zip with cing project directory structure (including html report) and log.
    # http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1/1brv_CING_report.zip
    resultZipUrl = os.path.join(resultBaseUrl, entryId + "_CING_report.zip")
     
    NTdebug("resultHtmlUrl   : " + resultHtmlUrl)
    NTdebug("resultLogUrl    : " + resultLogUrl)
    NTdebug("resultZipUrl    : " + resultZipUrl)
```
Note that you can always look in the directory using the iCingServerBaseUrl; something like:
```
http://nmr.cmbi.ru.nl
```