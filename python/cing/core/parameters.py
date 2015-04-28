import cing
import cing.constants as constants
import cing.constants.definitions as cdefs
from cing.Libs.NTutils import NTdict
#from cing.PluginCode.required.reqCcpn import CCPN_STR
#import platform

#LEGACY:
directories = cdefs.directories
moleculeDirectories = cdefs.validationDirectories
validationDirectories = cdefs.validationDirectories
htmlDirectories = cdefs.htmlDirectories
cingPaths = cdefs.cingPaths

outlierColor = '#CC66FF' #  iWeb lavender

plotParameters = NTdict(
    #default
    dihedralDefault = NTdict(
        min      =    0.0,
        max      =  360.0,
        mticksize=   10,
        ticksize =   60,
#        color    = 'green',
        color    = '#990099', # iWeb plum
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

plotParameters.Cb4N = plotParameters.dihedralDefault.copy()
plotParameters.Cb4N.xlabelLat = '$Cb4N$'

plotParameters.Cb4C = plotParameters.dihedralDefault.copy()
plotParameters.Cb4C.xlabelLat = '$Cb4C$'


#OBSOLETE:
#plugins = NTdict()
