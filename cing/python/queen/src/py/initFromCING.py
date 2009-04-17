# ADD QUEEN SOURCE TO SYSTEM PATH
import sys,os

sys.path += [os.path.join(sys.path[0])]
from qn import *

# CING IMPORTS
try:
  from cing import *
  from cing.core.parameters import directories
  from cing.Libs.NTutils import removedir
except ImportError:
  error("""You do not seem to have the CING API installed""")
  exit(1)


def initFromCING( queenProject, cingProject ):
    """Initialize the QUEEN data structure from a CING project instance.
       Export and check the restraints.
       Generate the templates.
    """
    if not cingProject:
        NTerror('initFromCING: Please supply a valid CING project argument.')
        exit(1)
    #end if

    if not cingProject.contentIsRestored:
        cingProject.restore()

    nmvconf = queenProject.nmvconf

    # Create the queen directory structure
    removedir( queenProject.projectpath )
    queenProject.createproject()

    # export restraints and WRITE DATASET DESCRIPTION FILE
    setfile = nmv_adjust(queenProject.dataset, 'all')
    fp = open(setfile,'w')
    for drl in cingProject.distances:
        tableName = nmv_adjust(queenProject.table,drl.name.replace(' ','_'))
        drl.export2xplor( tableName )
        restraints,doubles,selfrefs = rfile_check( tableName, type='DIST' )
        print "- %5i valid restraints."%restraints
        print "- %5i double restraints."%doubles
        print "- %5i self referencing restraints."%selfrefs

        # write entry in set file
        fprintf( fp, "NAME = %s\nTYPE = %s\nFILE = %s\n//\n",
                     "Distance restraints " + drl.name,
                     "DIST",
                     drl.name.replace(' ','_')
               )
    # end for
    for drl in cingProject.dihedrals:
        tableName = nmv_adjust(queenProject.table,drl.name.replace(' ','_'))
        drl.export2xplor( tableName )
        restraints,doubles,selfrefs = rfile_check( tableName, type='DIST' )
        print "- %5i valid restraints."%restraints
        print "- %5i double restraints."%doubles
        print "- %5i self referencing restraints."%selfrefs

        fprintf( fp, "NAME = %s\nTYPE = %s\nFILE = %s\n//\n",
                     "Dihedral restraints " + drl.name,
                     "DIHED",
                     drl.name.replace(' ','_')
               )
    # end for
    fp.close()
    NTmessage('==> Dataset file: %s', setfile)

    # Generate templates by writing pdbfile and calling qn_pdb2all
    if not cingProject.molecule:
        NTerror('initFromCING: no molecule defined, skipping template generation')
        return
    #end if
    NTmessage('==> Generating templates ...')
    pdbfile = os.path.join(queenProject.pdb, cingProject.molecule.name.replace(' ','_')+'.pdb')
    #print '>', pdbfile
    cingProject.molecule.toPDBfile( pdbfile, model=0 ) # save first model to pdbfile
    qn_pdb2all( queenProject, pdbfile, xplorflag=0)
#end def


class CingBasedQueen( queenbase ):
    """Class to initialize the QUEEN data structure from a CING project instance.
       Method to export and check the restraints and generate the templates.
    """

    def __init__(self, nmvconf, cingProjectName, numproc, myid ):

        cingProject = Project.open( cingProjectName, status='old', restore=False)
        if cingProject == None:
            NTerror('CingBasedQueen: Opening project "%s"\n', cingProjectName )
            exit(1)
        #end if

        self.cingProject = cingProject

        # patch the nmrconf file to point to CING project
        nmvconf["Q_PROJECT"] = os.path.abspath(cingProject.path())

        # patch the project to point to cingProject/Queen directory
        queenbase.__init__( self, nmvconf, project = directories.queen, numproc=numproc, myid=myid)
    #end def

    def exportFromCING(self):
        """Export and check the restraints.
           Generate the templates.
        """
        if not self.cingProject:
            NTerror('CingBasedQueen.exportFromCING: Please supply a valid CING project argument.')
            exit(1)
        #end if

        if not self.cingProject.contentIsRestored:
            self.cingProject.restore()

        # export restraints and WRITE DATASET DESCRIPTION FILE
        setfile = nmv_adjust(self.dataset, 'all')
        fp = open(setfile,'w')
        for drl in self.cingProject.distances:
            tableName = nmv_adjust(self.table,drl.name.replace(' ','_'))
            drl.export2xplor( tableName )
            restraints,doubles,selfrefs = rfile_check( tableName, type='DIST' )
            print "- %5i valid restraints."%restraints
            print "- %5i double restraints."%doubles
            print "- %5i self referencing restraints."%selfrefs

            # write entry in set file
            fprintf( fp, "NAME = %s\nTYPE = %s\nFILE = %s\n//\n",
                         "Distance restraints " + drl.name,
                         "DIST",
                         drl.name.replace(' ','_')
                   )
        # end for
        for drl in self.cingProject.dihedrals:
            tableName = nmv_adjust(self.table,drl.name.replace(' ','_'))
            drl.export2xplor( tableName )
            restraints,doubles,selfrefs = rfile_check( tableName, type='DIST' )
            print "- %5i valid restraints."%restraints
            print "- %5i double restraints."%doubles
            print "- %5i self referencing restraints."%selfrefs

            fprintf( fp, "NAME = %s\nTYPE = %s\nFILE = %s\n//\n",
                         "Dihedral restraints " + drl.name,
                         "DIHED",
                         drl.name.replace(' ','_')
                   )
        # end for
        fp.close()
        NTmessage('==> Dataset file: %s', setfile)

        # Generate templates by writing pdbfile and calling qn_pdb2all
        if not self.cingProject.molecule:
            NTerror('CingBasedQueen.exportFromCING: no molecule defined, skipping template generation')
            return
        #end if
        NTmessage('==> Generating templates ...')
        pdbfile = os.path.join(self.pdb, self.cingProject.molecule.name.replace(' ','_')+'.pdb')
        #print '>', pdbfile
        self.cingProject.molecule.toPDBfile( pdbfile, model=0 ) # save first model to pdbfile
        qn_pdb2all( self, pdbfile, xplorflag=0)
    #end def

#end class




