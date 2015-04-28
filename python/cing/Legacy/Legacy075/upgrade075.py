import os
import cing
import cing.Legacy.Legacy100.upgrade100
import cing.Libs.io as io
import cing.core.classes as classes
import cing.core.molecule as molecule
import cing.Libs.NTutils as ntu
import cing.Libs.xmlTools as xmlTools

def upgrade075(project, restore):
    """
    Upgrade project from 075 or earlier conventions
    return upgraded project or None on error
    """
    io.message('upgrade075: converting from CING version {0}\n', project.version)

    # 0.75 version had moleculeNames stored in molecules attribute
    # >=0.76 version molecules is a ProjectList instance
    project.moleculeNames = project.molecules

    # store the project file and reopen to have correct settings
    project._save2json()
    pr = classes.Project._restoreFromJson(project.path(cing.cingPaths.project))
    if pr == None:
        io.error('upgrade075: conversion from version %s failed on read\n', project.version)
        return None

    for molName in pr.moleculeNames:
        pathName = pr.path(cing.directories.molecules, molName) # old reference, versions 0.48-0.75
        if pr.version <= 0.48:
            pathName = pr.path('Molecules', molName) # old reference
        # end if
        io.debug('upgrade075: trying molecule conversion from {0}\n', pathName)
        if not pathName.exists():
            io.error('upgrade075: old molecule pathName "{0}" does not exist\n', pathName)
            return None
        mol = openMol_075(pathName)
        if not mol:
            io.error('upgrade075: conversion from version {0} failed on molecule {1}\n', project.version, molName)
            return None
        pathName.removedir()
        # Save molecule to new format
        mol.save(pr.molecules.path(molName))
    #end for

    # restore
    pr.restore()
    # Save to consolidate
    pr.save()

    return cing.Legacy.Legacy100.upgrade100.upgrade100(pr, restore)
#end def


# version <= 0.91: old sequence.dat defs
# version 0.92: xml-sequence storage, xml-stereo storage
# Superseded by SML routines >0.93
# 0.94 storage of molecule specific database stuff
NTmolParameters = ntu.NTdict(
    version        = 0.92,
    contentFile    = 'content.xml',
    sequenceFile   = 'sequence.xml',
    resonanceFile  = 'resonances.dat',
    coordinateFile = 'coordinates.dat',
    stereoFile     = 'stereo.xml'
)

##old code
#     def _save075( self, path = None)   :
#         """Save sequence, resonances, stereo assignments and coordinates in <=0.75 format
#
#            gwv 13 Jun 08: Return self or None on error
#         """
#         if not path:
#             path = self.name + '.NTmol'
#
#         content = NTdict( name = self.name, convention = INTERNAL )
#         content.update( NTmolParameters )
#         content.saveAllXML()
#         content.keysformat()
#         xmlfile = os.path.join( path, NTmolParameters.contentFile )
#         if (obj2XML( content, path=xmlfile ) != content):
#             nTerror('Molecule.save: writing xml file "%s" failed', xmlfile)
#             return None
#         #end if
#         self.content = content
#         self._saveSequence(   os.path.join( path, NTmolParameters.sequenceFile   ) )
#         self._saveResonances(  os.path.join( path, NTmolParameters.resonanceFile  ) )
#         self._saveStereoAssignments( os.path.join( path, NTmolParameters.stereoFile ) )
#         self._saveCoordinates( os.path.join( path, NTmolParameters.coordinateFile ) )
# #        nTdetail('==> Saved %s to "%s"', self, smlFile) # smlFile was undefined.
#         nTdetail('==> Saved %s to "%s"', self )
#         return self
#     #end def


def openMol_075( path )   :
    """Static method to restore molecule from directory path
       implements the <=0.75 storage model
       returns Molecule instance or None on error
    """
    # old format

    content = xmlTools.xML2obj( path=os.path.join( path, NTmolParameters.contentFile ) )
    if not content:
        io.error('openMol_075: error reading xml file "{0}"\n',
                 os.path.join( path, NTmolParameters.contentFile )
                )
        return None
    #end if
    content.keysformat()
    io.debug('openMol_075: content from xml-file: %s', content.format())

    mol = molecule.Molecule( name = content.name )
    if not mol:
        io.error('openMol_075: initializing molecule\n')
        return None
    #end if

    mol.content = content
    if content.has_key('sequenceFile') and \
       restoreSequence(mol, os.path.join(path, content.sequenceFile)) is None:
        return None
    if content.has_key('resonanceFile') and \
        restoreResonances(mol, os.path.join(path, content.resonanceFile), append=False) < 0:
        return None
    if content.has_key('stereoFile') and \
       restoreStereoAssignments(mol, os.path.join(path, content.stereoFile)) < 0:
        return None
    if content.has_key('coordinateFile') and \
       restoreCoordinates(mol, os.path.join(path, content.coordinateFile), append=False) is None:
        return None

    mol._check()
    mol.updateAll()

    return mol
#end def

 ## old code
    # def _saveSequence( self, fileName ):
    #     """Write a xml sequence file.
    #     return self or None on error
    #     """
    #     sequence = NTlist()
    #     for res in self.allResidues():
    #         # append a tuple
    #         sequence.append( ( res.chain.name,
    #                            res.db.translate(CYANA),
    #                            res.resNum,
    #                            CYANA
    #                          )
    #                        )
    #     #end for
    #     if obj2XML( sequence, path=fileName ) != sequence:
    #         nTerror('Molecule._saveSequence: writing xml sequence file "%s"', fileName)
    #         return None
    #     #end if
    #     return self
    # #end def

def restoreSequence( molecule, sequenceFile ):
    """Restore sequence from sequenceFile.
    Return self or None on error.
    """
    if (not os.path.exists( sequenceFile ) ):
        io.error('Molecule.restoreSequence: sequenceFile "{0}" not found\n',
                 sequenceFile
               )
        return None
    #end if
    # compatibility
    if molecule.content.version < 0.92:
        fileObject = open(sequenceFile, 'r')
        for line in fileObject:
            exec(line)
        #end for
        fileObject.close()
    else:
        sequence = xmlTools.xML2obj( sequenceFile )
        if sequence is None:
            io.error('restoreSequence: error parsing xml-file "{0}"', sequenceFile)
            return None
        for chainId, resName, resNum, convention in sequence:
            molecule.addResidue( chainId, resName, resNum, convention )
        #end for
    #end if
    return molecule
#end def


## old code
#     def _saveResonances( self, fileName ):
#         """Write a plain text file with code for saving resonances
#         """
#         fp = open( fileName, 'w' )
# #        fprintf( fp, 'self.resonanceCount = %d\n', self.resonanceCount )
#         for atm in self.allAtoms():
#             for r in atm.resonances:
#                 fprintf( fp, 'self%s.addResonance( value=%s, error=%s )\n',
#                               atm.cName2( 2 ),
#                               repr(r.value), repr(r.error)
#                        )
#             #end for
#         #end for
#         fp.close()
#         #nTdebug('Molecule.saveResonances: %s', fileName)
#     #end def

def restoreResonances( molecule, fileName, append = True ):
    """Restore resonances from fileName
       Optionally append to existing settings
       Return resonanceCount or -1 on error
    """
    if not os.path.exists( fileName ):
        io.error('restoreResonances: file "{0}" not found\n', fileName )
        return -1
    #end if
    if not append:
        molecule.initResonances()
    #end if

    #execfile( fileName )
    # 25 Sep 2007: Explicit coding, less memory, better:
    file = open(fileName, 'r')
    for line in file:
        exec(line)
    #end for
    file.close()

    resonanceCount = len(molecule.resonanceSources)
    #nTdebug('Molecule.restoreResonances: %s (%d)', fileName, resonanceCount)
    return resonanceCount
#end def

##old code
    # def _saveStereoAssignments( self, stereoFileName ):
    #     """
    #     Save the stereo assignments to xml stereoFileName.
    #     Return self of None on error
    #     """
    #     stereo = NTlist()
    #     for atm in self.allAtoms():
    #         if atm.isStereoAssigned():
    #             stereo.append( atm.nameTuple(convention=CYANA) )
    #         #endif
    #     #end for
    #     if obj2XML(stereo, path=stereoFileName) != stereo:
    #         nTerror('Molecule._saveStereoAssignments: write xml-file "%s" failed', stereoFileName)
    #         return None
    #     #end if
    #
    #     #nTdebug('Molecule.saveStereoAssignments: saved %d stereo assignments to "%s', len(stereo), stereoFileName)
    #     return self
    # #end def

def restoreStereoAssignments( molecule, stereoFileName ):
    """
    Restore the stereo assignments from xml stereoFileName,
    return count or -1 on error
    """
    if not os.path.exists( stereoFileName ):
        return -1

    stereo = xmlTools.xML2obj(stereoFileName)
    if stereo is None:
        io.error('restoreStereoAssignment: parsing xml-file "{0}"\n', stereoFileName)
        return -1
    #end if

    count = 0
    for nameTuple in stereo:
        atm = molecule.decodeNameTuple( nameTuple )
        if atm is None:
            io.error('restoreStereoAssignment: invalid atom nameTuple ({0})', nameTuple)
        else:
            atm.stereoAssigned = True
            count += 1
        #end if
    #end for

    #nTdebug('Molecule.restoreStereoAssignments: restored %d stereo assignments from "%s\n',count, stereoFileName)
    return count
#end def

    # def _saveCoordinates( self, fileName ):
    #     """Write a plain text file with code for saving coordinates"""
    #     fp = open( fileName, 'w' )
    #     fprintf( fp, 'self.modelCount = %d\n', self.modelCount )
    #     for atm in self.allAtoms():
    #         for c in atm.coordinates:
    #             fprintf( fp, 'self%s.addCoordinate( %r, %r, %r, Bfac=%r )\n',
    #                           atm.cName2( 2 ), c[0], c[1], c[2], c.Bfac)
    #     fp.close()
    #     #nTdebug('Molecule.saveCoordinates: %s', fileName)

def restoreCoordinates( molecule, fileName, append = True ):
    """Restore coordinates from fileName
       Optionally append to existing settings
       Return self or None on error
    """
    if not os.path.exists( fileName ):
        io.error('restoreCoordinates: file "{0}" not found\n', fileName )
        return None
    #end if
    if not append:
        for atm in molecule.allAtoms():
            atm.coordinates = ntu.NTlist()
        #end for
    #end if
    #execfile(fileName);
    # 25 Sep 2007: Explicit coding, less memory, better:
    file = open(fileName, 'r')
    for line in file:
        exec(line)
    #end for
    file.close()
    #nTdebug('Molecule.restoreCoordinates: %s (%d)', fileName, self.modelCount)
    return molecule
#end def