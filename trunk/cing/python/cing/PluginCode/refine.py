"""
Adds export2refine method

    Project.export2refine( name ):
        generates the name refine setup directories under project/Refine
        exports molecule in xplor nomenclature
        exports DistanceRestraintLists in xplor format
        exports DihedralRestraintLists in xplor format
"""
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import sprintf
from cing.Refine.config import convertedConfig
from cing.Refine.config import refConfig
from cing.Refine.config import refinedConfig
from cing.Refine.config import tablesConfig
from cing.Refine.refine import doSetup
from cing.core.molecule import dots
import os


def export2refine( project, name ):    
    basePath = project.path( project.directories.refine, name)
    
    if project.parameters.verbose():
        NTmessage('\n' + dots*5 +'\n' )
        NTmessage(   '==> Exporting %s to for refinement\n', project )
    #end if

    doSetup( refConfig, basePath )
    
    # JFD notes: really weird; inside Eclipse pydev extensions confuses this config with that in:
    # cing.core.parameters.py and not as specified from cing.Refine.config.py
    # Let me try refreshing the workspaces; doesn't help.
    # Dang; even writting this out doesn't help. Ok, used a slightly different name to work this out.
    for drl in project.distances:
        fname = project.path( project.directories.refine, name, tablesConfig, drl.name +'.tbl')
        drl.export2xplor( fname, verbose = project.parameters.verbose() )
    #end for 
    
    for drl in project.dihedrals:
        fname = project.path( project.directories.refine, name, tablesConfig, drl.name +'.tbl')
        drl.export2xplor( fname, verbose = project.parameters.verbose() )
    #end for

    # export structures in PDB format
    path = project.path( project.directories.refine, name, convertedConfig, 'model%03d.pdb' )
    project.molecule.export2xplor( path, verbose = project.parameters.verbose() )

#end def


def importFromRefine( project, name ):
    """
    Import data from Refine/name directory as new molecule
    Optionally use basename; otherwise look for model%03d.fitted.pdb 
    or model%03d.pdb file
    
    Return Molecule or None on error
    """
    
    basePath = project.path( project.directories.refine, name)
    if not os.path.exists(basePath):
        NTerror('ERROR importFromRefine: no path "%s" found\n', basePath)
        return None
    #endif

    global params
    execfile(project.path( project.directories.refine, name,'parameters.py'), globals() )
    params.keysformat()
    print params
          
    # little misery to check for presence of files
    path,b,_ext = NTpath(params.baseName)
    basenames = [b+'.fitted.pdb', b+'.pdb']    
    found = True
    for b in basenames:
        path = project.path( project.directories.refine, 
                             name, 
                             refinedConfig, 
                             b
                            )
        if os.path.exists( sprintf(path,params.models[0]) ):
            found = True
            break
        #endif
    #end for
    
    if not found:
        NTerror('ERROR importFromRefine: no files (%s) found\n', path)
        return None
    #endif

    # import structures from Xplor PDB files    
    return project.newMoleculeFromXplor( path, name, models=params.models )

#end def

#-----------------------------------------------------------------------------
# register the functions in the project class
methods  = [(export2refine, None),
            (importFromRefine, None)
           ]
#saves    = []
#restores = []
#exports  = []