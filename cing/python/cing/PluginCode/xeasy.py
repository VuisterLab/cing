"""
Adds import/export of xeasy files in CYANA/XEASY or CYANA2 format


Methods:
        
  importXeasy( seqFile, protFile, convention ):
        Import shifts from Xeasy protFile           

  importXeasyPeaks( seqFile, protFile, peakFile, convention ):
        Import peaks from Xeasy peakFile; requires matching seqFile,protFile 
        returns PeakList instance or None on error
        
  export2Xeasy( ):
        Export to Xeasy in CYANA/XEASY and CYANA2 formats
        
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import sprintf
from cing.core.classes import Peak
from cing.core.classes import PeakList
from cing.core.constants import CYANA
from cing.core.constants import CYANA2
from cing.core.constants import CYANA_NON_RESIDUES
from cing.core.constants import INTERNAL
from cing.core.constants import X_AXIS
from cing.core.dictionaries import isValidAtomName
from cing.core.dictionaries import isValidResidueName
from cing.core.dictionaries import translateAtomName
from cing.core.molecule import allResidues
import os

#==============================================================================
class Xeasy( NTdict ):
    """Class to parse and store some Xeasy stuff
       Read seqFile, prot file and peaks file 
    """
    def __init__( self, seqFile, protFile, convention, verbose=1 ):
        NTdict.__init__( self )
        
        # parse the seqFile
        self.seq = {}
        resNum = 1
        self.resCount = 0
        for f in AwkLike( seqFile ):
            if (not f.isEmpty() and not f.isComment( '#')):
                if ( f.dollar[1] in CYANA_NON_RESIDUES         # skip the bloody CYANA non-residue stuff
                   ):
                    pass

                elif (not isValidResidueName( f.dollar[1], convention ) ):
                    NTerror( 'ERROR Xeasy: residue "%s" invalid for convention "%s" in "%s:%d"\n',
                             f.dollar[1], convention, seqFile, f.NR
                           )
                    self.error = 1
                else:
                    if (f.NF > 1):
                        resNum = f.int(2)
                        if resNum == None: 
                            self.error = 1
                        #end if
                    #endif
                    self.seq[ resNum ] = f.dollar[1] # store original 'convention' name
                    resNum += 1
                    self.resCount += 1
                #end if
            #end if
        #end for
        self.seqFile = seqFile
        self.convention = convention
        
        # parse the prot file
        self.prot = {}
        self.protCount = 0
        self.error = 0
        for f in  AwkLike( protFile ):
            if (f.NF == 5):
                # Xeasy/Cyana atom index
                index = f.int( 1 )
                atomName  = f.dollar[4]
                resNum    = f.int( 5 )
                if (resNum not in self.seq):
                    NTerror( 'ERROR Xeasy: undefined residue number %d in "%s:%d" (%s)\n',
                             resNum, protFile, f.NR, f.dollar[0]
                           )
                    self.error = 1
                else:
                    resName   = self.seq[resNum]
                    if (not isValidAtomName( resName, atomName, convention)):
                        NTerror( 'ERROR Xeasy: invalid atom "%s" for residue "%s %d" in "%s:%d" (%s)\n',
                                  atomName, resName, resNum, protFile, f.NR, f.dollar[0]
                               ) 
                        self.error = 1
                    else:
                        p = NTdict(index     = index,
                                     shift     = f.float( 2 ),
                                     error     = f.float( 3 ),
                                     atomName  = atomName,
                                     resNum    = resNum,
                                     resName   = resName,
                                     atom      = None
                                    )
                        self.prot[ index ] = p
                        self.protCount += 1
                    #end if
                #end if
            #end if
        #end for
        
        self.protFile = protFile
        if verbose:
            NTmessage('==> Xeasy: parsed %d residues, %d atoms from %s, %s\n', 
                      self.resCount, self.protCount, self.seqFile,self.protFile 
                     )
        #end if
    #end def
            
    def map2molecule( self, molecule ):
        """map entries of the prot-dict onto an atom of molecule
        """
        chain = molecule.chains[0]
        for p in self.prot.itervalues():
            if p.resNum in chain:
                res = chain[p.resNum]
                aName = translateAtomName(self.convention, p.resName, p.atomName,INTERNAL)
                if aName in res:
                    p.atom = res[aName]
                else:
                    NTerror('ERROR Xeasy.map2molecule: Xeasy atom "%s" not mapped on "%s"\n', 
                             p.atomName, res
                           )                    
                #end if
            else:
                NTerror('ERROR Xeasy.map2molecule: residue "%s%d" not defined in %s\n', p.resName, p.resNum, molecule.name )
            #end if
        #end for
    #end def
    
    def appendShifts( self, molecule, verbose = 1 ):
        """append the shifts to molecule
        """
        self.map2molecule( molecule )
        
        # first set NONE shift for all atoms
        molecule.newResonances()
        
        # now update the values
        for p in self.prot.itervalues():
            if (p.atom != None):
                p.atom.resonances().value = p.shift
                p.atom.resonances().error = p.error
            #end if
        #end for
        
        if verbose:
            NTmessage('==> Xeasy.appendShifts: appended shifts to molecule %s\n', molecule )
        #end if

    #end def
    

    def importPeaks( self, molecule, peakFile, status='keep', verbose=True ):
        """Read Xeasy peak file
           returns a PeaksList instance or None on error
        """
        #print '>>', molecule, peakFile, verbose 
        
        self.map2molecule( molecule )
    
        _path,name,_ext = NTpath( peakFile )
        peaks = PeakList( name=name, status=status ) 


        dimension = 0
        for f in  AwkLike( peakFile ):
            if (f.NR == 1 and f.NF == 5): 
                dimension = f.int(5)
            
            elif (not f.isComment('#') ):
#                 if (f.NF == 12):
#                     dimension = 2
#                 elif (f.NF == 13 or f.NF == 14 or (f.NF>):
#                     dimension = 3
#                 else:
#                     NTerror('ERROR Xeasy.importPeaks: invalid number of fields (%d) in file "%s" on line %d (%s)\n', 
#                              f.NF, peakFile, f.NR, f.dollar[0]
#                            )
#                     return None
#                 #end if
                if (dimension == 0):
                    NTerror('ERROR Xeasy.importPeaks: invalid dimensionalty in file "%s" (line %d, "%s")\n', 
                             peakFile, f.NR, f.dollar[0]
                           )
                    return None
                #end if
      
                cur = 1

                # preserve the Xeasy peak id
                peakId = f.int( cur ) 
                if (peakId == None): return None
                cur += 1

                peakpos = []
                for _i in range(X_AXIS, dimension):
                    p = f.float( cur )
                    if (p == None): return None
                    peakpos.append( p )
                    cur += 1
                #end if
          
                cur += 2 # skip two fields 
                height = f.float( cur )
                if height == None: return None
                cur += 1
                heightError = f.float( cur )
                if heightError == None: return None
                cur += 1
      
                resonances = []
                error = 0
                cur += 2 # skip two fields
                for _i in range(X_AXIS, dimension):
                    aIndex = f.int( cur )
                    if aIndex == None: return None
                    cur += 1                         
                    # 0 means unassigned according to Xeasy convention
                    if aIndex == 0:
                        resonances.append( None )
                    else:
                        if not aIndex in self.prot:
                            NTerror('ERROR Xeasy.importPeaks: invalid atom id %d on line %d (%s)\n',
                                     aIndex, f.NR, f.dollar[0]
                                   )
                            error = 1
                            break
                        else:
                            atom = self.prot[ aIndex].atom
                            resonances.append( atom.resonances() )
                        #end if
                    #end if
                #end for
    
                if not error:
                    peak = Peak( dimension=dimension,
                                 positions=peakpos,
                                 height=height, heightError=heightError,
                                 resonances = resonances,
                                )
                    # store original peak id
                    peak.xeasyIndex = peakId
                    peaks.append( peak )
                #end if
            #end if
        #end for

        if verbose:
            NTmessage('==> Xeasy.importPeaks: extracted %d peaks from %s\n', len(peaks), peakFile )
        #end if
  
        return peaks
    #end def
#end class

#==============================================================================
def exportShifts2Xeasy( molecule, seqFile, protFile, convention, verbose=1 ):
    """Export shifts to Xeasy prot and seq file
       not be called directly: use export2xeasy

    """
    if not molecule:
        NTerror( 'Error exportShifts2Xeasy: undefined molecule\n' )
        return
    #end if

#   export seq file
    fout = open( seqFile, 'w' )
    resCount = 0
    for res in allResidues( molecule ):
        resName = res.translate(convention)
        if (resName != None):
            fprintf( fout, '%3s %4d\n', 
                     resName,
                     res.resNum
                   )
        #end if
        resCount += 1
    #end for
    fout.close()      

#   export prot file
    fout = open( protFile, 'w' )
    idx  = 1
    for atom in molecule.allAtoms():
        cyanaName = atom.translate(convention)        
        if (cyanaName != None and atom.resonances() != None ):
            atom.xeasyIndex = idx
            fprintf( fout, '%4d %7.3f %5.3f %-4s %4d\n', 
                     atom.xeasyIndex, atom.resonances().value, atom.resonances().error,
                     cyanaName, atom._parent.resNum
                   )
            idx += 1
        #end if
    #end for
    fout.close()
      
    if verbose:
        NTmessage( '==> Exported %s in %s format to "%s" and "%s"\n', molecule, convention, seqFile, protFile )
    #end if
#end def
    

#==============================================================================
def exportPeaks2Xeasy( peakList, peakFile, verbose=True ):
  """Export peaks to peakFile in xeasy format; 
     routine assumes that exportShifts2xeasy is called first: this sets the 
     xeasyIndex value of each atom and generates matching seq and prot-files.
     
     not be called directly: use export2xeasy
     
     Modifying attributes:
     
     xeasyColor: for peakList or peak
     xeasyIndex: for peak
  """
  if peakList==None:
      NTerror('exportPeaks2Xeasy: undefined peak list\n' )
      return
  #end if
  if len(peakList) == 0:
      NTerror('exportPeaks2Xeasy: zero-length peak list\n' )
      return
  #end if
      
  fout = open( peakFile, 'w' )
  # write header
  dimension = peakList[0].dimension
  fprintf( fout, '# Number of dimensions %d\n', dimension )
  for i in range(X_AXIS, dimension):
      fprintf( fout, '#INAME %d ?\n', i+1 )
  #end for

  # write the peaks
  count = 0
  for peak in peakList:
      if hasattr( peak, 'xeasyIndex'):
          idx = peak.xeasyIndex
      else:
          idx = peak.peakIndex
      #end if
      fprintf( fout, '%4d ', idx )
      
      for i in range(X_AXIS, dimension):
          fprintf( fout, '%7.3f ', peak.positions[i] )
      #end for
    
      if hasattr( peak, 'xeasyColor'):
          color = peak.xeasyColor
      elif hasattr( peakList, 'xeasyColor'):
          color = peakList.xeasyColor
      else:
          color = 1
      #end if
      fprintf( fout, '%1d U         ', color )
      
      fprintf( fout, '%10.3e %9.2e ', peak.height, peak.heightError )  
      fprintf( fout, '-   0 ' )
      for i in range (X_AXIS, dimension):
          if peak.isAssigned( i ):
              fprintf( fout, '%4d ', peak.resonances[i].atom.xeasyIndex )
          else:
              fprintf( fout, '%4d ', 0 )
          #end if
      #end for
      fprintf( fout, '0\n' )
      count += 1
  #end for
      
  fout.close()
      
  if verbose:
    NTmessage( '==> Exported %s to "%s"\n', peakList, peakFile )
  #end if
  
#end def


def importXeasy( project, seqFile, protFile, convention ):
        """Import shifts from Xeasy protFile
        return the 'slot' (i.e position in the list) of these resonances or None on error
        """
        if seqFile == None:
            NTerror('ERROR importXeasy: undefined seqFile\n' )
            return None
        #end if
        if protFile == None:
            NTerror('ERROR importXeasy: undefined protFile\n' )
            return None
        #end if
            
        if not os.path.exists( seqFile ):
            NTerror('ERROR importXeasy: seqFile "%s" not found\n', seqFile )
            return None
        #end if
        if not os.path.exists( protFile ):
            NTerror('ERROR importXeasy: protFile "%s" not found\n', protFile )
            return None
        #end if

#       Parse the seq file and prot file
        project.xeasy = Xeasy( seqFile, protFile, convention = convention, verbose = False )
#       Append the shifts to molecule
        project.xeasy.appendShifts( project.molecule, verbose = False )

        project.addHistory( sprintf('Imported Xeasy shifts from "%s"', protFile ) )
        
        if project.parameters.verbose():
            if project.xeasy.error:
                NTmessage( '==> importXeasy: error(s) appending resonances from "%s"\n', protFile )
            else:
                NTmessage( '==> importXeasy: appended resonances from "%s"\n', protFile )   
            #end if
#            NTmessage( '%s\n', project.molecule.format() )
        #end if
        return project.molecule.resonanceCount-1
#end def

def importXeasyPeaks( project, seqFile, protFile, peakFile, convention ):
        """Import peaks from Xeasy peakFile; requires matching seqFile,protFile 
        return PeakList instance or None on error
        """
        if seqFile == None:
            NTerror('ERROR importXeasyPeaks: undefined seqFile\n' )
            return None
        #end if
        if protFile == None:
            NTerror('ERROR importXeasyPeaks: undefined protFile\n' )
            return None
        #end if
        if peakFile == None:
            NTerror('ERROR importXeasyPeaks: undefined peakFile\n' )
            return None
        #end if
        if not os.path.exists( seqFile ):
            NTerror('ERROR importXeasyPeaks: seqFile "%s" not found\n', seqFile )
            return None
        #end if
        if not os.path.exists( protFile ):
            NTerror('ERROR importXeasyPeaks: protFile "%s" not found\n', protFile )
            return None
        #end if
        if not os.path.exists( peakFile ):
            NTerror('ERROR importXeasyPeaks: peakFile "%s" not found\n', peakFile )
            return None
        #end if

#       Parse the seq file and prot file
        project.xeasy = Xeasy( seqFile, protFile, convention = convention, verbose = False )
#       Extract the peaks
        peaks = project.xeasy.importPeaks( project.molecule, peakFile, verbose = False )
#       Append to project
        project.appendPeakList( peaks, verbose = False )
        
        project.addHistory( sprintf('Imported Xeasy peaks from "%s"', peakFile ) )
        
        if project.parameters.verbose():
            if project.xeasy.error:
                NTmessage( '==> importXeasyPeaks: new %s from "%s" completed with error(s)\n', peaks, peakFile )
            else:
                NTmessage( '==> importXeasyPeaks: new %s from "%s"\n', peaks, peakFile )   
            #end if
        #end if
        return peaks
#end def

def export2Xeasy( project, tmp=None ):
        """Export to shift and peaks to Xeasy in CYANA and CYANA2 formats
        """
        for molName in project.molecules:
            #Xeasy/Cyana 1.x format
            fileName = project.path( project.directories.xeasy, project[molName].name )
            exportShifts2Xeasy(  project[molName], 
                                 seqFile=fileName+'.seq', 
                                 protFile=fileName+'.prot', 
                                 convention=CYANA,
                                 verbose=project.parameters.verbose()
                              )
            #Cyana 2.x format
            fileName = project.path( project.directories.xeasy2, project[molName].name )        
            exportShifts2Xeasy(  project[molName], 
                                 seqFile=fileName+'.seq', 
                                 protFile=fileName+'.prot', 
                                 convention=CYANA2,
                                 verbose=project.parameters.verbose()
                              )
        #end if

        idx = 1
        for pl in project.peaks:
            if (pl.status == 'keep'):
                #print '>', pl, idx
                # add xeasyIndex to peak, go in steps of 10000 for succesive
                # peaklists
                for peak in pl:
                    peak.xeasyIndex = idx
                    idx += 1
                #end for
                while (idx%10000): idx += 1
                
                #Xeasy/Cyana 1.x format
                peakFile = project.path( project.directories.xeasy, pl.name+'.peaks' )
                exportPeaks2Xeasy( pl, peakFile, verbose = project.parameters.verbose() )
                #Cyana 2.x format
                peakFile = project.path( project.directories.xeasy2, pl.name+'.peaks' )
                exportPeaks2Xeasy( pl, peakFile, verbose = project.parameters.verbose() )
            #end if
        #end for
#end def

# register the functions
methods  = [(importXeasy, None),
            (importXeasyPeaks, None)
           ]
saves    = []
restores = []
exports  = [(export2Xeasy, None)]

#print '>>at the end'


