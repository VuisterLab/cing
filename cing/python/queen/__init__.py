from cing.Libs.NTutils import * #@UnusedWildImport
from q_utils import dct_read

# READ THE QUEEN CONFIGURATION FILE and adjust Q_PATH
nmvconf = dct_read(os.path.join(sys.path[0],'queen.conf'))
nmvconf["Q_PATH"] = os.path.abspath(os.sys.path[0])

#print "nmvconf %s" % nmvconf