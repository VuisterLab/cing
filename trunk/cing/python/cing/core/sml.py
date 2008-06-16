from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import printf
from cing.Libs.NTutils import sprintf

from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTmessage

from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTdict
import os

SMLstarthandlers = {}
SMLendhandlers   = {}
SMLversion       = 0.2
# version history:
#  0.1: initial version
#  0.2: NTlist and NTdict SML handlers; recursion in dict-like handlers

class SMLhandler:
    """
    Base class for decoding of the Simple-markup language storage.

Example file:

<SML> 0.1
<PeakList> n15 keep
<Peak>
    dimension       = 3
    positions       = NTlist(122.892, 1.3480000000000001, 8.0530000000000008)
    height          = 12190.0
    heightError     = 0.0
    hasHeight       = False
    volume          = 0.0
    volumeError     = 0.0
    hasVolume       = False
    atoms           = [('INTERNAL', 'A', 502, 'N'), ('INTERNAL', 'A', 502, 'QB'), ('INTERNAL', 'A', 502, 'HN')]
</Peak>
<Peak>
    dimension       = 3
    positions       = NTlist(121.06, 3.633, 8.1780000000000008)
    height          = 8937.0
    heightError     = 0.0
    hasHeight       = False
    volume          = 0.0
    volumeError     = 0.0
    hasVolume       = False
    atoms           = [('INTERNAL', 'A', 504, 'N'), ('INTERNAL', 'A', 503, 'HA1'), ('INTERNAL', 'A', 504, 'HN')]
</Peak>
</PeakList>
</SML>
    """
    global SMLstarthandlers, SMLendhandlers

    def __init__(self, name):
        self.startTag = sprintf('<%s>', name)
        self.endTag   = sprintf('</%s>', name)
        self.name     = name
        self.debug    = False

        SMLstarthandlers[self.startTag] = self
        SMLendhandlers[self.endTag]     = self

    def __str__(self):
        return sprintf('<SMLhandler %s>', self.name )

    def listHandler(self, listObj, fp, project=None):
        """
        General list handling routine. Parses items and append to
        listObj.

        Returns listObj or None on error.
        """
        line = SMLhandler.readline( fp )
        if self.debug: NTmessage('%s> %s', self, line)
        while (line):
#            if len(line) > 0 and SMLendhandlers.has_key(line[1]):
#                handler = SMLendhandlers[line[1]]
#                if (handler != self):
#                    NTerror('Error SMLhandler.listHandler: badly formed SML list (%s)\n', line[1] )
#                    return None
#                #end if
#                handler.endHandler( listObj, project )
#                return listObj
#            elif len(line) > 0 and SMLstarthandlers.has_key(line[1]):
#                handler = SMLstarthandlers[line[1]]
#                listObj.append( handler.handle( line, fp, project ) )
#            else:
#                listObj.append( eval(line[0]) )
#            #end if
#            line = SMLhandler.readline( fp )
#            if self.debug: NTmessage('%s> %s', self, line)

            if len(line) > 0 and line[1] == self.endTag:
                self.endHandler( listObj, project )
                return listObj
            elif len(line) > 0 and SMLstarthandlers.has_key(line[1]):
                listObj.append( SMLstarthandlers[line[1]].handle( line, fp, project ) )
            else:
                listObj.append( eval(line[0]) )
            #end if
            line = SMLhandler.readline( fp )
            if self.debug: NTmessage('%s> %s', self, line)

        #end while
        # we should not be here
        NTerror('Error SMLhandler.listHandler: unterminated list\n')
        return None
    #end def

    def dictHandler(self, dictObj, fp, project=None):
        """
        General dict handling routine. Parses key = value pairs and inserts into
        dictObj.

        Returns dictObj or None on error.
        """
        line = SMLhandler.readline( fp )
        if self.debug: NTmessage('%s> %s', self, line)
        while (line):


#            if len(line) > 0 and SMLendhandlers.has_key(line[1]):
#                handler = SMLendhandlers[line[1]]
#                if (handler != self):
#                    NTerror('Error SMLhandler.dictHandler: badly formed SML list (%s)\n', line[0] )
#                    return None
#                #end if
#                handler.endHandler( dictObj, project )
#                return dictObj
#            # version 0.2: implement recursion
#            elif len(line) > 3 and SMLstarthandlers.has_key(line[3]):
##                handler = SMLstarthandlers[line[3]]
##                obj     = SMLstarthandlers[line[3]].handle( line[3:], fp, project )
#                dictObj[line[1]] = SMLstarthandlers[line[3]].handle( line[3:], fp, project )
#            elif len(line) > 3:
#                dictObj[line[1]] = eval(''.join(line[3:]))
#            else:
#                NTerror('Error SMLhandler.dictHandler: incomplete line "%s"\n', line[0])
#            #end if
#            line = SMLhandler.readline( fp )
#            if self.debug: printf('%s> %s\n', self, line)

            if len(line) > 0 and line[1]==self.endTag:
                self.endHandler( dictObj, project )
                return dictObj
            # version 0.2: implement recursion
            elif len(line) > 3 and SMLstarthandlers.has_key(line[3]):
                dictObj[line[1]] = SMLstarthandlers[line[3]].handle( [''.join(line[3:])] + line[3:], fp, project )
            elif len(line) > 3:
                dictObj[line[1]] = eval(''.join(line[3:]))
            else:
                NTerror('Error SMLhandler.dictHandler: incomplete line "%s"\n', line[0])
            #end if
            line = SMLhandler.readline( fp )
            if self.debug: printf('%s> %s\n', self, line)

        #end while
        # we should not be here
        NTerror('Error SMLhandler.dictHandler: unterminated dict\n')
        return None
    #end def

    def handle(self, line, fp, project=None ):
        """
        This method should be subclassed to fit specific needs in the actual class.
        The code could serve as a starting point or dictHandler or listHandler could be
        called:

        e.g.
            object = myObject( arguments )
            return self.listHandler( object, line, fp, project )

        Should return a object or None on error

        The code below implements handling of the SML 'root'
        """
        #print 'entering>', self.startTag
        obj  = None
        line = SMLhandler.readline( fp )
        if self.debug: NTmessage('%s> %s', self, line)
        while (line):
            #rint '>>>', len(line), SMLendhandlers.has_key(line[1])
            if len(line) > 0 and SMLendhandlers.has_key(line[1]):
                handler = SMLendhandlers[line[1]]
                #print '>>>', handler
                if (handler != self):
                    NTerror('Error SMLhandler.handle: badly formed SML list (%s)\n', line[1] )
                    return None
                #end if
                #print 'returning>'
                return handler.endHandler( obj, project )
            elif len(line) > 0 and SMLstarthandlers.has_key(line[1]):
                handler = SMLstarthandlers[line[1]]
                obj     = handler.handle( line, fp, project )
            else:
                NTerror('Error SMLhandler.handle: incomplete line "%s"\n', line[0])
            #end if
            line = SMLhandler.readline( fp )
            if self.debug: NTmessage('%s> %s', self, line)
        #end while
        return obj
    #end def

    def endHandler(self, obj, project=None):
        """
        This method should be sub-classed to fit specific needs in the actual class.
        Should return obj or None on error
       """
        return obj
    #end def

    def toSML(self, obj, fp):
        """
        This method should be subclassed to fit specific needs in the actual class.
        Should return obj or None on error
        """
        fprintf( fp, '%s\n', self.startTag )
        # code should be here
        fprintf( fp, '%s\n', self.endTag )
        return obj
    #end def

    def list2SML(self, theList, fp ):
        """
        Write element of theList to fp for restoring later with fromFile method
        Returns theList or None on error.
        """
        fprintf( fp, '%s %s %s\n', self.startTag, theList.name, theList.status )
        for item in theList:
            item.SMLhandler.toSML( item, fp )
        #end for
        fprintf( fp, '%s\n', self.endTag )
        return theList
    #end def

    def readline( fp ):
        """
        Static method to read a line from fp, split it
        return an list instance with line and splitted line
        """
        line = fp.readline()
        if len(line) == 0: return None
        line = line[0:-1]
#        result = NTlist(line, *line.split())
        #print '>', result, '<'
        # Much quicker then previous NTlist stuff!
        return [line]+line.split()
    #end def
    readline = staticmethod( readline )

    def fromFile( fileName, project=None)   :
        """
        Static method to restore object from SML file.
        Returns obj or None on error.
        """
        if not os.path.exists( fileName ):
            NTerror('Error SMLhandler.fromFile: file "%s" does not exist\n', fileName )
            return None
        #end if
        fp   = open( fileName, 'r' )
        obj  = smlhandler.handle( None, fp, project )
        fp.close()
        NTdebug('Restored %s from "%s"', obj, fileName )
        return obj
    #end def
    fromFile = staticmethod( fromFile )

    def toFile(self, object, fileName)   :
        """
        Save element of theList to fileName for restoring later with fromFile method
        Returns object or None on error.
        """
        fp = open( fileName, 'w' )
        if not fp:
            NTerror('SMLhandle.toFile: opening "%s"\n', fileName)
            return None
        #end if
        fprintf( fp, '%s %s\n', smlhandler.startTag, SMLversion )

        if not hasattr(object,'SMLhandler'):
            NTerror('SMLHandle.toFile: object "%s" without SMLhandler method', object)
            fp.close()
            return None

        object.SMLhandler.toSML( object, fp )
        fprintf( fp, '%s\n', smlhandler.endTag )

        NTdebug('saved %s to "%s"', object, fileName )
        #end if
        return object
    #end def
#end class

# make one instance of the class that takes care of the basic things; i.e. initial first parse and inclusion of
# <SML> and </SML> tags
smlhandler = SMLhandler(name='SML')

# Make SML handler for NTlist
class SMLNTlistHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'NTlist' )
    #end def

    def handle(self, line, fp, project=None):
        listObj = NTlist()
        return self.listHandler(listObj, fp, project)
    #end def

    def toSML(self, theList, fp):
        """
        Write element of l to fp for restoring later with fromFile method
        Returns theList or None on error.
        """
        fprintf( fp, '%s\n', self.startTag )
        for item in theList:
            if hasattr(item,'SMLhandler'):
                item.SMLhandler.toSML( item, fp )
            else:
                fprintf( fp, 's\n', repr(item) )
            #end if
        #end for
        fprintf( fp, '%s\n', self.endTag )
        return theList
    #end def
#end class
NTlist.SMLhandler = SMLNTlistHandler()

# Make SMLhandlers for NTdict
class SMLNTdictHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'NTdict' )
    #end def

    def handle(self, line, fp, project=None):
        dictObj = NTdict()
        return self.dictHandler(dictObj, fp, project)
    #end def

    def toSML(self, theDict, fp):
        """
        Write key value pairs of theDict to fp for restoring later with fromFile method
        Returns theDict or None on error.
        """
        fprintf( fp, '%s\n', self.startTag )
        for key,value in theDict.iteritems():
            fprintf( fp, '%s = ', key )
            if hasattr(value,'SMLhandler'):
                value.SMLhandler.toSML( value, fp )
            else:
                fprintf( fp, '%s\n', repr(value) )
            #end if
        #end for
        fprintf( fp, '%s\n', self.endTag )
        return theDict
    #end def
#end class
NTdict.SMLhandler = SMLNTdictHandler()

def obj2SML( obj, smlFile ):
    """
    Generate SML file from object.
    Return obj or None on error
    """
    if smlhandler.toFile(obj, smlFile) == None:
        return None
    return obj
#end def

def SML2obj( smlFile, externalObject=None ):
    """
    Generate obj from smlFile
    """
    obj = smlhandler.fromFile(smlFile, externalObject)
    return obj
#end def


# Just testing
if __name__ == "__main__":

    NTdict.SMLhandler.debug = True

    a = NTdict(aap=1,noot=2,mies=3)
    b = NTdict(dd=a, kess=4)
    print repr(a), repr(b)


    obj2SML( b, 'bla2.sml')

    c = SML2obj( 'bla2.sml')

    print repr(a), repr(b), repr(c), repr(c.dd)
