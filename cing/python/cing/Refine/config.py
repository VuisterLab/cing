# **********************************************************
# *                                                        *
# *       config.py                                        *
# *                                                        *
# **********************************************************
# *   Adapted as config.py by GWV Feb 2005/March 2007      *
# **********************************************************
#
# This configuration file contains all necessary information 
# for the refine.py script.
from cing.Libs.NTutils import NTstruct
import os

refinePath = os.getenv('refinePath','.')
xplorPath  = os.getenv('xplorPath','.')

# **********************************************************
# editing below here should generally not be necessary
# **********************************************************
# Relabelled from config to refineConfig for apparent clashes with other config.
refConfig = NTstruct(  

    XPLOR            =  xplorPath,

# (waterrefine) xplor stuff, directories, etc.
    refinePath       = refinePath,
    topparPath       = os.path.join(refinePath,'toppar'), 
    protocolsPath    = os.path.join(refinePath,'explicit_solvent'), 

    parameterFiles   = [ os.path.join(refinePath,'toppar','parallhdg5.3-merge.pro'),
                         os.path.join(refinePath,'toppar','parallhdg5.3.sol'),
                         os.path.join(refinePath,'toppar','par_axis_aria.pro'),
                         os.path.join(refinePath,'toppar','ion.param'),
                       ],
    topologyFiles    = [ os.path.join(refinePath,'toppar','topallhdg5.3-merge.pro'),
                         os.path.join(refinePath,'toppar','topallhdg5.3.sol'),
                         os.path.join(refinePath,'toppar','top_axis_aria.pro'),
                         os.path.join(refinePath,'toppar','ion.top'),
                       ],
    directoriesConfig      = NTstruct(
        converted    = 'Converted',
        analyzed     = 'Analyzed',
        refined      = 'Refined', 
        tables       = 'Tables',
        jobs         = 'Jobs', 
        psf          = 'PSF'
    )
)

refConfig.directoriesConfig.keysformat()
refConfig.keysformat()
# The below is ugly but is the last thing to do before pydev and JFD understand each other.
directoriesConfig   = refConfig.directoriesConfig
convertedConfig     = directoriesConfig.converted
tablesConfig        = directoriesConfig.tables
refinedConfig       = directoriesConfig.refined

