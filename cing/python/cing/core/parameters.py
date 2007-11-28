from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTparameter
from cing.Libs.NTutils import NTstruct
import os
 
#-----------------------------------------------------------------------------
# Global program parameters (non-user)
#-----------------------------------------------------------------------------


# These directories get created. They are defined relative to project root path,
# available through Project.rootPath( name ) method, or can be joined relative
# to project root by Project.path( *args ) method.
directories = NTstruct(
                       
    data       = 'Data',
    molecules  = 'Data/Molecules',
    peaklists  = 'Data/Peaklists',
    restraints = 'Data/Restraints',
    ccpn       = 'Data/CCPN',
    sources    = 'Data/Sources',
   
    export     = 'Export',
    xeasy      = 'Export/Xeasy',
    xeasy2     = 'Export/Xeasy2',
    nih        = 'Export/NIH',
    sparky     = 'Export/Sparky',
    PDB        = 'Export/PDB',
    xplor      = 'Export/Xplor',

    queen      = 'Queen',

    refine     = 'Refine'    
)
directories.keysformat() #define a format string for 'pretty' output

# These directories get created upon opening/appending a molecule to project
# Can be accessed as:
# e.g.
# project.path( molecule.name, moleculeDirectories.procheck )
moleculeDirectories = NTdict(     
    # Directories generated 
    procheck   = 'Procheck',
    whatif  = 'Whatif',
    analysis   = 'Cing',
#    profit     = 'Profit',
    shiftx     = 'Shiftx', 
    html       = 'HTML',
)
moleculeDirectories.keysformat() #define a format string for 'pretty' output

#These directories get generated below the HLML root of a molecule 
htmlDirectories = NTdict(     
    # Directories generated 
    procheck= 'Models',
    whatif  = 'Restraints',
    peaks      = 'Peaks'
)
htmlDirectories.keysformat() #define a format string for 'pretty' output


# These files and directories are just definitions
cingPaths = NTstruct(    
    project      = 'project.xml',
    plugins      = 'PluginCode',
    scripts      = '../Scripts',
    bin          = '../bin',
    html         = 'HTML',
    css          = 'cing.css',
    xplor        = os.getenv('xplorPath'),
    profit       = os.getenv('profitPath'),
    procheck_nmr = os.getenv('procheckPath'),
)

cingPaths.keysformat() #define a format string for 'pretty' output
    
plotParameters = NTstruct(
    #default
    dihedralDefault = NTstruct(
        min      =    0.0,
        max      =  360.0,
        ticksize =   60,
        color    = 'green',
        outlier  = 'red',
        average  = 'blue',
        lower    = 'orange',
        upper    = 'orange'
    ),
    PHI = NTstruct(
        min      = -180.0,
        max      =  180.0,
        ticksize =   60,
        color    = 'green',
        outlier  = 'red',
        average  = 'blue',
        lower    = 'orange',
        upper    = 'orange'
    ),
    PSI = NTstruct(
        min      = -180.0,
        max      =  180.0,
        ticksize =   60,
        color    = 'green',
        outlier  = 'red',
        average  = 'blue',
        lower    = 'orange',
        upper    = 'orange'
    ),

)


#-----------------------------------------------------------------------------
# Parameter definitions (value user adaptable)
#-----------------------------------------------------------------------------
parameters = NTparameter( name = 'parameters', branch = True,

    programs = NTparameter( name = 'programs', branch = True,
    
        procheck_nmr = NTparameter( name       = 'procheck_nmr',
                                    partype    = 'string',
                                    default    = 'procheck_nmr',
                                    prettyS    = 'path to procheck_nmr',
                                    help       = 'Path to procheck_nmr',
                                    __FORMAT__ = '%(value)s'
        ),
        whatif =    NTparameter( name       = 'whatif',
                                    partype    = 'string',
                                    default    = 'whatif',
                                    prettyS    = 'path to whatif',
                                    help       = 'Path to whatif',
                                    __FORMAT__ = '%(value)s'
        ),
        profit =       NTparameter( name       = 'profit',
                                    partype    = 'string',
                                    default    = 'profit',
                                    prettyS    = 'path to profit',
                                    help       = 'Path to profit',
                                    __FORMAT__ = '%(value)s'
        ),
    
    ),
    
    verbose = NTparameter( name       = 'verbose',
                           partype    = 'integer',
                           default    =  1,
                           prettyS    = 'verbose flag',
                           help       = 'Verbose flag',
                           __FORMAT__ = '%(value)d'
    ),

)
# Read definition file
#JFD moved these defs into source here.
parameters.verbose.value                 = 1
parameters.programs.procheck_nmr.value   = 'procheck_nmr'

#if os.path.exists( 'cing.par'): 
#    execfile('cing.par')



# Define globals
plugins = NTstruct()