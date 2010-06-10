# Obtained thru Tim Stevens.

from cing.Libs.NTutils import * #@UnusedWildImport
import mimetools
import mimetypes
import random
import time
import urllib2

def getRandomKey(size=6):
    """Get a random alphanumeric string of a given size"""
    ALPHANUMERIC = [chr(x) for x in range(48, 58) + range(65, 91) + range(97, 123)]
    #random.shuffle(ALPHANUMERIC)

    n = len(ALPHANUMERIC) - 1
    random.seed(time.time()*time.time())

    return ''.join([ALPHANUMERIC[random.randint(0, n)] for x in range(size)])

#########################################################################################
# Initial code from http://www.voidspace.org.uk/python/cgi.shtml#upload                                                #
#########################################################################################

BOUNDARY = mimetools.choose_boundary()

def encodeForm(fields, files=None, lineSep='\r\n',
               boundary='-----' + BOUNDARY + '-----'):
    """Function to encode form fields and files so that they can be sent to a URL"""

    if not files:
        files = []

    lines = []
    if isinstance(fields, dict):
        fields = fields.items()


    for (key, fileName, value) in files:
        fileType = mimetypes.guess_type(fileName)[0] or 'application/octet-stream'
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, fileName))
        if not fileType.startswith('text'):
            lines.append('Content-Transfer-Encoding: binary')
        lines.append('Content-Type: %s' % fileType)
        #lines.append('Content-Length: %s\r\n' % str(len(value)))
        lines.append('')
        lines.append(value)

    for (key, value) in fields:
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        lines.append('')
        lines.append(value)


    lines.append('--' + boundary + '--')
    lines.append('')

    bodyData = lineSep.join(lines)
    contentType = 'multipart/form-data; boundary=%s' % boundary

    return contentType, bodyData


def sendRequest(url, fields, files=None):
    """Function to send form fields and files to a given URL.
    """

    contentType, bodyData = encodeForm(fields, files)

    headerDict = {'User-Agent': 'anonymous',
                  'Content-Type': contentType,
                  'Content-Length': str(len(bodyData))
                  }

#    NTdebug( "contentType: [%s]" % contentType )
#    NTdebug( "headerDict: [%s]" % headerDict )
#    NTdebug( "bodyData: [%s]" % bodyData )

    #enterRequest = urllib2.Request(url)
    #print urllib2.urlopen(enterRequest).read()
    #time.sleep(2)

#    NTdebug("Requesting form to url: [" + url + "]")
    request = urllib2.Request(url, bodyData, headerDict)

    try:
        response = urllib2.urlopen(request)

    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            msg = 'Connection to server URL %s failed with reason:\n%s' % (url, e.reason)
        elif hasattr(e, 'code'):
            msg = 'Server request failed and returned code:\n%s' % e.code
        else:
            msg = 'Server totally barfed with no reason of fail code'
        NTwarning('Failure', msg)
        return

    return response.read()


