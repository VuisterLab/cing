# **********************************************************
# *                                                        *
# *       configure.py                                     *
# *                                                        *
# **********************************************************
# *   Adapted as configure.py by GWV Feb 2005/March 2007   *
# **********************************************************
#
# This configuration file contains all necessary information
# for the refine.py script.
from cing.Libs.NTutils import * #@UnusedWildImport

refinePath = os.path.join(os.getenv('CINGROOT','.'), 'python','Refine')
xplorPath  = os.getenv('xplorPath','.')

# **********************************************************
# editing below here should generally not be necessary
# **********************************************************
# Relabelled from config to refineConfig for apparent clashes with other config.
config = NTdict(

    XPLOR            =  xplorPath,

# (waterrefine) xplor stuff, directories, etc.
    refinePath       = refinePath,
    topparPath       = os.path.join(refinePath,'toppar'),
    protocolsPath    = os.path.join(refinePath,'explicit_solvent'),

    parameterFiles   = [ 'parallhdg5.3-merge.pro',
                         'parallhdg5.3.sol',
                         'par_axis_aria.pro',
                         'ion.param',
                       ],
    topologyFiles    = [ 'topallhdg5.3-merge.pro',
                         'topallhdg5.3.sol',
                         'top_axis_aria.pro',
                         'ion.top',
                       ],
    directories      = NTdict(
        converted    = 'Converted',
        analyzed     = 'Analyzed', # analyzed from refine
        annealed     = 'Annealed', # annealed from template
        template     = 'Template', # extended structure at random
        refined      = 'Refined',  # from analyzed
        tables       = 'Tables',
        jobs         = 'Jobs',
        psf          = 'PSF',
        toppar	     = 'Toppar'
    )
)

config.directories.keysformat()
config.keysformat()
#print '>>', config.format()