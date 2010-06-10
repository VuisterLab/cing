"""
Adds export to sparky files


Methods:

  export2Sparky():
        Export resonances and peaks in sparky format

"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import allAtoms
from cing.core.parameters import directories


#-----------------------------------------------------------------------------
# Sparky routines
#-----------------------------------------------------------------------------
def exportShifts2Sparky( molecule, fileName=None, onlyAssigned=1)   :
    """Export shifts to sparky format
    """

    if not molecule:
        return None
    #end if

    if not fileName:
        fileName = molecule.name + '.sparky'
    #end if

    f = open( fileName, 'w' )

    count = 0
    for ac in allAtoms( molecule ):
#        shift = ac.resonances().value
        assigned = ac.isAssigned()
        if (onlyAssigned and assigned) or (not onlyAssigned):
            fprintf(  f,'%-5s %-5s %-5s %10.3f %10.3f %7d\n',
                      ac._parent.shortName,
                      ac.translate(SPARKY),
                      ac.db.spinType,
                      ac.resonances().value,
                      ac.resonances().error,
                      1
                   )
            count += 1
        #end if
    #end for
    f.close()

    NTmessage('==> exportShifts2Sparky: %-4d shifts   written to "%s"', count, fileName)
    #end if
#end def

def exportPeaks2Sparky( peaks, peakFile)   :
    """Export peaks to Sparky fileName
    """
    if (peaks==None):
        NTerror('exportPeaks2Sparky: undefined peak list\n' )
        return
    #end if
    if (len(peaks) == 0):
        NTerror('exportPeaks2Sparky: zero-length peak list\n' )
        return
    #end if

    fout = open( peakFile, 'w' )
    # write the peaks
    count = 0
    for peak in peaks:
        if ( peak.isAssigned( X_AXIS ) ):
            atom = peak.resonances[X_AXIS].atom
            atomName = atom.translate( SPARKY )
            if (atomName == None):
                NTerror('WARNING exportPeaks2Sparky: no translation to "SPARKY" format of atom %s\n', atom)
                atomName = atom.name
            #end if
            assignment = atom._parent.shortName + atomName
        else:
            assignment = '???'
        #end if
        for i in range(Y_AXIS, peak.dimension):
            if ( peak.isAssigned( i ) ):
                atom = peak.resonances[i].atom
                assignment = assignment + '-' + atom._parent.shortName + atom.translate( SPARKY )
            else:
                assignment = assignment + '-???'
            #end if
        #end for
        fprintf( fout, '%-30s ', assignment )

        for i in range(X_AXIS, peak.dimension):
            fprintf( fout, '  %9.3f ', peak.positions[i] )
        #end for

        fprintf( fout, '\n' )
        count += 1
    #end for
    fout.close()

    NTmessage( '==> exportPeaks2Sparky:  %-4d peaks    written to "%s"', count, peakFile )
    #end if
#end def

#-----------------------------------------------------------------------------
def export2Sparky( project, tmp=None ):
    """
    Export resonances and peaks to sparky format
    """

    for mol in project.molecules:
        fileName = project.path( directories.sparky, mol.name+'.sparky' )
        exportShifts2Sparky( mol,
                             fileName=fileName,
                             onlyAssigned=True,

                           )
    #end for

    for pl in project.peaks:
        if (pl.status == 'keep'):
            peakFile = project.path( directories.sparky, pl.name+'.peaks' )
            exportPeaks2Sparky( pl, peakFile)
        #end if
    #end for
#end def
#-----------------------------------------------------------------------------

# register the functions
methods  = []
saves    = []
restores = []
exports  = [(export2Sparky, None)]

#print '>>at the end'


