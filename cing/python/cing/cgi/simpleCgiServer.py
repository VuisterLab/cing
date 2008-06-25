#!PYTHON_EXECUTABLE
# -1- First setup cing:
#     Localized by ant build.xml script.
import sys
sys.path.insert(0, "CING_ROOT_PYTHON")
sys.stderr = sys.stdout # Errors from python script will need to flow to user.        

from cgi import FieldStorage
from cing import verbosityDebug
from cing import verbosityOutput
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.core.classes import Project
from cing.core.constants import IUPAC
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTmessage
import cgitb; 
import cing
import os

class SimpleCgiServer():
    MAX_FILE_SIZE_BYTES = 1024 * 1024 * 50
    def __init__(self):
        self.logUrl = 'log.txt'
        self.form = None
        self.footer = """<div id="footer">
    <p>Contact
    <a href="mailto:vuister@science.ru.nl">Geerten Vuister</a>, 
    <a href="mailto:jurgend@cmbi.ru.nl">Jurgen F. Doreleijers</a> or 
    <a href="mailto:alanwilter@gmail.com">Alan Wilter Sousa da Silva</a></p>
    </div>
    for help, when required."""
        self.timer = """
<SCRIPT LANGUAGE="JavaScript">
<!-- Hide script>
    var seconds = 0
    var minutes = 0
    var hours = 0
    var timerID = setTimeout("showtime()",1000);

    function showtime() { 
      seconds ++;
      if (seconds == 60) {
       seconds=0;
       minutes ++;
      }
      if (minutes == 60){
        minutes=0;
        hours ++;
      }
      if (hours == 24){
        hours = 0;
      }
      var timeValue =""+(hours)
      timeValue +=((minutes < 10) ? ":0" : ":")+minutes
      timeValue +=((seconds < 10) ? ":0":":")+seconds
      document.clock.face.value = timeValue;
      timerID = setTimeout("showtime()",1000);
    }
// End script hiding --></SCRIPT>";        
    
    """
        NTmessage( "Content-Type: text/html\n" )     # HTML is following # blank line, end of headers
        
    def main(self):
        NTmessage( "<TITLE>CGI script output</TITLE>")
        NTmessage( "<H1>This is my first CGI script</H1>")
        NTmessage( "Hello, worldddd!")
        NTerror( "Where does this error show up/")
        NTmessage( "Hello, CING!")
        
        
        
        #os.putenv('HOME', '/Users/jd/Sites/tmp/cing') # not recommended on mac os for memory leaks may occur.
        
        # Note that other environment variables needed by CING need to be inhereted from
        # the script that started apache by using the PassEnv directive in the apache
        # settings file.
        
#        keyList = os.environ.keys()
#        keyList.sort()
#        for key in keyList:
#            NTdebug(  "<p>key: [" + key + '] value: [' + os.environ[key] + ']')
            
        # Localized by ant build.xml script.
        
        
        
        #import cgi
        #". Do not use "from cgi import *" -- the module defines all sorts of names for 
        # its own use or for backward compatibility that you don't want in your namespace.
        ACCESS_KEY      = "ACCESS_KEY"
#        PROJECT_FILE    = "PROJECT_FILE"
        COOR_FILE       = "COOR_FILE"
        DO_WHATIF       = "DO_WHATIF" # absent when unchecked.
        DO_PROCHECK     = "DO_PROCHECK"
        DO_IMAGES       = "DO_IMAGES"
        
        keyListExpected = [ ACCESS_KEY, COOR_FILE ]
         
        self.form = FieldStorage()
#        NTmessage('<p>Found form: [%s]' % form)
        keyFormList = self.form.keys()
        keyFormList.sort()
        for key in keyFormList:
            value = ''
            element = self.form[key]
            if hasattr(element, 'value'):
                value = self.form[key].value[:80]
            if hasattr(element, 'checked'):
                value = "checked was set to: " + self.form[key].checked
            NTmessage(  "<p>Found key [%s] and value first 80 char(s): [%s]" % (key, value))
        for expectedKey in keyListExpected:
            if not self.form.has_key(expectedKey):
                self.endError("Missing self.form field: [" + expectedKey + 
                         ']\n<BR>All together expecting: ' + `keyListExpected` )
            NTmessage(  "<p>Found expected key [%s] and value first 80 char(s): [%s]" % (expectedKey, self.form[expectedKey].value[:80]))
        #NTmessage(  "<p>PROJECT_FILE:", self.form["PROJECT_FILE"].value
        
        # -3- Settings by self.form
        doWhatif   =      self.form.has_key( DO_WHATIF )  and self.form[DO_WHATIF].value   == 'on'
        doProcheck =      self.form.has_key( DO_PROCHECK) and self.form[DO_PROCHECK].value == 'on'
        htmlOnly   = not (self.form.has_key( DO_IMAGES)   and self.form[DO_IMAGES].value   == 'on')
        NTmessage(  "<p>doWhatif     %3s" % doWhatif)
        NTmessage(  "<p>doProcheck   %3s" % doProcheck)
        NTmessage(  "<p>htmlOnly     %3s" % htmlOnly)
        
        # JFD not sure if the absolute address should be used in order to get the cingDirTmp setting
        # changed for all. It should not be changed between different instances of the apache launched 
        # python versions either. The CING_SERVER_TMP is localized on installation. On the development
        # machine this is: /Users/jd/Sites/tmp/cing. With content like: 4A2EM9kt/1brv.cing/index.html
        # -2- Then other imports
#        cgitb.enable(display=1, logdir="CING_SERVER_TMP")
        cgitb.enable()
        access_key_value = self.form[ACCESS_KEY].value
        cing.cingDirTmp = os.path.join( "CING_SERVER_TMP", access_key_value )
        cingDirTmp = cing.cingDirTmp
        if os.path.exists(cingDirTmp):
            if removedir(cingDirTmp):
                self.endError("The tmp dir already existed and could not be removed: %s" % cingDirTmp)
        if os.mkdir(cingDirTmp):
            self.endError("Failed to create new dir: %s" % cingDirTmp)
        if os.chdir(cingDirTmp):
            self.endError("Failed to change to dir: %s" % cingDirTmp)
            
            
        
        fileitem = self.form[COOR_FILE]
        if not fileitem.file:
            self.endError("Please provide a PDB_FILE actual file.")    
        #    If an error is encountered when obtaining the contents of an uploaded file (for example, when the user interrupts the form 
        #submission by clicking on a Back or Cancel button) the done attribute of the object for the field will be set to the value -1.
        if fileitem.done == -1:
            self.endError("The send file was not 'done' please retry.")    
        atomcount = 0
        while 1:
            line = fileitem.file.readline()
            if not line: 
                break
            if line.startswith("ATOM"):
                atomcount += 1
        NTmessage(  "<pre>Found uploaded atom count:    %9d" % atomcount)
        totalTimeInSecondsExpected = 2. # Just for some html
        numberOfAtomsPerResidue = 10.
        residueCount = atomcount / numberOfAtomsPerResidue
        NTmessage(  "Estimated number of residues:      %4d" % residueCount)
        perResidueTimeTotal = 1/100. # Just for some html
        if doWhatif:
             totalTimeInSecondsExpected += 10 # Biggest effort is in actually running WI.
             perResidueTimeTotal += 1/13.
        if doProcheck:
             perResidueTimeTotal += 1/30.
             totalTimeInSecondsExpected += 30# Biggest effort is in ps2pdf conversions
        if not htmlOnly:
             perResidueTimeTotal += 1. # Per residue plots.
             totalTimeInSecondsExpected += 3 # Molmol image generation.
        overallTime = totalTimeInSecondsExpected+perResidueTimeTotal*residueCount
        NTmessage(  "Estimated time per residue:    %8.3f" % perResidueTimeTotal)
        NTmessage(  "Estimated time independent of size: %3d" % totalTimeInSecondsExpected)
        NTmessage(  "Estimated total time:               %3d" % overallTime)
        NTmessage(  "</pre>")
        
        self.save_uploaded_file (form_field=COOR_FILE, upload_dir=cingDirTmp)
            
        pdbConvention = IUPAC
#        restraintsConvention = CYANA
        _directory, basename, _extension = NTpath( fileitem.filename )
        entryId = basename
            
            
        #if entryId.startswith("1YWUcdGMP"):
        #    pdbConvention = XPLOR
        #if entryId.startswith("2hgh"):
        #    pdbConvention = CYANA
        #if entryId.startswith("1tgq"):
        #    pdbConvention = PDB                        
        NTmessage( self.timer )
        NTmessage(  "<pre>")
        project = Project.open( entryId, status='new' )
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cingDirTmp, pdbFileName)
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
        NTmessage(  "</pre>")
        #NTdebug("Reading files from directory: " + cyanaDirectory)
        #kwds = {'uplFiles': [ entryId ],
        #        'acoFiles': [ entryId ]         
        #          }
        if project.save():
            self.endError( 'Failed to save project.')
            
        NTmessage(  "<pre>")
        if project.validate(htmlOnly=htmlOnly,doProcheck=doProcheck, doWhatif=doWhatif ):
            self.endError( 'Failed to run the validate step.' )
        NTmessage(  "</pre>")
        
        # Localized in ant script.
        # SERVER_CGI_URL_TMP is like: localhost/~jd/tmp/cing
        tmpUrl = os.path.join( "SERVER_CGI_URL_TMP", access_key_value)        
        cingResultUrl = os.path.join( tmpUrl, entryId+".cing", "index.html")
        NTmessage(  '<P>Please find the results <a href="http://%s"> here </A>' % cingResultUrl)
        NTmessage(  '<P>Your uploads and logs are available from <a href="http://%s"> here </A>' % tmpUrl)
        
    def endError( self, message ):    
#        reference2Log = "Please inspect the log %s" % self.logUrl
        NTerror( "<P>"+message+self.footer )
#        sys.stderr = initial_stderr
#        NTerror( message )         
        sys.exit(1)
        
    def save_uploaded_file (self, form_field, upload_dir):
        """This saves a file uploaded by an HTML form.
           The form_field is the name of the file input field from the form.
           For example, the following form_field would be "file_1":
               <input name="file_1" type="file">
           The upload_dir is the directory where the file will be written.
           If no file was uploaded or if the field does not exist then
           this does nothing.
        """
        if not self.form.has_key(form_field): 
            self.endError( 'Failed to find form field ['+form_field+']' )
        fileitem = self.form[form_field]
        if not fileitem.file: 
            self.endError( 'Failed to find form field ['+form_field+']' )
        if fileitem.done == -1:
            self.endError("The send file [%s] was not 'done' please retry." % form_field)
        if len(fileitem.value) > self.MAX_FILE_SIZE_BYTES:
            self.endError("The send file [%s] was larger than the allowed number of bytes compare: [%s] and [%s]" % 
                          (fileitem.filename, len(fileitem.value) , self.MAX_FILE_SIZE_BYTES))
            
        fullFileName = os.path.join(upload_dir, fileitem.filename)     
        fout = file(fullFileName, 'wb')        
        while 1:
            chunk = fileitem.file.read(100000)
            if not chunk:
                break
            fout.write (chunk)
        fout.close()
        NTdebug('Saved file: [%s]' % fullFileName)
        
if __name__ == '__main__':
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    cgiServer = SimpleCgiServer()
    cgiServer.main()

