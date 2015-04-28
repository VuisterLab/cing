#@PydevCodeAnalysisIgnore # pylint: disable-all
from cing.Libs.NTutils import * #@UnusedWildImport
import string

'''
Created on Jan 7, 2011
'''

#  ======================================================================
#    D I C T I O N A R Y   F U N C T I O N   G R O U P
#  ======================================================================

# READ DICTIONARY
# ===========================
# READ A DICTIONARY FROM DISC
def dct_read(filename):
  try: dctfile = open(filename,"r")
  except: nTerror("Dictionary %s could not be read" % filename)
  dct = {}
  for line in dctfile.readlines():
    line=string.strip(line)
    # CHECK IF CURRENT LINE IS A COMMENT (STARTS WITH '#')
    l=len(line);
    if (l):
      if (line[0]!='#'):
        # IF LINE IS NOT A COMMENT:
        #   CHECK IF DICTIONARY KEY AND ENTRY ARE REALLY PRESENT
        i=string.find(line,"=")
        if (i==-1):  nTerror("No equals sign found in %s at %s" % (filename,line))
        if (i==0):   nTerror("No data found before equals sign in %s at %s" % (filename,line))
        if (i==l-1): nTerror("No data found behind equals sign in %s at %s" % (filename,line))
        # ADD TO DICTIONARY
        dct[string.strip(line[:i])] = string.strip(line[i+1:])
  return(dct)

# WRITE DICTIONARY
# ==========================
# WRITE A DICTIONARY TO DISC
def dct_write(dct,filename):
  try: dctfile = open(filename,"w")
  except: nTerror("Dictionary %s could not be written" % filename)
  # PRINT ENTRIES
  for key in dct.keys():
    # PRINT KEY AND VALUE
    dctfile.write("%s = %s\n" % (key,dct[key]))
  dctfile.close()


# CHECK PYTHON VERSION
# ====================
# CHECK PYTHON VERSION
def nmv_checkpython():
  version = float(sys.version[0])
  if version < 2.0:
    nTerror('Python version 2.0 or higher required')
  return float(sys.version.split()[0][:3])
