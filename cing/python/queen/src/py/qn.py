#@PydevCodeAnalysisIgnore
from queen.queen import nmvconf
from subprocess import PIPE
from subprocess import Popen
import string,os,sys,math,socket,time,shutil,copy,types,random,glob,fnmatch,nmv,pdb_file

#  ======================================================================
#    P R O G R E S S   I N D I C A T O R   C L A S S
#  ======================================================================

class progress_indicator:
    """
    USAGE:
    - Create a class instance giving the total number of increments
    - Instance.increment(numincrements) will increase the bar with numincrements
    """

    # OPEN PROGRESS INDICATOR
    # =======================
    # - totalincrements IS THE TOTAL NUMBER OF INCREMENTS
    # - lengthofbar IS THE LENGTH OF THE BAR ONSCREEN (IN TOTAL)
    def __init__(self, totalincrements, lengthofbar=56):
      self.totalincrements = float(totalincrements)
      # LENGTH OF THE BAR
      self.lengthofbar = lengthofbar

    # INCREMENT
    # =========
    # INCREMENT THE BAR WITH THE PROVIDED NUMBER OF INCREMENTS
    def increment( self, numincrements ):
      # LENGT OF PROGRESS INDICATOR
      numchars = int(self.lengthofbar*(float(numincrements)/self.totalincrements))
      # PROGRESS STRING
      progstr = ""
      for i in range(numchars):
        progstr += "="
      # EMPTY SPACE STRING
      numspaces = self.lengthofbar-numchars
      for i in range(numspaces):
        progstr += " "
      # COMBINE STRING
      progstr = "[%s] (%i/%i)"%(progstr,numincrements,
                                  int(self.totalincrements))
      sys.stdout.write(progstr+'\r')
      sys.stdout.flush()
      # IN THE END GO TO THE NEXT LINE
      if numincrements==self.totalincrements:
        print

#  ======================================================================
#    E R R O R   F U N C T I O N   G R O U P
#  ======================================================================

# SCRIPT ERROR
# ============
# DISPLAY ERROR MESSAGE AND STOP SCRIPT
def error(err):
  text="ERROR - %s.\n        Script has been stopped." %err
  print text
  sys.exit(1)

# PRINT WARNING MESSAGE
# ====================================
def warning(warn):
  text="WARNING - %s.\n          Script continues." % warn
  print text

# SKIP AN ERROR
# =============
def skiperrors(err):
  print "Skipping error: "+err

# DISPLAY ERROR NUMBER AND STOP SCRIPT (DebugError)
# =================================================
def de(x):
  text="Error %d occured. Script has been stopped." % x
  print text
  sys.exit(1)

# SHOW CONTENT OF VARIABLE AND STOP SCRIPT (DebugShow)
# ====================================================
def ds(x):
  print "The content of the specified variable is:"
  print x
  print "Script has been stopped."
  sys.exit(1)

#  ======================================================================
#    L O G F I L E   F U N C T I O N   G R O U P
#  ======================================================================

# INITIALIZE NMR_VALIBASE.LOG WHERE ALL THE WARNINGS AND ERRORS ARE COLLECTED
# =============================================================================
def log_init():
  logfile=open("nmr_valibase.log","a")
  logfile.write("NMR_VALIBASE LOGFILE\n")
  logfile.write("======================\n\n")
  logfile.write("On my watch it's %s.\n\n" % time.ctime(time.time()))
  logfile.write("This is not one of those LOG - files containing loads of useless\n")
  logfile.write("warnings. If NMR_VALIBASE could solve a problem,you won't read\n")
  logfile.write("about it here  ( as there's at least one problem with every file\n");
  logfile.write("processed.- ;-) If a WARNING is given, it means that a data base\n");
  logfile.write("entry is faulty,incomplete or missing. Every WARNING should thus\n");
  logfile.write("be checked manually... Sorry for every line below..\n\n")
  logfile.close()
  try: os.chmod("nmr_valibase.log",0666)
  except: pass

# ADD MESSAGE TO NMR_VALIBASE.LOG
# =================================
def log_message(text):
  logfile=open("nmr_valibase.log","a")
  logfile.write(text+"\n")
  logfile.close()

# CALCULATE THE PASSED TIME
# =========================
def log_passedtime(starttime,endtime):
  passedtime = endtime-starttime
  hours = int(passedtime/3600)
  minutes = int(passedtime%3600/60)
  seconds = int(passedtime%3600%60)
  return hours,minutes,seconds

#  ======================================================================
#    M P I   F U N C T I O N   G R O U P
#  ======================================================================

# GROUP LIST
# ==========
# SEPARATE A LIST FOR USE ON DIFFERENT PROCs
def mpi_setrange(list,myid,numproc):
  # SET BOUNDS
  upper,lower = len(list),0
  # SET INTERVAL
  interval=upper-lower
  # SET LOCAL INTERVAL
  myinterval=interval/numproc
  # DETERMINE MYLOWER
  mylower=lower+myid*myinterval
  # DETERMINE MYUPPER
  if myid==numproc-1:
    myupper=upper
  else:
    myupper=mylower+myinterval
  # RETURN BOUNDS
  return mylower,myupper

#  ======================================================================
#    P D B   F I L E   F U N C T I O N   G R O U P
#  ======================================================================

# RESIDUE INDEX
# =============
# MAP RESIDUE NUMBER TO RESIDUE INDEX
def pdb_resindex(pdb,residuenumber):
  for residue in pdb.residues:
    if residue.number == residuenumber:
      return pdb.residues.index(residue)
  return None


# EXTRACT DISULFIDES
# ==================
# FUNCTION EXTRACT DISULFIDES FROM A PDB FILE
# BASED ON THE SSBONDS FIELD
def pdb_getdisulfides(pdbfile):
  # READ THE PDBFILE
  content = open(pdbfile,'r').readlines()
  # GO THROUGH THE CONTENT
  found, no_models = 0,0
  list = []
  for line in content:
    sline = string.split(line)
    if sline[0]=='SSBOND':
      if sline[5]=='CYS':
        disu = [sline[3],int(sline[4]),sline[6],int(sline[7])]
      if sline[4]=='CYS':
        disu = [int(sline[3]),int(sline[5])]
      list.append(disu)
    if line[0:4]=='ATOM':
      break
  return list

# PDB2SEQ
# =======
# EXTRACT SEQUENCE FROM PDBFILE
def pdb_pdb2seq(pdbfile,sequencefile,xplorflag=0):
  print "Reading sequence from PDB file",
  if xplorflag: print "(XPLOR format)."
  else: print "(PDB format)."
  pdb = pdb_file.Structure(pdbfile)
  seqfile = open(sequencefile,'w')
  rcount = 0
  for chain in pdb.peptide_chains:
    if not xplorflag:
      id = chain.chain_id
    else:
      id = chain.segment_id
    seqfile.write("> %s\n"%id)
    rcount += len(chain.sequence3())
    for res in chain.sequence3():
      seqfile.write("%s\n"%res)
  seqfile.close()
  print "Wrote %i chain(s) and %i residue(s) to sequence file."\
        %(len(pdb.peptide_chains),rcount)

# GET HIS PROTONATION STATES
# ==========================
# FUNCTION EXTRACTS THE HIS PROTONATION
# STATES FROM THE PROVIDED PDBFILE
def pdb_gethisprotonation(pdbfile):
  prot = []
  # READ PDB FILE, MODEL 1
  pdb = pdb_file.Structure(pdbfile)
  for chain in pdb.peptide_chains:
    for residue in chain:
      # CHECK HISTIDINES ONLY
      if residue.name=='HIS':
        eflag,dflag=1,1
        for atom in residue.atom_list:
          # SET FLAGS
          if atom.name == 'HD1': eflag = 0
          if atom.name == 'HE2': dflag = 0
        # SET PROTONATION STATES
        if chain.chain_id != "":
          if eflag: prot.append(['HISE',chain.chain_id,residue.number])
          if dflag: prot.append(['HISD',chain.chain_id,residue.number])
        else:
          if eflag: prot.append(['HISE',residue.number])
          if dflag: prot.append(['HISD',residue.number])
  return prot

# DETERMINE NUMBER OF MODELS
# ==========================
# THE NUMBER OF MODELS IN THE PDBFILE IS RETURNED
def pdb_models(pdbfile):
  # READ THE PDBFILE
  file = open(pdbfile,'r')
  content = file.readlines()
  file.close()
  # GO THROUGH THE CONTENT
  found, no_models = 0,0
  for line in content:
    sline = string.split(line)
    if sline[0]=='MODEL':
      no_models += 1
    if line[0:4]=='ATOM':
      if no_models == 0:
        no_models = 1
  return no_models
#  ======================================================================
#    A V E R A G I N G   F U N C T I O N   G R O U P
#  ======================================================================

# AVERAGE SURFACE
# ===============
# c      = smudge factor
# cutoff = datapoint density
def avg_surface(xaxis,yaxis,xyzlist,c=1,cutoff=1.0):
  xydict = {}
  vlist = []
  for x in xaxis:
    for y in yaxis:
      sumtop,sumbot = 0,0
      for el in xyzlist:
        mult = math.exp(-((x-el[0])**2+(y-el[1])**2)/c)
        sumtop += el[2]*mult
        sumbot += mult
      xydict[x]=xydict.get(x,{})
      score = sumtop/sumbot
      if sumbot < cutoff: xydict[x][y]=0.0
      else: xydict[x][y]=score
      vlist.append(sumtop/sumbot)
  return xydict

# AVERAGE COLUMN
# ==============
# DETERMINE THE AVERAGE AND STANDARD DEVIATION OF A COLUM OF VALUES IN A FILE
def avg_filecolumn(filename,column):
  # READ THE FILE
  text = open(filename,'r')
  lines = text.readlines()
  text.close()
  sum, sumsq, n = 0,0,0
  for line in lines:
    line = string.split(line)
    num = float(line[column-1])
    sum = sum + num
    sumsq = sumsq + num*num
    n = n + 1
  # DETERMINE THE AVERAGE
  avg = float(sum)/n
  sd = math.sqrt((sumsq - sum*sum/n)/(n-1))
  return [avg,sd]

# AVERAGE LIST
# ============
# DETERMINE THE AVERAGE AND STANDARD DEVIATION OF A LIST OF VALUES
# sd FLAG DECIDES WHETHER SD IS RETURNED OR NOT
def avg_list(list,sdflag=1):
  # IF WE HAVE MORE THAN ONE VALUE
  if len(list)>1:
    sum,sumsq,n=0.0,0.0,0
    for element in list:
        sum = sum + element
        sumsq = sumsq + element**2
        n=n+1
    # DETERMINE AVERAGE AND SD
    try:
      avg = sum/n
      sd = math.sqrt((sumsq - sum*sum/n)/(n-1))
    except ValueError:
      avg = 0.0
      sd = 0.0
  # IN CASE OF ONLY ONE VALUE
  elif len(list)==1:
    avg = list[0]
    sd = 0.0
  # IN CASE OF EMPTY LIST
  else:
    avg = 0.0
    sd = 0.0
  # RETURN AVG AND SD
  if sdflag==1: return [avg,sd]
  # RETURN ONLY AVG
  else: return avg

# AVERAGE LIST WITH SD'S
# ======================
# DETERMINE THE AVERAGE AND STANDARD DEVIATION OF A LIST OF VALUES
# EACH WITH IT'S OWN STANDARD DEVIATION. INPUT IS LIST OF LISTS
# WITH EACH LIST LENGTH 2: VALUE AND SD
def avg_listsd(list):
  # IF WE HAVE MORE THAN ONE VALUE
  if len(list)>1:
    sum,sumsq,sumsdsq=0.0,0.0,0.0
    n = 0
    for element in list:
        sum = sum + element[0]
        sumsdsq = sumsdsq + element[1]**2
        n=n+1
    # DETERMINE AVERAGE AND SD
    avg = sum/n
    sd = math.sqrt(sumsdsq)/n
  # IN CASE OF ONLY ONE VALUE
  else:
    avg=list[0][0]
    sd=list[0][1]
  return [avg,sd]

#  ======================================================================
#    L I S T   F U N C T I O N   G R O U P
#  ======================================================================

# PERMUTE LIST
# ============
# RETURN ALL PERMUTATIONS OF PROVIDED LIST
def list_permutations(lst):
  if len(lst) == 1:
    return  [lst]
  if len(lst) == 2:
    return [ lst, [lst[1],lst[0]] ]
  lop = []
  first = lst[0]
  rest = lst[1:]
  restprms = list_permutations(rest)
  for permutation in restprms:
    for i in range(1 + len(permutation)):
      newp = permutation[:i]+[first]+permutation[i:]
      lop.append(newp)
  return lop

# DETERMINE CORRELATION
# =====================
# RETURN THE PEARSON CORRELATION COEFFICIENT
# BETWEEN TWO LISTS OF NUMBERS
def list_cc(xlist,ylist):
  # PEARSON'S CORRELATION COEFFICIENT
  n = len(xlist)
  sumx,sumy,sumx2,sumy2,sumxy=.0,.0,.0,.0,.0
  for i in range(len(xlist)):
    sumx  += xlist[i]
    sumy  += ylist[i]
    sumx2 += xlist[i]**2
    sumy2 += ylist[i]**2
    sumxy += xlist[i]*ylist[i]
  cc = (n*sumxy-(sumx*sumy))/math.sqrt(((n*sumx2)-sumx**2)*((n*sumy2)-sumy**2))
  return cc

# DETERMINE RMS DEVIATION
# =======================
# RETURN CHI-SQUARE VALUE
def list_chi2(predicted,observed):
  chi2 = 0.0
  for i in range(len(predicted)):
    chi2 += (predicted[i]-observed[i])**2
  return chi2

# DETERMINE FLUCTATIONS
# ====================
# DETERMINE THE FLUCTATIONS IN A LIST OF COORDINATES
def coord_fluct(list):
  # IF WE HAVE MORE THAN ONE VALUE
  if len(list)>1:
    n = 0
    sum = [0,0,0]
    sumsq = [0,0,0]
    for coord in list:
      for i in range(len(coord)):
        sum[i] += coord[i]/len(list)
        sumsq[i] += coord[i]**2/len(list)
      n=n+1
    # DETERMINE FLUCTATIONS
    fl = 0.0
    for i in range(len(coord)):
      fl += sumsq[i]-sum[i]**2
    return fl
  # IN CASE OF ONLY ONE COORDINATE
  elif len(list)==1: return 0.0
  # IN CASE OF EMPTY LIST
  else: return 0.0

#  ======================================================================
#    D I C T I O N A R Y   F U N C T I O N   G R O U P
#  ======================================================================

# READ DICTIONARY
# ===========================
# READ A DICTIONARY FROM DISC
def dct_read(filename):
  try: dctfile = open(filename,"r")
  except: error("Dictionary %s could not be read" % filename)
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
        if (i==-1):  error("No equals sign found in %s at %s" % (filename,line))
        if (i==0):   error("No data found before equals sign in %s at %s" % (filename,line))
        if (i==l-1): error("No data found behind equals sign in %s at %s" % (filename,line))
        # ADD TO DICTIONARY
        dct[string.strip(line[:i])] = string.strip(line[i+1:])
  return(dct)

# WRITE DICTIONARY
# ==========================
# WRITE A DICTIONARY TO DISC
def dct_write(dct,filename):
  try: dctfile = open(filename,"w")
  except: error("Dictionary %s could not be written" % filename)
  # PRINT ENTRIES
  for key in dct.keys():
    # PRINT KEY AND VALUE
    dctfile.write("%s = %s\n" % (key,dct[key]))
  dctfile.close()

#  ======================================================================
#    X P L O R   F U N C T I O N   G R O U P
#  ======================================================================


# FORMAT DISULFIDES
# =================
# FUNCTION FORMATS A LIST OF DISULFIDES
def xplor_formatdisu(disulist):
  xplrstr = ""
  if len(disulist)>0:
    xplrstr+="noe\n"
    for elem in disulist:
      if len(elem)==2:
        xplrstr+="    assign (resid %4i and name sg) (resid %4i and name sg)  2.02 0.1 0.1\n"%(elem[0],elem[1])
      elif len(elem)==4:
        xplrstr+="    assign (segi %4s and resid %4i and name sg) (segi %4s and resid %4i and name sg)  2.02 0.1 0.1\n"%(elem[0],elem[1],elem[2],elem[3])
    xplrstr+="end\n"
  return xplrstr


# FORMAT DATAFILE
# ===============
# FUNCTION READS A RESTRAINTDICT AND FORMATS IT FOR XPLOR
def xplor_formatdict(restraintdict,averaging='sum'):
  xplrstr = ""
  # READ THE DISTANCES
  if restraintdict.has_key("DIST"):
    xplrstr+="noe\n"
    xplrstr+="  averaging * %s\n"%averaging
    xplrstr+="  nres=%i\n"%(max(100,float(len(restraintdict["DIST"]))*10))
    # WE SORT THE RESTRAINTS HERE, THIS IS NECESSARY FOR
    # COMPARATIVE RUNS!
    rlist = []
    for restraint in restraintdict["DIST"]:
      rlist.append(restraint.format("XPLOR"))
    rlist.sort()
    for restraint in rlist:
      xplrstr+="  %s\n"%restraint
    xplrstr+="end\n"
  # READ THE DIHEDRALS
  if restraintdict.has_key("DIHE"):
    xplrstr+="restraint dihe\n"
    xplrstr+="  nass=%i\n"%(float(len(restraintdict["DIHE"]))*1.5)
    # WE SORT THE RESTRAINTS HERE, THIS IS NECESSARY FOR
    # COMPARATIVE RUNS!
    dlist = []
    for restraint in restraintdict["DIHE"]:
      dlist.append(restraint.format("XPLOR"))
    dlist.sort()
    for restraint in dlist:
      xplrstr+="  %s\n"%restraint
    xplrstr+="end\n"
  # WE RETURN THE FORMATTED XPLOR STRING
  return xplrstr


# FORMAT LIST OF RESTRAINTS
# =========================
# FUNCTION READS A RESTRAINTLIST AND FORMATS IT FOR XPLOR
def xplor_formatlist(restraintlist,averaging='sum'):
  # CYCLE AND GROUP RESTRAINTS
  dist, dihe = [],[]
  for r in restraintlist:
    if r.type == 'DIST': dist.append(r)
    elif r.type == 'DIHE': dihe.append(r)
  xplrstr = ""
  # READ THE DISTANCES
  if len(dist)>0:
    xplrstr+="noe\n"
    xplrstr+="  averaging * %s\n"%averaging
    xplrstr+="  class=all\n"
    xplrstr+="  nres=%i\n"%(max(100,float(len(dist))*5))
    # WE SORT THE RESTRAINTS HERE, THIS IS NECESSARY FOR
    # COMPARATIVE RUNS!
    rlist = []
    for r in dist:
      rlist.append(r.format("XPLOR"))
    rlist.sort()
    for r in rlist:
      xplrstr+="  %s\n"%r
    xplrstr+="end\n"
  # READ THE DIHEDRALS
  if len(dihe)>0:
    xplrstr+="restraint dihe\n"
    xplrstr+="  nass=%i\n"%(float(len(dihe))*1.5)
    # WE SORT THE RESTRAINTS HERE, THIS IS NECESSARY FOR
    # COMPARATIVE RUNS!
    dlist = []
    for r in dihe:
      dlist.append(r.format("XPLOR"))
    dlist.sort()
    for r in dlist:
      xplrstr+="  %s\n"%r
    xplrstr+="end\n"
  # WE RETURN THE FORMATTED XPLOR STRING
  return xplrstr


# RENUMBER PSF FILE
# =================
# RENUMBER PSF FILE ACCORDING TO A PDBFILE
def xplor_renumberpsf(inpsf,outpsf,pdbfile,xplorflag=0):
  print "Renumbering PSF file."
  # READ PDB FILE
  pdb = pdb_file.Structure(pdbfile)
  pdbd = {}
  for chain in pdb.peptide_chains:
    # SEE WHERE TO GET SEGMENT OR CHAIN IDS
    if xplorflag: ch = chain.segment_id
    else: ch = chain.chain_id
    if len(ch)==0: ch=' '
    for residue in chain:
      pdbd[ch]=pdbd.get(ch,[])+[residue]
  # READ INPSF
  inpsf = open(inpsf,'r').readlines()
  # INITIALIZE OUTLIST
  outlist = []
  section = None
  currentchain = None
  offset,pdbcount = None,0
  for line in inpsf:
    # CHECK SECTION
    if '!' in line:
      index = line.index('!')
      section = line[index+1:-1]
    # EMPTY LINE INDICATES END OF SECTION
    elif len(line)==1:
      section = None
    # LINES THAT NEED TO BE ALTERED ARE IN THE ATOM SECTION
    elif section == 'NATOM':
      # ASSIGN CURRENT CHAIN
      if currentchain==None:
        currentchain = line[9]
      pchain = line[9]
      if len(pchain)==0: pchain=' '
      # CHECK CHAIN
      if pchain!=currentchain:
        offset=None
        pdbcount = 0
        currentchain=pchain
      presname = line[19:22]
      presnumb = int(line[14:19])
      # SET PSF FIRST RESIDUE NUMBER
      if offset==None:
        psfnum = presnumb
        pdbres = pdbd[pchain][pdbcount]
        offset = pdbres.number - psfnum
      # HANDLE THE FOLLOWING RESIDUES
      else:
        # MOVE TO NEXT RESIDUE
        if presnumb!=psfnum:
          psfnum = presnumb
          pdbcount += 1
        pdbres = pdbd[pchain][pdbcount]
      # SANITY CHECK
      if presname != pdbres.name: error("PSF mismatch")
      # CONSTRUCT UPDATED LINE
      line = "%s%s%s"%(line[:14],
                       str(pdbres.number).ljust(5),
                       line[19:])
    outlist.append(line)
  # WRITE OUTPSF
  open(outpsf,'w').writelines(outlist)
  print "Renumbered PSF file."


# CREATE PSF FROM PDB FILE
# ========================
#
def xplor_pdb2psf(inpdb,outpsf,xplor=None,topology=None,
                  peptide=None,xplorflag=0):
  # DELETE PSF IF EXISTS
  if os.path.exists(outpsf): os.remove(outpsf)
  # TAKE DEFAULTS FOR TOPOLOGY, PEPTIDE AND XPLOR
  if not topology: topology = nmvconf["X_TOP"]
  if not peptide: peptide = nmvconf["X_PEP"]
  if not xplor: xplor = nmvconf["XPLOR"]
  # BUILD SEQUENCE FILE
  seqfile = outpsf+'.tmp'
  pdb_pdb2seq(inpdb,seqfile,xplorflag=xplorflag)
  patches = {}
  # GET DISULFIDES
  patches["DISU"] = pdb_getdisulfides(inpdb)
  # GET HISPROTONATION STATES
  prots = pdb_gethisprotonation(inpdb)
  for el in prots:
    if len(el)==3:
      patches[el[0]]=patches.get(el[0],[])+[[el[1],el[2]]]
    else:
      patches[el[0]]=patches.get(el[0],[])+[[el[1]]]
  # BUILD THE STRUCTURES
  xplor_buildstructure(outpsf,seqfile,'sequence',
                       topology,peptide,xplor,patches=patches)
  # CLEAN UP
  os.remove(seqfile)


# BUILD STRUCTURE
# ===============
# BUILD STRUCTURE FILE BASED
# ON SEQUENCE OR COORDINATES
def xplor_buildstructure(psf,basefile,base="sequence",
                         topology=None,peptide=None,xplor=None,patches=None):
  # FIRST WE DELETE ANY OLD FILES
  if os.path.exists(psf): os.remove(psf)
  # TAKE DEFAULTS FOR TOPOLOGY, PEPTIDE AND XPLOR
  if not topology: topology = nmvconf["NMRI_TOP"]
  if not peptide: peptide = nmvconf["NMRI_PEP"]
  if not xplor: xplor = nmvconf["XPLOR"]
  # INITIALIZE THE XPLOR SCRIPT CLASS
  xplr = xplor_script(xplor)
  # READ TOPOLOGY FILE
  xplr.write("topology\n  @%s\nend"%topology)
  # GENERATE PROTEIN FROM SEQUENCE / COORDINATES
  # USE EITHER SEQUENCE OR COORDINATES TO BUILD
  # THE STRUCTURE FILE
  if base=='sequence':
    seqdict = qn_readsequence(basefile)
    for key in seqdict:
      xplr.write("segment")
      if key=='\n' or key==' ':
        xplr.write("  name=\" \" ")
      else:
        xplr.write("  name=%s"%key)
      xplr.write("  chain")
      xplr.write("    @%s"%peptide)
      xplr.write("    sequence")
      for aa in seqdict[key]:
        xplr.write("      %s"%aa)
      xplr.write("    end")
      xplr.write("  end")
      xplr.write("end")
  if base=='coordinates':
    segment = "\" \""
    xplr.write("segment")
    xplr.write("  name=%s"%segment)
    xplr.write("  chain")
    xplr.write("    @%s"%peptide)
    xplr.write("    coordinates\n      @%s\n    end"%basefile)
    xplr.write("  end\nend")
  # HANDE THE PATCHES
  if patches:
    # DISULFIDE BRIDGES
    if patches.has_key("DISU"):
      for ss in patches["DISU"]:
        xplr.write("patch DISU")
        if len(ss)==2:
          xplr.write("  reference=1=( resid %i ) reference=2=( resid %i )"%(ss[0],ss[1]))
        elif len(ss)==4:
          xplr.write("  reference=1=( resid %i and segid %s ) reference=2=( resid %i and segid %s )"%(ss[1],ss[0],ss[3],ss[2]))
        xplr.write("end")
    # HISTIDINE PATCHES
    if patches.has_key("HISE"):
      for his in patches["HISE"]:
        xplr.write("patch HISE")
        if len(his)==1:
          xplr.write("  reference=nil=( resid %i )"%(his[0]))
        elif len(his)==2:
          xplr.write("  reference=nil=( resid %i and segid %s )"%(his[1],his[0]))
        xplr.write("end")
    if patches.has_key("HISD"):
      for his in patches["HISD"]:
        xplr.write("patch HISD")
        if len(his)==1:
          xplr.write("  reference=nil=( resid %i )"%(his[0]))
        elif len(his)==2:
          xplr.write("  reference=nil=( resid %i and segid %s )"%(his[1],his[0]))
        xplr.write("end")
  # WRITE OUT THE PSF FILE
  xplr.write("write structure")
  xplr.write("  output=%s"%psf)
  xplr.write("end")
  print "Building XPLOR structure file."
  # SUBMIT XPLOR JOB
  xplr.submit()
  print "Done."


# PATCH STRUCTURE
# ===============
# PATCH PSF FILE BASED ON THE PROVIDED
# PATCHES DICTIONARY
def xplor_patchstructure(inpsf,outpsf,patches,topology=None,xplor=None):
  # FIRST WE DELETE ANY OLD FILES
  if os.path.exists(outpsf): os.remove(outpsf)
  # TAKE DEFAULTS FOR XPLOR
  if not xplor: xplor = nmvconf["XPLOR"]
  if not topology: topology = nmvconf["Q_TOP"]
  # INITIALIZE THE XPLOR SCRIPT CLASS
  xplr = xplor_script(xplor)
  # READ TOPOLOGY FILE
  xplr.write("topology\n  @%s\nend"%topology)
  # READ THE PSF FILE
  xplr.write("structure")
  xplr.write("  @%s"%inpsf)
  xplr.write("end")
  # HANDE THE PATCHES
  if len(patches.keys())>0:
    # DISULFIDE BRIDGES
    if patches.has_key("DISU"):
      for ss in patches["DISU"]:
        xplr.write("patch DISU")
        if len(ss)==2:
          xplr.write("  reference=1=( resid %i ) reference=2=( resid %i )"%(ss[0],ss[1]))
        elif len(ss)==4:
          xplr.write("  reference=1=( resid %i and segid %s ) reference=2=( resid %i and segid %s )"%(ss[1],ss[0],ss[3],ss[2]))
        xplr.write("end")
    # HISTIDINE PATCHES
    if patches.has_key("HISE"):
      for his in patches["HISE"]:
        xplr.write("patch HISE")
        if len(his)==1:
          xplr.write("  reference=nil=( resid %i )"%(his[0]))
        elif len(his)==2:
          xplr.write("  reference=nil=( resid %i and segid %s )"%(his[1],his[0]))
        xplr.write("end")
    if patches.has_key("HISD"):
      for his in patches["HISD"]:
        xplr.write("patch HISD")
        if len(his)==1:
          xplr.write("  reference=nil=( resid %i )"%(his[0]))
        elif len(his)==2:
          xplr.write("  reference=nil=( resid %i and segid %s )"%(his[1],his[0]))
        xplr.write("end")
  # WRITE OUT THE PSF FILE
  xplr.write("write structure")
  xplr.write("  output=%s"%outpsf)
  xplr.write("end")
  print "Patching XPLOR structure file with %i patches."%len(patches.keys())
  # SUBMIT XPLOR JOB
  xplr.submit()
  print "Done."


# GENERATE EXTENDED
# =================
# GENERATE EXTENDED STRUCTURE
def xplor_generatetemplate(template,psf,parameter=None,xplor=None):
  print "Building XPLOR template file."
  # FIRST WE DELETE ANY OLD FILES
  if os.path.exists(template): os.remove(template)
  # TAKE DEFAULTS FOR TOPOLOGY, PEPTIDE AND XPLOR
  if not parameter: parameter = nmvconf["Q_PAR"]
  if not xplor: xplor = nmvconf["XPLOR"]
  # INITIALIZE THE XPLOR SCRIPT CLASS
  xplr = xplor_script(xplor)
  # READ THE STRUCTURE FILE
  xplr.write("structure\n  @%s\nend"%psf)
  # READ PARAMETER FILE
  xplr.write("evaluate ($par_nonbonded=PROLSQ)")
  xplr.write("parameter\n  @%s\nend"%parameter)
  xplr.write("""
    vector ident (x) ( all )
    vector do (x=x/10.) ( all )
    vector do (y=random(0.5) ) ( all )
    vector do (z=random(0.5) ) ( all )
    vector do (fbeta=50) (all)         {*Friction coefficient, in 1/ps.*}
    vector do (mass=100) (all)                 {*Heavy masses, in amus.*}

    parameter
      nbonds
        cutnb=5.5 rcon=20. nbxmod=-2 repel=0.9  wmin=0.1
        tolerance=1. rexp=2 irexp=2 inhibit=0.25
      end
    end

    flags exclude * include bond angle vdw end
    minimize powell nstep=50  nprint=10 end

    flags include impr end
    minimize powell nstep=50 nprint=10 end

    dynamics  verlet
      nstep=50  timestep=0.001 iasvel=maxwell  firsttemp= 300.
      tcoupling = true  tbath = 300.   nprint=50  iprfrq=0
    end

    parameter
      nbonds
        rcon=2. nbxmod=-3 repel=0.75
      end
    end

    minimize powell nstep=100 nprint=25 end

    dynamics  verlet
      nstep=500  timestep=0.005 iasvel=maxwell  firsttemp= 300.
      tcoupling = true  tbath = 300.   nprint=100  iprfrq=0
    end

    flags exclude vdw elec end
    vector do (mass=1.) ( name h* )
    hbuild selection=( name h* ) phistep=360 end

    flags include vdw elec end

    minimize powell nstep=200 nprint=50 end
  """)
  # WRITE OUT THE TEMPLATE FILE
  xplr.write("write coordinates")
  xplr.write("  output=%s"%template)
  xplr.write("end")
  # SUBMIT XPLOR JOB
  xplr.submit()
  print "Done."

# REBUILD HYDROGENS
# =================
# REBUILD HYDROGEN ATOMS IN PDB FILE
def xplor_hbuild(inpdb,outpdb,psf,
                 xplor=None,
                 parameter=None,
                 topology=None):
  # TAKE DEFAULT PARAMETERS
  if not xplor: xplor = nmvconf["XPLOR"]
  if not parameter: parameter = nmvconf["PAR_PROT"]
  if not topology: topology = nmvconf["TOP_PROT"]
  # INITIALIZE THE XPLOR SCRIPT CLASS
  xplr = xplor_script(xplor,scriptpath=nmvconf["TMP"])
  # READ THE STRUCTURE FILE
  xplr.write("structure\n  @%s\nend"%psf)
  # READ PARAMETER FILE
  xplr.write("evaluate ($par_nonbonded=OPLSX)")
  xplr.write("parameter\n  @%s\nend"%parameter)
  # READ TOPOLOGY
  xplr.write("topology\n  @%s\nend"%topology)
  # READ PDB FILE
  xplr.write("coordinates @%s"%inpdb)
  xplr.write("""
  ! Minimize proton positions to remove problems with wrong
  ! stereochemical types from other programs

  flags exclude vdw elec end
  hbuild selection=(name H*) end
  flags include vdw elec end
  constraints fix=(not hydrogen) end
  minimize powell nstep=500 nprint=50 end

  ! now minimize the protons in the OPLS force field
  {*==========================================================================*}
  {*================== SET VALUES FOR NONBONDED PARAMETERS ===================*}
  {*==========================================================================*}
  parameter
    nbonds
      repel=0
      nbxmod=5 atom cdiel shift
      cutnb=9.5 ctofnb=8.5 ctonnb=6.5 eps=1.0 e14fac=0.4 inhibit 0.25
      wmin=0.5
      tolerance  0.5
    end
  end
  flags exclude * include bond angle impr vdw elec end
  minimize powell nstep=500 nprint=50 end
  constraints fix=(not all) end
  """)
  # WRITE OUT THE PDB FILE
  xplr.write("write coordinates output=%s end"%outpdb)
  xplr.write("stop")
  xplr.submit()
#  ======================================================================
#    Q U E E N   F U N C T I O N   G R O U P
#  ======================================================================

# CREATE PROJECT
# ==============
# CREATE QUEEN PROJECT DIRECTORY FROM QUEEN CONF FILE
def qn_createproject(nmvconf,projectname=None,projectpath=None):
  # CHECK IF PROJECTPATH EXISTS
  #print '>',nmvconf
  if not projectpath:
    projectpath = nmvconf["Q_PROJECT"]
  if os.path.exists(projectpath):
    if not projectname:
        qpath = projectpath
    else:
        qpath = os.path.join(projectpath,projectname)
    #print '>',qpath

    if os.path.exists(qpath):
      error("Project already exists")
    else:
      print( "==> Creating QUEEN project directory tree at %s", qpath )
      # CREATE THE PROJECT DIR
      os.makedirs(qpath)
      # CREATE THE NECESSARY SUBDIRS
      for key in nmvconf.keys():
        if key[:2]=='Q_' and key not in ['Q_PEP','Q_TOP','Q_PAR']:
          subpath = os.path.dirname(nmvconf[key])
          # TAKE ONLY THE RELATIVE PATHS
          if len(subpath)>0 and subpath[0]!='/':
            # BUILD THE FULL PATH
            fullpath = os.path.join(qpath,subpath)
            # CREATE THE SUBDIRS
            try:
              os.mkdir(fullpath)
            except OSError:
              # WE PROBABLY HAVE TO GO DEEPER THAN ONE DIR
              if fullpath[0]=='/': basepath = '/'
              else: basepath=''
              fullpath = fullpath.split('/')
              # CONSTRUCT THE FULL PATH ONE BY ONE
              for element in fullpath:
                basepath = os.path.join(basepath,element)
                if not os.path.exists(basepath):
                  os.mkdir(basepath)
  else:
    error("Project path does not exist")

# READ SEQUENCE
# =============
# READ SEQUENCE FILE
def qn_readsequence(sequencefile):
  print "Reading sequence file."
  dict = {}
  # OPEN FILE
  content = open(sequencefile,'r').readlines()
  if content[0][0]!='>' and len(content[0])!=4:
    error("Start sequence file with chain identifier")
  rcount = 0
  for line in content:
    if line[0]=='>':
      # START NEW CHAIN
      key = line[2]
      dict[key]=[]
    else:
      # APPEND TO CHAIN
      dict[key].append(line[:-1])
      rcount += 1
  print "Read %i chain(s) and %i residue(s) from sequence file."%(len(dict.keys()),rcount)
  # RETURN THE DICTIONARY
  return dict

# READ PATCH DICTIONARY
# =====================
# DICTIONARY IS ALLOWED TO HAVE MORE VALUES WITH
# ONE KEY, VALUES ARE ADDED TO A LIST
def qn_readpatches(filename):
  print "Reading XPLOR patches."
  try: dctfile = open(filename,"r")
  except: error("Dictionary %s could not be read" % filename)
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
        if (i==-1):  error("No equals sign found in %s at %s" % (filename,line))
        if (i==0):   error("No data found before equals sign in %s at %s" % (filename,line))
        if (i==l-1): error("No data found behind equals sign in %s at %s" % (filename,line))
        # ADD TO DICTIONARY
        key = string.strip(line[:i])
        value = string.split(line[i+1:])
        if len(value)==1:
          value = [int(value[0])]
        elif len(value)==2:
          value = [value[0],int(value[1])]
        else:
          error("Dictionary format error found in %s at %s" % (filename,line))
        if dct.has_key(key):
          dct[key] += [value]
        else:
          dct[key] = [value]
  print "Read %i XPLOR patches."%(len(dct.keys()))
  return dct

# READ DISULFIDES
# ===============
# FUNCTION READS DISULFIDES
def qn_readdisulfides(disulfidefile):
  print "Reading disulfide bridgjes."
  dict = {}
  # OPEN FILE
  content = open(disulfidefile,'r').readlines()
  for line in content:
    sline = string.split(line)
    if len(sline)==4:
      dict["DISU"]=dict.get("DISU",[]) + [[sline[0],int(sline[1]),sline[2],int(sline[3])]]
    elif len(sline)==2:
      dict["DISU"]=dict.get("DISU",[]) + [[int(sline[0]),int(sline[1])]]
    else:
      error("Invalid disulfide line!")
  print "Read %i disulfide bridges."%(len(dict.keys()))
  return dict

# WRITE DISULFIDES
# =================
# FUNCTION READS DISULFIDES FROM PDBFILE
# AND WRITES TO DISULFIDE FILE
def qn_writedisulfides(pdbfile,disulfidefile):
  # EXTRACT THE DISULFIDES
  disulist = pdb_getdisulfides(pdbfile)
  # WRITE THE DISULFIDEFILE
  file = open(disulfidefile,'w')
  for disu in disulist:
    for elem in disu:
      file.write("%s\t"%elem)
    file.write("\n");
  file.close()

# WRITE HISPATCHES
# ================
# FUNCTION READS HIS PROTONATION STATE
# FROM PDB FILE AND WRITES A PATCHES FILE
def qn_writehispatches(pdbfile,patchesfile):
  # EXTRACT THE STATES
  prot = pdb_gethisprotonation(pdbfile)
  # WRITE THE DISULFIDEFILE
  file = open(patchesfile,'w')
  for state in prot:
    file.write("%s = %s %s\n"%(state[0],state[1],state[2]))
  file.close()

# PDB2SEQ
# =======
# EXTRACT SEQUENCE FROM PDBFILE
def qn_pdb2seq(pdbfile,sequencefile,xplorflag=0):
  print "Reading sequence from PDB file",
  if xplorflag: print "(XPLOR format)."
  else: print "(PDB format)."
  pdb = pdb_file.Structure(pdbfile)
  seqfile = open(sequencefile,'w')
  rcount = 0
  for chain in pdb.peptide_chains:
    if not xplorflag:
      id = chain.chain_id
    else:
      id = chain.segment_id
    seqfile.write("> %s\n"%id)
    rcount += len(chain.sequence3())
    for res in chain.sequence3():
      # HACK FOR RES NAMES WITH - OR + ADDED TO THEM
      res = res[:3]
      seqfile.write("%s\n"%res)
  seqfile.close()
  print "Wrote %i chain(s) and %i residue(s) to sequence file."\
        %(len(pdb.peptide_chains),rcount)

# SETUP XPLOR
# ===========
# SETUP XPLOR FROM QUEEN CONF FILE
def qn_setupxplor(nmvconf,projectname,projectpath=None):
  # READ THE CONFFILE
  dict = nmvconf
  # CREATE XPLOR INSTANCE
  xplr = xplor(dict["XPLOR"])
  xplr.topology = os.path.join(dict["Q_PATH"],dict["Q_TOP"])
  xplr.peptide = os.path.join(dict["Q_PATH"],dict["Q_PEP"])
  xplr.parameter = os.path.join(dict["Q_PATH"],dict["Q_PAR"])
  if not projectpath:
    base = os.path.join(dict["Q_PROJECT"],projectname)
  else:
    base = os.path.join(projectpath,projectname)
  xplr.patches = os.path.join(base,dict["Q_PATCHES"])
  xplr.disulfides = os.path.join(base,dict["Q_DISULFIDES"])
  xplr.psf = os.path.join(base,dict["Q_PSF"])
  xplr.template = os.path.join(base,dict["Q_TEMPLATE"])
  # RETURN THE XPLOR INSTANCE
  return xplr


def qn_seq2psf( queenProject, seqfile):
    """
    Generate psf file from seqfile.

    Return True on error, False on succes.
    """
    if not queenProject.exists():
        error("qn_seq2psf: Project directory does not exist. Please setup project first")
        return True
    #end if

    nmvconf     = queenProject.nmvconf
    projectpath = queenProject.projectpath
    psffile     = queenProject.psffile

    top = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_TOP"])
    pep = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_PEP"])
    par = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_PAR"])
    xpl = nmvconf["XPLOR"]

    patches = {}
    # CHECK FOR DISULFIDES
    disulfidefile = os.path.join(projectpath,nmvconf["Q_DISULFIDES"])
    if os.path.exists(disulfidefile):
        patches.update(qn_readdisulfides(disulfidefile))
    # CHECK FOR OTHER PATCHES
    patchesfile = os.path.join(projectpath,nmvconf["Q_PATCHES"])
    if os.path.exists(patchesfile):
        patches.update(qn_readpatches(patchesfile))
    xplor_buildstructure(psffile,seqfile,'sequence',top,pep,xpl,patches=patches)
    return False
#end def

def qn_psf2tem( queenProject, psffile ):
    """
    Generate psf file from psffile.

    Return True on error, False on succes.
    """
    if not queenProject.exists():
        error("qn_psf2tem: Project directory does not exist. Please setup project first")
        return True
    #end if

    nmvconf     = queenProject.nmvconf
    top = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_TOP"])
    pep = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_PEP"])
    par = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_PAR"])
    xpl = nmvconf["XPLOR"]

    xplor_generatetemplate(queenProject.temfile, psffile, par, xpl)
    return False
#end def

def qn_pdb2all( queenProject, pdbfile, xplorflag=0 ):
    """
    Generate all required template files in queen project from pdbfile.

    Return True on error, False on succes.
    """
    if not queenProject.exists():
        error("qn_pdb2all: QUEEN project directory does not exist. Please setup project first")
        return True
    #end if

    # Generate seq file
    qn_pdb2seq(pdbfile, queenProject.seqfile, xplorflag)

    # Generate psf file
    qn_seq2psf( queenProject, queenProject.seqfile)

    # RENUMBER PSF FILE
    psffile = queenProject.psffile
    inpsf = "%s.prenum"%psffile
    shutil.copy(psffile,inpsf)
    xplor_renumberpsf(inpsf,psffile,pdbfile,xplorflag)

    # BUILD TEMPLATE
    qn_psf2tem( queenProject, psffile )

    return False
#end def

def qn_test(nmvconf):
    """
    QUEEN testing routine
    """
    # CHECK PYTHON
    print "Checking your Python version."
    print "  Found Python version %s."%sys.version.split()[0]
    nmv_checkpython()
    print

    # CHECK THE QUEEN CONFIGURATION FILE
    print "Checking your configuration:"

    print "Checking if XPLOR path is correct...",
    if not os.path.exists(nmvconf["XPLOR"]):
      print "No."
      error("  Please set the correct path for XPLOR")
    else:
      print "Yes."
    print

    print "Testing QUEEN ..."
    # TEST WITH THE EXAMPLE
    print "  Temporarily switching Q_PROJECT to the example/ directory..."
    nmvconf["Q_PROJECT"]=nmvconf["Q_PATH"]
    project,dataset = 'example','all'
    # SETUP QUEEN
    print "  Initializing QUEEN...",
    queen = qn_setup(nmvconf,project,0,1)
    xplr  = qn_setupxplor(nmvconf,project)
    print "Ok."
    print "  Reading test set of restraints...",
    table = nmv_adjust(queen.table,'test')
    r = restraint_file(table,'r')
    r.read()
    print "Ok."
    print "  Calculating and validating output...",
    sys.stdout.flush()
    score = queen.uncertainty(xplr,{"DIST":r.restraintlist})
    print score
    if "%13.11f"%score=="4.55017471313":
      print "Installation ok."
    else:
      print "Problem."
      print "  Outcome of procedure not as expected."
      print
      print "Please don't change the restraint file 'test.tbl' in the example directory!"
      print "If you did so, please restore the directory to it's original state"
      print "and run the testsuite again."
    print
#end def

# SETUP QUEEN
# ===========
# SETUP QUEEN
def qn_setup(nmvconf,project,myid=0,numproc=1):
  """
  Setup QUEEN:
  GWV made this mostly into a dummy by moving it to the initialization of the queenbase instance
  """
  queen = queenbase(nmvconf,project)
  queen.numproc    = numproc
  queen.myid       = myid
  if numproc>1:
    import pypar
  # RETURN QUEEN INSTANCE
  return queen

# READ DATA
# =========
# PARSE DATASET DESCRIPTION FILE AND READ
# RESTRAINT FILES BASED ON THE RETURNED
# FILELIST
def qn_readdata(queen,datafile):
  filelist = qn_readdatafile(datafile)
  data = qn_readdatasets(queen,filelist)
  return data

# READ DATAFILE
# =============
# FUNCTION READS A DATASET DESCRIPTION FILE
def qn_readdatafile(datafile):
  print "Reading dataset description file."
  # WE KEEP A LIST IN ORDER TO RETAIN THE ORDER IN THE FILE
  filelist = []
  # READ AND PARSE THE DICTIONARY TYPE FILE
  try: dctfile = open(datafile,"r")
  except: error("Datasetfile %s could not be read" %datafile)
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
        if (i==-1):  error("No equals sign found in %s at %s" % (datafile,line))
        if (i==0):   error("No data found before equals sign in %s at %s" % (datafile,line))
        if (i==l-1): error("No data found behind equals sign in %s at %s" % (datafile,line))
        # ADD TO DICTIONARY
        dct[string.strip(line[:i])] = string.strip(line[i+1:])
      # END OF DICT
      if line[:2]=='//':
          filelist.append(dct)
          dct = {}
  print "Found %i restraint files in dataset."%(len(filelist))
  return filelist

# READ DATASETS
# =============
# FUNCTION READS A DATASET DESCRIPTION DICTIONARY
def qn_readdatasets(queen,datasets):
  data = {}
  # SET INFORMATION
  data["sets"]={}
  # ACTUAL DATA, LIST OF RESTRAINTS
  data["data"]=[]
  # BACKGROUND DATA, LIST OF RESTRAINTS
  data["bckg"]=[]
  # CYCLE THE AVAILABLE SETS
  for filedict in datasets:
    table = nmv_adjust(queen.table,filedict["FILE"])
    # READ THE RESTRAINT FILE
    r = restraint_file(table,'r',type=filedict["TYPE"])
    r.read()
    # SET THE BACKGROUND FLAG
    if not filedict.has_key("INFO"): filedict["INFO"]=1
    elif filedict["INFO"].lower()=='no' or filedict["INFO"].lower()=='n':
      filedict["INFO"]=0
    else: filedict["INFO"]=1
    # FILL DICTIONARY
    data["sets"][filedict["FILE"]] = r.restraintlist
    # ADD TO THE RIGHT DATA LIST
    if not filedict["INFO"]: data["bckg"] = data.get("bckg",[]) + r.restraintlist
    else: data["data"] = data.get("data",[]) + r.restraintlist
  return data

# READ INFORMATION FILE
# =====================
# FUNCTION READS A QUEEN INFORMATION FILE AND RETURNS A
# DICTIONARY WITH THE RESTRAINT STRINGS AS KEY AND THE
# INFORMATION AS VALUE
def qn_readinffile(file):
  print "Reading QUEEN information file."
  inf = {}
  comments = ['#','@','&']
  content = open(file,'r').readlines()
  for line in content:
    if line[0] not in comments:
      line = line.split()
      if len(line)==3: inf[line[2][1:-1]]=[float(line[1])]
      if len(line)==4: inf[line[3][1:-1]]=[float(line[1]),float(line[2])]
  return inf

# SORT INFORMATION FILE
# =====================
# FUNCTION READS A QUEEN INFORMATION FILE AND SORTS THE
# RESTRAINT IN THE FILE BASED ON THEIR INFORMATION VALUES
def qn_sortinffile(infile,outfile):
  comments = ['#','@','&']
  print "Sorting QUEEN information file."
  # OPEN OUTPUT FILE
  outf = open(outfile,'w')
  # OPEN INFILE AND EXTRACT HEADERS
  inff = open(infile,'r').readlines()
  for line in inff:
    if line[0] not in comments: break
    else: outf.write(line)
  lastline = inff[-1]
  # PARSE INFILE
  inf = qn_readinffile(infile)
  # SORT DICTIONARY BY VALUES
  infs = inf.items()
  infs.sort(lambda (k1,v1),(k2,v2): cmp(v2[0],v1[0]))
  count = 0
  for el in infs:
    count += 1
    if len(el[1])==2:
      outf.write("%10e %10e %10e \"%s\"\n"%(count,el[1][0],el[1][1],el[0]))
    else:
      outf.write("%10e %10e \"%s\"\n"%(count,el[1][0],el[0]))
  outf.write(lastline)
  outf.close()
  print "Wrote sorted file to:\n%s"%outfile

# TEST DATA FOR QUEEN
# ===================
# CHECK VALIDITY OF EXPERIMENTAL DATA
def qn_checkdata(queen,xplr,dataset,iterate=0,errorfunc=error):
  project = queen.project
  # READ DATA
  data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
  # COMBINE ALL DATA, WE ALSO CHECK THE BACKGROUND INFORMATION!
  restraints = data["data"] + data["bckg"]
  # INITIALIZE QUEEN CLASS FOR FULL AND INITIAL UNCERTAINTY
  if not iterate:
    unc = queen.uncertainty(xplr,restraints)
    if not queen.errorflag:
      print "Dataset '%s' runs through QUEEN without problems.\n"%dataset
    else:
      errorfunc("Dataset '%s'  seems to be problematic. Please check"%dataset)
  else:
    testlist = []
    print """\nQUEEN will now cycle all restraints in your dataset and add them
one by one. This should help you in identifying problematic restraints in
your dataset.\n"""
    for r in restraints:
      testlist.append(r)
      print "Adding restraint:\n%s"%r.format()
      score = queen.uncertainty(xplr,testlist)
      if queen.errorflag:
        errorfunc("Restraint seems to be problematic. Please check.")
    if not queen.errorflag:
      print "Dataset '%s' runs through QUEEN without problems."%dataset
    else:
      errorfunc("Dataset '%s'  seems to be problematic. Please check"%dataset)
  return queen.errorflag


# SET INFORMATION
# ===============
# CALCULATE THE INFORMATION CONTENT OF THE DIFFERENT
# RESTRAINT FILES IN A PROVIDED DATASET
def qn_setinformation(queen,xplr,dataset):
  print "Calculating set information content."
  if queen.numproc > 1: import pypar
  # STARTING TIME
  starttime = time.time()
  project = queen.project
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # SET THE OUTPUT FILE
  outputfile = os.path.join(queen.outputpath,'setinfo_%s.dat'%dataset)
  outlist = []
  # BUILD A DATA DICTIONARY
  rcount = 0
  datadict = {}
  for filedict in datasets:
    table = nmv_adjust(queen.table,filedict["FILE"])
    # READ THE RESTRAINT FILE
    r = restraint_file(table,'r',type=filedict["TYPE"])
    r.read()
    rcount += len(r.restraintlist)
    # STORE THE PARSED RESTRAINTS
    filedict["DATA"] = r.restraintlist
    datadict[r.type] = datadict.get(r.type,[]) + r.restraintlist
  # TAKE ALL PERMUTATIONS OF LIST
  permutationlist = list_permutations(range(len(datasets)))
  # SET THE RANGE FOR MPI RUNS
  mylower,myupper = mpi_setrange(permutationlist,queen.myid,queen.numproc)
  # INITIALIZE PROGRESS BAR
  if queen.numproc == 1:
    # NUMBER OF CALCULATIONS FOR EACH PERMUTATION
    npermcalc = myupper*(len(permutationlist[0])-1)
    # TWO CALCULATIONS PER DATASET
    ndatacalc = len(datasets)*2
    # TWO REFERENCE CALCULATIONS
    nrefscalc = 2
    # START BAR
    print "Number of completed calculations:"
    prog = progress_indicator(nrefscalc+npermcalc+ndatacalc)
    prog.increment(0)
  # INITIALIZE QUEEN CLASS FOR FULL AND INITIAL UNCERTAINTY
  unc_all = queen.uncertainty(xplr,datadict)
  # SHOW PROGRESS
  if queen.numproc==1: prog.increment(1)
  unc_ini = queen.uncertainty(xplr,{})
  # SHOW PROGRESS
  if queen.numproc==1: prog.increment(2)
  # CALCULATE TOTAL INFORMATION
  inf_all = unc_ini - unc_all
  # STORAGE LISTS
  inflist, avlist = [],[]
  for i in range(len(datasets)):
    inflist.append([])
  # CYCLE THE PERMUTATIONS
  ncount = 2
  for i in range(mylower,myupper):
    setlist = permutationlist[i]
    unclist = [unc_ini]
    # CYCLE ALL SETS
    for j in range(len(setlist)):
      # SUBSET UNC
      unc_sub = unclist[j]
      # SET + SUBSET UNC
      setdict = {}
      for subset in setlist[:(j+1)]:
        setdict[datasets[subset]["TYPE"]] = setdict.get(datasets[subset]["TYPE"],[]) \
                                            + datasets[subset]["DATA"]
      # WE KNOW THE OUTCOME FOR THE LAST SET
      if j==len(setlist)-1: unc_set = unc_all
      # ELSE WE CALCULATE IT
      else:
        unc_set = queen.uncertainty(xplr,setdict)
        # INCREMENT BAR
        if queen.numproc == 1:
          ncount += 1
          prog.increment(ncount)
      unclist.append(unc_set)
      # SET INFO
      inf_set = unc_sub - unc_set
      # STORE THE INFO
      inflist[setlist[j]].append((inf_set/inf_all)*100)
  if queen.myid!=0:
    # SEND INFORMATION TO PROC 0
    pypar.send(inflist,0)
  else:
    # RECEIVE INFORMATION ON PROC 0
    for i in range(1,queen.numproc):
      reclist = pypar.receive(i)
      for j in range(len(reclist)):
        inflist[j] += reclist[j]
    # CALCULATE AVERAGES
    for list in inflist:
      avlist.append(avg_list(list)[0])
    # EVALUATE Iuni AND Ionly
    for i in range(len(datasets)):
      # SET AS THE LAST ONE: Iuni
      setdict = {}
      for j in range(len(datasets)):
        if i!=j:
          setdict[datasets[j]["TYPE"]] = setdict.get(datasets[j]["TYPE"],[]) \
                                         + datasets[j]["DATA"]
      unc_uni = queen.uncertainty(xplr,setdict)
      inf_uni = unc_uni - unc_all
      # INCREMENT BAR
      if queen.numproc == 1:
        prog.increment(nrefscalc+npermcalc+i*2+1)
      # SET AS THE ONLY ONE: Ionly
      setdict = {}
      for j in range(len(datasets)):
        if i==j:
          setdict[datasets[j]["TYPE"]] = setdict.get(datasets[j]["TYPE"],[]) \
                                         + datasets[j]["DATA"]
          setcount = len(datasets[j]["DATA"])
      unc_onl = queen.uncertainty(xplr,setdict)
      inf_onl = unc_ini - unc_onl
      # INCREMENT BAR
      if queen.numproc == 1: prog.increment(nrefscalc+npermcalc+i*2+2)
      # OUTPUT
      outlist.append("%7.3f\t%7.3f\t%7.3f\t%7.3f\t%s\n"%(avlist[i],
                                                         inf_uni/inf_all*100,
                                                         inf_onl/inf_all*100,
                                                         float(setcount)/rcount*100,
                                                         datasets[i]["NAME"]))
    # OUTPUT
    endtime = time.time()
    hours,minutes,seconds = log_passedtime(starttime,endtime)
    output = open(outputfile,'w')
    print "Output can be found in:\n%s"%outputfile
    output.write("# %3i hours, %3i minutes, %3i seconds\n"%(hours,minutes,seconds))
    output.write("Itotal       : %e bits/atom2\n"%inf_all)
    output.write("Hstructure|0 : %e bits/atom2\n"%unc_ini)
    output.write("Hstructure|R : %e bits/atom2\n"%unc_all)
    output.flush()
    output.write("\n%7s\t%7s\t%7s\t%7s\t%7s\n"%('Iave','Iuni','Ionly','count','setname'))
    output.write("%7s\t%7s\t%7s\t%7s\t\n"%('[%Itot]','[%Itot]','[%Itot]','[%R]'))
    for elem in outlist:
      output.write(elem)
    output.close()
  print "Done."

# PLOT UNCERTAINTY
# ================
# THIS SCRIPT GENERATE A PLOT WHICH DISPLAYS THE DECREASE IN UNCERTAINTY
# AS EXPERIMENTAL DATA IS ADDED TO THE SYSTEM.
def qn_plotuncertainty(queen,xplr,dataset):
  project = queen.project
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # READ DATASETS
  data = qn_readdatasets(queen,datasets)
  # CLEAN OUT THE DATASETS LIST, REMOVE THE BACKGROUND SETS
  nonbckg,bckg = [],[]
  for set in datasets:
    if set["INFO"]: nonbckg.append(set)
    else: bckg.append(set)
  datasets = nonbckg
  # SET THE OUTPUT FILE
  outputfile = os.path.join(queen.outputpath,'uncertainty_%s.dat'%dataset)
  xmgr = graceplot(outputfile,'xy','w')
  xmgr.xlab = "Number of restraints"
  xmgr.ylab = "H\sstructure\N (bits/atom\S2\N)"
  xmgr.writeheader()
  # KEEP A RESTRAINT COUNTER
  rcount = 0
  # DETERMINI INITIAL UNCERTAINTY: Istructure|0
  unc_ini = queen.uncertainty(xplr,data['bckg'])
  xmgr.write([rcount,unc_ini])
  # CYCLE THE DATAFILES
  memory = []
  for filedict in datasets:
    # GET THE RESTRAINTS
    restraintlist = data["sets"][filedict["FILE"]]
    rtype = filedict["TYPE"]
    # CYCLE THE RESTRAINTS
    for i in range(len(restraintlist)):
      rlist = copy.copy(data['bckg'])
      rlist += restraintlist[:i+1]
      # ADD PREVIOUS SETS
      rlist += memory
      unc = queen.uncertainty(xplr,rlist)
      xmgr.write([i+1+rcount,unc,str(restraintlist[i])])
    # KEEP SET IN MEMORY DICT
    memory += restraintlist
    # RAISE THE RESTRAINT COUNTER
    rcount += len(restraintlist)
  xmgr.close()

# CREATE INITIAL MATRIX
# =====================
# THIS SCRIPT GENERATES A DISTANCE MATRIX
# REPRESENTING Hstructure|0
def qn_hstructure0(queen,xplr):
  project = queen.project
  # SET THE OUTPUT FILE
  mtxfile = os.path.join(queen.outputpath,'Hstructure0.mtx')
  # GET MATRIX
  queen.getmatrix(xplr,mtxfile)


# GET UNI INFORMATION PER RESIDUE
# ===============================
# THIS SCRIPT RETURNS A DICTIONARY WITH THE AMOUNT OF
# UNIQUE INFORMATION PER RESIDUE
def qn_infuniperres(iunifile,restraintlist,pdbfile,pdbformat='xplor'):
  print "Calculating unique information per residue."
  # STORE INFORMATION PER RESIDUE
  ipr = {}
  # READ PDBFILE
  pdb = pdb_file.Structure(pdbfile)
  for chain in pdb.peptide_chains:
    if pdbformat=='xplor': cid = chain.segment_id
    if pdbformat=='pdb': cid = chain.chain_id
    ipr[cid]={}
    for residue in chain:
      ipr[cid][residue.number] = 0.0
  # READ Iuni
  uni = qn_readinffile(iunifile)
  # CYCLE THE RESTRAINTS
  ambiskipped = 0
  for r in restraintlist:
    # ONLY UNAMBIGUOUS DISTANCE DATA FOR NOW
    if r.type=='DIST' and not r.ambiguous:
      # CYCLE THE TWO CONTRIBUTIONS
      for i in range(2):
        # SEGID
        if len(r.data[i]["SEGI"])>0: cha_id = r.data[i]["SEGI"][0]
        else: cha_id = ''
        # RESID
        res_id = r.data[i]["RESI"][0]
        # STORE UNIQUE INFO
        ipr[cha_id][res_id] += uni[str(r)][0]/2
    else:
      if r.ambiguous: ambiskipped += 1
  print "%i Ambiguous restraints were skipped."%ambiskipped
  return ipr

# RESTRAINT INFORMATION: Iuni
# ===========================
# THIS SCRIPT CALCULATES THE INFORMATION CONTENT OF EACH OF THE
# INDIVIDUAL RESTRAINTS IN AN NMR DATASET WITH RESPECT TO THE REMAINDER
# OF THE DATASET
def qn_infuni(queen,xplr,dataset):
  print "Calculating unique restraint information."
  if queen.numproc > 1: import pypar
  # STARTING TIME
  starttime = time.time()
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # READ DATASETS
  data = qn_readdatasets(queen,datasets)
  # CALCULATE Istructure|0
  unc_ini = queen.uncertainty(xplr,[])
  # CALCULATE Istructure|R
  unc_all = queen.uncertainty(xplr,data['bckg']+data['data'])
  inf_all = unc_ini - unc_all
  # THE LIST IN WHICH ALL DATAPOINTS ARE JOINED
  loglist = []
  # GO THROUGH THE RESTRAINT AND DELETE THEM ONE BY ONE
  restraintlist = data["data"]
  # SET THE RANGE FOR MPI RUNS
  mylower,myupper = mpi_setrange(restraintlist,queen.myid,queen.numproc)
  # INITIALIZE PROGRESS BAR
  if queen.numproc == 1:
    print "Number of processed restraints:"
    prog = progress_indicator(myupper)
  # CALCULATED RESTRAINTINFO: Iuni
  for i in range(mylower,myupper):
    # PRINT PROGRESS
    if queen.numproc==1:
      prog.increment(i+1)
    # TAKE BACKGROUND
    rlist = copy.copy(data['bckg'])
    # DELETE RESTRAINT OF INTEREST
    tmplist = copy.copy(restraintlist)
    restraint = tmplist[i]
    del tmplist[i]
    rlist += tmplist
    # CALCULATE UNCERTAINTY
    unc = queen.uncertainty(xplr,rlist)
    # CALCULATE Iuni
    inf_uni = unc - unc_all
    loglist.append([i+1,inf_uni/inf_all*100,restraint])
  # COLLECT RESULTS ON MASTER CPU
  if queen.myid==0:
    for i in range(1,queen.numproc):
      loglist += pypar.receive(i)
    loglist.sort()
    print "Writing outputfiles."
    # WRITE TO LOGFILE
    outputfile = os.path.join(queen.outputpath,'Iuni_%s.dat'%dataset)
    print "Grace (Xmgr) input file:\n%s"%outputfile
    xmgr = graceplot(outputfile,'xy','w')
    xmgr.title = "Restraint information"
    xmgr.xlab = "Restraint index"
    xmgr.ylab = "I\suni\N/I\stotal\N (%)"
    xmgr.writeheader()
    xmgr.mwrite(loglist)
    # PASSED TIME
    endtime = time.time()
    h,m,s = log_passedtime(starttime,endtime)
    xmgr.comment("%3i procs - %4i h - %2i m - %2i s"%(queen.numproc,h,m,s))
    xmgr.close()
    # WRITE RESTRAINT TABLE SORTED ON Iuni
    outputfile = os.path.join(queen.outputpath,'Iuni_%s_sorted.tbl'%dataset)
    print "All restraints sorted by Iuni:\n%s"%outputfile
    # STORE RESTRAINTS IN DICT
    rdict = {}
    for el in loglist: rdict[el[2]]=el[1]
    # SORT DICT BY VALUE
    r_sorted = rdict.items()
    r_sorted.sort(lambda (k1,v1),(k2,v2): cmp(v2,v1))
    # OPEN AND WRITE TO OUTPUT FILE
    rfile = restraint_file(outputfile,'w')
    for el in r_sorted:
      rfile.comment("%10e %% unique information"%el[1])
      rfile.write(el[0])
    rfile.close()
    print "Done."
  # SEND RESULT ON OTHER CPUS
  else:
    pypar.send(loglist,0)

# RESTRAINT INFORMATION: Iave
# ===========================
# THIS SCRIPT CALCULATES THE AVERAGE INFORMATION CONTENT OF EACH OF THE
# INDIVIDUAL RESTRAINTS IN AN NMR DATASET
def qn_infave(queen,xplr,dataset,convcutoff=0.01):
  print "Calculating average restraint information."
  if queen.numproc > 1: import pypar
  # STARTING TIME
  starttime = time.time()
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # READ DATASETS
  data = qn_readdatasets(queen,datasets)
  # STORE RESTRAINTLIST
  restraintlist = data["data"]+data["bckg"]
  # SHUFFLE THE RESTRAINT LIST
  rlist = copy.copy(restraintlist)
  # CALCULATE INITIAL UNCERTAINTY
  unc_ini = queen.uncertainty(xplr,[])
  unc_all = queen.uncertainty(xplr,data["data"]+data["bckg"])
  inf_all = unc_ini - unc_all
  # DEFINE DICTIONARIESS
  inf_dict, con_dict, avg_dict = {}, {}, {}
  # INITIALIZE CONVERGENCE DICT
  for r in rlist:
    con_dict[str(r)]=0
  # FLAG THE BACKGROUND RESTRAINTS AS CONVERGED, SO THEY
  # WILL BE INCLUDED BUT NOT EVALUATED
  for r in data["bckg"]:
    con_dict[str(r)]=1
  # DETERMINE THE AVERAGE INFORMATION
  done,cycles,total,comparisons = 0,queen.numproc,0,0
  ttotal = 0
  loglist = []
  # MAXIMUM NUMBER OF CYCLES
  cyclescutoff = 1000
  # MINIMUM NUMBER OF AVERAGES TO CALC CONVERGENCE
  lenconvlist = 10
  # PLOTDICT
  plotdict = {}
  while not done and cycles<=cyclescutoff:
    skipped = 0
    # SHUFFE LIST
    random.shuffle(rlist)
    # CREATE CYCLED LIST
    slice = int(round(len(rlist)/5.0))
    lists = []
    for i in range(5):
      rlist = rlist[slice:] + rlist[:slice]
      lists.append(rlist)
    # DETERMINE INFO FOR THE FIVE LISTS
    for list in lists:
      # BACKGROUND UNCERTAINTY IS RESET TO EMPTY MATRIX
      unc_bg = unc_ini
      # RESET THE TESTLIST
      testlist = []
      for r in list:
        # CHECK IF THE RESTRAINT IS NOT YET CONVERGED
        if con_dict[str(r)] == 0:
          # ADD THE SKIPPED CONVERGED ONES
          if skipped:
            unc_bg = queen.uncertainty(xplr,testlist)
            comparisons+=queen.numproc
            skipped = 0
          # ADD TO THE TESTLIST
          testlist += [r]
          # CALCULATE INFO
          unc_r = queen.uncertainty(xplr,testlist)
          comparisons+=queen.numproc
          inf_r = unc_bg - unc_r
          # SET THE NEW BACKGROUND
          unc_bg = unc_r
          # STORE INFO
          inf_dict[str(r)] = inf_dict.get(str(r),[]) + [inf_r]
        # ELSE SKIP IT
        else:
          # ADD TO THE TESTLIST
          testlist += [r]
          # SET FLAG THAT WE SKIPPED RESTRAINTS
          skipped = 1
    # HANDLE ON MAIN CPU
    if queen.myid==0:
      # TRANSFER CALCULATED INFOS
      for i in range(queen.numproc):
        # HANDLE PROC 0
        if i==0:
          for key in inf_dict.keys():
            # CALCULATE AVERAGE OVER ALL SCORES
            ravg = avg_list(inf_dict[key])
            # ADD TO AVG DICT
            avg_dict[key] = avg_dict.get(key,[]) + [ravg[0]]
        # HANDLE PROC 1 TO queen.numproc
        else:
          recdict = pypar.receive(i)
          for key in recdict.keys():
            inf_dict[key]+=recdict[key]
            # CALCULATE AVERAGE OVER ALL SCORES
            ravg = avg_list(inf_dict[key])
            # ADD TO AVG DICT
            avg_dict[key] = avg_dict.get(key,[]) + [ravg[0]]
      # WRAP UP
      for r in rlist:
        # IF NOT CONVERGED
        if con_dict[str(r)]==0:
          converged = 0
          # CALC GENERAL AVERAGES
          ravg = avg_list(inf_dict[str(r)])
          aavg = avg_list(avg_dict[str(r)])
          # CHECK AVERAGE
          clen = len(avg_dict[str(r)])
          slice = lenconvlist
          cavg = avg_list(avg_dict[str(r)][-slice:])
          # CHECK CONVERGENCE
          if (cavg[1] <= convcutoff*cavg[0] and clen>lenconvlist) \
                 or cycles+queen.numproc>cyclescutoff:
            converged = 1
          # PLOT DICT
          plotdict[str(r)]=plotdict.get(str(r),[])+[cavg]
          # CALCULATE SOME PERCENTAGES FOR HUMAN EVALUATION....
          if aavg[0]!=0.0: paavg = int((aavg[1]/aavg[0])*100)
          else: paavg = 0.0
          if cavg[0]!=0.0: pcavg = int((cavg[1]/cavg[0])*100)
          else: pcavg = 0.0
          # IF A RESTRAINT CONVERGES
          if converged:
            # SET CONVERGENCE FLAG
            con_dict[str(r)]=1
            # GET THE OLDPOSITION
            oldpos = restraintlist.index(r)
            # ADD TO THE LOGFILE LIST
            loglist.append([oldpos+1,cavg[0]/inf_all*100,ravg[1]/inf_all*100, \
                            r,cycles])

            total += (aavg[0]/inf_all)*100
      # CHECK IF WE ARE DONE
      done = 1
      converged = 0
      for key in con_dict.keys():
        if con_dict[key]==0: done = 0
        else: converged+=1
      print "Cycle %4i, %4i of %4i converged.\r"%(cycles,
                                                  converged-len(data["bckg"]),
                                                  len(rlist)-len(data["bckg"])),
      sys.stdout.flush()
    # SEND CONVERGENCE INFO
    else:
      pypar.send(inf_dict,0)
      inf_dict = {}
    # COMMUNICATE DONE AND CONVERGENCE DICTIONARY
    if queen.myid==0:
      for i in range(1,queen.numproc):
        pypar.send([done,con_dict],i)
    else:
      [done,con_dict]=pypar.receive(0)
    # INCREASE CYCLES
    cycles+=queen.numproc
  # WRITE LOGFILE ON MAIN CPU
  if queen.myid==0:
    # SET THE OUTPUT FILE
    outputfile = os.path.join(queen.outputpath,'Iave_%s.dat'%dataset)
    print "\nGrace (Xmgr) input file:\n%s"%outputfile
    xmgr = graceplot(outputfile,'xydy','w')
    xmgr.title = "Average restraint information"
    xmgr.xlab = "Restraint index."
    xmgr.ylab = "I\save\N/I\stotal\N (%)"
    xmgr.writeheader()
    loglist.sort()
    for log in loglist:
      xmgr.comment("Convergence after %i cycles."%log[-1])
      del log[-1]
      xmgr.write(log)
    xmgr.comment("%4.1f %% - %7.5f - %4i comparisons - %.2f comp per restraint"%(total,convcutoff,comparisons*queen.numproc,float(comparisons*queen.numproc)/len(rlist)))
    # PASSED TIME
    endtime = time.time()
    h,m,s = log_passedtime(starttime,endtime)
    xmgr.comment("%3i procs - %4i h - %2i m - %2i s"%(queen.numproc,h,m,s))
    xmgr.close()
    # WRITE RESTRAINT TABLE SORTED ON Iuni
    outputfile = os.path.join(queen.outputpath,'Iave_%s_sorted.tbl'%dataset)
    print "All restraints sorted by Iave:\n%s"%outputfile
    # STORE RESTRAINTS IN DICT
    rdict = {}
    for el in loglist: rdict[el[-1]]=el[1]
    # SORT DICT BY VALUE
    r_sorted = rdict.items()
    r_sorted.sort(lambda (k1,v1),(k2,v2): cmp(v2,v1))
    # OPEN AND WRITE TO OUTPUT FILE
    rfile = restraint_file(outputfile,'w')
    for el in r_sorted:
      rfile.comment("%10e %% average information"%el[1])
      rfile.write(el[0])
    rfile.close()
  if queen.numproc>1: pypar.Barrier()
  print "Done."

# RESTRAINT INFORMATION: Iavef
# ============================
# THIS SCRIPT CALCULATES THE AVERAGE INFORMATION CONTENT OF EACH OF THE
# INDIVIDUAL RESTRAINTS IN AN NMR DATASET IN A SOMEWHAT FASTER (BUT
# POSSIBLY LESS ACCURATE...) WAY
def qn_infave_fast(queen,xplr,dataset,ncycles=25):
  print "Calculating average restraint information."
  if queen.numproc > 1: import pypar
  # STARTING TIME
  starttime = time.time()
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # READ DATASETS
  data = qn_readdatasets(queen,datasets)
  # STORE RESTRAINTLIST
  restraintlist = data["data"]+data["bckg"]
  # COPY THE RESTRAINT LIST
  rlist = copy.copy(restraintlist)
  # CALCULATE INITIAL UNCERTAINTY
  unc_ini = queen.uncertainty(xplr,[])
  unc_all = queen.uncertainty(xplr,data["bckg"]+data["data"])
  inf_all = unc_ini - unc_all
  # DEFINE DICTIONARIESS
  inf_dict, avg_dict,con_dict = {}, {}, {}
  # INITIALIZE CONVERGENCE DICT
  for r in data["data"]:
    con_dict[str(r)]=0
  # FLAG THE BACKGROUND RESTRAINTS AS CONVERGED, SO THE WILL BE
  # INCLUDED BUT NOT EVALUATED
  for r in data["bckg"]:
    con_dict[str(r)]=1
  # DETERMINE THE AVERAGE INFORMATION
  done,cycles,total,comparisons = 0,0,0,0
  loglist = []
  # PLOTDICT
  plotdict = {}
  while cycles < ncycles:
    if queen.myid==0:
      print "Starting cycles: %i to %i of %i"%(cycles+1,cycles+queen.numproc,ncycles)
    sys.stdout.flush()
    # SHUFFE LIST
    random.shuffle(rlist)
    # CREATE FIVE CYCLED LISTS
    slice = int(round(len(rlist)/5.0))
    lists = []
    for i in range(5):
      rlist = rlist[slice:] + rlist[:slice]
      lists.append(rlist)
    # DETERMINE INFO FOR THE FIVE LISTS
    for list in lists:
      # RESET THE RESTRAINT DICTIONARY
      testlist = []
      # BACKGROUND UNCERTAINTY IS RESET TO EMPTY MATRIX + BACKGROUND
      unc_bg = unc_ini
      for r in list:
        # ADD TO THE TESTLIST
        testlist += [r]
        # CALCULATE INFO
        unc_r = queen.uncertainty(xplr,testlist)
        comparisons+=queen.numproc
        inf_r = unc_bg - unc_r
        # SET THE NEW BACKGROUND
        unc_bg = unc_r
        # STORE INFO
        inf_dict[str(r)] = inf_dict.get(str(r),[]) + [inf_r]
    # HANDLE ON MAIN CPU
    if queen.myid==0:
      # TRANSFER CALCULATED INFOS
      for i in range(queen.numproc):
        # HANDLE PROC 0
        if i==0:
          for key in inf_dict.keys():
            # CALCULATE AVERAGE OVER ALL SCORES
            ravg = avg_list(inf_dict[key])
            # ADD TO AVG DICT
            avg_dict[key] = avg_dict.get(key,[]) + [ravg[0]]
        # HANDLE PROC 1 TO queen.numproc
        else:
          recdict = pypar.receive(i)
          for key in recdict.keys():
            inf_dict[key]+=recdict[key]
            # CALCULATE AVERAGE OVER ALL SCORES
            ravg = avg_list(inf_dict[key])
            # ADD TO AVG DICT
            avg_dict[key] = avg_dict.get(key,[]) + [ravg[0]]
      # WRAP UP
      if cycles+queen.numproc >= ncycles:
        for r in rlist:
          # CALC GENERAL AVERAGES
          ravg = avg_list(inf_dict[str(r)])
          aavg = avg_list(avg_dict[str(r)])
          # GET THE OLDPOSITION
          oldpos = restraintlist.index(r)
          # ADD TO THE LOGFILE LIST
          loglist.append([oldpos+1,ravg[0]/inf_all*100,ravg[1]/inf_all*100, \
                          r,cycles])
#                         "%s"%str(r),cycles])
          total += (ravg[0]/inf_all)*100
    # SEND CONVERGENCE INFO
    else:
      pypar.send(inf_dict,0)
      inf_dict = {}
    # INCREASE CYCLES
    cycles+=queen.numproc
  # WRITE LOGFILE ON MAIN CPU
  if queen.myid==0:
    # SET THE OUTPUT FILE
    outputfile = os.path.join(queen.outputpath,'Iavef_%s.dat'%dataset)
    print "\nGrace (Xmgr) input file:\n%s"%outputfile
    xmgr = graceplot(outputfile,'xydy','w')
    xmgr.title = "Average restraint information"
    xmgr.xlab = "Restraint index."
    xmgr.ylab = "I\save\N/I\stotal\N (%)"
    xmgr.writeheader()
    loglist.sort()
    for log in loglist:
      del log[-1]
      xmgr.write(log)
    # PASSED TIME
    endtime = time.time()
    h,m,s = log_passedtime(starttime,endtime)
    xmgr.comment("%.1f %% - %3i procs - %4i h - %2i m - %2i s"%(total,queen.numproc,h,m,s))
    xmgr.close()
    # WRITE RESTRAINT TABLE SORTED ON Iuni
    outputfile = os.path.join(queen.outputpath,'Iavef_%s_sorted.tbl'%dataset)
    print "All restraints sorted by Iave:\n%s"%outputfile
    # STORE RESTRAINTS IN DICT
    rdict = {}
    for el in loglist: rdict[el[-1]]=el[1]
    # SORT DICT BY VALUE
    r_sorted = rdict.items()
    r_sorted.sort(lambda (k1,v1),(k2,v2): cmp(v2,v1))
    # OPEN AND WRITE TO OUTPUT FILE
    rfile = restraint_file(outputfile,'w')
    for el in r_sorted:
      rfile.comment("%10e %% average information"%el[1])
      rfile.write(el[0])
    rfile.close()
  pypar.Barrier()
  print "Done."

# COMBINE Iave AND Iuni
# =====================
# THIS SCRIPT COMBINES THE AVERAGE AND UNIQUE RESTRAINT
# INFORMATION IN ONE PLOT
def qn_avevsuni(queen,xplr,dataset):
  print "Combining Iave and Iuni information."
  comments = ['#','@','&']
  # CHECK IF AVERAGE AND UNIQUE INFORMATION ARE CALCULATED
  unifile = os.path.join(queen.outputpath,'Iuni_%s.dat'%dataset)
  if not os.path.exists(unifile):
    error("Your Iuni file does not seem to present")
  avefile = os.path.join(queen.outputpath,'Iave_%s.dat'%dataset)
  if not os.path.exists(avefile):
    error("Your Iave file does not seem to present")
  # SET THE OUTPUT FILE
  outputfile = os.path.join(queen.outputpath,'IaveIuni_%s.dat'%dataset)
  print "Output can be found in:\n%s"%outputfile
  xmgr = graceplot(outputfile,'xy','w')
  xmgr.ylab = "I\save\N/I\stotal\N (%)"
  xmgr.xlab = "I\suni\N/I\stotal\N (%)"
  xmgr.square = 1
  xmgr.writeheader()
  # READ AND CLEAN FILES
  ufile = open(unifile,'r').readlines()
  ulist = []
  for line in ufile:
    try:
      if line[0] not in comments:
        ulist.append(line)
    except IndexError:
      pass
  afile = open(avefile,'r').readlines()
  alist = []
  for line in afile:
    try:
      if line[0] not in comments:
        alist.append(line)
    except IndexError:
      pass
  if len(ulist)!=len(alist): error("Files seem to be different")
  # BUILD THE OUTPUT FILE
  for i in range(len(ulist)):
    uline = string.split(ulist[i])
    uscore = float(uline[1])
    ustr = uline[2][1:-1]
    aline = string.split(alist[i])
    ascore = float(aline[1])
    astr = aline[3][1:-1]
    if ustr==astr:
      xmgr.write([uscore,ascore,astr])
    else: error("Files seem to be different")
  xmgr.close()
  print "Done."


# SORT RESTRAINTS BASED ON Iave AND Iuni
# ======================================
# THIS SCRIPT SORTS RESTRAINTS BASED ON Iave AND
# Iuni AND WRITES THEM TO AN OUTPUT FILE
def qn_sorttbl(queen,xplr,dataset):
  print "Sorting restraint file based on Iave and Iuni."
  unifile = os.path.join(queen.outputpath,'Iuni_%s.dat'%dataset)
  if not os.path.exists(unifile):
    error("Your Iuni file does not seem to present")
  avefile = os.path.join(queen.outputpath,'Iave_%s.dat'%dataset)
  if not os.path.exists(avefile):
    error("Your Iave file does not seem to present")
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # CYCLE THE AVAILABE SETS
  datadict = {}
  rlist = []
  for filedict in datasets:
    table = nmv_adjust(queen.table,filedict["FILE"])
    # READ THE RESTRAINT FILE
    r = restraint_file(table,'r',type=filedict["TYPE"])
    r.read()
    # STORED RESTRAINTS FOR FUTURE USE
    rlist += r.restraintlist
    datadict[r.type] = datadict.get(r.type,[]) + r.restraintlist
  # WE ONLY LOOK AT THE DISTANCE RESTRAINTS IN THIS STAGE
  rdict = {}
  for r in rlist:
    rdict[str(r)]=r
  # SET THE OUTPUT FILES
  outputtbl = os.path.join(queen.outputpath,'IaveIuni_%s.tbl'%dataset)
  print "Output can be found in:\n%s"%outputtbl
  che_r = restraint_file(outputtbl,'w')
  outputtbl = os.path.join(queen.outputpath,'Iave_%s.tbl'%dataset)
  print "Output can be found in:\n%s"%outputtbl
  avg_r = restraint_file(outputtbl,'w')
  udict,adict,cdict={},{},{}
  sumdict = {}
  # READ AND CLEAN FILES
  comments = ['#','@','&']
  # UNIQUE
  umax = 0
  ufile = open(unifile,'r').readlines()
  for line in ufile:
    try:
      if line[0] not in comments:
        line=line.split()
        key = float(line[1])
        val = line[-1][1:-1]
        udict[key]=udict.get(key,[])+[val]
        umax = max(umax,key)
    except IndexError:
      pass
  # AVERAGE
  amax = 0
  afile = open(avefile,'r').readlines()
  for line in afile:
    try:
      if line[0] not in comments:
        line=line.split()
        key = float(line[1])
        val = line[-1][1:-1]
        adict[key]=adict.get(key,[])+[val]
        amax = max(amax,key)
    except IndexError:
      pass
  # WRITE SORTED UNIQUE
  ukeylist = udict.keys()
  ukeylist.sort()
  ukeylist.reverse()
  for key in ukeylist:
    for rstr in udict[key]:
      sumdict[rstr]=sumdict.get(rstr,0)+key/umax
      #uni_r.comment("%e %% unique information"%key)
      #uni_r.write(rdict[rstr])
  #uni_r.close()
  # WRITE SORTED AVERAGE
  akeylist = adict.keys()
  akeylist.sort()
  akeylist.reverse()
  for key in akeylist:
    for rstr in adict[key]:
      sumdict[rstr]=sumdict.get(rstr,0)+key/amax
      avg_r.comment("%e %% average information"%key)
      avg_r.write(rdict[rstr])
  avg_r.close()
  # WRITE CHECKWORTHY LIST
  ch = sumdict.items()
  ch.sort(lambda (k1,v1),(k2,v2): cmp(v2,v1) ) # sort by value, not by key
  for element in ch:
    che_r.comment("%e"%element[1])
    che_r.write(rdict[element[0]])
  che_r.close()
  print "Done."

# BUILD INFO SORTED DATASET
# =========================
# SORT DATASET SUCH THAT THE MOST INFORMATIVE RESTRAINTS COME FIRST
def qn_infsort(queen,xplr,dataset):
  if queen.numproc > 1: import pypar
  if queen.myid==0:
    print "Calculating information sorted dataset"
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # SET OUTPUT TABLE
  sorttbl = os.path.join(queen.outputpath,'Isorted_%s.tbl'%dataset)
  # CYCLE THE AVAILABE SETS
  rlist = []
  for filedict in datasets:
    if filedict["TYPE"]=='DIST':
      table = nmv_adjust(queen.table,filedict["FILE"])
      # READ THE RESTRAINT FILE
      r = restraint_file(table,'r',type=filedict["TYPE"])
      r.read()
      # ADD ALL RESTRAINTS TO THE RESTRAINT LIST
      rlist += r.restraintlist
  # CALCULATE INITIAL UNCERTAINTY
  iniunc = queen.uncertainty(xplr,[])
  fulunc = queen.uncertainty(xplr,rlist)
  # READ IN THE WORK THAT HAS ALREADY BEEN DONE
  if os.path.exists(sorttbl):
    rin = restraint_file(sorttbl,'r',type=filedict["TYPE"])
    rin.read()
    rsorted = rin.restraintlist
    # CHECK IF THERE IS STILL WORK LEFT TO DO
    if len(rsorted)==len(rlist):
      if queen.myid==0:
        print "Information file already exists for this dataset."
        print "Done."
      return
    else:
      rsorted = rin.restraintlist
      isorted = []
      if queen.myid==0:
        print "Information file found."
        print "%i of %i restraints already done."%(len(rsorted),len(rlist))
        print "Reconstructing information..."
      # RECONSTRUCT THE INFORMATION LIST
      for i in range(len(rsorted)):
        # CALCULATE INFO
        unc = queen.uncertainty(xplr,rsorted[:i+1])
        info = iniunc-unc
        isorted.append(info)
      # BUILD CURRENT RLIST
      tlist = []
      for elem in rlist:
        if elem not in rsorted:
          tlist.append(elem)
      rlist = tlist
  else:
    rsorted,isorted = [],[]
  # CYCLE THE RESTRAINTS
  while len(rlist)>0:
    info = 0
    # SET AND SHUFFLE THE RANGE LIST
    if queen.myid==0:
      # SET THE TESTRANGE
      random.shuffle(rlist)
      # DISTRIBUTE THE LIST OVER THE NODES
      for m in range(1,queen.numproc):
        pypar.send(rlist,m)
    else:
      # RECEIVE THE LIST
      rlist=pypar.receive(0)
    # SET THE PER PROCESSOR RANGE FOR MPI RUNS
    mylower,myupper=mpi_setrange(rlist,queen.myid,queen.numproc)
    print "Submitted %i restraints to %i CPU(s).\r"%(len(rlist),queen.numproc),
    sys.stdout.flush()
    # FIND THE HIGHEST INFO
    for i in range(mylower,myupper):
      # TAKE THE CURRENTLY SORTED ONES
      tlist = copy.copy(rsorted)
      # ADD THE TEST RESTRAINT
      tlist.append(rlist[i])
      # CALCULATE INFO
      tunc = queen.uncertainty(xplr,tlist)
      tinfo = iniunc-tunc
      if tinfo>info:
        info = tinfo
        sdict = {}
        sdict[i]=info
    # COLLECT RESULTS ON MASTER AND DETERMINE THE HIGHEST SCORING RESTRAINT
    if queen.myid==0:
      for i in range(1,queen.numproc):
        sdict.update(pypar.receive(i))
      finfo, fi = 0,0
      for key in sdict.keys():
        if sdict[key]>finfo:
          finfo=sdict[key]
          fi=key
    # SEND RESULTS ON OTHER CPUS
    else: pypar.send(sdict,0)
    # COMMUNICATE THE HIGHEST SCORING ID TO THE OTHER CPUS
    if queen.myid==0:
      for i in range(1,queen.numproc):
        pypar.send(fi,i)
    else: fi = pypar.receive(0)
    # ON ALL CPUS WE ADD THE HIGHEST SCORER TO THE LIST OF NEW NOES!
    rsorted.append(rlist[fi])
    if queen.myid==0: isorted.append(finfo)
    # DELETE THE RESTRAINT FROM THE OLD LIST
    del rlist[fi]
    # WRITE CURRENT SORTED LIST:
    if queen.myid==0:
      rfile = restraint_file(sorttbl,'w')
      for i in range(len(rsorted)):
        rfile.write(rsorted[i])
        rfile.comment("%6.2f %% of information transferred"%((float(isorted[i])/(iniunc-fulunc))*100))
      rfile.close()
  if queen.myid==0: print "\nDone."


# BUILD NR DATASET
# ================
# THIS SCRIPT CONSTRUCTS A NON-REDUNDANT VERSION
# OF THE PROVIDED DATASET
def qn_nrdataset(queen,xplr,dataset):
  # STARTING TIME
  starttime = time.time()
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # CYCLE THE AVAILABE SETS
  restraintlist = []
  memdict = {}
  for filedict in datasets:
    table = nmv_adjust(queen.table,filedict["FILE"])
    # READ THE RESTRAINT FILE
    r = restraint_file(table,'r',type=filedict["TYPE"])
    r.read()
    # ADD ALL RESTRAINTS TO THE RESTRAINT LIST
    restraintlist += r.restraintlist
    for r in r.restraintlist:
      memdict[str(r)]=filedict["FILE"]
    # REMOVE RESULTS FROM PREVIOUS RUNS
    outputtbl = os.path.join(queen.outputpath,'nr_%s.tbl'%filedict["FILE"])
    if os.path.exists(outputtbl): os.remove(outputtbl)
    outputtbl = os.path.join(queen.outputpath,'nr_%s.tbl.redundant'%filedict["FILE"])
    if os.path.exists(outputtbl): os.remove(outputtbl)
  # SHUFFLE THE LIST
  random.shuffle(restraintlist)
  # CALCULATE BACKGROUND
  rdict,redundict = {},{}
  unc_bg = queen.uncertainty(xplr,rdict)
  # CYCLE THE RESTRAINTS
  for r in restraintlist:
    tdict = copy.copy(rdict)
    # CALCULATE BG + RESTRAINT
    tdict[r.type]=tdict.get(r.type,[])+[r]
    unc_re = queen.uncertainty(xplr,tdict)
    # RESTRAINT INFORMATION
    inf_re = unc_bg - unc_re
    if inf_re > 0.0:
      rdict[r.type]=rdict.get(r.type,[])+[r]
    else:
      redundict[r.type]=redundict.get(r.type,[])+[r]
    unc_bg = unc_re
  # WRITE THE NON-REDUNDANT RESTRAINT FILES
  endtime = time.time()
  hours,minutes,seconds = log_passedtime(starttime,endtime)
  for key in rdict.keys():
    for r in rdict[key]:
      outputtbl = os.path.join(queen.outputpath,'nr_%s.tbl'%(memdict[str(r)]))
      if not os.path.exists(outputtbl):
        rfile = restraint_file(outputtbl,'w',key).close()
      rfile = restraint_file(outputtbl,'a',key)
      rfile.write(r)
      rfile.close()
  # WRITE THE REDUNDANT RESTRAINT FILES
  for key in redundict.keys():
    for r in redundict[key]:
      outputtbl = os.path.join(queen.outputpath,'nr_%s.tbl.redundant'%(memdict[str(r)]))
      if not os.path.exists(outputtbl):
        rfile = restraint_file(outputtbl,'w',key).close()
      rfile = restraint_file(outputtbl,'a',key)
      rfile.write(r)
      rfile.close()

#  ======================================================================
#    N M V   F U N C T I O N   G R O U P
#  ======================================================================

# NMV ADJUST
# ==========
# REPLACES THE ???? IN THE NMVCONF VALUE WITH THE PROVIDED STRING
def nmv_adjust(nmvconfkey,value):
  return string.replace(nmvconfkey,'????',value)

# CHECK PYTHON VERSION
# ====================
# CHECK PYTHON VERSION
def nmv_checkpython():
  version = float(sys.version[0])
  if version < 2.0:
    error('Python version 2.0 or higher required')
  return float(sys.version.split()[0][:3])
#  ======================================================================
#    N M R   F U N C T I O N   G R O U P
#  ======================================================================

# CALCULATE DISTANCE
# ==================
# FUNCTION CALCULATES THE DISTANCE BETWEEN
# TO SETS OF COORDINATES
def nmr_distance(atomcoord1,atomcoord2):
  distance = math.sqrt((atomcoord1[0]-atomcoord2[0])**2+(atomcoord1[1]-atomcoord2[1])**2+(atomcoord1[2]-atomcoord2[2])**2)
  return distance

# AVERAGE COORDINATES
# ===================
# FUNCTION CALCULATES AN AVERAGE COORDINATE GIVEN
# A LIST OF 3D COORDINATES
def nmr_averagecoordinates(coordinatelist):
  average_coord = [[],[],[]]
  # GO TRHOUGH X,Y AND Z
  for i in range(3):
    sum = 0.0
    # GO TROUGH THE COORDINATES IN THE LIST
    for coord in coordinatelist:
      sum += coord[i]
    # CALCULATE THE AVERAGE
    average_coord[i]=sum/len(coordinatelist)
  return average_coord

# AVERAGE DISTANCE
# ================
# FUNCTION AVERAGES THE DISTANCE BETWEEN TO (GROUPS OF) ATOMS
# DIFFERENT TYPE OF AVERAGING CAN BE USED:
# 'R-6' : R = (<Rij-6>)-1/6
# 'R-3' : R = (<Rij-3>)-1/3
# 'SUM' : R = ((Sigma Rij-6)/monomers)-1/6
# 'CENT': R = (Ricenter - Rjcenter)
# PROVIDE TWO LISTS OF COORDINATES, EACH CONTAINING THE
# COORDINATES FOR THE ATOMS IN THE GROUP
def nmr_averagedistance(coord0,coord1,averaging):
  monomers = 1
  # CALCULATE THE NECESSARY SUMS
  sum = 0.0
  combinations = len(coord0)*len(coord1)
  for i in range(len(coord0)):
    for j in range(len(coord1)):
      if averaging == 'SUM':
        sum += pow(nmr_distance(coord0[i],coord1[j]),-6)
      elif averaging == 'R-6':
        sum += pow(nmr_distance(coord0[i],coord1[j]),-6)
      elif averaging == 'R-3':
        sum += pow(nmr_distance(coord0[i],coord1[j]),-3)
  #print len(coord0), len(coord1), sum, combinations
  if averaging == 'CENT':
    # CALCULATE GROUP CENTERS
    cent0 = nmr_averagecoordinates(coord0)
    cent1 = nmr_averagecoordinates(coord1)
  # CALCULATE THE FINAL DISTANCE
  if averaging == 'SUM':
    distance = pow(sum/monomers,float(-1)/6)
  elif averaging == 'R-6':
    distance = pow(sum/combinations,float(-1)/6)
  elif averaging == 'R-3':
    distance = pow(sum/combinations,float(-1)/3)
  elif averaging == 'CENT':
    distance = nmr_distance(cent0,cent1)
  return distance

#  ======================================================================
#    N M R   R E S T R A I N T S   F U N C T I O N   G R O U P
#  ======================================================================

# GROUP DISTANCE RESTRAINTS
# =========================
# FUNCTION TAKES A DISTANCE RESTRAINT FILE AND GROUP IT INTO
# IR, SQ, MR AND LR RESTRAINTS
def rfile_group(intbl,format="XPLOR"):
  # READ THE INPUT FILE
  r = restraint_file(intbl,'r',type="DIST",format=format)
  r.read()
  # GROUP RESTRAINTS
  group = r_group(r.restraintlist)
  irl,sql,mrl,lrl = [],[],[],[]
  if group.has_key('IR'): irl = group['IR']
  if group.has_key('SQ'): sql = group['SQ']
  if group.has_key('MR'): mrl = group['MR']
  if group.has_key('LR'): lrl = group['LR']
  # LOCATE THE EXTENSION
  dotpos = intbl.rfind('.')
  filelist = []
  # CREATE OUTPUT FILES
  if len(irl)>0:
    tbl = "%s_%s.%s"%(intbl[:dotpos],"IR",intbl[dotpos+1:])
    ir = restraint_file(tbl,'w',type="DIST",format=format)
    ir.mwrite(irl)
    filelist.append(tbl)
  if len(sql)>0:
    tbl = "%s_%s.%s"%(intbl[:dotpos],"SQ",intbl[dotpos+1:])
    sq = restraint_file(tbl,'w',type="DIST",format=format)
    sq.mwrite(sql)
    filelist.append(tbl)
  if len(mrl)>0:
    tbl = "%s_%s.%s"%(intbl[:dotpos],"MR",intbl[dotpos+1:])
    mr = restraint_file(tbl,'w',type="DIST",format=format)
    mr.mwrite(mrl)
    filelist.append(tbl)
  if len(lrl)>0:
    tbl = "%s_%s.%s"%(intbl[:dotpos],"LR",intbl[dotpos+1:])
    lr = restraint_file(tbl,'w',type="DIST",format=format)
    lr.mwrite(lrl)
    filelist.append(tbl)
  return [filelist,len(irl),len(sql),len(mrl),len(lrl)]


# CHECK DISTANCE RESTRAINTS
# =========================
# FUNCTION TAKES A DISTANCE RESTRAINT FILE AND CHECKS
# IT CONTENT OPTIONALLY THE CLEAN RESTRAINT ARE WRITTEN
# TO AN OUTPUT FILE
def rfile_check(intbl,outtbl=None,type='DIST',informat="XPLOR",outformat="XPLOR"):
  # READ RESTRAINT FILE
  rin = restraint_file(intbl,'r',type,format=informat)
  # READ THE INPUT
  rin.read()
  rin.clean()
  # WRITE TO OUTPUT
  if outtbl:
    rout = restraint_file(outtbl,'w',type,format=outformat)
    rout.mwrite(rin.restraintlist)
    if len(rin.doubles)>0 or len(rin.rejected)>0:
      rrej = restraint_file("%s.rejected"%outtbl,'w',type,format=outformat)
      if len(rin.doubles)>0:
        rrej.comment("Rejected double restraints")
        rrej.mwrite(rin.doubles)
      if len(rin.rejected)>0:
        rrej.comment("Rejected other restraints")
        rrej.mwrite(rin.rejected)
  return len(rin.restraintlist),len(rin.doubles),len(rin.rejected)


# ADJUST DISTANCE RESTRAINTS
# ==========================
# FUNCTION TAKES A DISTANCE RESTRAINT FILE AND ADJUSTS
# THE DISTANCES TO THE PROVIDED PDBFILE
def rfile_adjust(intbl,outtbl,pdbfile,precision=None,
                 format='XPLOR',averaging='SUM'):
  # READ RESTRAINT FILE
  rf = restraint_file(intbl,'r',format=format)
  rf.read()
  # READ PDBFILE
  pdb = pdb_file.Structure(pdbfile)
  # CYCLE THE RESTRAINT FILE
  adjusted = r_adjust(rf.restraintlist,pdb,averaging,precision)
  # WRITE OUTPUT
  r = restraint_file(outtbl,'w',format=format)
  r.mwrite(adjusted)

# VISUALIZE DISTANCE RESTRAINTS
# =============================
# FUNCTION TAKES A DISTANCE RESTRAINT FILE AND
# SHOWS THEM IN THE PROVIDED PDBFILE
def rfile_visualize(intbl,pdbfile,yaspath,cutoff=10000,type='DIST',format='XPLOR'):
  # READ THE RESTRAINTS
  r = restraint_file(intbl,'r',format=format)
  r.read()
  restraints = r.restraintlist
  #  READ THE PDB FILE
  pdb = pdb_file.Structure(pdbfile)
  # INITIALIZE YASARE
  macro=ysr_macro(yaspath,errorfunc=error)
  macro.write(["LoadPDB %s"%pdbfile,
               "Style Stick",
               "Console Off"])
  # TAKE ALL RESTRAINTS
  count = 1
  for restraint in restraints[:cutoff]:
    # TAKE ALL ATOM COMBOS
    for k in range(len(restraint.data[0]["RESI"])):
      for l in range(len(restraint.data[1]["RESI"])):
        atomk = restraint.data[0]['NAME'][k]
        atoml = restraint.data[1]['NAME'][l]
        kindex = pdb_resindex(pdb,restraint.data[0]['RESI'][k])
        lindex = pdb_resindex(pdb,restraint.data[1]['RESI'][l])
        resk = pdb.residues[kindex].name
        resl = pdb.residues[lindex].name
        klist = nmcl_pseudoatoms(atomk,resk)
        llist = nmcl_pseudoatoms(atoml,resl)
        for m in klist[:1]:
          for n in llist[:1]:
            serialk = pdb[kindex][m]['serial_number']
            seriall = pdb[lindex][n]['serial_number']
            macro.write("ShowArrow Start=AtAtom,%i,End=AtAtom,%i,Radius=0.1,Heads=0,Color=Yellow"%(serialk,seriall))
        count+=1
  macro.write("Stop")
  macro.submit()

# VISUALIZE DISTANCE RESTRAINTS
# =============================
# FUNCTION TAKES A DISTANCE RESTRAINT FILE AND
# SHOWS THEM IN THE PROVIDED PDBFILE
def rfile_pic(intbl,pdbfile,yaspath,cutoff=10000,type='DIST',format='XPLOR'):
  path = os.path.basename(pdbfile)[:-4]
  # READ THE RESTRAINTS
  r = restraint_file(intbl,'r',format=format)
  r.read()
  restraints = r.restraintlist
  macro=ysr_macro(yaspath,errorfunc=error)
##  macro.write(["ErrorExit On",
##               #"Screensize 800,800",
##               "LoadPDB %s"%pdbfile,
##               "DelObj !1",
##               #"ZoomObj 1,0",
##               "CleanAll",
##               "SavePDB 1, %s.xplor,Format=Xplor"%pdbfile,
##               "Exit"])
##  macro.submit(conflag=1)
##  macro.clear()
  #  READ THE PDB FILE
  pdb = pdb_file.Structure("%s.xplor"%pdbfile)
  # INITIALIZE YASARE
  macro.write(["ErrorExit On",
               "Screensize 800,800",
               "LoadPDB %s.xplor"%pdbfile,
               "Colbg 666699,white",
               "ColorAll 325",
               "ColorRes SecStr Helix, blue",
               "ColorRes SecStr Strand, red",
               "Style Ribbon",
               "ZoomObj 1,0",
               "LabelAll Format=%s,Height=1.0,Color=White,X=0.0,Y=2.75,Z=0.0"%path.upper(),
               "LabelPar Font=Arial,Height=1.0,Color=White,OnTop=0,Shrink=1,Fog=0",
               "Console Off"])
  # TAKE ALL RESTRAINTS
  count = 1
  for restraint in restraints[:cutoff]:
    # TAKE ALL ATOM COMBOS
    for k in range(len(restraint.data[0]["RESI"])):
      for l in range(len(restraint.data[1]["RESI"])):
        atomk = restraint.data[0]['NAME'][k]
        atoml = restraint.data[1]['NAME'][l]
        kindex = pdb_resindex(pdb,restraint.data[0]['RESI'][k])
        lindex = pdb_resindex(pdb,restraint.data[1]['RESI'][l])
        resk = pdb.residues[kindex].name
        resl = pdb.residues[lindex].name
        klist = nmcl_pseudoatoms(atomk,resk)
        llist = nmcl_pseudoatoms(atoml,resl)
        for m in klist[:1]:
          for n in llist[:1]:
            serialk = pdb[kindex][m]['serial_number']
            seriall = pdb[lindex][n]['serial_number']
            macro.write("ShowArrow Start=AtAtom,%i,End=AtAtom,%i,Radius=0.1,Heads=0,Color=Yellow"%(serialk,seriall))
        count+=1
  macro.write(["RayTrace %s.bmp,X=150,Y=150,Zoom=1.0,Atoms=Balls,LabelShadow=No"%path,
               "Shell convert -quality 100 %s.bmp %s.jpg"%(path,path),
               "Delfile %s.bmp"%path,
               "Exit"])
  macro.submit()

# GROUP RESTRAINTLIST
# ===================
# GROUP A DISTANCE RESTRAINT LIST
def r_group(restraintlist):
  group = {}
  for restraint in restraintlist:
    rlist = restraint.data[0]["RESI"]+restraint.data[1]["RESI"]
    dres = max(rlist)-min(rlist)
    if dres == 0:
      group['IR']=group.get('IR',[]) + [restraint]
    elif dres == 1:
      group['SQ']=group.get('SQ',[]) + [restraint]
    elif dres <  5:
      group['MR']=group.get('MR',[]) + [restraint]
    elif dres >= 5:
      group['LR']=group.get('LR',[]) + [restraint]
  return group

# SET RESTRAINTLIST
# =================
# SET RESTRAINTLIST TO PROVIDED VALUES FOR UPPER
# AND LOWER BOUNDS
def r_set(restraintlist,lower,upper,target=None):
  setrestraints = []
  # CYCLE THE RESTRAINTS
  for r in restraintlist:
    # SET BOUNDS
    r.lowerb = lower
    r.upperb = upper
    if target: r.target=target
    else: r.target=upper
    # ADD TO LIST
    setrestraints.append(r)
    print "Set bounds for %4i of %4i restraints.\r"%(restraintlist.index(r)+1,len(restraintlist)),
    sys.stdout.flush()
  print
  return setrestraints

# ADJUST RESTRAINTLIST
# ====================
# ADJUST A DISTANCE RESTRAINT LIST TO THE PROVIDED
# STRUCTURE (PDB_FILE INSTANCE)
def r_adjust(restraintlist,pdb,averaging='SUM',precision=None):
  adjusted = []
  # CYCLE THE RESTRAINTS
  for r in restraintlist:
    orig = r.upperb
    coordlist = []
    # CYCLE THE TWO PARTNERS IN THE RESTRAINT
    for i in range(2):
      coords = []
      re = r.data[i]
      # IF THE RESTRAINT HAS A SEGI WE TAKE THAT ONE,
      # OTHERWISE WE ASSUME ONLY ONE CHAIN
      if re["SEGI"]:
        chain_id = re["SEGI"][0]
        for c in pdb.peptide_chains:
          if c.chain_id == chain_id:
            chain = c
      else:
        chain = pdb.peptide_chains[0]
      # SELECT THE CORRECT RESIDUE
      for number in re["RESI"]:
        for res in chain:
          if res.number == number:
            # SELECT THE CORRECT ATOMS
            for ratom in re["NAME"]:
              for atom in nmcl_pseudoatoms(ratom,res.name):
                for patom in res:
                  if patom.name == atom:
                    coords.append(patom.position)
      # STORE COORDINATES
      coordlist.append(coords)
    # CALCULATE NEW UPPERBOUND
    upp = nmr_averagedistance(coordlist[0],coordlist[1],averaging)
    if not precision:
      if upp <= 2.8: upp = 2.8
      elif upp <= 3.5: upp = 3.5
      elif upp <= 5.0: upp = 5.0
      elif upp > 5.0: upp = round(upp)
      r.lowerb = 0.0
      r.upperb = upp
    else:
      r.lowerb = upp - precision/2.0
      r.upperb = upp + precision/2.0
    r.target = r.upperb
    adjusted.append(r)
    print "Adjusted %4i of %4i restraints.\r"%(restraintlist.index(r)+1,len(restraintlist)),
    sys.stdout.flush()
  print
  return adjusted

#  ======================================================================
#    N O M E N C L A T U R E   F U N C T I O N   G R O U P
#  ======================================================================

# CONVERT AMINOACID
# =================
# FUNCTION CONVERTS A STRING CONTAINING AN AMINO-ACID IN 3- OR 1-LETTER CODE
# TO A LIST OF STRING WITH THE 1 LETTER CODE AS ELEMENT 0, THE 3-LETTER CODE
# AS ELEMENT 1 AND THE NAME AS ELEMENT 2.
# CODE WAS TAKEN FROM ARIA SOURCE CODE.
def nmcl_aminoacid(input):
  # THE DICTIONARY FOR CONVERSION FROM 1 TO 3
  one2all = {'A': ['A', 'ALA', 'alanine'],
             'R': ['R', 'ARG', 'arginine'],
             'N': ['N', 'ASN', 'asparagine'],
             'D': ['D', 'ASP', 'aspartic acid'],
             'C': ['C', 'CYS', 'cysteine'],
             'Q': ['Q', 'GLN', 'glutamine'],
             'E': ['E', 'GLU', 'glutamic acid'],
             'G': ['G', 'GLY', 'glycine'],
             'H': ['H', 'HIS', 'histidine'],
             'I': ['I', 'ILE', 'isoleucine'],
             'L': ['L', 'LEU', 'leucine'],
             'K': ['K', 'LYS', 'lysine'],
             'M': ['M', 'MET', 'methionine'],
             'F': ['F', 'PHE', 'phenylalanine'],
             'P': ['P', 'PRO', 'proline'],
             'S': ['S', 'SER', 'serine'],
             'T': ['T', 'THR', 'threonine'],
             'W': ['W', 'TRP', 'tryptophan'],
             'Y': ['Y', 'TYR', 'tyrosine'],
             'V': ['V', 'VAL', 'valine']}
  # THE DICTIONARY FOR CONVERSION FROM 3 TO 1.
  three2all = {'ALA': ['A', 'ALA', 'alanine'],
               'ARG': ['R', 'ARG', 'arginine'],
               'ASN': ['N', 'ASN', 'asparagine'],
               'ASP': ['D', 'ASP', 'aspartic acid'],
               'CYS': ['C', 'CYS', 'cysteine'],
               'GLN': ['Q', 'GLN', 'glutamine'],
               'GLU': ['E', 'GLU', 'glutamic acid'],
               'GLY': ['G', 'GLY', 'glycine'],
               'HIS': ['H', 'HIS', 'histidine'],
               'ILE': ['I', 'ILE', 'isoleucine'],
               'LEU': ['L', 'LEU', 'leucine'],
               'LYS': ['K', 'LYS', 'lysine'],
               'MET': ['M', 'MET', 'methionine'],
               'PHE': ['F', 'PHE', 'phenylalanine'],
               'PRO': ['P', 'PRO', 'proline'],
               'SER': ['S', 'SER', 'serine'],
               'THR': ['T', 'THR', 'threonine'],
               'TRP': ['W', 'TRP', 'tryptophan'],
               'TYR': ['Y', 'TYR', 'tyrosine'],
               'VAL': ['V', 'VAL', 'valine'] }
  cleaninput = string.strip(string.upper(input))
  # HANDLE THE ONE-LETTER CODES
  if len(cleaninput) == 1:
    if one2all.has_key(cleaninput):
      return one2all[cleaninput]
  # HANDE THE THREE-LETTER CODE
  elif len(cleaninput) == 3:
    if three2all.has_key(cleaninput):
      return three2all[cleaninput]
  return ['', '', input]


# CONVERT ATOM NAMES BETWEEN NOMENCLATURES
# ========================================
def nmcl_convert(informat,outformat,aa,atomname,atomnomtbl=None):
  # DIRTY!
  if atomnomtbl==None: atomnomtbl = nmvconf["ATOMNOM"]
  # CREATE ONE LETTER CODE FOR AA
  aa = nmcl_aminoacid(aa)[0]
  # NOMENCLATURE FILE
  file = open(atomnomtbl,'r').readlines()
  ndict = {}
  formats = []
  for line in file:
    # STORE FORMATS
    if len(line)>1 and line[2:6]=='A.A.':
      sline = string.split(line[6:])
      for elem in sline: formats.append(elem)
    # STORE NAME
    if len(line)>1 and line[0]!='#':
      line = string.split(line)
      # ONELETTERCODES
      faa = line[0]
      ndict[faa]=ndict.get(faa,{})
      # ATOMNAME
      for pos in range(len(line[1:])):
        # NAME
        format = formats[pos]
        ndict[faa][format]=ndict[faa].get(format,[]) + [line[pos+1]]
  # DO THE CONVERSION
  if atomname not in ndict[aa][informat]:
    if atomname in ndict['N_ter'][informat]: aa='N_ter'
    if atomname in ndict['C_ter'][informat]: aa='C_ter'
  namepos = ndict[aa][informat].index(atomname)
  return ndict[aa][outformat][namepos]


# CONVERT ATOM NAMES FROM PDB TO CNS OR FROM CNS TO PDB
# =====================================================
def nmcl_pdbvscns(threelettercode, atomname):
  # A LONG LIST OF CONVERSIONS
  #1. GLY HA:
  if threelettercode == 'GLY' and atomname in ['HA1','1HA']:
      atomname = 'HA3'
  if threelettercode == 'GLY' and atomname in ['HA2','2HA']:
      atomname = 'HA2'
  elif threelettercode == 'GLY' and atomname in ['HA3','3HA']:
      atomname = 'HA1'
  #2. ARG, ASN, ASP, CYS, GLN, GLU, HIS, LEU, LYS, MET, PHE, PRO, SER, TRP, TYR HB%:
  elif threelettercode in ('ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'HIS', 'LEU', 'LYS',\
                           'MET', 'PHE', 'PRO', 'SER', 'TRP', 'TYR') and \
                           atomname in ['HB3','3HB']:
    atomname = 'HB1'
  elif threelettercode in ('ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'HIS', 'LEU', 'LYS',\
                           'MET', 'PHE', 'PRO', 'SER', 'TRP', 'TYR') and \
                           atomname in ['HB2','2HB']:
    atomname = 'HB2'
  elif threelettercode in ('ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'HIS', 'LEU', 'LYS',\
                           'MET', 'PHE', 'PRO', 'SER', 'TRP', 'TYR') and \
                           atomname in ['HB1','1HB']:
    atomname = 'HB3'
  #3. ARG, GLN, GLU, LYS, MET, PRO HG%:
  elif threelettercode in ('ARG', 'GLN', 'GLU', 'LYS', 'MET', 'PRO') and\
       atomname in ['HG1','1HG']:
    atomname = 'HG3'
  elif threelettercode in ('ARG', 'GLN', 'GLU', 'LYS', 'MET', 'PRO') and\
       atomname in ['HG2','2HG']:
    atomname = 'HG2'
  elif threelettercode in ('ARG', 'GLN', 'GLU', 'LYS', 'MET', 'PRO') and\
       atomname in ['HG3','3HG']:
    atomname = 'HG1'
  #4. ILE HG1%:
  elif threelettercode == 'ILE' and atomname in ['HG13','3HG1']:
    atomname = 'HG11'
  elif threelettercode == 'ILE' and atomname in ['HG12','2HG1']:
    atomname = 'HG12'
  elif threelettercode == 'ILE' and atomname in ['HG11','1HG1']:
    atomname = 'HG13'
  #5. ARG, ASN, LYS, PRO HD:
  elif threelettercode in ('ARG', 'ASN', 'LYS', 'PRO') and atomname in ['HD1','1HD']:
    atomname = 'HD3'
  elif threelettercode in ('ARG', 'ASN', 'LYS', 'PRO') and atomname in ['HD2','2HD']:
    atomname = 'HD2'
  elif threelettercode in ('ARG', 'ASN', 'LYS', 'PRO') and atomname in ['HD3','3HD']:
    atomname = 'HD1'
  #6. LYS HE:
  elif threelettercode == 'LYS' and atomname in ['HE3','3HE']:
    atomname = 'HE1'
  elif threelettercode == 'LYS' and atomname in ['HE2','2HE']:
    atomname = 'HE2'
  elif threelettercode == 'LYS' and atomname in ['HE1','1HE']:
    atomname = 'HE3'
  #1. ALA beta:
  elif threelettercode == 'ALA' and atomname in ['HB2','2HB']:
    atomname = 'HB1'
  elif threelettercode == 'ALA' and atomname in ['HB3','3HB']:
    atomname = 'HB3'
  elif threelettercode == 'ALA' and atomname in ['HB1','1HB']:
    atomname = 'HB2'
  #2. VAL gamma1:
  elif threelettercode == 'VAL' and atomname in ['HG11','1HG1']:
    atomname = 'HG12'
  elif threelettercode == 'VAL' and atomname in ['HG12','2HG1']:
    atomname = 'HG11'
  elif threelettercode == 'VAL' and atomname in ['HG13','3HG1']:
    atomname = 'HG13'
  #3. ILE, VAL gamma2:
  elif threelettercode in ('ILE', 'VAL') and atomname in ['HG21','1HG2']:
    atomname = 'HG22'
  elif threelettercode in ('ILE', 'VAL') and atomname in ['HG22','2HG2']:
    atomname = 'HG21'
  elif threelettercode in ('ILE', 'VAL') and atomname in ['HG23','3HG2']:
    atomname = 'HG23'
  #4. ILE, LEU delta1:
  elif threelettercode in ('ILE', 'LEU') and atomname in ['HD11','1HD1']:
      atomname = 'HD12'
  elif threelettercode in ('ILE', 'LEU') and atomname in ['HD12','2HD1']:
      atomname = 'HD11'
  elif threelettercode in ('ILE', 'LEU') and atomname in ['HD13','3HD1']:
      atomname = 'HD13'
  #5. LEU delta2:
  elif threelettercode == 'LEU' and atomname in ['HD21','1HD2']:
      atomname = 'HD22'
  elif threelettercode == 'LEU' and atomname in ['HD22','2HD2']:
      atomname = 'HD21'
  elif threelettercode == 'LEU' and atomname in ['HD23','3HD2']:
      atomname = 'HD23'
  #6. MET epsilon:
  elif threelettercode == 'MET' and atomname in ['HE1','1HE']:
      atomname = 'HE2'
  elif threelettercode == 'MET' and atomname in ['HE2','2HE']:
      atomname = 'HE1'
  elif threelettercode == 'MET' and atomname in ['HE3','3HE']:
      atomname = 'HE3'
  #7. zeta:
  elif threelettercode != 'TRP' and atomname in ['HZ1','1HZ']:
      atomname = 'HZ2'
  elif threelettercode != 'TRP' and atomname in ['HZ2','2HZ']:
      atomname = 'HZ1'
  #IV. ARG NHs:
  elif threelettercode == 'ARG' and atomname in ['HH11','1HH1']:
      atomname = 'HH12'
  elif threelettercode == 'ARG' and atomname in ['HH12','2HH1']:
      atomname = 'HH11'
  elif threelettercode == 'ARG' and atomname in ['HH21','1HH2']:
      atomname = 'HH22'
  elif threelettercode == 'ARG' and atomname in ['HH22','2HH2']:
        atomname = 'HH21'
  # V. Additional stuff:
  elif threelettercode == 'ASN' and atomname in ['HD21','1HD2']:
    atomname = 'HD21'
  elif threelettercode == 'ASN' and atomname in ['HD22','2HD2']:
    atomname = 'HD22'
  elif threelettercode == 'GLN' and atomname in ['HE21','1HE2']:
    atomname = 'HE21'
  elif threelettercode == '' and atomname in ['HE22','2HE2']:
    atomname = 'HE22'
  else:
    if len(atomname)>2 and 'Q' not in atomname:
      print 'Atomname %s in %s not converted!'%(atomname,threelettercode)
  return atomname


# CONVERT PSEUDO ATOMS TO CNS FORMAT
# ==================================
# PSEUDO ATOMS ARE CONVERT TO THE APPROPRIATE
# CNS GROUP DEFINITIONS
def nmcl_pseudo2cns(atom):
  # THE REPLACEMENT DICTIONARY
  replacedic = {'QA' : 'HA#',
                'QB' : 'HB#',
                'QG' : 'HG#',
                'QG1': 'HG1#',
                'QG2': 'HG2#',
                'QQG': 'HG#',
                'QD' : 'HD#',
                'QD1': 'HD1#',
                'QD2': 'HD2#',
                'QQD': 'HD#',
                'QE' : 'HE#',
                'QE2': 'HE2#',
                'QR' : 'HD# or name HE# or name HZ',
                'QZ' : 'HZ#',
                'QH1': 'HH1#',
                'QH2': 'HH2#' }
  atom = string.strip(string.upper(atom))
  if replacedic.has_key(atom):
    atom = replacedic[atom]
  return atom

# PSEUDO ATOMS
# ============
# RETURN ALL ATOMS INVOLVED IN PSEUDO ATOMS
def nmcl_pseudoatoms(name,residue,format='XPLOR'):
  # DIRTY HACK!!!!
  name = name.replace('*','#')
  residue = nmcl_aminoacid(residue)[0]
  # HANDLE THE XPLOR FORMAT
  if format=='XPLOR':
    if name=='HA#': return ['HA1','HA2']
    elif name=='HB#':
      if residue=='A':
        return ['HB1','HB2','HB3']
      # CIRCUMVENT A COMMON MISTAKE
      elif residue=='V':
        return ['HB']
      else:
        return ['HB1','HB2']
    elif name=='HG#' or name=='HG##':
      if residue=='T':
        return ['HG21','HG22','HG23']
      elif residue=='V':
        return ['HG21','HG22','HG23','HG11','HG12','HG13']
      else:
        return ['HG1','HG2']
    elif name=='HG1#':
      if residue=='I':
        return ['HG11','HG12']
      else:
        return ['HG11','HG12','HG13']
    elif name=='HG2#':
      return ['HG21','HG22','HG23']
    elif name=='HD#' or name=='HD##':
      if residue=='N':
        return ['HD21','HD22']
      elif residue=='I':
        return ['HD11','HD12','HD13']
      elif residue=='L':
        return ['HD11','HD12','HD13','HD21','HD22','HD23']
      else:
        return ['HD1','HD2']
    elif name=='HD1#':
      return ['HD11','HD12','HD13']
    elif name=='HD2#':
      return ['HD21','HD22','HD23']
    elif name=='HE#':
      if residue=='Q':
        return ['HE21','HE22']
      if residue=='M':
        return ['HE1','HE2','HE3']
      if residue=='Y':
        return ['HE1','HE3']
      else:
        return ['HE1','HE2']
    elif name=='HE2#':
      if residue=='Q':
        return ['HE21','HE22']
    elif name=='HH#' or name =='HH##':
      return ['HH11','HH12','HH13','HH21','HH22','HH23']
    elif name=='HH2#':
      return ['HH21','HH22','HH23']
    elif name=='HH1#':
      return ['HH11','HH12','HH13']
    elif name=='HZ#':
      return ['HZ1','HZ2','HZ3']
    elif name=='HT#':
      return ['HT1','HT2','HT3']
    else:
      return [name]
  else: return None

#  ======================================================================
#    X P L O R   C L A S S
#  ======================================================================

class xplor:
  """
  This class is used to stores parameters pertaining to an XPLOR project.
  - Create a class instance by passing the command to run XPLOR.
  """
  def __init__(self,path):
    self.path = path

#  ======================================================================
#    Y A S A R A   M A C R O   C L A S S
#  ======================================================================

class ysr_macro:
  """
  This class provides an interface to YASARA
  Create a class instance passing the command to run YASARA and the name
  of an error handling function.
  - Instance.error contains an error description if something went wrong
  - Instance.clear() clears the macro
  - Instance.write() adds a line (if argument is a string) or multiple lines
    (if argument is a list) to the macro. Line feeds are added automatically.
  - Instance.submit() executes the macro in YASARA
  """

  # OPEN MACRO FILE FOR OUTPUT
  # ==========================
  # - yasara IS THE COMMAND TO RUN YASARA.
  def __init__(self,yasara,scriptpath='/tmp',errorfunc=None):
    self.yasara=yasara
    self.errorfunc=errorfunc
    self.script = os.path.join(scriptpath,'startup_%i.mcr'%os.getpid())
    self.clear()

  # RAISE AN ERROR
  # ==============
  # CALLS THE ERRORFUNCTION PROVIDED BY THE USER WITH THE GIVEN STRING
  def raiseerror(self,errormsg):
    self.error=errormsg
    if (self.errorfunc!=None): apply(self.errorfunc,[errormsg])
    return

  # CLEAR MACRO
  # ===========
  # THE FILE "startup.mcr" IS REOPENED, ALL DATA WRITTEN TO THE MACRO IS LOST.
  def clear(self):
    self.error=None
    try: self.macro=open(self.script,"w")
    except: self.raiseerror("YASARA macro startup.mcr could not be created")

  # ADD A LINE TO THE MACRO
  # =======================
  # data IS EITHER A STRING OR A LIST OF STRINGS, LINE FEEDS WILL BE ADDED WHEN MISSING.
  def write(self,data):
    if (not self.error):
      if (type(data)==types.ListType):
        for line in data:
          if (line=="" or line[-1]!='\n'): line=line+"\n"
          self.macro.write(line)
      else:
        if (data=="" or data[-1]!='\n'): data=data+"\n"
        self.macro.write(data)

  # SUBMIT MACRO
  # ============
  # THE MACRO IS SUBMITTED TO YASARA
  def submit(self,conflag=0):
    #global debugflag
    ret=0
    if (not self.error):
      self.macro.close()
      if not conflag:
        try: ret=os.system(self.yasara+" -mcr %s"%self.script)
        except: self.raiseerror("YASARA could not be run")
      else:
        try: ret=os.system(self.yasara+" -con -mcr %s"%self.script)
        except: self.raiseerror("YASARA could not be run")
    return(ret)

#  ======================================================================
#    G R A C E P L O T   C L A S S
#  ======================================================================

class graceplot:
  """
  This class provides an interface to GRACE plots.
  Create class instance by giving a path+filename,a type,'r'/'w'/'a' and
  an error handling function.
  Current supported types are:
    - xy     : xy and an optional string annotation
    - bar    : xy and an optional string annotation
    - xyz    : xy and z value
    - xydy   : same as xy but with error on y axis
    - xydxdy : same as xy but with error on x and y axes
    - xysize : same ax xy but symbol size is variable
  -
  """
  def __init__(self,path,type,access,errorfunc=None):
    self.error=None
    self.errorfunc=errorfunc
    self.path=path
    self.type=type
    # IF DESIRED, OPEN FILE
    if access=='w':
      self.file = open(path,'w')
    # STUFF FOR THE HEADER
    self.title = None
    self.xlab = None
    self.ylab = None
    self.subtitle = None
    # SET TO ONE FOR A SQUARE PLOT
    self.square = 0

  # WRITE HEADER
  # ============
  # WRITE A HEADER TO THE DATA FILE
  def writeheader(self):
    # ALWAYS WRITE HEADER
    self.file.write("# GRACE input file written by queen.py\n")
    self.file.write("# On my watch it's %s.\n#\n" % time.ctime(time.time()))
    # WRITE IF PRESENT
    if self.title:
      self.file.write("@    title \"%s\"\n"%self.title)
    if self.subtitle:
      self.file.write("@    subtitle \"%s\"\n"%self.subtitle)
    if self.xlab:
      self.file.write("@    xaxis  label \"%s\"\n"%self.xlab)
    if self.ylab:
      self.file.write("@    yaxis  label \"%s\"\n"%self.ylab)
    if self.square:
      self.file.write("@    page size 594,594\n")
      self.file.write("@    view xmax 0.850000\n")
    # ALWAYS WRITE THE TYPE
    self.file.write("@TYPE %s\n"%self.type)

  # ADD TO HEADER
  # =============
  # ADD CUSTOM LINE TO THE HEADER
  def add2header(self,string):
    self.file.write("%s\n"%string)

  # WRITE COMMENT
  # =============
  # ADD A COMMENT TO THE DATAFILE
  def comment(self,comment):
    self.file.write("# %s\n"%comment)
    self.file.flush()

  # NEW SET
  # =======
  # START A NEW DATASET
  def newset(self):
    self.file.write("@\n")
    self.file.write("@TYPE %s\n"%self.type)
    self.file.flush()

  # WRITE DATA
  # ==========
  # ADD DATA POINT
  def write(self,data):
    if self.type=='xy' or self.type=='bar':
      if len(data)==2:
        self.file.write("%10e %10e\n"%(data[0],data[1]))
      elif len(data)==3:
        self.file.write("%10e %10e \"%s\"\n"%(data[0],data[1],data[2]))
    if self.type=='xydy':
      if len(data)==3:
        self.file.write("%10e %10e %10e\n"%(data[0],data[1],data[2]))
      if len(data)==4:
        self.file.write("%10e %10e %10e \"%s\"\n"%(data[0],data[1],data[2],data[3]))
    if self.type=='xydxdy':
      if len(data)==4:
        self.file.write("%10e %10e %10e %10e\n"%(data[0],data[1],
                                                 data[2],data[3]))
      if len(data)==5:
        self.file.write("%10e %10e %10e %10e \"%s\"\n"%(data[0],data[1],
                                                        data[2],data[3],
                                                        data[4]))
    if self.type=='xysize':
      self.file.write("%10e %10e %10e\n"%(data[0],data[1],data[2]))
    self.file.flush()

  # WRITE MULTIPLE DATA
  # ===================
  # ADD MULTIPLE DATA POINTS
  def mwrite(self,datalist):
    for datapoint in datalist:
      self.write(datapoint)

  # GENERATE PLOT
  # =============
  # PLOT THE GRACE FILE. SUPPORTED FORMATS:
  # - ps
  def output(self,format='ps'):
    # AUTOGENERATE FILE NAME
    plotfile = "%s.%s"%(os.path.splitext(self.path)[0],format)
    # GENERATE THE PLOT
    if format=='ps':
#      os.popen("gracebat -printfile %s %s"%(plotfile,self.path))
      cmd = "gracebat -printfile %s %s" % (plotfile,self.path)
      _pipe = Popen(cmd, shell=True, stdout=PIPE).stdout

  # CLOSE
  # =====
  # CLOSE THE FILE
  def close(self):
    #self.file.write("&\n")
    self.file.close()

#  ======================================================================
#    X P L O R _ S C R I P T   C L A S S
#  ======================================================================

class xplor_script:
  """
  This class provides an interface to XPLOR / XPLOR-NIH
  - Create a class instance passing the command to run XPLOR
  - Instance.error contains an error description if something went wrong
  - Instance.clear() clears the current script
  - Instance.write() adds a line to the script
  - Instance.submit() executes the script in XPLOR
  """

  # OPEN SCRIPT FILE FOR OUTPUT
  # ===========================
  # - xplor IS THE COMMAND TO RUN XPLOR
  # - runpath IS THE PATH WHERE XPLOR IS RAN
  # - errorfunc IS THE NAME OF THE ERROR HANDLING FUNCTION
  def __init__(self,xplor,scriptpath='/tmp/',errorfunc=error,logfiles='delete'):
    self.xplor=xplor
    self.progstr = 'XPLOR'
    id = 1
    self.scriptpath = os.path.join(scriptpath,'%s_%i_%s.in'%(self.progstr,
                                                             os.getpid(),
                                                             socket.gethostname()))
    self.logpath = os.path.join(scriptpath,'%s_%i_%s.log'%(self.progstr,
                                                           os.getpid(),
                                                           socket.gethostname()))
    self.errorfunc=errorfunc
    self.logfiles = logfiles
    self.clear()

  # RAISE AN ERROR
  # ==============
  # CALLS THE ERRORFUNCTION PROVIDED BY THE USER WITH THE GIVEN STRING
  def raiseerror(self,errormsg):
    self.error=errormsg
    if (self.errorfunc!=None): apply(self.errorfunc,[errormsg])
    return

  # CLEAR THE SCRIPT
  # ================
  # THE SCRIPT FILE IS REOPENED, instance.error IS CLEARED
  def clear(self):
    self.error=None
    try: self.script=open(self.scriptpath,"w")
    except: self.raiseerror("%s script could not be created"%self.progstr)

  # ADD A LINE TO THE SCRIPT
  # ========================
  def write(self,line):
    if (not self.error): self.script.write(line+"\n")

  # SUBMIT SCRIPT
  # =============
  def submit(self):
    if (not self.error):
      # CLOSE THE SCRIPT
      self.write("stop")
      self.script.close()
      # RUN XPLOR WITH THE SCRIPT
#      log = os.popen("%s < %s"%(self.xplor,self.scriptpath))
      cmd = "%s < %s"%(self.xplor,self.scriptpath)
      log = Popen(cmd, shell=True, stdout=PIPE).stdout

      # CHECK FOR ERRORS
      xplorlog = log.read()
      skiperrors = string.count(xplorlog,"POWELL-ERR")
      errors = string.count(xplorlog,"ERR")
      warnings = string.count(xplorlog,"WRN")
      # TAKE CARE OF ERRORS
      if errors-skiperrors:
        file = open(self.logpath,'w')
        file.write(xplorlog)
        self.raiseerror("%s generated %i errors.\nLogfile: %s"%(self.progstr,errors-skiperrors,self.logpath))
      # TAKE CARE OF WARNINGS
      if warnings:
        file = open(self.logpath,'w')
        file.write(xplorlog)
        print "%s generated %i warnings. Please investigate!\nLogfile: %s"%(self.progstr,warnings,self.logpath)
      exitstatus = log.close()
      if (exitstatus): self.raiseerror("XPLOR returned error %d"%exitstatus)
      if self.logfiles=='delete':
        os.remove(self.scriptpath)
      elif self.logfiles=='keep':
        print "%s executed without serious problems."%self.progstr
        print "Log can be found in: %s"%self.logpath
        print "Script can be found in: %s"%self.scriptpath
        file = open(self.logpath,'w')
        file.write(xplorlog)
      elif self.logfiles=='silent':
        file = open(self.logpath,'w')
        file.write(xplorlog)
    return

#  ======================================================================
#    N M R _ R E S T R A I N T   C L A S S
#  ======================================================================
class nmr_restraint:
  """
  This class provides a description for an NMR restraint.
  Create a class instance by given a type.
  Current types are:
   - DIST : distance restraints
   - DIHE : dihedral angle restraints
   - DIPO : dipolar coupling restraints
  - Instance.format(format) returns a formatted string.
    Current formats: XPLOR
    CNCR is under construction...
  """
  def __init__(self,type="DIST",pdb_file=None,error=error):
    self.type = type
    self.error = error
    self.pdb = pdb_file
    self.ambiguous = None
    # DEFINE DISTANCE RESTRAINT
    if type == "DIST":
      # SELECTION OF ATOMS INVOLVED
      dict = {"RESI":[],"RESN":[],"SEGI":[],"ATOM":[],"NAME":[]}
      self.data = {0:copy.deepcopy(dict),1:copy.deepcopy(dict)}
      # DISTANCE BOUNDS
      self.target = 0.0
      self.lowerb = 0.0
      self.upperb = 0.0
    # DEFINE A DIHEDRAL ANGLE RESTRAINT
    elif type == "DIHE":
      # SELECTION OF ATOMS INVOLVED
      dict = {"RESI":[],"RESN":[],"SEGI":[],"ATOM":[],"NAME":[]}
      self.data = {0:copy.deepcopy(dict),
                   1:copy.deepcopy(dict),
                   2:copy.deepcopy(dict),
                   3:copy.deepcopy(dict)}
      # ANGLE BOUNDS
      self.c = 1.0      # XPLOR - CONSTANT
      self.angle = 0.0
      self.range = 0.0
      self.ed = 2       # XPLOR - EXPONENT
    # DEFINE A DIPOLAR COUPLING RESTRAINT
    elif type=="DIPO":
      # SELECTION OF THE ATOMS INVOLVED
      pass

  # STRING REPRESENTATION
  # =====================
  # DEPENDING OF THE TYPE OF RESTRAINT WE CHOOSE
  # A REPRESENTATION
  def __str__(self):
    # DISTANCE TYPE
    if self.type=="DIST":
      str = '['
      # SORT THE PARTNER IN THE RESTRAINT
      r0 = copy.copy(self.data[0]["RESI"])
      r0.sort()
      r1 = copy.copy(self.data[1]["RESI"])
      r1.sort()
      # KEEP LIST
      rstrlist = []
      # CYCLE THE PARTNERS IN THE RESTRAINT
      for i in range(len(r0)):
        for j in range(len(r1)):
          try: index0 = self.data[0]["RESI"][i:].index(r0[i])+i
          except ValueError: index0 = i
          try: index1 = self.data[1]["RESI"][j:].index(r1[j])+j
          except ValueError: index1 = j
          # IN CASE OF A SEQUENCE ID, WE BUILD A LONGER STRING
          if len(self.data[0]["SEGI"])>0:
            rstr = '(%s-%s-%s-%s-%s-%s)'%(r0[i],self.data[0]["NAME"][index0],self.data[0]["SEGI"][index0],r1[j],self.data[1]["NAME"][index1],self.data[1]["SEGI"][index1])
          # IN CASE OF NO SEQUENCE ID, WE CAN KEEP IT SOMEWHAT SHORTER
          else:
            rstr = '(%s-%s-%s-%s)'%(r0[i],self.data[0]["NAME"][index0],r1[j],self.data[1]["NAME"][index1])
          rstrlist.append(rstr)
      # SORT AND CONSTRUCT THE LIST
      rstrlist.sort()
      for elem in rstrlist:
        str+=elem
      str += ']'
      return str
    # DIHEDRAL TYPE
    if self.type=="DIHE":
      str = '['
      r0 = copy.copy(self.data[0]["RESI"])
      r0.sort()
      r1 = copy.copy(self.data[1]["RESI"])
      r1.sort()
      r2 = copy.copy(self.data[2]["RESI"])
      r2.sort()
      r3 = copy.copy(self.data[3]["RESI"])
      r3.sort()
      for i in range(len(r0)):
        for j in range(len(r1)):
          for k in range(len(r2)):
            for l in range(len(r3)):
              index0 = self.data[0]["RESI"].index(r0[i])
              index1 = self.data[1]["RESI"].index(r1[j])
              index2 = self.data[2]["RESI"].index(r2[i])
              index3 = self.data[3]["RESI"].index(r3[j])
              str += '(%s-%s-%s-%s-%s-%s-%s-%s)'%(r0[i],self.data[0]["NAME"][index0],r1[j],self.data[1]["NAME"][index1],r2[k],self.data[2]["NAME"][index2],r3[l],self.data[3]["NAME"][index3])
      str += ']'
      return str
    else:
      return ""

  # RESTRAINT HASH
  # ==============
  # VERY PRIMITIVE, BUT SHOULD BE
  # COMPATIBLE WITH __EQ__
  def __hash__(self):
    return hash(str(self))

  # RESTRAINT COMPARISON
  # ====================
  # COMPARE RESTRAINTS, WE ONLY CHECK IF THE
  # ASSIGNED ATOMS AND RESIDUES ARE THE SAME
  def __eq__(self,other):
    eq=0
    # DISTANCE TYPE
    if self.type=="DIST":
      if str(self)==str(other):
        eq=1
    # DIHEDRAL TYPE
    if self.type=="DIHE":
      if str(self)==str(other):
        eq=1
    return eq

  # GREATER THEN
  # ============
  def __gt__(self,other):
    gt = 0
    # DISTANCE TYPE
    if self.type=='DIST':
      if (self.upperb-self.lowerb) > (other.upperb-other.lowerb):
        gt=1
    # DIHEDRAL TYPE
    if self.type=='DIHE':
      sdif = (self.angle+self.range)-(self.angle-self.range)
      odif = (other.angle+other.range)-(other.angle-self.range)
      if sdif > odif:
        gt=1
    return gt

  # LESS THEN
  # =========
  def __lt__(self,other):
    lt = 0
    # DISTANCE TYPE
    if self.type=='DIST':
      if (self.upperb-self.lowerb) < (other.upperb-other.lowerb):
        lt=1
    # DIHEDRAL TYPE
    if self.type=='DIHE':
      sdif = (self.angle+self.range)-(self.angle-self.range)
      odif = (other.angle+other.range)-(other.angle-self.range)
      if sdif < odif:
        lt=1
    return lt

  # FORMAT A RESTRAINT
  # ==================
  # FORMATS A RESTRAINT INTO A FORMAT
  def format(self,format='XPLOR'):
    # DISTANCE TYPE
    if self.type == "DIST":
      # HANDLE XPLOR FORMAT
      if format=="XPLOR":
        # BEGIN FORMATTED RESTRAINT
        fr="ASSI "
        orflag,amflag = 0,0
        # CYCLE THE TWO PARTNERS IN THE RESTRAINT
        for i in range(2):
          # CYCLE ALL AMBIGUOUS ASSIGNMENTS
          for j in range(len(self.data[i]["RESI"])):
            # START GROUP BLOCK
            if len(self.data[i]["RESI"])>1 and j==0:
              fr+='('
              orflag = 1
            # IF NO GROUP ADD ADDITIONAL SPACE
            else: fr+=" "
            # PRINT A BLOCK
            fr += "(RESI %5s AND NAME %4s"%(self.data[i]["RESI"][j],self.data[i]["NAME"][j])
            # IF A SEGID PRESENT WE ADD IT
            if len(self.data[i]["SEGI"])>0:
              fr += " AND SEGI %4s)"%self.data[i]["SEGI"][j]
            # IF NO SEGID IS PRESENT, CLOSE THE GROUP
            else:
              fr += ")"
              amflag = 0
            # END GROUP BLOCK
            if len(self.data[i]["RESI"])>1 and j==len(self.data[i]["RESI"])-1:
              fr+='    )'
              orflag = 0
              amflag = 1
            # ADD THE DISTANCE WITH CORRECT INDENTATION
            if j==len(self.data[i]["RESI"])-1 and i==1:
              # FOR AMBIGUOUS RESTRAINT THE INDENT IS DIFFERENT
              if amflag:
                fr+=" %5.3f %5.3f %5.3f"%(self.target,self.target-self.lowerb,self.upperb-self.target)
              # DEFAULT INDENT
              else:
                fr+="      %5.3f %5.3f %5.3f"%(self.target,self.target-self.lowerb,self.upperb-self.target)
            # END THE LINE
            else:
              # WITH AN OR IF NECESSARY OR A NEW LINE
              if orflag:
                fr+=' OR \n     '
              else:
                fr+='\n     '
    # DIHEDRAL ANGLE TYPE
    #####################
    if self.type == "DIHE":
      # HANDLE XPLOR FORMAT
      #####################
      if format=="XPLOR":
        # BEGIN FORMATTED RESTRAINT
        fr="ASSI "
        # CYCLE THE FOUR PARTNERS IN THE RESTRAINT
        for i in range(4):
          # PRINT A BLOCK
          fr += "(RESI %5s AND NAME %4s"%(self.data[i]["RESI"][0],self.data[i]["NAME"][0])
          # IF A SEGID PRESENT WE ADD IT
          if len(self.data[i]["SEGI"])>0:
            fr += " AND SEGI %4s)"%self.data[i]["SEGI"][0]
          # IF NO SEGID IS PRESENT, CLOSE THE GROUP
          else:
            fr += ")"
          # ADD THE DISTANCE WITH CORRECT INDENTATION
          if i==3:
            fr+=" %4.1f %7.2f %7.2f %i"%(self.c,self.angle,self.range,self.ed)
          # END THE LINE
          else:
            fr+='\n     '
    # RETURN THE FORMATTED STRING
    return fr

#  ======================================================================
#    R E S T R A I N T _ F I L E   C L A S S
#  ======================================================================

class restraint_file:
  """
  This class provides an interface to NMR restraint files.
  Create a class instance by giving a path+filename, 'r','w', a type and an
  error handling function in parentheses.
  Current types are DIST=DISTance data, DIHE=DIHEdral data.
  Current formats are XPLOR=XPLOR data.
   - Instance.read() reads the restraint file.
   - Instance.write(restraint) writes restraint to the file.
  """
  # OPEN THE FILE
  # =============
  # - path IS THE RESTRAINTFILE LOCATION.
  # - access IS EITHER 'r','a' OR 'w'.
  # - type IS THE TYPE OF RESTRAINTS.
  # - format IS THE FORMAT OF THE RESTRAINTS.
  # - errorfunc IS THE NAME OF AN ERROR HANDLING FUNCTION.
  def __init__(self,path,access,type='DIST',format='XPLOR',errorfunc=error):
    self.errorfunc = errorfunc
    self.eof = 0
    self.type = type
    self.format = format
    self.comments = ['#','!']
    self.restraintlist = []
    # OPEN FILE
    try: self.file = open(path,access)
    except:
      self.eof=1
      self.file=None
      self.raiseerror("Restraint file %s not found"%path)
      return
    # IF THE FILE IS READ, SKIP INITIAL COMMENTS
    if (access=='r'):
      while 1:
        # CURRENT POSITION IN FILE IS STORED BEFORE SNOOPING AHEAD
        pos = self.file.tell()
        line=self.file.readline()
        if (len(line)==0): break
        if (line[0] not in self.comments): break
      # BACK TO THE LAST VALID POSITION
      self.file.seek(pos)
    # IF THE FILE IS WRITTEN FOR THE FIRST TIME, ADD INITIAL COMMENTS
    elif access=='w' and self.file.tell()==0:
      self.file.write("! On my watch it's %s.\n!\n"%time.ctime(time.time()))


  # RAISE AN ERROR
  # ==============
  # CALLS THE ERRORFUNCTION PROVIDED BY THE USER WITH THE GIVEN STRING
  def raiseerror(self,errormsg):
    self.error=errormsg
    if (self.errorfunc!=None): apply(self.errorfunc,[errormsg])
    return

  # READ A RESTRAINT
  # ================
  # READ A RESTRAINT FROM THE FILE
  def read(self):
    # RETURN IF NOTHING CAN BE READ
    if (self.eof): return
    # HANDLE NOE TYPE RESTRAINTS
    if self.type == 'DIST':
      # HANDLE THE XPLOR TYPE
      if self.format == 'XPLOR':
        while not self.eof:
          # READ NEW RECORD
          line=self.file.readline()
          # IF LINE IS EMPTY, EOF HAS BEEN REACHED
          if (line==""):
            self.eof=1
          # CUT LINE AT !
          if '!' in line:
            line = line[:string.find(line,'!')]
          # IF WE FIND AN ASSIGN STATEMENT
          # WE BUILD THE FULL LINE
          if string.upper(string.lstrip(line)[:4])=='ASSI':
            # CREATE A RESTRAINT INSTANCE
            restr = nmr_restraint('DIST')
            r = line[:-1]
            #alt = None
            while 1:
              # CURRENT POSITION IS STORED BEFORE SNOOPING AHEAD
              pos=self.file.tell()
              line = self.file.readline()
              # STRIP OFF COMMENTS
              if '!' in line: line[:string.find(line,'!')]
              # HANDLE THE LINE
              if line=="": break
              elif line=='\n': pass
              elif string.upper(string.lstrip(line)[:4])=='ASSI': break
              elif line[0] in self.comments: pass
              # TAKE CARE OF THESE ALTERNATE ASSIGNMENTS!
              # CHECK PERHAPS ARIA DOCUMENTATION....
              ##################################################
              #elif string.split(line)[0]=='OR': pass
              else: r += " "+line[:-1]
            # BACK TO LAST VALID POSITION
            self.file.seek(pos)
            # PARSE THE RESTRAINT LINE
            if string.count(r,'(') == string.count(r,')'):
              if '!' in r:
                r=r[:string.find(r,'!')]
            else:
              self.raiseerror('Inconsistent bracket usage!')
            # RETRIEVE RESIDUE NUMBERS, ATOM NAMES AND DISTANCES
            r = string.upper(r)
            r = r.replace('"','')
            # FIND THE FIRST BRACKET
            pos = string.find(r,'(')
            brkcount,group = 0,0
            # THE LEFTOVERS
            leftover = ''
            # LOOP WHILE WE'RE NOT A THE LAST BRACKET
            while pos <= string.rfind(r,')'):
              # IF WE FIND AN OPENING BRACKET
              if r[pos]=='(':
                brkcount += 1
                # CHECK IF THERE IS ANOTHER OPENING BRACKET
                # BEFORE THE NEXT CLOSING ONE AND WE ARE NOT
                # LOOKIN AT THE LAST OPENING BRACKER
                if string.find(r,'(',pos+1)<string.find(r,')',pos) and pos!=string.rfind(r,'('):
                  pos+=1
                # PARSE THE DATA
                else:
                  data = string.replace(r[pos+1:string.find(r,')',pos)],'AND','')
                  data = string.split(data)
                  # FILL THE RESTRAINT DICT
                  # NORMAL ASSIGNMENT
                  for i in range(len(data)):
                    if i%2==0:
                      if data[i][:4]=="RESI":
                        restr.data[group%2][data[i][:4]].append(int(data[i+1]))
                      else:
                        restr.data[group%2][data[i][:4]].append(data[i+1])
                  pos = string.find(r,')',pos)
              # OTHERWISE READ NEXT CHARACTER
              else:
                # LOWER THE BRACKET COUNTER
                if r[pos]==')':
                  brkcount -=1
                  # IF THE FIRST GROUP IS FINISHED
                  # GO TO THE SECOND
                  if brkcount == 0:
                    group += 1
                # IF WE'RE BETWEEN ASSIGNMENTS THERE MIGHT BE AN
                # ALTERNATE ASSIGNMENT OR!
                else:
                  if brkcount == 0:
                    leftover+=r[pos]
                pos+=1
            # PARSE THE DISTANCES
            # IN CASE OF AN 'OR' ASSIGNMENT AFTER A FULL ASSIGNMENT
            # WITH DISTANCES, THE DISTANCES ARE FOUND IN THE LEFTOVER
            # AND NOT AT THE END OF THE RESTRAINT STRING
            if len(leftover.split())==0:
              distlist = string.split(r[string.rfind(r,')')+1:])
            else:
              distlist = string.split(leftover)[:3]
            restr.target = float(distlist[0])
            restr.lowerb = restr.target-float(distlist[1])
            restr.upperb = restr.target+float(distlist[2])
            # REDUCE AMBIGUITY
            if len(restr.data[0]["RESI"])>1 or len(restr.data[1]["RESI"])>1:
              #print "before:"
              #print restr.format()
              for i in range(2):
                # FIND MAX LENGTH
                maxl = 0
                for key in restr.data[i].keys(): maxl = max(maxl,len(restr.data[i][key]))
                # CHECK FOR DOUBLES
                chklist = []
                posdel = []
                for j in range(maxl):
                  # BUILD CHECK STRING
                  chkstr = ''
                  for key in restr.data[i].keys():
                    if len(restr.data[i][key])==maxl:
                      chkstr += "%s-"%restr.data[i][key][j]
                  # CHECK IF CHECKSTRING IS KNOWN
                  if chkstr not in chklist:
                    chklist.append(chkstr)
                  else:
                    posdel.append(j)
                # DO THE DELETIONS
                posdel.sort()
                posdel.reverse()
                for el in posdel:
                  for key in restr.data[i].keys():
                    if len(restr.data[i][key])==maxl:
                      del restr.data[i][key][el]
              #print "after:"
              #print restr.format()
            # CHECK IF RESTRAINT IS AMBIGUOUS
            if len(restr.data[0]["RESI"])>1 or len(restr.data[1]["RESI"])>1:
              restr.ambiguous=1
            else: restr.ambiguous = 0
            # STORE THE RESTRAINT
            self.restraintlist.append(restr)
            #if restr.ambiguous: x = raw_input()
    # HANDLE THE DIHEDRAL ANGLE RESTRAINTS
    if self.type == 'DIHE':
      # HANDLE THE XPLOR TYPE
      if self.format == 'XPLOR':
        while not self.eof:
          # READ NEW RECORD
          line=self.file.readline()
          # IF LINE IS EMPTY, EOF HAS BEEN REACHED
          if (line==""):
            self.eof=1
          # IF WE FIND AN ASSIGN STATEMENT
          # WE BUILD THE FULL LINE
          if string.upper(string.lstrip(line)[:4])=='ASSI':
            # CREATE A RESTRAINT INSTANCE
            restr = nmr_restraint('DIHE')
            r = line[:-1]
            #alt = None
            while 1:
              # CURRENT POSITION IS STORED BEFORE SNOOPING AHEAD
              pos=self.file.tell()
              line = self.file.readline()
              if (line==""): break
              elif string.upper(string.lstrip(line)[:4])=='ASSI': break
              elif line[0] in self.comments: pass
              else: r += " "+line[:-1]
            # BACK TO LAST VALID POSITION
            self.file.seek(pos)
            # PARSE THE RESTRAINT LINE
            if string.count(r,'(') == string.count(r,')'):
              r = string.replace(r,'*','#')
              if '!' in r:
                r=r[:string.find(r,'!')]
            else:
              self.raiseerror('Inconsistent bracket usage!')
            # RETRIEVE RESIDUE NUMBERS, ATOM NAMES AND DISTANCES
            r = string.upper(r)
            # FIND THE FIRST BRACKET
            pos = string.find(r,'(')
            brkcount,group = 0,0
            # LOOP WHILE WE'RE NOT A THE LAST BRACKET
            while pos <= string.rfind(r,')'):
              # IF WE FIND AN OPENING BRACKET
              if r[pos]=='(':
                brkcount += 1
                # PARSE THE DATA
                data = string.replace(r[pos+1:string.find(r,')',pos)],'AND','')
                data = string.split(data)
                # FILL THE RESTRAINT DICT
                for i in range(len(data)):
                  if i%2==0:
                    restr.data[group][data[i][:4]].append(data[i+1])
                pos = string.find(r,')',pos)
              # OTHERWISE READ NEXT CHARACTER
              else:
                # LOWER THE BRACKET COUNTER
                if r[pos]==')':
                  brkcount -=1
                  # IF THE FIRST GROUP IS FINISHED
                  # GO TO THE SECOND
                  if brkcount == 0:
                    group += 1
                pos+=1
            # PARSE THE DISTANCES
            anglelist = string.split(r[string.rfind(r,')')+1:])
            restr.c = float(anglelist[0])
            restr.angle = float(anglelist[1])
            restr.range = float(anglelist[2])
            restr.ed = int(anglelist[3])
            # STORE THE RESTRAINT
            self.restraintlist.append(restr)
    #print "Read %i restraints."%len(self.restraintlist)

  # CLEAN RESTRAINTLIST
  # ===================
  # REMOVE DOUBLES FROM LIST
  def clean(self):
    # CHECK FOR DOUBLE ASSIGNMENTS, WE KEEP
    # THE TIGHEST RESTRAINT AS THE FINAL ONE
    tmplist,strlist,doubles,rejects = [],[],[],[]
    for restraint in self.restraintlist:
      rejected = 0
      if restraint.type=="DIST":
        # RAW CHECK FOR SELF REFERENCE
        if str(restraint.data[0])==str(restraint.data[1]):
          rejects.append(restraint)
          rejected=1
        # RAW CHECK FOR RESTRAINTS BETWEEN PROTONS
        # CONNECTED TO THE SAME ATOM
        elif len(restraint.data[0]["RESI"])==1:
          if restraint.data[0]["RESI"]==restraint.data[1]["RESI"]:
            name0 = restraint.data[0]["NAME"][0]
            name1 = restraint.data[1]["NAME"][0]
            if len(name0)<=2 and len(name1)<=2:
              if name0==name1:
                rejects.append(restraint)
                rejected = 1
            elif len(name0)>=2 and len(name1)>=2:
              if name0[:-1]==name1[:-1]:
                rejects.append(restraint)
                rejected=1
        # REMOVE DOUBLES FROM SELECTION
        for i in range(2):
          d = restraint.data[i]
          list = []
          if len(restraint.data[i]["RESI"])>0:
            d = restraint.data[i]
            j = 0
            while j < len(d["RESI"]):
              # SEE IF WE HAVE A SEGI
              if len(d["SEGI"])==len(d["RESI"]): segi=d["SEGI"][j]
              else: segi = ""
              # SEE IF WE HAVE A RESN
              if len(d["RESN"])==len(d["RESI"]): resn=d["RESN"][j]
              else: resn = ""
              # SEE IF WE HAVE A ATOM
              if len(d["ATOM"])==len(d["RESI"]): atom=d["ATOM"][j]
              else: atom = ""
              # JOIN SEGI, NAME AND RESI
              check = str((segi,d["RESI"][j],d["NAME"][j]))
              if check in list:
                del d["RESI"][j]
                del d["NAME"][j]
                if segi!="": del d["SEGI"][j]
                if resn!="": del d["RESN"][j]
                if atom!="": del d["ATOM"][j]
              else:
                list.append(check)
                j+=1
      # IF DOESN'T EXIST ADD IT TO THE RESTRAINTLIST
      if str(restraint) not in strlist and not rejected:
        tmplist.append(restraint)
        strlist.append(str(restraint))
      # OTHERWISE WE KEEP THE TIGHEST ONE
      elif not rejected:
        rindex = tmplist.index(str(restraint))
        doubles.append(restraint)
        if tmplist[rindex]>restraint:
          del doubles[-1]
          doubles.append(tmplist[rindex])
          del tmplist[rindex]
          del strlist[rindex]
          tmplist.append(restraint)
          strlist.append(str(restraint))
    self.restraintlist = tmplist
    self.doubles = doubles
    self.rejected = rejects
    #print "Done."

  # RENUMBER RESTRAINTLIST
  # ======================
  # RENUMBER RESTRAINT WITH THE PROVIDED OFFSET
  def renumber(self,offset):
    for restraint in self.restraintlist:
      for i in range(2):
        for j in range(len(restraint.data[i]["RESI"])):
          restraint.data[i]["RESI"][j]+=offset

  # WRITE RESTRAINT
  # =================
  # WRITE A RESTRAINT TO FILE
  def write(self,restraint):
    # HANDLE NOE TYPE RESTRAINTS
    if self.type == 'DIST':
      # HANDLE THE XPLOR TYPE
      if self.format == 'XPLOR':
        self.file.write("%s\n"%restraint.format(self.format))
    # HANDLE DIHEDRAL TYPE RESTRAINTS
    if self.type == 'DIHE':
      # HANDLE THE XPLOR TYPE
      if self.format == 'XPLOR':
        self.file.write("%s\n"%restraint.format(self.format))
    self.file.flush()

  # WRITE COMMENT
  # =============
  # ADD COMMENT TO RESTRAINT FILE
  def comment(self,comment):
    # HANDLE XPLOR
    if self.format == 'XPLOR':
      self.file.write("! %s\n"%comment)
    self.file.flush()

  # WRITE MULTIPLE RESTRAINTS
  # =========================
  # WRITE MULTIPLE RESTRAINTS TO FILE
  def mwrite(self,restraintlist):
    # CYCLE THE LIST
    for restraint in restraintlist:
      self.write(restraint)

  # CLOSE FILE
  # ==========
  # CLOSE THE RESTRAINT FILE
  def close(self):
    self.file.close()

#  ======================================================================
#    Q U E E N B A S E   C L A S S
#  ======================================================================
class queenbase:
  """
  A base class for a QUEEN project.
  Create a class instance by giving an optional path and a name of a project.
  """
  def __init__(self, nmvconf, project, path=None, numproc=1, myid=0 ):

    if not path:
        self.path        = nmvconf["Q_PROJECT"]
    else:
        self.path        = path
    #end if
    self.project         = project
    self.nmvconf         = nmvconf

    self.projectpath     = os.path.join(self.path,self.project)
    self.logpath         = os.path.join(self.projectpath,nmvconf["Q_LOG"])
    self.sequence        = os.path.join(self.projectpath,nmvconf["Q_SEQ"])
    self.seqfile         = os.path.join(self.projectpath,nmvconf["Q_SEQ"])
    self.psffile         = os.path.join(self.projectpath,nmvconf["Q_PSF"])
    self.temfile         = os.path.join(self.projectpath,nmvconf["Q_TEMPLATE"])
    self.table           = os.path.join(self.projectpath,nmvconf["Q_DATATBL"])
    self.dataset         = os.path.join(self.projectpath,nmvconf["Q_DATASET"])
    self.pdb             = os.path.join(self.projectpath,nmvconf["Q_PDB"])
    self.outputpath      = os.path.join(self.projectpath,nmvconf["Q_OUTPUT"])

    self.display_error   = 1
    self.display_warning = 1
    self.display_debug   = 1
    self.errorflag       = 0

    self.numproc         = numproc
    self.myid            = myid
  #end def

  def exists(self):
      """
       Return True if projectpath exists.
      """
      return os.path.exists(self.projectpath)
  #end def

  def createproject(self, overwrite=False):
      """
      Create project tree.
      Optionally overwrite existing data

      """

      if self.exists() and not overwrite:
          error('queenbase.createproject: project directory already exists; use overwrite flag')
      #end if

      print "==> Creating QUEEN project directory tree at %s" % (self.projectpath)
      # CREATE THE PROJECT DIR
      if not os.path.exists(self.projectpath):
          os.makedirs(self.projectpath)

      # CREATE THE NECESSARY SUBDIRS
      for key in ["Q_SEQUENCE","Q_RESTRAINTS","Q_DATASETS","Q_OUTPUT","Q_LOG","Q_PDB"]:
          subpath = os.path.join(self.projectpath, os.path.dirname(self.nmvconf[key]))
          #print '>', key, subpath
          if not os.path.exists(subpath):
              os.makedirs(subpath)
          #end if
      #end for
  #end def

  def error(self):
    pass

  def warning(self):
    pass

  def debug(self):
    pass

  def halt(self):
    pass

  def plot(self):
    pass

  def clear(self):
    # FREE MEMORY ALLOCATED IN NMV MODULE
    nmv.free_memory()
    os.remove(self.dmtx)

  def calcmtx(self,xplr,restraints,averaging='sum'):
    self.dmtx = os.path.join(self.logpath,'d_%i.mtx'%os.getpid())
    # INITIALIZE XPLOR
    xplrs = xplor_script(xplr.path,self.logpath)
    # BUILD SCRIPT
    xplrs.write("structure\n @%s\nend"%xplr.psf)
    xplrs.write("evaluate ($par_nonbonded=PROLSQ)")
    xplrs.write("parameter\n @%s\nend"%xplr.parameter)
    # ECHO CAN BE HANDY FOR DEBUGGING, BUT LET'S
    # LEAVE IT OFF FOR NOW
    xplrs.write("set echo on message on end")
    # FORMAT THE RESTRAINT FILE
    if type(restraints)==types.DictType:
      xplrs.write(xplor_formatdict(restraints,averaging))
    elif type(restraints)==types.ListType:
      xplrs.write(xplor_formatlist(restraints,averaging))
    # READ TEMPLATE FOR PSEUDOATOM CORRECTIONS
    xplrs.write("coord disp=refe @%s"%xplr.template)
    # SET FLAGE
    xplrs.write("flags")
    xplrs.write("  exclude * include bond angle improper vdw noe cdih")
    xplrs.write("end")
    # DO DG
    xplrs.write("mmdg")
    xplrs.write("  refe=para")
    xplrs.write("  shortest-path-algorithm=auto")
    xplrs.write("  writebounds=%s"%self.dmtx)
    xplrs.write("end")
    xplrs.submit()

  def calcunc(self):
    # READ MATRIX USING NMV MODULE
    nmv.xplor_read(self.dmtx)
    # CALCULATE UNCERTAINTY USING NMV MODULE
    unc = nmv.total_uncertainty()
    self.errorflag = nmv.cvar.eflag
    return unc

  def uncertainty(self,xplr,restraints):
    # CALCULATE MATRIX
    self.calcmtx(xplr,restraints)
    # CALCULATE UNCERTAINTY
    unc = self.calcunc()
    # CLEAR MEMORY
    self.clear()
    # RETURN UNCERTAINTY
    return unc

  def rmsde(self,xplr,restraints):
    # CALCULATE MATRIX
    self.calcmtx(xplr,restraints)
    # CALCULATE UNCERTAINTY
    nmv.xplor_read(self.dmtx)
    unc = nmv.total_rmsde()
    # CLEAR MEMORY
    self.clear()
    # RETURN UNCERTAINTY
    return unc

  def atom_uncertainties(self,atomnumbers,xplr,restraints):
    # CALCULATE MATRIX
    self.calcmtx(xplr,restraints)
    # CALCULATE UNCERTAINTY
    nmv.xplor_read(self.dmtx)
    unc = []
    for atomnumber in atomnumbers:
      unc.append(nmv.atom_uncertainty(atomnumber-1))
    self.errorflag = nmv.cvar.eflag
    # CLEAR MEMORY
    self.clear()
    # RETURN UNCERTAINTY
    return unc

  def getmatrix(self,xplr,matrix,restraints=[]):
    # CALCULATE MATRIX
    self.calcmtx(xplr,restraints)
    # COPY MATRIX
    shutil.copy(self.dmtx,matrix)
    # CLEAR MEMORY
    self.clear()
  #end def
#end class


class ExampleQueen( queenbase ):

    def __init__(self, nmvconf ):
        nmvconf["Q_PROJECT"]=nmvconf["Q_PATH"]
        queenbase.__init__( self, nmvconf, project='example')
    #end def

    def createproject(self, overwrite=False):
        """
        Subclass to prevent creation of the Example directories
        """
        error('ExampleQueen.createproject: not allowed for example project')
    #end def
#end class

