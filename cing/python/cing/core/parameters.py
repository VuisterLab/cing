from cing.Libs.NTutils import NTdict, NTdebug
import os

#-----------------------------------------------------------------------------
# Global program parameters (non-user)
#-----------------------------------------------------------------------------


# These directories get created. They are defined relative to project root path,
# available through Project.rootPath( name ) method, or can be joined relative
# to project root by Project.path( *args ) method.
directories = NTdict(
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
    aqua       = 'Export/Aqua',
    queen      = 'Queen',
    refine     = 'Refine',
    tmp        = 'Temp'
)
directories.keysformat() #define a format string for 'pretty' output

# These directories get created upon opening/appending a molecule to project
# Can be accessed as:
# e.g.
# project.path( molecule.name, moleculeDirectories.procheck )
moleculeDirectories = NTdict(
    # Directories generated
    procheck   = 'Procheck',
    dssp       = 'Dssp',
    whatif     = 'Whatif',
    wattos     = 'Wattos',
    analysis   = 'Cing',
    shiftx     = 'Shiftx',
    html       = 'HTML',
)
moleculeDirectories.keysformat() #define a format string for 'pretty' output

#These directories get generated below the HLML root of a molecule
htmlDirectories = NTdict(
    # Directories generated
    procheck= 'Models', # CHECK:weird mapping!
    restraints  = 'Restraints',
    atoms   = 'Atoms',
    peaks   = 'Peaks'
)
htmlDirectories.keysformat() #define a format string for 'pretty' output


# These files and directories are just definitions
cingPaths = NTdict(
    project      = 'project.xml',
    plugins      = 'PluginCode',
    scripts      = 'Scripts',
    bin          = 'bin',
    html         = 'HTML',
    css          = 'cing.css',
    jsMultiLine  = 'multilineTitles.js',
    xplor        = os.getenv('xplorPath'),
    procheck_nmr = os.getenv('procheckPath'),
    aqpc         = os.getenv('aqpcPath'),
    whatif       = os.getenv('whatifPath'),
    dssp         = os.getenv('dsspPath'),
    convert      = os.getenv('convertPath'),
    ghostscript  = os.getenv('ghostscriptPath'),
    ps2pdf       = os.getenv('ps2pdfPath'),
    molmol       = os.getenv('molmolPath'),
    povray       = os.getenv('povrayPath'),
)
#print 'using dssp: ' + `cingPaths.dssp`
if cingPaths.convert:
    cingPaths[ 'montage' ] = cingPaths.convert.replace('convert','montage')

cingPaths.keysformat() #define a format string for 'pretty' output

outlierColor = 'red'
plotParameters = NTdict(
    #default
    dihedralDefault = NTdict(
        min      =    0.0,
        max      =  360.0,
        mticksize=   10,
        ticksize =   60,
        color    = 'green', # use names that are html legal here so matplot knows them.
        outlier  = outlierColor,
        average  = 'blue',
        lower    = 'orange',
        upper    = 'orange'
    ),
)
plotParameters.PHI     = plotParameters.dihedralDefault.copy()
plotParameters.PHI.min = -180
plotParameters.PHI.max =  180
plotParameters.PHI.xlabelLat = '$\phi 1$' # Latex

plotParameters.PSI  = plotParameters.PHI.copy()
plotParameters.PHI.xlabelLat = '$\psi 1$' # Latex

plotParameters.CHI1 = plotParameters.dihedralDefault.copy()
plotParameters.CHI1.xlabelLat = '$\chi 1$'

plotParameters.CHI2 = plotParameters.dihedralDefault.copy()
plotParameters.CHI2.xlabelLat = '$\chi 2$'

plotParameters.CHI3 = plotParameters.dihedralDefault.copy()
plotParameters.CHI3.xlabelLat = '$\chi 3$'

#-----------------------------------------------------------------------------
# Parameter definitions (value user adaptable)
#-----------------------------------------------------------------------------
#parameters = NTparameter( name = 'parameters', branch = True,
#
#    programs = NTparameter( name = 'programs', branch = True,
#
#        procheck_nmr = NTparameter( name       = 'procheck_nmr',
#                                    partype    = 'string',
#                                    default    = 'procheck_nmr',
#                                    prettyS    = 'path to procheck_nmr',
#                                    help       = 'Path to procheck_nmr',
#                                    __FORMAT__ = '%(value)s'
#        ),
#        whatif =    NTparameter( name       = 'whatif',
#                                    partype    = 'string',
#                                    default    = 'whatif',
#                                    prettyS    = 'path to whatif',
#                                    help       = 'Path to whatif',
#                                    __FORMAT__ = '%(value)s'
#        ),
#    )
#)
#parameters.programs.procheck_nmr.value   = 'procheck_nmr'
#
#if os.path.exists( 'cing.par'):
#    execfile('cing.par')



# Define globals
plugins = NTdict()