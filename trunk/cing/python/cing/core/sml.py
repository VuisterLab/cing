from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import printf
from cing.Libs.NTutils import sprintf

from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTdebug

from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTdict
# do not remove these two: they are needed during parsing of the sml files
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTvalue
from cing.core.molecule import Coordinate #@UnusedImport

from cing.core.molecule import Molecule
from cing.core.molecule import Chain
from cing.core.molecule import Residue
from cing.core.molecule import Atom
from cing.core.molecule import Resonance

from cing.core.classes import Peak
from cing.core.classes import PeakList

from cing.core.classes import DistanceRestraint
from cing.core.classes import DistanceRestraintList

from cing.core.classes import DihedralRestraint
from cing.core.classes import DihedralRestraintList

from cing.core.classes import RDCRestraint
from cing.core.classes import RDCRestraintList

from cing.core.constants import CYANA

#The following imports we need for restoring the project
from cing.Libs.fpconst import NaN as nan #@UnresolvedImport @UnusedImport

import os
import sys

SMLstarthandlers = {}
SMLendhandlers   = {}
SMLversion       = 0.221
# version history:
#  0.1: initial version
#  0.2: NTlist and NTdict SML handlers; recursion in dict-like handlers
#  0.21: Explicitly require endHandler to return obj or None on error.
#  0.22: SML Molecule, Chain, Residue, Atom handlers
#  0.221: Atom saves shiftx

SMLsaveFormat  = CYANA
SMLfileVersion = None

class SMLhandler:
    """
    Base class for decoding of the Simple-markup language storage.

Example file:

<SML> 0.221
<PeakList> n15 keep
<Peak>  3  0
    positions       = NTlist(122.892, 1.3480000000000001, 8.0530000000000008)
    height          = (12190.0, 0.0)
    volume          = (nan, nan)
    xeasyIndex      = 20000
    resonances      = NTlist(('refine2', 'A', 502, 'N', None, 0, 'CYANA'), ('refine2', 'A', 502, 'QB', None, 0, 'CYANA'), ('refine2', 'A', 502, 'HN', None, 0, 'CYANA'))
</Peak>
<Peak>  3  1
    positions       = NTlist(121.06, 3.9929999999999999, 8.1780000000000008)
    height          = (6104.0, 0.0)
    volume          = (nan, nan)
    xeasyIndex      = 20001
    resonances      = NTlist(('refine2', 'A', 504, 'N', None, 0, 'CYANA'), ('refine2', 'A', 503, 'HA1', None, 0, 'CYANA'), ('refine2', 'A', 504, 'HN', None, 0, 'CYANA'))
</Peak>
</PeakList>
</SML>
    """
    global SMLstarthandlers, SMLendhandlers
    debug = False

    def __init__(self, name):
        self.startTag = sprintf('<%s>', name)
        self.endTag   = sprintf('</%s>', name)
        self.name     = name

        SMLstarthandlers[self.startTag] = self
        SMLendhandlers[self.endTag]     = self

    def __str__(self):
        return sprintf('<SMLhandler %s>', self.name )

    def listHandler(self, listObj, fp, obj=None):
        """
        General list handling routine. Parses items and append to
        listObj.

        Returns listObj or None on error.
        """
        line = SMLhandler.readline( fp )
        while (line):
#            if len(line) > 0 and SMLendhandlers.has_key(line[1]):
#                handler = SMLendhandlers[line[1]]
#                if (handler != self):
#                    NTerror('Error SMLhandler.listHandler: badly formed SML list (%s)', line[1] )
#                    return None
#                #end if
#                handler.endHandler( listObj, obj )
#                return listObj
#            elif len(line) > 0 and SMLstarthandlers.has_key(line[1]):
#                handler = SMLstarthandlers[line[1]]
#                listObj.append( handler.handle( line, fp, obj ) )
#            else:
#                listObj.append( eval(line[0]) )
#            #end if
#            line = SMLhandler.readline( fp )
#            if self.debug: NTmessage('%s> %s', self, line)

            if len(line) > 0 and line[1] == self.endTag:
                return self.endHandler( listObj, obj )
            elif len(line) > 0 and SMLstarthandlers.has_key(line[1]):
                listObj.append( SMLstarthandlers[line[1]].handle( line, fp, obj ) )
            else:
                listObj.append( eval(line[0]) )
            #end if
            line = SMLhandler.readline( fp )

        #end while
        # we should not be here
        NTerror('SMLhandler.listHandler: unterminated list')
        return None
    #end def

    def dictHandler(self, dictObj, fp, obj=None):
        """
        General dict handling routine. Parses key = value pairs and inserts into
        dictObj.

        Returns dictObj or None on error.
        """
        line = SMLhandler.readline( fp )
        while (line):


#            if len(line) > 0 and SMLendhandlers.has_key(line[1]):
#                handler = SMLendhandlers[line[1]]
#                if (handler != self):
#                    NTerror('Error SMLhandler.dictHandler: badly formed SML list (%s)', line[0] )
#                    return None
#                #end if
#                handler.endHandler( dictObj, obj )
#                return dictObj
#            # version 0.2: implement recursion
#            elif len(line) > 3 and SMLstarthandlers.has_key(line[3]):
##                handler = SMLstarthandlers[line[3]]
##                obj     = SMLstarthandlers[line[3]].handle( line[3:], fp, obj )
#                dictObj[line[1]] = SMLstarthandlers[line[3]].handle( line[3:], fp, obj )
#            elif len(line) > 3:
#                dictObj[line[1]] = eval(''.join(line[3:]))
#            else:
#                NTerror('Error SMLhandler.dictHandler: incomplete line "%s"', line[0])
#            #end if
#            line = SMLhandler.readline( fp )
#            if self.debug: printf('%s> %s\n', self, line)

            if len(line) > 0 and line[1]==self.endTag:
                return self.endHandler( dictObj, obj )
            # version 0.2: implement recursion
            elif len(line) > 3 and SMLstarthandlers.has_key(line[3]):
                dictObj[line[1]] = SMLstarthandlers[line[3]].handle( [''.join(line[3:])] + line[3:], fp, obj )
            elif len(line) > 3:
                dictObj[line[1]] = eval(''.join(line[3:]))
            else:
                NTerror('SMLhandler.dictHandler: incomplete line "%s"', line[0])
            #end if
            line = SMLhandler.readline( fp )

        #end while
        # we should not be here
        NTerror('SMLhandler.dictHandler: unterminated dict')
        return None
    #end def

    def handle(self, line, fp, obj=None ):
        """
        This method should be subclassed to fit specific needs in the actual class.
        The code could serve as a starting point or dictHandler or listHandler could be
        called:

        e.g.
            object = myObject( arguments )
            return self.listHandler( object, line, fp, obj )

        Should return a object or None on error

        The code below implements handling of the SML 'root'
        """
        global SMLfileVersion

        SMLfileVersion = float(line[2])

        newObj  = None
        line = SMLhandler.readline( fp )
        while (line):
            if len(line) > 0 and line[1]==self.endTag:
                return self.endHandler( newObj, obj )
            elif len(line) > 0 and SMLstarthandlers.has_key(line[1]):
                handler = SMLstarthandlers[line[1]]
                newObj  = handler.handle( line, fp, obj )
            else:
                NTerror('SMLhandler.handle: incomplete line "%s"', line[0])
            #end if
            line = SMLhandler.readline( fp )
        #end while
        # we should not be here
        NTerror('SMLhandler.handle: unterminated %s', self)
        return None
    #end def

    def endHandler(self, newObj, obj=None):
        """
        This method should be sub-classed to fit specific needs in the actual class.
        Should return newObj or None on error
       """
        return newObj
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
        if SMLhandler.debug: printf('%s> %s\n', SMLfileVersion, [line]+line.split())
        return [line]+line.split()
    #end def
    readline = staticmethod( readline )

    def fromFile( fileName, obj=None)   :
        """
        Static method to restore object from SML file.
        Returns obj or None on error.
        """
        if not os.path.exists( fileName ):
            NTerror('Error SMLhandler.fromFile: file "%s" does not exist\n', fileName )
            return None
        #end if
        fp   = open( fileName, 'r' )
        line = SMLhandler.readline( fp )
        if len(line) > 0 and SMLstarthandlers.has_key(line[1]):
            handler = SMLstarthandlers[line[1]]
            newObj  = handler.handle( line, fp, obj )
        else:
            NTerror('SMLhandler.fromFile: invalid SML file line "%s"', line[0])
#        newObj  = smlhandler.handle( None, fp, obj )
        fp.close()
        NTdebug('Restored %s from "%s"', newObj, fileName )
        return newObj
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

    def handle(self, line, fp, obj=None):
        listObj = NTlist()
        return self.listHandler(listObj, fp, obj)
    #end def

    def toSML(self, theList, stream=sys.stdout):
        """
        Write element of theList to stream for restoring later with fromFile method
        Returns theList or None on error.
        """
        fprintf( stream, '%s\n', self.startTag )
        for item in theList:
            if hasattr(item,'SMLhandler') and item.SMLhandler != None:
                item.SMLhandler.toSML( item, stream )
            else:
                fprintf( stream, '%r\n', item )
            #end if
        #end for
        fprintf( stream, '%s\n', self.endTag )
        return theList
    #end def
#end class
NTlist.SMLhandler = SMLNTlistHandler()

# Make SMLhandlers for NTdict
class SMLNTdictHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'NTdict' )
    #end def

    def handle(self, line, fp, obj=None):
        dictObj = NTdict()
        return self.dictHandler(dictObj, fp, obj)
    #end def

    def toSML(self, theDict, stream=sys.stdout):
        """
        Write key value pairs of theDict to stream for restoring later with fromFile method
        Returns theDict or None on error.
        """
        fprintf( stream, '%s\n', self.startTag )
        for key,value in theDict.iteritems():
            fprintf( stream, '%s = ', key )
            if hasattr(value,'SMLhandler') and value.SMLhandler != None:
                value.SMLhandler.toSML( value, stream )
            else:
                fprintf( stream, '%r\n', value )
            #end if
        #end for
        fprintf( stream, '%s\n', self.endTag )
        return theDict
    #end def
#end class
NTdict.SMLhandler = SMLNTdictHandler()


class SMLMoleculeHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'Molecule' )
    #end def

    def handle(self, line, fp, _tmp=None):
        # The handle restores the attributes of Molecule
        # Explicitly encode it because we want on the fly action for _sequence

        nameTuple = eval(' '.join(line[2:]))
        mol = Molecule( nameTuple[0] )

        line = SMLhandler.readline( fp )
        while (line):
            if len(line) > 0 and line[1]==self.endTag:
                return self.endHandler( mol, None )
            # version 0.2: implement recursion
            elif len(line) > 3 and line[1]=='_sequence'  and SMLstarthandlers.has_key(line[3]):
                _sequence = SMLstarthandlers[line[3]].handle( [''.join(line[3:])] + line[3:], fp, mol )
                # Restore the sequence
                #print '>>', _sequence
                for chain, resName, resNum, convention in _sequence:
                    mol._addResidue( chain, resName, resNum, convention )
                #end for
            elif len(line) > 3 and SMLstarthandlers.has_key(line[3]):
                mol[line[1]] = SMLstarthandlers[line[3]].handle( [''.join(line[3:])] + line[3:], fp, mol )
            elif len(line) > 3:
                mol[line[1]] = eval(''.join(line[3:]))
            else:
                NTerror('SMLMoleculeHandler.handle: incomplete line "%s"', line[0])
            #end if
            line = SMLhandler.readline( fp )

        #end while
        # we should not be here
        NTerror('SMLMoleculeHandler.handle: unterminated %s', self)
        return None
    #end def

    def endHandler(self, mol, _tmp=None):
        # Restore linkage
        mol.chains = mol._children
        mol._check()
        return mol
    #end def

    def toSML(self, mol, stream=sys.stdout ):
        """
        Write SML code for chain to stream
        """
        # Generate a sequence list
        mol._sequence = NTlist()
        for res in mol.allResidues():
            mol._sequence.append( ( res.chain.name,
                                    res.translate(SMLsaveFormat) ,
                                    res.resNum,
                                    SMLsaveFormat
                                   )
                                )

        fprintf( stream, "%s  %r\n", self.startTag, mol.nameTuple(SMLsaveFormat) )

#       Can add attributes here; update endHandler if needed
        for a in ['resonanceCount','resonanceSources','modelCount','ranges']:
            if mol.has_key(a):
                fprintf( stream, '%s = %r\n', a, mol[a] )
        #end for
        fprintf( stream, '_sequence = ')
        mol._sequence.toSML( stream )

        fprintf( stream, 'chains = ')
        mol.chains.toSML( stream )

        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
#register this handler
Molecule.SMLhandler = SMLMoleculeHandler()


class SMLChainHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'Chain' )
    #end def

    def handle(self, line, fp, molecule=None):
        # The handle restores the attributes of chain
        # Needs a valid molecule
        #print 'Chain.handle>', line, len(line)
        if molecule == None: return None

        nameTuple = eval(' '.join(line[2:]))
        #print '>>', nameTuple, len(nameTuple)

        chain = molecule.decodeNameTuple(nameTuple)
        if chain == None:
            NTerror('SMLChainHandler.handle: invalid nameTuple %s', nameTuple)
            return None
        #end if
        return self.dictHandler(chain, fp, molecule)
    #end def

    def endHandler(self, chain, molecule=None):
        # Restore linkage
        chain.residues = chain._children
        return chain
    #end def

    def toSML(self, chain, stream=sys.stdout ):
        """
        Write SML code for chain to stream
        """
        # print value, error, model ontag line to speed up parsing and initialization
        fprintf( stream, "%s  %r\n", self.startTag, chain.nameTuple(SMLsaveFormat) )
#       Can add attributes here; update endHandler if needed
        for a in []:
            fprintf( stream, '%s = %r\n', a, chain[a] )
        #end for

        fprintf( stream, 'residues = ')
        chain.residues.toSML( stream )

        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
#register this handler
Chain.SMLhandler = SMLChainHandler()


class SMLResidueHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'Residue' )
    #end def

    def handle(self, line, fp, molecule=None):
        # The handle restores the attributes of atom
        # Needs a valid molecule
        if molecule == None: return None

        nameTuple = eval(' '.join(line[2:]))
        res = molecule.decodeNameTuple(nameTuple)
        if res == None:
            NTerror('SMLResidueHandler.handle: invalid nameTuple %s', nameTuple)
            return None
        #end if
        return self.dictHandler(res, fp, molecule)
    #end def

    def endHandler(self, res, molecule=None):
        # Restore linkage
        res.atoms = res._children
        return res
    #end def

    def toSML(self, res, stream=sys.stdout ):
        """
        Write SML code for residue to stream
        """
        fprintf( stream, "%s  %r\n", self.startTag, res.nameTuple(SMLsaveFormat) )
#       Can add attributes here; update endHandler if needed
        for a in []:
            fprintf( stream, '%s = %r\n', a, res[a] )
        #end for

        fprintf( stream, 'atoms = ')
        res.atoms.toSML( stream )

        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
#register this handler
Residue.SMLhandler = SMLResidueHandler()


class SMLAtomHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'Atom' )
    #end def

    def handle(self, line, fp, molecule=None):
        # The handle restores the attributes of atom
        # Needs a valid molecule
        if molecule == None: return None

        nameTuple = eval(' '.join(line[2:]))
        atm = molecule.decodeNameTuple(nameTuple)
        if atm == None:
            NTerror('SMLAtomHandler.handle: invalid nameTuple %s', nameTuple)
            return None
        #end if
        return self.dictHandler(atm, fp, molecule)
    #end def


    def endHandler(self, atm, molecule=None):
        # Restore the required linkages and indices
        for i,r in enumerate(atm.resonances):
            r.atom = atm
            r.resonanceIndex = i

        for i,c in enumerate(atm.coordinates):
            c.atom = atm
            c.model = i
        return atm
    #end def

    def toSML(self, atm, stream=sys.stdout ):
        """
        Write SML code for atom to stream
        """
        fprintf( stream, "%s  %r\n", self.startTag, atm.nameTuple(SMLsaveFormat) )
#       Can add attributes here; update endHandler if needed
        for a in ['shiftx']:
            if atm.has_key(a):
                fprintf( stream, '%s = %r\n', a, atm[a] )
        #end for

        # coordinates; only write when present
        if len(atm.coordinates) > 0:
            fprintf(stream,"coordinates = ")
            atm.coordinates.toSML( stream )
        # resonances; only write when present
        if len(atm.resonances) > 0:
            fprintf(stream,"resonances = ")
            atm.resonances.toSML( stream )

        # Minimize the number of lines by not outputting the default values
        if atm.stereoAssigned:
            fprintf( stream, 'stereoAssigned = True\n' )
        #end if

        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
#register this handler
Atom.SMLhandler = SMLAtomHandler()


#class SMLCoordinateHandler( SMLhandler ):
#
#    def __init__(self):
#        SMLhandler.__init__( self, name = 'Coordinate' )
#    #end def
#
#    def handle(self, line, fp, molecule=None):
#        # Explicit coding saved ca 30%
#        c = Coordinate(x=float(line[2]), y=float(line[3]), z=float(line[4]), Bfac=float(line[5]),occupancy=float(line[6]))
#        c.model = int(line[7])
#        line = self.readline( fp )
#        c.atomNameTuple = eval(line[0])
##        return self.dictHandler(c, fp, molecule)
#        line = self.readline( fp )
#        if line[0] == self.endTag:
#            self.endHandler(c, obj)
#            return c
#        #end if
#        # We should not be here
#        NTerror('SMLCoordinateHandler.handle: missing Coordinate endTag')
#        return None
#    #end def
#
#    def endHandler(self, c, molecule):
#        # Map the atomNameTuple
#        if obj == None: return None
#        atm = molecule.decodeNameTuple(c.atomNameTuple)
#        if atm == None:
#            NTerror('SMLCoordinateHandler.endHandler: invalid atomNameTuple (%s)', c.atomNameTuple)
#            return None
#        #end if
#        c.atom = atm
#        atm.coordinates.append(c)
#        return c
#    #end def
#
#    def toSML(self, c, stream ):
#        """
#            For coordinate
#        """
##        fprintf( stream, "%s\n", self.startTag)
##        for a in ['x','y','z','Bfac','occupancy','model']:
##            fprintf( stream, '%s = %s\n', a, repr(c[a]) )
##        #end for
#
#        # print x,y,z,Bfac,occupancy, model ontag line to speed up parsing and initialization
#        fprintf( stream, "%s %.3f %.3f %.3f %.3f %.3f %d\n",
#                         self.startTag,
#                         c.e[0], c.e[1], c.e[2],
#                         c.Bfac, c.occupancy,
#                         c.model
#               )
#        fprintf( stream, '%s\n', repr( c.atom.nameTuple(SMLsaveFormat) ) )
##        Can add attributes here; update handle
##        for a in ['model']:
##            fprintf( stream, '%s = %s\n', a, repr(c[a]) )
#        #end for
#
#        fprintf( stream, "%s\n", self.endTag )
#    #end def
##end class
#Coordinate.SMLhandler = SMLCoordinateHandler()

#Resonance inherits the SMLhandler from NTdict: that we do not want, so unassign it
Resonance.SMLhandler = None

class SMLPeakHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'Peak' )
    #end def

    def handle(self, line, fp, project=None):
        if SMLfileVersion <= 0.21:
            # older SML format <= 0.2
            pk = Peak( 0 )
        else:
            pk = Peak( int(line[2]) )
        return self.dictHandler(pk, fp, project)
    #end def

    def endHandler(self, pk, project):
        if project == None:
            NTerror('Error SMLPeakHandler.endHandler: Undefined project\n')
            return None
        #end if
        if project.molecule == None:
            NTerror('Error SMLPeakHandler.endHandler: Undefined molecule\n')
            return None
        #end if

        if SMLfileVersion <= 0.21:
            pk.resonances = NTfill(None,pk.dimension)
            pk.positions  = NTlist(*pk.positions)
            del(pk['hasHeight'])
            del(pk['hasVolume'])
            pk.height = NTvalue( pk.height, pk.heightError, Peak.HEIGHT_VOLUME_FORMAT, Peak.HEIGHT_VOLUME_FORMAT2 )
            del(pk['heightError'])
            pk.volume = NTvalue( pk.volume, pk.volumeError, Peak.HEIGHT_VOLUME_FORMAT, Peak.HEIGHT_VOLUME_FORMAT2 )
            del(pk['volumeError'])

            ### REMARK: This restoring of resonances is dangerous, because it is not guranteed that the order and hence last
            #           resonance of atoms is always the same. Needs reviewing !!!

            # Check if we have to make the linkage
            if pk.atoms and project.molecule:
                #print '>>',pk.atoms
                for i in range(pk.dimension):
                    if pk.atoms[i] != None:
                        atm = project.molecule.decodeNameTuple(pk.atoms[i])
                        pk.resonances[i] = atm.resonances()
                    else:
                        pk.resonances[i] = None
                    #end if
                #end for
            #end if
        else:
            pk.height = NTvalue(pk.height[0],pk.height[1], Peak.HEIGHT_VOLUME_FORMAT, Peak.HEIGHT_VOLUME_FORMAT2)
            pk.volume = NTvalue(pk.volume[0],pk.volume[1], Peak.HEIGHT_VOLUME_FORMAT, Peak.HEIGHT_VOLUME_FORMAT2)
            pk.resonances = decode(pk.resonances, project)
        #end if
        return pk
    #end def

    def toSML(self, peak, fp):
        """
        Version 0.22: Use the encode for resonances
        """
        fprintf( fp, '%s  %d  %d\n', self.startTag, peak.dimension, peak.peakIndex )
        for a in ['positions']:
            fprintf( fp, '    %-15s = %r\n', a, peak[a] )
        #end for

        # special cases
        for a in ['height','volume']:
            fprintf( fp, '    %-15s = %r\n', a, peak[a].toTuple() )
        #end for
        if peak.has_key('xeasyIndex'):
            fprintf( fp, '    %-15s = %r\n', 'xeasyIndex', peak['xeasyIndex'] )
        # Resonances
        fprintf( fp, '    %-15s = %r\n', 'resonances', encode( peak.resonances ))
        fprintf( fp, '%s\n', self.endTag )
    #end def

#end class
Peak.SMLhandler = SMLPeakHandler()

class SMLPeakListHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'PeakList' )
    #end def

    def handle(self, line, fp, project=None):
        pl = PeakList( *line[2:] )
        if not self.listHandler(pl, fp, project): return None
        if project: project.peaks.append( pl )
        return pl
    #end def

    def toSML(self, pl, fp):
        return self.list2SML( pl, fp )
#end class
PeakList.SMLhandler = SMLPeakListHandler()

class SMLDistanceRestraintHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'DistanceRestraint' )
    #end def

    def handle(self, line, fp, project=None):
        dr = DistanceRestraint( *line[2:] )
        return self.dictHandler(dr, fp, project)
    #end def

    def endHandler(self, dr, project):
        # Parse the atomPairs tuples, map to molecule
        if project == None or project.molecule == None: return dr
        aps = dr.atomPairs
        dr.atomPairs = NTlist()
        for ap in aps:
            dr.appendPair( (project.molecule.decodeNameTuple(ap[0]), project.molecule.decodeNameTuple(ap[1])) )
        #end for
        return dr
    #end def

    def toSML(self, dr, stream ):
        """
            For DistanceRestraint
        """
        fprintf( stream, "%s\n", self.startTag )
        for a in ['lower','upper' ]:
            fprintf( stream, '    %-15s = %s\n', a, repr(dr[a]) )
        #end for

        rl = []
        for r in dr.atomPairs:
            rl.append((r[0].nameTuple(SMLsaveFormat),r[1].nameTuple(SMLsaveFormat)))
        #end for
        fprintf( stream, '    %-15s = %s\n', 'atomPairs', repr( rl ) )
        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
DistanceRestraint.SMLhandler = SMLDistanceRestraintHandler()


class SMLDistanceRestraintListHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'DistanceRestraintList' )
    #end def

    def handle(self, line, fp, project=None):
        drl = DistanceRestraintList( *line[2:] )
        if not self.listHandler(drl, fp, project): return None
        project.distances.append( drl )
        return drl
    #end def

    def toSML(self, drl, fp):
        self.list2SML( drl, fp )
    #end def
#end class
DistanceRestraintList.SMLhandler = SMLDistanceRestraintListHandler()


class SMLDihedralRestraintHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'DihedralRestraint' )
    #end def

    def handle(self, line, fp, project=None):
        dr = DihedralRestraint( atoms=[], upper = 0.0 , lower =0.0 )
        return self.dictHandler(dr, fp, project)
    #end def

    def endHandler(self, dr, project):
        # Parse the atoms nameTuples, map to molecule
        dr.atoms = decode( dr.atoms, project.molecule )
        return dr
    #end def

    def toSML(self, dr, stream ):
        """
        """
        fprintf( stream, "%s\n", self.startTag )
        for a in ['lower','upper' ]:
            fprintf( stream, '    %-15s = %s\n', a, repr(dr[a]) )
        #end for
        fprintf( stream, '    %-15s = %s\n', 'atoms', repr(encode(dr.atoms)) )

        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
DihedralRestraint.SMLhandler = SMLDihedralRestraintHandler()

class SMLDihedralRestraintListHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'DihedralRestraintList' )
    #end def

    def handle(self, line, fp, project=None):
        drl = DihedralRestraintList( *line[2:] )
        if not self.listHandler(drl, fp, project): return None
        project.dihedrals.append( drl )
        return drl
    #end def

    def toSML(self, drl, fp):
        self.list2SML( drl, fp )
    #end def
#end class
DihedralRestraintList.SMLhandler = SMLDihedralRestraintListHandler()


class SMLRDCRestraintHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'RDCRestraint' )
    #end def

    def handle(self, line, fp, project=None):
        dr = RDCRestraint( atoms=[], upper = 0.0 , lower =0.0 )
        return self.dictHandler(dr, fp, project)
    #end def

    def endHandler(self, dr, project):
        # Parse the atoms nameTuples, map to molecule
        if project == None or project.molecule == None: return dr
        aps = dr.atomPairs
        dr.atomPairs = NTlist()
        for ap in aps:
            dr.appendPair( (project.molecule.decodeNameTuple(ap[0]), project.molecule.decodeNameTuple(ap[1])) )
        #end for
        return dr
    #end def

    def toSML(self, dr, stream ):
        """
            For RDCRestraint (based on DistanceRestraint)
        """
        fprintf( stream, "%s\n", self.startTag )
        for a in ['lower','upper' ]:
            fprintf( stream, '    %-15s = %s\n', a, repr(dr[a]) )
        #end for

        rl = []
        for r in dr.atomPairs:
            rl.append((r[0].nameTuple(SMLsaveFormat),r[1].nameTuple(SMLsaveFormat)))
        #end for
        fprintf( stream, '    %-15s = %s\n', 'atomPairs', repr( rl ) )
        fprintf( stream, "%s\n", self.endTag )
    #end def
#end class
RDCRestraint.SMLhandler = SMLRDCRestraintHandler()


class SMLRDCRestraintListHandler( SMLhandler ):

    def __init__(self):
        SMLhandler.__init__( self, name = 'RDCRestraintList' )
    #end def

    def handle(self, line, fp, project=None):
        drl = RDCRestraintList( *line[2:] )
        if not self.listHandler(drl, fp, project): return None
        project.rdcs.append( drl )
        return drl
    #end def

    def toSML(self, drl, fp):
        self.list2SML( drl, fp )
    #end def
#end class
RDCRestraintList.SMLhandler = SMLRDCRestraintListHandler()



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

#-----------------------------------------------------------------------------
# Two handy (?) routines
#-----------------------------------------------------------------------------

def encode( objects ):
    """Return a list of nametuples encoding the molecule objects (chains, residues, atoms)
    """
    result = NTlist()
    for obj in objects:
        if (obj == None):
            result.append(None)
        else:
            result.append( obj.nameTuple(SMLsaveFormat) )
        #end if
    #end for
    return result
#end def

def decode( nameTuples, refObj ):
    """
    Return a list objects, decoding the nametuples relative to refObj
    """
    result = NTlist()
    for nt in nameTuples:
        if refObj == None or nt == None:
            result.append(None)
        else:
            result.append( refObj.decodeNameTuple( nt ) )
        #end if
    #end for
    return result
#end def

# Just testing
if __name__ == "__main__":

    SMLhandler.debug = True

    a = NTdict(aap=1,noot=2,mies=3)
    b = NTdict(dd=a, kess=4)
    print repr(a), repr(b)


    obj2SML( b, 'bla2.sml')

    c = SML2obj( 'bla2.sml')

    print repr(a), repr(b), repr(c), repr(c.dd)
