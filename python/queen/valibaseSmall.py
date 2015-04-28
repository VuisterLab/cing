#!/usr/bin/env python
#@PydevCodeAnalysisIgnore # pylint: disable-all

from cing.Libs.NTutils import * #@UnusedWildImport
from queen import nmv
from queen import nmvconf
from queen import pdb_file
from queen.main import graceplot
from queen.main import nmv_adjust
from queen.main import restraint_file
from queen.main import xplor_formatdict
from queen.main import xplor_script
import string,socket

# TODO
# - check the pdb_bfactor section!
# - finish pdb_resample ...

debugflag = 1
myid = 0 #pypar.rank()


# CREATE A NEW TMP DIRECTORY IN THE GIVEN PATH
# ============================================
def dsc_tmpdir(basepath):
  if os.path.exists(basepath):
    id = 1
    while 1:
      tmppath = os.path.join(basepath,"tmp_p%i_%s_%i"%(myid,socket.gethostname(),id))
      if os.path.exists(tmppath):
        id+=1
      else:
        os.mkdir(tmppath)
        break
  return tmppath

# READ DATAFILE
# =============
# FUNCTION READS A DATASET DESCRIPTION FILE
def nmrinfo_readdatafile(datafile):
  # WE KEEP A LIST IN ORDER TO RETAIN THE ORDER IN THE FILE
  filelist = []
  # READ AND PARSE THE DICTIONARY TYPE FILE
  try: dctfile = open(datafile,"r")
  except: nTerror("Datasetfile %s could not be read" %datafile)
  dct = {}
  for line in dctfile.readlines():
    line=string.strip(line)
    # CHECK IF CURRENT LINE IS A COMMENT (STARTS WITH '#')
    l=len(line);
    if (l):
      if (line[0] not in ['#','/']):
        # IF LINE IS NOT A COMMENT:
        #   CHECK IF DICTIONARY KEY AND ENTRY ARE REALLY PRESENT
        i=string.find(line,"=")
        if (i==-1):  nTerror("No equals sign found in %s at %s" % (datafile,line))
        if (i==0):   nTerror("No data found before equals sign in %s at %s" % (datafile,line))
        if (i==l-1): nTerror("No data found behind equals sign in %s at %s" % (datafile,line))
        # ADD TO DICTIONARY
        dct[string.strip(line[:i])] = string.strip(line[i+1:])
      # END OF DICT
      if line[:2]=='//':
          filelist.append(dct)
          dct = {}
  return filelist


#  ======================================================================
#    N M R   I N F O R M A T I O N   C L A S S
#  ======================================================================

class nmr_info:
  """
  This class provides an interface to NMR information content algoritm.
  """
  # INITIALIZE NMR INFO CLASS
  # =========================
  #
  def __init__(self):
    self.natoms = 0
    pass

  # CALCULATE SET INFO
  # ==================
  # CALCULATES THE INFORMATION CONTAINED IN A
  # DICTIONARY OF RESTRAINTS
  def calcsetmtx(self,xplor,parameter,psf,restraintdict,dmtx,logpath,template,averaging='sum'):
    self.parameter = parameter
    self.psf = psf
    self.xplor = xplor
    self.template = template
    self.averaging = averaging
    if os.path.exists(dmtx): os.remove(dmtx)
    # INITIALIZE XPLOR
    xplr = xplor_script(self.xplor,logpath)
    # READ THE STRUCTURE FILE
    xplr.write("structure\n  @%s\nend"%self.psf)
    # READ PARAMETER FILE
    xplr.write("evaluate ($par_nonbonded=PROLSQ)")
    xplr.write("parameter\n  @%s\nend"%self.parameter)
    # FORMAT THE RESTRAINT FILE
    xplr.write(xplor_formatdict(restraintdict))
    # READ TEMPLATE FOR PSEUDOATOM CORRECTIONS
    xplr.write("coord disp=refe @%s"%self.template)
    # SET FLAGE
    xplr.write("flags")
    xplr.write("  exclude * include bond angle dihe improper vdw noe cdih")
    xplr.write("end")
    # DO DG
    xplr.write("mmdg")
    xplr.write("  refe=para")
    xplr.write("  shortest-path-algorithm=auto")
    xplr.write("  writebounds=%s"%dmtx)
    xplr.write("end")
    xplr.submit()

  # READ DISTANCE MATRIX
  # ====================
  # READ A DISTANCE MATRIX IN THE GIVEN FORMAT
  def readmtx(self,filename,format="XPLOR"):
    # READ XPLOR MATRIX
    if format == "XPLOR":
      self.natoms = nmv.xplor_read(filename)
    # READ NMV MATRIX
    if format == "NMV":
      pass

  # CALCULATE SET UNCERTAINTY
  # =========================
  # ONE CALL FOR FULL SET UNCERTAINTY
  def calcsetunc(self,xplor,parameter,psf,restraintdict,dmtx,logpath,template):
    # CALCULATE SET INFO
    self.calcsetmtx(xplor,parameter,psf,restraintdict,dmtx,logpath,template)
    # READ THE MATRIX
    self.readmtx(dmtx)
    # CALCULATE UNCERTAINTY
    return self.calcuncertainty()

  # FREE MEMORY
  # ===========
  # FREE MEMORY USED BY NMV CODE
  def freemem(self):
    nmv.free_memory()

  # CALCULATE UNCERTAINTY
  # =====================
  # CALCULATE THE UNCERTAINTY OF THE CURRENT
  # DISTANCE MATRIX
  def calcuncertainty(self):
    return nmv.total_uncertainty()

  # CALCULATE ATOM UNCERTAINTY
  # ==========================
  # CALCULATE THE UNCERTAINTY OF THE GIVEN
  # ATOM IN THE CURRENT DISTANCE MATRIX
  def calcatomuncertainty(self,atom):
    return nmv.atom_uncertainty(atom-1)

  # CALCULATE UNCERTAINTY
  # =====================
  # CALCULATE THE UNCERTAINTY
  def uncertainty(self,atom1,atom2):
    return nmv.uncertainty(atom1-1,atom2-1)

#  ============================================================================
#   S U B S C R I P T  23:  C A L C U L A T E   A T O M  U N C E R T A I N T Y
#  ============================================================================
#
# THIS SCRIPT CALCULATES THE UNCERTAINTY OF GIVEN ATOMS IN A
# PROTEIN STUCTURE.
# AVAILABLE SELECTIONS: N,C,CA,BB->(N,C,CA),RESIDUE
def nmv_atomuncertainty(projectname,datasetlist,selection):
  print "Calculating atom uncertainty."
  print "============================"
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  logpath = dsc_tmpdir(os.path.join(path,nmvconf["NMRI_LOG"]))
  # SET SOME DEFAULT VARS
  xplr = nmvconf["XPLOR"]
  para = nmvconf["NMRI_PAR"]
  dmtx = os.path.join(logpath,nmvconf["NMRI_TEMPMTX"])
  template = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  # OPEN THE LOGFILE
  logfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"atom_%s_%s"%(datasetlist,selection)))
  # READ THE DATASET DESCRIPTION FILE
  setlist = nmrinfo_readdatafile(dataset)
  print "Found %i datafiles in dataset."%len(setlist)
  # SET THE PSF FILE PATH
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  xmgr = graceplot(logfile,'xy','w')
  xmgr.title = "Uncertainty."
  xmgr.xlab = "Residue number"
  xmgr.ylab = "Uncertainty (bits/atom)"
  xmgr.writeheader()
  # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
  fulldict = {}
  for set in setlist: fulldict[set["TYPE"]]=[]
  for filedict in setlist:
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # STORE PARSED RESTRAINT FOR FUTURE USE
    filedict["DATA"] = r.restraintlist
    fulldict[filedict["TYPE"]]+=r.restraintlist
##  # INITIALIZE NMRINFO CLASS FOR INITIAL UNCERTAINTY
##  ini = nmr_info()
##  ini.calcsetunc(xplr,para,psffile,{},dmtx,logpath,template)
##  base = Numeric.array([0.0])
##  iniarray=Numeric.resize(base,(ini.natoms,ini.natoms))
##  for i in range(ini.natoms):
##    for j in range(ini.natoms):
##      iniarray[i][j]=ini.uncertainty(i+1,j+1)
##  ini.freemem()
  # INITIALIZE NMRINFO CLASS FOR FULL UNCERTAINTY
  nmrinfo = nmr_info()
  nmrinfo.calcsetunc(xplr,para,psffile,fulldict,dmtx,logpath,template)
  # READ THE TEMPLATE
  pdb = pdb_file.Structure(template)
  for chain in pdb.peptide_chains:
    for residue in chain:
      unc,atomcount = 0,0
      for atom in residue:
        atomnum = atom.properties["serial_number"]
        if selection == 'res':
          unc += nmrinfo.calcatomuncertainty(atomnum)
          atomcount += 1
        elif selection == 'bb':
          if atom.name in ['N','C','CA']:
            unc += nmrinfo.calcatomuncertainty(atomnum)
            atomcount += 1
        elif selection == 'CA':
          if atom.name == 'CA':
            unc += nmrinfo.calcatomuncertainty(atomnum)
            atomcount += 1
      xmgr.write([residue.number,unc/atomcount])
    xmgr.newset()
  nmrinfo.freemem()
  xmgr.close()
  xmgr.output('ps')
  print 'Finished.'