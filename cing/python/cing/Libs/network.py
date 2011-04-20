# Obtained thru Tim Stevens.

from cing.Libs.NTutils import * #@UnusedWildImport
import commands
import mimetools
import mimetypes
import urllib2


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


def sendFileByScp( fileName, targetUrl, ensureDirIsPresent = True, ntriesMax = 2):
    "Returns True for on error"

    userNameAtDomain, targetDir = targetUrl.split(':')
    if ensureDirIsPresent:
        cmdSsh = 'ssh %s mkdir -p %s' % (userNameAtDomain, targetDir)
        NTdebug("cmdSsh: %s" % cmdSsh)
        status, result = commands.getstatusoutput(cmdSsh)
        if status:
            if 'File exists' in result:
                pass # this is ok
            else:
                NTerror("Failed to create remote directory %s by ssh to %s. Status: %s with result %s" % (userNameAtDomain, targetDir, status, result))
                return True
            # end if
        # end if
    # end if
    # -l units are kbit/s
    cmdScp = 'scp %s %s' % (fileName, targetUrl)
#    cmdScp = 'rsync -ave ssh %s %s/' % (fileName, targetUrl)
    NTdebug("cmdScp: %s" % cmdScp)
    for tryCount in range(ntriesMax):
        NTdebug("Try count: %s" % tryCount)
        if tryCount:
            NTwarning("Retrying count: %s" % tryCount)
        status, result = commands.getstatusoutput(cmdScp)
        if not status:
            NTdebug("Succeeded sendFileByScp by command: %s" % cmdScp)
            return
        # end if
        NTerror("Failed to sendFileByScp status: %s with result %s" % (status, result))
    # end for
    NTerror("Failed to sendFileByScp after all %s tries." % ntriesMax)
    return True
# end def

def getFileByRsyncOver( sourceUrl, targetUrl, rsyncOptions = "-r", ntriesMax = 2):
    "Returns True for on error"
    # NB the trailing / just to be sure it goes to a directory.
    # consider using --max-delete=NUM when using delete options.
    cmd = 'rsync %s -ave ssh %s %s/' % (rsyncOptions, sourceUrl, targetUrl)
#    NTdebug("cmd: %s" % cmd)
    for tryCount in range(ntriesMax):
#        NTdebug("Try count: %s" % tryCount)
        if tryCount:
            NTwarning("Retrying count: %s" % tryCount)
        status, result = commands.getstatusoutput(cmd)
        if not status:
            NTdebug("Succeeded sendFileByScp by command: %s" % cmd)
            return
        # end if
        NTerror("Failed to sendFileByScp status: %s with result %s" % (status, result))
    # end for
    NTerror("Failed to sendFileByScp after all %s tries." % ntriesMax)
    return True
# end def

