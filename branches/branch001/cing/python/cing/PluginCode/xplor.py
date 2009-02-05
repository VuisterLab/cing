"""
Adds export2xplor methods to:
DistanceRestraint , DistanceRestraintList, DihedralRestraint, DihedralRestraintList,
Atom, Molecule and Project classes.

    DistanceRestraint.export2xplor()

    DistanceRestraintList.export2xplor( path  )

    DihedralRestraint.export2xplor()

    DihedralRestraintList.export2xplor( path  )

    Atom.export2xplor()

    Molecule.export2xplor( path  )

    Project.export2xplor():
        exports Molecules in xplor nomenclature
        exports DistanceRestraintLists in xplor format

    Molecule.newMoleculeFromXplor( project, path, name, models=None ):
        Generate new molecule 'name' from set of pdbFiles in XPLOR convention
        path should be in the form filename%03d.pdb, to allow for multiple files
        for each model.
        models is a list of model numbers.
        return Molecule or None on error


!!NEED to Check periodicity in dihedrals

"""
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import sprintf
from cing.core.classes import DihedralRestraint
from cing.core.classes import DihedralRestraintList
from cing.core.classes import DistanceRestraint
from cing.core.classes import DistanceRestraintList
from cing.core.constants import XPLOR
from cing.core.molecule import Atom
from cing.core.molecule import Molecule
import math
import os

#==============================================================================
# XPLOR stuff
#==============================================================================

#-----------------------------------------------------------------------------
def exportAtom2xplor( atom ):
    """returns string in xplor format"""
    return sprintf( '(resid %-3d and name %s)',
                      atom.residue.resNum,
                      atom.translate(XPLOR)
                   )
#end def
# add as a method to Atom Class
Atom.export2xplor = exportAtom2xplor


#-----------------------------------------------------------------------------
def exportDistanceRestraint2xplor( distanceRestraint ):
    """Return string with restraint in Xplor format"""
    # Strange xplor syntax
    atm1,atm2 = distanceRestraint.atomPairs[0]
    s = sprintf('assi %-30s %-30s %8.3f  %8.3f  %8.3f',
                atm1.export2xplor(),atm2.export2xplor(),
                distanceRestraint.upper, distanceRestraint.upper-distanceRestraint.lower, 0.0  # syntax xplor: d, dminus, dplus
               )

    for atm1,atm2 in distanceRestraint.atomPairs[1:]:
        s = s + sprintf( '\n  or %-30s %-30s ', atm1.export2xplor(), atm2.export2xplor() )
    #end for
    return s
#    s = sprintf( 'assi %-30s %-30s  %8.3f  %8.3f  %8.3f',
#                 distanceRestraint.atomPairs[0][0].export2xplor(),
#                 distanceRestraint.atomPairs[0][1].export2xplor(),
#                 distanceRestraint.upper, distanceRestraint.upper-distanceRestraint.lower, 0.0  # syntax xplor: d, dminus, dplus
#               )
#    for atm1,atm2 in distanceRestraint.atomPairs[1:]:
#        s = s + sprintf( '\n  or %-30s %-30s',
#                        distanceRestraint.atomPairs[0][0].export2xplor(),
#                        distanceRestraint.atomPairs[0][1].export2xplor(),
#                       )
#    #end for
#    return s
#end def
# add as a method to DistanceRestraint Class
DistanceRestraint.export2xplor = exportDistanceRestraint2xplor


#-----------------------------------------------------------------------------
def exportDistanceRestraintList2xplor( drl, path)   :
    """Export a distanceRestraintList (DRL) to xplor format:
       return drl or None on error
    """
    fp = open( path, 'w' )
    if not fp:
        NTerror('exportDistanceRestraintList2xplor: unable to open "%s"\n', path )
        return None
    #end def
    for dr in drl:
        fprintf( fp, '%s\n', dr.export2xplor() )
    #end for

    fp.close()
    NTmessage('==> Exported %s to "%s"', drl, path)
    #end if
    return drl
#end def
# add as a method to DistanceRestraintList Class
DistanceRestraintList.export2xplor = exportDistanceRestraintList2xplor

#-----------------------------------------------------------------------------
def exportDihedralRestraint2xplor( dihedralRestraint ):
    """Return string with restraint in Xplor format
       GV 24 Sept 2007: delta adjusted to delta*0.5
    """
    s = sprintf('assign \n')
    for a in dihedralRestraint.atoms:
        s = s + sprintf( '     %-30s\n', a.export2xplor() )
    #end for

    delta = math.fabs( dihedralRestraint.upper-dihedralRestraint.lower )
    ave   = dihedralRestraint.lower + delta*0.5

    s = s + sprintf('     %8.2f %8.2f %8.2f 2\n',
                     1.0, ave, delta*0.5  # syntax xplor:
                   )
    return s
#end def
# add as a method to DihedralRestraint Class
DihedralRestraint.export2xplor = exportDihedralRestraint2xplor

#-----------------------------------------------------------------------------
def exportDihedralRestraintList2xplor( drl, path)   :
    """Export a dihedralRestraintList (DRL) to xplor format:
       return drl or None on error
    """
    fp = open( path, 'w' )
    if not fp:
        NTerror('exportDihedralRestraintList2xplor: unable to open "%s"\n', path )
        return None
    #end def
    for dr in drl:
        fprintf( fp, '%s\n', dr.export2xplor() )
    #end for

    fp.close()
    NTmessage('==> Exported %s to "%s"', drl, path)
    #end if
    return drl
#end def
# add as a method to DistanceRestraintList Class
DihedralRestraintList.export2xplor = exportDihedralRestraintList2xplor


#-----------------------------------------------------------------------------
def exportMolecule2xplor( molecule, path)   :
    """Export coordinates of molecule to pdbFile in XPLOR convention;
       generate modelCount files,
       path should be in the form name%03d.pdb, to allow for multiple files
       for each model

       return Molecule or None on error
    """
    for model in range(molecule.modelCount):
        pdbFile = molecule.toPDB( model=model, convention = XPLOR)
        if not pdbFile:
            return None
        pdbFile.save( sprintf( path, model )   )
        del(pdbFile)
    #end for
    return molecule
#end def
# add as a method to Molecule Class
Molecule.export2xplor = exportMolecule2xplor


def newMoleculeFromXplor( project, path, name, models=None ):
    """Generate new molecule 'name' from set of pdbFiles in XPLOR convention

       path should be in the form filename%03d.pdb, to allow for multiple files
       for each model.

       models is a optional list of model numbers, otherwise it scans for files.

       return Molecule or None on error

       NB model_000.pdb becomes model number 0. Ie model=0
    """
#    print '>', path, name, models
#    NTmessage(name,models[0])

    if models == None:
        models = NTlist()
        model = 0
        xplorFile = sprintf(path,model)
        #print '>>', xplorFile
        while os.path.exists( xplorFile ):
            model += 1
            models.append( model )
            xplorFile = sprintf(path,model)
            #print '>>', xplorFile
        #end while
        #print '>>', models
    #end if

    if len(models) == 0:
        NTerror('newMoleculeFromXplor: empty models list\n')
        return None
    #end if

    # first one:
#    modelId = models[0]
    xplorFile = sprintf( path, models[0] )
    if not os.path.exists(xplorFile):
        NTerror('newMoleculeFromXplor: file "%s" not found\n', xplorFile)
        return None
    #end if
#    molecule = Molecule.PDB2Molecule( xplorFile, name, convention = XPLOR)
#    project.appendMolecule( molecule )
    molecule = project.initPDB( xplorFile, name=name, convention = XPLOR )
    if not molecule:
        return None
    # now the other models:
    for model in models[1:]:
#        modelId = model - 1
        xplorFile = sprintf( path, model )
        if not molecule.importFromPDB( xplorFile, XPLOR, nmodels=1):
            return None
        #end if
    #end for

    project.molecule.updateAll()

    project.addHistory( sprintf('New molecule "%s" from XPLOR files %s (%d models)\n', name, path, molecule.modelCount ) )
    project.updateProject()
    NTdetail( '%s', molecule.format() )

    return molecule

#end def
#-----------------------------------------------------------------------------
def export2xplor( project, tmp=None ):
    """export distanceRestraintLists to xplor
       export Molecules to PDB files in xplor format
    """
    for drl in project.distances:
        drl.export2xplor( project.path( project.directories.xplor, drl.name +'.tbl' ),

                        )
    #end for

    for drl in project.dihedrals:
        drl.export2xplor( project.path( project.directories.xplor, drl.name +'.tbl' ),

                        )
    #end for

    for molName in project.moleculeNames:
        mol   = project[molName]
        path = project.path( project.directories.xplor, mol.name + '_%03d.pdb' )
        mol.export2xplor( path)
    #end for
#end def

#-----------------------------------------------------------------------------
# register the functions in the project class
methods  = [(newMoleculeFromXplor, None)
           ]
#saves    = []
#restores = []
exports  = [(export2xplor, None),
           ]
