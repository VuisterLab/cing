#@PydevCodeAnalysisIgnore
#!/usr/bin/env python

import string,os,sys,cPickle,math,socket,time,shutil,copy,random,glob,fnmatch,smtplib,types,base64

# TODO
# - check the pdb_bfactor section!
# - finish pdb_resample ...

debugflag = 1

# *********************************************************************
# Type nmr_valibase.py to get a summary of NMR_VALIBASE can do for you!
# *********************************************************************

# MY MACHINE
mymachines = ["cmbipc58","cmbipc59","sander","cmbi14.cmbi.ru.nl"]

# LIST OF HOSTNAMES IN THE OCTOPUS CLUSTER
octopus_nodes = ["octopus",
                 "bigbird",
                 "node02.cmbi-octopus.nl",
                 "node03.cmbi-octopus.nl",
                 "node04.cmbi-octopus.nl",
                 "node05.cmbi-octopus.nl",
                 "node06.cmbi-octopus.nl",
                 "node07.cmbi-octopus.nl"]

# LIST OF HOSTNAMES IN THE NMR CLUSTER
nmr_nodes =     ["beoclus",
                 "beo-01",
                 "beo-02",
                 "beo-03",
                 "beo-04",
                 "beo-05",
                 "beo-06",
                 "beo-07",
                 "beo-08",
                 "beo-09"]

# MACHINE SPECIFIC STUFF
if socket.gethostname() in mymachines:
  sys.path += [os.path.join(sys.path[0],'tarfile')]
  import nmv, pdb_file, tarfile #, pypar
  # SET NUMBER OF PROCESSORS AND PROCESSOR ID FOR PARALLEL EXECUTION
  numproc = 1 #pypar.size()
  myid = 0 #pypar.rank()
# CHECK IF WE ARE ON ONE OF THE CLUSTER NODES
elif socket.gethostname() in octopus_nodes or socket.gethostname() in nmr_nodes:
  sys.path += [os.path.join(sys.path[0],'nmv'),
               os.path.join(sys.path[0],'pdb_file'),
               os.path.join(sys.path[0],'tarfile'),
               os.path.join(sys.path[0],'pypar')]
  import nmv, pdb_file, tarfile #,pypar
  # SET NUMBER OF PROCESSORS AND PROCESSOR ID FOR PARALLEL EXECUTION
  numproc = 1 #pypar.size()
  myid = 0 #pypar.rank()
# ON ANY OTHER SYSTEM
else:
  numproc=1
  myid=0

# THE TEXT HEADER
def txt_header():
  print"**********************************************************"
  print"*                                                        *"
  print"*               N M R _ V A L I B A S E                  *"
  print"*                                                        *"
  print"**********************************************************"
  print"*        Written in 2001-2004 by Sander Nabuurs          *"
  print"* CMBI,Center for Molecular and Biomolecular Informatics *"
  print"*        University of Nijmegen, The Netherlands         *"
  print"**********************************************************"
  print"*                s.nabuurs@cmbi.kun.nl                   *"
  print"**********************************************************"
  print""


#  ======================================================================
#                     G L O B A L   V A R I A B L E S
#  ======================================================================

# WHAT IF MAXIMUM NUMBER OF RESIDUES
wifmaxaa=6000


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
#    C P I C K L E   F U N C T I O N   G R O U P
#  ======================================================================

# CPICKLE VARIABLE
# ================
def cpi_dump(var,file):
  dump = open(file,'w')
  cPickle.dump(var,dump)
  dump.close()


# LOAD CPICKLED VARIABLE
# ======================
def cpi_load(file):
  dump = open(file,'r')
  var = cPickle.load(dump)
  dump.close()
  return var

#  ======================================================================
#    X E A S Y   F U N C T I O N   G R O U P
#  ======================================================================

# DEASSIGN THE PEAKS
# ==================
# DEASSIGN THE PEAKS IN AN XEASY PEAK FILE
def xeasy_deassignpeaks(peaksin,peaksout):
  print "Deassigning XEASY peak file:\n%s"%peaksin
  # READ INFILE
  content = open(peaksin,'r').readlines()
  # OPEN OUTFILE
  output  = open(peaksout,'w')
  for line in content:
    if line[0]=='#':
      output.write(line)
    else:
      nline = "%s    0    0    0 %s"%(line[:67],line[83:])
      output.write(nline)
  output.close()
  print "Wrote deassigned XEASY peak file:\n%s"%peaksout


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
#    X M L   P A R S E R   C L A S S
#  ======================================================================

"""
Borrowed from wxPython XML tree demo and modified.
SN: Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/149368.
"""

class Element:
  'A parsed XML element'
  def __init__(self,name,attributes):
    from xml.parsers import expat
    'Element constructor'
    # The element's tag name
    self.name = name
    # The element's attribute dictionary
    self.attributes = attributes
    # The element's cdata
    self.cdata = ''
    # The element's child element list (sequence)
    self.children = []

  def AddChild(self,element):
    'Add a reference to a child element'
    self.children.append(element)

  def getAttribute(self,key):
    'Get an attribute value'
    return self.attributes.get(key)

  def getData(self):
    'Get the cdata'
    return self.cdata

  def getElements(self,name=''):
    'Get a list of child elements'
    #If no tag name is specified, return the all children
    if not name:
      return self.children
    else:
      # else return only those children with a matching tag name
      elements = []
      for element in self.children:
        if element.name == name:
          elements.append(element)
      return elements

class Xml2Obj:
  'XML to Object'
  def __init__(self):
    self.root = None
    self.nodeStack = []

  def StartElement(self,name,attributes):
    'SAX start element even handler'
    # Instantiate an Element object
    element = Element(name.encode(),attributes)
    # Push element onto the stack and make it a child of parent
    if len(self.nodeStack) > 0:
      parent = self.nodeStack[-1]
      parent.AddChild(element)
    else:
      self.root = element
    self.nodeStack.append(element)

  def EndElement(self,name):
    'SAX end element event handler'
    self.nodeStack = self.nodeStack[:-1]

  def CharacterData(self,data):
    'SAX character data event handler'
    if string.strip(data):
      data = data.encode()
      element = self.nodeStack[-1]
      element.cdata += data
      return

  def Parse(self,filename):
    # Create a SAX parser
    from xml.parsers import expat
    Parser = expat.ParserCreate()
    # SAX event handlers
    Parser.StartElementHandler = self.StartElement
    Parser.EndElementHandler = self.EndElement
    Parser.CharacterDataHandler = self.CharacterData
    # Parse the XML File
    ParserStatus = Parser.Parse(open(filename,'r').read(), 1)
    return self.root



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
#    D A T A B A S E   C L A S S
#  ======================================================================

class data_base:
  """
  USAGE:
  - Create a class instance giving the filename of the database in parentheses
  - Instance.error contains an error description if something went wrong
  - Instance.save() saves the current database back to disc
  """

  # OPEN DATABASE
  # =============
  # THE DATABASE FILE IS PARSED AND STORED AS A LIST OF DICTIONARIES
  def __init__(self,dbfilename,errorfunc=None,fieldlist=None):
    self.error=None
    self.errorfunc=errorfunc
    self.filename=dbfilename
    if (not os.path.exists(dbfilename)):
      # NEW DATABASE
      if (fieldlist==None): self.raiseerror("__init__: Database not found")
      db=[string.join(fieldlist,'|')]
    else:
      # LOAD EXISTING DATABASE
      db=open(dbfilename).readlines()
    self.record=[]
    self.key=string.split(string.strip(db[0]),'|')
    self.keys=len(self.key)
    for line in db[1:]:
      line=string.strip(line)
      if (len(line)):
        line=string.split(line,'|')
        if (len(line)!=self.keys): self.raiseerror("__init__: Number of fields does not match")
        record={}
        for i in range(self.keys):
          record[self.key[i]]=line[i]
        self.record.append(record)
    self.records=len(self.record)

  # GET A RECORD STRING
  # ===================
  def recordstring(self,rec):
    recordstring=""
    for j in range(self.keys):
      recordstring=recordstring+self.record[rec][self.key[j]]+'|'
    return(recordstring[:-1])

  # PRINT DATABASE
  # ==============
  def __repr__(self):
    str="Database: "
    if (self.filename!=None): str=str+self.filename+"\n\n"
    else: str=str+"nameless\n\n"
    keystr=string.join(self.key,'|')
    str=str+keystr+"\n"+"="*len(keystr)+"\n"
    for i in range(self.records):
      str=str+self.recordstring(i)+"\n"
    return(str)

  # DELETE A RECORD
  # ===============
  def delrecord(self,rec):
    del self.record[rec]
    self.records=self.records-1

  # INSERT A KEY
  # ============
  def insertkey(self,pos,key):
    self.key.insert(pos,key)
    self.keys=len(self.key)
    for i in range(self.records):
      self.record[i][key]=""

  # SAVE DATABASE
  # =============
  # THE LIST OF DICTIONARIES IS CONVERTED BACK TO AN ASCII FILE
  def save(self,filename=None):
    if (filename==None): filename=self.filename
    dbfile=open(filename,"w")
    keystring=""
    for i in range(self.keys):
      keystring=keystring+self.key[i]+'|'
    dbfile.write(keystring[:-1]+'\n')
    for i in range(self.records):
      dbfile.write(self.recordstring(i)+'\n')
    dbfile.close()

  # FIND THE RECORD WITH A GIVEN KEY VALUE
  # ======================================
  def recordwithkey(self,key,value):
    for i in range(self.records):
      record=self.record[i]
      if (record.get(key)==value): return(record)
    return(None)

  # CLEAN A STRING FOR DATABASE
  # ===========================
  def cleaned(self,str):
    str=string.replace(str,"\n","")
    str=string.replace(str,"\r","")
    str=string.replace(str,"|"," ")
    return(str)

  # ADD RECORD WITH LIST OF VALUES
  # ==============================
  def addvaluelist(self,valuelist):
    record={}
    if (len(valuelist)!=self.keys): self.raiseerror("addvaluelist: Number of list elements and database keys does not match")
    for i in range(self.keys):
      record[self.key[i]]=self.cleaned(valuelist[i])
    self.record.append(record)
    self.records=len(self.record)

  # GET LIST OF VALUES IN A RECORD
  # ==============================
  def valuelist(self,record):
    valuelist=[]
    for i in range(self.keys):
      valuelist.append(record[self.key[i]])
    return(valuelist)

  # GET LIST OF VALUES FOR A KEY
  # ============================
  def valuesforkey(self,key):
    valuelist=[]
    for i in range(self.records):
      valuelist.append(self.record[i].get(key))
    return(valuelist)

  # FIND THE RECORD WITH GIVEN KEY VALUES
  # =====================================
  def recordwithkeys(self,keylist,valuelist):
    for i in range(self.records):
      record=self.record[i]
      for j in range(len(keylist)):
        key=keylist[j]
        if (not record.has_key(key) or record[key]!=valuelist[j]): break
      else:
        # FOUND
        return(record)
    return(None)

  # RAISE AN ERROR
  # ==============
  # CALLS THE ERRORFUNCTION PROVIDED BY THE USER WITH THE GIVEN STRING
  def raiseerror(self,errormsg):
    errormsg="data_base."+errormsg
    self.error=errormsg
    if (self.errorfunc!=None): apply(self.errorfunc,[errormsg])
    return


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
    - xydx   : same as xy but with error on x axis
    - xydydy : same as xy but with two errors on y axis
    - xydxdy : same as xy but with error on x and y axes
    - xysize : same ax xy but symbol size is variable
  -
  """
  def __init__(self,path,type,access,errorfunc=None):
    self.error=None
    self.errorfunc=errorfunc
    self.path=path
    self.type=type
    # XMGRACE COMMENT MARKERS
    self.comments = ['#','@','&']
    # IF DESIRED, OPEN FILE
    if access=='w':
      self.file = open(path,'w')
    elif access=='a':
      self.file = open(path,'a')
    elif access=='r':
      self.file = open(path,'r')
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
    if self.type=='xydy' or self.type=='xydx':
      if len(data)==3:
        self.file.write("%10e %10e %10e\n"%(data[0],data[1],data[2]))
      if len(data)==4:
        self.file.write("%10e %10e %10e \"%s\"\n"%(data[0],data[1],data[2],data[3]))
    if self.type=='xydxdy' or self.type=='xydydy':
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
  def output(self,format='ps',parameter=None):
    # AUTOGENERATE FILE NAME
    plotfile = "%s.%s"%(os.path.splitext(self.path)[0],format)
    # GENERATE THE PLOT
    if format=='ps':
      if parameter==None:
        os.popen("gracebat -printfile %s %s"%(plotfile,self.path))
      else:
        os.popen("gracebat -autoscale none -printfile %s -param %s %s"%(plotfile,parameter,self.path))

  # READ DATA
  # =========
  # READ THE DATA IN THE XMGRACE FILE AND RETURN IT AS A
  # LIST OF VALUE PAIRS
  def read(self):
    self.data = []
    content = self.file.readlines()
    for line in content:
      if line[0] not in self.comments:
        line = line.split()
        if self.type=='xy' or self.type=='bar':
          self.data.append([float(line[0]),float(line[1])])
        if self.type=='xydy' or self.type=='xyz':
          self.data.append([float(line[0]),float(line[1]),float(line[2])])
        if self.type=='xydxdy':
          self.data.append([float(line[0]),float(line[1]),float(line[2]),float(line[3])])
        if self.type=='xysize':
          self.data.append([float(line[0]),float(line[1]),float(line[2])])

  # CLOSE
  # =====
  # CLOSE THE FILE
  def close(self):
    self.file.close()



#  ======================================================================
#    B L A S T   F U N C T I O N   G R O U P
#  ======================================================================

# PARSE BLAST FILE
# ================
# INPUT IS THE CONTENT OF A BLAST OUTPUT FILE
# FROM .readlines()
def blast_parse_pdb(blastfilecontents):
  content = blastfilecontents
  # PARSE BLAST OUTPUT
  hits = {}
  for line in content:
    if line[0]=='>':
      pdbs = []
    if len(line)>4 and line[4]=='|':
      pdbs.append(line[5:11])
    if line[:11]==' Identities':
      line = line.split()
      perc = int(line[3][1:-3])
      for pdb in pdbs:
        hits[pdb.replace(' ','_')]=perc
  return hits

# PARSE BLAST FILE
# ================
# INPUT IS THE CONTENT OF A BLAST OUTPUT FILE
# FROM .readlines()
def blast_parse_refdb(blastfilecontents):
  content = blastfilecontents
  # PARSE BLAST OUTPUT
  hits = {}
  for line in content:
    if line[0]=='>':
      line = line.split()
      name = line[0][1:]
    if line[:11]==' Identities':
      line = line.split()
      perc = int(line[3][1:-3])
      hits[name]=perc
  return hits


#  ======================================================================
#    S E Q U E N C E   F U N C T I O N   G R O U P
#  ======================================================================

# BLAST SEQUENCE
# ==============
def seq_blastrefdb(blast,sequence,blastdb):
  # WRITE SEQUENCE TO FASTA
  fastaf = dsc_tmpfile()
  seq_writefasta(sequence,'',fastaf)
  # RUN BLAST
  cmd = "%s -p blastp -P 1 -d %s -i %s"%(blast,
                                         blastdb,
                                         fastaf)
  log = os.popen(cmd)
  content = log.readlines()
  # PARSE OUTPUT
  hits = blast_parse_refdb(content)
  # CLEAN UP
  os.remove(fastaf)
  return hits

# BLAST SEQUENCE AGAINST PDB
# ==========================
# RETURNS LIST OF PDB ENTRIES WITH A SEQUENCE IDENTITY
# HIGHER THEN PROVIDED CUTOFF
def seq_netblastpdb(sequence,outputfile=None,blastfile=None):
  # WRITE SEQUENCE TO FASTA
  fastaf = dsc_tmpfile()
  seq_writefasta(sequence,'',fastaf)
  # READ INPUT FILE OR RUN BLAST
  if not blastfile:
    # RUN BLAST
    cmd = '%s -p blastp -P 1 -d pdb -i %s'%(nmvconf["NETBLAST_RUN"],
                                            fastaf)
    # RUN BLAST
    log = os.popen(cmd)
    content = log.readlines()
  # READ INPUTFILE
  else:
    content = open(blastfile,'r').readlines()
  # WRITE OUTPUT FILE
  if outputfile:
    file = open(outputfile,'w')
    for line in content:
      file.write(line)
    file.close()
  # PARSE OUTPUT
  hits = blast_parse_pdb(content)
  # CLEAN UP
  os.remove(fastaf)
  return hits

# WRITE A PIR SEQUENCE FILE
# =========================
# RETURNS OK/ERR
def seq_writepir(sequence,header,seqfilename,secstr=None):
  try: seqfile=open(seqfilename,"w")
  except:
    error("seq_writepir: PIR sequence file %s could not be written" % seqfilename)
    return(1)
  seqfile.write(">P1;"+header+"\n\n")
  sequence=sequence+'*'
  if (secstr!=None):
    secstr=string.upper(secstr)
    for i in range(len(secstr)):
      secstr=secstr[:i]+dssp_tophd(secstr[i])+secstr[i+1:]
    secstr=string.lower(string.replace(secstr," ","c"))
    secstr=secstr+"*"
    if (len(secstr)!=len(sequence)):
      error("seq_writepir: Sequence and secondary structure have different lengths")
  while (len(sequence)):
    l=min(40,len(sequence))
    seqfile.write(sequence[:l]+"\n")
    sequence=sequence[l:]
    if (secstr!=None):
      seqfile.write(string.lower(secstr[:l])+"\n")
      secstr=secstr[l:]
  seqfile.close()
  return(0)

# WRITE A FASTA SEQUENCE FILE
# ===========================
# RETURNS OK/ERR
def seq_writefasta(sequence,header,seqfilename):
  try: seqfile=open(seqfilename,"w")
  except:
    error("FASTA sequence file %s could not be written" % seqfilename)
    return(1)
  seqfile.write(">"+header+"\n")
  seqfile.write(sequence+"\n")
  seqfile.close()
  return(0)

# READ A FASTA SEQUENCE FILE
# ==========================
# RETURNS A LIST OF [ID,Sequence,SecStr] LISTS.
# SecStr IS None IF THE FASTA FILE DOES NOT CONTAIN SECONDARY STRUCTURE.
def seq_readfasta(seqfilename):
  try: seq=open(seqfilename,"r").readlines()
  except: return("FASTA file %s could not be opened" % seqfilename)
  seqlist=[]
  i=0
  while (i<len(seq)):
    line=seq[i]
    if (line[0]=='>'):
      # GET ID
      record=[string.strip(line[1:])]
      if (record[0][-1]==';'): record[0]=record[0][:-1]
      # GET SEQUENCE AND SECSTR
      sequence=""
      secstr=""
      i=i+1
      while (i<len(seq) and seq[i][0]!='>'):
        line=string.strip(seq[i])
        if (len(line)):
          if (line[0] in string.uppercase): sequence=sequence+line
          else: secstr=secstr+line
        i=i+1
      seqlist.append(record+[sequence,string.upper(secstr)])
    else: i=i+1
  return(seqlist)

# READ A PIR SEQUENCE FILE
# ========================
# RETURNS A LIST OF [ID,Sequence,SecStr] LISTS.
# SecStr IS None IF THE PIR FILE DOES NOT CONTAIN SECONDARY STRUCTURE.
def seq_readpir(seqfilename):
  try: seq=open(seqfilename,"r").readlines()
  except: return("PIR file %s could not be opened" % seqfilename)
  seqlist=[]
  i=0
  while (i<len(seq)):
    line=seq[i]
    if (line[0]=='>'):
      # GET ID
      if (line[1:4]!="P1;"): return("No 'P1;' found after '>' in PIR file "+seqfilename)
      record=[string.strip(line[4:])]
      # GET SEQUENCE AND SECSTR
      sequence=""
      secstr=""
      i=i+1
      while (i<len(seq) and seq[i][0]!='>'):
        line=string.strip(seq[i])
        if (len(line)):
          if (line[0] in string.uppercase+"-"): sequence=sequence+line
          else: secstr=secstr+line
        i=i+1
      if ((sequence!="" and sequence[-1]!='*') or (secstr!="" and secstr[-1]!='*')):
        print "Sequence:",sequence
        print "SecStr:",secstr
        return("Terminal '*' missing in PIR file "+seqfilename)
      seqlist.append(record+[sequence[:-1],string.upper(secstr)[:-1]])
    else: i=i+1
  return(seqlist)

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

# CONVERT COR
# ===========
# CONVERT DYANA COR FILES TO PDB FORMAT
def pdb_cor2pdb(corfile,pdbfile):
  print "Converting CYANA DG file to PDB file."
  # READ CONTENT
  content = open(corfile,'r').readlines()
  # WRITE OUTPUT
  output  = open(pdbfile,'w')
  for i in range(3):
    output.write("REMARK %s"%content[i])
  atcnt,cnt = 1,1
  output.write("MODEL %i\n"%cnt)
  # SKIP COMMENT LINES
  content  = content[3:]
  # STORE THE FIRST RESIDUE
  currentres,lastres = None,None
  for line in content:
    if 'Q' not in line:
      line = line.split()
      currentres = int(line[2])
      if currentres < lastres:
        cnt += 1
        output.write("ENDMDL\nMODEL %i\n"%cnt)
        atcnt=1
      atname = line[1]
      if len(atname) < 4: atname = " %s"%atname.ljust(3)
      s = "%5s %4i %3s %3s  %4i    %8.3f%8.3f%8.3f\n"%("ATOM".ljust(6),
                                                       atcnt,
                                                       atname,
                                                       line[3],
                                                       int(line[2]),
                                                       float(line[4]),
                                                       float(line[5]),
                                                       float(line[6]))
      atcnt+=1
      output.write(s)
      lastres = currentres


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

# PDB2FASTA
# =========
# EXTRACT SEQUENCE FROM PDBFILE AND WRITE IT TO FASTA FILE
# FORMAT CAN BE 'pdb' OR 'xplor'
def pdb_pdb2fasta(pdbfile,fastafile,format='pdb'):
  print "Reading sequence from PDB file",
  if format=='xplor': print "(XPLOR format)."
  else: print "(PDB format)."
  pdb = pdb_file.Structure(pdbfile)
  seqfile = open(fastafile,'w')
  rcount = 0
  for chain in pdb.peptide_chains:
    if format != 'xplor':
      id = chain.chain_id
    else:
      id = chain.segment_id
    seqfile.write("> %s %s\n"%(pdbfile,id))
    rcount += len(chain.sequence1())
    for res in chain.sequence1():
      seqfile.write("%s"%res)
    seqfile.write("\n")
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
          if eflag: prot.append(['HISE','',residue.number])
          if dflag: prot.append(['HISD','',residue.number])
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
#    P D B   F I L E   F U N C T I O N   G R O U P   P R I V A T E
#  ======================================================================

# STRUCTURAL ANISOTROPY
# =====================
# DETERMINE PDB ANISOTROPY USING WHATIF
# PDBFILE CAN SINGLE ENTRY OR LIST OF ENTRIES
def pdb_anisotropy(pdb,whatifpath):
  pdblist,anisolist = [], []
  # CHECK INPUT
  if type(pdb)==types.ListType:
    pdblist=pdb
  else:
    pdblist = [pdb]
  # DEFINE LOGFILE
  log = os.path.join(nmvconf["TMP"],'wiflog_%i.dat'%os.getpid())
  # CYCLE THE LIST
  for pdb in pdblist:
    models = pdb_models(pdb)
    # INITALIZE WHATIF SCRIPT
    script = wif_script(whatifpath)
    script.write("GETMOL %s"%pdb)
    script.write("pdb")
    script.write("1000")
    script.write("N")
    for i in range(models):
      script.write("DOLOG %s.%i\n"%(log,i+1))
      script.write("%cigar")
      script.write("m%i 0"%(i+1))
      script.write("NOLOG")
    script.write("FULLSTOP Y")
    script.submit()
    for i in range(models):
      content = open("%s.%i"%(log,i+1),'r').readlines()
      sval = float(content[-2].split()[-1])
      anisolist.append(sval)
      dsc_remove("%s.%i"%(log,i+1))
  return avg_list(anisolist)[0]

# RADIUS OF GYRATION
# ==================
# CALCULATE AVG RADIUS OF GYRATION FOR A LIST OF PDB FILES
# IF getratio IS SET TO 1, THE FUNCTION WILL
# RETURN RATIO PRED/EXP
def pdb_radiusofgyration(pdbl,getratio=0):
  # CHECK TYPE
  if type(pdbl)!=types.ListType: pdbl=[pdbl]
  results = []
  prog = progress_indicator(len(pdbl))
  for el in pdbl:
    prog.increment(pdbl.index(el)+1)
    # READ THE PDBFILE
    pdb = pdb_file.Structure(el)
    # CALCULATE THE CENTROID
    xsum,ysum,zsum = 0.0,0.0,0.0
    asum, rsum = 0,0
    atomlist = []
    for chain in pdb.peptide_chains:
      for residue in chain:
        rsum += 1
        for atom in residue:
          xsum+=atom.position[0]
          ysum+=atom.position[1]
          zsum+=atom.position[2]
          asum += 1
    centroid = [xsum/asum,ysum/asum,zsum/asum]
    # CALCULATE SUM FOR RADIUS
    rgsum = 0.0
    for chain in pdb.peptide_chains:
      for residue in chain:
        for atom in residue:
          rgsum += nmr_distance(atom.position,centroid)**2
    rg = math.sqrt(rgsum/asum)
    results.append(rg)
  rg = avg_list(results)
  print "Calculated RG: %6.2f +- %5.2f."%(rg[0],rg[1])
  pred = 2.2*pow((rsum),0.38)
  print "Predicted RG : %6.2f"%(pred)
  print "Calc vs Pred : %6.2f %%"%((rg[0]/pred)*100)
  if getratio: return [(rg[0]/pred)*100,(rg[1]/rg[0])*((rg[0]/pred)*100)]
  else: return rg
  #R\sg\N-measured / R\sg\N-predicted (%)


# SYNC CHAIN NAME
# ===============
# SYNCHRONE THE CHAINNAMES IN PDB WITH THOSE IN SYNCPDB AND
# WRITE THE ADJUSTED FILE TO OUTPDB
def pdb_syncchainnames(yaspath,inpdb,outpdb,syncpdb,xplorflag=0):
  # INITIALIZE YASARA MACRO
  ysr = ysr_macro(yaspath)
  ysr.write(["ErrorExit Off",
             "LoadPDB %s"%syncpdb,
             "LoadPDB %s"%inpdb])
  # READ THE PDBFILE
  pdb = pdb_file.Structure(syncpdb)
  for chain in pdb.peptide_chains:
    if not xplorflag: id = chain.chain_id
    else: id = chain.segment_id
    if id == ' ' or id== '': id = '____'
    ysr.write(["RenameSeg Obj 2,%s"%id])
    if xplorflag: format = 'Xplor'
    else: format = 'PDB'
    ysr.write(["SavePDB Obj 2,%s,Format=%s"%(outpdb,format)])
  ysr.write("Exit")
  ysr.submit(conflag=1)

# DETERMINE B-FACTOR FROM ENSEMBLE
# ================================
# CALCULATE THE B-FACTOR FROM NMR ENSEMBLE
def pdb_bfactor(pdbfile,selection='CA'):
  # DETERMINE THE NUMBER OF MODELS
  no_models = pdb_models(pdbfile)
  # READ THE PDBFILE, ALL MODELS
  pdb = pdb_file.Structure(pdbfile,endmodel=no_models)
  coordict = {}
  # CYCLE ALL CHAINS
  for pdbchain in pdb.peptide_chains:
    chain = pdbchain.chain_id
    if not chain: chain = ' '
    if not coordict.has_key(chain):
      coordict[chain]={}
    # CYCLE ALL RESIDUES
    for residue in pdbchain:
      if not coordict[chain].has_key(residue.number):
        coordict[chain][residue.number]={}
      # CYCLE THE ATOMS
      for atom in residue:
        name = atom.name
        if not coordict[chain][residue.number].has_key(name):
          coordict[chain][residue.number][name]=[]
        # STORE THE COORDINATES
        coordict[chain][residue.number][name].append(atom["position"])
  # CALCULATE THE B-FACTOR
  blist = []
  for chain in coordict.keys():
    for residue in coordict[chain].keys():
      for atom in coordict[chain][residue].keys():
        if atom==selection:
          fl = coord_fluct(coordict[chain][residue][atom])
          b = 8*(math.pi**2)*fl/3
          blist.append(b)
          print "%s\t%s\t%5.2f"%(residue, atom, b)
  return blist

# DETERMIN S2 FROM ENSEMBLE
# =========================
# CALCULATE THE S2 ORDER PARAMETER FROM AN NMR ENSEMBLE
# METHOD OF ZHANG&BRUSCHWEILER, JACS(2002)124:12654-55
def pdb_s2(pdbfile):
  hnname = 'H'
  # DETERMINE THE NUMBER OF MODELS
  no_models = pdb_models(pdbfile)
  # READ THE PDBFILE, ALL MODELS
  pdb = pdb_file.Structure(pdbfile,endmodel=no_models)
  # A CHECK FOR THE FUTURE
  if no_models!=len(pdb.peptide_chains):
    print "It looks like this ensemble does not contain monomeric structures!"
    print "Please update the pdb_s2() function!"
  # A DICTIONAY IN WHICH WE STORE ALL COORDINATES
  # FOR FAST ACCES
  coordict = {}
  # CYCLE ALL MODELS
  for pdbchain in pdb.peptide_chains:
    # STORE THE CHAINID
    chain = pdbchain.chain_id
    if not chain: chain = ' '
    # SET UP DICTIONARY
    coordict[chain]=coordict.get(chain,{})
    # CYCLE ALL RESIDUES
    for residue in pdbchain:
      # SET UP DICTIONARY
      coordict[chain][residue.number]=coordict[chain].get(residue.number,{})
      # CYCLE THE ATOMS
      for atom in residue:
      # SET UP DICTIONARY
        coordict[chain][residue.number][atom.name]=coordict[chain][residue.number].get(atom.name,[])
        # STORE THE COORDINATES
        coordict[chain][residue.number][atom.name].append(atom["position"])
  # CYCLE MODELS
  s2dict = {}
  # WE AVERAGE S2 OVER THE NUMBER OF MODELS
  for i in range(no_models):
    # LOAD THE CHAIN
    pdbchain = pdb.peptide_chains[i]
    chain = pdbchain.chain_id
    if not chain: chain = ' '
    # CALCULATE S2 PER RESIDUE
    for residue in pdbchain:
      # THE FIRST RESIDUE CAN'T BE DONE
      if pdbchain.residues.index(residue)>0 and residue.name!='PRO':
        s2dict[residue.number] = s2dict.get(residue.number,[])
        sum = 0.0
        co=coordict[chain][residue.number-1]['O'][i]
        ch=coordict[chain][residue.number][hnname][i]
        # SUM OVER THE OTHER RESIDUE IN THE SYSTEM
        for residue2 in pdbchain:
          # EXCLUDE THE CURRENT AND PREVIOUS IN CHAIN
          if residue2.number!=residue.number and residue2.number!=residue.number-1:
            # FIND ALL HEAVY ATOMS
            for atom in residue2:
              name = atom.name
              if atom.properties["element"]!='H':
                c2=coordict[chain][residue2.number][name][i]
                # THE CONTACT MODEL!
                sum+=math.exp(-nmr_distance(co,c2))+0.8*math.exp(-nmr_distance(ch,c2))
        # THE S2 VALUE
        s2=1.0-math.tanh(2.656*sum)+0.1
        # STORE IT
        s2dict[residue.number].append(s2)
  # RETURN THE DICTIONARY
  return s2dict

# GET QUALITY FILE FROM PDB FILE
# ==============================
# USE WHATMODELBASE TO CONVERT PDB TO QUA
# TYPE CAN BE NUM OR ASCI
def pdb_getqua(pdbfile,qualityfile,type='num'):
  # GET CURRENT PATH
  cur_path = os.getcwd()
  # GET WHAT MODELBASE PATH
  wmb = nmvconf["WHAT_MODELBASE"]
  wmb_path = os.path.dirname(wmb)
  # GO TO WHATMODELBASE PATH
  os.chdir(wmb_path)
  os.system("%s -pdbtoqua -%s %s %s"%(wmb,type,pdbfile,qualityfile))
  # GET BACK TO THE ORIGINAL PATH
  os.chdir(cur_path)

# PLOT QUALITY SUMMARY FOR PDB FILES
# ==================================
# USE TWINSET TO PLOT QUALITY FOR PDB FILES
def pdb_sumcheck_global(pdblist,checklist,sumfile):
  # GET QUALITY
  checkd = pdb_check_global(pdblist,checklist)
  # GET AVERAGE QUAL
  avgd = {}
  for check in checkd.keys():
    avgd[check] = avg_list(checkd[check])
  # WRITE SUMMARY FILE
  out = open(sumfile,'w')
  out.write("Overall summary\n")
  out.write("###############\n\n")
  for check in checklist:
    out.write("%10s: %6.2f +/- %6.2f\n"%(check.ljust(10),
                                         avgd[check][0],
                                         avgd[check][1]))
  # DETAILED SUMMARY
  out.write("\n\nDetailed summary\n")
  out.write("################\n")
  out.write("\n")
  # WRITE HEADER LINE
  text = "File"
  str  = text.ljust(len(os.path.basename(pdblist[0]))+5)
  for check in checklist:
    str += "%10s"%(check.ljust(10))
  out.write("%s\n"%str)
  # WRITE TABLE
  for pdb in pdblist:
    str = os.path.basename(pdb).ljust(len(os.path.basename(pdb))+5)
    for check in checklist:
      score = "%5.2f"%(checkd[check][pdblist.index(pdb)])
      str  += "%10s"%(score.ljust(10))
    out.write("%s\n"%str)
  out.close()
  return avgd

# GET QUALITY FOR PDB FILES
# =========================
# USE TWINSET TO GET QUALITY FOR PDB FILES
def pdb_check_global(pdblist,checklist):
  # CHECK TYPES
  if type(pdblist)   != types.ListType: pdblist   = [pdblist]
  if type(checklist) != types.ListType: checklist = [checklist]
  tabfilename = dsc_tmpfile()
  # CREATE YASARA MACRO
  ysr = ysr_macro(nmvconf["YASARA_RUN"])
  for pdb in pdblist:
    ysr.write(["LoadPDB %s"%pdb])
  # STORE SCORES
  for check in checklist:
    ysr.write(["Tabulate CheckObj 1-(LastObj),%s"%(check)])
  ysr.write(["SaveTab 1,%s,Columns=1,NumFormat=%%6.2f,(LastObj)"%tabfilename])
  ysr.write(["Exit"])
  ysr.submit(conflag=2)
  # READ OUTPUT
  content = open(tabfilename,'r').readlines()
  nobjects = int(content[0].strip())
  content = content[1:]
  # QUALITY SCORES
  checkd = {}
  for i in range(len(checklist)):
    for j in range(nobjects):
      # EXTRACT SCORE
      line = i*(nobjects) + j
      score = float(content[line].strip())
      # STORE SCORE
      checkd[checklist[i]] = checkd.get(checklist[i],[]) + [score]
  return checkd

# PLOT QUALITY FOR PDB FILES
# ==========================
# USE TWINSET TO PLOT QUALITY FOR PDB FILES
def pdb_plotchecks(pdblist,checklist,basename):
  # CHECK TYPE CHECKLIST
  if type(checklist) != types.ListType: checklist = [checklist]
  # BUILD DICTIONARY
  avgcheckd = yas_checkpdbs(nmvconf["YASARA_RUN"],
                            pdblist,
                            checklist)
  # CYCLE CHECKS
  files = {}
  for check in checklist:
    plotfile = basename+"_%s.dat"%check.replace('/','-')
    files[check]=plotfile
    xmgr = graceplot(plotfile,'xydy','w')
    xmgr.writeheader()
    for i in range(len(avgcheckd['resn'])):
      if avgcheckd[check][i][0]!=-999.0:
        xmgr.write([avgcheckd['resn'][i],
                    avgcheckd[check][i][0],
                    avgcheckd[check][i][1]])
    xmgr.close()
  return files

# PLOT RMSD FOR PDB FILES
# =======================
# USE YASARA TO PLOT RMSD FOR PDB FILES
def pdb_plotrmsd(pdblist,plotname,atoms='backbone',fitflag=0):
  # BUILD LIST OF ATOMS
  if atoms == 'backbone':
    atomlist = ['CA','N','C']
  elif atoms == 'heavy':
    atomlist = ['Element !H']
  else:
    atomlist = atoms
  # DETERMINE NUMBER OF RESIDUES
  pdbf = pdb_file.Structure(pdblist[0])
  nres = 0
  residuenumbers = []
  for chain in pdbf.peptide_chains:
    nres += len(chain)
    for residue in chain:
      residuenumbers.append(residue.number)
  # DETERMINE THE PER RESIDUE RMSD SCORES
  bbrmsd, plotlist = [], []
  # BUILD LIST OF RESIDUE NUMBERS
  residues = []
  for residue in range(1,nres+1): residues.append(residue)
  # CALCULATE LIST OF RMSD MATRICES
  rmsdmtxlist = yas_rmsdmtxfast(nmvconf["YASARA_RUN"],pdblist,atomlist,
                                unit='Res',fitflag=fitflag)
  # CYCLE THE RESIDUES
  for r in residues:
    rmsdmtx = rmsdmtxlist[residues.index(r)]
    rmsdlist = []
    for i in range(len(pdblist)):
      del rmsdmtx[i][i]
      rmsdlist.append(avg_list(rmsdmtx[i],sdflag=0))
    avg = avg_list(rmsdlist)
    bbrmsd.append(avg[0])
    plotlist.append([residuenumbers[residues.index(r)],avg[0],avg[1]])
  # WRITE PLOT
  xmgr = graceplot(plotname,'xy','w')
  xmgr.writeheader()
  xmgr.mwrite(plotlist)
  xmgr.close()
  return avg_list(bbrmsd)

# GET BACKBONE NORMALITY
# ======================
def pdb_getbbc(whatifpath,pdbfile):
  # DEFINE LOGFILE
  log = dsc_tmpfile()
  # INITIALIZE WHATIF SCRIPT
  script = wif_script(whatifpath)
  script.write("GETMOL %s"%pdbfile)
  script.write("pdb")
  script.write("1000")
  script.write("n")
  script.write("check")
  script.write("dolog %s"%log)
  script.write("0")
  script.write("bbc")
  script.write("nolog")
  script.write("fullstop y")
  # RUN IT
  script.submit()
  # PARSE OUTPUT
  output = open(log,'r').readlines()
  for line in output:
    if line[:30]==' Backbone conformation Z-score':
      line = line.split(':')
      bbc = float(line[1])
      break
  # CLEAR LOG
  dsc_remove(log)
  return bbc

# GET RAMACHANDRAN PLOT Z-SCORE
# =============================
def pdb_getramazscore(whatifpath,pdbfile):
  # DEFINE LOGFILE
  log = dsc_tmpfile()
  # INITIALIZE WHATIF SCRIPT
  script = wif_script(whatifpath)
  script.write("GETMOL %s"%pdbfile)
  script.write("pdb")
  script.write("1000")
  script.write("n")
  script.write("check")
  script.write("dolog %s"%log)
  script.write("0")
  script.write("ramchk")
  script.write("nolog")
  script.write("fullstop y")
  # RUN IT
  script.submit()
  # PARSE OUTPUT
  output = open(log,'r').readlines()
  nobumps,sumline = 0,0
  for line in output:
    try:
      if line[:21]==' Ramachandran Z-score':
        line = line.split()
        zscore = float(line[-1])
    except IndexError:
      pass
  # CLEAR LOG
  dsc_remove(log)
  return zscore

# GET NUMBER OF BUMPS
# ===================
def pdb_getnobumpsper100(whatifpath,pdbfile):
  print "DEBUG"
  models = pdb_models(pdbfile)
  print "DEBUG", pdbfile
  print "DEBUG", models
  # READ PDBFILE
  pdb = pdb_file.Structure(pdbfile,endmodel=models)
  nres = 0
  for chain in pdb.peptide_chains:
    nres += len(chain)
  print "DEBUG", len(chain), len(pdb.peptide_chains)
  print "DEBUG", nres
  print "/DEBUG"
  # DEFINE LOGFILE
  log = dsc_tmpfile()
  # INITIALIZE WHATIF SCRIPT
  script = wif_script(whatifpath)
  script.write("SETWIF 593 100000")
  script.write("GETMOL %s"%pdbfile)
  script.write("pdb")
  script.write("1000")
  script.write("n")
  script.write("check")
  script.write("dolog %s"%log)
  script.write("0")
  script.write("bmpchk")
  script.write("nolog")
  script.write("fullstop y")
  # RUN IT
  script.submit()
  # PARSE OUTPUT
  output = open(log,'r').readlines()
  nobumps,sumline = 0,0
  for line in output:
    try:
      if line[77:82]=='INTRA': nobumps += 1
      elif line[:24]=='And so on for a total of':
        line = line.split()
        sumline = int(line[-2])
    except IndexError:
      pass
  # CLEAR LOG
  if sumline==0: totbumps = nobumps
  else: totbumps = sumline
  dsc_remove(log)
  b100 = (100.0/nres)*totbumps
  print "%7.2f bumps per 100 residues found."%b100
  return b100

# CHECK IF A PDBID HAS NMR RESTRAINTS AVAILABLE
# =============================================
# CONTAINS A SLEEP STATEMENT, SO WE DO NOT OVER
# LOAD THE PDB SERVER WITH MANY REQUESTS AT THE
# SAME TIME
def pdb_hasrestraints(pdbid,pdbftp):
  # HANDLE THE STRING CASE
  if type(pdbid)==types.StringType:
    pdbid=pdbid.lower()
    from ftplib import FTP
    # OPEN FTP CONNECTION
    ftp = FTP(pdbftp)
    ftp.login()
    # CHECK IF RESTRAINTS ARE AVAILABLE
    path = 'pub/pdb/data/structures/divided/nmr_restraints/'
    subpath = os.path.join(path,pdbid[1:3])
    filelist = ftp.nlst(subpath)
    if "%s.mr.Z"%pdbid in filelist:
      ftp.quit()
      time.sleep(1)
      return 1
    else:
      ftp.quit()
      time.sleep(1)
      return 0
  # HANDLE THE LIST CASE
  if type(pdbid)==types.ListType:
    from ftplib import FTP
    # OPEN FTP CONNECTION
    ftp = FTP(pdbftp)
    ftp.login()
    hasrestraints = []
    # CHECK IF RESTRAINTS ARE AVAILABLE
    path = 'pub/pdb/data/structures/divided/nmr_restraints/'
    for el in pdbid:
      el = el.lower()
      subpath = os.path.join(path,el[1:3])
      filelist = ftp.nlst(subpath)
      if "%s.mr.Z"%el in filelist:
        hasrestraints.append(el)
      print el,
      time.sleep(0.5)
    print
    ftp.quit()
    return hasrestraints


# GET PDB METHOD
# ==============
# FUNCTION TAKES A PDB ID AND A PDB FINDER INSTANCE
# AND RETURNS THE EXPERIMENTAL METHOD BY WHICH THE
# STRUCTURE WAS DETERMINED.
def pdb_method(pdbid,pdbfinder):
  # READ ENTRY IN PDBFINDER
  pdbfinder.read(pdbid)
  return pdbfinder.fieldvalue("Exp-Method")

# RESAMPLE THE PROVIDED PDB FILE
# ==============================
def pdb_resample(inpdb,psffile,restraintlist):
  # IF WE DON'T GET A LIST OF PDB FILES WE SPLIT IT
  if type(inpdb)!=types.ListType:
    # SPLIT THE PDB FILE
    outputpath = os.path.dirname(inpdb)
    tmpid = "tmp"
    yas_splitpdb2xplor(nmvconf["YASARA_RUN"],inpdb,outputpath,tmpid)
    pdblist = glob.glob(os.path.join(outputpath,"%s*"%tmpid))
  # ELSE WE JUST SET THE OUTPUT PATH
  else:
    outputpath = os.path.dirname(inpdb[0])
    pdblist = inpdb
  print "Resampling an ensemble of %i structures."%(len(pdblist))
  # WATER REFINE ALL STRUCTURES BEFORE WE START
  for pdb in pdblist:
    outpdb = pdb+'.w'
    xplor_refstruct(pdb,outpdb,psffile,restraintlist)
  # START RESAMPLING


#  ======================================================================
#    A V E R A G I N G   F U N C T I O N   G R O U P
#  ======================================================================

# AVERAGE SURFACE
# ===============
# c      = smudge factor
# cutoff = datapoint density
def avg_surface(xaxis,yaxis,xyzlist,delta=1,cutoff=1):
  xydict = {}
  for x in xaxis:
    for y in yaxis:
      sumtop,sumbot = 0,0
      for el in xyzlist:
        mult = math.exp(-((x-el[0])**2+(y-el[1])**2)/(2*(delta**2)))
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

# AVERAGE LIST FOR TIEFIGHTER
# ===========================
# SORT AND AVERAGE LIST AND RETURN TIEFIGHTER SCORES
# THE FOLLOWING KEYS ARE PRESENT IN THE RETURN DICTIONARY
# 10 - 25 - 50 - 75 -90 = percentiles
# avg, sd               = average and standard deviation
# outliers              = element < 10 and >90th percentile
def avg_list_tiefighter(list):
  # SORT LIST
  list.sort()
  dct = {}
  # DETERMINE PERCENTILES
  for el in [10,25,50,75,90]:
    dct[el] = list[int((float(el)/100)*len(list))]
  # CONSTRUCT OUTLIERS
  dct['outliers'] = list[:int((0.1*len(list)))] + list[int(0.9*len(list)):]
  # AVERAGE LIST
  avg = avg_list(list)
  dct['avg'] = avg[0]
  dct['sd']  = avg[1]
  return dct


#  ======================================================================
#    S U R F A C E   F U N C T I O N   G R O U P
#  ======================================================================

# AVERAGE SURFACE
# ===============
# AVERAGE LIST OF VALUES TO A SMOOTH SURFACE USING GAUSSIAN SMOOTHING
# INPUT DATA IS LIST OF XYZS : [[x1,y1,z1],[x2,y2,z2],....]
# DELTA                      : delta in gaussian function
# CUTOFF                     : threshold of surface level
def surf_avg(xaxis,yaxis,xyzlist,delta=1,cutoff=1):
  xydict = {}
  for x in xaxis:
    for y in yaxis:
      sumtop,sumbot = 0,0
      for el in xyzlist:
        mult = math.exp(-((x-el[0])**2+(y-el[1])**2)/(2*(delta**2)))
        sumtop += el[2]*mult
        sumbot += mult
      score = sumtop/sumbot
      xydict[x]=xydict.get(x,{})
      if sumbot < cutoff: xydict[x][y]=0.0
      else: xydict[x][y]=score
  return xydict

# FIT TO SURFACE
# ==============
def surf_fit(surfdict,datadict):
  pass

# RMSD TO SURFACE
# ===============
# XYZ SURFACE IS REPRESENTED BY A DICTIONARY: dict[x][y] = z
# VALUES ARE REPRESENTED BY A LIST          : [[x1,y1,z1],[x1,y1,z1],...]]
# AND THUS CAN HAVE MULTIPLE Z VALUES FOR ONE GRID POINT!
def surf_rmsd(surface,values):
  rmsd_sum = 0.
  rmsd_cnt = 0
  # CYCLE THE VALUES
  for value in values:
    # CALCULATE DEVIATION
    rmsd_sum += (value[2]-surface[value[0]][value[1]])**2
    rmsd_cnt += 1
  # RETURN RMSD
  return math.sqrt((1./rmsd_cnt)*rmsd_sum)

# CORRELATION WITH SURFACE
# XYZ SURFACE IS REPRESENTED BY A DICTIONARY: dict[x][y] = z
# VALUES ARE REPRESENTED BY A LIST          : [[x1,y1,z1],[x1,y1,z1],...]]
def surf_corr(surface,values):
  pred,meas = [],[]
  # CYCLE THE VALUES
  for value in values:
    pred.append(surface[value[0]][value[1]])
    meas.append(value[2])
  return list_cc(pred,meas)

# PLACE DATAPOINTS ON THE GRID
# ============================
# VALUES ARE REPRESENTED BY A LIST OF XYZs  : [[x1,y1,z1],[x1,y1,z1],...]]
def surf_placeongrid(values,xstep,ystep):
  nvalues = []
  for value in values:
    value[0] = round(value[0]/float(xstep))*xstep
    value[1] = round(value[1]/float(xstep))*xstep
    nvalues.append(value)
  return nvalues

# SELECT NON-ZERO POINTS
# ======================
# XYZ SURFACE IS REPRESENTED BY A DICTIONARY: dict[x][y] = z
# VALUES ARE REPRESENTED BY A LIST OF XYZs  : [[x1,y1,z1],[x1,y1,z1],...]]
# FUNCTION DELETE THOSE XY PAIRS FROM VALUES WHICH HAVE A
# NON-ZERO VALUE IN THE SURFACE DICTIONARY
def surf_infit(surfdict,values):
  # NEW DICTIONARY
  nonzero = []
  # CYCLE THE VALUES
  for value in values:
    if surfdict.has_key(value[0]) and surfdict[value[0]].has_key(value[1]):
      if surfdict[value[0]][value[1]]!=0:
        nonzero.append(value)
  return nonzero


#  ======================================================================
#    L I S T   F U N C T I O N   G R O U P
#  ======================================================================


# BIN LIST
# ========
# BIN A LIST OF VALUES
def list_bin(list,binsize=1,plot2screen=False):
  binsize = float(binsize)
  bins = {}
  # DETERMINE THE MIN AND MAX VALUES
  values = list
  start, end = min(values), max(values)
  start = int(start/binsize)*binsize
  end   = (int(round(end/binsize))+1)*binsize
  # DETERMINE BINS
  dist  = end - start
  nbins = int(round(dist/float(binsize)))+1
  for i in range(nbins):
    bins["%10e"%(start+i*binsize)]=0
  # CYCLE LIST AND FILL BINS
  for el in values:
    bin = int(round(el/float(binsize)))*binsize
    bins["%10e"%bin]+=1
  # PLOT TO SCREEN
  if plot2screen:
    plotheight = 50
    values = [bins[key] for key in bins]
    maxheight = float(max(values))
    keys = [float(key) for key in bins]
    keys.sort()
    for key in keys:
      plt = ''
      plt += '='*int(round(plotheight*(bins["%10e"%key]/maxheight)))
      print "%8.3f %s"%(key,plt)
  return bins

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
  try:
    cc = (n*sumxy-(sumx*sumy))/math.sqrt(((n*sumx2)-sumx**2)*((n*sumy2)-sumy**2))
    return cc
  except ZeroDivisionError:
    return None

# DETERMINE SLOPE
# ===============
# RETURN THE SLOPE AND INTERCEPT OF THE BEST FIT
# BETWEEN TWO LISTS OF NUMBERS
def list_slope(xlist,ylist):
  n = len(xlist)
  sumx,sumy,sumx2,sumy2,sumxy=.0,.0,.0,.0,.0
  for i in range(len(xlist)):
    sumx  += xlist[i]
    sumy  += ylist[i]
    sumx2 += xlist[i]**2
    sumy2 += ylist[i]**2
    sumxy += xlist[i]*ylist[i]
  try:
    slope = (n*sumxy-(sumx*sumy))/(n*sumx2-(sumx)**2)
    ic    = (sumy-slope*sumx)/n
    return [ic,slope]
  except ZeroDivisionError:
    return None

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
#    D I S C   F U N C T I O N   G R O U P
#  ======================================================================

# FILE SIZE
# ================
# GET SIZE OF FILE
def dsc_filesize(filename):
  if (not os.path.exists(filename)): return(0)
  return(os.stat(filename)[6])

# INCREASE NAME
# ==================
# INCREASE FILE NAME
def dsc_incfilename(filename):
  i=len(filename)-1
  while (i>0 and (filename[i]<'0' or filename[i]>'9')): i=i-1
  while (i>=0):
    num=ord(filename[i])
    if (num<48 or num>57): break
    num=num+1
    if (num==58): num=48
    filename=filename[:i]+chr(num)+filename[i+1:]
    if (num!=48): break
    i=i-1
  return(filename)

# CHECK SAME CONTENT
# ===============================
# CHECK IF TWO FILES ARE THE SAME
def dsc_havesamecontent(filename1,filename2):
  content1=open(filename1,"r").read()
  content2=open(filename2,"r").read()
  return (content1==content2)

# GENERATE TMP FILE NAME
# ======================
# GENERATE A TEMPORARY FILENAME
def dsc_tmpfile(tmppath=None):
  if not tmppath: tmppath=nmvconf['TMP']
  fname = os.path.join(tmppath,"tmp_%s_%i.tab"%(socket.gethostname(),
                                                os.getpid()))
  return fname

# TMP FILENAME
# =========================
# BUILD TEMPORARY FILE NAME
def dsc_tmpfilename(filename):
  dotpos=string.rfind(filename,".")
  if (dotpos==-1): filename=filename+"_tmp"
  else: filename=filename[:dotpos]+".tmp"
  return(filename+str(os.getpid()))

# PATH EXISTS
# =========================
# CHECK IF FILE(S) EXIST(S)
def dsc_pathexists(path):
  # NORMALIZE PATH, IMPORTANT TO CONVERT UNIX FORWARD TO WINDOWS BACKWARD SLASHES
  path=os.path.normpath(os.path.normcase(path))
  # CREATE LIST OF ALL THE FILENAMES IN THE DIRECTORY SPECIFIED BY PATH
  path=os.path.split(path)
  wildcard=path[1]
  path=path[0]
  if (path==""): path="."
  try: files=os.listdir(path)
  except: return(0)
  # DELETE ALL LIST ENTRIES THAT DO NOT MATCH THE WILDCARD GIVEN IN PATH
  for name in files:
    # CHECK IF FILENAME MATCHES WILDCARD
    #   INCLUDING A POSSIBLE _MOD APPENDIX (LIKE EMBL DSSP FILES)
    if (fnmatch.fnmatch(name,wildcard)): return(1)
  return(0)

# CREATE DIRECTORY LISTING INCLUDING FULL PATH NAMES
# ==================================================
def dsc_dirlist(path):
  # NORMALIZE PATH, IMPORTANT TO CONVERT UNIX FORWARD TO WINDOWS
  # BACKWARD SLASHES
  path=os.path.normpath(os.path.normcase(path))
  # CREATE LIST OF ALL THE FILENAMES IN THE DIRECTORY SPECIFIED BY PATH
  (path,wildcard)=os.path.split(path)
  if (path==""): path="."
  try: filelist=os.listdir(path)
  except: return(None)
  # CYCLE THROUGH ALL FILES AND CHECK IF THEY MATCH WILDCARD
  i=0
  while (i<len(filelist)):
    if (fnmatch.fnmatch(filelist[i],wildcard)):
      filelist[i]=os.path.join(path,filelist[i])
      if (os.path.isfile(filelist[i])):
        i=i+1
        continue
    # NO MATCH
    del filelist[i]
  filelist.sort()
  return(filelist)

# DELETE A FILE
# =============
def dsc_remove(filename):
  if (type(filename)==type([])):
    for filename2 in filename: dsc_remove(filename2)
  else:
    if (filename!=None and os.path.exists(filename)): os.remove(filename)

# DELETE DIRECTORY
# ==================================================
# DELETE AN ENTIRE DIRECTORY INCLUDING ALL THE FILES
def dsc_rmdir(path):
  while (1):
    try: shutil.rmtree(path)
    except:
      print "Directory could not be removed, most likely an NFS problem. Trying again."
      continue
    break

# COUNT FILES
# =================================
# COUNT NUMBER OF FILENAMES PRESENT
def dsc_countpresent(filenamelist):
  count=0
  for filename in filenamelist:
    if (os.path.exists(filename)): count=count+1
  return(count)

# BUILD TREE
# ==========
# BUILD A DIRECTORY TREE
def dsc_buildtree(basepath,dirlist):
  if os.path.exists(basepath):
    try:
      os.rename(basepath,basepath[:-1]+'.old')
    except OSError:
      os.system("rm -rf %s"%(basepath[:-1]+'.old'))
      os.rename(basepath,basepath[:-1]+'.old')
    os.mkdir(basepath)
  else:
    os.mkdir(basepath)
  # CREATE THE DIRECTORIES IN THE NEW DIR
  for dir in dirlist:
    os.makedirs(basepath+dir)

# REMOVE FILE EXTENSION
# =====================
def dsc_rmext(filename):
  dotpos=string.rfind(filename,".")
  if (dotpos!=-1): filename=filename[:dotpos]
  return(filename)

# GET THE MODIFICATION TIME OF A FILE
# ===================================
def dsc_modtime(filename):
  if (not os.path.exists(filename)): return(0)
  else: return(os.path.getmtime(filename))

# GET ALL MODIFICATION TIMES FOR A LIST OF FILES
# ==============================================
def dsc_modtimes(filelist):
  timelist=[]
  for filename in filelist:
    if (not os.path.exists(filename)): timelist.append(0)
    else: timelist.append(os.path.getmtime(filename))
  return(timelist)

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

# BIN A DICTIONARY
# ================
# BIN A KEY-VALUE DICTIONARY
def dct_bin(dct,binsize=1,autobin=0,nbins=20,plot2screen=False):
  binsize = float(binsize)
  bins = {}
  # DETERMINE THE MIN AND MAX VALUES
  values = [dct[el] for el in dct.keys()]
  start, end = min(values), max(values)
  start = int(start/binsize)*binsize
  end   = (int(round(end/binsize))+1)*binsize
  # DETERMINE BINS
  dist  = end - start
  nbins = int(round(dist/float(binsize)))+1
  for i in range(nbins):
    bins["%10e"%(start+i*binsize)]=0
  # CYCLE DCT AND FILL BINS
  for key in dct:
    bin = int(round(dct[key]/float(binsize)))*binsize
    bins["%10e"%bin]+=1
  # PLOT TO SCREEN
  if plot2screen:
    plotheight = 50
    values = [bins[key] for key in bins]
    maxheight = float(max(values))
    keys = [float(key) for key in bins]
    keys.sort()
    for key in keys:
      plt = ''
      plt += '='*int(round(plotheight*(bins["%10e"%key]/maxheight)))
      print "%8.3f %s"%(key,plt)
  return bins


#  ======================================================================
#    C O N C O O R D   C L A S S
#  ======================================================================

class cncrd:
  """
  This class provides an interface to CONCOORD
  Create a class instance by passing:
  - path to CONCOORD bin dir
  - path to DSSP
  - optional error function
  """

  # INITIALIZE CLASS
  # ================
  # - path IS THE PATH TO CONCOORD BIN DIR
  # - ddsp IS THE PATH TO DSSP
  # - basename IS THE BASENAME FOR THE OUTPUT FILES
  def __init__(self,path,dssp=None,errorfunc=error):
    # SET PATH FOR DIST AND DISCO
    self.distpath = os.path.join(path,'bin/dist')
    self.discopath = os.path.join(path,'bin/disco')
    self.dssp = dssp
    self.errorfunc = errorfunc
    # SET ENVIRONMENT STUFF
    os.environ["CONCOORDDIR"]=path
    os.environ["CONCOORDBIN"]=os.path.join(path,'bin')
    os.environ["CONCOORDLIB"]=os.path.join(path,'lib')

  # RUN CONCOORD
  # ============
  # WE DO DIST AN DISCO IN ONCE COMMAND
  def run_nmr(self,pdb,basename,nstruct=500,viol=0.4,bs=5,iter=10000,seed=None):
    # RUN DIST
    self.dist_nmr(basename,pdb,cnctbl)
    # RUN DISCO
    self.disco_nmr(basename,nstruct,viol,bs,iter,seed)

  # RUN DIST
  # ========
  # EXECUTE DIST
  def dist_nmr(self,basename,pdb,cnctbl):
    # BUILD THE COMMAND
    command = "%s -p %s -op %s.pdb -og %s.gro -od %s.dat -r -noe %s"%(self.distpath,pdb,basename,basename,basename,cnctbl)
    # EXECUTE THE COMMAND
    ret = os.system(command)
    return ret

  # RUN DISCO
  # =========
  # EXECUTE DISCO
  def disco_nmr(self,basename,nstruct=500,viol=0.4,bs=5,iter=10000,maxtry=5,seed=None):
    # HANDLE THE SEED
    if seed: seed = "-s %i"%seed
    else: seed = ""
    # BUILD THE COMMAND
    command = "%s -d %s.dat -p %s.pdb -op %s_ -n %i -ox %s.xtc -or %s.rms -of %s.flc -viol %5.2f -bs %i -i %i -t %i"%(self.discopath,basename,basename,
                                                                                                                      basename,nstruct,basename,
                                                                                                                      basename,basename,viol,bs,iter,maxtry)
    # EXECUTE THE COMMAND
    ret = os.system(command)
    return ret

  # RUN CONCOORD
  # ============
  # WE DO DIST AN DISCO IN ONCE COMMAND
  def run(self,pdb,basename,damp,nstruct=500,seed=741265,r=1):
    # RUN DIST
    self.dist(pdb,basename,damp,r)
    # RUN DISCO
    self.disco(basename,nstruct,seed)

  # RUN DIST
  # ========
  # EXECUTE DIST
  def dist(self,pdb,basename,damp,r=1):
    # SET THE DAMPINGFUNCTION
    self.damp = damp
    # HANDE THE PROTON SELECTION
    if r==1: r='-r'
    else: r=''
    # COMLETE THE BASE NAME
    base = os.path.join(self.path,basename)
    # BUILD THE COMMAND
    command = "%s -p %s -dssp %s %s -damp %4.2f -op %s.pdb -og %s.gro -od %s.dat"%(self.distpath,pdb,self.dssp,r,damp,base,base,base)
    # EXECUTE THE COMMAND
    ret = os.system(command)
    return ret

  # RUN DISCO
  # =========
  # EXECUTE DISCO
  def disco(self,basename,nstruct=500,seed=None):
    # HANDLE THE SEED
    if seed: seed = "-s %i"%seed
    else: seed = ""
    # COMPLETE THE BASENAME
    base = os.path.join(self.path,basename)
    # BUILD THE COMMAND
    command = "%s -d %s.dat -p %s.pdb -op %s_ -n %i -ox %s.xtc -or %s.rms -of %s.flc"%(self.discopath,base,base,base,nstruct,base,base,base)
    # EXECUTE THE COMMAND
    ret = os.system(command)
    return ret

#  ======================================================================
#    C O N C O O R D   F U N C T I O N   G R O U P
#  ======================================================================

# CONVERT XPLOR 2 CONCOORD
# ========================
# CONVERT AN XPLOR TABLE INTO A CONCOORD TABLE
# NOTE: THIS FUNCTION WAS WRITTEN BY CHRIS AND PREFERABLY NEEDS TO
# REWRITTEN TO USE THE NMR_RESTRAINT CLASSES!
def cnc_writeconcoord(psf,pdb,restraintlist,outtbl,
                       xplor=None,parameter=None):
  print "Converting XPLOR data in CNC format."
  # TAKE DEFAULTS
  if not xplor: xplor = nmvconf["XPLOR"]
  if not parameter: parameter = nmvconf["PAR_PROT"]
  # WRITE XPLOR SCRIPT
  xplr = xplor_script(xplor)
  # READ THE STRUCTURE FILE
  xplr.write("structure\n  @%s\nend"%psf)
  # READ PARAMETER FILE
  xplr.write("evaluate ($par_nonbonded=PROLSQ)")
  xplr.write("parameter\n @@%s\nend"%parameter)
  # READ COORDINATES
  xplr.write("coor\n @@%s\n"%pdb)
  # DO THE WORK
  xplr.write("""
  flags exclude * include noe end

  set message on echo on end

  noe reset
    nrestraints = 30000
    ceiling       100
    class         prot""")
  # GET ALL DISTANCE RESTRAINTS
  distlist = [r for r in restraintlist if r.type=="DIST"]
  for el in distlist:
    xplr.write(el.format("XPLOR"))
  xplr.write("""
    averaging  prot sum
    potential  prot soft
    sqconstant prot 1.
    sqexponent prot 2
    scale      prot 25
    soexponent prot 1
    rswitch    prot 1.0
    sqoffset   prot 0.0
    asymptote  prot 2.0
  end

  print threshold=-0.00001 noe

  stop""")
  xplr.logfiles = 'silent'
  xplr.submit()
  # PARSE THE LOGFILE
  lines = open(xplr.logpath,'r').readlines()
  filelist = []
  # IN THE PSEUDOATOMS_DICT
  # XPLOR   IS AT POSITION 0
  # IUPAC   IS AT POSITION 1
  # CORRECTION AT POSITION 2
  informat = 'xplor'
  if string.upper(informat)=='XPLOR':   pos=0
  elif string.upper(informat)=='IUPAC': pos=1
  # READ THE PSEUDOATOMS DICTIONARY
  pseudoatoms_dict = cnc_pseudodict()
  # WRITE THE HEADER OF THE OUTPUT FILE
  filelist.append('[ distance_restraints ]\n')
  filelist.append('[ resid1 resname1 atomname1 segid1 ')
  filelist.append('resid2 resname2 atomname2 segid2 ')
  filelist.append('lowbound uppbound upppscor index restrnum ]\n')
  i = 0
  while i < len(lines):
    # GO THROUGH THE DISTANCES IN THE RESTRAINT LIST
    if len(lines[i])>10 and string.split(lines[i])[0]=='==========' and string.split(lines[i])[3]=='restraint':
      # CREATE ENTRIES FOR BOTH PARTNERS
      restr_dict = {}
      restr_dict['i']= {}
      restr_dict['j']= {}
      # X IS USED TO CREATE AN INDEX IN EACH RESTRAINT FOR THE DIFFERENT CONTRIBUTIONS
      # CNTI AND CNTJ COUNT THE I- AND J CONTRIBUTIONS RESPECTIVELY
      x = 0
      cnti = 0
      cntj = 0
      # GET RESTRAINT NUMBER
      restr_num=int(string.split(lines[i])[4])
      while not string.split(lines[i+x])[0]=='R<average>=':
        x = x + 1
        # CREATE THE DICTIONARIES FOR THE DIFFERENT CONTRIBUTIONS IN EACH RESTRAINT
        if string.split(lines[i+x])[0]=='set-i-atoms':
          x = x + 1
          while not string.split(lines[i+x])[0]=='set-j-atoms':
            line=string.split(lines[i+x])
            atomname=line[-1]
            resname=line[-2]
            resnum=int(line[-3])
            # GET SEGID
            try: segid=line[-4]
            except IndexError: segid='.'
            restr_dict['i'][x]= {}
            restr_dict['i'][x]['atomname']=atomname
            restr_dict['i'][x]['resname']=resname
            restr_dict['i'][x]['resnum']=resnum
            restr_dict['i'][x]['segid']=segid
            x = x + 1
            cnti = cnti + 1
        if string.split(lines[i+x])[0]=='set-j-atoms':
          x = x + 1
          while not string.split(lines[i+x])[0]=='R<average>=':
            line=string.split(lines[i+x])
            atomname=line[-1]
            resname=line[-2]
            resnum=int(line[-3])
            # GET SEGID
            try: segid=line[-4]
            except IndexError:  segid='.'
            restr_dict['j'][x]= {}
            restr_dict['j'][x]['atomname']=atomname
            restr_dict['j'][x]['resname']=resname
            restr_dict['j'][x]['resnum']=resnum
            restr_dict['j'][x]['segid']=segid
            x = x + 1
            cntj = cntj + 1
        # CALCULATE THE UPPER AND LOWER BOUNDS
        if string.split(lines[i+x])[0]=='R<average>=' and string.split(lines[i+x])[2]=='NOE=':
          try:
            line=string.split(lines[i+x])
            restr_arg1=float(line[3])
            # chris:
            #restr_arg2=float(string.split(line[5],'/')[0])
            # NEGATIVE LOWER BOUNDS...
            val = lines[i+x][33:38]
            if val=='*****':
              restr_arg2=-100.0
              warning("Sub zero lower bound found")
              print lines[i+x]
              print "Check: %s"%xplr.logpath
            else:
              restr_arg2=float(val)
            # NON NOES...
            val = lines[i+x][40:45]
            if val=='*****':
              restr_arg3=100.
              warning("Probably found non-NOE")
              print lines[i+x]
              print "Check: %s"%xplr.logpath
            else:
              restr_arg3=float(val)
          except ValueError:
            print line
            print xplr.logpath
            raise SystemExit
          low=restr_arg1 - restr_arg2
          upl=restr_arg1 + restr_arg3
          index = 0
          # CHECK WHETHER WE NEED UPPER BOUND CORRECTIONS FOR THE BOUND SMOOTHING IN CONCOORD
          # IF CHECKI=1, CORRECTION IS APPLIED TO SET OF I ATOMS
          # IF CHECKJ=1, CORRECTION IS APPLIED TO SET OF J ATOMS
          #
          # IN CASE OF ONLY ONE CONTRIBUTION, NO CORRECTION IS APPLIED, CHECKI,J=0
          if cnti==1:
            ipass='true'
            pseudoatomcorri=0.0
          if cntj==1:
            jpass='true'
            pseudoatomcorrj=0.0
          # IN CASE OF MULTIPLE CONTRIBUTIONS:
          if cnti>1:
            # GET THE INFORMATION FOR THE FIRST CONTRIBUTION IN THE RESTRAINT
            contrib1_index=restr_dict['i'].keys()[0]
            atomname1=restr_dict['i'][contrib1_index]['atomname']
            resname1=restr_dict['i'][contrib1_index]['resname']
            resnum1=restr_dict['i'][contrib1_index]['resnum']
            segid1=restr_dict['i'][contrib1_index]['segid']
            pseudoatomi=None
            checki=0
            # check whether all i contributions are in the same residue
            # if not do not use pseudoatom correction
            for sel in restr_dict['i'].keys():
              atomnamei=restr_dict['i'][sel]['atomname']
              resnamei=restr_dict['i'][sel]['resname']
              resnumi=restr_dict['i'][sel]['resnum']
              segidi=restr_dict['i'][sel]['segid']
              if not resnamei==resname1 or not resnumi==resnum1 or not segidi==segid1:
                checki=0
                #print 'i check1  ',resnamei,resname1,resnumi,resnum1,segidi,segid1,restr_num
                break
              else:
                checki=1
            # check whether a pseudoatom exists for the first atom in i-contributions;
            # if not, we have more than one different groups in the
            # i contributions: don't correct
            # check the number of contributions to identify which of the pseudoatoms
            # are involved
            if checki==1:
              for key in pseudoatoms_dict[resname1].keys():
                if atomname1 in pseudoatoms_dict[resname1][key][pos] and cnti==len(pseudoatoms_dict[resname1][key][pos])-1:
                  pseudoatomi=key
              if not pseudoatomi:
                checki=0
                #print 'i check2  ',resname1,atomname1,pseudoatomi,cnti,restr_num
            # Now check all contributions
            if checki==1:
              for sel in restr_dict['i'].keys():
                atomnamei=restr_dict['i'][sel]['atomname']
                resnamei=restr_dict['i'][sel]['resname']
                resnumi=restr_dict['i'][sel]['resnum']
                segidi=restr_dict['i'][sel]['segid']
                if not atomnamei in pseudoatoms_dict[resname1][pseudoatomi][pos]:
                  checki=0
                  #print 'i check3  ',resnamei,atomnamei,pseudoatomi,restr_num
            if checki==1:
              ipass='true'
              #print 'i pass  ',resnamei,atomnamei,pseudoatomi,restr_num
              pseudoatomcorri=pseudoatoms_dict[resname1][pseudoatomi][2]
            else:
              ipass='false'
              pseudoatomcorri=0.0
          # do the same for the j-contributions
          if cntj>1:
            contrib1_index=restr_dict['j'].keys()[0]
            atomname1=restr_dict['j'][contrib1_index]['atomname']
            resname1=restr_dict['j'][contrib1_index]['resname']
            resnum1=restr_dict['j'][contrib1_index]['resnum']
            segid1=restr_dict['j'][contrib1_index]['segid']
            pseudoatomj=None
            checkj=0
            for sel in restr_dict['j'].keys():
              atomnamej=restr_dict['j'][sel]['atomname']
              resnamej=restr_dict['j'][sel]['resname']
              resnumj=restr_dict['j'][sel]['resnum']
              segidj=restr_dict['j'][sel]['segid']
              if not resnamej==resname1 or not resnumj==resnum1 or not segidj==segid1:
                checkj=0
                #print 'j check1  ',resnamej,resname1,resnumj,resnum1,segidj,segid1,restr_num
                break
              else:
                checkj=1
            if checkj==1:
              for key in pseudoatoms_dict[resname1].keys():
                if atomname1 in pseudoatoms_dict[resname1][key][pos] and cntj==len(pseudoatoms_dict[resname1][key][pos])-1:
                  pseudoatomj=key
              if not pseudoatomj:
                #print 'j check2  ',resname1,atomname1,pseudoatomj,cntj,restr_num
                checkj=0
            if checkj==1:
              for sel in restr_dict['j'].keys():
                atomnamej=restr_dict['j'][sel]['atomname']
                resnamej=restr_dict['j'][sel]['resname']
                resnumj=restr_dict['j'][sel]['resnum']
                segidj=restr_dict['j'][sel]['segid']
                if not atomnamej in pseudoatoms_dict[resname1][pseudoatomj][pos]:
                  checkj=0
                  #print 'j check3  ',resnamej,atomnamej,pseudoatomj,restr_num
            if checkj==1:
              jpass='true'
              #print 'j pass  ',resnamej,atomnamej,pseudoatomj,restr_num
              pseudoatomcorrj=pseudoatoms_dict[resname1][pseudoatomj][2]
            else:
              jpass='false'
              pseudoatomcorrj=0.0
          # calculate correction
          if ipass=='true' and jpass=='true':
            pseudoatomcorrection = pseudoatomcorri + pseudoatomcorrj
          else:
            pseudoatomcorrection = 999.0 - upl
          # WRITE ALL THE INFORMATION TO THE FILE IN SORTED FASHION
          ilist=restr_dict['i'].keys()
          ilist.sort()
          jlist=restr_dict['j'].keys()
          jlist.sort()
          for sel1 in ilist:
            for sel2 in jlist:
              if cnti+cntj==2:
                index=0
              elif cnti+cntj>2:
                index=index+1
              filelist.append('%8i'%(restr_dict['i'][sel1]['resnum']))
              filelist.append('%9s'%(restr_dict['i'][sel1]['resname']))
              filelist.append('%10s'%(restr_dict['i'][sel1]['atomname']))
              filelist.append('%7s'%(restr_dict['i'][sel1]['segid']))
              filelist.append('%7i'%(restr_dict['j'][sel2]['resnum']))
              filelist.append('%9s'%(restr_dict['j'][sel2]['resname']))
              filelist.append('%10s'%(restr_dict['j'][sel2]['atomname']))
              filelist.append('%7s'%(restr_dict['j'][sel2]['segid']))
              filelist.append('%9.3f'%(low))
              filelist.append('%9.3f'%(upl))
              filelist.append('%9.3f'%(upl+pseudoatomcorrection))
              filelist.append('%6i'%(index))
              filelist.append('%9i\n'%(restr_num))
    i = i + 1
  # WRITE THE OUTPUTFILE
  outfile_disre = open(outtbl,'w')
  for el in filelist:
    outfile_disre.write(el)
  outfile_disre.close()
  # DELETE TMP FILE
  os.remove(xplr.logpath)
  print "Done."


# A DICTIONARY WITH THE CNC PSEUDOATOMS CORRECTIONS
# =================================================
# RETURNS A DICTIONARY PER RESIDUE THAT CONTAINS ALL PSEUDOATOM DEFINITIONS
def cnc_pseudodict():
  pseudoatoms_dict = {}
  # ALA
  pseudoatoms_dict['ALA']={}
  pseudoatoms_dict['ALA']['HB*']=[['HB1','HB2','HB3','HB*'],
                                  ['HB1','HB2','HB3','MB'],1.8]
  # ARG
  pseudoatoms_dict['ARG']={}
  pseudoatoms_dict['ARG']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['ARG']['HG*']=[['HG1','HG2','HG*'],['HG3','HG2','QG'],1.8]
  pseudoatoms_dict['ARG']['HD*']=[['HD1','HD2','HD*'],['HD3','HD2','QD'],1.8]
  pseudoatoms_dict['ARG']['HH1*']=[['HH11','HH12','HH1*'],['HH11','HH12','QH1'],1.8]
  pseudoatoms_dict['ARG']['HH2*']=[['HH21','HH22','HH2*'],['HH21','HH22','QH2'],1.8]
  pseudoatoms_dict['ARG']['HH*']=[['HH11','HH12','HH21','HH22','HH*'],['HH11','HH12','HH21','HH22','QH'],4.0]
  # ASN
  pseudoatoms_dict['ASN']={}
  pseudoatoms_dict['ASN']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['ASN']['HD*']=[['HD21','HD22','HD*'],['HD21','HD22','QD'],1.8]
  # ASP
  pseudoatoms_dict['ASP']={}
  pseudoatoms_dict['ASP']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  # CYS
  pseudoatoms_dict['CYS']={}
  pseudoatoms_dict['CYS']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  # GLN
  pseudoatoms_dict['GLN']={}
  pseudoatoms_dict['GLN']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['GLN']['HG*']=[['HG1','HG2','HG*'],['HG3','HG2','QG'],1.8]
  pseudoatoms_dict['GLN']['HE*']=[['HE21','HE22','HE*'],['HE21','HE22','QE'],1.8]
  # GLU
  pseudoatoms_dict['GLU']={}
  pseudoatoms_dict['GLU']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['GLU']['HG*']=[['HG1','HG2','HG*'],['HG3','HG2','QG'],1.8]
  # GLY
  pseudoatoms_dict['GLY']={}
  pseudoatoms_dict['GLY']['HA*']=[['HA1','HA2','HA*'],['HA3','HA2','QA'],1.8]
  # HIS
  pseudoatoms_dict['HIS']={}
  pseudoatoms_dict['HIS']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  # ILE
  pseudoatoms_dict['ILE']={}
  pseudoatoms_dict['ILE']['HG1*']=[['HG11','HG12','HG1*'],['HG13','HG12','QG'],1.8]
  pseudoatoms_dict['ILE']['HG2*']=[['HG21','HG22','HG23','HG2*'],['HG21','HG22','HG23','MG'],1.8]
  pseudoatoms_dict['ILE']['HD1*']=[['HD11','HD12','HD13','HD1*'],['HD11','HD12','HD13','MD'],1.8]
  # LEU
  pseudoatoms_dict['LEU']={}
  pseudoatoms_dict['LEU']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['LEU']['HD1*']=[['HD11','HD12','HD13','HD1*'],['HD11','HD12','HD13','MD1'],1.8]
  pseudoatoms_dict['LEU']['HD2*']=[['HD21','HD22','HD23','HD2*'],['HD21','HD22','HD23','MD2'],1.8]
  pseudoatoms_dict['LEU']['HD*']=[['HD11','HD12','HD13','HD21','HD22','HD23','HD*'],['HD11','HD12','HD13','HD21','HD22','HD23','QD'],4.4]
  # LYS
  pseudoatoms_dict['LYS']={}
  pseudoatoms_dict['LYS']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['LYS']['HG*']=[['HG1','HG2','HG*'],['HG3','HG2','QG'],1.8]
  pseudoatoms_dict['LYS']['HD*']=[['HD1','HD2','HD*'],['HD3','HD2','QD'],1.8]
  pseudoatoms_dict['LYS']['HE*']=[['HE1','HE2','HE*'],['HE3','HE2','QE'],1.8]
  pseudoatoms_dict['LYS']['HZ*']=[['HZ1','HZ2','HZ3','HZ*'],['HZ1','HZ2','HZ3','QZ'],1.8]
  # MET
  pseudoatoms_dict['MET']={}
  pseudoatoms_dict['MET']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['MET']['HG*']=[['HG1','HG2','HG*'],['HG3','HG2','QG'],1.8]
  pseudoatoms_dict['MET']['HE*']=[['HE1','HE2','HE3','HE*'],['HE1','HE2','HE3','ME'],1.8]
  # PHE
  pseudoatoms_dict['PHE']={}
  pseudoatoms_dict['PHE']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['PHE']['HD*']=[['HD1','HD2','HD*'],['HD1','HD2','QD'],4.3]
  pseudoatoms_dict['PHE']['HE*']=[['HE1','HE2','HE*'],['HE1','HE2','QE'],4.3]
  pseudoatoms_dict['PHE']['QR']=[['HD1','HD2','HE1','HE2','HZ','name HD* OR name HE* OR name HZ'],['HD1','HD2','HE1','HE2','HZ','QR'],5.0]
  # PRO
  pseudoatoms_dict['PRO']={}
  pseudoatoms_dict['PRO']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['PRO']['HG*']=[['HG1','HG2','HG*'],['HG3','HG2','QG'],1.8]
  pseudoatoms_dict['PRO']['HD*']=[['HD1','HD2','HD*'],['HD3','HD2','QD'],1.8]
  # SER
  pseudoatoms_dict['SER']={}
  pseudoatoms_dict['SER']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  # THR
  pseudoatoms_dict['THR']={}
  pseudoatoms_dict['THR']['HG2*']=[['HG21','HG22','HG23','HG2*'],['HG21','HG22','HG23','MG'],1.8]
  # TRP
  pseudoatoms_dict['TRP']={}
  pseudoatoms_dict['TRP']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  # TYR
  pseudoatoms_dict['TYR']={}
  pseudoatoms_dict['TYR']['HB*']=[['HB1','HB2','HB*'],['HB3','HB2','QB'],1.8]
  pseudoatoms_dict['TYR']['HD*']=[['HD1','HD2','HD*'],['HD1','HD2','QD'],4.3]
  pseudoatoms_dict['TYR']['HE*']=[['HE1','HE2','HE*'],['HE1','HE2','QE'],4.3]
  pseudoatoms_dict['TYR']['QR']=[['HD1','HD2','HE1','HE2','name HD* OR name HE*'],['HD1','HD2','HE1','HE2','QR'],5.0]
  # VAL
  pseudoatoms_dict['VAL']={}
  pseudoatoms_dict['VAL']['HG1*']=[['HG11','HG12','HG13','HG1*'],['HG11','HG12','HG13','MG1'],1.8]
  pseudoatoms_dict['VAL']['HG2*']=[['HG21','HG22','HG23','HG2*'],['HG21','HG22','HG23','MG2'],1.8]
  pseudoatoms_dict['VAL']['HG*']=[['HG11','HG12','HG13','HG21','HG22','HG23','HG*'],['HG11','HG12','HG13','HG21','HG22','HG23','QG'],4.4]
  return pseudoatoms_dict


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
    if (self.macro==None):
      try: self.macro=open(self.filename,"w")
      except: self.raiseerror("write: YASARA macro %s could not be created"%self.filename)
    if (not self.error):
      if (type(data)!=types.ListType): data=[data]
      for line in data:
        if (line[-1:]!='\n'): line=line+"\n"
        self.macro.write(line)

  # SUBMIT MACRO
  # ============
  # THE MACRO IS SUBMITTED TO YASARA
  def submit(self,conflag=0):
    #global debugflag
    ret=0
    if (not self.error):
      self.macro.close()
      if conflag==0:
        try: ret=os.system(self.yasara+" -mcr %s"%self.script)
        except: self.raiseerror("YASARA could not be run")
      elif conflag==1:
        try: ret=os.system(self.yasara+" -con -mcr %s"%self.script)
        except: self.raiseerror("YASARA could not be run")
      elif conflag==2:
        try: ret=os.system(self.yasara+" -txt -mcr %s"%self.script)
        except: self.raiseerror("YASARA could not be run")
    return(ret)


#  ======================================================================
#    Y A S A R A   T O O L S
#  ======================================================================

# HACK HACK HACK
# ==============
# REMOVE THE TER STATEMENTS FROM YASARA PDB FILE
def yas_terhack(pdbfile):
  tmpfile = pdbfile+'.tmp'
  shutil.copy(pdbfile,tmpfile)
  content = open(tmpfile,'r').readlines()
  newfile = open(pdbfile,'w')
  for line in content:
    if line[:3] != 'TER' and line[:3] != 'CON':
      newfile.write(line)
  dsc_remove(tmpfile)


# COLOR ENSEMBLE BY RMSD
# ======================
# ENSEMBLE IS COLOR FROM BLUE TO RED, A REFERENCE MAXIMUMVALUE
# CAN BE PROVIDED. RANGE IS AUTOMAGICALLY ADJUSTED IS THERE ARE
# OUTLIERS PRESENT (> 2 SIGMA)
def yas_rmsdcolensemble(yaspath,filelist,refval=None,
                        atomlist=['CA'],unit="Res",fitflag=1):
  # FIRST WE BUILD AN RMSD MATRIX
  rmsdmtxlist = yas_rmsdmtxfast(yaspath,filelist,atomlist,unit,fitflag)
  # NEXT WE DETERMINE THE AVERAGE RMSD VALUES
  nres = len(rmsdmtxlist)
  rmsds = []
  for r in range(nres):
    rmsdmtx = rmsdmtxlist[r]
    rmsdlist = []
    for i in range(len(filelist)):
      del rmsdmtx[i][i]
      rmsdlist.append(avg_list(rmsdmtx[i],sdflag=0))
    avg = avg_list(rmsdlist)[0]
    rmsds.append(avg)
  # CONVERT THE RMSDS TO COLOURS
  # WE GO FROM BLUE (0) TO RED (120) IN YASARA COLORS
  colors = []
  minval = 0
  # GET MAXIMUM VALUE
  if refval:
    maxval = refval
  else:
    maxval = max(rmsds)
    # ADJUST MAXVAL IN CASE OF OUTLIERS
    # NO DEVIATIONS > 2 SIGMA ARE ALLOWED
    avg = avg_list(rmsds)
    if maxval > avg[0]+2*avg[1]: maxval = avg[0]+2*avg[1]
    if minval < avg[0]-2*avg[1]: minval = avg[0]-2*avg[1]
  print "Using %5.2f for minimum value."%minval
  print "Using %5.2f for maximum value."%maxval
  # CREATE COLORS
  for rmsd in rmsds:
    colors.append(int((min(rmsd,maxval)/maxval)*120))
  # LOAD THE PDBFILES
  ysr = ysr_macro(yaspath)
  for file in filelist:
    ysr.write("LoadPDB %s,Center=No"%file)
    ysr.write("RenumberRes Obj (LastObj),First=1")
  for i in range(len(colors)):
    print i, colors[i]
    ysr.write("ColorRes %i,%i"%(i+1,colors[i]))
  ysr.submit()


# DETERMINE MATRIX OF PAIRWISE RMSDS
# ==================================
# - filelist CONTAINS THE NAMES OF THE PDB-FILES TO SUPERPOSE.
# - unit IS Obj OR Res TO CALCULATE RMSDs PER OBJECT OR RESIDUE.
def yas_rmsdmtxfast(yaspath,filelist,atomlist=['CA'],unit="Obj",fitflag=1):
  print "Running YASARA to determine pairwise RMSDs for %d files." % len(filelist)
  tabfilename=dsc_tmpfilename("suppos.log")
  # BUILD STRING FOR ATOMS
  atom_str = string.join(atomlist," ")
  # CALCULATE RMSDs
  macro=ysr_macro(yaspath)
  for filename in filelist: macro.write("LoadPDB %s,Center=No"%filename)
  # DETERMINE THE NUMBER OF RMSDs PER SUPERPOSITION: EITHER 1 (unit="Obj") OR NUMBER OF RESIDUES PER OBJECT (unit="Res")
  # (ASSUMING THAT EVERY RESIDUE CONTAINS AT LEAST ONE ATOM IN atomlist)
  if (unit=="Obj"): columns="1"
  else: columns="Residues/Objects"
  macro.write(["MakeTab RMSDs,Dimensions=3,Columns=(%s),Rows=(Objects)"%columns])
  if fitflag==1:
    macro.write(["Tabulate SupAtom %s,%s,Unit=%s"%(atom_str,atom_str,unit)])
  elif fitflag==0:
    macro.write(["Tabulate RmsdAtom %s,%s,Unit=%s"%(atom_str,atom_str,unit)])
  macro.write(["FlipTab RMSDs,Columns,Pages",
               "SaveTab RMSDs,%s,Format=Text,NumFormat=7.4f,RMSDs"%tabfilename,
               "Exit"])
  macro.submit(conflag=1)
  tab=tab_read(tabfilename)
  dsc_remove(tabfilename)
  return(tab)

# READ A TABLE
# ============
# A TABLE IN YASARA FORMAT (1 HEADER LINE, THEN n LINES WITH FLOATS) IS PARSED
# AND RETURNED AS A LIST (1D), A LIST OF LISTS (2D), OR A LIST OF LISTS OF LISTS (3D)
def tab_read(filename):
  if (os.path.exists(filename+".zip")): tabtxt=string.split(dsc_unzipped(filename),"\n")
  else: tabtxt=open(filename,"r").readlines()
  table=[[]]
  # TRUNCATE EMPTY LINES AT THE END
  while (string.strip(tabtxt[-1])==""): del tabtxt[-1]
  for row in tabtxt[1:]:
    row=string.strip(row)
    if (row==""):
      # A NEW TABLE PAGE
      table.append([])
    else:
      # A NEW TABLE ROW
      celllist=[]
      for cell in string.split(row):
        celllist.append(float(cell))
      table[-1].append(celllist)
  # REDUCE FROM 3D TO 2D TO 1D TABLE
  for i in range(2):
    if (len(table)==1): table=table[0]
    else: break
  return(table)

# DETERMINE MATRIX OF PAIRWISE CA RMSDS
# =====================================
# - filelist CONTAINS THE NAMES OF THE PDB-FILES TO SUPERPOSE.
def yas_rmsdmtx(yaspath,filelist,atomlist=['CA'],residues=None,fitflag=1):
  print "Running YASARA to determine pairwise RMSDs for %d files." % len(filelist)
  tabfilename=dsc_tmpfilename("suppos.log")
  # BUILD STRING FOR ATOMS
  atom_str = ''
  for atom in atomlist: atom_str += '%s '%atom
  # INITIALIZE MATRIX
  size=len(filelist)
  if residues:
    # MANY MATRICES
    mtxlist = []
    for r in range(len(residues)):
      mtx = []
      for i in range(size): mtx.append([None]*size)
      mtxlist.append(mtx)
  else:
    # ONE MATRIX
    mtx=[]
    for i in range(size): mtx.append([None]*size)
  maxsubsize=99
  macro=ysr_macro(yaspath)
  macro.write("Console Off")
  # CYCLE THROUGH THE ROWS OF THE MATRIX
  for i in range(0,size,maxsubsize):
    # LOAD ALL "ROW" MOLECULES
    rowmols=min(maxsubsize,size-i)
    macro.write("DelObj All")
    for j in range(rowmols): macro.write("LoadPDB "+filelist[i+j])
    # CYCLE THROUGH THE COLUMNS OF THE MATRIX
    # MAKE THE "FREE" SUPERPOSITIONS (MOLECULES ALREADY LOADED)
    for j in range(rowmols):
      for k in range(j+1,rowmols):
        if fitflag:
          macro.write("SupAtom %s Obj %d,%s Obj %d\n"%
                      (atom_str,j+1,atom_str,k+1))
        if residues==None:
          macro.write("rmsd=RmsdAtom %s Obj %d,%s Obj %d\nAddTab (rmsd)\n"%
                      (atom_str,j+1,atom_str,k+1))
        else:
          for r in range(len(residues)):
            macro.write("rmsd=RmsdAtom %s Res %i Obj %d,%s Res %i Obj %d\nAddTab (rmsd)\n"%
                        (atom_str,residues[r],j+1,atom_str,residues[r],k+1))
    # MAKE THE REMAINING SUPERPOSITIONS, LOADING AND DELETING COLUMN MOLECULES
    for j in range(i+rowmols,size):
      macro.write("LoadPDB "+filelist[j])
      for k in range(rowmols):
        if fitflag:
          macro.write("SupAtom %s Obj %d,%s Obj %d\n" %
                      (atom_str,k+1,atom_str,rowmols+1))
        if residues==None:
          macro.write("rmsd=RmsdAtom %s Obj %d,%s Obj %d\nAddTab (rmsd)\n"%
                      (atom_str,k+1,atom_str,rowmols+1))
        else:
          for r in range(len(residues)):
            macro.write("rmsd=RmsdAtom %s Res %i Obj %d,%s Res %i Obj %d\nAddTab (rmsd)\n"%
                        (atom_str,residues[r],k+1,atom_str,residues[r],rowmols+1))
      macro.write("DelObj %d" % (rowmols+1))
  # SAVE TABLE
  macro.write("SaveTab %s,1,%%7.4f,RMSDs\nExit\n" % tabfilename)
  macro.submit(conflag=1)
  # PARSE TABLE
  # CYCLE THROUGH THE ROWS OF THE MATRIX
  log=open(tabfilename,"r").readlines()
  log=log[1:]
  pos=0
  if residues==None:
    for i in range(0,size,maxsubsize):
      # LOAD ALL "ROW" MOLECULES
      rowmols=min(maxsubsize,size-i)
      # PARSE THE LOG FILE AND ADD RMSD VALUES TO MATRIX
      for j in range(rowmols):
        # RMSD OF SELF SUPERPOSITION IS ZERO
        mtx[i+j][i+j]=0
        for k in range(j+1,rowmols):
          rmsd=float(log[pos])
          mtx[i+j][i+k]=rmsd
          mtx[i+k][i+j]=rmsd
          pos=pos+1
      for j in range(i+rowmols,size):
        for k in range(rowmols):
          rmsd=float(log[pos])
          mtx[i+k][j]=rmsd
          mtx[j][i+k]=rmsd
        pos=pos+1
  else:
    for i in range(0,size,maxsubsize):
      # LOAD ALL "ROW" MOLECULES
      rowmols=min(maxsubsize,size-i)
      # PARSE THE LOG FILE AND ADD RMSD VALUES TO MATRIX
      for j in range(rowmols):
        # RMSD OF SELF SUPERPOSITION IS ZERO
        for r in range(len(residues)):
          mtxlist[r][i+j][i+j]=0
        for k in range(j+1,rowmols):
          for r in range(len(residues)):
            rmsd=float(log[pos])
            mtxlist[r][i+j][i+k]=rmsd
            mtxlist[r][i+k][i+j]=rmsd
            pos=pos+1
      for j in range(i+rowmols,size):
        for k in range(rowmols):
          for r in range(len(residues)):
            rmsd=float(log[pos])
            mtxlist[r][i+k][j]=rmsd
            mtxlist[r][j][i+k]=rmsd
            pos=pos+1
  dsc_remove(tabfilename)
  if residues== None: return(mtx)
  else: return(mtxlist)


# DETERMINE MATRIX OF PAIRWISE CA RMSDS
# =====================================
# - filelist CONTAINS THE NAMES OF THE PDB-FILES TO SUPERPOSE.
def yas_rmsdmtx_ori(yaspath,filelist,atomlist=['CA'],residue=None,fitflag=1):
  print "Running YASARA to determine pairwise RMSDs for %d files." % len(filelist)
  tabfilename=dsc_tmpfilename("suppos.log")
  # BUILD STRING FOR ATOMS
  atom_str = ''
  for atom in atomlist: atom_str += '%s '%atom
  # INITIALIZE MATRIX
  size=len(filelist)
  mtx=[]
  for i in range(size): mtx.append([None]*size)
  maxsubsize=50
  macro=ysr_macro(yaspath)
  #macro.write("Console Off")
  # CYCLE THROUGH THE ROWS OF THE MATRIX
  for i in range(0,size,maxsubsize):
    # LOAD ALL "ROW" MOLECULES
    rowmols=min(maxsubsize,size-i)
    macro.write("DelObj All")
    for j in range(rowmols): macro.write("LoadPDB "+filelist[i+j])
    # CYCLE THROUGH THE COLUMNS OF THE MATRIX
    # MAKE THE "FREE" SUPERPOSITIONS (MOLECULES ALREADY LOADED)
    for j in range(rowmols):
      for k in range(j+1,rowmols):
        if fitflag:
          macro.write("SupAtom %s Obj %d,%s Obj %d\n"%
                      (atom_str,j+1,atom_str,k+1))
        if residue==None:
          macro.write("rmsd=RmsdAtom %s Obj %d,%s Obj %d\nAddTab (rmsd)\n"%
                      (atom_str,j+1,atom_str,k+1))
        else:
          macro.write("rmsd=RmsdAtom %s Res %i Obj %d,%s Res %i Obj %d\nAddTab (rmsd)\n"%
                      (atom_str,residue,j+1,atom_str,residue,k+1))
    # MAKE THE REMAINING SUPERPOSITIONS, LOADING AND DELETING COLUMN MOLECULES
    for j in range(i+rowmols,size):
      macro.write("LoadPDB "+filelist[j])
      for k in range(rowmols):
        if fitflag:
          macro.write("SupAtom %s Obj %d,%s Obj %d\n" %
                      (atom_str,k+1,atom_str,rowmols+1))
        if residue == None:
          macro.write("rmsd=RmsdAtom %s Obj %d,%s Obj %d\nAddTab (rmsd)\n"%
                      (atom_str,k+1,atom_str,rowmols+1))
        else:
          macro.write("rmsd=RmsdAtom %s Res %i Obj %d,%s Res %i Obj %d\nAddTab (rmsd)\n"%
                      (atom_str,residue,k+1,atom_str,residue,rowmols+1))
      macro.write("DelObj %d" % (rowmols+1))
  # SAVE TABLE
  macro.write("SaveTab %s,1,%%7.4f,RMSDs\nExit\n" % tabfilename)
  macro.submit(conflag=1)
  # PARSE TABLE
  # CYCLE THROUGH THE ROWS OF THE MATRIX
  log=open(tabfilename,"r").readlines()
  log=log[1:]
  pos=0
  for i in range(0,size,maxsubsize):
    # LOAD ALL "ROW" MOLECULES
    rowmols=min(maxsubsize,size-i)
    # PARSE THE LOG FILE AND ADD RMSD VALUES TO MATRIX
    for j in range(rowmols):
      # RMSD OF SELF SUPERPOSITION IS ZERO
      mtx[i+j][i+j]=0
      for k in range(j+1,rowmols):
        rmsd=float(log[pos])
        mtx[i+j][i+k]=rmsd
        mtx[i+k][i+j]=rmsd
        pos=pos+1
    for j in range(i+rowmols,size):
      for k in range(rowmols):
        rmsd=float(log[pos])
        mtx[i+k][j]=rmsd
        mtx[j][i+k]=rmsd
        pos=pos+1
  dsc_remove(tabfilename)
  return(mtx)


# SPLIT PDB 2 XPLOR
# =================
# SPLIT A PDB FILE IN SEPARATE XPLOR FILES
# OBSOLETE! OBSOLETE! OBSOLETE! OBSOLETE!
def yas_splitpdb2xplor(yaspath,inpdb,outpath,basename,no_models=None,
                       rebuildh=0,noclean=0):
  if not no_models:
    # READ THE PDB FILE
    no_models = pdb_models(inpdb)
  else: no_models = 1
  # CREATE YASARA MACRO
  ysr = ysr_macro(yaspath)
  ysr.write(["OnError Stop",
             "LoadPDB %s"%inpdb])
  if rebuildh:
    ysr.write(["DelAtom Element H and res !His"])
    noclean = 0
  # SELECTIVE CLEANING
  if not noclean:
    ysr.write(["Clean"])
  ysr.write(["DelWaterObj All"])
  # CLEAR SEGMENT ID, CHAIN ID WILL NOW BE AUTOMAGICALLY TRANSFER
  # TO SEGMENT ID FIELD WHEN SAVED AS XPLOR FILE
  ysr.write(["RenameSeg All,____"])
  for i in range(1,no_models+1):
    ysr.write(["SavePDB %i,%s/%s_%03i,Format=Xplor"%(i,outpath,basename,i)])
  ysr.write(["Exit"])
  # RUN MACRO
  ysr.submit(conflag=1)
  pdblist = []
  # HACK HACK HACK
  for i in range(1,no_models+1):
    pdbfile = os.path.join(outpath,"%s_%03i.pdb"%(basename,i))
    yas_terhack(pdbfile)
    pdblist.append(pdbfile)
  return pdblist

# PDB 2 XPLOR
# ===========
# CONVERT A PDB FILE INTO XPLOR FORMAT
def yas_pdb2xplor(yaspath,inpdb,outpdb,no_models=None,segname='____'):
  if not no_models:
    # READ THE PDB FILE
    no_models = pdb_models(inpdb)
  # CREATE YASARA MACRO
  ysr = ysr_macro(yaspath)
  ysr.write(["ErrorExit Off",
             "LoadPDB %s"%inpdb,
             "CleanAll",
             "DelWaterObj All"])
  # CLEAR SEGMENT ID, CHAIN ID WILL NOW BE AUTOMAGICALLY TRANSFER
  # TO SEGMENT ID FIELD WHEN SAVED AS XPLOR FILE
  ysr.write(["RenameSeg All,%s"%segname])
  ysr.write(["SavePDB 1-%i,%s,Format=Xplor"%(no_models,outpdb)])
  ysr.write(["Exit"])
  # RUN MACRO
  ysr.submit(conflag=1)
  # HACK HACK HACK
  yas_terhack(outpdb)

# SPLITPDB
# ========
# CONVERT A PDB FILE INTO SEPARATE MODELS
def yas_splitpdb(yaspath,inpdb,basename,no_models=None,format='pdb'):
  format = format.lower()
  if not no_models:
    # READ THE PDB FILE
    no_models = pdb_models(inpdb)
  # CREATE YASARA MACRO
  ysr = ysr_macro(yaspath)
  ysr.write(["ErrorExit Off",
             "LoadPDB %s"%inpdb,
             "CleanAll"])
  for i in range(1,no_models+1):
    if format=='pdb':
      ysr.write(["SavePDB %i,%s%03i"%(i,basename,i)])
    elif format=='xplor':
      ysr.write(["SavePDB %i,%s%03i,Format=Xplor"%(i,basename,i)])
  ysr.write(["Exit"])
  # RUN MACRO
  ysr.submit(conflag=1)
  return glob.glob(os.path.join(yaspath,"%s*.pdb"%basename))

# XPLOR 2 PDB
# ===========
# CONVERT AN XPLOR FILE INTO PDB FORMAT
def yas_xplor2pdb(yaspath,inpdb,outpdb,no_models=None):
  if not no_models:
    # READ THE PDB FILE
    no_models = pdb_models(inpdb)
  # CREATE YASARA MACRO
  ysr = ysr_macro(yaspath)
  ysr.write(["ErrorExit Off",
             "LoadPDB %s"%inpdb,
             "CleanAll",
             "DelWaterObj All"])
  ysr.write(["SavePDB 1-%i,%s"%(no_models,outpdb)])
  ysr.write(["Exit"])
  # RUN MACRO
  ysr.submit(conflag=1)

# JOINPDB
# =======
# JOIN PDB FILES INTO AN ENSEMBLE
def yas_joinpdb(yaspath,pdblist,outpdb,format='pdb'):
  # CREATE YASARA MACRO
  ysr = ysr_macro(yaspath)
  ysr.write(["ErrorExit On"])
  for pdb in pdblist:
    ysr.write(["LoadPDB %s"%pdb])
  if format=='xplor': ysr.write(["SavePDB All,%s,Format=Xplor"%outpdb])
  elif format=='pdb': ysr.write(["SavePDB All,%s"%outpdb])
  ysr.write(["Exit"])
  # RUN MACRO
  ysr.submit(conflag=1)

# CHECK PDB
# =========
# CHECK QUALITY OF PDB FILE
def yas_checkpdb(yaspath,pdb,checklist):
  # CHECK TYPE
  if type(checklist)!=types.ListType: checklist = [checklist]
  checks = {}
  tabfilename = dsc_tmpfile()
  # CREATE YASARA MACRO
  ysr = ysr_macro(yaspath)
  ysr.write(["LoadPDB %s"%pdb])
  # STORE NUMBER OF RESIDUES
  ysr.write(["Tabulate (residues)"])
  # STORE RESIDUE NUMBERS
  ysr.write("Tabulate ListRes Obj 1")
  # STORE SCORES
  for check in checklist:
    ysr.write(["Tabulate CheckRes Obj 1,%s"%check])
  ysr.write("SaveTab 1,%s,Columns=1"%tabfilename)
  ysr.write("Exit")
  ysr.submit(conflag=2)
  # READ OUTPUT
  content = open(tabfilename,'r').readlines()
  # NUMBER OF RESIDUES
  nres = int(float(content[1].strip()))
  # RESIDUE NUMBERS
  resn = []
  sub = content[2:2+nres]
  for el in sub: resn.append(int(float(el.strip())))
  checks['resn'] = resn
  # QUALITY SCORES
  for i in range(len(checklist)):
    scores = []
    sub = content[(2+(i+1)*nres):(2+((i+2)*nres))]
    for el in sub: scores.append(float(el.strip()))
    checks[checklist[i]]=scores
  os.remove(tabfilename)
  return checks

# CHECK PDBLIST
# =============
# CHECK QUALITY OF MULTIPLE PDB FILES
def yas_checkpdbs(yaspath,pdblist,checklist):
  # CHECK TYPE
  if type(checklist)!=types.ListType: checklist = [checklist]
  # OVERALL DICT
  quad = {}
  for pdb in pdblist:
    quad[pdb] = yas_checkpdb(yaspath,pdb,checklist)
  # CREATE AVERAGE DICTIONARY
  nres = len(quad[pdb][checklist[0]])
  # STORE RESIDUE NUMBERS
  avgd = {}
  avgd['resn'] = quad[pdb]['resn']
  for check in checklist:
    avgd[check]=[]
    for i in range(nres):
      values = []
      for pdb in pdblist:
        values.append(quad[pdb][check][i])
      avg = avg_list(values)
      avgd[check].append(avg)
  return avgd

# CLEAN PDB FILE
# ================
# CLEAN A PDB FILE AND REMOVE ALL WATERS
def yas_cleanpdb(yaspath,inpdb,outpdb,no_models=None):
  if not no_models:
    # READ THE PDB FILE
    no_models = pdb_models(inpdb)
  # CREATE YASARA MACRO
  ysr = ysr_macro(yaspath)
  ysr.write(["ErrorExit Off",
             "LoadPDB %s"%inpdb,
             "CleanAll",
             "DelWaterObj All"])
  ysr.write(["SavePDB 1-%i,%s"%(no_models,outpdb)])
  ysr.write(["Exit"])
  # RUN MACRO
  ysr.submit(conflag=1)

# GET PERCENTAGE SEC STR
# ======================
# DETERMINE THE PERCENTAGE OF SECONDARY STRUCTURE IN A PDB FILE
# - helix
# - sheet
# - turn
def yas_percsecstr(yaspath,inpdb,no_models=None):
  if not no_models:
    # READ THE PDB FILE
    no_models = pdb_models(inpdb)
  # CREATE YASARA MACRO
  ysr = ysr_macro(yaspath)
  ysr.write(["ErrorExit Off",
             "LoadPDB %s"%inpdb])
  for i in range(1,no_models+1):
    ysr.write(["all = CountRes Obj %i"%i])
    ysr.write(["sst = CountRes SecStr Helix Sheet Turn Obj %i"%i])
    ysr.write(["AddTab %i"%i,"AddTab (((0e0+sst)/all)*100)"])
  fname = dsc_tmpfile(nmvconf["TMP"])
  ysr.write(["SaveTab %s,2,%%7.3f"%fname])
  ysr.write(["Exit"])
  # RUN MACRO
  ysr.submit(conflag=1)
  content = open(fname,'r').readlines()
  secstr = []
  for line in content[1:]:
    line = line.split()
    secstr.append(float(line[1]))
  return avg_list(secstr)[0]

# SUPERIMPOSE PDB FILES
# =====================
# SUPERIMPOSE PDB FILES AND GET RMSD
def yas_superimpose(yaspath,pdbref,pdblist,selection='heavy',
                    cleanflag=0,flipflag=0,outpdb=None,savescene=None,
                    xplorflag=0):
  # SET THE FLIPLAGS
  if flipflag == 0: flipstr='No'
  else: flipstr='Yes'
  # CREATE YASARA MACRO
  ysr = ysr_macro(yaspath)
#  ysr.write(["OnError Continue"])
  for el in pdblist:
    ysr.write(["LoadPDB %s"%el])
  ysr.write(["LoadPDB %s"%pdbref])
  # OPTIONALLY CLEAN THE FILES
  if cleanflag:
    ysr.write(["CleanAll"])
  # DO THE SUPERIMPOSITIONING
  if selection == 'heavy':
    for el in range(len(pdblist)):
      ysr.write(["Tabulate SupAtom Obj %i and element !H, Obj %i and element !H,Match=Yes,Flip=%s"%(el+1,len(pdblist)+1,flipstr)])
  if selection == 'bb':
    for el in range(len(pdblist)):
      ysr.write(["Tabulate SupAtom Obj %i and name ca n c, Obj %i and name ca n c,Match=Yes,Flip=%s"%(el+1,len(pdblist)+1,flipstr)])
  table = os.path.join(nmvconf["TMP"],"yas_%i.tab"%os.getpid())
  ysr.write(["SaveTab 1,%s,Columns=1"%table])
  # SAVE SCENE
  if savescene != None:
    ysr.write(["SaveSce %s"%savescene])
  # WRITE OUTSUPERPOSITIONED STRUCTURES
  if outpdb:
    if xplorflag: format='Xplor'
    else: format = 'PDB'
    ysr.write("SavePDB Obj 1-(nmob),%s,Format=%s"%(outpdb,format))
  ysr.write(["Exit"])
  ysr.submit(conflag=1)
  # READ OUTPUT FILE AND PARSE RMSDS
  content = open(table,'r').readlines()
  rmsds = []
  for line in content[1:]:
    line = line.split()
    print line
    rmsds.append(float(line[0]))
  return rmsds

# GET RMSD FOR ENSEMBLE
# =====================
#
def yas_ensemblermsd(yaspath,filelist,
                     selection='ca',
                     xplorflag=0):
  # SELECTION
  if selection == 'ca':
    selstr = 'name ca'
  elif selection == 'bb':
    selstr = 'name ca n c'
  elif selection == 'heavy':
    selstr = 'element !h'
  # CREATE YASARA MACRO
  tmptable = dsc_tmpfile(nmvconf["TMP"])+'.2'
  ysr= ysr_macro(yaspath)
  ysr.write(["OnError Exit",
             "Console Off"])
  # READ PDB FILES
  for file in filelist:
    ysr.write(["LoadPdb %s"%file])
  # READ PDB FILE IN PDB FILE
  pdbf = pdb_file.Structure(file)
  for chain in pdbf.peptide_chains:
    nres = len(chain)
    for residue in chain:
      # CALCULATE RMSD
      ysr.write("""for i=1 to LastObj
  AddTab rmsdatom %s and res %i and obj !(i), %s and res %i and obj (i)"""%(selstr,
                                                                                      residue.number,
                                                                                      selstr,
                                                                                      residue.number))
  # WRITE TABLE
  ysr.write(["SaveTab %s,2,%%7.3f,RMSD    SD"%tmptable])
  ysr.write(["Exit"])
  ysr.submit(conflag=1)
  # READ OUTPUT FILE AND PARSE RMSDS
  content = open(tmptable,'r').readlines()
  content = content[1:]
  nmod = len(content)/nres
  print nres, nmod, len(content)/float(nres)
  rmsds = []
  for i in range(nres):
    val = content[:nmod]
    content = content[nmod:]
    val = [float(el.split()[0]) for el in val]
    rmsds.append(avg_list(val,0))
  # CLEAN OUT FILES
  os.remove(tmptable)
  return rmsds


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
    self.atomchkerr = 0
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
      #print self.scriptpath
      # RUN XPLOR WITH THE SCRIPT
      log = os.popen("%s < %s"%(self.xplor,self.scriptpath))
      # CHECK FOR ERRORS
      xplorlog = log.read()
      skiperrors = string.count(xplorlog,"POWELL-ERR")
      errors     = string.count(xplorlog,"ERR")
      warnings   = string.count(xplorlog,"WRN")
      atomchks   = string.count(xplorlog,"ATMCHK-ERR")
      readcerr   = string.count(xplorlog,"READC-ERR")
      hcor = 0
      if xplorlog.find("HBUILD") != -1: hcor = readcerr
      # TAKE CARE OF ERRORS
      if errors-skiperrors-atomchks-hcor:
        file = open(self.logpath,'w')
        file.write(xplorlog)
        self.raiseerror("%s generated %i errors.\nLogfile: %s"%(self.progstr,errors-skiperrors,self.logpath))
      if atomchks:
        warning("Atom check error.")
        self.atomchkerr = 1
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
#    C N S _ S C R I P T   C L A S S
#  ======================================================================

class cns_script(xplor_script):

  # OPEN SCRIPT FILE FOR OUTPUT
  # ===========================
  # - cns IS THE COMMAND TO RUN CNS
  # - runpath IS THE PATH WHERE CNS IS RAN
  # - errorfunc IS THE NAME OF THE ERROR HANDLING FUNCTION
  def __init__(self,cns,scriptpath='/tmp',errorfunc=error,logfiles='delete'):
    self.xplor = cns
    self.progstr = "CNS"
    id = 1
    self.scriptpath = os.path.join(scriptpath,'%s_%i.in'%(self.progstr,os.getpid()))
    self.logpath = os.path.join(scriptpath,'%s_%i.log'%(self.progstr,os.getpid()))
    self.errorfunc=errorfunc
    self.logfiles = logfiles
    self.clear()


#  ======================================================================
#    C N S   C L A S S
#  ======================================================================

class cns:
  """
  This class is used to stores parameters pertaining to an CNS project.
  - Create a class instance by passing the command to run CNS.
  """
  def __init__(self,path):
    self.path = path


#  ======================================================================
#    C N S   F U N C T I O N   G R O U P
#  ======================================================================

# MTF 2 PSF
# =========
# CONVERT CNS MTF FILE TO XPLOR PSF FILE
def cns_mtf2psf(cnspath,mtffile,psffile):
  # CREATE CNS INPUT FILE
  cns = cns_script(cnspath)
  cns.write('structure @@%s end'%mtffile)
  cns.write('write psf output=%s end'%psffile)
  cns.submit()

# PSF 2 MTF
# =========
# CONVERT CNS MTF FILE TO XPLOR PSF FILE
def cns_psf2mtf(cnspath,psffile,mtffile):
  # CREATE CNS INPUT FILE
  cns = cns_script(cnspath)
  cns.write('structure @@%s end'%psffile)
  cns.write('write structure output=%s end'%mtffile)
  cns.submit()

# FORMAT LIST OF RESTRAINTS
# =========================
# FUNCTION READS A RESTRAINTLIST AND GROUPS IT FOR CNS
def cns_formatlist(restraintlist,disttbl,dihetbl):
  # CYCLE AND GROUP RESTRAINTS
  dist, dihe = [],[]
  for r in restraintlist:
    if r.type == 'DIST': dist.append(r)
    elif r.type == 'DIHE': dihe.append(r)
  # WRITE DIST
  distf = restraint_file(disttbl,'w')
  for r in dist:
    distf.write(r)
  distf.close()
  # WRITE DIHE
  dihef = restraint_file(dihetbl,'w','DIHE')
  for r in dihe:
    dihef.write(r)
  dihef.close()

# CALCULATE STRUCTURE
# ===================
# CALCULATE STRUCTURE BASED ON THE PROVIDED
# LIST OF EXPERIMENTAL RESTRAINTS
def cns_calcstructure(pdbbase,
                      template,
                      mtf,
                      restraintlist,
                      averaging='sum',
                      naccepted=20,
                      thr_noe=0.5,
                      thr_dih=5.0,
                      parameter=None,
                      cns=None,
                      seed=None,
                      ntrial=5):
  # TAKE DEFAULTS FOR PARAMETER AND XPLOR
  if not parameter: parameter = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_PAR"])
  if not cns: cns = nmvconf["CNS"]
  if not seed: seed = randint(10000,99999)
  # INITIALIZE THE CNS SCRIPT CLASS
  scriptpath = nmvconf["TMP"]
  cns = cns_script(cns,scriptpath)
  # GROUP RESTRAINTS, CNS TAKES COMPLETE FILES, SAVES WRITING
  # A FORMATTER WHICH WOULD HAVE SET A LOT OF PARAMETERS, THIS
  # WAY IT'S AUTOMATIC...
  disttbl = os.path.join(scriptpath,'%s_%i_DIST.tbl'%(cns.progstr,os.getpid()))
  dihetbl = os.path.join(scriptpath,'%s_%i_DIHE.tbl'%(cns.progstr,os.getpid()))
  cns_formatlist(restraintlist,disttbl,dihetbl)
  # CNS
  cns.write("""
  {- begin block parameter definition -} define(

  {======================= molecular structure =========================}

  {* type of non-bonded parameters *}
  {* specify the type of non-bonded interaction *}
  {+ choice: \"PROLSQ\" \"PARMALLH6\" \"PARALLHDG\" \"OPLSX\" +}
  {===>} par_nonbonded=\"PROLSQ\";

  {* parameter file(s) *}
  {===>} par.1=\"%s\";
  {===>} par.2=\"\";
  {===>} par.3=\"\";
  {===>} par.4=\"\";
  {===>} par.5=\"\";

  {* structure file(s) *}
  {===>} struct.1=\"%s\";
  {===>} struct.2=\"\";
  {===>} struct.3=\"\";
  {===>} struct.4=\"\";
  {===>} struct.5=\"\";

  {* input coordinate file(s) *}
  {===>} pdb.in.file.1=\"%s\";
  {===>} pdb.in.file.2=\"\";
  {===>} pdb.in.file.3=\"\";


  {========================== atom selection ===========================}

  {* input \"backbone\" selection criteria for average structure generation *}
  {* for protein      (name n or name ca or name c)
  for nucleic acid (name O5' or name C5' or name C4' or name C3'
                    or name O3' or name P) *}
  {===>} pdb.atom.select=(name n or name ca or name c);

  {====================== refinement parameters ========================}

  {* type of molecular dynamics for hot phase *}
  {+ choice: \"torsion\" \"cartesian\" +}
  {===>} md.type.hot=\"torsion\";

  {* type of molecular dynamics for cool phase *}
  {+ choice: \"torsion\" \"cartesian\" +}
  {===>} md.type.cool=\"torsion\";

  {* refine using different initial velocities or coordinates
  (enter base name in \"input coordinate files\" field) *}
  {+ choice: \"veloc\" \"coord\" +}
  {===>} md.type.initial=\"veloc\";

  {* seed for random number generator *}
  {* change to get different initial velocities *}
  {===>} md.seed=%s;

  {* select whether the number of structures will be either trial or
  accepted structures and whether to print only the trial, accepted,
  both sets of structures. *}
  {+ list: The printing format is as follows:
  trial =  + _#.pdb , accepted =  + a_#.pdb +}

  {* are the number of structures to be trials or accepted? *}
  {+ choice: \"trial\" \"accept\" +}
  {===>} flg.trial.struc=\"accept\";
  {* number of trial or accepted structures *}
  {===>} pdb.end.count=%i;

  {* print accepted structures *}
  {+ choice: true false +}
  {===>} flg.print.accept=true;
  {* print trial structures *}
  {+ choice: true false +}
  {===>} flg.print.trial=false;

  {* calculate an average structure for either the trial or
  accepted structure.  If calculate accepted average is false then
  an average for the trial structures will be calculated. *}

  {* calculate an average structure? *}
  {+ choice: true false +}
  {===>} flg.calc.ave.struct=false;
  {* calculate an average structure for the accepted structures? *}
  {+ choice: true false +}
  {===>} flg.calc.ave.accpt=false;
  {* minimize average coordinates? *}
  {+ choice: true false +}
  {===>} flg.min.ave.coor=false;

  {=================== torsion dynamics parameters ====================}

  {* maximum unbranched chain length *}
  {* increase for long stretches of polyalanine or for nucleic acids *}
  {===>} md.torsion.maxlength=50;

  {* maximum number of distinct bodies *}
  {===>} md.torsion.maxtree=4;

  {* maximum number of bonds to an atom *}
  {===>} md.torsion.maxbond=6;

  {========== parameters for high temperature annealing stage ==========}

  {* temperature (proteins: 50000, dna/rna: 20000) *}
  {===>} md.hot.temp=50000;
  {* number of steps (proteins: 1000, dna/rna: 4000) *}
  {===>} md.hot.step=1000;
  {* scale factor to reduce van der Waals (repel) energy term *}
  {===>} md.hot.vdw=0.1;
  {* scale factor for NOE energy term *}
  {===>} md.hot.noe=150;
  {* scale factor for dihedral angle energy term (proteins: 100, dna/rna: 5) *}
  {===>} md.hot.cdih=100;
  {* molecular dynamics timestep *}
  {===>} md.hot.ss=0.015;

  {======== parameters for the first slow-cool annealing stage =========}

  {* temperature (cartesian: 1000, torsion: [proteins: 50000, dna/rna: 20000]) *}
  {===>} md.cool.temp=50000;
  {* number of steps *}
  {===>} md.cool.step=1000;
  {* scale factor for final van der Waals (repel) energy term
  (cartesian: 4.0, torsion: 1.0) *}
  {===>} md.cool.vdw=1;
  {* scale factor for NOE energy term *}
  {===>} md.cool.noe=150;
  {* scale factor for dihedral angle energy term *}
  {===>} md.cool.cdih=200;
  {* molecular dynamics timestep (cartesian: 0.005, torsion: 0.015) *}
  {===>} md.cool.ss=0.015;
  {* slow-cool annealing temperature step (cartesian: 25, torsion: 250) *}
  {===>} md.cool.tmpstp=250;

  {========= parameters for a second slow-cool annealing stage ==========}

  {* cartesian slow-cooling annealing stage to be used only with torsion
  slow-cool annealing stage *}
  {* this stage is only necessary when the macromolecule is a protein
  greater than 160 residues or in some cases for nucleic acids *}

  {* use cartesian cooling stage? *}
  {+ choice: true false +}
  {===>} md.cart.flag=true;
  {* temperature *}
  {===>} md.cart.temp=2000;
  {* number of steps *}
  {===>} md.cart.step=3000;
  {* scale factor for initial van der Waals (repel) energy term *}
  {===>} md.cart.vdw.init=1.0;
  {* scale factor for final van der Waals (repel) energy term *}
  {===>} md.cart.vdw.finl=4.0;
  {* scale factor for NOE energy term *}
  {===>} md.cart.noe=150;
  {* scale factor for dihedral angle energy term *}
  {===>} md.cart.cdih=200;
  {* molecular dynamics timestep *}
  {===>} md.cart.ss=0.005;
  {* slow-cool annealing temperature step *}
  {===>} md.cart.tmpstp=50;

  {=============== parameters for final minimization stage ==============}

  {* scale factor for NOE energy term *}
  {===>} md.pow.noe=100;
  {* scale factor for dihedral angle energy term *}
  {===>} md.pow.cdih=400;
  {* number of minimization steps *}
  {===>} md.pow.step=200;
  {* number of cycles of minimization *}
  {===>} md.pow.cycl=2;

  {============================= noe data ===============================}

  {- Important - if you do not have a particular data set then
  set the file name to null (\"\") -}

  {* NOE distance restraints files. *}

  {* restraint set 1 file *}
  {===>} nmr.noe.file.1=\"%s\";
  {* restraint set 2 file *}
  {===>} nmr.noe.file.2=\"\";
  {* restraint set 3 file *}
  {===>} nmr.noe.file.3=\"\";
  {* restraint set 4 file *}
  {===>} nmr.noe.file.4=\"\";
  {* restraint set 5 file *}
  {===>} nmr.noe.file.5=\"\";

  {* NOE averaging modes *}

  {* restraint set 1 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.1=\"%s\";
  {* restraint set 2 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.2=\"sum\";
  {* restraint set 3 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.3=\"R-6\";
  {* restraint set 4 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.4=\"sum\";
  {* restraint set 5 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.5=\"sum\";

  {======================== hydrogen bond data ==========================}

  {* hydrogen-bond distance restraints file. *}
  {===>} nmr.noe.hbnd.file=\"\";

  {* enter hydrogen-bond distance averaging mode *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.hbnd=\"sum\";

  {======================= 3-bond J-coupling data =======================}
  {* the default setup is for the phi dihedral *}

  {* Class 1 *}

  {* 3-bond J-coupling non-glycine restraints file *}
  {===>} nmr.jcoup.file.1=\"\";
  {* 3-bond J-coupling non-glycine potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.jcoup.pot.1=\"harmonic\";
  {* 3-bond J-coupling non-glycine force value *}
  {===>} nmr.jcoup.force.1.1=1;
  {* 3-bond j-coupling multiple class force second value *}
  {===>} nmr.jcoup.force.2.1=0;
  {* 3-bond j-coupling Karplus coefficients *}
  {* the default values are for phi *}
  {===>} nmr.jcoup.coef.1.1=6.98;
  {===>} nmr.jcoup.coef.2.1=-1.38;
  {===>} nmr.jcoup.coef.3.1=1.72;
  {===>} nmr.jcoup.coef.4.1=-60.0;

  {* Class 2 *}

  {* 3-bond j-coupling glycine restraints files *}
  {===>} nmr.jcoup.file.2="";
  {* 3-bond J-coupling glycine potential *}
  {* The potential for the glycine class must be multiple *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.jcoup.pot.2=\"multiple\";
  {* 3-bond J-coupling first force value *}
  {===>} nmr.jcoup.force.1.2=1;
  {* 3-bond j-coupling glycine or multiple force second value *}
  {===>} nmr.jcoup.force.2.2=0;
  {* 3-bond j-coupling Karplus coefficients *}
  {* the default values are for glycine phi *}
  {===>} nmr.jcoup.coef.1.2=6.98;
  {===>} nmr.jcoup.coef.2.2=-1.38;
  {===>} nmr.jcoup.coef.3.2=1.72;
  {===>} nmr.jcoup.coef.4.2=0.0;

  {================ 1-bond heteronuclear J-coupling data ================}

  {* Class 1 *}

  {* 1-bond heteronuclear j-coupling file *}
  {===>} nmr.oneb.file.1="";
  {* 1-bond heteronuclear j-coupling potential *}
  {+ choice: \"harmonic\" \"square\" +}
  {===>} nmr.oneb.pot.1=\"harmonic\";
  {* 1-bond heteronuclear j-coupling force value *}
  {===>} nmr.oneb.force.1=1.0;

  {=============== alpha/beta carbon chemical shift data ================}

  {* Class 1 *}

  {* carbon, alpha and beta, chemical shift restraints file *}
  {===>} nmr.carb.file.1=\"\";
  {* carbon, alpha and beta, chemical shift restraint potential *}
  {+ choice: \"harmonic\" \"square\" +}
  {===>} nmr.carb.pot.1=\"harmonic\";
  {* carbon, alpha and beta, chemical shift restraint force value *}
  {===>} nmr.carb.force.1=0.5;

  {===================== proton chemical shift data =====================}

  {* Class 1 *}

  {* class 1 proton chemical shift restraints file *}
  {===>} nmr.prot.file.1=\"\";
  {* class 1 proton chemical shift potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.prot.pot.1=\"harmonic\";
  {* class 1 proton chemical shift force value *}
  {===>} nmr.prot.force.1.1=7.5;
  {* 2nd class 1 proton chemical shift force value for multi *}
  {===>} nmr.prot.force.2.1=0;
  {* class 1 proton chemical shift violation cutoff threshold *}
  {===>} nmr.prot.thresh.1=0.3;

  {* Class 2 *}

  {* class 2 proton chemical shift restraints file *}
  {===>} nmr.prot.file.2=\"\";
  {* class 2 proton chemical shift potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.prot.pot.2=\"harmonic\";
  {* class 2 proton chemical shift force value *}
  {===>} nmr.prot.force.1.2=7.5;
  {* 2nd class 2 proton chemical shift force value for multi *}
  {===>} nmr.prot.force.2.2=0;
  {* class 2 proton chemical shift violation cutoff threshold *}
  {===>} nmr.prot.thresh.2=0.3;

  {* Class 3 *}

  {* class 3 proton chemical shift restraints file *}
  {===>} nmr.prot.file.3=\"\";
  {* class 3 proton chemical shift potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.prot.pot.3=\"harmonic\";
  {* class 3 proton chemical shift force value *}
  {===>} nmr.prot.force.1.3=7.5;
  {* 2nd class 3 proton chemical shift force value for multi *}
  {===>} nmr.prot.force.2.3=0;
  {* class 3 proton chemical shift violation cutoff threshold *}
  {===>} nmr.prot.thresh.3=0.3;

  {* Class 4 *}

  {* class 4 proton chemical shift restraints file *}
  {===>} nmr.prot.file.4=\"\";
  {* class 4 proton chemical shift potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.prot.pot.4=\"multiple\";
  {* class 4 proton chemical shift force value *}
  {===>} nmr.prot.force.1.4=7.5;
  {* 2nd class 4 proton chemical shift force value for multi *}
  {===>} nmr.prot.force.2.4=0;
  {* class 4 proton chemical shift violation cutoff threshold *}
  {===>} nmr.prot.thresh.4=0.3;

  {================ diffusion anisotropy restraint data =================}

  {* fixed or harmonically restrained external axis *}
  {+ choice: \"fixed\" \"harm\" +}
  {===>} nmr.dani.axis=\"harm\";

  {* Class 1 *}

  {* diffusion anisotropy restraints file *}
  {===>} nmr.dani.file.1=\"\";
  {* diffusion anisotropy potential *}
  {+ choice: \"harmonic\" \"square\" +}
  {===>} nmr.dani.pot.1=\"harmonic\";
  {* diffusion anisotropy initial force value *}
  {===>} nmr.dani.force.init.1=0.01;
  {* diffusion anisotropy final force value *}
  {===>} nmr.dani.force.finl.1=1.0;
  {* diffusion anisotropy coefficients *}
  {* coef: <Tc> <anis> <rhombicity> <wh> <wn> *}

  {* Tc = 1/2(Dx+Dy+Dz) in <ns> *}
  {===>} nmr.dani.coef.1.1=13.1;
  {* anis = Dz/0.5*(Dx+Dy) *}
  {===>} nmr.dani.coef.2.1=2.1;
  {* rhombicity = 1.5*(Dy-Dx)/(Dz-0.5*(Dy+Dx)) *}
  {===>} nmr.dani.coef.3.1=0.0;
  {* wH in <MHz> *}
  {===>} nmr.dani.coef.4.1=600.13;
  {* wN in <MHz> *}
  {===>} nmr.dani.coef.5.1=60.82;

  {============= susceptability anisotropy restraint data ===============}

  {* fixed or harmonically restrained external axis *}
  {+ choice: \"fixed\" \"harm\" +}
  {===>} nmr.sani.axis=\"harm\";

  {* Class 1 *}

  {* susceptability anisotropy restraints file *}
  {===>} nmr.sani.file.1=\"\";
  {* susceptability anisotropy potential *}
  {+ choice: \"harmonic\" \"square\" +}
  {===>} nmr.sani.pot.1=\"harmonic\";
  {* susceptability anisotropy initial force value *}
  {===>} nmr.sani.force.init.1=0.01;
  {* susceptability anisotropy final force value *}
  {===>} nmr.sani.force.finl.1=50.0;
  {* susceptability anisotropy coefficients *}
  {* coef: <DFS> <axial > <rhombicity>;
  a0+a1*(3*cos(theta)^2-1)+a2*(3/2)*sin(theta)^2*cos(2*phi) *}

  {* DFS = a0 *}
  {===>} nmr.sani.coef.1.1=-0.0601;
  {* axial = a0-a1-3/2*a2 *}
  {===>} nmr.sani.coef.2.1=-8.02;
  {* rhombicity = a2/a1 *}
  {===>} nmr.sani.coef.3.1=0.4;

  {======================== other restraint data ========================}

  {* dihedral angle restraints file *}
  {* Note: the restraint file MUST NOT contain restraints
  dihedral or end *}
  {===>} nmr.cdih.file=\"%s\";

  {* DNA-RNA base planarity restraints file *}
  {* Note: include weights as $pscale in the restraint file *}
  {===>} nmr.plan.file=\"\";
  {* input planarity scale factor - this will be written into $pscale *}
  {===>} nmr.plan.scale=150;

  {* NCS-restraints file *}
  {* example is in inputs/xtal_data/eg1_ncs_restrain.dat *}
  {===>} nmr.ncs.file=\"\";

  {======================== input/output files ==========================}

  {* base name for input coordinate files *}
  {===>} pdb.in.name=\"\";

  {* base name for output coordinate files *}
  {===>} pdb.out.name=\"%s_\";

  {===========================================================================}
  {         things below this line do not normally need to be changed         }
  {         except for the torsion angle topology setup if you have           }
  {         molecules other than protein or nucleic acid                      }
  {===========================================================================}
  flg.cv.flag=false;
  flg.cv.noe=false;
  flg.cv.coup=false;
  flg.cv.cdih=false;
  flg.dgsa.flag=false;
  nmr.cv.numpart=10;

  ) {- end block parameter definition -}

  """%(parameter,mtf,template,seed,naccepted,disttbl,averaging,dihetbl,pdbbase))
  # THE ACTUAL WORK!
  cns.write("""
  checkversion 1.1

  evaluate ($log_level=quiet)

  structure
     if  (&struct.1 # \"\") then
        @@&struct.1
     end if
     if  (&struct.2 # \"\") then
        @@&struct.2
     end if
     if  (&struct.3 # \"\") then
        @@&struct.3
     end if
     if  (&struct.4 # \"\") then
        @@&struct.4
     end if
     if  (&struct.5 # \"\") then
        @@&struct.5
     end if
  end

  if ( &BLANK%%pdb.in.file.1 = false ) then
     coor @@&pdb.in.file.1
  end if
  if ( &BLANK%%pdb.in.file.2 = false ) then
     coor @@&pdb.in.file.2
  end if
  if ( &BLANK%%pdb.in.file.3 = false ) then
     coor @@&pdb.in.file.3
  end if

  parameter
     if ( &par_nonbonded = \"PROLSQ\" ) then
       evaluate ($par_nonbonded = \"PROLSQ\")
     end if
     if ( &par_nonbonded = \"OPLSX\" ) then
       evaluate ($par_nonbonded = \"OPLSX\")
     end if
     if ( &par_nonbonded = \"PARMALLH6\" ) then
       evaluate ($par_nonbonded = \"PARMALLH6\")
     end if
     if ( &par_nonbonded = \"PARALLHDG\" ) then
       evaluate ($par_nonbonded = \"PARALLHDG\")
     end if
     if (&par.1 # \"\") then
        @@&par.1
     end if
     if (&par.2 # \"\") then
        @@&par.2
     end if
     if (&par.3 # \"\") then
        @@&par.3
     end if
     if (&par.4 # \"\") then
        @@&par.4
     end if
     if (&par.5 # \"\") then
        @@&par.5
     end if
  end

  if ( $log_level = verbose ) then
    set message=normal echo=on end
  else
    set message=off echo=off end
  end if

  parameter
     nbonds
        repel=0.80
        rexp=2 irexp=2 rcon=1.
        nbxmod=3
        wmin=0.01
        cutnb=6.0 ctonnb=2.99 ctofnb=3.
        tolerance=1.5
     end
  end

  {- Read experimental data -}

     @CNS_NMRMODULE:readdata ( nmr=&nmr;
                               flag=&flg;
                               output=$nmr; )

  {- Read and store the number of NMR restraints -}

     @CNS_NMRMODULE:restraintnumber ( num=$num; )

  {- Set mass values -}

  do (fbeta=10) (all)
  do (mass=100) (all)

  evaluate ($nmr.trial.count = 0)    {- Initialize current structure number   -}
  evaluate ($nmr.accept.count = 0)   {- Initialize number accepted            -}
  evaluate ($nmr.counter 	= 0)
  evaluate ($nmr.prev.counter = -1)

  @CNS_NMRMODULE:initave  ( ave=$ave;
                            ave2=$ave2;
                            cv=$cv;
                            ener1=$ener1;
                            ener2=$ener2;
                            flag=&flg;
                            nmr.prot=&nmr.prot; )

  {- Zero the force constant of disulfide bonds. -}
  parameter
     bonds ( name SG ) ( name SG ) 0. TOKEN
  end

  {- define a distance restraints for each disulfide bond, i.e.,
     treat it as if it were an NOE. -}
  for $ss_rm_id_1 in id ( name SG ) loop STRM
    for $ss_rm_id_2 in id ( name SG and
                            bondedto ( id $ss_rm_id_1 )  ) loop STR2
      if ($ss_rm_id_1 > $ss_rm_id_2) then
        pick bond ( id $ss_rm_id_1 ) ( id $ss_rm_id_2 ) equil
        evaluate ($ss_bond=$result)
        noe
           assign ( id $ss_rm_id_1 ) ( id $ss_rm_id_2 ) $ss_bond 0.1 0.1
        end
      end if
    end loop STR2
  end loop STRM

  {- Count the number of residues and determine molecule type -}
  identify (store9) (tag)
  evaluate ($nmr.rsn.num = $SELECT)
  identify (store9) ( tag and ( resn THY or resn CYT or resn GUA or
                                resn ADE or resn URI ))
  evaluate ($nmr.nucl.num = $SELECT)

  {- Improve geometry for torsion angle molecular dynamics -}
  evaluate ($flag_tad=false)
  if ( &md.type.hot = \"torsion\" ) then
     if ($nmr.nucl.num > 0) then
        flag exclude * include bond angl impr dihed vdw end
        minimize powell nstep=2000 drop=10.  nprint=100 end
     else
        flag exclude * include bond angl impr vdw end
        minimize powell nstep=2000 drop=10.  nprint=100 end
     end if
     evaluate ($flag_tad=true)
  end if

  if ( &md.type.cool=\"torsion\") then
     evaluate ($flag_tad=true)
  end if

  if (&nmr.dani.axis = \"harm\") then
     do (harmonic=20.0) (resid 500 and name OO)
     do (harmonic=0.0) (resid 500 and name Z )
     do (harmonic=0.0) (resid 500 and name X )
     do (harmonic=0.0) (resid 500 and name Y )
     do (harmonic=0.0) (not (resid 500))
     restraints harmonic exponent=2 end
  elseif (&nmr.sani.axis = \"harm\") then
     do (harmonic=20.0) (resid 500 and name OO)
     do (harmonic=0.0) (resid 500 and name Z )
     do (harmonic=0.0) (resid 500 and name X )
     do (harmonic=0.0) (resid 500 and name Y )
     do (harmonic=0.0) (not (resid 500))
     restraints harmonic exponent=2 end
  end if

  do (refx=x) ( all )
  do (refy=y) ( all )
  do (refz=z) ( all )

  set seed=&md.seed end

  {- Begin protocol to generate structures -- loop until done -}
  while (&pdb.end.count > $nmr.counter) loop main
     evaluate ($maxcount = %i)
     if ($nmr.trial.count >= $maxcount ) then
         display  ****&&&& ENDCOUNT REACHED, NO CONVERGENCE
         stop
       end if
     {- Set parameter values -}
     parameter
        nbonds
           repel=0.80
           rexp=2 irexp=2 rcon=1.
           nbxmod=3
           wmin=0.01
           cutnb=6.0 ctonnb=2.99 ctofnb=3.
           tolerance=1.5
        end
     end

     evaluate ($nmr.trial.count = $nmr.trial.count + 1)

     if (&md.type.initial = \"coord\") then
        if ($nmr.trial.count < &pdb.end.count) then
           evaluate ($coor_count = $nmr.trial.count)
           evaluate ($coor_count_init=0.)
        else
           evaluate ($coor_count_init=$coor_count_init+1)
           evaluate ($coor_count = $coor_count_init)
           if ($coor_count_init > &pdb.end.count ) then
              evaluate ($coor_count = 1)
           end if
        end if
        set remarks=reset end
        evaluate ($in_file = &pdb.in.name + \"_\" + encode($coor_count) + \".pdb\")
        coor @@$in_file
     else
        do (x=refx) ( all )
        do (y=refy) ( all )
        do (z=refz) ( all )
     end if

     if (&nmr.dani.axis = \"fixed\" ) then
        fix
           select=(resname ANI)
        end
     elseif (&nmr.sani.axis = \"fixed\" ) then
        fix
           select=(resname ANI)
        end
     end if

     do ( vx = maxwell(0.5) ) ( all )
     do ( vy = maxwell(0.5) ) ( all )
     do ( vz = maxwell(0.5) ) ( all )

     flags exclude *
           include bond angle dihe impr vdw
                   noe cdih coup oneb carb ncs dani
                   sani harm end

     {- scaling of nmr restraint data during hot dynamics -}

     @CNS_NMRMODULE:scalehot ( md=&md;
                               nmr=&nmr;
                               input.noe.scale=&md.hot.noe;
                               input.cdih.scale=&md.hot.cdih; )

     {- Zero the force constant of disulfide bonds. -}
     parameter
        bonds ( name SG ) ( name SG ) 0. TOKEN
     end

     if ($flag_tad=true) then

        {- initialize torsion dynamics topology for this iteration -}

        dyna torsion
           topology
              maxlength=&md.torsion.maxlength
              maxtree=&md.torsion.maxtree
              maxbond=&md.torsion.maxbond
              {- All dihedrals w/ (force constant > 23) will be locked -}
              {- This keeps planar groups planar -}
              kdihmax = 23.
              @CNS_TOPPAR:torsionmdmods
           end
        end
     end if

  {- High temperature dynamics -}

     if ( &md.type.hot = \"torsion\" ) then

        igroup
           interaction (chemical h* ) (all) weights * 1 vdw 0. elec 0. end
           interaction (not chemical h* ) (not chemical h*) weights * 1 vdw &md.hot.vdw
           end
        end

        dyna torsion
           cmperiodic=500
           vscaling = false
           tcoupling = true
           timestep = &md.hot.ss
           nstep = &md.hot.step
           nprint = 50
           temperature = &md.hot.temp
        end
     else
        evaluate ($md.hot.nstep1=int(&md.hot.step* 2. / 3. ))
        evaluate ($md.hot.nstep2=int(&md.hot.step* 1. / 3. ))
        noe asymptote * 0.1  end
        parameter  nbonds repel=1.   end end
        igroup
           interaction (chemical h* ) (all) weights * 1 vdw 0. elec 0. end
           interaction (not chemical h* ) (not chemical h*) weights * 1 angl 0.4 impr 0.1
                       vdw &md.hot.vdw end
        end

        dynamics cartesian
           cmperiodic=500
           vscaling = true
           tcoupling=false
           timestep=&md.hot.ss
           nstep=$md.hot.nstep1
           nprint=50
           temperature=&md.hot.temp
        end

        noe asymptote * 1.0  end
        igroup
           interaction (chemical h* ) (all) weights * 1 vdw 0. elec 0. end
           interaction (not chemical h* ) (not chemical h*) weights * 1 vdw &md.hot.vdw end
        end

        dynamics cartesian
           cmperiodic=500
           vscaling = true
           tcoupling=false
           timestep=&md.hot.ss
           nstep=$md.hot.nstep2
           nprint=50
           temperature=&md.hot.temp
        end

     end if

  {- The first slow-cooling with torsion angle dynamics -}

     flags include plan end

     {- Increase the disulfide bond force constants to their full strength -}
     parameter
        bonds ( name SG ) ( name SG ) 1000. TOKEN
     end

     evaluate ($final_t = 0)

     evaluate ($ncycle = int((&md.cool.temp-$final_t)/&md.cool.tmpstp))
     evaluate ($nstep = int(&md.cool.step/$ncycle))

     evaluate ($ini_vdw =  &md.hot.vdw)
     evaluate ($fin_vdw =  &md.cool.vdw)
     evaluate ($vdw_step = ($fin_vdw-$ini_vdw)/$ncycle)

     if (&md.type.cool = \"cartesian\") then

        evaluate ($vdw_step = (&md.cool.vdw/&md.hot.vdw)^(1/$ncycle))
        evaluate ($ini_rad  = 0.9)
        evaluate ($fin_rad  = 0.8)
        evaluate ($rad_step = ($ini_rad-$fin_rad)/$ncycle)
        evaluate ($radius=    $ini_rad)

        do (vx=maxwell(&md.cool.temp)) ( all )
        do (vy=maxwell(&md.cool.temp)) ( all )
        do (vz=maxwell(&md.cool.temp)) ( all )

     end if

     {- set up nmr restraint scaling -}

     evaluate ($kdani.inter.flag=false)
     evaluate ($ksani.inter.flag=false)
     evaluate ($kdani.cart.flag=false)
     evaluate ($ksani.cart.flag=false)
     if (&md.cart.flag=true) then
        evaluate ($kdani.inter.flag=true)
        evaluate ($ksani.inter.flag=true)
        @CNS_NMRMODULE:scalecoolsetup ( kdani=$kdani;
                                        ksani=$ksani;
                                        nmr=&nmr;
                                        input.noe.scale=&md.cool.noe;
                                        input.cdih.scale=&md.cool.cdih;
                                        input.ncycle=$ncycle; )
        evaluate ($kdani.cart.flag=true)
        evaluate ($ksani.cart.flag=true)
     else
        @CNS_NMRMODULE:scalecoolsetup ( kdani=$kdani;
                                        ksani=$ksani;
                                        nmr=&nmr;
                                        input.noe.scale=&md.cool.noe;
                                        input.cdih.scale=&md.cool.cdih;
                                        input.ncycle=$ncycle; )
     end if

     evaluate ($bath  = &md.cool.temp)
     evaluate ($k_vdw = $ini_vdw)

     evaluate ($i_cool = 0)
     while ($i_cool <= $ncycle) loop cool
        evaluate ($i_cool = $i_cool + 1)

        igroup
           interaction (chemical h*) (all) weights * 1 vdw 0. elec 0. end
           interaction (not chemical h*) (not chemical h*) weights * 1 vdw $k_vdw end
        end

        if ( &md.type.cool = \"torsion\" ) then
           dynamics  torsion
              cmremove=true
              vscaling = true
              tcoup = false
              timestep = &md.cool.ss
              nstep = $nstep
              nprint = $nstep
              temperature = $bath
           end
        else
           dynamics  cartesian
              cmremove=true
              vscaling = true
              tcoup = false
              timestep = &md.cool.ss
              nstep = $nstep
              nprint = $nstep
              temperature = $bath
           end
        end if

        if (&md.type.cool = \"cartesian\") then
           evaluate ($radius=max($fin_rad,$radius-$rad_step))
           parameter  nbonds repel=$radius   end end
           evaluate ($k_vdw=min($fin_vdw,$k_vdw*$vdw_step))
        else
           evaluate ($k_vdw= $k_vdw + $vdw_step)
        end if
        evaluate ($bath  = $bath  - &md.cool.tmpstp)

        @CNS_NMRMODULE:scalecool ( kdani=$kdani;
                                   ksani=$ksani;
                                   nmr=&nmr; )

     end loop cool

  {- A second slow-cooling with cartesian dyanmics -}

     evaluate ($flag_cart=false)
     if (&md.cart.flag=true) then
        if (&md.type.cool = \"torsion\") then

           evaluate ($flag_cart=true)

           dynamics torsion
              topology
                 reset
              end
           end

           evaluate ($cart_nucl_flag=false)
           if ($nmr.nucl.num > 0) then
              evaluate ($cart_nucl_flag=true)
              parameter
                 nbonds
                    repel=0
                    nbxmod=5
                    wmin=0.01
                    tolerance=0.5
                    cutnb=11.5 ctonnb=9.5 ctofnb=10.5
                    rdie vswitch switch
                 end
              end
              flags include elec end
           end if

           evaluate ($ncycle=int((&md.cart.temp-$final_t)/&md.cart.tmpstp))
           evaluate ($nstep=int(&md.cart.step/$ncycle))

           evaluate ($vdw_step=(&md.cart.vdw.finl/&md.cart.vdw.init)^(1/$ncycle))
           evaluate ($ini_rad=0.9)
           evaluate ($fin_rad=0.8)
           evaluate ($rad_step=($ini_rad-$fin_rad)/$ncycle)
           evaluate ($radius=$ini_rad)

           @CNS_NMRMODULE:scalecoolsetup ( kdani=$kdani;
                                           ksani=$ksani;
                                           nmr=&nmr;
                                           input.noe.scale=&md.cart.noe;
                                           input.cdih.scale=&md.cart.cdih;
                                           input.ncycle=$ncycle; )

           do (vx=maxwell(&md.cart.temp)) ( all )
           do (vy=maxwell(&md.cart.temp)) ( all )
           do (vz=maxwell(&md.cart.temp)) ( all )

           evaluate ($bath=&md.cart.temp)
           evaluate ($k_vdw=&md.cart.vdw.init)

           evaluate ($i_cool = 0)
           while ($i_cool <= $ncycle) loop cart
              evaluate ($i_cool = $i_cool + 1)

              igroup
                 interaction (chemical h*) (all) weights * 1 vdw 0. elec 0. end
                 interaction (not chemical h*) (not chemical h*) weights * 1 vdw $k_vdw
                 end
              end

              dynamics  cartesian
                 vscaling = true
                 tcoup = false
                 timestep = &md.cart.ss
                 nstep = $nstep
                 nprint = $nstep
                 temperature = $bath
              end

              if ($cart_nucl_flag=false) then
                 evaluate ($radius=max($fin_rad,$radius-$rad_step))
                 parameter  nbonds repel=$radius   end end
              end if
              evaluate ($k_vdw=min(&md.cart.vdw.finl,$k_vdw*$vdw_step))
              evaluate ($bath=$bath-&md.cart.tmpstp)

              @CNS_NMRMODULE:scalecool ( kdani=$kdani;
                                         ksani=$ksani;
                                         nmr=&nmr; )

           end loop cart

        end if
     end if

     {- reset torsion angle topology -}
     if ( $flag_tad=true ) then
        if ($flag_cart=false) then
           dynamics torsion
              topology
                 reset
              end
           end
        end if
     end if


  {- Final minimization -}

     {- turn on proton chemical shifts -}

     flags include prot end

     noe
        scale * &md.pow.noe
     end

     restraints dihedral
        scale = &md.pow.cdih
     end

     igroup interaction ( all ) ( all ) weights * 1 end end

     evaluate ($count=0 )
     evaluate ($nmr.min.num=0.)
     while (&md.pow.cycl > $count) loop pmini

        evaluate ($count=$count + 1)
        minimize powell nstep=&md.pow.step drop=10.0 nprint=25 end
        evaluate ($nmr.min.num=$nmr.min.num + $mini_cycles)

     end loop pmini

     {- translate the geometric center of the structure to the origin -}
     if ($num.dani > 0. ) then
     elseif ($num.sani > 0. ) then
     else
        show ave ( x ) ( all )
        evaluate ($geom_x=-$result)
        show ave ( y ) ( all )
        evaluate ($geom_y=-$result)
        show ave ( z ) ( all )
        evaluate ($geom_z=-$result)
        coor translate vector=( $geom_x $geom_y $geom_z ) selection=( all ) end
     end if


     @CNS_NMRMODULE:printaccept ( ave=$ave;
                                  ave2=$ave2;
                                  cv=$cv;
                                  ener1=$ener1;
                                  ener2=$ener2;
                                  flag=&flg;
                                  md=&md;
                                  nmr=&nmr;
                                  num=$num;
                                  output=$nmr;
                                  pdb=&pdb;  )

  end loop main

     @CNS_NMRMODULE:calcave ( ave=$ave;
                              ave2=$ave2;
                              cv=$cv;
                              ener1=$ener1;
                              ener2=$ener2;
                              flag=&flg;
                              md=&md;
                              nmr=&nmr;
                              num=$num;
                              output=$nmr;
                              pdb=&pdb;  )


  stop
  """%(naccepted*ntrial))

  # SUBMIT XPLOR JOB
  cns.submit()
  # CLEANUP
  os.remove(disttbl)
  os.remove(dihetbl)

# CALCULATE STRUCTURE CV
# ======================
# CALCULATE STRUCTURE BASED ON THE PROVIDED
# LIST OF EXPERIMENTAL RESTRAINTS
# USES COMPLETE CROSS VALIDATION
def cns_calcstructurecv(pdbbase,
                        template,
                        mtf,
                        restraintlist,
                        averaging='sum',
                        naccepted=20,
                        thr_noe=0.5,
                        thr_dih=5.0,
                        parameter=None,
                        cns=None,
                        seed=None,
                        ntrial=5):
  # TAKE DEFAULTS FOR PARAMETER AND XPLOR
  if not parameter: parameter = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_PAR"])
  if not cns: cns = nmvconf["CNS"]
  if not seed: seed = randint(10000,99999)
  # INITIALIZE THE CNS SCRIPT CLASS
  scriptpath = nmvconf["TMP"]
  cns = cns_script(cns,scriptpath,logfiles='keep')
  # GROUP RESTRAINTS, CNS TAKES COMPLETE FILES, SAVES WRITING
  # A FORMATTER WHICH WOULD HAVE SET A LOT OF PARAMETERS, THIS
  # WAY IT'S AUTOMATIC...
  disttbl = os.path.join(scriptpath,'%s_%i_DIST.tbl'%(cns.progstr,os.getpid()))
  dihetbl = os.path.join(scriptpath,'%s_%i_DIHE.tbl'%(cns.progstr,os.getpid()))
  cns_formatlist(restraintlist,disttbl,dihetbl)
  dist = [el for el in restraintlist if el.type=='DIST']
  dihe = [el for el in restraintlist if el.type=='DIHE']
  if len(dist)>0: distflag = 'true'
  else: distflag = 'false'
  if len(dihe)>0: diheflag = 'true'
  else: diheflag = 'false'
  # CNS
  cns.write("""
  {- begin block parameter definition -} define(

  {======================= molecular structure =========================}

  {* type of non-bonded parameters *}
  {* specify the type of non-bonded interaction *}
  {+ choice: \"PROLSQ\" \"PARMALLH6\" \"PARALLHDG\" \"OPLSX\" +}
  {===>} par_nonbonded=\"PROLSQ\";

  {* parameter file(s) *}
  {===>} par.1=\"%s\";
  {===>} par.2=\"\";
  {===>} par.3=\"\";
  {===>} par.4=\"\";
  {===>} par.5=\"\";

  {* structure file(s) *}
  {===>} struct.1=\"%s\";
  {===>} struct.2=\"\";
  {===>} struct.3=\"\";
  {===>} struct.4=\"\";
  {===>} struct.5=\"\";

  {* input coordinate file(s) *}
  {===>} pdb.in.file.1=\"%s\";
  {===>} pdb.in.file.2=\"\";
  {===>} pdb.in.file.3=\"\";


  {========================== atom selection ===========================}

  {* input \"backbone\" selection criteria for average structure generation *}
  {* for protein      (name n or name ca or name c)
  for nucleic acid (name O5' or name C5' or name C4' or name C3'
                    or name O3' or name P) *}
  {===>} pdb.atom.select=(name n or name ca or name c);

  {====================== refinement parameters ========================}

  {* type of molecular dynamics for hot phase *}
  {+ choice: \"torsion\" \"cartesian\" +}
  {===>} md.type.hot=\"torsion\";

  {* type of molecular dynamics for cool phase *}
  {+ choice: \"torsion\" \"cartesian\" +}
  {===>} md.type.cool=\"torsion\";

  {* refine using different initial velocities or coordinates
  (enter base name in \"input coordinate files\" field) *}
  {+ choice: \"veloc\" \"coord\" +}
  {===>} md.type.initial=\"veloc\";

  {* seed for random number generator *}
  {* change to get different initial velocities *}
  {===>} md.seed=%s;

  {* select whether the number of structures will be either trial or
  accepted structures and whether to print only the trial, accepted,
  both sets of structures. *}
  {+ list: The printing format is as follows:
  trial =  + _#.pdb , accepted =  + a_#.pdb +}

  {* are the number of structures to be trials or accepted? *}
  {+ choice: \"trial\" \"accept\" +}
  {===>} flg.trial.struc=\"accept\";
  {* number of trial or accepted structures *}
  {===>} pdb.end.count=%i;

  {* print accepted structures *}
  {+ choice: true false +}
  {===>} flg.print.accept=true;
  {* print trial structures *}
  {+ choice: true false +}
  {===>} flg.print.trial=false;

  {* calculate an average structure for either the trial or
  accepted structure.  If calculate accepted average is false then
  an average for the trial structures will be calculated. *}

  {* calculate an average structure? *}
  {+ choice: true false +}
  {===>} flg.calc.ave.struct=false;
  {* calculate an average structure for the accepted structures? *}
  {+ choice: true false +}
  {===>} flg.calc.ave.accpt=false;
  {* minimize average coordinates? *}
  {+ choice: true false +}
  {===>} flg.min.ave.coor=false;

  {=================== torsion dynamics parameters ====================}

  {* maximum unbranched chain length *}
  {* increase for long stretches of polyalanine or for nucleic acids *}
  {===>} md.torsion.maxlength=50;

  {* maximum number of distinct bodies *}
  {===>} md.torsion.maxtree=4;

  {* maximum number of bonds to an atom *}
  {===>} md.torsion.maxbond=6;

  {========== parameters for high temperature annealing stage ==========}

  {* temperature (proteins: 50000, dna/rna: 20000) *}
  {===>} md.hot.temp=50000;
  {* number of steps (proteins: 1000, dna/rna: 4000) *}
  {===>} md.hot.step=1000;
  {* scale factor to reduce van der Waals (repel) energy term *}
  {===>} md.hot.vdw=0.1;
  {* scale factor for NOE energy term *}
  {===>} md.hot.noe=150;
  {* scale factor for dihedral angle energy term (proteins: 100, dna/rna: 5) *}
  {===>} md.hot.cdih=100;
  {* molecular dynamics timestep *}
  {===>} md.hot.ss=0.015;

  {======== parameters for the first slow-cool annealing stage =========}

  {* temperature (cartesian: 1000, torsion: [proteins: 50000, dna/rna: 20000]) *}
  {===>} md.cool.temp=50000;
  {* number of steps *}
  {===>} md.cool.step=1000;
  {* scale factor for final van der Waals (repel) energy term
  (cartesian: 4.0, torsion: 1.0) *}
  {===>} md.cool.vdw=1;
  {* scale factor for NOE energy term *}
  {===>} md.cool.noe=150;
  {* scale factor for dihedral angle energy term *}
  {===>} md.cool.cdih=200;
  {* molecular dynamics timestep (cartesian: 0.005, torsion: 0.015) *}
  {===>} md.cool.ss=0.015;
  {* slow-cool annealing temperature step (cartesian: 25, torsion: 250) *}
  {===>} md.cool.tmpstp=250;

  {========= parameters for a second slow-cool annealing stage ==========}

  {* cartesian slow-cooling annealing stage to be used only with torsion
  slow-cool annealing stage *}
  {* this stage is only necessary when the macromolecule is a protein
  greater than 160 residues or in some cases for nucleic acids *}

  {* use cartesian cooling stage? *}
  {+ choice: true false +}
  {===>} md.cart.flag=true;
  {* temperature *}
  {===>} md.cart.temp=2000;
  {* number of steps *}
  {===>} md.cart.step=3000;
  {* scale factor for initial van der Waals (repel) energy term *}
  {===>} md.cart.vdw.init=1.0;
  {* scale factor for final van der Waals (repel) energy term *}
  {===>} md.cart.vdw.finl=4.0;
  {* scale factor for NOE energy term *}
  {===>} md.cart.noe=150;
  {* scale factor for dihedral angle energy term *}
  {===>} md.cart.cdih=200;
  {* molecular dynamics timestep *}
  {===>} md.cart.ss=0.005;
  {* slow-cool annealing temperature step *}
  {===>} md.cart.tmpstp=50;

  {=============== parameters for final minimization stage ==============}

  {* scale factor for NOE energy term *}
  {===>} md.pow.noe=100;
  {* scale factor for dihedral angle energy term *}
  {===>} md.pow.cdih=400;
  {* number of minimization steps *}
  {===>} md.pow.step=200;
  {* number of cycles of minimization *}
  {===>} md.pow.cycl=2;

  {==================== complete cross validation =======================}

  {* would you like to perform complete cross validation? *}
  {+ choice: true false +}
  {===>} flg.cv.flag=true;
  {* the number of data partitions *}
  {===>} nmr.cv.numpart=10;
  {* for NOEs excluding h-bonds? *}
  {+ choice: true false +}
  {===>} flg.cv.noe=%s;
  {* for 3-bond J-coupling? *}
  {+ choice: true false +}
  {===>} flg.cv.coup=false;
  {* for dihedral restraints? *}
  {+ choice: true false +}
  {===>} flg.cv.cdih=%s;

  {============================= noe data ===============================}

  {- Important - if you do not have a particular data set then
  set the file name to null (\"\") -}

  {* NOE distance restraints files. *}

  {* restraint set 1 file *}
  {===>} nmr.noe.file.1=\"%s\";
  {* restraint set 2 file *}
  {===>} nmr.noe.file.2=\"\";
  {* restraint set 3 file *}
  {===>} nmr.noe.file.3=\"\";
  {* restraint set 4 file *}
  {===>} nmr.noe.file.4=\"\";
  {* restraint set 5 file *}
  {===>} nmr.noe.file.5=\"\";

  {* NOE averaging modes *}

  {* restraint set 1 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.1=\"%s\";
  {* restraint set 2 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.2=\"sum\";
  {* restraint set 3 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.3=\"R-6\";
  {* restraint set 4 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.4=\"sum\";
  {* restraint set 5 *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.5=\"sum\";

  {======================== hydrogen bond data ==========================}

  {* hydrogen-bond distance restraints file. *}
  {===>} nmr.noe.hbnd.file=\"\";

  {* enter hydrogen-bond distance averaging mode *}
  {+ choice: \"sum\" \"cent\" \"R-6\" \"R-3\" \"symm\" +}
  {===>} nmr.noe.ave.mode.hbnd=\"sum\";

  {======================= 3-bond J-coupling data =======================}
  {* the default setup is for the phi dihedral *}

  {* Class 1 *}

  {* 3-bond J-coupling non-glycine restraints file *}
  {===>} nmr.jcoup.file.1=\"\";
  {* 3-bond J-coupling non-glycine potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.jcoup.pot.1=\"harmonic\";
  {* 3-bond J-coupling non-glycine force value *}
  {===>} nmr.jcoup.force.1.1=1;
  {* 3-bond j-coupling multiple class force second value *}
  {===>} nmr.jcoup.force.2.1=0;
  {* 3-bond j-coupling Karplus coefficients *}
  {* the default values are for phi *}
  {===>} nmr.jcoup.coef.1.1=6.98;
  {===>} nmr.jcoup.coef.2.1=-1.38;
  {===>} nmr.jcoup.coef.3.1=1.72;
  {===>} nmr.jcoup.coef.4.1=-60.0;

  {* Class 2 *}

  {* 3-bond j-coupling glycine restraints files *}
  {===>} nmr.jcoup.file.2="";
  {* 3-bond J-coupling glycine potential *}
  {* The potential for the glycine class must be multiple *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.jcoup.pot.2=\"multiple\";
  {* 3-bond J-coupling first force value *}
  {===>} nmr.jcoup.force.1.2=1;
  {* 3-bond j-coupling glycine or multiple force second value *}
  {===>} nmr.jcoup.force.2.2=0;
  {* 3-bond j-coupling Karplus coefficients *}
  {* the default values are for glycine phi *}
  {===>} nmr.jcoup.coef.1.2=6.98;
  {===>} nmr.jcoup.coef.2.2=-1.38;
  {===>} nmr.jcoup.coef.3.2=1.72;
  {===>} nmr.jcoup.coef.4.2=0.0;

  {================ 1-bond heteronuclear J-coupling data ================}

  {* Class 1 *}

  {* 1-bond heteronuclear j-coupling file *}
  {===>} nmr.oneb.file.1="";
  {* 1-bond heteronuclear j-coupling potential *}
  {+ choice: \"harmonic\" \"square\" +}
  {===>} nmr.oneb.pot.1=\"harmonic\";
  {* 1-bond heteronuclear j-coupling force value *}
  {===>} nmr.oneb.force.1=1.0;

  {=============== alpha/beta carbon chemical shift data ================}

  {* Class 1 *}

  {* carbon, alpha and beta, chemical shift restraints file *}
  {===>} nmr.carb.file.1=\"\";
  {* carbon, alpha and beta, chemical shift restraint potential *}
  {+ choice: \"harmonic\" \"square\" +}
  {===>} nmr.carb.pot.1=\"harmonic\";
  {* carbon, alpha and beta, chemical shift restraint force value *}
  {===>} nmr.carb.force.1=0.5;

  {===================== proton chemical shift data =====================}

  {* Class 1 *}

  {* class 1 proton chemical shift restraints file *}
  {===>} nmr.prot.file.1=\"\";
  {* class 1 proton chemical shift potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.prot.pot.1=\"harmonic\";
  {* class 1 proton chemical shift force value *}
  {===>} nmr.prot.force.1.1=7.5;
  {* 2nd class 1 proton chemical shift force value for multi *}
  {===>} nmr.prot.force.2.1=0;
  {* class 1 proton chemical shift violation cutoff threshold *}
  {===>} nmr.prot.thresh.1=0.3;

  {* Class 2 *}

  {* class 2 proton chemical shift restraints file *}
  {===>} nmr.prot.file.2=\"\";
  {* class 2 proton chemical shift potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.prot.pot.2=\"harmonic\";
  {* class 2 proton chemical shift force value *}
  {===>} nmr.prot.force.1.2=7.5;
  {* 2nd class 2 proton chemical shift force value for multi *}
  {===>} nmr.prot.force.2.2=0;
  {* class 2 proton chemical shift violation cutoff threshold *}
  {===>} nmr.prot.thresh.2=0.3;

  {* Class 3 *}

  {* class 3 proton chemical shift restraints file *}
  {===>} nmr.prot.file.3=\"\";
  {* class 3 proton chemical shift potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.prot.pot.3=\"harmonic\";
  {* class 3 proton chemical shift force value *}
  {===>} nmr.prot.force.1.3=7.5;
  {* 2nd class 3 proton chemical shift force value for multi *}
  {===>} nmr.prot.force.2.3=0;
  {* class 3 proton chemical shift violation cutoff threshold *}
  {===>} nmr.prot.thresh.3=0.3;

  {* Class 4 *}

  {* class 4 proton chemical shift restraints file *}
  {===>} nmr.prot.file.4=\"\";
  {* class 4 proton chemical shift potential *}
  {+ choice: \"harmonic\" \"square\" \"multiple\" +}
  {===>} nmr.prot.pot.4=\"multiple\";
  {* class 4 proton chemical shift force value *}
  {===>} nmr.prot.force.1.4=7.5;
  {* 2nd class 4 proton chemical shift force value for multi *}
  {===>} nmr.prot.force.2.4=0;
  {* class 4 proton chemical shift violation cutoff threshold *}
  {===>} nmr.prot.thresh.4=0.3;

  {================ diffusion anisotropy restraint data =================}

  {* fixed or harmonically restrained external axis *}
  {+ choice: \"fixed\" \"harm\" +}
  {===>} nmr.dani.axis=\"harm\";

  {* Class 1 *}

  {* diffusion anisotropy restraints file *}
  {===>} nmr.dani.file.1=\"\";
  {* diffusion anisotropy potential *}
  {+ choice: \"harmonic\" \"square\" +}
  {===>} nmr.dani.pot.1=\"harmonic\";
  {* diffusion anisotropy initial force value *}
  {===>} nmr.dani.force.init.1=0.01;
  {* diffusion anisotropy final force value *}
  {===>} nmr.dani.force.finl.1=1.0;
  {* diffusion anisotropy coefficients *}
  {* coef: <Tc> <anis> <rhombicity> <wh> <wn> *}

  {* Tc = 1/2(Dx+Dy+Dz) in <ns> *}
  {===>} nmr.dani.coef.1.1=13.1;
  {* anis = Dz/0.5*(Dx+Dy) *}
  {===>} nmr.dani.coef.2.1=2.1;
  {* rhombicity = 1.5*(Dy-Dx)/(Dz-0.5*(Dy+Dx)) *}
  {===>} nmr.dani.coef.3.1=0.0;
  {* wH in <MHz> *}
  {===>} nmr.dani.coef.4.1=600.13;
  {* wN in <MHz> *}
  {===>} nmr.dani.coef.5.1=60.82;

  {============= susceptability anisotropy restraint data ===============}

  {* fixed or harmonically restrained external axis *}
  {+ choice: \"fixed\" \"harm\" +}
  {===>} nmr.sani.axis=\"harm\";

  {* Class 1 *}

  {* susceptability anisotropy restraints file *}
  {===>} nmr.sani.file.1=\"\";
  {* susceptability anisotropy potential *}
  {+ choice: \"harmonic\" \"square\" +}
  {===>} nmr.sani.pot.1=\"harmonic\";
  {* susceptability anisotropy initial force value *}
  {===>} nmr.sani.force.init.1=0.01;
  {* susceptability anisotropy final force value *}
  {===>} nmr.sani.force.finl.1=50.0;
  {* susceptability anisotropy coefficients *}
  {* coef: <DFS> <axial > <rhombicity>;
  a0+a1*(3*cos(theta)^2-1)+a2*(3/2)*sin(theta)^2*cos(2*phi) *}

  {* DFS = a0 *}
  {===>} nmr.sani.coef.1.1=-0.0601;
  {* axial = a0-a1-3/2*a2 *}
  {===>} nmr.sani.coef.2.1=-8.02;
  {* rhombicity = a2/a1 *}
  {===>} nmr.sani.coef.3.1=0.4;

  {======================== other restraint data ========================}

  {* dihedral angle restraints file *}
  {* Note: the restraint file MUST NOT contain restraints
  dihedral or end *}
  {===>} nmr.cdih.file=\"%s\";

  {* DNA-RNA base planarity restraints file *}
  {* Note: include weights as $pscale in the restraint file *}
  {===>} nmr.plan.file=\"\";
  {* input planarity scale factor - this will be written into $pscale *}
  {===>} nmr.plan.scale=150;

  {* NCS-restraints file *}
  {* example is in inputs/xtal_data/eg1_ncs_restrain.dat *}
  {===>} nmr.ncs.file=\"\";

  {======================== input/output files ==========================}

  {* base name for input coordinate files *}
  {===>} pdb.in.name=\"\";

  {* base name for output coordinate files *}
  {===>} pdb.out.name=\"%s_\";

  {===========================================================================}
  {         things below this line do not normally need to be changed         }
  {         except for the torsion angle topology setup if you have           }
  {         molecules other than protein or nucleic acid                      }
  {===========================================================================}
  flg.dgsa.flag=false;

  ) {- end block parameter definition -}

  """%(parameter,mtf,template,seed,naccepted,distflag,diheflag,
       disttbl,averaging,dihetbl,pdbbase))
  # THE ACTUAL WORK!
  cns.write("""
  checkversion 1.1

  evaluate ($log_level=quiet)

  structure
     if  (&struct.1 # \"\") then
        @@&struct.1
     end if
     if  (&struct.2 # \"\") then
        @@&struct.2
     end if
     if  (&struct.3 # \"\") then
        @@&struct.3
     end if
     if  (&struct.4 # \"\") then
        @@&struct.4
     end if
     if  (&struct.5 # \"\") then
        @@&struct.5
     end if
  end

  if ( &BLANK%%pdb.in.file.1 = false ) then
     coor @@&pdb.in.file.1
  end if
  if ( &BLANK%%pdb.in.file.2 = false ) then
     coor @@&pdb.in.file.2
  end if
  if ( &BLANK%%pdb.in.file.3 = false ) then
     coor @@&pdb.in.file.3
  end if

  parameter
     if ( &par_nonbonded = \"PROLSQ\" ) then
       evaluate ($par_nonbonded = \"PROLSQ\")
     end if
     if ( &par_nonbonded = \"OPLSX\" ) then
       evaluate ($par_nonbonded = \"OPLSX\")
     end if
     if ( &par_nonbonded = \"PARMALLH6\" ) then
       evaluate ($par_nonbonded = \"PARMALLH6\")
     end if
     if ( &par_nonbonded = \"PARALLHDG\" ) then
       evaluate ($par_nonbonded = \"PARALLHDG\")
     end if
     if (&par.1 # \"\") then
        @@&par.1
     end if
     if (&par.2 # \"\") then
        @@&par.2
     end if
     if (&par.3 # \"\") then
        @@&par.3
     end if
     if (&par.4 # \"\") then
        @@&par.4
     end if
     if (&par.5 # \"\") then
        @@&par.5
     end if
  end

  if ( $log_level = verbose ) then
    set message=normal echo=on end
  else
    set message=off echo=off end
  end if

  parameter
     nbonds
        repel=0.80
        rexp=2 irexp=2 rcon=1.
        nbxmod=3
        wmin=0.01
        cutnb=6.0 ctonnb=2.99 ctofnb=3.
        tolerance=1.5
     end
  end

  {- Read experimental data -}

     @CNS_NMRMODULE:readdata ( nmr=&nmr;
                               flag=&flg;
                               output=$nmr; )

  {- Read and store the number of NMR restraints -}

     @CNS_NMRMODULE:restraintnumber ( num=$num; )

  {- Set mass values -}

  do (fbeta=10) (all)
  do (mass=100) (all)

  evaluate ($nmr.trial.count = 0)    {- Initialize current structure number   -}
  evaluate ($nmr.accept.count = 0)   {- Initialize number accepted            -}
  evaluate ($nmr.counter 	= 0)
  evaluate ($nmr.prev.counter = -1)

  @CNS_NMRMODULE:initave  ( ave=$ave;
                            ave2=$ave2;
                            cv=$cv;
                            ener1=$ener1;
                            ener2=$ener2;
                            flag=&flg;
                            nmr.prot=&nmr.prot; )

  {- Zero the force constant of disulfide bonds. -}
  parameter
     bonds ( name SG ) ( name SG ) 0. TOKEN
  end

  {- define a distance restraints for each disulfide bond, i.e.,
     treat it as if it were an NOE. -}
  for $ss_rm_id_1 in id ( name SG ) loop STRM
    for $ss_rm_id_2 in id ( name SG and
                            bondedto ( id $ss_rm_id_1 )  ) loop STR2
      if ($ss_rm_id_1 > $ss_rm_id_2) then
        pick bond ( id $ss_rm_id_1 ) ( id $ss_rm_id_2 ) equil
        evaluate ($ss_bond=$result)
        noe
           assign ( id $ss_rm_id_1 ) ( id $ss_rm_id_2 ) $ss_bond 0.1 0.1
        end
      end if
    end loop STR2
  end loop STRM

  {- Count the number of residues and determine molecule type -}
  identify (store9) (tag)
  evaluate ($nmr.rsn.num = $SELECT)
  identify (store9) ( tag and ( resn THY or resn CYT or resn GUA or
                                resn ADE or resn URI ))
  evaluate ($nmr.nucl.num = $SELECT)

  {- Improve geometry for torsion angle molecular dynamics -}
  evaluate ($flag_tad=false)
  if ( &md.type.hot = \"torsion\" ) then
     if ($nmr.nucl.num > 0) then
        flag exclude * include bond angl impr dihed vdw end
        minimize powell nstep=2000 drop=10.  nprint=100 end
     else
        flag exclude * include bond angl impr vdw end
        minimize powell nstep=2000 drop=10.  nprint=100 end
     end if
     evaluate ($flag_tad=true)
  end if

  if ( &md.type.cool=\"torsion\") then
     evaluate ($flag_tad=true)
  end if

  if (&nmr.dani.axis = \"harm\") then
     do (harmonic=20.0) (resid 500 and name OO)
     do (harmonic=0.0) (resid 500 and name Z )
     do (harmonic=0.0) (resid 500 and name X )
     do (harmonic=0.0) (resid 500 and name Y )
     do (harmonic=0.0) (not (resid 500))
     restraints harmonic exponent=2 end
  elseif (&nmr.sani.axis = \"harm\") then
     do (harmonic=20.0) (resid 500 and name OO)
     do (harmonic=0.0) (resid 500 and name Z )
     do (harmonic=0.0) (resid 500 and name X )
     do (harmonic=0.0) (resid 500 and name Y )
     do (harmonic=0.0) (not (resid 500))
     restraints harmonic exponent=2 end
  end if

  if (&flg.cv.flag=false) then
    if (&flg.cv.noe=true) then
      echo \"Complete cross-validation for NOE, J-coupling and Dihedrals\"
      echo \"must be disabled if complete cross-validation is not used\"
      abort
    elseif (&flg.cv.coup=true) then
      echo \"Complete cross-validation for NOE, J-coupling and Dihedrals\"
      echo \"must be disabled if complete cross-validation is not used\"
      abort
    elseif (&flg.cv.cdih=true) then
      echo \"Complete cross-validation for NOE, J-coupling and Dihedrals\"
      echo \"must be disabled if complete cross-validation is not used\"
      abort
    end if
  end if

  if (&flg.cv.flag=true) then
     evaluate ($cv.part.num=1)
     evaluate ($cvtemp = int(&pdb.end.count/&nmr.cv.numpart))
     if ($cvtemp < 1) then
        evaluate ($cvtemp = 1)
     end if
     evaluate ($pdb_end_count=&nmr.cv.numpart*$cvtemp)
  else
     evaluate ($pdb_end_count=&pdb.end.count)
  end if

  do (refx=x) ( all )
  do (refy=y) ( all )
  do (refz=z) ( all )

  set seed=&md.seed end

  {- Begin protocol to generate structures -- loop until done -}
  while (&pdb.end.count > $nmr.counter) loop main
     evaluate ($maxcount = %i)
     if ($nmr.trial.count >= $maxcount ) then
         display  ****&&&& ENDCOUNT REACHED, NO CONVERGENCE
         stop
       end if
     {- Set parameter values -}
     parameter
        nbonds
           repel=0.80
           rexp=2 irexp=2 rcon=1.
           nbxmod=3
           wmin=0.01
           cutnb=6.0 ctonnb=2.99 ctofnb=3.
           tolerance=1.5
        end
     end

     evaluate ($nmr.trial.count = $nmr.trial.count + 1)

     do (x=refx) ( all )
     do (y=refy) ( all )
     do (z=refz) ( all )

     if (&nmr.dani.axis = \"fixed\" ) then
        fix
           select=(resname ANI)
        end
     elseif (&nmr.sani.axis = \"fixed\" ) then
        fix
           select=(resname ANI)
        end
     end if

     do ( vx = maxwell(0.5) ) ( all )
     do ( vy = maxwell(0.5) ) ( all )
     do ( vz = maxwell(0.5) ) ( all )

     flags exclude *
           include bond angle dihe impr vdw
                   noe cdih coup oneb carb ncs dani
                   sani harm end

     {- repartition the data for multiple completely cross-validated
        refinements -}

     if ($nmr.prev.counter # $nmr.counter) then
       if (&flg.cv.flag=true) then
         if ($cv.part.num > &nmr.cv.numpart) then

            evaluate ($cv.part.num=1)
           @CNS_NMRMODULE:repartition ( cv=$cv;
                                        flag=&flg;
                                        nmr=&nmr; )

         else
          if (&flg.cv.noe=true) then
             noe cv = $cv.part.num end
          end if
          if (&flg.cv.coup=true) then
             coup cv = $cv.part.num end
          end if
          if (&flg.cv.cdih=true) then
             restraints dihed cv = $cv.part.num end
          end if
           evaluate ($cv.part.num=$cv.part.num+1)
         end if
       end if
     end if

     {- scaling of nmr restraint data during hot dynamics -}

     @CNS_NMRMODULE:scalehot ( md=&md;
                               nmr=&nmr;
                               input.noe.scale=&md.hot.noe;
                               input.cdih.scale=&md.hot.cdih; )

     {- Zero the force constant of disulfide bonds. -}
     parameter
        bonds ( name SG ) ( name SG ) 0. TOKEN
     end

     if ($flag_tad=true) then

        {- initialize torsion dynamics topology for this iteration -}

        dyna torsion
           topology
              maxlength=&md.torsion.maxlength
              maxtree=&md.torsion.maxtree
              maxbond=&md.torsion.maxbond
              {- All dihedrals w/ (force constant > 23) will be locked -}
              {- This keeps planar groups planar -}
              kdihmax = 23.
              @CNS_TOPPAR:torsionmdmods
           end
        end
     end if

  {- High temperature dynamics -}

     if ( &md.type.hot = \"torsion\" ) then

        igroup
           interaction (chemical h* ) (all) weights * 1 vdw 0. elec 0. end
           interaction (not chemical h* ) (not chemical h*) weights * 1 vdw &md.hot.vdw
           end
        end

        dyna torsion
           cmperiodic=500
           vscaling = false
           tcoupling = true
           timestep = &md.hot.ss
           nstep = &md.hot.step
           nprint = 50
           temperature = &md.hot.temp
        end
     else
        evaluate ($md.hot.nstep1=int(&md.hot.step* 2. / 3. ))
        evaluate ($md.hot.nstep2=int(&md.hot.step* 1. / 3. ))
        noe asymptote * 0.1  end
        parameter  nbonds repel=1.   end end
        igroup
           interaction (chemical h* ) (all) weights * 1 vdw 0. elec 0. end
           interaction (not chemical h* ) (not chemical h*) weights * 1 angl 0.4 impr 0.1
                       vdw &md.hot.vdw end
        end

        dynamics cartesian
           cmperiodic=500
           vscaling = true
           tcoupling=false
           timestep=&md.hot.ss
           nstep=$md.hot.nstep1
           nprint=50
           temperature=&md.hot.temp
        end

        noe asymptote * 1.0  end
        igroup
           interaction (chemical h* ) (all) weights * 1 vdw 0. elec 0. end
           interaction (not chemical h* ) (not chemical h*) weights * 1 vdw &md.hot.vdw end
        end

        dynamics cartesian
           cmperiodic=500
           vscaling = true
           tcoupling=false
           timestep=&md.hot.ss
           nstep=$md.hot.nstep2
           nprint=50
           temperature=&md.hot.temp
        end

     end if

  {- The first slow-cooling with torsion angle dynamics -}

     flags include plan end

     {- Increase the disulfide bond force constants to their full strength -}
     parameter
        bonds ( name SG ) ( name SG ) 1000. TOKEN
     end

     evaluate ($final_t = 0)

     evaluate ($ncycle = int((&md.cool.temp-$final_t)/&md.cool.tmpstp))
     evaluate ($nstep = int(&md.cool.step/$ncycle))

     evaluate ($ini_vdw =  &md.hot.vdw)
     evaluate ($fin_vdw =  &md.cool.vdw)
     evaluate ($vdw_step = ($fin_vdw-$ini_vdw)/$ncycle)

     if (&md.type.cool = \"cartesian\") then

        evaluate ($vdw_step = (&md.cool.vdw/&md.hot.vdw)^(1/$ncycle))
        evaluate ($ini_rad  = 0.9)
        evaluate ($fin_rad  = 0.8)
        evaluate ($rad_step = ($ini_rad-$fin_rad)/$ncycle)
        evaluate ($radius=    $ini_rad)

        do (vx=maxwell(&md.cool.temp)) ( all )
        do (vy=maxwell(&md.cool.temp)) ( all )
        do (vz=maxwell(&md.cool.temp)) ( all )

     end if

     {- set up nmr restraint scaling -}

     evaluate ($kdani.inter.flag=false)
     evaluate ($ksani.inter.flag=false)
     evaluate ($kdani.cart.flag=false)
     evaluate ($ksani.cart.flag=false)
     if (&md.cart.flag=true) then
        evaluate ($kdani.inter.flag=true)
        evaluate ($ksani.inter.flag=true)
        @CNS_NMRMODULE:scalecoolsetup ( kdani=$kdani;
                                        ksani=$ksani;
                                        nmr=&nmr;
                                        input.noe.scale=&md.cool.noe;
                                        input.cdih.scale=&md.cool.cdih;
                                        input.ncycle=$ncycle; )
        evaluate ($kdani.cart.flag=true)
        evaluate ($ksani.cart.flag=true)
     else
        @CNS_NMRMODULE:scalecoolsetup ( kdani=$kdani;
                                        ksani=$ksani;
                                        nmr=&nmr;
                                        input.noe.scale=&md.cool.noe;
                                        input.cdih.scale=&md.cool.cdih;
                                        input.ncycle=$ncycle; )
     end if

     evaluate ($bath  = &md.cool.temp)
     evaluate ($k_vdw = $ini_vdw)

     evaluate ($i_cool = 0)
     while ($i_cool <= $ncycle) loop cool
        evaluate ($i_cool = $i_cool + 1)

        igroup
           interaction (chemical h*) (all) weights * 1 vdw 0. elec 0. end
           interaction (not chemical h*) (not chemical h*) weights * 1 vdw $k_vdw end
        end

        if ( &md.type.cool = \"torsion\" ) then
           dynamics  torsion
              cmremove=true
              vscaling = true
              tcoup = false
              timestep = &md.cool.ss
              nstep = $nstep
              nprint = $nstep
              temperature = $bath
           end
        else
           dynamics  cartesian
              cmremove=true
              vscaling = true
              tcoup = false
              timestep = &md.cool.ss
              nstep = $nstep
              nprint = $nstep
              temperature = $bath
           end
        end if

        if (&md.type.cool = \"cartesian\") then
           evaluate ($radius=max($fin_rad,$radius-$rad_step))
           parameter  nbonds repel=$radius   end end
           evaluate ($k_vdw=min($fin_vdw,$k_vdw*$vdw_step))
        else
           evaluate ($k_vdw= $k_vdw + $vdw_step)
        end if
        evaluate ($bath  = $bath  - &md.cool.tmpstp)

        @CNS_NMRMODULE:scalecool ( kdani=$kdani;
                                   ksani=$ksani;
                                   nmr=&nmr; )

     end loop cool

  {- A second slow-cooling with cartesian dyanmics -}

     evaluate ($flag_cart=false)
     if (&md.cart.flag=true) then
        if (&md.type.cool = \"torsion\") then

           evaluate ($flag_cart=true)

           dynamics torsion
              topology
                 reset
              end
           end

           evaluate ($cart_nucl_flag=false)
           if ($nmr.nucl.num > 0) then
              evaluate ($cart_nucl_flag=true)
              parameter
                 nbonds
                    repel=0
                    nbxmod=5
                    wmin=0.01
                    tolerance=0.5
                    cutnb=11.5 ctonnb=9.5 ctofnb=10.5
                    rdie vswitch switch
                 end
              end
              flags include elec end
           end if

           evaluate ($ncycle=int((&md.cart.temp-$final_t)/&md.cart.tmpstp))
           evaluate ($nstep=int(&md.cart.step/$ncycle))

           evaluate ($vdw_step=(&md.cart.vdw.finl/&md.cart.vdw.init)^(1/$ncycle))
           evaluate ($ini_rad=0.9)
           evaluate ($fin_rad=0.8)
           evaluate ($rad_step=($ini_rad-$fin_rad)/$ncycle)
           evaluate ($radius=$ini_rad)

           @CNS_NMRMODULE:scalecoolsetup ( kdani=$kdani;
                                           ksani=$ksani;
                                           nmr=&nmr;
                                           input.noe.scale=&md.cart.noe;
                                           input.cdih.scale=&md.cart.cdih;
                                           input.ncycle=$ncycle; )

           do (vx=maxwell(&md.cart.temp)) ( all )
           do (vy=maxwell(&md.cart.temp)) ( all )
           do (vz=maxwell(&md.cart.temp)) ( all )

           evaluate ($bath=&md.cart.temp)
           evaluate ($k_vdw=&md.cart.vdw.init)

           evaluate ($i_cool = 0)
           while ($i_cool <= $ncycle) loop cart
              evaluate ($i_cool = $i_cool + 1)

              igroup
                 interaction (chemical h*) (all) weights * 1 vdw 0. elec 0. end
                 interaction (not chemical h*) (not chemical h*) weights * 1 vdw $k_vdw
                 end
              end

              dynamics  cartesian
                 vscaling = true
                 tcoup = false
                 timestep = &md.cart.ss
                 nstep = $nstep
                 nprint = $nstep
                 temperature = $bath
              end

              if ($cart_nucl_flag=false) then
                 evaluate ($radius=max($fin_rad,$radius-$rad_step))
                 parameter  nbonds repel=$radius   end end
              end if
              evaluate ($k_vdw=min(&md.cart.vdw.finl,$k_vdw*$vdw_step))
              evaluate ($bath=$bath-&md.cart.tmpstp)

              @CNS_NMRMODULE:scalecool ( kdani=$kdani;
                                         ksani=$ksani;
                                         nmr=&nmr; )

           end loop cart

        end if
     end if

     {- reset torsion angle topology -}
     if ( $flag_tad=true ) then
        if ($flag_cart=false) then
           dynamics torsion
              topology
                 reset
              end
           end
        end if
     end if


  {- Final minimization -}

     {- turn on proton chemical shifts -}

     flags include prot end

     noe
        scale * &md.pow.noe
     end

     restraints dihedral
        scale = &md.pow.cdih
     end

     igroup interaction ( all ) ( all ) weights * 1 end end

     evaluate ($count=0 )
     evaluate ($nmr.min.num=0.)
     while (&md.pow.cycl > $count) loop pmini

        evaluate ($count=$count + 1)
        minimize powell nstep=&md.pow.step drop=10.0 nprint=25 end
        evaluate ($nmr.min.num=$nmr.min.num + $mini_cycles)

     end loop pmini

     {- translate the geometric center of the structure to the origin -}
     if ($num.dani > 0. ) then
     elseif ($num.sani > 0. ) then
     else
        show ave ( x ) ( all )
        evaluate ($geom_x=-$result)
        show ave ( y ) ( all )
        evaluate ($geom_y=-$result)
        show ave ( z ) ( all )
        evaluate ($geom_z=-$result)
        coor translate vector=( $geom_x $geom_y $geom_z ) selection=( all ) end
     end if


     @CNS_NMRMODULE:printaccept ( ave=$ave;
                                  ave2=$ave2;
                                  cv=$cv;
                                  ener1=$ener1;
                                  ener2=$ener2;
                                  flag=&flg;
                                  md=&md;
                                  nmr=&nmr;
                                  num=$num;
                                  output=$nmr;
                                  pdb=&pdb;  )

  end loop main

     @CNS_NMRMODULE:calcave ( ave=$ave;
                              ave2=$ave2;
                              cv=$cv;
                              ener1=$ener1;
                              ener2=$ener2;
                              flag=&flg;
                              md=&md;
                              nmr=&nmr;
                              num=$num;
                              output=$nmr;
                              pdb=&pdb;  )


  stop
  """%(naccepted*ntrial))
  # SUBMIT XPLOR JOB
  cns.submit()
  # CLEANUP
  if cns.logfiles!='keep':
    os.remove(disttbl)
    os.remove(dihetbl)


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


# ADD SEGI TO PDB FILE
# ====================
def xplor_pdbmatchsegi(inpdb,refpdb):
  # READ REFPDB
  content = open(refpdb,'r')
  found = 0
  # AND FIND THE SEGID
  while not found:
    line = content.readline()
    if len(line)>4:
      if line[:4]=='ATOM':
        segid = line[72]
        found = 1
  # READ INPDB
  content = open(inpdb,'r').readlines()
  # OPEN OUTPDB
  tmp = dsc_tmpfile()
  outfile = open(tmp,'w')
  for line in content:
    # ONLY LINES THAT ARE LONG ENOUGH
    if len(line)>4:
      # SET SEGID
      if line[:4]=='ATOM':
        # HANDLE NEWLINES AT
        if line[:72][-1]=='\n': first = line[:72][:-1].ljust(72)
        else: first = line[:72]
        newline = "%s%s%s\n"%(first,segid,line[73:-1])
        line = newline
      # REPLACE HEADER BY REMARK
      line = line.replace('HEADER','REMARK')
      line = line.replace('CRYST1','REMARK')
      outfile.write(line)
    # WRITE THE REST (EXCEPT TER LINES)
    else:
      if line[:3]!='TER':
        outfile.write(line)
  outfile.close()
  # OVERWRITE INPUT FILE
  shutil.copy(tmp,inpdb)
  # DELETE TEMPORARY FILE
  os.remove(tmp)


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


# SHUFFLE ATOMS
# =============
def xplor_setatoms(inpdb,psf,outpdb=None,xplor=None):
  if not outpdb:
    tmppdb = "%s.tmp"%inpdb
  else: tmppdb = outpdb
  # TAKE DEFAULT FOR XPLOR
  if not xplor: xplor = nmvconf["XPLOR"]
  # INITIALIZE THE XPLOR SCRIPT CLASS
  xplr = xplor_script(xplor)
  # READ THE STRUCTURE FILE
  xplr.write("structure\n  @%s\nend"%psf)
  # READ PDB FILE
  xplr.write("coordinates @%s"%inpdb)
  # WRITE OUT THE TEMPLATE FILE
  xplr.write("write coordinates")
  xplr.write("  output=%s"%tmppdb)
  xplr.write("end")
  # SUBMIT XPLOR JOB
  xplr.submit()
  if not outpdb and os.path.exists(tmppdb):
    os.rename(tmppdb,inpdb)

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
#    X P L O R   F U N C T I O N   G R O U P   P R I V A T E
#  ======================================================================

# REFINE STRUCTURE IN WATER
# =========================
# REFINE STRUCTURE BASED ON THE PROVIDED DATASET
def xplor_refstruct(inpdb,outpdb,psf,restraintlist,
                    averaging='sum',
                    thr_noe=0.5,
                    thr_dih=10.,
                    xplor=None,
                    parsolv=None,
                    parprot=None,
                    topsolv=None,
                    topprot=None,
                    solvbox=None,
                    seed=None,
                    maxtry=10,
                    mdheat=200,
                    mdhot =2000,
                    mdcool=200):
  # TAKE DEFAULTS PARAMETERS AND XPLOR
  if not parsolv: parsolv = nmvconf["PAR_SOLV"]
  if not topsolv: topsolv = nmvconf["TOP_SOLV"]
  if not parprot: parprot = nmvconf["PAR_PROT"]
  if not topprot: topprot = nmvconf["TOP_PROT"]
  if not solvbox: solvbox = nmvconf["SOLVBOX"]
  if not xplor: xplor = nmvconf["XPLOR"]
  if not seed: seed = 65748309
  retry,attempt = 1,1
  while retry and attempt <= maxtry:
    # INITIALIZE THE XPLOR SCRIPT CLASS
    xplr = xplor_script(xplor,scriptpath=nmvconf["TMP"])
    # READ THE STRUCTURE FILE
    xplr.write("structure\n  @@%s\nend"%psf)
    # READ PARAMETER FILE
    xplr.write("evaluate ($par_nonbonded=OPLSX)")
    xplr.write("parameter\n  @@%s\nend"%parsolv)
    xplr.write("parameter\n  @@%s\nend"%parprot)
    # READ TOPOLOGY FILE
    xplr.write("topology\n  @@%s\nend"%topsolv)
    xplr.write("topology\n  @@%s\nend"%topprot)
    # READ PDB FILE
    xplr.write("coordinates @@%s"%inpdb)
    # BUILD THE WATER BOX
    xplr.write("""
    {*==========================================================================*}
    {*================== SET VALUES FOR NONBONDED PARAMETERS ===================*}
    {*==========================================================================*}

    parameter
      nbonds
      nbxmod=5 atom cdiel shift
      cutnb=9.5 ctofnb=8.5 ctonnb=6.5 eps=1.0 e14fac=0.4 inhibit 0.25
      wmin=0.5
      tolerance  0.5
      end
    end

    {*==========================================================================*}
    {*============== COPY THE COORDINATES TO THE REFERENCE SET =================*}
    {*==========================================================================*}

    vector do (refx = x) (all)
    vector do (refy = y) (all)
    vector do (refz = z) (all)

    {*==========================================================================*}
    {*========================= GENERATE THE WATER LAYER =======================*}
    {*==========================================================================*}

    vector do (segid = \"PROT\") (segid \"    \")

    ! generate_water.inp
    ! soaks a protein structure in a layer of water
    ! can be applied iteratively (using dyncount > 1)
    !
    !     ************************************
    !     * Authors and copyright:           *
    !     * Michael Nilges, Jens Linge, EMBL *
    !     * No warranty implied or expressed *
    !     * All rights reserved              *
    !     ************************************
    !     MODIFIED FOR USE WITH XPLOR-NIH, CHRIS SPRONK

    eval ($boxlength = 18.856)   ! length of Brooks' water box
    eval ($thickness = 8)        ! maxi. initial water-protein distance (heavy atoms)
    eval ($pw_dist = 4.0)        ! mini. initial water-protein distance (heavy atoms)
    eval ($water_diam = 2.4)     ! diameter of water molecule
    eval ($dyncount = 1)         ! iteration number (usually 1)

    eval ($water = \"WAT\" + encode($dyncount))

    !--------------------------------------------------
    ! read in the same box of water several times, and move it around
    ! so as to cover all the space around the site of interest.
    ! take into account box offset

    vector show max (x) ((not resn tip3) and not resn ani)
    evaluate ($xmax = $result)
    vector show min (x) ((not resn tip3) and not resn ani)
    evaluate ($xmin = $result)

    vector show max (y) ((not resn tip3) and not resn ani)
    evaluate ($ymax = $result)
    vector show min (y) ((not resn tip3) and not resn ani)
    evaluate ($ymin = $result)

    vector show max (z) ((not resn tip3) and not resn ani)
    evaluate ($zmax = $result)
    vector show min (z) ((not resn tip3) and not resn ani)
    evaluate ($zmin = $result)

    !--------------------------------------------------
    ! read in the same box of water several times, and move it around
    ! so as to cover all the space around the site of interest.
    ! take into account box offset

    ! determine how many boxes are necessary in each dimension
    eval ($xbox = int( ($xmax - $xmin + 2 * ($thickness + $water_diam)) / $boxlength  + 0.5))
    eval ($ybox = int( ($ymax - $ymin + 2 * ($thickness + $water_diam)) / $boxlength  + 0.5))
    eval ($zbox = int( ($zmax - $zmin + 2 * ($thickness + $water_diam)) / $boxlength  + 0.5))

    eval ($xmtran =  $xmax + $thickness - $boxlength/2 + $water_diam)
    eval ($ymtran =  $ymax + $thickness - $boxlength/2 + $water_diam)
    eval ($zmtran =  $zmax + $thickness - $boxlength/2 + $water_diam)

    set echo off message off end
    eval ($xcount=0)
    eval ($xtrans = $xmin - $thickness - $water_diam - $boxlength/2 )
    while ($xtrans < $xmtran) loop wat1
      eval ($xcount=$xcount+1)
      eval ($xtrans = $xtrans + $boxlength)
      eval ($ycount=0)
      eval ($ytrans = $ymin - $thickness - $water_diam - $boxlength/2 )
      while ($ytrans < $ymtran) loop wat2
        eval ($ycount=$ycount+1)
        eval ($ytrans = $ytrans + $boxlength)
        eval ($zcount=0)
        eval ($ztrans = $zmin - $thickness - $water_diam - $boxlength/2 )
        while ($ztrans < $zmtran) loop wat3
          eval ($zcount=$zcount+1)
          eval ($ztrans = $ztrans + $boxlength)

          segment
            name=\"    \"
            chain
              coordinates @@%s
            end
          end
          coor @@%s
          vector do (segid=W000) (segid \"    \")
          coor sele=(segid W000) translate vector = ($xtrans $ytrans $ztrans) end
          ! all new water oxygens
          vector identity (store1) (segid W000 and name oh2)
          ! all new water oxygens close to a protein heavy atom
          vector identity (store2) (store1 and (not (resn tip3 or resn ani or hydro)) around $pw_dist)
          ! all new water oxygens close to old water oxygens
          vector identity (store3) (store1 and (segid wat# and not hydro) around $water_diam)
          ! all new water oxygens further than thickness away from a protein heavy atom
          vector identity (store4) (store1 and not (not (resn tip3 or resn ani or hydro)) around $thickness)
          delete sele= (byres (store2 or store3 or store4)) end
          ! give waters unique segid name
          eval ($segid= \"W\"
                  + encode($xcount) + encode($ycount) + encode($zcount))
          vector do (segid = $segid) (segid W000)

        end loop wat3
      end loop wat2
    end loop wat1

    ! now, give waters a unique resid so that we get the segid to play around with
    vector identity (store1) (all)
    vector show min (store1) (segid w*)
    vector do (store1 = store1 - $result + 1) (segid w*)
    vector do (resid = encode(int(store1/3 -0.1) +1)) (segid w* and not segid wat#)
    vector do (segid = $water) (segid w* and not segid wat#)

    ! shave off any waters that left
    delete sele= (byres (name oh2 and not (not (resn tip3 or resn ani or hydro)) around $thickness)) end

    set echo on message on end

    vector do (segid = \"    \") (segid \"PROT\")
    """%(solvbox,solvbox))
    # READ EXPERIMENTAL DATA
    xplr.write("""
    {*==========================================================================*}
    {*========================= READ THE EXPERIMENTAL DATA =====================*}
    {*==========================================================================*}

    noe reset
      nrestraints = 30000
      ceiling     = 100
      class      1
      averaging  1 %s
      potential  1 soft
      scale      1 50
      sqconstant 1 1.0
      sqexponent 1 2
      soexponent 1 1
      rswitch    1 1.0
      sqoffset   1 0.0
      asymptote  1 2.0
      """%(averaging))
    # GET ALL DISTANCE RESTRAINTS
    distlist = [r for r in restraintlist if r.type=="DIST"]
    for el in distlist:
      xplr.write(el.format("XPLOR"))
    xplr.write("end")
    # DO THE DIHEDRAL ANGLE RESTRAINTS
    xplr.write("""
    restraints dihedral
      reset
      nassign =10000
      scale   = 200
      """)
    dihelist = [r for r in restraintlist if r.type=="DIHE"]
    for el in dihelist:
      xplr.write(el.format("XPLOR"))
    xplr.write("end")
    # CONTINUE
    xplr.write("""
    {*==========================================================================*}
    {*============================ SET FLAGS ===================================*}
    {*==========================================================================*}

    flags exclude *
    include bond angle dihe impr vdw elec
            noe cdih coup oneb carb ncs dani
            vean sani prot harm
    end


    {*==========================================================================*}
    {*================== SET PARAMETERS FOR MD-SIMULATION ======================*}
    {*==========================================================================*}

    {* set number of md steps for the heating stage *}
    !evaluate ( $mdsteps.heat = 200 )
    evaluate ( $mdsteps.heat = %i )

    {* set number of md steps for the hot md stage *}
    !evaluate ( $mdsteps.hot = 2000 )
    evaluate ( $mdsteps.hot = %i )

    {* set number of md steps for the cooling stage *}
    !evaluate ( $mdsteps.cool = 200 )
    evaluate ( $mdsteps.cool = %i )

    {* seed for velocity generation *}
    evaluate ( $seed = %i )


    {*==========================================================================*}
    {*========================= START THE REFINEMENT ===========================*}
    {*==========================================================================*}

    set seed $seed end

    ! We loop untill we have an accepted structure, maximum trials=1
    !evaluate ($end_count = 1)
    !evaluate ($count = 0)

    !while ($count < $end_count ) loop main

    evaluate ($accept = 0)

    ! since we do not use SHAKe, increase the water bond angle energy constant
    parameter
    angle (resn tip3) (resn tip3) (resn tip3) 500 TOKEN
    end

    ! reduce improper and angle force constant for some atoms
    evaluate ($kbonds = 1000)
    evaluate ($kangle = 50)
    evaluate ($kimpro = 5)
    evaluate ($kchira = 5)
    evaluate ($komega = 5)
    parameter
    angle    (not resn tip3)(not resn tip3)(not resn tip3) $kangle  TOKEN
    improper (all)(all)(all)(all) $kimpro  TOKEN TOKEN
    end

    ! fix the protein for initial minimization
    constraints fix (not resn tip3) end
    minimize powell nstep=40 drop=100 end

    ! release protein and restrain harmonically
    constraints fix (not all) end
    vector do (refx=x) (all)
    vector do (refy=y) (all)
    vector do (refz=z) (all)
    restraints harmonic
    exponent = 2
    end
    vector do (harmonic = 0)  (all)
    vector do (harmonic = 10) (not name h*)
    vector do (harmonic = 20.0)(resname ANI and name OO)
    vector do (harmonic = 0.0) (resname ANI and name Z )
    vector do (harmonic = 0.0) (resname ANI and name X )
    vector do (harmonic = 0.0) (resname ANI and name Y )

    constraints
    interaction (not resname ANI) (not resname ANI)
    interaction ( resname ANI) ( resname ANI)
    end

    evaluate ($mini_steps = 10)
    evaluate ($mini_step = 1)
    while ($mini_step <= $mini_steps) loop mini
      minimize powell nstep=100 drop=10 nprint=50 end
      vector do (refx=x) (not resname ANI)
      vector do (refy=y) (not resname ANI)
      vector do (refz=z) (not resname ANI)
      evaluate ($mini_step=$mini_step+1)
    end loop mini

    vector do (mass =50) (all)
    vector do (mass=1000) (resname ani)
    vector do (fbeta = 0) (all)
    vector do (fbeta = 20. {1/ps} ) (not resn ani)
    evaluate ($kharm = 50)
    ! heat to 500 K
    for $bath in (100 200 300 400 500) loop heat
    vector do (harm = $kharm) (not name h* and not resname ANI)
    vector do (vx=maxwell($bath)) (all)
    vector do (vy=maxwell($bath)) (all)
    vector do (vz=maxwell($bath)) (all)
    dynamics verlet
            nstep=$mdsteps.heat timest=0.003{ps}
            tbath=$bath  tcoupling = true
            iasvel=current
            nprint=50
    end
    evaluate ($kharm = max(0, $kharm - 4))
    vector do (refx=x) (not resname ANI)
    vector do (refy=y) (not resname ANI)
    vector do (refz=z) (not resname ANI)
    end loop heat

    ! refinement at high T:
    constraints
    interaction (not resname ANI) (not resname ANI) weights * 1 dihed 2 end
    interaction ( resname ANI) ( resname ANI) weights * 1 end
    end

    vector do (harm = 0)  (not resname ANI)
    vector do (vx=maxwell($bath)) (all)
    vector do (vy=maxwell($bath)) (all)
    vector do (vz=maxwell($bath)) (all)
    dynamics verlet
    nstep=$mdsteps.hot timest=0.004{ps}
    tbath=$bath  tcoupling = true
    iasvel=current
    nprint=50
    end

    constraints
    interaction (not resname ANI) (not resname ANI) weights * 1 dihed 3 end
    interaction ( resname ANI) ( resname ANI) weights * 1  end
    end

    ! cool
    evaluate ($bath = 500)
    while ($bath >= 25) loop cool

    evaluate ($kbonds    = max(225,$kbonds / 1.1))
    evaluate ($kangle    = min(200,$kangle * 1.1))
    evaluate ($kimpro    = min(200,$kimpro * 1.4))
    evaluate ($kchira    = min(800,$kchira * 1.4))
    evaluate ($komega    = min(80,$komega * 1.4))

    parameter
            bond     (not resn tip3 and not name H*)(not resn tip3 and not name H*) $kbonds  TOKEN
            angle    (not resn tip3 and not name H*)(not resn tip3 and not name H*)(not resn tip3 and not name H*) $kangle  TOKEN
            improper (all)(all)(all)(all) $kimpro  TOKEN TOKEN
            !VAL: stereo CB
            improper (name HB and resn VAL)(name CA and resn VAL)(name CG1 and resn VAL)(name CG2 and resn VAL) $kchira TOKEN TOKEN
            !THR: stereo CB
            improper (name HB and resn THR)(name CA and resn THR)(name OG1 and resn THR)(name CG2 and resn THR) $kchira TOKEN TOKEN
            !LEU: stereo CG
            improper (name HG and resn LEU)(name CB and resn LEU)(name CD1 and resn LEU)(name CD2 and resn LEU) $kchira TOKEN TOKEN
            !ILE: chirality CB
            improper (name HB and resn ILE)(name CA and resn ILE)(name CG2 and resn ILE)(name CG1 and resn ILE) $kchira TOKEN TOKEN
            !chirality CA
            improper (name HA)(name N)(name C)(name CB) $kchira TOKEN TOKEN

            improper (name O)  (name C) (name N) (name CA) $komega TOKEN TOKEN
            improper (name HN) (name N) (name C) (name CA) $komega TOKEN TOKEN
            improper (name CA) (name C) (name N) (name CA) $komega TOKEN TOKEN
            improper (name CD) (name N) (name C) (name CA) $komega TOKEN TOKEN
    end

    vector do (vx=maxwell($bath)) (all)
    vector do (vy=maxwell($bath)) (all)
    vector do (vz=maxwell($bath)) (all)
    dynamics verlet
            nstep=$mdsteps.cool timest=0.004{ps}
            tbath=$bath  tcoupling = true
            iasvel=current
            nprint=50
    end

    evaluate ($bath = $bath - 25)
    end loop cool


    !final minimization:
    mini powell nstep 200 end
    """%(mdheat,mdhot,mdcool,seed))
    # FINISH UP
    xplr.write("""
    {*==========================================================================*}
    {*======================= CHECK RESTRAINT VIOLATIONS =======================*}
    {*==========================================================================*}

    constraints interaction
    (not resname TIP* and not resname ANI)
    (not resname TIP* and not resname ANI)
    end

    energy end
    evaluate ($violations = 0)
    ! NOES overall analysis
    print threshold=0.5 noe
    evaluate ( $viol.noe.viol05 = $violations )
    print threshold=0.3 noe
    evaluate ( $viol.noe.viol03 = $violations )
    print threshold=0.1 noe
    evaluate ( $viol.noe.viol01 = $violations )
    evaluate ( $rms.noe = $result )

    ! NOES
    evaluate ( $viol.noe.total = 0 )

    evaluate ( $accept.noe.1 = %5.2f )
    noe reset
      nrestraints = 20000
      ceiling     = 100
      class      1
      averaging  1 sum
      potential  1 soft
      scale      1 50
      sqconstant 1 1.0
      sqexponent 1 2
      soexponent 1 1
      rswitch    1 1.0
      sqoffset   1 0.0
      asymptote  1 2.0
    """%(thr_noe))
    for el in distlist:
      xplr.write(el.format("XPLOR"))
    xplr.write("""
      print threshold=$accept.noe.1
    end
    evaluate ( $viol.noe.1 = $violations )
    evaluate ( $viol.noe.total = $violations + $viol.noe.total )

    ! DIHEDRALS
    evaluate ( $viol.cdih.total = 0 )

    evaluate ( $accept.cdih.1 = %5.2f )
    restraints dihedral reset
    """%(thr_dih))
    for el in dihelist:
      xplr.write(el.format("XPLOR"))
    xplr.write("""
      scale=200
    end
    print threshold=$accept.cdih.1 cdih
    evaluate ( $rms.cdih = $result )
    evaluate ( $viol.cdih.1 = $violations )
    evaluate ( $viol.cdih.total = $viol.cdih.total + $violations )

    {*==========================================================================*}
    {*======================= CHECK ACCEPTANCE CRITERIA ========================*}
    {*==========================================================================*}

    if ( $viol.noe.total  > 0 ) then  evaluate ( $accept=$accept + 1 ) end if
    if ( $viol.cdih.total  > 0 ) then  evaluate ( $accept=$accept + 1 ) end if

    if ($accept = 0 ) then
    evaluate ( $label = \"ACCEPTED - trial %i of %i\" )
    exit main
    else
    evaluate ( $label = \"NOT ACCEPTED - trial %i of %i\" )
    !evaluate ( $count = $count + 1 )
    end if

    !end loop main


    remarks Structure $label
    remarks Energies and RMS deviations:
    remarks ener.total=$ener
    remarks ener.noe=$noe ener.cdih=$cdih
    remarks rms.noe=$rms.noe rms.cdih=$rms.cdih
    remarks noe violations ( classes: ['1'] )
    remarks viol.noe.1=$viol.noe.1 ( accept.noe.1=$accept.noe.1 )
    remarks cdih violations ( classes: ['1'] )
    remarks viol.cdih.1=$viol.cdih.1 ( accept.cdih.1=$accept.cdih.1 )
    remarks All NOE violations >0.5, 0.3 and 0.1A respectively ( all classes ):
    remarks viol.noe.viol05=$viol.noe.viol05 viol.noe.viol03=$viol.noe.viol03 viol.noe.viol01=$viol.noe.viol01
    write coordinates
      sele=(not resn TIP3 and not resn ANI)
      output=%s
    end
    stop

    """%(attempt,maxtry,attempt,maxtry,outpdb))
    xplr.submit()
    accepted = 0
    if not xplr.atomchkerr:
      # CHECK ACCEPTANCE
      accepted = xplor_accept(outpdb,psf,restraintlist,thr_noe=thr_noe,
                              thr_dih=thr_dih)
    # CHECK FOR ERRORS
    if accepted:
      retry = 0
    else:
      if os.path.exists(outpdb):
        os.rename(outpdb,outpdb+".%i-%i"%(attempt,maxtry))
      seed = randint(100000,999999)
      attempt += 1

# A SHORT EM IN XPLOR
# ===================
# A SHORT EM OF THE STRUCTURE
# BASED ON THE PROVIDED DATASET
def xplor_emstruct(inpdb,outpdb,psf,restraintlist,
                   averaging='sum',
                   thr_noe=0.5,
                   thr_dih=5.0,
                   xplor=None,
                   parprot=None,
                   topprot=None,
                   maxtry=10):
  # TAKE DEFAULTS PARAMETERS AND XPLOR
  if not parprot: parprot = nmvconf["PAR_PROT"]
  if not topprot: topprot = nmvconf["TOP_PROT"]
  if not xplor: xplor = nmvconf["XPLOR"]
  retry,attempt = 1,1
  while retry and attempt <= maxtry:
    # INITIALIZE THE XPLOR SCRIPT CLASS
    xplr = xplor_script(xplor,scriptpath=nmvconf["TMP"])
    # READ THE STRUCTURE FILE
    xplr.write("structure\n  @@%s\nend"%psf)
    # READ PARAMETER FILE
    xplr.write("evaluate ($par_nonbonded=OPLSX)")
    xplr.write("parameter\n  @@%s\nend"%parprot)
    # READ TOPOLOGY FILE
    xplr.write("topology\n  @@%s\nend"%topprot)
    # READ PDB FILE
    xplr.write("coordinates @@%s"%inpdb)
    # BUILD THE WATER BOX
    xplr.write("""
    set message on echo on end

    ! Set occupancies to 1.00
    vector do (Q = 1.00) (all)

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

    flags exclude *
    include bond angle impr vdw
            noe cdih coup oneb carb ncs dani
            vean sani dipo prot
    end
    """)
    # READ EXPERIMENTAL DATA
    xplr.write("""
    {*==========================================================================*}
    {*========================= READ THE EXPERIMENTAL DATA =====================*}
    {*==========================================================================*}

    noe reset
      nrestraints = 30000
      ceiling     = 100
      class      1
      averaging  1 %s
      potential  1 soft
      scale      1 250
      sqconstant 1 1.0
      sqexponent 1 2
      sqoffset   1 0.0
      rswitch    1 1.0
      asymptote  1 2.0
      """%(averaging))
    # GET ALL DISTANCE RESTRAINTS
    distlist = [r for r in restraintlist if r.type=="DIST"]
    for el in distlist:
      xplr.write(el.format("XPLOR"))
    xplr.write("end")
    # DO THE DIHEDRAL ANGLE RESTRAINTS
    xplr.write("""
    restraints dihedral
      reset
      nassign = 10000
      scale   = 200
      """)
    dihelist = [r for r in restraintlist if r.type=="DIHE"]
    for el in dihelist:
      xplr.write(el.format("XPLOR"))
    xplr.write("end")
    # CONTINUE
    xplr.write("""
    minimize powell nstep=500 nprint=10 end
    """)
    # FINISH UP
    xplr.write("""
    {*==========================================================================*}
    {*======================= CHECK RESTRAINT VIOLATIONS =======================*}
    {*==========================================================================*}

    constraints interaction
    (not resname TIP* and not resname ANI)
    (not resname TIP* and not resname ANI)
    end

    energy end

    evaluate ($end_count = 1)
    evaluate ($count = 0)
    evaluate ($accept = 0)

    evaluate ($violations = 0)
    ! NOES overall analysis
    print threshold=0.5 noe
    evaluate ( $viol.noe.viol05 = $violations )
    print threshold=0.3 noe
    evaluate ( $viol.noe.viol03 = $violations )
    print threshold=0.1 noe
    evaluate ( $viol.noe.viol01 = $violations )
    evaluate ( $rms.noe = $result )

    ! NOES
    evaluate ( $viol.noe.total = 0 )

    evaluate ( $accept.noe.1 = %5.2f )
    noe reset
      nrestraints = 30000
      ceiling     = 2000
      class      1
      averaging  1 sum
      potential  1 square
      scale      1 2000
      sqconstant 1 1.0
      sqexponent 1 2
      sqoffset   1 0.0
    """%(thr_noe))
    for el in distlist:
      xplr.write(el.format("XPLOR"))
    xplr.write("""
      print threshold=$accept.noe.1
    end
    evaluate ( $viol.noe.1 = $violations )
    evaluate ( $viol.noe.total = $violations + $viol.noe.total )

    ! DIHEDRALS
    evaluate ( $viol.cdih.total = 0 )

    evaluate ( $accept.cdih.1 = %5.2f )
    restraints dihedral reset
    """%(thr_dih))
    for el in dihelist:
      xplr.write(el.format("XPLOR"))
    xplr.write("""
      scale=200
    end
    print threshold=$accept.cdih.1 cdih
    evaluate ( $rms.cdih = $result )
    evaluate ( $viol.cdih.1 = $violations )
    evaluate ( $viol.cdih.total = $viol.cdih.total + $violations )

    {*==========================================================================*}
    {*======================= CHECK ACCEPTANCE CRITERIA ========================*}
    {*==========================================================================*}

    if ( $viol.noe.total  > 0 ) then  evaluate ( $accept=$accept + 1 ) end if
    if ( $viol.cdih.total  > 0 ) then  evaluate ( $accept=$accept + 1 ) end if

    if ($accept = 0 ) then
    evaluate ( $label = \"ACCEPTED\" )
    exit main
    else
    evaluate ( $label = \"NOT ACCEPTED\" )
    evaluate ( $count = $count + 1 )
    end if

    remarks Structure $label
    remarks Energies and RMS deviations:
    remarks ener.total=$ener
    !remarks ener.noe=$noe ener.cdih=$cdih
    remarks rms.noe=$rms.noe rms.cdih=$rms.cdih
    remarks noe violations ( classes: ['1'] )
    remarks viol.noe.1=$viol.noe.1 ( accept.noe.1=$accept.noe.1 )
  !  remarks viol.noe.2=$viol.noe.2 ( accept.noe.2=$accept.noe.2 )
    remarks cdih violations ( classes: ['1'] )
    remarks viol.cdih.1=$viol.cdih.1 ( accept.cdih.1=$accept.cdih.1 )
    remarks All NOE violations >0.5, 0.3 and 0.1A respectively ( all classes ):
    remarks viol.noe.viol05=$viol.noe.viol05 viol.noe.viol03=$viol.noe.viol03 viol.noe.viol01=$viol.noe.viol01
    write coordinates
      sele=(not resn TIP3 and not resn ANI)
      output=%s
    end
    stop

    """%outpdb)
    xplr.submit()
    # CHECK FOR ERRORS
    if not xplr.atomchkerr:
      retry = 0
    else:
      seed = randint(100000,999999)
      attempt += 1


# ANNEAL STRUCTURE
# ================
# ANNEAL STRUCTURE IN XPLORNIH WITH CDS'S PROTOCOL
def xplornih_anneal2(pdbbase,
                     template,
                     psf,
                     restraintlist,
                     averaging='sum',
                     naccepted=20,
                     thr_noe=0.5,
                     thr_dih=5.0,
                     parprot=None,
                     xplor=None,
                     seed=None,
                     ntrial=5):
  if numproc > 1: import pypar
  # LIST OF ANNEAL AND ACCEPTED STRUCTURES
  annealed = []
  # TAKE DEFAULTS FOR PARAMETER AND XPLOR
  if not parprot: parprot = nmvconf["PAR_PROT"]
  if not xplor: xplor = nmvconf["XPLOR"]
  # SET INITIAL SEED
  if not seed: seed = randint(10000,99999)
  # THE PROGRESS INDICATOR
  #prog = progress_indicator(naccepted)
  #prog.increment(n_acc)
  n_acc = 0
  # DIVIDE FOR MY RUNS
  str_ids = range(1,naccepted+1)
  mylower,myupper = mpi_setrange(str_ids,myid,numproc)
  # TRY TO CALCULATE naccepted STRUCTURES
  for struct in range(mylower,myupper):
    n_try,accepted = 0,0
    # CONTINUE UNTILL THE STRUCTURE IS ACCEPTED
    # OR MAXIMUM NUMBER OF TRIES IS REACHED
    while ((n_try<ntrial) and not accepted):
      n_try += 1
      print "%03i - %03i\r"%(str_ids[struct],n_try),
      sys.stdout.flush()
      # TMP FILE
      tmppdb = os.path.join(os.path.dirname(pdbbase),
                            'trial_%i_%i_%s_%s.pdb'%(str_ids[struct],n_try,
                                                     os.getpid(),myid))
      # FINAL PDB
      finalpdb = "%s_%03i.pdb"%(pdbbase,str_ids[struct])
      if not os.path.exists(finalpdb):
        # INITIALIZE THE XPLOR SCRIPT CLASS
        xplr = xplor_script(xplor,scriptpath=nmvconf["TMP"])
        # READ THE STRUCTURE FILE
        xplr.write("structure\n  @@%s\nend"%psf)
        # READ PARAMETER FILE
        xplr.write("evaluate ($par_nonbonded=OPLSX)")
        xplr.write("parameter\n  @@%s\nend"%parprot)
        # READ PDB FILE
        xplr.write("coordinates @@%s"%template)
        # DO THE ANNEALING
        xplr.write("""
        evaluate ($seed=%i)

        set seed $seed  end

        noe
           reset
           nres = 5000
           set message off echo off end
           class all
           """%(seed))
        # GET ALL DISTANCE RESTRAINTS
        distlist = [r for r in restraintlist if r.type=="DIST"]
        for el in distlist:
          xplr.write(el.format("XPLOR"))
        xplr.write("""
        end

         set echo on message on end

        restraints dihed
         reset
          nass = 10000
          set message off echo off end
        """)
        dihelist = [r for r in restraintlist if r.type=="DIHE"]
        for el in dihelist:
          xplr.write(el.format("XPLOR"))
        xplr.write("""
          set message on echo on end
        end

        {* Minimize with only the covalent constraints. *}
        flags exclude * include bond angle impr end
        mini powell nstep 1000 nprint 100 end

        coor copy end

        !
        ! annealing settings
        !

        eval ($init_t  = 3500.01)
        eval ($final_t = 100)

        eval ($cool_steps = 15000)
        eval ($tempstep = 25)

        eval ($ncycle_vdw = 100)

        eval ($ncycle = ($init_t-$final_t)/$tempstep)
        eval ($nstep = int($cool_steps/$ncycle))

        eval ($ini_rad  = 0.4)
        eval ($fin_rad  = 0.80)
        eval ($radfact = ($fin_rad/$ini_rad)^(1/$ncycle))

        eval ($ini_con = 0.004)
        eval ($fin_con = 4.0)
        eval ($k_vdwfact = ($fin_con/$ini_con)^(1/$ncycle))

        eval ($ini_ang = 0.4)
        eval ($fin_ang = 1.0)
        eval ($ang_fac = ($fin_ang/$ini_ang)^(1/$ncycle))

        eval ($ini_imp = 0.4)     ! CDS was 0.1
        eval ($fin_imp = 1.0)
        eval ($imp_fac = ($fin_imp/$ini_imp)^(1/$ncycle))

        eval ($hitemp_noe = 20.0) ! CDS was 150
        eval ($ini_noe = 20.0)    ! CDS was 2
        eval ($fin_noe = 30.0)
        eval ($noe_fac = ($fin_noe/$ini_noe)^(1/$ncycle))

        eval ($ini_timestep = 0.010)    !reduced from 0.015
        eval ($fin_timestep = 0.003)
        eval ($timestep_fac = ($fin_timestep/$ini_timestep)^(1/$ncycle))

        vector do (mass = 100.0) (all)
        vector do (fbeta = 10.0) (all)

        set echo on message on end

        !
        ! set up the torsion angle dynamics topology stuff
        ! to eliminate degrees of freedom in the aromatics

        dynamics internal
          set echo off message off end
          evaluate ( $res = 1 )
          while ($res le 500) loop group
            {* group aromatic ring atoms. *}
            group (resid $res and resname PHE and
                  (name CG or name CD1 or name CD2 or name CE1 or name CE2 or name CZ))
            group (resid $res and resname PRO and
                  (name N or name CA or name CB or name CG or name CD))
            group (resid $res and resname HIS and
                  (name CG or name ND1 or name CD2 or name CE1 or name NE2))
            group (resid $res and resname TYR and
                  (name CG or name CD1 or name CD2 or name CE1 or
                        name CE2 or name CZ))
            group (resid $res and resname TRP and
                  (name CG or name CD1 or name CD2 or name NE1 or
                        name CE2 or name CE3 or name CZ2 or name CZ3 or
                        name CH2))
            evaluate ( $res = $res + 1 )
          end loop group

          set echo on message on end

          cloop=false
          auto torsion
          maxe 10000
        end

        constraints
        interaction (not resname ANI) (not resname ANI)
          weights * 1 angl $ini_ang impr $ini_imp  {* Scale covalent constraints. *}
          end
        end

        noe                             {*Parameters for NOE effective energy term.*}
          ceiling=1000
          averaging  * cent
          potential  * square
          sqconstant * 1.
          sqexponent * 2
          scale      * 50.              {*Constant NOE scale throughout the protocol.*}
        end

        parameter                       {*Parameters for the repulsive energy term.*}
           nbonds
              repel=0.5                 {*Initial value for effective atom radius  *}
                                        {*--modified later.*}
              rexp=2 irexp=2 rcon=1.
              nbxmod=-2                 {*Initial value for nbxmod--modified later.*}
              wmin=0.01
              cutnb=4.5 ctonnb=2.99 ctofnb=3.
              tolerance=0.5
           end
        end

        restraints dihedral
              scale=5.                            {*Initial weight--modified later.*}
        end

        !
        ! reset the force constants and call the energy terms
        !

        eval ($bath  = $init_t)
        eval ($radius = $ini_rad)
        eval ($k_vdw = $ini_con)
        eval ($k_ang = $ini_ang)
        eval ($k_imp = $ini_imp)
        eval ($knoe  = $ini_noe)
        eval ($timestep = $ini_timestep)

        flags
          exclude * include bonds angl impr noe coup cdih sani
        end

        !
        ! re-init the coords
        !

        coor swap end
        coor copy end {* Save the first structure to copy to use as a reference *}

        !
        ! set some high-temp force constants
        !

        noe
          averaging  * sum
          potential  * soft
          sqconstant * 1.0
          sqexponent * 2
          sqoffset   * 0.0
          soexponent * 1
          asymptote  * 1.0
          rswitch * 0.5
          scale      * $hitemp_noe
        end

        parameters
           nbonds
              atom
              nbxmod 4  {* Can use 4 here, due to internal coordinate dynamics. *}
              wmin 0.01
              cutnb 4.5
              tolerance 0.5
              rexp 2
              irex 2
              repel $radius
              rcon $k_vdw
           end
        end


        vector do (vx = maxwell(3500)) (all)
        vector do (vy = maxwell(3500)) (all)
        vector do (vz = maxwell(3500)) (all)
        {* Set initial velocities to fit a temperature of 3500K. *}
        {* High temperature to promote convergence.              *}

        !
        ! high temp dynamics
        !

        evaluate ($tol = $bath/1000)
        dynamics internal
           nstep 0
           endt 20
           timestep $timestep
           tbath $bath
           response 20
           nprint 100
           etol $tol
        end

        flags exclude * include bond angle impr vdw noe coup cdih sani end

        eval ($bath  = $init_t)

        evaluate ($i_vdw = 0)
        while ($i_vdw < $ncycle_vdw) loop vdw    {* iterate changes in van der  *}
                                                {* Waals interaction. Scale and*}
                                                {* radius.                     *}
           evaluate ($i_vdw=$i_vdw+1)
           {* Min function is used to keep variables within ini_variable and   *}
           {* fin_variable.                                                    *}
           eval ($k_vdw = min($fin_con,$k_vdw*$k_vdwfact))
           eval ($radius = min($fin_rad,$radius*$radfact))
           eval ($k_ang = min($fin_ang,$k_ang*$ang_fac))
           eval ($k_imp = min ($fin_imp,$k_imp*$imp_fac))

           parameter
              nbonds
                 rcon $k_vdw
                 repel $radius
              end
           end
           constraints
              interaction (all) (all)
                 weights * 1 angl $k_ang impr $k_imp
              end
           end

           !
           ! vdw dynamics {* dynamics with Van der Waals repulsion turned on. *}
           !

           dynamics internal
              timestep $timestep
              endt 3
              tbath $bath
              nprint $nstep
              ntrfr 1
           end

        end loop vdw

        !
        ! cooling
        !
        restraints dihedral
            scale=200.   end {* increase dihedral term  *}

        evaluate ($i_cool = 0)

        while ($i_cool < $ncycle) loop cool
           evaluate ($i_cool=$i_cool+1)

           eval ($bath = $bath  - $tempstep)
           eval ($knoe = $knoe*$noe_fac)    {* Scale during cooling. *}
           eval ($timestep = $timestep*$timestep_fac)
           eval ($k_vdw = min($fin_con,$k_vdw*$k_vdwfact))
           eval ($radius = min($fin_rad,$radius*$radfact))
           eval ($k_ang = min($fin_ang,$k_ang*$ang_fac))
           eval ($k_imp = min($fin_imp,$k_imp*$imp_fac))

           noe scale * $knoe end
           parameter
              nbonds
                 rcon $k_vdw
                 repel $radius
              end
           end
           constraints
             interaction (not resname ANI) (not resname ANI)
              weights * 1 angl $k_ang impr $k_imp {* Scale impropers and angles *}
             end
           end

           !
           ! cooling dynamics
           !

           evaluate ($tol = $bath/1000)
           dynamics internal
              endt 2
              tbath $bath
              nprint $nstep
              ntrfr 1
           end

        end loop cool

        !
        ! final minimization - with fixed tensor axis
        !

        mini powell nstep 500 nprint 50 end

        !
        ! recenter
        !

        coor orient end

        !
        ! analysis
        ! evaluates RMS deviations and violations

        print threshold %4.2f noe
        eval ($rms_noe = $result)
        eval ($violations_noe = $violations)

        print thres 0.05 bonds
        eval ($rms_bonds = $result)

        print thres 5. angles
        eval ($rms_angles = $result)

        print thres 5. impropers
        eval ($rms_impropers = $result)

        print thres %4.2f cdih
        eval  ($rms_cdih = $result)
        eval  ($violations_cdih=$violations)

         remarks ===============================================================
        remarks trial structure %03i of %03i.
        remarks ===============================================================
        remarks      overall bonds angles improper vdw noe
        remarks energies: $ener $bond $angl $impr $vdw $noe
        remarks ===============================================================
        remarks            bonds angles impropers noe
        remarks  $rms_bonds $rms_angles $rms_impropers $rms_noe
        remarks ===============================================================
        remarks                 noe         dihedrals
        remarks violations :    $violations_noe         $violations_cdih
        remarks ===============================================================

      eval ($file = \"%s\")

      write coor output= $file end
      stop
        """%(thr_noe,thr_dih,n_try,ntrial,tmppdb))
        xplr.submit()
        # CHECK IF STRUCTURE IS ACCEPTED
        if xplor_accept(tmppdb,
                        psf,
                        restraintlist,
                        thr_noe=thr_noe,
                        thr_dih=thr_dih,
                        parameter=parprot,
                        xplor=xplor):
          accepted = 1
          # COPY TO FINAL FILENAME
          shutil.copy(tmppdb,finalpdb)
          os.remove(tmppdb)
          # ADD TO LIST OF ANNEALED STRUCTURES
          annealed.append(finalpdb)
          #prog.increment(n_acc)
        else:
          pass
      else:
        accepted = 1
        annealed.append(finalpdb)
      # OTHER SEED FOR NEXT STRUCTURE
      seed = randint(10000,99999)
  # SEND FROM OTHER NODES
  if myid!=0:
    pypar.send(annealed,0)
  # RECEIVE ON PROC 0
  else:
    for i in range(1,numproc):
      annealed += pypar.receive(i)
  # PRINT WARNING IF NEEDED
  if myid==0:
    if len(annealed)!=naccepted:
      warning("Only %i of %i structures accepted!"%(len(annealed),
                                                    naccepted))
  return annealed


# ANNEAL STRUCTURE
# ================
# ANNEAL STRUCTURE IN XPLORNIH WITH GMC'S PROTOCOL
def xplornih_anneal(pdbbase,
                    template,
                    psf,
                    restraintlist,
                    averaging='sum',
                    naccepted=20,
                    thr_noe=0.5,
                    thr_dih=5.0,
                    parprot=None,
                    xplor=None,
                    seed=None,
                    ntrial=5):
  if numproc > 1: import pypar
  # LIST OF ANNEAL AND ACCEPTED STRUCTURES
  annealed = []
  # TAKE DEFAULTS FOR PARAMETER AND XPLOR
  if not parprot: parprot = nmvconf["PAR_PROT"]
  if not xplor: xplor = nmvconf["XPLOR"]
  # SET INITIAL SEED
  if not seed: seed = randint(10000,99999)
  # THE PROGRESS INDICATOR
  #prog = progress_indicator(naccepted)
  n_acc = 0
  #prog.increment(n_acc)
  # DIVIDE FOR MY RUNS
  str_ids = range(1,naccepted+1)
  mylower,myupper = mpi_setrange(str_ids,myid,numproc)
  # TRY TO CALCULATE naccepted STRUCTURES
  for struct in range(mylower,myupper):
    n_try,accepted = 0,0
    # CONTINUE UNTILL THE STRUCTURE IS ACCEPTED
    # OR MAXIMUM NUMBER OF TRIES IS REACHED
    while ((n_try<ntrial) and not accepted):
      n_try += 1
      print "%03i - %03i\r"%(str_ids[struct],n_try),
      # TMP FILE
      tmppdb = os.path.join(os.path.dirname(pdbbase),
                            'trial_%i_%i_%s_%s.pdb'%(str_ids[struct],n_try,
                                                     os.getpid(),myid))
      # FINAL PDB
      finalpdb = "%s_%03i.pdb"%(pdbbase,str_ids[struct])
      if not os.path.exists(finalpdb):
        # INITIALIZE THE XPLOR SCRIPT CLASS
        xplr = xplor_script(xplor,scriptpath=nmvconf["TMP"])
        # READ THE STRUCTURE FILE
        xplr.write("structure\n  @@%s\nend"%psf)
        # READ PARAMETER FILE
        xplr.write("evaluate ($par_nonbonded=OPLSX)")
        xplr.write("parameter\n  @@%s\nend"%parprot)
        # READ PDB FILE
        xplr.write("coordinates @@%s"%template)
        # DO THE ANNEALING
        xplr.write("""
        evaluate ($seed=%i)

        set seed $seed  end
        !evaluate ($kbbang = 500.0)
        !evaluate ($kbbimp = 500.0)

        !--------------------------------------------------
        ! set the weights for the experimental energy terms

        evaluate ($knoe  = 50.0)      ! noes
        evaluate ($asym  = 0.1)       ! slope of NOE potential
        evaluate ($kcdi  = 10.0)      ! torsion angles
        evaluate ($krama = 0.002)     ! rama
        evaluate ($kandb = 0.001)
        evaluate ($kimdb = 0.001)
        evaluate ($klr = 0.001)       ! long range rama
        evaluate ($kvirt1doverall=0.0)
        evaluate ($kvirt1d=0.001)
        evaluate ($kvirt2d=0.001)
        evaluate ($kvirt3d=0.001)
        evaluate ($kprot = 0.0)       ! proton shift
        evaluate ($kprotd = 0.2)      ! proton shifts

        !rgyr
        !collapse
        ! scale 1.0
        !ordered region of protein, constant=(#res^0.38)*2.2
        ! assign (resid 1:101) 50.0 12.7
        !end

        !----------------------------------------------------------------------
        ! The next statement makes sure the experimental energies are used in the
        ! calculation, and switches off the unwanted energy terms.
        ! note that the NMR torsions are only switched on in the cooling stage
        ! we include the noncrystallographic symmetry right from the start
        !---------------------------------------------------------------------------
        ! Read experimental restraints
        !set message off echo off end

        noe
           reset
           nres = 5000
           set message off echo off end
           class all
           """%(seed))
        # GET ALL DISTANCE RESTRAINTS
        distlist = [r for r in restraintlist if r.type=="DIST"]
        for el in distlist:
          xplr.write(el.format("XPLOR"))
        xplr.write("""
        end

         set echo on message on end

        noe
          ceiling 1000
          averaging  all sum
          potential  all soft        !replace \"square\" by \"soft\" to fold from an extended strand
          scale      all $knoe
          sqconstant all 1.0
          sqexponent all 2
          soexponent all 1           !to fold from an extended strand or random coil uncomment
          rswitch    all 1.0         !the following 4 lines
          sqoffset   all 0.0
          asymptote  all 2.0
        end

        set message off echo off end

        !carbon
        !  phistep=180
        !  psistep=180
        !  nres=300
        !  class all
        !  force 0.5
        !  potential harmonic
        !  @rcoil.tbl      !rcoil shifts
        !  @expected_edited.tbl   !13C shift database
        !  set echo off message off end
        !  @cacb_shifts.tbl         !carbon shifts
        !  set echo on message on end
        !end

        restraints dihed
         reset
          scale $kcdi
          nass = 10000
          set message off echo off end
        """)
        dihelist = [r for r in restraintlist if r.type=="DIHE"]
        for el in dihelist:
          xplr.write(el.format("XPLOR"))
        xplr.write("""
          set message on echo on end
        end

        !@protons_setup.tbl
        !protons
        !     potential harmonic
        ! class alpha
        !     degeneracy 1
        !     force $kprot
        !     error 0.3
        !     @alpha.tbl
        ! class gly
        !     degeneracy 2
        !     force $kprot $kprotd
        !     error 0.3
        !     @alpha_degen.tbl
        ! class md
        !     degeneracy 2
        !     force $kprot $kprotd
        !     error 0.3
        !     @methyl_degen.tbl
        !  class ms
        !     degeneracy 1
        !     force $kprot
        !     error 0.3
        !     @methyl_single.tbl
        ! class os
        !     degeneracy 1
        !     force $kprot
        !     error 0.3
        !     @other_single.tbl
        !   class od
        !     degeneracy 2
        !     force $kprot $kprotd
        !     error 0.3
        !     @other_degen.tbla
        !
        !
        !end

        !couplings
        !  nres 400
        !  potential harmonic
        ! class phi
        !  degen 1
        !  force 1.0
        !  set echo off message off end
        !  coefficients 6.98 -1.38 1.72 -60.0
        !     @phij_cvn.tbl
        ! class gly  !for gly where you don't know stereoassignement
        !  degen 2
        !  force 1.0 0.2
        !  coefficients 6.98 -1.38 1.72 0.0
        !     @phij_gly_final.tbl
        !  set echo on message on end
        !end

        evaluate ($ksani = 0.01)
        evaluate ($ksani_CH = 1.0*$ksani)
        evaluate ($ksani_CHX = 0.25*$ksani)
        evaluate ($ksani_CACO = 0.035*$ksani)
        evaluate ($ksani_NCO = 0.050*$ksani)
        evaluate ($ksani_HNC = 0.108*$ksani)
        evaluate ($kmul = 0.2)

        ! inserted by chrissy ..... ?
        !  noe
        !    !ceiling=1000
        !    soexponent * 2
        !    rswitch    * 10.0
        !    sqoffset   * 0.0
        !    asymptote  * 0.0
        !  end

        !dipo
        !   nres=1000
        !!all dipolar couplings normalized to NH couplings (i.e. scaled appropriately)
        !!mobile side chains:
        !!   lower limit set to observed value minus 0.1 Hz
        !!   upper limit set to observed value times 2
        !!   employs square-well potential form
        !class mets
        !   average sum
        !   force $ksani_CHX
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !   @methyl_single_dip.tbl
        !
        !class ch
        !   average sum
        !   force $ksani_CHX
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !   @ch_dip.tbl
        !
        !class aro
        !   average sum
        !   force $ksani_CHX
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !   @ch_aro_dipolar.tbl
        !
        !class metd
        !   average sumdiff
        !   force $ksani_CHX $kmul
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !   @methyl_double_dip.tbl
        !
        !class monh
        !   average sum
        !   force $ksani
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !    @cvn_dip_mob_nh.tbl
        !
        !class moch
        !   average sum
        !   force $ksani_CH
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !    @cvn_dip_mob_ch.tbl
        !
        !class mocaco
        !   average sum
        !   force $ksani_CACO
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !   @cvn_dip_mob_caco.tbl
        !
        !class monco
        !   average sum
        !   force $ksani_NCO
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !   @cvn_dip_mob_nco.tbl
        !
        !class mohco
        !   average sum
        !   force $ksani_HNC
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !   @cvn_dip_mob_hnco.tbl
        !
        !{class ch2
        !   average sumdiff
        !   force $ksani_CHX $kmul
        !   potential square
        !   coeff 0.0 -17.0 0.17
        !   @ch2_double_new.tbl
        !}
        !end

        !sani
        !!all dipolar couplings normalized to NH dipolar couplings
        !!backbone dipolars
        !   nres=400
        !   class JNH
        !   force $ksani
        !   potential harmonic
        !   coeff 0.0 -17.0 0.17
        !   @cvn_dip_nh.tbl
        !
        !   class JCH
        !   force $ksani_CH
        !   potential harmonic
        !   coeff 0.0 -17.0 0.17
        !   @cvn_dip_ch.tbl
        !
        !   class JCACO
        !   force $ksani_CACO
        !   potential harmonic
        !   coeff 0.0 -17.0 0.17
        !   @cvn_dip_caco.tbl
        !
        !   class JNCO
        !   force $ksani_NCO
        !   potential harmonic
        !   coeff 0.0 -17.0 0.17
        !   @cvn_dip_nco.tbl
        !
        !   class JHNC
        !   force $ksani_HNC
        !   potential harmonic
        !   coeff 0.0 -17.0 0.17
        !   @cvn_dip_hnco.tbl
        !
        !
        !end

        evaluate ($rcon  = 0.003)

        parameters
          nbonds
            atom
            nbxmod 3
            wmin  =   0.01  ! warning off
            cutnb =   4.5   ! nonbonded cutoff
            tolerance 0.5
            repel=    0.9   ! scale factor for vdW radii = 1 ( L-J radii)
            rexp   =  2     ! exponents in (r^irex - R0^irex)^rexp
            irex   =  2
            rcon=$rcon      ! actually set the vdW weight
              end
        end

        !rama
        !nres=10000
        !!set message off echo off end
        !@2D_quarts_new.tbl
        !@3D_quarts_new.tbl
        !!@4D_quarts_intra_new.tbl
        !@forces_torsion_prot_quarts_intra.tbl
        !end
        set message on echo on end
        !@setup_quarts_torsions_intra_2D3D.tbl
        !!@setup_quarts_torsions_intra_4D.tbl

        !! Fixing the axis using harmonic restraint
        !! leave out, let both rotate

        vector do (refx=x) (all)
        vector do (refy=y) (all)
        vector do (refz=z) (all)

        dynamics internal
        reset
        !set up alignment axis
        !  group (resid 500)
        !  hinge rotate (resid 500)

        !setup some sidechain groups

            set message off echo off end
            evaluate ( $res = 1 )
            while ($res le 400) loop group
              group (resid $res and resname PHE and
                    (name CG or name CD1 or name CD2 or name CE1 or name CE2 or name CZ))
              group (resid $res and resname HIS and
                     (name CG or name ND1 or name CD2 or name CE1 or name NE2))
              group (resid $res and resname TYR and
                    (name CG or name CD1 or name CD2 or name CE1 or
                          name CE2 or name CZ))
              group (resid $res and resname TRP and
                    (name CG or name CD1 or name CD2 or name NE1 or
                          name CE2 or name CE3 or name CZ2 or name CZ3 or
                          name CH2))
              group (resid $res and resname ARG and
                    (name CD or name NE or name NH1 or name NH2))
              group (resid $res and resname GLU and
                    (name CD or name OE1 or name OE2))
              group (resid $res and resname GLN and
                    (name CD or name OE1 or name NE2))
              group (resid $res and resname ASP and
                    (name CG or name OD1 or name OD2))
              group (resid $res and resname ASN and
                    (name CG or name OD1 or name ND2))
            evaluate ( $res = $res + 1 )
          end loop group
        set message on echo on end
        cloop=false
        auto torsion
        maxe 10000
        end

        evaluate ($cool_steps = 3000)
        evaluate ($init_t  = 3000.01)
        evaluate ($tol = $init_t/1000)

        vector do (mass  = 100.0) (not resid 500)         ! uniform mass for all atoms
        !vector do (mass  = 100.0) (resid 500)
        vector do (fbeta = 10.0)  (all)                   ! coupling to heat bath

        coor copy end

        {* Generate Structures 1 -> 50 *}

        evaluate ($count =0)
        while ($count < %i)
          loop structure
          evaluate ($count = $count + 1)

        {====>}                             {*Filename(s) for embedded coordinates.*}

        vector do (x=xcomp) (all)
        vector do (y=ycomp) (all)
        vector do (z=zcomp) (all)

        evaluate ($ini_rad  = 0.9)        evaluate ($fin_rad  = 0.80)
        evaluate ($ini_con=  0.004)       evaluate ($fin_con=  4.0)
        evaluate ($ini_ang = 0.4)         evaluate ($fin_ang = 1.0)
        evaluate ($ini_imp = 0.1)         evaluate ($fin_imp = 1.0)

        evaluate ($ini_noe = 2.0)         evaluate ($fin_noe = 50.0)
        evaluate ($knoe  = $ini_noe)    ! slope of NOE potential
        evaluate ($ini_rama = 0.002)      evaluate ($fin_rama = 1.0)
        evaluate ($krama = $ini_rama)
        evaluate ($ini_lr = 0.0002)       evaluate ($fin_lr = 0.15)
        evaluate ($klr = $ini_lr)
        evaluate ($virt1d=$klr)
        evaluate ($virt2d=$klr)
        evaluate ($virt3d=$klr)

        evaluate ($ini_andb = 0.001)      evaluate ($fin_andb = 1000.0)
        evaluate ($kandb = $ini_andb)
        evaluate ($ini_imdb = 0.001)      evaluate ($fin_imdb = 2000.0)
        evaluate ($kimdb = $ini_imdb)

        evaluate ($ini_kbb_a = 500.0)     evaluate ($fin_kbb_a = 100.0)
        evaluate ($kbbang = $ini_kbb_a)
        evaluate ($ini_kbb_i = 500.0)     evaluate ($fin_kbb_i = 10.0)
        evaluate ($kbbimp = $ini_kbb_i)

        evaluate ($kcdi  = 10.0)        ! torsion angles

        evaluate ($ini_sani = 0.01)       evaluate ($fin_sani = 0.75)
        evaluate ($ksani  = $ini_sani)  ! slope of NOE potential
        evaluate ($ksani_CH = 1.0*$ksani)
        evaluate ($ksani_CHX = 0.25*$ksani)
        evaluate ($ksani_CACO = 0.035*$ksani)
        evaluate ($ksani_NCO = 0.050*$ksani)
        evaluate ($ksani_HNC = 0.108*$ksani)

        !sani class JNH force $ksani end
        !sani class JCACO force $ksani_CACO end
        !sani class JNCO force $ksani_NCO end
        !sani class JCH force $ksani_CH end
        !sani class JHNC force $ksani_HNC end

        !dipo class JNH force 0.0 end !$ksani end
        !dipo class JCACO force 0.0 end !$ksani_CACO end
        !dipo class JNCO force 0.0 end !$ksani_NCO end
        !dipo class JCH force 0.0 end !$ksani_CHX end !$ksani_CHX end
        !dipo class JHNC force 0.0 end !$ksani_HNC end
        !dipo class metd force $ksani_CHX $kmul end
        !!dipo class ch2 force  $ksani_CHX $kmul end
        !dipo class mets force $ksani_CHX end
        !dipo class ch force $ksani_CHX end
        !dipo class aro force  $ksani_CHX end !$ksani_CHX end

        !dipo class monh force 0.0 end !$ksani end
        !dipo class moch force 0.0 end !$ksani_CH end
        !dipo class mocaco force 0.0 end !$ksani_CACO end
        !dipo class monco force 0.0 end !$ksani_NCO end
        !dipo class mohco force 0.0 end !$ksani_HNC end

        evaluate ($ini_prot  = 0.02)        evaluate ($fin_prot  = 7.5)
        evaluate ($ini_protd  = 0.2)        evaluate ($fin_protd  = 0.2)

        evaluate ($kprot = 0.00)   !proton shifts
        evaluate ($kprotd = 0.00)   !proton shifts

        flags
          exclude *
          ! include bonds angl impr vdw noe rama carb coup sani dipo cdih coll
          include bonds angl impr vdw noe cdih
        end


        restraints dihed
          scale $kcdi
        end

        noe scale all $knoe end
        !rama
        !  @forces_torsion_prot_quarts_intra.tbl
        !end

        !prot
        ! class alpha force $kprot
        ! class ms force $kprot
        ! class os force $kprot
        ! class gly force $kprot $kprotd
        ! class md force $kprot $kprotd
        ! class od force $kprot $kprotd
        !end


        evaluate ($rcon  = 1.0)

        parameters
          nbonds
            atom
            nbxmod 3
            wmin  =   0.01  ! warning off
            cutnb =   100   ! nonbonded cutoff
            tolerance 45
            repel=    1.2   ! scale factor for vdW radii = 1 ( L-J radii)
            rexp   =  2     ! exponents in (r^irex - R0^irex)^rexp
            irex   =  2
            rcon=$rcon      ! actually set the vdW weight
             end
        end



        constraints

                interaction (not name ca) (all)

                weights * 1 angl 0.4 impr 0.1 vdw 0 elec 0 end

                interaction (name ca) (name ca)

                weights * 1 angl 0.4 impr 0.1 vdw 1.0 end

        end


          vector do (vx = maxwell($init_t)) (all)
          vector do (vy = maxwell($init_t)) (all)
          vector do (vz = maxwell($init_t)) (all)


          dynamics internal
              itype=pc6
              !maxe=100
              !adjustTS=False
              etol=$tol
              tbath=$init_t
              response= 20
              response= 5
              nstep=30000
              timestep= 0.002
              endtime=60
              cloop=false
        !      print verbose=stepDebug
        !      info
          end



        parameters
          nbonds
            atom
            nbxmod 3
            wmin  =   0.01  ! warning off
            cutnb =   4.5   ! nonbonded cutoff
            tolerance 0.5
            repel=    0.9   ! scale factor for vdW radii = 1 ( L-J radii)
            rexp   =  2     ! exponents in (r^irex - R0^irex)^rexp
            irex   =  2
            rcon =1.0      ! actually set the vdW weight
          end
        end


        evaluate ($kcdi = 200)
        restraints dihed

          scale $kcdi

        end


        evaluate ($final_t  = 25)        { K }
        evaluate ($tempstep = 12.5)     { K }

        evaluate ($ncycle = ($init_t-$final_t)/$tempstep)
        evaluate ($nstep = int($cool_steps*4.0/$ncycle))
        evaluate ($endtime = $nstep*0.002)


        evaluate ($bath  = $init_t)
        evaluate ($k_vdw = $ini_con)
        evaluate ($k_vdwfact = ($fin_con/$ini_con)^(1/$ncycle))
        evaluate ($radius=    $ini_rad)
        evaluate ($radfact = ($fin_rad/$ini_rad)^(1/$ncycle))
        evaluate ($k_ang = $ini_ang)
        evaluate ($ang_fac = ($fin_ang/$ini_ang)^(1/$ncycle))
        evaluate ($k_imp = $ini_imp)
        evaluate ($imp_fac = ($fin_imp/$ini_imp)^(1/$ncycle))
        evaluate ($noe_fac = ($fin_noe/$ini_noe)^(1/$ncycle))
        evaluate ($knoe = $ini_noe)
        evaluate ($rama_fac = ($fin_rama/$ini_rama)^(1/$ncycle))
        evaluate ($krama = $ini_rama)
        evaluate ($lr_fac = ($fin_lr/$ini_lr)^(1/$ncycle))
        evaluate ($klr = $ini_lr)
        evaluate ($virt1d=$klr)
        evaluate ($virt2d=$klr)
        evaluate ($virt3d=$klr)
        evaluate ($andb_fac = ($fin_andb/$ini_andb)^(1/$ncycle))
        evaluate ($kandb = $ini_andb)
        evaluate ($imdb_fac = ($fin_imdb/$ini_imdb)^(1/$ncycle))
        evaluate ($kimdb = $ini_imdb)
        evaluate ($kbb_fac_i = ($fin_kbb_i/$ini_kbb_i)^(1/$ncycle))
        evaluate ($kbb_fac_a = ($fin_kbb_a/$ini_kbb_a)^(1/$ncycle))
        evaluate ($kbbang = $ini_kbb_a)
        evaluate ($kbbimp = $ini_kbb_i)

        evaluate ($sani_fac = ($fin_sani/$ini_sani)^(1/$ncycle))
        evaluate ($ksani = $ini_sani)
        evaluate ($ksani_CH = 1.0*$ksani)
        evaluate ($ksani_CHX = 0.25*$ksani)
        evaluate ($ksani_CACO = 0.035*$ksani)
        evaluate ($ksani_NCO = 0.050*$ksani)
        evaluate ($ksani_HNC = 0.108*$ksani)

        evaluate ($kprot = $ini_prot)
        evaluate ($kprotd = $ini_protd)
        evaluate ($prot_fac = ($fin_prot/$ini_prot)^(1/$ncycle))
        evaluate ($prot_facd = ($fin_protd/$ini_protd)^(1/$ncycle))


        flags
          exclude *
          !include bonds angl impr vdw noe rama carb coup sani dipo cdih coll prot   !proton shifts turned on during cooling
          include bonds angl impr vdw noe cdih
        end

        vector do (vx = maxwell($bath)) (all)
        vector do (vy = maxwell($bath)) (all)
        vector do (vz = maxwell($bath)) (all)

        evaluate ($i_cool = 0)
        while ($i_cool < $ncycle) loop cool
            evaluate ($i_cool=$i_cool+1)

            evaluate ($bath  = $bath  - $tempstep)
            evaluate ($k_vdw=min($fin_con,$k_vdw*$k_vdwfact))
            evaluate ($radius=max($fin_rad,$radius*$radfact))
            evaluate ($k_ang = $k_ang*$ang_fac)
            evaluate ($k_imp = $k_imp*$imp_fac)
            evaluate ($knoe  = $knoe*$noe_fac)
            evaluate ($krama  = $krama*$rama_fac)
            evaluate ($klr  = $klr*$lr_fac)
        evaluate ($virt1d=$klr)
        evaluate ($virt2d=$klr)
        evaluate ($virt3d=$klr)
            evaluate ($kandb  = $kandb*$andb_fac)
            evaluate ($kimdb  = $kimdb*$imdb_fac)
            evaluate ($kbbang  = $kbbang*$kbb_fac_a)
            evaluate ($kbbimp  = $kbbimp*$kbb_fac_i)

        evaluate ($ksani  = $ksani*$sani_fac)
        evaluate ($ksani_CH = 1.0*$ksani)
        evaluate ($ksani_CHX = 0.25*$ksani)
        evaluate ($ksani_CACO = 0.035*$ksani)
        evaluate ($ksani_NCO = 0.050*$ksani)
        evaluate ($ksani_HNC = 0.108*$ksani)


         evaluate ($kprot  = min($fin_prot,$kprot*$prot_fac))
         evaluate ($kprotd  = min($fin_protd,$kprotd*$prot_facd))


            constraints interaction (all) (all) weights
                * 1 angles $k_ang improper $k_imp
            end end
            parameter
                nbonds
                cutnb=4.5 rcon=$k_vdw nbxmod=3 repel=$radius
            end       end
            noe scale all $knoe  end
            !sani class JNH force $ksani end
            !sani class JCACO force $ksani_CACO end
            !sani class JNCO force $ksani_NCO end
            !sani class JCH force $ksani_CH end
            !sani class JHNC force $ksani_HNC end

        !dipo class JNH force 0.0 end !$ksani end
        !dipo class JCACO force 0.0 end !$ksani_CACO end
        !dipo class JNCO force 0.0 end !$ksani_NCO end
        !dipo class JCH force 0.0 end !$ksani_CHX end !$ksani_CHX end
        !dipo class JHNC force 0.0 end !$ksani_HNC end
        !dipo class metd force $ksani_CHX $kmul end
        !!dipo class ch2 force $ksani_CHX $kmul end
        !dipo class mets force $ksani_CHX end
        !dipo class ch force $ksani_CHX end
        !dipo class aro force $ksani_CHX end
        !dipo class monh force 0.0 end !$ksani end
        !dipo class moch force 0.0 end !$ksani_CH end
        !dipo class mocaco force 0.0 end !$ksani_CACO end
        !dipo class monco force 0.0 end !$ksani_NCO end
        !dipo class mohco force 0.0 end !$ksani_HNC end

        !protons
        !     class alpha force $kprot
        !     class ms force $kprot
        !     class os force $kprot
        !     class md force $kprot $kprotd
        !     class od force $kprot $kprotd
        !     class gly force $kprot $kprotd
        !end

        !rama
        !  @forces_torsion_prot_quarts_intra.tbl
        !end


          dynamics internal
              itype=pc6
              !maxe=100
              !adjustTS=False
              etol=$tol
              tbath=$bath
              response= 20
              response= 5
              nstep=$nstep
              timestep=  0.002
              endtime=$endtime
              cloop=false
        !      print verbose=stepDebug
        !      info
          end



        end loop cool

        dynamics internal
          itype=powell
          nstep=40000
          maxcalls=20000
          nprint=1
          etol=1e-7
          gtol=0.01
          depred=0.001
        end

        !mini powell nstep= 250 nprint= 50 end  !cartesian minimization: not needed

           print threshold=%4.2f noe
           evaluate ($rms_noe=$result)
           evaluate ($violations_noe=$violations)
           print threshold=%4.2f cdih
           evaluate ($rms_cdih=$result)
           evaluate ($violations_cdih=$violations)
           print thres=0.05 bonds
           evaluate ($rms_bonds=$result)
           print thres=5. angles
           evaluate ($rms_angles=$result)
           print thres=5. impropers
           evaluate ($rms_impropers=$result)
           couplings print threshold 1.0 class phi end
           evaluate ($rms_coup = $result)
           evaluate ($end_viols = $violations)
           couplings print threshold 1.0 class gly end
           evaluate ($rms_coup_g = $result)
           evaluate ($end_viols_g = $violations)
           carbon print threshold = 1.0 end
           evaluate ($rms_ashift = $rmsca)
           evaluate ($rms_bshift = $rmscb)
           evaluate ($viol_shift = $violations)
           angledb print threshold=0.5 type torsion end
           evaluate ($rms_tordb = $rms)
           angledb print threshold=0.5 type angle end
           evaluate ($rms_angdb = $rms)

        !   sani print threshold=2.0 all end
        !   evaluate ($rms_sani_all=$result)
        !   evaluate ($viol_sani_all=$violations)
           sani print threshold=0.0 class JNH end
           evaluate ($rms_sani_JNH=$result)
           evaluate ($R_sani_JNH = $result*100/21.735)        !21.735 = sqrt[2*Da**2*(4+3*rhombicity**2)/5]
           evaluate ($viol_sani_JNH=$violations)
           sani print threshold=0.0 class JCACO end
           evaluate ($rms_sani_JCACO=$result*0.18666)
           evaluate ($R_sani_JCACO = $result*100/21.735)
           evaluate ($viol_sani_JCACO=$violations)
           sani print threshold=0.0 class JNCO end
           evaluate ($rms_sani_JNCO=$result*0.11068)
           evaluate ($R_sani_JNCO = $result*100/21.735)
           evaluate ($viol_sani_JNCO=$violations)
           sani print threshold=0.0 class JCH end
           evaluate ($rms_sani_JCH=$result*2.08953)
           evaluate ($R_sani_JCH = $result*100/21.735)
           evaluate ($viol_sani_JCH=$violations)
           sani print threshold=0.0 class JHNC end
           evaluate ($rms_sani_JHNC=$result*0.329)
           evaluate ($R_sani_JHNC = $result*100/21.735)
           evaluate ($viol_sani_JHNC=$violations)


          { dipo print threshold=0.5 class JNH end
           evaluate ($rms_dipo_JNH=$result)
           evaluate ($viol_dipo_JNH=$violations)
           dipo print threshold=0.5 class JCACO end
           evaluate ($rms_dipo_JCACO=$result*0.18666)
           evaluate ($viol_dipo_JCACO=$violations)
           dipo print threshold=0.5 class JNCO end
           evaluate ($rms_dipo_JNCO=$result*0.11068)
           evaluate ($viol_dipo_JNCO=$violations)
           dipo print threshold=0.5 class JCH end
           evaluate ($rms_dipo_JCH=$result*2.08953)
           evaluate ($viol_dipo_JCH=$violations)
           dipo print threshold=0.5 class JHNC end
           evaluate ($rms_dipo_JHNC=$result*0.329)
           evaluate ($viol_dipo_JHNC=$violations)
        }

           dipo print threshold=0.0 class ch end
           evaluate ($rms_dipo_ch=$result*2.08953)
           evaluate ($R_dipo_ch = $result*100/21.735)
           evaluate ($viol_dipo_ch=$violations)
           dipo print threshold=0.0 class ch2 end
           evaluate ($rms_dipo_ch2=$result*2.08953)
           evaluate ($R_dipo_ch2 = $result*100/21.735)
           evaluate ($viol_dipo_ch2=$violations)
           dipo print threshold=0.0 class mets end
           evaluate ($rms_dipo_mets=$result*2.08953/3)
           evaluate ($R_dipo_mets = $result*100/21.735)
           evaluate ($viol_dipo_mets=$violations)
           dipo print threshold=0.0 class metd end
           evaluate ($rms_dipo_metd=$result*2.08953/3)
           evaluate ($R_dipo_metd = $result*100/21.735)
           evaluate ($viol_dipo_metd=$violations)
           dipo print threshold=0.0 class aro end
           evaluate ($rms_dipo_aro=$result*2.08953/2)
           evaluate ($R_dipo_aro = $result*100/21.735)
           evaluate ($viol_dipo_aro=$violations)

           dipo print threshold=0.0 class monh end
           evaluate ($rms_dipo_mob_nh= $result)

           dipo print threshold=0.0 class moch end
           evaluate ($rms_dipo_mob_ch= $result*2.08953)

           dipo print threshold=0.0 class mocaco end
           evaluate ($rms_dipo_mob_caco= $result*0.18666)

           dipo print threshold=0.0 class monco end
           evaluate ($rms_dipo_mob_nco= $result*0.11068)

           dipo print threshold=0.0 class mohco end
           evaluate ($rms_dipo_mob_hnco= $result*0.329)



        prot print threshold 0.3 all normsd end
        evaluate ($eprms = $rms)
        evaluate ($epviols = $violations)


        prot print threshold 0.3 class ms normsd end
        evaluate ($s_methyl_rms = $rms)
        evaluate ($s_methyl_viols = $violations)

        prot print threshold 0.3 class alpha normsd end
        evaluate ($alpha_rms = $rms)
        evaluate ($alpha_viols = $violations)

        prot print threshold 0.3 class gly normsd end
        evaluate ($g_alpha_rms = $rms)
        evaluate ($g_alpha_viols = $violations)


        prot print threshold 0.3 class os normsd end
        evaluate ($s_other_rms = $rms)
        evaluate ($s_other_viols = $violations)

        prot print threshold 0.3 class md normsd end
        evaluate ($d_methyl_rms = $rms)
        evaluate ($d_methyl_viols = $violations)

        prot print threshold 0.3 class od normsd end
        evaluate ($d_other_rms = $rms)
        evaluate ($d_other_viols = $violations)


           remarks ===============================================================
           remarks trial structure %03i of %03i.
           remarks ===============================================================
           remarks      overall,bonds,angles,improper,vdw,cdih,noe
    !       remarks      overall,bonds,angles,improper,vdw,cdih,noe   !,coup,rama,carb,coll,sani,dipo
           remarks energies: $ener $bond $angl $impr $vdw $cdih $noe
    !       remarks energies: $ener $bond $angl $impr $vdw $cdih $noe !$coup $rama $carb $coll $sani $dipo
           remarks ===============================================================
           remarks            bonds,angles,impropers,cdih,noe,coup
           remarks  bonds etc: $rms_bonds,$rms_angles,$rms_impropers,$rms_cdih,$rms_noe,$rms_coup
           remarks  shifts RMS a, b: $rms_ashift, $rms_bshift
           remarks ===============================================================
           remarks                cdih end_coup end_coup_gly noe
           remarks violations :  $violations_cdih  $end_viols $end_viols_g $violations_noe
           remarks shifts:  $viol_shift
           remarks ===============================================================
           remarks jcoup stats:  end_rms  end_rms_gly
           remarks rms-d:  $rms_coup $rms_coup_g
           remarks ===============================================================
           remarks  sani   NH CH CACO NCO HNCO
           remarks  RMS sani: $rms_sani_JNH $rms_sani_JCH $rms_sani_JCACO $rms_sani_JNCO $rms_sani_JHNC
           remarks  R-factor sani: $R_sani_JNH $R_sani_JCH $R_sani_JCACO $R_sani_JNCO $R_sani_JHNC
           remarks  viol sani: $viol_sani_JNH $viol_sani_JCH $viol_sani_JCACO $viol_sani_JNCO $viol_sani_JHNC
           remarks ===============================================================
           remarks dipo_side  CH  CH3s CH3d ARO
           remarks RMS dipo_side:  $rms_dipo_ch  $rms_dipo_mets $rms_dipo_metd $rms_dipo_aro
           remarks R-factor dipo_side:  $R_dipo_ch  $R_dipo_mets $R_dipo_metd $R_dipo_aro
           remarks viol dipo_side:  $viol_dipo_ch $viol_dipo_ch2 $viol_dipo_mets $viol_dipo_metd $viol_dipo_aro
           remarks ===============================================================
           remarks      all alpha alpha_gly methyl(s) methyl(d) other(s) other(d)
           remarks RMS prot: $eprms $alpha_rms $g_alpha_rms $s_methyl_rms $d_methyl_rms $s_other_rms $d_other_rms
           remarks viol prot: $eprms $alpha_viols $g_alpha_viols $s_methyl_viols $d_methyl_viols $s_other_viols $d_other_viols
           remarks ==============================================================




        {====>}                        {*Name(s) of the family of final structures.*}
        evaluate ($file = \"%s\")
        write coor output= $file end

        end loop structure
        stop
        """%(1,thr_noe,thr_dih,n_try,ntrial,tmppdb))
        xplr.submit()
        # CHECK IF STRUCTURE IS ACCEPTED
        if xplor_accept(tmppdb,
                        psf,
                        restraintlist,
                        thr_noe=thr_noe,
                        thr_dih=thr_dih,
                        parameter=parprot,
                        xplor=xplor):
          accepted = 1
          # COPY TO FINAL FILENAME
          #finalpdb = "%s_%03i.pdb"%(pdbbase,str_ids[struct])
          shutil.copy(tmppdb,finalpdb)
          os.remove(tmppdb)
          # ADD TO LIST OF ANNEALED STRUCTURES
          annealed.append(finalpdb)
          #prog.increment(n_acc)
        else:
          pass
      else:
        accepted = 1
        annealed.append(finalpdb)
      # OTHER SEED FOR NEXT STRUCTURE
      seed = randint(10000,99999)
  # SEND FROM OTHER NODES
  if myid!=0:
    pypar.send(annealed,0)
  # RECEIVE ON PROC 0
  else:
    for i in range(1,numproc):
      annealed += pypar.receive(i)
  # PRINT WARNING IF NEEDED
  if myid==0:
    if len(annealed)!=naccepted:
      warning("Only %i of %i structures accepted!"%(len(annealed),
                                                    naccepted))
  return annealed


# CALCULATE AVERAGE STRUCTURE
# ===========================
# CALCULATE AVERAGE STRUCTURE BASED ON THE
# PROVIDED STRUCTURES
def xplor_calcave(pdbbase,nstruct,psf,
                  parameter=None,
                  xplor=None,
                  seed=None):
  # TAKE DEFAULTS FOR PARAMETER AND XPLOR
  if not parameter: parameter = nmvconf["Q_PAR"]
  if not xplor: xplor = nmvconf["XPLOR"]
  if not seed: seed = 65748309
  # INITIALIZE THE XPLOR SCRIPT CLASS
  xplr = xplor_script(xplor,scriptpath=nmvconf["TMP"])
  # CALCULATE THE AVERAGE
  xplr.write("""
    remarks file  nmr/average.inp
    remarks Computes the average structure, atomic rms differences from the
    remarks mean for a family of structures, and average overall rms
    remarks difference between the family and the mean structure.

    {====>}
    structure
@@%s
    end                     {*Read the structure file.*}


    {====>}       {*Backbone selection--this example is typical for proteins.*}
    vector idend ( store9 ) ( name ca or name n or name c )


       {*============ The first stage consists of computing the mean structure.*}

    {====>}                 {*Loop through the family of 8 accepted structures.*}
    evaluate ($end_count=%i)

    eval ($nfile=0)
    vector do (store1=0) (all)
    vector do (store2=0) (all)
    vector do (store3=0) (all)
    vector do (store4=0) (all)

    evaluate ($count = 0)
    while ($count < $end_count ) loop main
       evaluate ($count=$count+1)

    {====>}                     {*This is the name of the family of structures.*}
       evaluate ($filename=\"%s\"+encode($count)+\".pdb\")
       coor init end
       coor @@$filename

       if ($count=1) then
          coor copy end              {*Store first structure in comparison set.*}
       end if
       coor sele=( recall9 ) fit end
       vector do (store1=store1+x) (all)
       vector do (store2=store2+y) (all)
       vector do (store3=store3+z) (all)
       vector do (store4=store4+x*x+y*y+z*z) (all)
       eval ($nfile=$nfile+1)
    end loop main

    vector do (x = store1 / $nfile) (all)
    vector do (y = store2 / $nfile) (all)
    vector do (z = store3 / $nfile) (all)
    vector do (bcomp=sqrt(max(0,store4/$nfile-(x**2+y**2+z**2)))) (all)


            {*The second stage consists of computing an overall rms difference.*}

    evaluate ($ave_rmsd_all=0.)
    evaluate ($ave_rmsd_back=0.)

    coor copy end

    evaluate ($count = 0)
    while ($count < $end_count ) loop main
       evaluate ($count=$count+1)


    {====>}                     {*This is the name of the family of structures.*}
       evaluate ($filename=\"%s\"+encode($count)+\".pdb\")

       coor init end
       coor @@$filename
       coor fit sele=( recall9 ) end
       coor rms selection=( recall9 )end
       evaluate ($ave_rmsd_back = $ave_rmsd_back + $result)
       coor rms selection=( not hydrogen )end
       evaluate ($ave_rmsd_all = $ave_rmsd_all + $result)
    end loop main

    evaluate ($ave_rmsd_back=$ave_rmsd_back / $nfile)
    evaluate ($ave_rmsd_all =$ave_rmsd_all  / $nfile)
    display ave. rms diff. to the mean struct. for non-h atoms= $ave_rmsd_all
    display ave. rms diff. to the mean struct. for the backbone= $ave_rmsd_back

       {*====== Finally, the average structure and RMSDs are written to a file.*}
    coor swap end
    vector do (b=bcomp) ( all )

    remarks unminimized average over $nfile files
    remarks ave. rms diff. to the mean struct. for non-h atoms= $ave_rmsd_all
    remarks ave. rms diff. to the mean struct. for the backbone= $ave_rmsd_back
    remarks b array (last column) is the rms difference from the mean

    {====>}            {*Write average coordinates and RMSDs to specified file.*}
    write coordinates output=%save.pdb end

    stop
  """%(psf,nstruct,pdbbase,pdbbase,pdbbase))
  # SUBMIT XPLOR JOB
  xplr.submit()


# CHECK IF STRUCTURE IS ACCEPTED
# ==============================
# CHECK IF STRUCTURE IS ACCPEPTED BASED ON THE
# PROVIDED DATASET
def xplor_accept(pdb,psf,restraintlist,
                 averaging='sum',
                 thr_noe=0.5,
                 thr_dih=5.0,
                 parameter=None,
                 xplor=None):
  # SET SOME PARS
  accepted = 0
  pdba = os.path.join(os.path.dirname(pdb),'acc_%s'%os.path.basename(pdb))
  # TAKE DEFAULTS FOR PARAMETER AND XPLOR
  if not parameter: parameter = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_PAR"])
  if not xplor: xplor = nmvconf["XPLOR"]
  # INITIALIZE THE XPLOR SCRIPT CLASS
  xplr = xplor_script(xplor)
  # READ THE STRUCTURE FILE
  xplr.write("structure\n  @%s\nend"%psf)
  # READ PARAMETER FILE
  xplr.write("evaluate ($par_nonbonded=PROLSQ)")
  xplr.write("parameter\n  @%s\nend"%parameter)
  # READ THE EXPERIMENTAL DATA
  xplr.write(xplor_formatlist(restraintlist,averaging))
  # SELECT THE ACCEPTED STRUCTURES
  xplr.write("""
    noe                             {*Parameters for NOE effective energy term.*}
      ceiling=1000
      averaging  * %s
      potential  * square
      sqconstant * 1
      sqexponent * 2
      scale      * 50
    end

    parameter                       {*Parameters for the repulsive energy term.*}
      nbonds
        repel=0.75
        rexp=2 irexp=2 rcon=4.
        nbxmod=3
        wmin=0.01
        cutnb=4.5 ctonnb=2.99 ctofnb=3.
        tolerance=0.5
      end
    end

    restraints dihedral
      scale=200.
    end

    flags exclude * include bonds angle impr vdw noe cdih end

    set precision=4 end

    {====>}                             {*Filename(s) for embedded coordinates.*}
    evaluate ($filename=\"%s\")

    coor @@$filename
    evaluate ($violations=0)
    evaluate ($result=0)
    evaluate ($accept=0)
                              {*Print all NOE violations larger than 0.3 A *}
                              {*and compute RMS difference between observed*}
                              {*and model distances.                       *}
    print threshold=%4.2f noe
    evaluate ($rms_noe=$result)
    evaluate ($violations_noe=$violations)
    if ($violations_noe > 0) then  evaluate ( $accept=$accept + 1)   end if

                                       {*Print all dihedral angle restraint*}
                                       {*violations.                       *}
    print threshold=%4.2f cdih
    evaluate ($rms_cdih=$result)
    evaluate ($violations_cdih=$violations)
    if ($violations_cdih > 0) then  evaluate ( $accept=$accept + 1)   end if

    !print thres=0.05 bonds         {*Print deviations from ideal geometry.*}
    !evaluate ($rms_bonds=$result)
    !if ($result > 0.01) then  evaluate ( $accept=$accept + 1)   end if

    !print thres=5. angles
    !evaluate ($rms_angles=$result)
    !if ($result > 1) then  evaluate ( $accept=$accept + 1)   end if

    !print thres=5. impropers
    !evaluate ($rms_impropers=$result)

    distance from=( not hydrogen ) to=( not hydrogen ) cutoff=1.5 end

               {*rms difference for bond deviations from ideality < 0.01 A,*}
               {*rms difference for angle deviations from ideality < 2 deg.*}
    energy end

    if ($accept = 0 ) then
      {====>}
      evaluate ($filename=\"%s\")
      remarks ============================================================
      remarks            overall,bonds,angles,vdw,noe,cdih
      !remarks energies: $ener, $bond, $angl, $vdw, $noe, $cdih, $impr
      remarks ============================================================
      remarks            bonds, angles, impropers, noe, cdih
      !remarks rms-d: $rms_bonds,$rms_angles,$rms_impropers,$rms_noe,$rms_cdih
      remarks ============================================================
      remarks               noe,  cdih
      remarks violations.: $violations_noe, $violations_cdih

      write coordinates output=$filename end
    end if

    stop
  """%(averaging,pdb,thr_noe,thr_dih,pdba))
  # SUBMIT XPLOR JOB
  xplr.submit()
  # CHECK IF STRUCTURE IS ACCEPTED
  if os.path.exists(pdba):
    accepted = 1
    os.remove(pdba)
  return accepted

# CALCULATE THE Q-FACTOR FOR A PDB FILE
# =====================================
#
def xplor_qfactor(pdbfile,psf,restraintlist,
                  parameter=None,
                  xplor=None,
                  axispar=None,
                  axispdb=None,
                  axispsf=None):
  # SET Daxi AND Drho
  Daxi = restraintlist[0].Daxi
  Drho = restraintlist[0].Drho
  # READ DEFAULT FILES
  if not xplor:     xplor = nmvconf["XPLOR"]
  if not parameter: parameter = nmvconf["PAR_PROT"]
  if not axispar:   axispar = nmvconf["PAR_AXIS"]
  if not axispdb:   axispdb = nmvconf["PDB_AXIS"]
  if not axispsf:   axispsf = nmvconf["PSF_AXIS"]
  import random
  seed = randint(100000,999999)
  # INITIALIZE XPLOR SCRIPT
  xplr = xplor_script(xplor,scriptpath=nmvconf["TMP"],
                      logfiles='silent')
  # READ THE STRUCTURES FILES
  xplr.write("structure\n  @%s\nend"%psf)
  # READ PARAMETER FILE
  xplr.write("evaluate ($par_nonbonded=OPLSX)")
  xplr.write("parameter\n  @%s\n  @%s\nend"%(parameter,
                                             axispar))
  # READ PDB FILES
  xplr.write("coordinates @%s"%pdbfile)
  # READ AXIS
  xplr.write("structure\n  @%s\nend"%axispsf)
  xplr.write("coordinates @%s"%axispdb)
  # SET PARAMETERS
  xplr.write("sani reset")
  xplr.write("  nrestraints = %i"%len(restraintlist))
  xplr.write("  class       1")
  xplr.write("  potential    harmonic")
  xplr.write("  force        1")
  xplr.write("  coefficients 0.0 %7.3f %7.3f"%(Daxi,(Drho/Daxi)))
  # READ THE RESTRAINTS
  for r in restraintlist:
    xplr.write(r.format("XPLOR"))
  xplr.write("end")
  # SET ENERGY FLAGS
  xplr.write("""
  flags exclude *
  include
    oneb carb ncs dani
    vean sani dipo prot harm
  end
  """)
  # SET INTERACTION PARTNERS
  xplr.write("""
  constraints interaction
    (resname ANI) ( resname ANI)
  end
  constraints interaction
    (not resname ANI)
    (not resname ANI)
  end
  """)
  xplr.write("energy end")
  # OPTIMIZE ALIGNMENT TENSOR
  xplr.write("constraints fix (not resn ani) end")
  # RESTRAIN ANI HARMONICALLY
  xplr.write("""
  vector do (refx=x) (resname ani)
  vector do (refy=y) (resname ani)
  vector do (refz=z) (resname ani)
  restraints harmonic
    exponent = 2
  end
  vector do (harmonic = 20.0)(resname ANI and name OO)
  vector do (harmonic = 0.0) (resname ANI and name Z )
  vector do (harmonic = 0.0) (resname ANI and name X )
  vector do (harmonic = 0.0) (resname ANI and name Y )

  flags exclude sani end
  evaluate ($seed=%i)
  set seed = $seed end
  dynamics  verlet
    nstep=1000  timestep=0.001 iasvel=maxwell  firsttemp= 300.
    tcoupling = true  tbath = 300.   nprint=50  iprfrq=0
  end
  flags include sani end

  minimize powell nstep=400 drop=5 nprint=50 end

  energy end
  """%seed)

  # PRINT ANALYSIS
  xplr.write("sani")
  xplr.write("  print thres = 0.0 1")
  xplr.write("end")
  xplr.write("evaluate($rms_sani = $result)")
  d = math.sqrt(2*(Daxi**2)*(4+3*(Drho/Daxi)**2)/5)
  xplr.write("evaluate ($R_sani_JNH = $result*100/%7.3f)"%d)
  #print xplr.scriptpath
  xplr.submit()
  # OPEN LOGFILE FOR ANALYSIS
  content = open(xplr.logpath,'r').readlines()
  inlist = 0
  sumsq_obs,sumsq_dif = 0.,0.
  rdcd = {}
  for line in content:
    if len(line)>0 and line[:9]==' SANI>end': inlist = 0
    if inlist:
      Dcal = float(line[45:53])
      Dobs = float(line[53:61])
      sumsq_obs += (Dobs)**2
      sumsq_dif += (Dobs-Dcal)**2
      resn = int(line.split()[0])
      rdcd[resn] = rdcd.get(resn,[]) + [(Dobs-Dcal)**2]
    if len(line)>0 and line[:7]=='class 1': inlist = 1
  list = rdcd.keys()
  list.sort()
  for el in list:
    print "%3i %7.3f"%(el,avg_list(rdcd[el],sdflag=0))
  qfactor = (sumsq_dif/len(restraintlist))/(sumsq_obs/len(restraintlist))
  rfactor = math.sqrt(5*(sumsq_dif/len(restraintlist))/
                      (2*(Daxi**2)*(4+3*(Drho/Daxi)**2)))
  #print "Q: %5.2f"%qfactor
  #print "R: %5.2f"%rfactor
  #print "T: %5.2f = %5.2f"%(qfactor/math.sqrt(2),rfactor)
  # DELETE THE LOGFILE
  os.remove(xplr.logpath)
  #print xplr.logpath
  return rfactor


# CREATE A SUMMARY FILE ON VIOLATIONS
# ===================================
#
def xplor_violanalysis(pdblist,psf,restraintlist,outputfile=None,
                       cutoff={"DIST":[1. , .75, .5, .25, .1],
                               "DIHE":[10., 7.5, 5., 2.5, 1.]},
                       constcutoff=0.50,averaging='sum',parameter=None,xplor=None):
  constperc = int(100*constcutoff)
  # CONSTRUCT DICTIONARIES
  viol,rviol = xplor_violations(pdblist,psf,restraintlist,
                                averaging,parameter,xplor)
  # COUNT NUMBER OF RESIDUES
  nres = 0
  pdb = pdb_file.Structure(pdblist[0])
  for chain in pdb.peptide_chains:
    for residue in chain: nres += 1
  # WRITE OUTPUT
  if outputfile:
    file = open(outputfile,'w')
    # PRINT NUMBER AND SIZE OF VIOLATIONS
    # -----------------------------------
    # CYCLE DIFFERENT TYPES
    for type in cutoff.keys():
      # SORT LIMITS
      cutoff[type].sort()
      # MAKE SURE ZERO IS FIRST CUTOFF
      if cutoff[type][0] not in [0.0,0]:
        cutoffzero = [0]+cutoff[type]
      else: cutoffzero = cutoff[type]
      # FILTER RESTRAINT FOR TYPE
      typelist = [el for el in restraintlist if el.type==type]
      if len(typelist)>0:
        if type=='DIST':
          file.write('Distance restraints\n')
          file.write('===================\n')
        elif type=='DIHE':
          file.write('Dihedral angle restraints\n')
          file.write('=========================\n')
        file.write("%24s :%5i\n"%("Number of structures",len(pdblist)))
        file.write("%24s :%5i\n"%("Number of restraints",len(typelist)))
        file.write("%24s :%8.2f\n"%("Restraints/residue",len(typelist)/float(nres)))
        cumulative = {}
        # CALCULATE RMS
        rmslist = []
        for i in range(len(pdblist)):
          rms = 0.0
          for el in typelist:
            rms += rviol[str(el)][i]**2
          rms = math.sqrt(rms/(len(typelist)))
          rmslist.append(rms)
        rms = avg_list(rmslist)
        file.write("%24s :%8.4f +/-%8.4f\n"%("RMS violations",
                                             rms[0],rms[1]))
        # DO THE VIOLATION ANALYSIS
        viol_str, viol_cum = {},{}
        for limit in cutoffzero[1:]:
          viol_cum[limit]=0
          viol_str[limit]={}
          for i in range(len(pdblist)): viol_str[limit][i]=0
        above = 0
        # IN EVERY STRUCTURE
        for i in range(len(pdblist)):
          # CHECK EACH RESTRAINT
          for r in typelist:
            # FOR EVERY LIMIT
            for j in range(1,len(cutoffzero)):
              limit = cutoffzero[j]
              viol = rviol[str(r)][i]
              if viol <= limit and viol > cutoffzero[j-1]:
                viol_cum[limit]+=1
                viol_str[limit][i]+=1
            if viol >= cutoffzero[-1]: above +=1
        # PRINT SUMMARY
        file.write("\nNumber of violations       Total  Per model\n")
        for i in range(1,len(cutoffzero)):
          vi = cutoffzero[i]
          vj = cutoffzero[i-1]
          avgl = []
          for j in range(len(pdblist)):
            avgl.append(viol_str[cutoffzero[i]][j])
          avg = avg_list(avgl)
          file.write("%6.2f <  viol <= %6.2f : %5i  %5.2f +/- %5.2f\n"%(vj,vi,
                                                                     viol_cum[vi],
                                                                     avg[0],
                                                                     avg[1]))
        # OUTSIDE LIMITS
        file.write("          viol >  %6.2f : %5i\n"%(cutoffzero[-1],above))
        file.write("\n\n")


    # CONSTRUCT OVERVIEW OF VIOLATIONS IN STRUCTURES
    # ----------------------------------------------
    # DEFINE THE ENSEMBLE
    file.write('Ensemble\n')
    file.write('========\n')
    file.write('%i structures in ensemble.\n'%len(pdblist))
    file.write('Index number below refer to the numbers used in\n')
    file.write('the following violation analyses.\n\n')
    file.write('index\tfilename\n')
    for i in range(1,len(pdblist)+1):
      file.write("%i\t%s\n"%(i,pdblist[i-1]))
    file.write("\n\n")
    # BUILD STRING TO GO ON TOP
    topval = len(pdblist)
    topstr,i = '',1
    while i <= topval:
      if (i+1)%10==0 or i==1:
        if i!=1: topstr+="%i"%(i+1)
        else: topstr+="1"
        i+=len("%i"%(i+1))-1
      elif i%5==0 and i%10!=0: topstr+="."
      elif i==topval:
        val = "%i"%topval
        topstr+=val[-1]
      else: topstr+=" "
      i+=1
    # SYMBOLS TO USE
    flags = string.letters
    # CYCLE DIFFERENT TYPES
    for type in cutoff.keys():
      typelist = [el for el in restraintlist if el.type==type]
      if cutoff[type][0] not in [0.0,0]:
        cutoffzero = [0]+cutoff[type]
      if type=='DIST' and len(typelist)>0:
        file.write('Distance restraints\n')
        file.write('===================\n')
        for i in range(1,len(cutoffzero)):
          if i<len(flags):
            file.write('%s    = (%5.2f < violation <= %5.2f) A.\n'%(flags[i-1],
                                                                  cutoffzero[i-1],
                                                                  cutoffzero[i]))
        file.write('RMS  = RMS violation in A.\n')
        file.write('Vmax = maximum violation in A.\n')
        file.write('C    = consistently violating (>%3i%% of structures)\n\n'%constperc)
        file.write('%s  RMS   Vmax  C    restraint\n'%topstr)
      elif type=='DIHE' and len(typelist)>0:
        file.write('Dihedral angle restraints\n')
        file.write('=========================\n')
        for i in range(1,len(cutoffzero)):
          if i<len(flags):
            file.write('%s    = (%5.1f < violation <= %5.1f degrees.\n'%(flags[i-1],
                                                                       cutoffzero[i-1],
                                                                       cutoffzero[i]))
        file.write('RMS  = RMS violation in degrees.\n')
        file.write('Vmax = maximum violation in degrees.\n')
        file.write('C    = consistently violating (>%3i%% of structures)\n\n'%constperc)
        file.write('%s  RMS   Vmax  C    restraint\n'%topstr)
      # CYCLE ALL RESTRAINTS AND BUILD A DICTIONARY WITH
      # THE TOTAL SUM OF VIOLATIONS AS KEY
      vdict = {}
      for r in typelist:
        stri,const = '',''
        constcount,vsum = 0,0.0
        # CYCLE ALL STRUCTURES
        for elem in rviol[str(r)]:
          violstatus = -1
          # CYCLE THE CUTOFF
          for i in range(len(cutoffzero)):
            if elem > cutoffzero[i]:
              violstatus = i
          # PRINT APPROPRIATE FLAG
          if violstatus != -1:
            constcount += 1
            stri+=flags[violstatus]
            f = flags[violstatus]
          else:
            stri+='.'
          # ADD TOTAL SUM OF VIOLATIONS
          vsum += elem
        frac = float(constcount)/len(rviol[str(r)])
        if frac >= constcutoff:
          const = "%3i%%"%(int(frac*100))
        vmax = max(rviol[str(r)])
        # CONSTRUCT THE STRING
        rstring = "%s %5.3f %5.3f %4s %s\n"%(string.ljust(stri,topval),
                                             avg_list(rviol[str(r)])[0],
                                             vmax,
                                             const,
                                             str(r))
        vdict[vsum]=vdict.get(vsum,[])+[rstring]
      # SORT THE DICTIONARY KEYS
      sums = vdict.keys()
      sums.sort()
      sums.reverse()
      for sum in sums:
        for el in vdict[sum]:
          file.write(el)
      file.write("\n\n")
    file.close()
  return viol,rviol

# GET VIOLATIONS OF RESTRAINTLIST IN STRUCTURES
# =============================================
# FUNCTION RETURN A DICTIONARY WITH THE VIOLATIONS IN
# THE PROVIDED PDB FILE. VIOLATIONS ARE GROUPED IN
# DIFFERENT CATEGORIES:
# - DIST: 0.0, <0.1, <0.2, <0.3, <0.4, <0.5, >=0.5
# - DIHE: 0.0, <1.0, <2.0, <3.0, <4.0, <5.0, >=5.0
def xplor_violations(pdblist,psf,restraintlist,
                     averaging='sum',
                     parameter=None,
                     xplor=None):
  # WE WANT TO SEE ALL RESTRAINTS, THEREFORE WE PRINT ALL VIOLATIONS!
  thr_noe, thr_dih = -1,-1
  # INITIALIZE OUTPUT DICTIONARIES
  rviol = {}
  viol = {"DIST":{},"DIHE":{}}
  for el in ["< 0.1","< 0.2","< 0.3","< 0.4","< 0.5",">=0.5"]: viol["DIST"][el]=0
  for el in ["< 1.0","< 2.0","< 3.0","< 4.0","< 5.0",">=5.0"]: viol["DIHE"][el]=0
  # MAKE A LIST
  if type(pdblist)!=types.ListType: pdblist = [pdblist]
  for pdb in pdblist:
    # TAKE DEFAULTS FOR PARAMETER AND XPLOR
    if not parameter: parameter = os.path.join(nmvconf["Q_PATH"],nmvconf["Q_PAR"])
    if not xplor: xplor = nmvconf["XPLOR"]
    # INITIALIZE THE XPLOR SCRIPT CLASS
    xplr = xplor_script(xplor,logfiles='silent')
    # READ THE STRUCTURE FILE
    xplr.write("structure\n  @%s\nend"%psf)
    # READ PARAMETER FILE
    xplr.write("evaluate ($par_nonbonded=PROLSQ)")
    xplr.write("parameter\n  @%s\nend"%parameter)
    # READ THE EXPERIMENTAL DATA
    xplr.write(xplor_formatlist(restraintlist,averaging))
    # WE NEED TO SORT THE RESTRAINTS HERE, SINCE xplor_formatlist ALSO DOES
    # OTHERWISE THE NUMBERING WILL NOT MATCH...
    dist,dihe = [],[]
    for r in restraintlist:
      if r.type == "DIST": dist.append(r)
      if r.type == "DIHE": dihe.append(r)
    dist.sort(lambda x, y: cmp(x.format(), y.format()))
    dihe.sort(lambda x, y: cmp(x.format(), y.format()))
    # SCREEN THE VIOLATIONS
    xplr.write("""
      noe                             {*Parameters for NOE effective energy term.*}
        ceiling=1000
        averaging  * %s
        potential  * square
        sqconstant * 1
        sqexponent * 2
        scale      * 50
      end

      parameter                       {*Parameters for the repulsive energy term.*}
        nbonds
          repel=0.75
          rexp=2 irexp=2 rcon=4.
          nbxmod=3
          wmin=0.01
          cutnb=4.5 ctonnb=2.99 ctofnb=3.
          tolerance=0.5
        end
      end

      restraints dihedral
        scale=200.
      end

      flags exclude * include bonds angle impr vdw noe cdih end

      set precision=4 end

      {====>}                             {*Filename(s) for embedded coordinates.*}
      evaluate ($filename=\"%s\")

      coor @@$filename
      evaluate ($violations=0)
      evaluate ($result=0)
      evaluate ($accept=0)
                                {*Print all NOE violations larger than 0.3 A *}
                                {*and compute RMS difference between observed*}
                                {*and model distances.                       *}
      print threshold=%4.2f noe
      evaluate ($rms_noe=$result)
      evaluate ($violations_noe=$violations)
      if ($violations_noe > 0) then  evaluate ( $accept=$accept + 1)   end if

                                         {*Print all dihedral angle restraint*}
                                         {*violations.                       *}
      print threshold=%4.2f cdih
      evaluate ($rms_cdih=$result)
      evaluate ($violations_cdih=$violations)
      if ($violations_cdih > 0) then  evaluate ( $accept=$accept + 1)   end if

      distance from=( not hydrogen ) to=( not hydrogen ) cutoff=1.5 end

                 {*rms difference for bond deviations from ideality < 0.01 A,*}
                 {*rms difference for angle deviations from ideality < 2 deg.*}
      energy end

      stop
    """%(averaging,pdb,thr_noe,thr_dih))
    # SUBMIT XPLOR JOB
    xplr.submit()
    # READ THE XPLOR OUTPUT FILE
    # PARSE THE VIOLATIONS OUT OF THE LOG FILE
    distcount,dihecount = 0,0
    xplorlog = open(xplr.logpath,'r').readlines()
    for line in xplorlog:
      # THE DISTANCE VIOLATIONS
      if line[:11]==' R<average>':
        delta = abs(float(line[53:63]))
        if delta!=0.0:
          # STORE DISTRIBUTION
          if   delta < 0.1: viol["DIST"]["< 0.1"]=viol["DIST"].get("< 0.1",0)+1
          elif delta < 0.2: viol["DIST"]["< 0.2"]=viol["DIST"].get("< 0.2",0)+1
          elif delta < 0.3: viol["DIST"]["< 0.3"]=viol["DIST"].get("< 0.3",0)+1
          elif delta < 0.4: viol["DIST"]["< 0.4"]=viol["DIST"].get("< 0.4",0)+1
          elif delta < 0.5: viol["DIST"]["< 0.5"]=viol["DIST"].get("< 0.5",0)+1
          elif delta >=0.5: viol["DIST"][">=0.5"]=viol["DIST"].get(">=0.5",0)+1
        # STORE INDIVIDUAL RESTRIANTS
        rviol[str(dist[distcount])]=rviol.get(str(dist[distcount]),[])+[delta]
        distcount+=1
      # THE DIHEDRAL VIOLATIONS
      if line[:9]==' Dihedral':
        delta = abs(float(line[72:82]))
        if delta!=0:
          # STORE DISTRIBUTION
          if   delta < 1.0: viol["DIHE"]["< 1.0"]=viol["DIHE"].get("< 1.0",0)+1
          elif delta < 2.0: viol["DIHE"]["< 2.0"]=viol["DIHE"].get("< 2.0",0)+1
          elif delta < 3.0: viol["DIHE"]["< 3.0"]=viol["DIHE"].get("< 3.0",0)+1
          elif delta < 4.0: viol["DIHE"]["< 4.0"]=viol["DIHE"].get("< 4.0",0)+1
          elif delta < 5.0: viol["DIHE"]["< 5.0"]=viol["DIHE"].get("< 5.0",0)+1
          elif delta >=5.0: viol["DIHE"][">=5.0"]=viol["DIHE"].get(">=5.0",0)+1
        # STORE INDIVIDUAL RESTRAINTS
        rviol[str(dihe[dihecount])]=rviol.get(str(dihe[dihecount]),[])+[delta]
        dihecount+=1
    if len(dist)!=distcount or len(dihe)!=dihecount:
      error("XPLOR output does not match restraintlist")
    # CLEAN UP XPLOR JUNK
    os.remove(xplr.scriptpath)
    os.remove(xplr.logpath)
  return viol,rviol


#  ======================================================================
#    W H A T  I F   S C R I P T   C L A S S
#  ======================================================================

class wif_script:
  """
  This class provides an interface to WHAT IF
  - Create a class instance passing the command to run WHATIF
  - Instance.error contains an error description if something went wrong
  - Instance.clear() clears the current script
  - Instance.write() adds a line to the script
  - Instance.submit() executes the script in WHATIF
  It is possible to provide a custom TOPOLOGY.H. They can be handy,
  especially if a typical proton nomenclature is desired. Look at
  whatif/dbdata/RESNAM.DAT if there are no nomenclature conflicts!
  """

  # OPEN SCRIPT FILE FOR OUTPUT
  # ===========================
  # - whatif IS THE COMMAND TO RUN WHATIF
  # - runpath IS THE PATH WHERE WHATIF IS RAN
  # - errorfunc IS THE NAME OF THE ERROR HANDLING FUNCTION
  def __init__(self,whatif,runpath=None,errorfunc=None,topology=None):
    self.whatif=whatif
    if runpath == None: self.runpath=nmvconf["WHATIF_RUNPATH"]
    else: self.runpath=runpath
    self.errorfunc=errorfunc
    self.topology=topology
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
    self.scriptpath = os.path.join(self.runpath,"STARTUP_%s.FIL"%os.getpid())
    try: self.script=open(self.scriptpath,"w")
    except: self.raiseerror("WHATIF script %s could not be created"%self.scriptpath)

   # ADD A LINE TO THE SCRIPT
  # ========================
  def write(self,line):
    if (not self.error): self.script.write(line+"\n")

  # SUBMIT SCRIPT
  # =============
  def submit(self):
    if (not self.error):
      self.script.close()
      ret = 0
      try:
        # REMEMBER CURRENT LOCATION
        cur_loc = os.getcwd()
        # CHANGE TO TMP DIR
        os.chdir(self.runpath)
        # COPY TOPOLOGY.H
        if self.topology:
          toppath = os.path.join(self.runpath,'TOPOLOGY.H')
          # CLEAN ANY PREVIOUS TOPOLOGY FILE
          if os.path.exists(toppath): os.remove(toppath)
          shutil.copy(self.topology,toppath)
        ret=os.system("%s script %s"%(self.whatif,self.scriptpath))
        # BACK TO THE ORIGINAL LOCATION
        os.chdir(cur_loc)
      except: self.raiseerror("WHATIF could not be run")
      if (ret): self.raiseerror("WHATIF returned error %d"%ret)
    os.remove(self.scriptpath)
    return


#  ======================================================================
#    W H A T  I F   F U N C T I O N   W R A P P E R
#  ======================================================================

# REGULARIZE STRUCTURE
# ====================
# QUICKY REGULARIZE STRUCTURE WITH WHATIF
# NOT FINISHED YET!
def wif_regularize(file):
  print "Regularizing stucture:\n%s"%file
  # CREATE WHATIF SCRIPT
  script = wif_script(nmvconf["WHATIF_RUN"])
  script.write("getmol")
  print "Done."

# DETERMINE MATRIX OF PAIRWISE CA RMSDS
# =====================================
# - filelist CONTAINS THE NAMES OF THE PDB-FILES TO SUPERPOSE.
def wif_rmsdmtx(filelist):
  global wifmaxaa
  #chainid="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  print "Preparing to determine pairwise superposition matrix..."
  # INITIALIZE MATRIX
  size=len(filelist)
  mtx=[]
  for i in range(size): mtx.append([None]*size)
  # READ FIRST MODEL TO DETERMINE RESIDUE NUMBER
  pdb=pdb_file.Structure(filelist[0])
  seqlen=len(pdb.residues)
  # CALCULATE THE MAXIMUM SUB-MATRIX SIZE (MODELS WHATIF CAN READ BEFORE SOUP IS FULL)
  # (62 POSSIBLE CHAIN IDENTIFIERS)
  maxsubsize=min(20,int((float(wifmaxaa)*0.9)/seqlen)-1)
  if (maxsubsize<1): error("Molecule too large for superposition")
  # CYCLE THROUGH THE ROWS OF THE MATRIX
  for i in range(0,size,maxsubsize):
    # CREATE WHATIF SCRIPT
    script=wif_script(nmvconf["WHATIF_RUN"],'/home/snabuurs/python/nmr_valibase/')
    # LOAD ALL "ROW" MOLECULES
    rowmols=min(maxsubsize,size-i)
    print "Now superposing molecules %d - %d" % (i,i+rowmols-1)
    nmrlist=[]
    for k in range(rowmols): nmrlist.append(filelist[i+k])
    dsc_remove("ensemble.pdb")
    nmv_mergepdb(nmrlist,"ensemble.pdb")
    #for k in range(rowmols):
    #script.write("%%setcha m%d 0 y %s" % (k+1,chainid[k]))
    script.write("getmol ensemble.pdb\n\n10000")
    # ADDED BY SN
    script.write("n")
    # START THE LOG FILE
    dsc_remove("suppos.log")
    script.write("suppos\ndolog suppos.log 0")
    # CYCLE THROUGH THE COLUMNS OF THE MATRIX
    # MAKE THE "FREE" SUPERPOSITIONS (MOLECULES ALREADY LOADED)
    for j in range(rowmols):
      for k in range(j+1,rowmols):
        script.write("range1 m%d 0" % (j+1))
        script.write("range2 m%d\ndosup" % (k+1))
    # MAKE THE REMAINING SUPERPOSITIONS, LOADING AND DELETING COLUMN MOLECULES
    for j in range(i+rowmols,size):
      script.write("getmol %s\n" % filelist[j])
      for k in range(rowmols):
        # THIS n IS NECESSARY IN CASE WHAT IF DETECTS A CA BUMP OF THE MODEL
        #   WITH THE NMR ENSEMBLE AND ASKS IF ALTERNATIVE RESIDUES SHOULD BE
        #   DELETED
        script.write("n")
        script.write("range1 m%d 0" % (k+1))
        script.write("range2 m%d\ndosup" % (rowmols+1))
      script.write("%%delmol m%d" % (rowmols+1))
    # SUBMIT THE SCRIPT
    script.write("nolog\nfullst y\n")
    script.submit()
#    raise SystemExit
    # CHECK THAT WHAT IF CREATED AT LEAST A BIT OF OUTPUT
    if (script.error): error("Submission of WHATIF script failed")
    # PARSE THE LOG FILE AND ADD RMSD VALUES TO MATRIX
    log=open("suppos.log","r").readlines()
    pos=0
    for j in range(rowmols):
      # RMSD OF SELF SUPERPOSITION IS ZERO
      mtx[i+j][i+j]=0
      for k in range(j+1,rowmols):
        while (len(log[pos])<6 or log[pos][0:6]!="RMS of"): pos=pos+1
        rmsd=float(log[pos][22:])
        mtx[i+j][i+k]=rmsd
        mtx[i+k][i+j]=rmsd
        pos=pos+1
    for j in range(i+rowmols,size):
      for k in range(rowmols):
        while (len(log[pos])<6 or log[pos][0:6]!="RMS of"): pos=pos+1
        rmsd=float(log[pos][22:])
        mtx[i+k][j]=rmsd
        mtx[j][i+k]=rmsd
        pos=pos+1
  return(mtx)


#  ======================================================================
#    S H I F T X   C L A S S
#  ======================================================================
class shiftx:
  """
  This class provides an interface to SHIFTX
  - Create a class instance passing the command to run SHIFTX
  - Instance.predictions contains a dictionary of predicted shifts
  - Instance.output contains the SHIFTX output as a list of lines.
  """
  def __init__(self,shiftx,runpath='/tmp',errorfunc=None):
    self.shiftx      = shiftx
    self.runpath     = runpath
    self.errorfunc   = errorfunc
    self.predictions = {}
    self.nuclei      = {}

  def clear():
    self.predictions = {}
    self.nuclei      = {}

  # DO A CHEMICAL SHIFT PREDICTION
  # ==============================
  def predict(self,pdbfile,chainid=''):
    # OUTPUT FILE
    self.outfile  = os.path.join(self.runpath,
                                 '%s_%s.shiftout'%(os.getpid(),
                                                   socket.gethostname()))
    self.pdbfile  = pdbfile
    # THE SHIFTX COMMAND
    cmd = "%s 1%s %s %s"%(self.shiftx,
                          chainid,
                          self.pdbfile,
                          self.outfile)
    # EXECUTE THE COMMAND
    os.system(cmd)
    # READ THE OUTPUT
    content = open(self.outfile,'r').readlines()
    # WE ONLY DO BACKBONE CHEMICAL SHIFTS FOR NOW...
    for i in range(len(content)):
      line = content[i].split()
      # STOP AFTER THE BACKBONE BLOCK
      if len(line)==0: break
      # GET THE ATOMS
      if i == 0:
        atoms = line[2:]
        for atom in atoms:
          self.nuclei[atom]=[]
      # GET THE SHIFTS
      elif i > 1:
        if line[0][0]=='*': line[0]=line[0][1:]
        residue = int(line[0])
        # STORE RESIDUE NUMBER
        self.predictions[residue] = {}
        shifts = line[2:]
        # CYCLE THE ATOMS
        for j in range(len(atoms)):
          self.predictions[residue][atoms[j]]=float(shifts[j])
          self.nuclei[atoms[j]].append(float(shifts[j]))
    # CLEAR FILE
    os.remove(self.outfile)


#  ======================================================================
#    P R O F I T _ S C R I P T   C L A S S
#  ======================================================================
class profit_script:
  """
  This class provides an interface to PROFIT
  - Create a class instance passing the command to run PROFIT and the path where to run it.
  - Instance.error contains an error description if something went wrong
  - Instance.clear() clears the current script
  - Instance.write() adds a line to the script
  - Instance.submit() executes the script in PROFIT
  - Instance.output contains the PROFIT output as a list of lines.
  """
  # OPEN SCRIPT FILE FOR OUTPUT
  # ===========================
  # - profit IS THE COMMAND TO RUN PROFIT
  # - runpath IS THE PATH WHERE PROFIT IS RAN
  # - errorfunc IS THE NAME OF THE ERROR HANDLING FUNCTION
  def __init__(self,profit,runpath,errorfunc=None,errorcheck=1):
    self.profit=profit
    self.runpath=runpath
    self.errorfunc=errorfunc
    self.errorflag = 0
    self.errorcheck = errorcheck
    id=0
    while 1:
      self.scriptpath=os.path.join(runpath,'PROFIT_%i_%i.SCR'%(myid,id))
      if os.path.exists(self.scriptpath):
        id+=1
      else:
        break
    self.clear()

  # RAISE AN ERROR
  # ==============
  # CALLS THE ERRORFUNCTION PROVIDED BY THE USER WITH THE GIVEN STRING
  def raiseerror(self,errormsg):
    if (self.errorfunc!=None): apply(self.errorfunc,[errormsg])
    return

  # CLEAR THE SCRIPT
  # ================
  # THE SCRIPT FILE IS REOPENED, instance.error IS CLEARED
  def clear(self):
    self.error=None
    self.output = []
    try: self.script=open(self.scriptpath,"w")
    except: self.raiseerror("PROFIT script %s could not be created"%self.scriptpath)

  # ADD A LINE TO THE SCRIPT
  # ========================
  def write(self,line):
    if (not self.error): self.script.write(line+"\n")

  # SUBMIT SCRIPT
  # =============
  def submit(self):
    if (not self.error):
      self.script.close()
      ret = 0
      try:
        # RUN PROFIT
        output=os.popen("%s < %s"%(self.profit,self.scriptpath))
        # READ THE OUTPUT
        self.output = output.readlines()
        # CHECK FOR ERRORS
        if self.errorcheck:
          for line in self.output:
            if line.find('Error')!=-1:
              self.errorflag = 1
              break
        # REMOVE THE SCRIPT
        os.remove(self.scriptpath)
      except: self.raiseerror("PROFIT could not be run")
      if (ret): self.raiseerror("PROFIT returned error %d"%ret)


#  ======================================================================
#    P R O F I T   F U N C T I O N   G R O U P
#  ======================================================================

# SUPERIMPOSE ENSEMBLE
# ====================
# USE PROFIT TO ITERATIVELY SUPERIMPOSE STRUCTURES
def prft_superimpose(filelist,runpath='/tmp/',overwrite=1):
  # THE LIST OF SUPERIMPOSED STRUCTURES
  fittedlist = []
  # CREATE INPUT FILE
  fpath = os.path.join(runpath,'profit_%i.list'%os.getpid())
  infile = open(fpath,'w')
  for item in filelist: infile.write("%s\n"%item)
  infile.close()
  # INITIALZE PROFIT
  profit = profit_script(nmvconf["PROFIT"],runpath)
  # WRITE THE SCRIPT
  profit.write("multi %s"%fpath)
  profit.write("iterate")
  profit.write("fit")
  profit.write("mwrite")
  # RUN PROFIT
  profit.submit()
  for item in filelist:
    fitfile = "%s%s"%(os.path.splitext(item)[0],'.fit')
    if overwrite:
      # COPY THE FITTED STRUCTURES OVER THE OLD ONES
      shutil.copy(fitfile,item)
      os.remove(fitfile)
      fittedlist.append(item)
    else:
      fittedlist.append(fitfile)
  # CLEAN THE INPUT FILE
  os.remove(fpath)
  return fittedlist

# SUPERIMPOSE TO REF
# ==================
# USE PROFIT TO ITERATIVELY SUPERIMPOSE STRUCTURES
def prft_fitref(reffile,filelist,selection='ca',runpath='/tmp/'):
  # CYCLE THE FILES
  for file in filelist:
    # INITIALZE PROFIT
    profit = profit_script(nmvconf["PROFIT"],runpath)
    # WRITE THE SCRIPT
    profit.write("reference %s"%reffile)
    profit.write("mobile %s"%file)
    if selection=='ca':
      profit.write('atoms CA\n')
    if selection=='bb':
      profit.write('atoms N,C,CA\n')
    if selection=='heavy':
      profit.write('atoms N*,C*,O*,S*\n')
    if selection=='all':
      profit.write('atoms *\n')
    profit.write("fit")
    profit.write("mwrite")
    # RUN PROFIT
    profit.submit()
  # COPY THE FITTED STRUCTURES OVER THE OLD ONES
  for item in filelist:
    fitfile = "%s%s"%(os.path.splitext(item)[0],'.fit')
    if not os.path.exists(fitfile): "Fitfile not present!!!"
    #oldfile = "%s%s"%(os.path.splitext(item)[0],'.old')
    #shutil.copy(item,oldfile)
    shutil.copy(fitfile,item)
    os.remove(fitfile)

# CALCULATE RMSD MATRIX
# =====================
# USE PROFIT TO CALCULATE THE RMSD MATRIX
# SELECTIONS:
#  ca - CA RMSD
#  bb - BACKBONE RMSD
#  heavy - HEAVY ATOM RMSD
#  all - ALL ATOM RMSD
def prft_rmsdmtx(filelist,selection='bb',runpath='/tmp/'):
  # INITIALZE PROFIT
  profit = profit_script(nmvconf["PROFIT"],runpath)
  # WRITE THE SCRIPT AND BUILD THE ARRAY
  rmsdarray=[]
  for file in filelist:
    rmsdarray.append([])
    profit.write("reference %s"%file)
    for rfile in filelist:
      rmsdarray[filelist.index(file)].append([])
      profit.write("mobile %s"%rfile)
      if selection=='ca':
        profit.write('atoms CA\n')
      if selection=='bb':
        profit.write('atoms N,C,CA\n')
      if selection=='heavy':
        profit.write('atoms N*,C*,O*,S*\n')
      if selection=='all':
        profit.write('atoms *\n')
      profit.write("fit")
  # RUN PROFIT
  profit.submit()
  if not profit.errorflag:
    # PARSE THE PROFIT OUTPUT
    i,j = 0,0
    for line in profit.output:
      line = line.split()
      # IF WE FIND AN RMS SCORE
      if 'RMS:' in line:
        # PLACE IT IN THE ARRAY
        rmsdarray[i][j] = float(line[1])
        # ADJUST THE COUNTERS
        i+=1
        if i>len(filelist)-1:
          i=0
          j+=1
    # RETURN THE RMS ARRAY
    return rmsdarray
  else:
    return None

# CALCULATE RMSD
# ==============
# USE PROFIT TO CALCULATE THE PAIRWISE RMSDS
# SELECTIONS:
#  ca - CA RMSD
#  bb - BACKBONE RMSD
#  heavy - HEAVY ATOM RMSD
#  all - ALL ATOM RMSD
def prft_rmsd(filelist,selection='bb',runpath='/tmp/'):
  # BUILD THE RMS ARRAY
  rmsdarray = prft_rmsdmtx(filelist,selection,runpath)
  if rmsdarray:
    rmsdlist=[]
    # BUILD RMSD LIST
    for i in range(len(rmsdarray)):
      tlist = []
      for j in range(len(rmsdarray)):
        if i!=j:
          tlist.append(rmsdarray[i][j])
      rmsdlist.append(avg_list(tlist,sdflag=0))
    return rmsdlist
  else:
    return None

# CALCULATE RMSD PER RESIDUE
# ==========================
# USE PROFIT TO CALCULATE THE PAIRWISE RMSDS
# SELECTIONS:
#  ca - CA RMSD
#  bb - BACKBONE RMSD
#  heavy - HEAVY ATOM RMSD
#  all - ALL ATOM RMSD
def prft_rmsd_perres(filelist,selection='ca',runpath='/tmp/'):
  print "Calculating per residue RMSD deviations for %03i structures."%len(filelist)
  # FIRST WE NEED TO FIT THE ENSEMBLE
  print "Determining optimal superpositioning using ProFit."
  fitlist = prft_superimpose(filelist,runpath=runpath,overwrite=0)
  print "Calculating pairwise RMSD using Yasara."
  # CALCULATE THE PAIRWISE RMSD
  rmsds = yas_ensemblermsd(nmvconf["YASARA_RUN"],fitlist,selection=selection)
  return rmsds


#  ======================================================================
#    L I T E R A T U R E   I M P O R T   C L A S S
#  ======================================================================

class lit_import:
  """
  This class imports literature references. The imported file has to be sent
  through a file parser before submitting it to the class.
  - Instance.read() reads the next MEDLINE entry
  - Instance.add() adds the current entry to the MySQL database
  - Instance.fields then contains the number of fields within this record
  - Instance.field[] contains the field names of the record just read
  - Instance.value[] contains the corresponding field values (a list of same length)
  """
  # OPEN FILE
  # =====================================
  # OPEN THE FILE WITH THE (PARSED!) MEDLINE REFERENCES
  def __init__(self,path):
    self.error=None
    self.eof=0
    # OPEN FILE
    try: self.file=open(path,'r')
    except:
      self.error="Literature file %s not found" % path
      self.eof=1
      self.file=None
      return

  # READ ENTRY
  # ====================
  # READ A MEDLINE ENTRY FROM THE FILE AND CHECK IT
  def read(self):
    # CLEAR FIELD AND VALUE LIST
    self.fields=0
    self.field=[]
    self.value=[]
    # RETURN IF NOTHING CAN BE READ
    if (self.eof): return
    # READ NEW RECORD
    while (not self.eof):
      line=self.file.readline()
      # IF LINE IS EMPTY, EOF HAS BEEN REACHED
      if (len(line)<=1):
        self.eof=1
      # STOP READING WHEN EOF OR RECORD SEPARATOR HAS BEEN REACHED
      if (self.eof or line[0:2]=="//"):
        break
      # INCREASE FIELD COUNTER
      self.fields=self.fields+1
      # SET COLUM OF DASH
      colpos = 4
      if (line[colpos]!='-'):
        self.error="Wrong file format - no dash found in column %d" % (colpos+1)
        self.fields=0
        break
      # ADD FIELD NAME
      self.field.append(string.rstrip(line[:colpos]))
      # ADD VALUE
      self.value.append(string.rstrip(line[colpos+2:]))


  # ADD ENTRY
  # =========
  # ADD THE ENTRY TO THE DATABASE
  # - db_user IS THE MYSQL USER
  # - db_db IS THE MYSQL DATABASE
  # - db_passwd IS THE MYSQL PASSWORD
  # - db_table IS DATABASE FOR STORAGE
  def add(self,db_user,db_db,db_passwd,db_table):
    # QUERY THE DATABASE TABLE
    db = MySQLdb.connect(user=db_user,db=db_db,passwd=db_passwd)
    cursor = db.cursor()
    command = "DESCRIBE "+db_table
    cursor.execute(command)
    # FILL THE LIST OF CURRENT IDENTIFIERS
    id_list = []
    description = cursor.fetchall()
    for id in description:
      id_list.append(id[0])
    # CHECK IF THERE ARE ANY NEW IDENTIFIERS AND ADD THEM TO THE TABLE IF THEY ARE FOUND
    for field in self.field:
      # A FIELD CANNOT BE NAMED "IS" IN MYSQL THAT'S SHITTY!
      if field not in id_list and field!="IS":
         command = "ALTER TABLE "+db_table+" ADD ("+field+" TEXT)"
         cursor.execute(command)
    # ADD THE FIELD VALUES TO THE DATABASE
    fields,values = '',''
    result = '1'
    for i in range(len(self.field)):
      if self.field[i]!="IS":
        fields = fields + self.field[i] + ','
        values = values +'"'+string.replace(self.value[i],'"',"'")+'",'
      # USE THE UNIQUE IDENTIFIER TO CHECK FOR DOUBLE ENTRIES
      if self.field[i]=="UI":
        command = "SELECT UI FROM "+db_table+' WHERE UI="'+self.value[i]+'" '
        cursor.execute(command)
        result = cursor.fetchall()
    if len(result)==0:
      # DEFINE THE MYSQL COMMAND
      command = "INSERT INTO "+db_table+" ("+fields[:-1]+") VALUES ("+values[:-1]+")"
      cursor.execute(command)
    # CLOSE THE MYSQL CONNECTION
    db.commit()


#  ======================================================================
#    L I T E R A T U R E   F U N C T I O N   G R O U P
#  ======================================================================

# PARSE MEDLINE FILE
# =================================================================
# PARSE A MEDLINE FILE, CHANGE MULTILINE ENTRIES IN ONELINE ENTRIES.
def lit_medparse(inputfile,outputfile):
  reference = 0
  # DEFINE DICTIONARY
  fields = {}
  # READ THE INPUT FILE
  try: raw_med = open(inputfile,'r')
  except: error("Medline input %s could not be read" %inputfile)
  entries = raw_med.readlines()
  raw_med.close()
  # OPEN THE OUTPUT FILE
  clean_med = open(outputfile,'w')
  # PARSE THE FILE
  for i in range(len(entries)):
    if len(entries[i])==1:
      if reference:
        keys = fields.keys()
        # WRITE THE KEYS AND VALUES
        for key in keys:
          clean_med.write(key+' '+fields[key]+'\n')
        # WRITE THE DELIMITER
        clean_med.write('//\n')
        # RESET THE DICTIONARY
        fields = {}
        # REFERENCE HAS ENDED
        reference = 0
    else:
      # IN THE PROCESS OF PROCESSING A REFERENCE
      reference = 1
      # DEFINE THE IDENTIFIER AND CONTENT
      tag = entries[i][0:5]
      desc = entries[i][6:-1]
      # SNOOP AHEAD FOR THE NEXT TAG
      if (i < len(entries)-1):
        ntag = entries[i+1][0:5]
      else:
        ntag = ''
      # ADD DESCRIPTIONS THAT SPAN MORE THAN ONE LINE
      if (ntag=='     ' and tag!='     '):
        while entries[i+1][0:5]=='     ':
          desc = desc +' '+ entries[i+1][6:-1]
          i=i+1
      # IF THE KEY ALREADY EXISTS ADD THE CURRENT VALUE
      if fields.has_key(tag):
        fields[tag]=fields[tag]+'|'+desc
      # IF THE KEY DOESN'T EXIST DEFINE IT
      else:
        if tag!='     ':
          fields[tag]=desc
  # CLOSE WITH DELIMITER
  clean_med.write('//\n')
  clean_med.close()


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
      dict = {"RESI":[],"RESN":[],"SEGI":[],"ATOM":[],"NAME":[]}
      self.data = {0:copy.deepcopy(dict),
                   1:copy.deepcopy(dict),
                   2:copy.deepcopy(dict),
                   3:copy.deepcopy(dict),
                   4:copy.deepcopy(dict),
                   5:copy.deepcopy(dict)}
      self.target = 0.0
      self.error  = 0.0
      self.Daxi   = None
      self.Drho   = None

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
    elif self.type=="DIHE":
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
              index2 = self.data[2]["RESI"].index(r2[k])
              index3 = self.data[3]["RESI"].index(r3[l])
              str += '(%s-%s-%s-%s-%s-%s-%s-%s)'%(r0[i],self.data[0]["NAME"][index0],r1[j],self.data[1]["NAME"][index1],r2[k],self.data[2]["NAME"][index2],r3[l],self.data[3]["NAME"][index3])
      str += ']'
      return str
    # DIPOLAR COUPLINGS
    elif self.type=='DIPO':
      str = '['
      r0 = copy.copy(self.data[0]["RESI"])
      r0.sort()
      r4 = copy.copy(self.data[4]["RESI"])
      r4.sort()
      r5 = copy.copy(self.data[5]["RESI"])
      r5.sort()
      for i in range(len(r0)):
        for j in range(len(r4)):
          for k in range(len(r5)):
            index0 = self.data[0]["RESI"].index(r0[i])
            index4 = self.data[4]["RESI"].index(r4[j])
            index5 = self.data[5]["RESI"].index(r5[k])
            str += '(%s-%s-%s-%s-%s-%s)'%(r0[i],self.data[0]["NAME"][index0],r4[j],self.data[4]["NAME"][index4],r5[k],self.data[5]["NAME"][index5])
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
    # DIHEDRAL TYPE
    if self.type=="DIPO":
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
    # DIPO TYPE
    if self.type=="DIPO":
      pass
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
    # DIPO TYPE
    if self.type=="DIPO":
      pass
    return lt

  # FORMAT A RESTRAINT
  # ==================
  # FORMATS A RESTRAINT INTO A FORMAT
  def format(self,format='XPLOR'):
    # DISTANCE TYPE
    ###############
    if self.type == "DIST":
      # HANDLE XPLOR FORMAT
      #####################
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
    # DIPOLAR COUPLING TYPE
    #######################
    if self.type == "DIPO":
      # HANDLE XPLOR FORMAT
      #####################
      if format=="XPLOR":
        # BEGIN FORMATTED RESTRAINT
        fr="ASSI "
        # CYCLE THE FOUR PARTNERS IN THE RESTRAINT
        for i in range(6):
          # WE RESET THE AXIS SYSTEM TO HAVE RESIDUE NUMBER 500!
          if i<4: self.data[i]["RESI"][0]=500
          # PRINT A BLOCK
          fr += "(RESI %5s AND NAME %4s"%(self.data[i]["RESI"][0],self.data[i]["NAME"][0])
          # IF A SEGID PRESENT WE ADD IT
          if len(self.data[i]["SEGI"])>0:
            fr += " AND SEGI %4s)"%self.data[i]["SEGI"][0]
          # IF NO SEGID IS PRESENT, CLOSE THE GROUP
          else:
            fr += ")"
          # ADD THE DISTANCE WITH CORRECT INDENTATION
          if i==5:
            fr+=" %8.3f %8.3f"%(self.value,self.error)
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
  Current types are DIST=DISTance data, DIHE=DIHEdral data, DIPO=DIPOlar couplings.
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
  # - Daxi and Drho desribe the alignment tensor for DIPO data
  def __init__(self,path,access,type='DIST',format='XPLOR',
               Daxi=None,Drho=None,errorfunc=error):
    self.errorfunc = errorfunc
    self.eof = 0
    self.type = type
    self.format = format
    self.comments = ['#','!']
    self.restraintlist = []
    self.Daxi = Daxi
    self.Drho = Drho
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
    # HANDLE THE DIHEDRAL ANGLE RESTRAINTS
    if self.type == 'DIPO':
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
            restr = nmr_restraint('DIPO')
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
                  # IF A GROUP IS FINISHED GO TO THE NEXT
                  if brkcount == 0:
                    group += 1
                pos+=1
            # PARSE THE DISTANCES
            dipolist = string.split(r[string.rfind(r,')')+1:])
            restr.value = float(dipolist[0])
            restr.error = float(dipolist[1])
            restr.Daxi  = self.Daxi
            restr.Drho  = self.Drho
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
    if self.type == 'DIST':
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
    # HANDLE DIPOLAR TYPE RESTRAINTS
    if self.type == 'DIPO':
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
#                      P D B _ F I N D E R   C L A S S
#  ======================================================================

class pdb_finder:
  """
  This class provides an interface to the PDBFINDER/CHECKDB data bases.
  Create a class instance giving a path+filename,"r"/"w"/"a", a type and an error
  handling function in parentheses.
  Current types are 0=PDBFINDER, 1=PDBFINDER2, 2=CHECKDB.
  - Instance.error contains an error description if something went wrong
  - Instance.file contains the PDBFINDER file object
  - Instance.read() reads the next record.
  - Instance.fields then contains the number of fields within this record
  - Instance.field[] contains the field names of the record just read
    (a list, the leading spaces are preserved, the trailing spaces are truncated)
  - Instance.value[] contains the corresponding field values (a list of same length)
  - Instance.id contains the four letter PDB ID
  - Instance.chain[] contains a list of chain names found
  - Instance.sequence contains a list of sequence strings, one for every chain.
  - Instance.secstr contains a list of secondary structure strings, one for every chain.
  - Instance.chainseq{} contains the sequence of every chain in Instance.chain
  - Instance.backboneok{} is a dictionary containing lists of tuples (Chain,OKflag)
  - Instance.recordpos{} is a dictionary used by Instance.seek() to find a certain record
  - Instance.resolution{} is a dictionary containing the resolution of the structures (4.0A if not specified)
  - Instance.rfactor{} is a dictionary containing the rfactor of the structures (0.3 if not specified)
  - Instance.amacs{} is a dictionary containing the number of amino acids per structure.
  - Instance.newfield is a list of fieldnames that are new in PDBFINDER II.

  """

  # OPEN PDBFINDER
  # ==============
  # - path IS THE PDBFINDER LOCATION.
  # - access IS EITHER "r" OR "w".
  # - type IS 0 FOR PDBFINDER, 1 FOR PDBFINDER II AND 2 FOR CHECKDB FILES.
  # - errorfunc IS THE NAME OF AN ERROR HANDLING FUNCTION.
  def __init__(self,path=None,access=None,type=None,errorfunc=None):
    self.error=None
    self.errorfunc=errorfunc
    self.eof=0
    self.type=type
    self.recordpos={}
    self.resolution={}
    self.rfactor={}
    self.amacs={}
    self.backboneok={}
    self.newfield=[" DSSP",        " Nalign",      " Nindel",     " Entropy",
                   " Cons-Weight", " Cryst-Cont",  " Access",      " Quality",
                   "  Present",    "  B-Factors",  "  Bonds",      "  Angles",
                   "  Torsions",   "  Phi/psi",    "  Planarity",  "  Chirality",
                   "  Backbone",   "  Peptide-Pl", "  Rotamer",    "  Chi-1/chi-2",
                   "  Bumps",      "  Packing 1",  "  Packing 2",  "  In/out",
                   "  H-Bonds",    "  Flips"]
    # WHATIF CHECKS THAT ARE ADDED TO PDBFINDER II
    self.checklist=["",             "",             "",             "",
                    "",             "SCOLST",       "ACCLST",       "",
                    "MISCHK",       "BVALST",       "BNDCHK",       "ANGCHK",
                    "CHICHK",       "RAMCHK",       "PLNCHK",       "HNDCHK",
                    "BBCCHK",       "FLPCHK",       "ROTCHK",       "C12CHK",
                    "BMPCHK",       "QUACHK",       "NQACHK",       "INOCHK",
                    "BH2CHK",       "HNQCHK"]
    # EMPTY OBJECT?
    if (path==None): return
    # NORMALIZE PATH, IMPORTANT TO CONVERT UNIX FORWARD TO WINDOWS BACKWARD SLASHES
    path=os.path.normpath(os.path.normcase(path))
    self.path=path
    #self.indexfilename=dsc_rmext(path)+".ind"
    self.indexfilename = '/tmp/PDBFIND2.ind'
    # OPEN FILE
    try: self.file=open(path,access)
    except:
      self.eof=1
      self.file=None
      self.raiseerror("__init__: PDBFINDER file %s not found" % path)
      return
    # IF FILE IS READ, SKIP INITIAL COMMENTS
    if (access[0]=="r"):
      while (1):
        # CURRENT POSITION IN FILE IS STORED BEFORE SNOOPING AHEAD
        pos=self.file.tell()
        line=self.file.readline()
        if (line[0:2]!='//'): break
      # BACK TO LAST VALID POSITION
      self.file.seek(pos)
    # IF FILE IS WRITTEN FOR THE FIRST TIME, ADD INITIAL COMMENTS
    elif ((access[0]=="w" or access[0]=="a") and self.file.tell()==0):
      if (type<2):
        if (type==1):
          self.file.write("// ##\\ ##\\ ##\\  ### O #\\  # ##\\ ### ##\\  ### ###\n")
          self.file.write("// # # # # # #  #   # #\\\\ # # # #   # #   #   #\n")
          self.file.write("// ##/ # # ##<  ##  # # \\\\# # # ##  ##<   #   #\n")
          self.file.write("// #   # # # #  #   # #  \\# # # #   # #   #   #\n")
          self.file.write("// #   ##/ ##/  #   # #   # ##/ ### # #  ### ###\n//\n")
          self.file.write("// On my watch it's %s.\n//\n" % time.ctime(time.time()))
          self.file.write("// When using this database, please cite:\n")
          self.file.write("// PDBFinderII - a database for protein structure analysis and prediction\n")
          self.file.write("// Krieger,E., Hooft,R.W.W., Nabuurs,S., Vriend.G. (2004) Submitted\n//\n")
          self.file.write("// Fields also present in the original PDBFinder are explained at www.cmbi.kun.nl/gv/pdbfinder/overview.html\n//\n")
          # ===============================================================================================
          self.file.write("// The following extensions have been added in PDBFinderII:\n")
          self.file.write("// Chain breaks '-' in the Sequence fields allow an easy alignment with Swissprot or SEQRES sequences.\n")
          self.file.write("// DSSP:         The secondary structure assigned by DSSP, 'C' indicates coil (instead of spaces).\n")
          self.file.write("// Nalign:       Number of alignments in the HSSP file on a logarithmic scale: calculate 10^((N-1)*0.25) to get an estimate (N is in [0..9]). The number on the right side is the average number of HSSP alignments per residue.\n")
          self.file.write("// Nindel:       Sum of insertions and deletions, on the same logarithmic scale as Nalign. Again the number on the right is the non-logarithmic average over all residues.\n")
          self.file.write("// Entropy:      The HSSP entropy (page 60 in the original paper), multiplied with 9/ln(20).\n")
          self.file.write("// Cons-Weight:  The HSSP conservation weights (page 59 in the original paper), multiplied with 9.\n")
          self.file.write("// Cryst-Cont:   '+' marks residues involved in crystal contacts.\n")
          self.file.write("// Access:       Relative side chain accessibility, 0=buried, 9=exposed.\n")
          self.file.write("// Quality:      The number given here is the average over the fields 'Phi/psi','Backbone' and 'Packing-1' below. High resolution X-ray structures reach values around 0.75, NMR structures calculated from only a few restraints can be found around 0.3.\n")
          self.file.write("//               Several quality estimators from the PDBREPORTs follow, most of the time, 0=requires attention, 9=perfect.\n")
          self.file.write("//   Present:    9 minus the number of missing atoms per residue.\n")
          self.file.write("//   B-Factors:  Crystallographic B-factors, the range [10..60] is mapped to [9..0].\n")
          self.file.write("//   Bonds:      Absolute Z-score of the largest bond deviation per residue (using Engh&Huber parameters), absolute Z-Scores in the range [5..2] are mapped to [0..9].\n")
          self.file.write("//   Angles:     Absolute Z-score of the largest angle deviation per residue (using Engh&Huber parameters), absolute Z-Scores in the range [5..2] are mapped to [0..9].\n")
          self.file.write("//   Torsions:   Average Z-score of the torsion angles per residue, Z-Scores in the range [-3..+3] are mapped to [0..9].\n")
          self.file.write("//   Phi/Psi:    Ramachandran Z-score per residue, Z-Scores in the range [-4..+4] are mapped to [0..9]. The number on the right side is not a plain average, but again remapped using the WHAT IF database distribution of averages. Multiply with 8 and subtract 4 to get the Z-score in the PDBReport. N- and C-terminal residues are undefined ('?').\n")
          self.file.write("//   Planarity:  Z-score for the planarity of the residue sidechain, Z-Scores in the range [6..2] are mapped to [0..9]. Residues without planar side-chains score '9'.\n")
          self.file.write("//   Chirality:  Average absolute Z-score of the chirality deviations per residue, average absolute Z-Scores in the range [4..2] are mapped to [0..9]. Glycine always scores '9'.\n")
          self.file.write("//   Backbone:   Number of similar backbone conformations found in the database, numbers in the range [0..10] are mapped to [0..9]. No scores can be obtained for the N- and C-terminal two residues, as stretches of five are used.\n")
          self.file.write("//   Peptide-Pl: RMS distance of the backbone oxygen from the oxygen in similar backbone conformations found in the database, distances in the range [3..1] are mapped to [0..9]. If less than 10 hits are found, there are not sufficient data to perform the following two checks.\n")
          self.file.write("//   Rotamer:    Probability that the sidechain rotamer (chi-1 only) is correct, probabilities in the range [0.1 .. 0.9] are mapped to [0..9]. Gly, Ala and Pro always score '9'.\n")
          self.file.write("//   Chi-1/chi-2:Z-score for the sidechain chi-1/chi-2 combination, Z-scores in the range probabilities in the range [-4..+4] are mapped to [0..9]. Residues with only <=1 side-chain torsion angle score '9'. The number on the right side is not a plain average, but again remapped using the WHAT IF database distribution of averages. Multiply with 8 and subtract 4 to get the Z-score in the PDBReport.\n")
          self.file.write("//   Bumps:      Sum of bumps per residue, distances in the range [0.1 .. 0] are mapped to [0..9].\n")
          self.file.write("//   Packing-1:  First packing quality Z-score, Z-scores in the range [-5..+5] are mapped to [0..9]. The number on the right side is not a plain average, but again remapped using the WHAT IF database distribution of averages. Multiply with 10 and subtract 5 to get the Z-score in the PDBReport.\n")
          self.file.write("//   Packing-2:  Second packing quality Z-score, Z-scores in the range [-3..+3] are mapped to [0..9]. The number on the right side is not a plain average, but again remapped using the WHAT IF database distribution of averages. Multiply with 6 and subtract 3 to get the Z-score in the PDBReport.\n")
          self.file.write("//   In/Out:     Absolute inside/outside distribution Z-score per residue, Z-scores in the range [4..2] are mapped to [0..9].\n")
          self.file.write("//   H-Bonds:    9 minus number of unsatisfied hydrogen bonds, an additional 1 is subtracted for a buried backbone nitrogen, 4 for buried sidechain.\n")
          self.file.write("//   Flips:      Indicates flipped Asn/Gln/His sidechain, 9=OK, 0=needs flipping.\n")
          self.file.write("// If not indicated otherwise, numbers on the right side are the average, multiplied with 1/9. This average is calculated before the values of the individual residues are clamped to [0..9].\n")
          self.file.write("//\n")
        else:
          self.file.write("//\n")
          self.file.write("// This file is PDBFIND.TXT\n")
          self.file.write("//\n")
          self.file.write("// On my watch it's %s.\n//\n" % time.ctime(time.time()))
          self.file.write("//\n")
          self.file.write("// (C) 1996 Rob W.W. Hooft, Chris Sander, Michael Scharf and Gert Vriend\n")
          self.file.write("//          Updated to V3.0 in May 2000 by Elmar Krieger\n")
        self.file.write("//\n")
        self.file.write("// This file is freely redistributable, but only in unmodified form.\n")
        self.file.write("// This copyright notice must be preserved on each copy. The latest\n")
        self.file.write("// version of this database should always be available by FTP from\n")
        self.file.write("// ftp.cmbi.kun.nl. It is distributed as part of the WHAT IF program.\n")
        self.file.write("// Proper acknowledgement is required.\n")

  # GET AVERAGE QUALITY
  # ===================
  # IN PDBFINDER II ENTRIES, QUALITY INDICATORS FOR MULTIPLE CHAINS CAN BE CONCATENATED
  # LIKE THAT:  5599999998999999999999|  0.94469999|  0.9912
  # (TWO CHAINS, ONE WITH 22 RESIDUES AND QUALITY 0.9446 AND ONE WITH 4 RESIDUES AND
  # QUALITY 0.9912)
  def averagequal(self,checkname):
    checkstr=self.fieldvalue(checkname)
    qualsum=0
    residues=0
    while (1):
      pos=string.find(checkstr,'|')
      chainlen=pos
      if (pos==-1): break
      quality=float(checkstr[pos+1:pos+9])
      #print "Qual for",chainlen,"is",quality
      if (quality!=0):
        qualsum=qualsum+quality*chainlen
        residues=residues+chainlen
      checkstr=checkstr[pos+9:]
    if (residues): return(qualsum/residues)
    else: return(None)

  # GET CLOSEST CHAIN
  # =================
  # THE CHAIN IDENTIFIER CLOSEST TO THE GIVEN ONE IS RETURNED
  def closestchain(self,chain):
    if (self.chainseq.has_key(chain)): return(chain)
    if (self.chainseq.has_key('_')): return('_')
    chainlist=self.chainseq.keys()
    chainlist.sort()
    return(chainlist[0])

  # RETURN CHAIN SEQUENCE
  # =====================
  # THE SEQUENCE OF THE GIVEN CHAIN IS RETURNED, chain CAN BE '~' FOR ALL CHAINS.
  def chainseq(self,chain):
    sequence=""
    for i in range(self.chains):
      if (self.chain[i]==chain or chain=='~'): sequence=sequence+self.sequence[i]
    return(sequence)

  # RETURN CHAIN SECONDARY STRUCTURE
  # ================================
  # THE SECONDARY STRUCTURE OF THE GIVEN CHAIN IS RETURNED, chain CAN BE '~' FOR ALL CHAINS.
  def chainsecstr(self,chain):
    secstr=""
    for i in range(self.chains):
      if (self.chain[i]==chain or chain=='~'): secstr=secstr+self.secstr[i]
    return(secstr)

  # GET CHAIN SEQUENCE WITHOUT GAPS
  # ===============================
  # THE SEQUENCE OF THE SPECIFIED CHAIN IS RETURNED WITH GAPS '-' REMOVED.
  def gaplesschainseq(self,chain):
    return(string.replace(self.chainseq(chain),'-',''))

  # GET SECONDARY STRUCTURE WITHOUT GAPS
  # ====================================
  # THE SECONDARY STRUCTURE OF THE SPECIFIED CHAIN IS RETURNED WITH GAPS '-' REMOVED.
  def gaplesschainsecstr(self,chain):
    return(string.replace(self.chainsecstr(chain),'-',''))

  # INSERT GAPS
  # ===========
  # GAP SYMBOLS '-' ARE INSERTED IN THE sequence STRING AT THE POSITIONS DEFINED
  # IN CHAIN chain.
  def gapsinserted(self,sequence,chain):
    chainseq=self.chainseq(chain)
    for i in range(len(chainseq)):
      if (chainseq[i]=='-' and i<len(sequence)):
        sequence=sequence[:i]+'-'+sequence[i:]
    return(sequence)

  # FIND MATCHING CHAIN
  # ===================
  # THE DSSP FILE IS SEARCHED FOR THE REQUIRED CHAIN. IF NOT FOUND, CHAIN 'A'
  # BECOMES '_', '_' BECOMES 'A' ETC.
  def matchchain(self,chain):
    if (chain=='~'): return(chain)
    if (chain in self.chain): return(chain)
    if (chain=='A' and '_' in self.chain): return('_')
    if (chain=='_' and 'A' in self.chain): return('A')
    self.raiseerror("matchchain: Chain %s not found in current PDBFINDER entry" % chain)
    return(None)

  # RAISE AN ERROR
  # ==============
  # CALLS THE ERRORFUNCTION PROVIDED BY THE USER WITH THE GIVEN STRING
  def raiseerror(self,errormsg):
    errormsg=self.__class__.__name__+'.'+errormsg
    self.error=errormsg
    if (self.errorfunc!=None): apply(self.errorfunc,[errormsg])
    else:
      print errormsg
      raise SystemExit

  """
  # ADD THE ATTRIBUTES FOR EASY USE
  # ===============================
  def addattr(self):
    # SET LIST ATTRIBUTES
    listattr=["Author","Chain"," HetId"]
    for attr in listattr:
      if (attr[0]!=' '): setattr(self,attr,[])
    # ADD ATTRIBUTES
    for i in range(self.fields):
      attr=string.replace(self.field[i],'-','')
      attr=string.replace(attr,'/','')
  """

  # READ A PDBFINDER RECORD
  # =======================
  # THE NEXT RECORD IS READ, Instance.eof IS SET WHEN END OF FILE IS REACHED.
  def read(self,id=None):
    self.error=None
    if (id):
      # ID IS GIVEN
      self.seek(id)
    # CLEAR FIELD AND VALUE LISTS
    self.fields=0
    self.field=[]
    self.value=[]
    self.chains=self.peptidechains=self.nucleotidechains=0
    self.diffchains=self.diffpeptidechains=self.diffnucleotidechains=0
    self.chain=[]
    self.sequence=[]
    self.secstr=[]
    bblist=[]
    # RETURN IF NOTHING CAN BE READ
    if (self.eof): return(0)
    # REMEMBER START OF RECORD
    startpos=self.file.tell()
    # READ NEW RECORD
    while (not self.eof):
      line=self.file.readline()
      # IF LINE IS EMPTY, EOF HAS BEEN REACHED
      if (line==""):
        self.eof=1
        # IF EOF FOUND, BUT field IS NOT EMPTY, THE LAST RECORD WAS CORRUPTED
        #   (MOST LIKELY BECAUSE THE USER RAISED A KeyboardInterrupt DURING
        #   WRITING THIS RECORD) - SO IT'S SIMPLY DELETED
        if (self.field!=[]):
          # DELETE RECORD
          self.fields=0
          self.field=[]
          self.value=[]
          # GO BACK TO START OF RECORD
          self.file.seek(startpos)
      # STOP READING WHEN END OF FILE (EOF) OR RECORD SEPARATOR // HAS BEEN REACHED
      if (self.eof or line[0:2]=="//"): break
      # INCREASE FIELD COUNTER
      self.fields=self.fields+1
      # SET COLUMN OF COLON
      if (self.type<2): colpos=13
      else: colpos=10
      if (string.strip(line)=="" or colpos>=len(line)):
        self.raiseerror("read: Wrong file format - line too short or missing // terminator")
        break
      if (line[colpos]!=':'):
        print line
        self.raiseerror("read: Wrong file format - no colon found in column %d" % (colpos+1))
        break
      # ADD FIELD NAME
      self.field.append(string.rstrip(line[:colpos]))
      # ADD VALUE
      self.value.append(string.rstrip(line[colpos+2:]))
    # IF NO FIELDS COULD BE READ, WE HAVE REACHED THE END
    if (not self.fields):
      self.eof=1
    else:
      # SEARCH FOR ID,RESOLUTION,CHAINS AND CHECK FOR BACKBONE COMPLETENESS
      self.id=None
      resolution=4.0
      rfactor=0.3
      amacs=0
      for i in range(self.fields):
        if (self.field[i]=="ID"): self.id=self.value[i]
        elif (self.field[i]==" Resolution"): resolution=float(self.value[i])
        elif (self.field[i]==" R-Factor"): rfactor=float(self.value[i])
        elif (self.field[i]=="T-Nres-Prot"): amacs=int(self.value[i])
        elif (self.field[i]=="Chain"):
          self.chain.append(self.value[i])
          self.sequence.append("")
          self.secstr.append("")
          bblist.append((self.value[i],1))
          self.chains=self.chains+1
        elif (self.field[i]==" Amino-Acids"):
          self.peptidechains=self.peptidechains+1
          chaintype="PEPTIDE"
        elif (self.field[i]==" Nucl-Acids"):
          self.nucleotidechains=self.nucleotidechains+1
          chaintype="DNA"
        elif (self.field[i]=="  Break" or self.field[i]=="  Miss-BB" or
              self.field[i]==" only-Ca"):
          bblist=bblist[:-1]
          bblist.append((self.chain[-1],0))
        elif (self.field[i]==" Sequence"):
          # UPDATE NUMBER OF DIFFERENT CHAINS
          if (self.value[i] not in self.sequence):
            self.diffchains=self.diffchains+1
            if (chaintype=="PEPTIDE"): self.diffpeptidechains=self.diffpeptidechains+1
            elif (chaintype=="DNA"): self.diffnucleotidechains=self.diffnucleotidechains+1
          self.sequence[-1]=self.value[i]
        elif (self.field[i]==" DSSP"):
          # ADD POSSIBLY MISSING TERMINAL SPACES
          self.value[i]=self.value[i]+' '*(len(self.sequence[-1])-len(self.value[i]))
          self.secstr[-1]=self.value[i]
      if (self.id!=None):
        # ADD VALUES TO FAST ACCESS DICTIONARY
        self.recordpos[self.id]=startpos
        self.resolution[self.id]=resolution
        self.rfactor[self.id]=rfactor
        self.amacs[self.id]=amacs
        self.backboneok[self.id]=bblist
      """
      # DO WE HAVE AS ANY SEQUENCES AS CHAINS?
      for chain in self.chain:
        if (not self.chainseq.has_key(chain)): self.chainseq[chain]=""
      """
    return(not self.eof)

  # WRITE A PDBFINDER RECORD
  # ========================
  # THE CURRENT RECORD IS WRITTEN TO DISC.
  def write(self):
    for i in range(self.fields):
      line=self.field[i]
      while (len(line)<13): line=line+" "
      line=line+": "+self.value[i]+"\n"
      self.file.write(line)
    self.file.write("//\n")

  # SEEK RECORD
  # ===========
  # THE RECORD CORRESPONDING TO PDB id IS READ, ASSUMING THAT
  # Instance.buildindex() WAS CALLED SOMETIME BEFORE.
  def seek(self,id):
    id=string.upper(id[:4])
    if (not self.recordpos.has_key(id)):
      self.raiseerror("seek: PDBFINDER does not contain a record called '%s'. Update database." % id)
    else:
      self.file.seek(self.recordpos[id])
      self.eof=0
      self.error=None

  # GET SEQUENTIAL RESIDUE NUMBERS
  # ==============================
  # THE CURRENT CHECKDB FILE IS READ TILL THE PDBLST FIELD, RESIDUES MATCHING
  #   chain ARE EXTRACTED, THEN THE LIST OF RESIDUE NAMES PASSED AS reslist IS
  #   CONVERTED INTO A LIST OF SEQUENTIAL RESIDUE NUMBERS WHICH IS RETURNED.
  def sequentialnumbers(self,chain,reslist):
    if (self.type!=2):
      self.raiseerror("sequentialnumbers: This method can only be called with CHECKDB files")
    if (chain==' '): chain='_'
    while (1):
      if (self.eof): self.raiseerror(".sequentialnumbers: No PDBLST found in CHECKDB file")
      if (self.fieldvalue("CheckID")=="PDBLST"):
        pdblist=[]
        resnolist=[]
        # READ ALL RESIDUE NAMES
        for i in range(self.fields):
          if (self.field[i]=="   Name"):
            resname=self.resname(i)
            if (resname[0]==chain): pdblist.append(resname)
        # FIND THE SEQUENTIAL RESIDUE NUMBERS
        for resname in reslist:
          if (resname not in pdblist):
            self.raiseerror("sequentialnumbers: Residue %s not found in PDBLST" % resname)
          resnolist.append(pdblist.index(resname))
        return(resnolist)
      self.read()

  # BUILD INDEX
  # ===========
  # READS THE COMPLETE DATA BASE AND MAKES IT ACCESSIBLE WITH Instance.seek()
  def buildindex(self):
    if (not self.error):
      if (os.path.exists(self.indexfilename) and
          dsc_modtime(self.indexfilename)>dsc_modtime(self.path)):
        # LOAD INDEX FILE
        print "Found index file: %s"%self.indexfilename
        indexfile=open(self.indexfilename,"r")
        self.recordpos=cPickle.load(indexfile)
        self.resolution=cPickle.load(indexfile)
        self.rfactor=cPickle.load(indexfile)
        self.amacs=cPickle.load(indexfile)
        self.backboneok=cPickle.load(indexfile)
        indexfile.close()
      else:
        # THIS BUILDS THE COMPLETE DICTIONARY OF RECORD POSITIONS FOR RANDOM ACCESS
        while (not self.eof): self.read()
        # WRITE INDEX TO DISC
        try:
          print "Writing PDBFINDER index for fast access next time"
          indexfile=open(self.indexfilename,"w")
          cPickle.dump(self.recordpos,indexfile)
          cPickle.dump(self.resolution,indexfile)
          cPickle.dump(self.rfactor,indexfile)
          cPickle.dump(self.amacs,indexfile)
          cPickle.dump(self.backboneok,indexfile)
        except: print "PDBFINDER index could not be written."

  # CLOSE FILE
  # ==========
  # THE PDBFINDER FILE IS CLOSED, NO FURTHER ACCESS IS POSSIBLE.
  def close(self):
    if (self.file): self.file.close()

  # COPY RECORD
  # ===========
  # THE CURRENT RECORD IS REPLACED WITH A COPY FROM ANOTHER pdb_finder INSTANCE.
  def copy(self,source):
    self.id=source.id
    self.error=source.error
    self.fields=source.fields
    self.field=source.field
    self.value=source.value
    self.chain=source.chain

  # SEARCH FOR FIELD
  # ================
  # THE SPECIFIED FIELD IS SEARCHED, ITS VALUE RETURNED.
  def fieldvalue(self,name):
    for i in range(self.fields):
      if (self.field[i]==name): return(self.value[i])
    return(None)

  # SEARCH FOR NEXT FIELD WITH GIVEN NAME
  # =====================================
  # THE INDEX IS RETURNED, THE SEARCH IS STOPPED IF A FIELD WITH LOWER INDENTATION IS FOUND
  def nextfield(self,index,name):
    if (index==None): return(None)
    # GET CURRENT INDENTATION LEVEL
    indlevel=string.count(self.field[index]," ")
    # SEARCH
    while (1):
      index=index+1
      if (index>=self.fields or string.count(self.field[index]," ")<indlevel): return(None)
      if (self.field[index]==name): return(index)

  # INSERT A FIELD
  # ==============
  # THE SPECIFIED field WITH value IS INSERTED AT <pos>.
  def insert(self,pos,field,value):
    self.field.insert(pos,field)
    self.value.insert(pos,value)
    self.fields=self.fields+1

  # DELETE ALL FIELDS
  # =================
  # ALL FIELDS WITH <name> ARE DELETED.
  def delfields(self,name):
    i=0
    while (i<self.fields):
      if (self.field[i]==name):
        self.field.pop(i)
        self.value.pop(i)
        self.fields=self.fields-1
      else:
        i=i+1

  # DELETE A FIELD
  # ==============
  # THE FIELD WITH <number> IS DELETED.
  def delete(self,number):
    if (number<self.fields):
      self.field.pop(number)
      self.value.pop(number)
      self.fields=self.fields-1

  # GET RESIDUE NAME
  # ================
  # THE RESIDUE NAME IN <field> IS RETURNED IN STANDARD FORMAT: C-NUMB-RES-ATOM
  # KNOWN CHECKDB FORMATS SO FAR:
  # - Name: A-   1-OCY- OP1
  # - Name:   21-CYS
  # - Name: HOH -HOH
  # - Name:   22-PRO - CA
  # - Name:   22-PRO-CA
  # - Name: A-  22-PRO-CA
  def resname(self,field):
    res=self.value[field]
    if (res[1]=='-' and res[6]=='-'):
      if (len(res)>10): res=res[0:10]
      return(res)
    if (res[4]=='-'):
      res="_-"+res
      if (len(res)>10):
        if (res[10]==' '): res=res[:10]+res[11:]
        if (res[10]=='-'): res=res[:10]
      return(res)
    return(None)

  # PRINT PDBFINDER RECORD
  # ======================
  def __repr__(pdbfinder):
    # WHEN USING THIS MODULE, YOU WOULD DO SOMETHING LIKE
    # import pdbfinder_file
    # pdbfinder = pdbfinder_file.interface("MyPDBFinderFilename")
    # IN THE BEGINNING. THEN FOLLOW THE EXAMPLES BELOW:
    print "PDBFinder Record:"
    for i in range(pdbfinder.fields):
      line=pdbfinder.field[i]
      while (len(line)<13): line=line+" "
      line=line+": "+pdbfinder.value[i]
      print line
    return("")


#  ======================================================================
#    P D B   F U N C T I O N   G R O U P
#  ======================================================================

#  PDB INSTITUTE
#  =============
#  SELECT THE INSTITUTE AT WHICH THE GIVEN PDB ENTRY IS PROCESSED
#  WE SELECT  EITHER EBI (SINCE 15 JUL 1999) OR RCSB. WE LOOK IN REMARK 100
def pdb_institute(pdb_id):
  # CONSTRUCT THE PDB FILE PATH
  filepath = string.replace(nmvconf["PDB"],"????",string.lower(pdb_id))
  # GREP THE LINE OF INTEREST
  os.system("fgrep -i 'has been processed by' %s > /tmp/pdbgrep"%filepath)
  # READ THE GREP FILE
  file = open ('/tmp/pdbgrep','r')
  content = file.readlines()
  file.close()
  # EXTRACT THE INSTITUTE
  try:
    institute = string.split(content[0])[8]
    if (institute != "EBI" and institute != "RCSB"):
      institute = 'other'
  except IndexError:
    institute = 'unknown'
  return institute

# PDB SELECTOR (RETURNS DICTIONARY)
# ===================
# SELECT PDB X-RAY STRUCTURES BETWEEN GIVEN RESOLUTIONS AND PUBLISHED IN GIVEN YEARS
#  - res_hi IS THE HI-RESOLUTION CUT-OFF
#  - res_lo IS THE LOW RESOLUTION CUT-OFF
#  - year_lo IS THE OLDEST YEAR IN THE RANGE
#  - year_hi IS THE MOST RECENT YEAR IN THE RANGE
# FUNCTION RETURNS A DICTIONARY WITH PDBNAME AS KEY AND RESOLUTION AND YEAR VALUE
def pdb_selectx(res_hi,res_lo,year_lo,year_hi):
  # OPEN AND READ THE PDBFINDER
  pdbfinder = pdb_finder(nmvconf["PDBFINDER"],"r",0,error)
  pdbfinder.read()
  if (pdbfinder.error): error("PDBFINDER not found, no structure selection possible")
  # DEFINE THE DICTIONARY
  dict = {}
  # READ THE STRUCTURE INFORMATION
  while not pdbfinder.eof:
    method = pdbfinder.fieldvalue('Exp-Method')
    year = int(pdbfinder.fieldvalue(' Date')[0:4])
    reso = pdbfinder.fieldvalue(' Resolution')
    pdb = pdbfinder.fieldvalue('ID')
    no_res = pdbfinder.fieldvalue('T-Nres-Prot')
    # DO THE STRUCTURE SELECTION
    # SELECT FOR PROTEINS (NO_RES MUST EXIST) AND X-RAY STRUCTURES
    if method=='X' and no_res:
      # CONVERT RESOLUTION TO FLOAT
      try:
        reso = float(reso)
      except TypeError:
        print 'PDB file %s has no resolution set.'%pdb
      # SELECT FOR RESOLUTION AND YEAR OF PUBLICATION
      if (reso <= res_lo and reso >= res_hi) and (year <= year_hi and year >= year_lo):
        # CREATE DICT
        dict[pdb]=[reso,year]
    # READ THE NEXT ENTRY
    pdbfinder.read()
  # RETURN THE BINS
  return dict

# PDB SELECTOR (RETURNS DICTIONARY)
# ===================
# SELECT PDB NMR STRUCTURES PUBLISHED BETWEEN GIVEN YEARS
#  - year_lo IS THE OLDEST YEAR IN THE RANGE
#  - year_hi IS THE MOST RECENT YEAR IN THE RANGE
# FUNCTION RETURNS A DICTIONARY WITH PDBNAME AS KEY AND YEAR AS VALUE
def pdb_selectnmr(year_lo,year_hi):
  # OPEN AND READ THE PDBFINDER
  pdbfinder = pdb_finder(nmvconf["PDBFINDER"],"r",0,error)
  pdbfinder.read()
  if (pdbfinder.error): error("PDBFINDER not found, no structure selection possible")
  # DEFINE THE DICTIONARY
  dict = {}
  # READ THE STRUCTURE INFORMATION
  while not pdbfinder.eof:
    method = pdbfinder.fieldvalue('Exp-Method')
    year = int(pdbfinder.fieldvalue('Date')[0:4])
    pdb = string.lower(pdbfinder.fieldvalue('ID'))
    no_res = pdbfinder.fieldvalue('T-Nres-Prot')
    no_struct = pdbfinder.fieldvalue('N-Models')
    # DO THE STRUCTURE SELECTION
    # SELECT FOR PROTEINS (NO_RES MUST EXIST) AND X-RAY STRUCTURES
    if method=='NMR' and no_res:
      # SELECT FOR RESOLUTION AND YEAR OF PUBLICATION
      if (year <= year_hi and year >= year_lo):
        # CREATE DICT
        dict[pdb]=[year,no_struct,no_res]
    # READ THE NEXT ENTRY
    pdbfinder.read()
  # RETURN THE BINS
  return dict


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


#  ======================================================================
#    Q U E E N B A S E   C L A S S
#  ======================================================================
class queenbase:
  """
  A base class for a QUEEN project.
  Create a class instance by giving a path and a projectname.
  """
  def __init__(self,path,project):
    self.path = path
    self.project = project
    self.projectpath = os.path.join(path,project)
    self.logpath = self.path
    self.display_error = 1
    self.display_warning = 1
    self.display_debug = 1
    self.errorflag = 0

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
    # REMOVE DISTANCE MATRIX FROM DISK
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

  def uncertainty(self,xplr,restraints,clear=1):
    # CALCULATE MATRIX
    self.calcmtx(xplr,restraints)
    # CALCULATE UNCERTAINTY
    unc = self.calcunc()
    # CLEAR MEMORY
    if clear: self.clear()
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


#  ======================================================================
#    Q U E E N   F U N C T I O N   G R O U P
#  ======================================================================


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

# SETUP QUEEN
# ===========
# SETUP QUEEN
def qn_setup(nmvconf,project,myid=0,numproc=1,projectpath=None):
  # SETUP QUEEN
  if not projectpath:
    path = os.path.join(nmvconf["Q_PROJECT"],project)
  else:
    path = os.path.join(projectpath,project)
  if not os.path.exists(path):
    error("Project directory does not exist. Please setup project first")
  queen = queenbase(path,project)
  queen.sequence     = os.path.join(queen.path,nmvconf["Q_SEQ"])
  queen.table        = os.path.join(queen.path,nmvconf["Q_DATATBL"])
  queen.dataset      = os.path.join(queen.path,nmvconf["Q_DATASET"])
  queen.logpath      = os.path.join(queen.path,nmvconf["Q_LOG"])
  queen.pdb          = os.path.join(queen.path,nmvconf["Q_PDB"])
  queen.outputpath   = os.path.join(queen.path,nmvconf["Q_OUTPUT"])
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
    if filedict["TYPE"]=='DIPO':
      r = restraint_file(table,'r',type=filedict["TYPE"],
                         Daxi=float(filedict["DAXI"]),
                         Drho=float(filedict["DRHO"]))
    else:
      r = restraint_file(table,'r',type=filedict["TYPE"])
    r.read()
    # SET THE BACKGROUND FLAG
    if not filedict.has_key("INFO"): filedict["INFO"]=1
    elif filedict["INFO"].lower()=='no' or filedict["INFO"].lower()=='n':
      filedict["INFO"]=0
    else: filedict["INFO"]=1
    # READ DIPO PARAMETERS

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

# GENERATE RANDOM SET WITH INFO
# =============================
def qn_generatedataset(queen,xplr,restraintlist,info,maxerr=5.,nsets=1):
  datasets = []
  print "Generating dataset with %5.1f %% of information."%info
  # CALCULATE FULL INFO
  print "Calculating information content full set."
  unc_ini = queen.uncertainty(xplr,[])
  unc_all = queen.uncertainty(xplr,restraintlist)
  inf_all = unc_ini-unc_all
  # GENERATE THE DATASETS
  print "Constructing %i subsets."%(nsets)
  while len(datasets) < nsets:
    dataset = {}
    # SHUFFLE RESTRAINT LIST
    shuffle(restraintlist)
    tlist = []
    prog = progress_indicator(100)
    prog.increment(0)
    # CYCLE THE RESTRAINTS
    for r in restraintlist:
      # THE FULL DATASET
      if info in [100,100.]:
        prog.increment(info)
        print "\nScore %6.2f accepted (%i restraints)."%(100.,len(restraintlist))
        dataset['restraints'] = restraintlist
        dataset['target'] = info
        dataset['info'] = 100.
        datasets.append(dataset)
        break
      # AND THE EMPTY ONE
      elif info in [0,0.]:
        prog.increment(info)
        print "\nScore %6.2f accepted (%i restraints)."%(0.,0)
        dataset['restraints'] = []
        dataset['target'] = info
        dataset['info'] = 0.
        datasets.append(dataset)
        break
      tlist.append(r)
      # CALCULATE UNCERTAINTY
      unc = queen.uncertainty(xplr,tlist)
      inf = unc_ini-unc
      # CALC NEW SCORE
      score = (inf/inf_all)*100
      prog.increment(int(score))
      if score <= info+maxerr and \
         score >= info-maxerr and \
         info !=100 and len(tlist)>25:
        print "\nScore %6.2f accepted (%i restraints)."%(score,len(tlist))
        # STORE DATASET
        dataset['restraints'] = tlist
        dataset['target'] = info
        dataset['info'] = score
        datasets.append(dataset)
        break
      # IN CASE WE OVERSHOOT THE TARGET
      elif score > info+maxerr:
        print "\nScore %6.2f rejected (%i restraints)."%(score,len(tlist))
        break
  return datasets

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
    print len(permutationlist[0])
    print myupper
    # NUMBER OF CALCULATIONS FOR EACH PERMUTATION
    npermcalc = myupper*(len(permutationlist[0])-1)
    print npermcalc
    # TWO CALCULATIONS PER DATASET
    ndatacalc = len(datasets)*2
    print ndatacalc
    # TWO REFERENCE CALCULATIONS
    nrefscalc = 2
    print nrefscalc
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

# GET LOCAL UNCERTAINTY
# =====================
# THIS SCRIPT RETURNS A DICTIONARY WITH THE LOCAL BACKBONE
# UNCERTAINTY PER RESIDUE
def qn_bbuncperresidue(queen,xplr,dataset,windowsize=7):
  print "Calculating local information per residue."
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # READ DATASETS
  data = qn_readdatasets(queen,datasets)
  # STORE RESTRAINTLIST
  restraintlist = data["data"]+data["bckg"]
  # CALCULATE IN MEMORY MATRIX
  queen.uncertainty(xplr,restraintlist,clear=0)
  # STORE INFORMATION PER RESIDUE
  ipr = {}
  # CUTOFF IN THE BEGINNING AND END OF THE SEQUENCE WE CANNOT TREAT
  cutoff = (windowsize-1)/2
  # READ PDBFILE
  pdbfile = xplr.template
  pdb = pdb_file.Structure(pdbfile)
  pdbd = {}
  for chain in pdb.peptide_chains:
    cid = chain.segment_id
    ipr[cid]={}
    for residue in chain[cutoff:-cutoff]:
      ipr[cid][residue] = 0.0
    pdbd[cid]=[]
    for residue in chain:
      pdbd[cid].append(residue)
  # DETERMINE LOCAL UNCERTAINTY PER RESIDUE
  for cid in ipr:
    for residue in ipr[cid]:
      # GET THE CA ATOM NUMBER
      for atom in residue:
        if atom.name == 'CA':
          cca = atom['serial_number']-1
          break
      # PICK THE RESIDUE TO SUM
      restosum = range(residue.number-cutoff,residue.number) + \
                 range(residue.number+1,residue.number+1+cutoff)
      #print "%3i"%residue.number,restosum
      # CYCLE THE RESIDUES AGAIN
      for res in pdbd[cid]:
        if res.number in restosum:
          # FIND THE CA
          for atom in res:
            if atom.name == 'CA':
              # CALCULATE UNCERTAINTY
              ca = atom['serial_number']-1
              # AND ADD IT TO THE RESIDUE
              # WE TALK DIRECTLY TO THE NMV MODULE HERE.. Q&D!
              unc = nmv.uncertainty(cca,ca)
              ipr[cid][residue]+= 1.0/(windowsize-1)*unc
    # CLEAR QUEEN
    queen.clear()
  return ipr

# GET LOCAL UNCERTAINTY
# =====================
# THIS SCRIPT RETURNS A DICTIONARY WITH THE LOCAL UNCERTAINTY
# PER RESIDUE
def qn_localuncperresidue(queen,xplr,dataset,cutoff=8):
  print "Calculating local information per residue."
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # READ DATASETS
  data = qn_readdatasets(queen,datasets)
  # STORE RESTRAINTLIST
  restraintlist = data["data"]+data["bckg"]
  # CALCULATE IN MEMORY MATRIX
  queen.uncertainty(xplr,restraintlist,clear=0)
  # STORE UNCERTAINTY PER RESIDUE
  ipr = {}
  # READ PDBFILE
  pdbfile = xplr.template
  pdb = pdb_file.Structure(pdbfile)
  pdbd = {}
  for chain in pdb.peptide_chains:
    cid = chain.segment_id
    ipr[cid]={}
    for residue in chain:
      ipr[cid][residue] = 0.0
    pdbd[cid]=[]
    for residue in chain:
      pdbd[cid].append(residue)
  # DETERMINE LOCAL UNCERTAINTY PER RESIDUE
  for cid in ipr:
    for residue in ipr[cid]:
      # GET THE CA ATOM NUMBER
      for atom in residue:
        if atom.name == 'CA':
          ca = atom['serial_number']-1
          # AND ADD IT TO THE RESIDUE
          # WE TALK DIRECTLY TO THE NMV MODULE HERE.. Q&D!
          unc = nmv.atom_localuncertainty(ca,float(cutoff))
          ipr[cid][residue] = unc
    # CLEAR QUEEN
    queen.clear()
  return ipr

# GET INFORMATION PER RESIDUE
# ===========================
# THIS SCRIPT RETURNS A DICTIONARY WITH THE INFORMATION
# ADDED PER RESIDUE BY THE PROVIDED DATASET
def qn_infperresidue(queen,xplr,dataset):
  print "Calculating local information per residue."
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  # READ DATASETS
  data = qn_readdatasets(queen,datasets)
  # STORE RESTRAINTLIST
  rlist = data["data"]+data["bckg"]
  # STORE INFORMATION PER RESIDUE
  ipr = {}
  # READ PDBFILE
  pdbfile = xplr.template
  pdb = pdb_file.Structure(pdbfile)
  pdbd = {}
  for chain in pdb.peptide_chains:
    cid = chain.segment_id
    ipr[cid]={}
    for residue in chain:
      ipr[cid][residue] = 0.
      pdbd[cid]=[]
    for residue in chain:
      pdbd[cid].append(residue)
  # WE NEED TO CYCLE TWICE TO BE ABLE TO CALCULATE A DIFFERENCE
  for i in range(2):
    if i==0: restraintlist = []
    elif i==1: restraintlist = rlist
    # CALCULATE IN MEMORY MATRIX
    queen.uncertainty(xplr,restraintlist,clear=0)
    # DETERMINE UNCERTAINTY PER RESIDUE
    for cid in ipr:
      for residue in ipr[cid]:
        # GET THE CA ATOM NUMBER
        for atom in residue:
          if atom.name == 'CA':
            ca = atom['serial_number']-1
            if i==0:
              # ADD IT TO THE RESIDUE
              unc = nmv.atom_uncertainty(ca)
              ipr[cid][residue] = unc
            elif i==1:
              # SUBSTRACT FINAL UNC
              unc = nmv.atom_uncertainty(ca)
              ipr[cid][residue] = ipr[cid][residue]-unc
    # CLEAR QUEEN
    queen.clear()
  # PRINT OUTPUT
  xmgr = graceplot('test_%s.dat'%(queen.project),'xy','w')
  xmgr.writeheader()
  for cid in ipr:
    residues = ipr[cid].keys()
    residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
    for residue in residues:
      xmgr.write([residue.number,ipr[cid][residue],residue.name])
  xmgr.close()
  return ipr

# GET HstructureR PER RESIDUE
# ===========================
# THIS SCRIPT RETURNS A DICTIONARY WITH THE UNCERTAINTY
# PER RESIDUE DETERMINED BY THE PROVIDED DATASET
def qn_uncperresidue(queen,xplr,dataset):
  print "Calculating local information per residue."
  if type(dataset)==types.StringType:
    # READ DATAFILE
    datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
    # READ DATASETS
    data = qn_readdatasets(queen,datasets)
    # STORE RESTRAINTLIST
    rlist = data["data"]+data["bckg"]
  elif type(dataset)==types.ListType:
    rlist = dataset
  # STORE INFORMATION PER RESIDUE
  ipr = {}
  # READ PDBFILE
  pdbfile = xplr.template
  pdb = pdb_file.Structure(pdbfile)
  pdbd = {}
  for chain in pdb.peptide_chains:
    cid = chain.segment_id
    ipr[cid]={}
    for residue in chain:
      ipr[cid][residue] = 0.
      pdbd[cid]=[]
    for residue in chain:
      pdbd[cid].append(residue)
  # WE NEED TO GO ONLY ONCE HERE
  restraintlist = rlist
  # CALCULATE IN MEMORY MATRIX
  queen.uncertainty(xplr,restraintlist,clear=0)
  # DETERMINE UNCERTAINTY PER RESIDUE
  for cid in ipr:
    for residue in ipr[cid]:
      # GET THE CA ATOM NUMBER
      for atom in residue:
        if atom.name == 'CA':
          ca = atom['serial_number']-1
          # ADD IT TO THE RESIDUE
          unc = nmv.atom_uncertainty(ca)
          ipr[cid][residue] = unc
  # CLEAR QUEEN
  queen.clear()
  return ipr


# GET UNI INFORMATION PER RESIDUE
# ===============================
# THIS SCRIPT RETURNS A DICTIONARY WITH THE AMOUNT OF
# UNIQUE INFORMATION PER RESIDUE
def qn_Iuniperres(iunifile,restraintlist,pdbfile,pdbformat='xplor'):
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
    shuffle(rlist)
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
def qn_infave_fast(queen,xplr,dataset,ncycles=5):
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
    shuffle(rlist)
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
      skipped = 0
      for r in list:
        # CHECK IF RESTRAINT NEEDS TO BE EVALUATED
        if con_dict[str(r)]==0:
          # ADD SKIPPED ONES
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
      if cycles+queen.numproc >= ncycles:
        for r in data['data']:
          # CALC GENERAL AVERAGES
          ravg = avg_list(inf_dict[str(r)])
          aavg = avg_list(avg_dict[str(r)])
          # GET THE OLDPOSITION
          oldpos = data['data'].index(r)
          # ADD TO THE LOGFILE LIST
          loglist.append([oldpos+1,ravg[0]/inf_all*100,ravg[1]/inf_all*100, \
                          r,cycles])
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
  if queen.numproc > 1:
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
    warning("Your Iave file does not seem to present")
    print "Trying to locate Iave fast file."
    avefile = os.path.join(queen.outputpath,'Iavef_%s.dat'%dataset)
    if not os.path.exists(avefile):
      error("Your Iavef file also does not seem to present")
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
    warning("Your Iave file does not seem to present")
    print "Trying to locate Iave fast file."
    avefile = os.path.join(queen.outputpath,'Iavef_%s.dat'%dataset)
    if not os.path.exists(avefile):
      error("Your Iavef file also does not seem to present")
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
      shuffle(rlist)
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
  shuffle(restraintlist)
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


# CLASIFIES DISTANCE RESTRAINTS
# ==========================
# FUNCTION TAKES A DISTANCE RESTRAINT FILE
# CLASSIFIES THE DISTANCES
def rfile_classify(intbl,outtbl=None,format='XPLOR'):
  # READ RESTRAINT FILE
  rf = restraint_file(intbl,'r',format=format)
  rf.read()
  # CYCLE THE RESTRAINT FILE
  classified = r_classify(rf.restraintlist)
  # WRITE OUTPUT
  if outtbl:
    r = restraint_file(outtbl,'w',format=format)
    r.mwrite(classified)

# VISUALIZE DISTANCE RESTRAINTS
# =============================
# FUNCTION TAKES A DISTANCE RESTRAINT FILE AND
# SHOWS THEM IN THE PROVIDED PDBFILE
def rfile_visualize(intbl,pdbfile,yaspath,cutoff=10000,
                    type='DIST',format='XPLOR'):
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
    #print restraint
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
        #print pdb[kindex].name, klist
        #print pdb[lindex].name, llist
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

# PLOT BOUND DISTRIBUTION
# =======================
# Normalize=1 : normalize on refpdb
# Normalize=2 : normalize on bounds
def rfile_plotbounds(intbl,plotfile,pdblist,refpdb=None,normalize=False):
  print "Creating bound distributions for %i PDB files."%len(pdblist)
  # READ RESTRAINT FILE
  rf = restraint_file(intbl,'r')
  rf.read()
  rf.restraintlist = rf.restraintlist[:100]
  # DISTANCE DICTIONARY
  dist = {}
  # CYCLE PDB FILES
  for pdbf in pdblist:
    # READ PDBFILE
    pdb = pdb_file.Structure(pdbf)
    # ADJUST THE RESTRAINT LIST
    adjusted = r_adjust(rf.restraintlist,pdb,precision=0.0)
    # STORE THE ADJUSTED BOUNDS
    for r in adjusted:
      dist[r] = dist.get(r,[]) + [r.upperb]
  # HANDLE THE REFERENCE FILE
  if refpdb:
    print "Processing reference file."
    refdist = {}
    # READ PDBFILE
    pdb = pdb_file.Structure(refpdb)
    # ADJUST THE RESTRAINT LIST
    adjusted = r_adjust(rf.restraintlist,pdb,precision=0.0)
    # STORE THE ADJUSTED BOUNDS
    for r in adjusted:
      refdist[r] = r.upperb
  # WRITE THE PLOT
  print "Writing plot."
  xmgr = graceplot(plotfile,'xy','w')
  xmgr.xlab = "Restraint index"
  xmgr.ylab = "Bound distribution"
  xmgr.writeheader()
  # EMPTY LISTS
  l_perc1090, l_perc2575 = [],[]
  l_avg, l_outliers, l_xray = [],[],[]
  # NORMALIZE ON CRYSTAL STRUCTURE
  if normalize==1 and refpdb:
    for r in rf.restraintlist:
      # NORMALIZE DISTANCES
      dist_norm  = []
      for i in range(len(dist[r])):
        dist_norm.append((dist[r][i]/refdist[r])*100)
      # BUILD TIE FIGHTER PLOTS
      tie = avg_list_tiefighter(dist_norm)
      # STORE TIE FIGTHER SCORES
      l_perc1090.append([rf.restraintlist.index(r),
                         tie[50],tie[90]-tie[50],tie[50]-tie[10]])
      l_perc2575.append([rf.restraintlist.index(r),
                         tie[50],tie[75]-tie[50],tie[50]-tie[25]])
      # STORE OUTLIERS
      for el in tie['outliers']:
        l_outliers.append([float(rf.restraintlist.index(r)),el])
      # STORE AVERAGE
      l_avg.append([rf.restraintlist.index(r),tie['avg'],tie['sd']])
    # WRITE GRACE OUTPUT
    xmgr.mwrite(l_outliers)
    xmgr.type = 'xydydy'
    xmgr.newset()
    xmgr.mwrite(l_perc1090)
    xmgr.newset()
    xmgr.mwrite(l_perc2575)
    xmgr.type = 'xydy'
    xmgr.newset()
    xmgr.mwrite(l_avg)
    # CLOSE FILE
    xmgr.close()
  # NORMALIZE ON BOUNDS
  elif normalize==2 and refpdb:
    for r in rf.restraintlist:
      # NORMALIZE DISTANCES
      dist_norm  = []
      for i in range(len(dist[r])):
        dist_norm.append(((dist[r][i]-r.lowerb)/(r.upperb-r.lowerb))*100)
      # BUILD TIE FIGHTER PLOTS
      tie = avg_list_tiefighter(dist_norm)
      # STORE TIE FIGTHER SCORES
      l_perc1090.append([rf.restraintlist.index(r),
                         tie[50],tie[90]-tie[50],tie[50]-tie[10]])
      l_perc2575.append([rf.restraintlist.index(r),
                         tie[50],tie[75]-tie[50],tie[50]-tie[25]])
      # STORE OUTLIERS
      for el in tie['outliers']:
        l_outliers.append([float(rf.restraintlist.index(r)),el])
      # STORE AVERAGE
      l_avg.append([rf.restraintlist.index(r),tie['avg'],tie['sd']])
      # STORE XRAY
      l_xray.append([rf.restraintlist.index(r),
                     ((refdist[r]-r.lowerb)/(r.upperb-r.lowerb))*100])
    # WRITE GRACE OUTPUT
    xmgr.mwrite(l_outliers)
    xmgr.type = 'xydydy'
    xmgr.newset()
    xmgr.mwrite(l_perc1090)
    xmgr.newset()
    xmgr.mwrite(l_perc2575)
    xmgr.type = 'xydy'
    xmgr.newset()
    xmgr.mwrite(l_avg)
    xmgr.type = 'xy'
    xmgr.newset()
    xmgr.mwrite(l_xray)
    # CLOSE FILE
    xmgr.close()
  else:
    # WRITE PLAIN VALUES
    for r in rf.restraintlist:
      for i in range(len(pdblist)):
        xmgr.write([rf.restraintlist.index(r)+1,
                    dist[r][i],
                    str(r)])
  xmgr.close()
  print "Done."


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


# EXTRACT HBONDS
# ==============
# EXTRACT HBONDS FROM RESTRAINT LIST
def r_extracthbonds(restraintlist):
  hbonds, others = [],[]
  for restraint in restraintlist:
    namelist = restraint.data[0]["NAME"] + restraint.data[1]["NAME"]
    hb = 0
    for el in namelist:
      el = el.lower()
      if el == 'o':
        hb =1
    if hb:
      hbonds.append(restraint)
    else:
      others.append(restraint)
  return hbonds,others

# CLASSIFY RESTRAINT
# ==================
# SET RESTRAINT BOUND TO ONE OF THE FOLLOWING THREE CLASSES
# 0.0-2.7
# 0.0-3.3
# 0.0-5.0
def r_classify(restraintlist):
  classifiedrestraints = []
  for r in restraintlist:
    if r.upperb >= 3.5:
      r.upperb = 5.0
    elif r.upperb < 3.5 and r.upperb > 2.7:
      r.upperb = 3.5
    else:
      r.upperb = 2.7
    r.lowerb = 0.0
    classifiedrestraints.append(r)
  return classifiedrestraints

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
    nr = copy.copy(r)
    if precision == None:
      if   upp <= 2.8: upp = 2.8
      elif upp <= 3.5: upp = 3.5
      elif upp <= 5.0: upp = 5.0
      elif upp  > 5.0: upp = round(upp)
      nr.lowerb = 0.0
      nr.upperb = upp
    else:
      nr.lowerb = upp - precision/2.0
      nr.upperb = upp + precision/2.0
    nr.target = nr.upperb
    adjusted.append(nr)
    print "Adjusted %4i of %4i restraints.\r"%(restraintlist.index(r)+1,len(restraintlist)),
    sys.stdout.flush()
  print
  return adjusted


#  ======================================================================
#    N M R I N F O   F U N C T I O N   G R O U P
#  ======================================================================

# READ SEQUENCE
# =============
# READ SEQUENCE FILE
def nmrinfo_readsequence(sequencefile):
  dict = {}
  # OPEN FILE
  content = open(sequencefile,'r').readlines()
  if content[0][0]!='>':
    error("Start sequence file with chain identifier.")
  for line in content:
    if line[0]=='>':
      # START NEW CHAIN
      key = line[2]
      dict[key]=[]
    else:
      # APPEND TO CHAIN
      dict[key].append(line[:-1])
  # RETURN THE DICTIONARY
  return dict

# CREATE SEQUENCE
# ===============
# CREATE SEQUENCE FILE
def nmrinfo_createsequence(pdbfile,sequencefile):
  seqfile = open(sequencefile,'w')
  pdb = pdb_file.Structure(pdbfile)
  for chain in pdb.peptide_chains:
    seqfile.write("> %s\n"%chain.chain_id)
    for res in chain.sequence3():
      seqfile.write("%s\n"%res)
  seqfile.close()

# READ DISULFIDES
# ===============
# FUNCTION READS DISULFIDES
def nmrinfo_readdisulfides(disulfidefile):
  list = []
  # OPEN FILE
  content = open(disulfidefile,'r').readlines()
  for line in content:
    sline = string.split(line)
    if len(sline)==4:
      list.append([sline[0],int(sline[1]),sline[2],int(sline[3])])
    elif len(sline)==2:
      list.append([int(sline[0]),int(sline[1])])
    else:
      error("Invalid disulfide line!")
  return list

# READ PATCH DICTIONARY
# =====================
# DICTIONARY IS ALLOWED TO HAVE MORE VALUES WITH
# ONE KEY, VALUES ARE ADDED TO A LIST
def nmrinfo_readpatches(filename):
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
  print dct
  return(dct)

# READ DATAFILE
# =============
# FUNCTION READS A DATASET DESCRIPTION FILE
def nmrinfo_readdatafile(datafile):
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
  return filelist


#  ======================================================================
#    P D B   E R R O R   C L A S S
#  ======================================================================

class pdb_error:
  """
  This class provides an interface to PDB errors
  - Create a class instance giving a path+filename, errortype and error handling function.
  - Allowed error types
     - 'all' (NOTES, WARNINGS, ERRORS)
     - 'we'  (WARNINGS AND ERRORS)
     - 'e'   (ONLY ERRORS)
  - Instance.list contains a list of all errornumber of the given errortype
  - Instance.dict contains a dictionary of the given errortypes (key) and to what the error applies (value):
     - 'V'   (Value, like in a Z-score)
     - 'M'   (Model, error applies to the full structure e.g. Matthews coefficient)
     - 'R'   (Residue, error goes per residue e.g. Arginine nomenclature error)
  - Instance.finderrors(errornumber) reads the PDBREPORT of the given error number
  - Instance.pdbswitherror then contains the PDB id's of the PDB file with the given errornumber
  - Instance.findvalue(pdb,errornumber) retrieves value of the error with the given errornumber of the given pdb file
  - Instance.value then contains the value
  - Instance.findentries(pdb,errornumber) retrieves the number of entries in the request error for the given pdbfile
  - Instance.findentriespdblist(pdblist,errornumber) retrieves the number of entries in the request error in the given pdblist
  - Instance.entries then contains the number of entries
  - Instance.name(errornumber) returns the name of the error with the given errornumber
  """
  # OPEN PDB ERROR
  # ==============
  # - path IS THE PDBREPORT revindex.html
  # different types are allowed:
  # - 'all' (NOTES, WARNINGS, ERRORS)
  # - 'we'  (WARNINGS AND ERRORS)
  # - 'e'   (ONLY ERRORS)
  # - errorfunc IS THE NAME OF AN ERROR HANDLING FUNCTION.
  def __init__(self,path,errortype,errorfunc):
    self.error=None
    self.errorfunc=errorfunc
    self.dict={}
    self.path = path
    self.pdbswitherror = []
    self.value = 0
    self.entries = 0
    # SET TYPES TO SELECT
    if errortype=='all':
      errors = ['Note:','Warning:','Error:']
    elif errortype=='we':
      errors = ['Warning:','Error:']
    elif errortype=='e':
      errors = ['Error:']
    else:
      self.raiseerror("%s is an invalid errortype."%errortype)
    # OPEN, READ AND CLOSE THE INDEX FILE
    file = open(path,'r')
    content = file.readlines()
    file.close()
    # PARSE THE FILE
    for line in content:
      # FIRST THE SELECT THE RIGHT LINES
      if line[0:4]=='<H3>':
        # DETERMINE THE TYPE (NOTE, ERROR, WARNING)
        type = string.split(line[:-1])[0][4:]
        # SELECT ONLY THE RIGHT ERROR TYPES
        if type in errors:
          # DETERMINE THE REVINDEX NUMBER
          begin_number = string.find(line,'revindex')+len('revindex')
          end_number = string.find(line,'.html>')
          number = int(line[begin_number:end_number])
          # DETERMINE THE ERROR TYPE
          if string.split(line)[0][4:] == 'Note:':
            self.dict[number] = 'N'
          else:
            # BUILD THE FILENAME FOR THE ERROR
            error_file = string.replace(path,'.html','%s.html'%number)
            # OPEN READ AND CLOSE THE ERRORFILE
            if os.path.exists(error_file):
              file = open(error_file,'r')
              errorlist = file.readlines()
              file.close()
            else:
              break
            # CHECK ERROR TYPE
            for errorline in errorlist:
              # READ THE FIRST ENTRY OF THE LIST
              if errorline[0:4]=='<LI>':
                # IF NO ADDITONAL DATA IS PRESENTED THE ERROR OR WARNING APPLIES FOR THE FULL MODEL
                if len(string.split(errorline)) == 2:
                  self.dict[number]= 'M'
                  # READ ONLY ONE ENTRY OF THE LIST
                  break
                else:
                  try:
                    # IF A VALUE IS GIVEN, SET THE VALUE FLAG
                    if string.split(errorline)[2]=='(Value':
                      self.dict[number] = 'V'
                    # IF AN ENTRY COUNT IS GIVEN, SET THE PER RESIDUE FLAG
                    if string.split(errorline)[3]=='entries':
                      self.dict[number] = 'R'
                  except IndexError:
                    pass
                  break

  # RAISE AN ERROR
  # ==============
  # CALLS THE ERRORFUNCTION PROVIDED BY THE USER WITH THE GIVEN STRING
  def raiseerror(self,errormsg):
    self.error=errormsg
    if (self.errorfunc!=None): apply(self.errorfunc,[errormsg])
    return

  # LIST OF PDBS WITH GIVEN ERROR
  # =============================
  # FUNCTION RETURNS A LIST OF PDB ID'S WITH A GIVEN ERROR
  def finderrors(self,errornumber):
    inreport = []
    # CONSTRUCT THE PDBREPORT REVINDEX FILE NAME FOR THE ERROR
    error_file = string.replace(self.path,'.html','%s.html'%errornumber)
    # CHECK IF THE ERROR FILE EXISTS
    if os.path.exists(error_file):
      # OPEN, READ AND CLOSE THE ERROR FILE
      file = open(error_file,'r')
      content = file.readlines()
      file.close()
      # EXTRACT THE PDB ENTRIES WITH THAT GIVEN ERROR
      for line in content:
        try:
          if line[0:4]=='<LI>':
            inreport.append(string.split(line)[1][-8:-4])
        except:
          pass
    # STOP SCRIPT IF ERROR(FILE) DOESN'T EXIST
    else:
      self.raiseerror("PDBREPORT indexfile %s does not exist!"%error_file)
    # RETURN THE LIST
    self.pdbswitherror = inreport


  # VALUE OF ERROR
  # ==============
  # FUNCTION RETURNS THE VALUE OF THE ERROR FOR A CERTAIN PDB ENTRY
  def findvalue(self,pdb,errornumber):
    # BUILD THE FILENAME FOR THE ERROR
    error_file = string.replace(self.path,'.html','%s.html'%errornumber)
    # OPEN READ AND CLOSE THE ERRORFILE
    if os.path.exists(error_file):
      file = open(error_file,'r')
      errorlist = file.readlines()
      file.close()
    else:
      self.raiseerror("PDB report %s does not exist"%error_file)
    # LOOK FOR THE CORRECT PDB FILE
    for errorline in errorlist:
      # READ THE FIRST ENTRY OF THE LIST
      if errorline[0:4]=='<LI>':
        # CHECK THE PDB CODE
        if string.split(errorline)[1][-8:-4] == pdb:
          value = float(string.split(errorline)[3][:-1])
          break
    # RETURN VALUE
    self.value = value


  # ENTRIES IN ERROR
  # ================
  # FUNCTION RETURNS THE ENTRIES IN THE ERROR FOR A CERTAIN PDB ENTRY
  def findentries(self,pdb,errornumber):
    entry_count = 0
    # BUILD THE FILENAME FOR THE ERROR
    error_file = string.replace(self.path,'.html','%s.html'%errornumber)
    # OPEN READ AND CLOSE THE ERRORFILE
    if os.path.exists(error_file):
      file = open(error_file,'r')
      errorlist = file.readlines()
      file.close()
    else:
      self.raiseerror("PDB report %s does not exist"%error_file)
    # LOOK FOR THE CORRECT PDB FILE
    for errorline in errorlist:
      # READ THE FIRST ENTRY OF THE LIST
      if errorline[0:4]=='<LI>':
        # CHECK THE PDB CODE
        if string.split(errorline)[1][-8:-4] == pdb:
          entry_count = int(string.split(errorline)[2][1:])
          break
    # RETURN VALUE
    self.entries = entry_count


  # ENTRIES IN ERROR INPUT PDBLIST
  # ==============================
  # FIND ENTRIES FROM A LIST OF PDB ID's
  def findentriespdblist(self,pdblist,errornumber):
    entry_count = 0
    # BUILD THE FILENAME FOR THE ERROR
    error_file = string.replace(self.path,'.html','%s.html'%errornumber)
    # OPEN READ AND CLOSE THE ERRORFILE
    if os.path.exists(error_file):
      file = open(error_file,'r')
      errorlist = file.readlines()
      file.close()
    else:
      self.raiseerror("PDB report %s does not exist"%error_file)
    # LOOK FOR THE CORRECT PDB FILE
    for errorline in errorlist:
      # READ THE FIRST ENTRY OF THE LIST
      if errorline[0:4]=='<LI>':
        # CHECK THE PDB CODE
        if string.split(errorline)[1][-8:-4] in pdblist:
          entry_count = entry_count + int(string.split(errorline)[2][1:])
    # RETURN VALUE
    self.entries = entry_count


  # ERROR NAME
  # ================
  # FUNCTION RETURNS THE NAME OF THE ERROR WITH THE GIVEN ERRORNUMBER
  def name(self,errornumber):
    # CONSTRUCT THE PDBREPORT REVINDEX FILE NAME FOR THE ERROR
    error_file = string.replace(self.path,'.html','%s.html'%errornumber)
    # CHECK IF THE ERROR FILE EXISTS
    if os.path.exists(error_file):
      # OPEN, READ AND CLOSE THE ERROR FILE
      file = open(error_file,'r')
      content = file.readlines()
      file.close()
      # EXTRACT THE PDB ENTRIES WITH THAT GIVEN ERROR
      line = content[0]
      begin = int(string.find(line,'<TITLE>'))+len('<TITLE>')
      end = int(string.find(line,'</TITLE>'))
      name = string.replace(line[begin:end],'"',' ')
    # STOP SCRIPT IF ERROR(FILE) DOESN'T EXIST
    else:
      self.raiseerror("PDBREPORT indexfile %s does not exist!"%error_file)
    # RETURN THE LIST
    return name


#  ======================================================================
#    C O N C O O R D   P A T C H E S   G R O U P
#  ======================================================================

# PATCH THE ILE CD ATOMS IN A CONCOORD OUTPUT FILE
# ================================================
def cncrd_ilepatch(filename):
  # OPEN AND READ THE FILE
  file = open(filename,'r')
  content = file.readlines()
  file.close()
  # GO TRHOUGH THE FILE
  cleancontent = []
  for line in content:
    # DO THE ATOM
    if line[:4]=='ATOM':
      splitline = string.split(line)
      if splitline[3]=='ILE' and  splitline[2]=='CD':
        line = string.replace(line,"CD ","CD1")
        cleancontent.append(line)
      else:
        cleancontent.append(line)
    elif line[:3]=='END':
      cleancontent.append(line)
  # WRITE THE NEW FILE
  file = open(filename,'w')
  for line in cleancontent:
    file.write(line)
  file.close()


# PATCH SEQ_ID'S IN A CONCOORD OUTPUT FILE
# ========================================
def cncrd_seqidpatch(filename):
  # OPEN AND READ THE FILE
  file = open(filename,'r')
  content = file.readlines()
  file.close()
  # GO TRHOUGH THE FILE
  cleancontent = []
  for line in content:
    # DO THE ATOM LINES INLY
    if line[:4]=='ATOM':
      line = line[:66]+"      A   \n"
      cleancontent.append(line)
    else:
      cleancontent.append(line)
  # WRITE THE NEW FILE
  file = open(filename,'w')
  for line in cleancontent:
    file.write(line)
  file.close()


#  ======================================================================
#                         E M A I L   C L A S S
#  ======================================================================

class email_server:
  """
  USAGE:
  - Create a class instance giving server,username,password and error function in parentheses
    If username or password is None, you can only send but not receive mail.
  - Instance.error contains an error description if something went wrong
  - Instance.new(Sender,subject) creates a new email.
  - Instance.msg is a list of message lines, use append to add text.
  - Instance.attachtext(filename) adds a text attachment.
  - Instance.attachbin(filename) adds a binary attachment.
  - Instance.send(receiver) sends the message.
  - Instance.retrieve(delflag) gets next message from server, message will be deleted if delflag is set.
  - Instance.close() ends connection to server

  Example:
  email=email_server("cmbi1","Eliza","tewoosmai",error)
  email.new("Eliza@yasara.com","Message from Eliza")
  email.msg=["Hi!","Just wanted to say I love you!"]
  email.attachtext("loveletter.txt")
  email.attachbin("eliza.jpg")
  email.send("afinkel@vega.protres.ru")
  email.send("snabuurs@cmbi.kun.nl")
  email.close()
  """

  # CONTACT EMAIL SERVER
  # ====================
  def __init__(self,server,username=None,password=None,errorfunc=None):
    #print "Opening %s with username %s and password %s\n" % (server,username,password)
    self.error=None
    self.errorfunc=errorfunc
    if (username!=None and password!=None):
      # ACCESS INCOMING MAIL
      # OPEN MAILBOX
      while (1):
        self.mail=poplib.POP3(server)
        """
        try: self.mail=poplib.POP3(server)
        except:
          print "POP3 server %s refused connection. Waiting 30 minutes." % server
          time.sleep(30*60)
          continue
        """
        break
      response=self.mail.user(username)
      #print response
      if (response[0:3]!="+OK"):
        self.raiseerror("__init__: Mail user name not accepted")
      response=self.mail.pass_(password)
      #print response
      if (response[0:3]!="+OK"):
        self.raiseerror("__init__: Mail password not accepted")
      # GET MESSAGE SCAN
      self.list=self.mail.list()
      #print self.list
      self.messages=len(self.list[1])
      print "%d messages waiting." % self.messages
    else:
      # NO INCOMING MAIL
      self.mail=None
      self.list=[]
      self.messages=0
    # OPEN SERVER FOR OUTGOING MAIL
    while (1):
      try: self.server=smtplib.SMTP(server)
      except:
        print "SMTP server %s refused connection. Waiting 30 minutes." % server
        time.sleep(30*60)
        continue
      break

  # RAISE AN ERROR
  # ==============
  # CALLS THE ERRORFUNCTION PROVIDED BY THE USER WITH THE GIVEN STRING
  def raiseerror(self,errormsg):
    self.error=errormsg
    if (self.errorfunc!=None): apply(self.errorfunc,["email_server."+errormsg])
    return

  # CLOSE CONNECTION
  # ================
  def close(self):
    if (self.mail!=None):
      print "Sending QUIT command to POP3 server."
      print self.mail.quit()
      self.mail=None
    if (self.server!=None):
      print "Sending QUIT command to SMTP server."
      print self.server.quit()
      self.server=None

  # START NEW EMAIL
  # ===============
  def new(self,sender,subject):
    self.msg=[]
    self.sender=sender
    self.subject=subject
    self.textattachment=[]
    self.binattachment=[]

  # ATTACH TEXT FILE
  # ================
  def attachtext(self,filename):
    self.textattachment.append(filename)

  # ATTACH BINARY FILE
  # ==================
  def attachbin(self,filename):
    self.binattachment.append(filename)

  # SEND EMAIL
  # ==========
  def send(self,recipient):
    boundary="----WrittenByEliza"
    # HEADER
    if (len(self.textattachment) or len(self.binattachment)): attachflag=1
    else: attachflag=0
    message="From: "+self.sender+"\nTo: "+recipient+"\nSubject: "+self.subject+"\n"
    if (attachflag):
      message=message+"MIME-Version: 1.0\n"+\
                      "Content-Type: multipart/mixed; boundary=\"%s\"\n\n" % boundary +\
                      "This is a multi-part message in MIME format.\n--"+boundary+\
                      "\nContent-Type: text/plain; charset=us-ascii\n"
    message=message+'\n'
    # ADD MESSAGE BODY
    for line in self.msg: message=message+line+'\n'
    # ATTACH TEXT FILES
    for i in range(len(self.textattachment)):
      filename=self.textattachment[i]
      message=message+"--"+boundary+"\nContent-Type: text/plain; charset=us-ascii; "+\
              "name=\"%s\"\nContent-Transfer-Encoding: 7bit\n" % os.path.basename(filename) +\
              "Content-Disposition: attachment; filename=\"%s\"\n\n" % os.path.basename(filename)
      try: txt=open(filename,"r").readlines()
      except: self.raiseerror("send: Attachment %s not found" % filename)
      for line in txt: message=message+line
    # ATTACH BINARY FILES
    for i in range(len(self.binattachment)):
      filename=self.binattachment[i]
      message=message+"--"+boundary+"\nContent-Type: application/octet-stream; "+\
              "name=\"%s\"\nContent-Transfer-Encoding: base64\n" % os.path.basename(filename) +\
              "Content-Disposition: attachment; filename=\"%s\"\n\n" % os.path.basename(filename)
      try: code=base64.encodestring(open(filename,"r").read())
      except: self.raiseerror("send: Attachment %s not found" % filename)
      while (len(code)):
        message=message+code[:min(72,len(code))]
        code=code[72:]
    if (attachflag): message=message+"--"+boundary
    # SEND EMAIL
    print "Sending EMAIL from %s to %s:"%(self.sender,recipient)
    print message
    while (1):
      try: self.server.sendmail(self.sender,recipient,message)
      except:
        print "EMAIL server not responding, no mails can be sent. Waiting 30 minutes."
        time.sleep(30*60)
        continue
      break

  # RETRIEVE EMAIL
  # ==============
  # THE NEXT MESSAGE RETRIEVED FROM THE MAILBOX AND MARKED FOR DELETION
  # IF delflag IS SET.
  def retrieve(self,delflag):
    dummyboundary="--*DummyBoundary12345678*"
    if (self.messages):
      # RETRIEVE NEXT MESSAGE
      message=self.mail.retr(self.messages)
      if (message[0][0:3]!="+OK"): self.raiseerror("retrieve: Message %d could not be retrieved" % (i+1))
      message=message[1]
      while (message[0]==''): del(message[0])
      # EXTRACT HEADER
      headlines=0
      while (headlines<len(message)):
        if (string.strip(message[headlines])==""): break
        headlines=headlines+1
      print "Email retrieved:"
      print "HEADER:"
      print message[:headlines]
      # SEARCH FOR BOUNDARY AND ENCODING
      boundary=dummyboundary
      for j in range(headlines):
        line=string.strip(message[j])
        # BOUNDARY
        pos=string.find(string.lower(line),"boundary=")
        if (pos!=-1):
          pos=pos+9
          while (line[pos]==' '): pos=pos+1
          if (line[pos]=='"'): pos=pos+1
          pos2=string.find(line[pos:],'"')
          if (pos2==-1): boundary="--"+line[pos:]
          else: boundary="--"+line[pos:pos+pos2]
          break
        # BASE64 ENCODING FOR ENTIRE MESSAGE
        pos=string.find(string.lower(line),"content-transfer-encoding: base64")
        if (pos!=-1):
          message[j]=line[:pos]+"Content-transfer-encoding: 7BiT"+line[pos+33:]
          # DECODE ENTIRE BODY
          k=headlines+1
          encoded=""
          while (k<len(message)):
            line=string.strip(message[k])
            del message[k]
            encoded=encoded+line
          print "Encoded string is:"
          print encoded
          # DECODE BASE64 STRING
          if (encoded==""): decoded=""
          else: decoded=base64.decodestring(encoded)
          message.insert(k,decoded)
          print "Decoded string is:"
          print message[k]
      print "The boundary is"+boundary+"\n"
      j=headlines+1
      if (boundary==dummyboundary):
        # NO BOUNDARY FOUND
        if (j<len(message) and message[j][0:2]=='--'):
          # ASSUME NO BOUNDARY WAS GIVEN
          boundary=string.strip(message[j])
          print "Assuming first line of body is boundary: "+boundary
      # SEARCH FOR ENCODING
      while (j<len(message)):
        line=string.lower(string.strip(message[j]))
        pos=string.find(line,"content-transfer-encoding: base64")
        if (pos!=-1):
          # BASE64 ENCODING FOUND
          message[j]="Content-transfer-encoding: 7BIT"
          while (j+1<len(message) and string.strip(message[j+1])!=""): del message[j+1]
          j=j+2
          encoded=""
          while (j<len(message)):
            line=string.strip(message[j])
            if (line[:len(boundary)]==boundary): break
            del message[j]
            encoded=encoded+line
          pos=string.find(encoded,"=")
          # SOME BUGGED MAILS CONTAIN CHARACTERS AFTER =
          if (pos!=-1): encoded=encoded[:pos+1]
          tripplets=int(len(encoded)/4)
          encoded=encoded[:tripplets*4]
          print len(encoded)
          # DECODE BASE64 STRING
          if (encoded==""): decoded=""
          else: decoded=base64.decodestring(encoded)
          message.insert(j,decoded)
        j=j+1
      print "BODY:"
      print message[headlines+1:]
      # DELETE MESSAGE IF REQUESTED
      if (delflag):
        print "Deleting message"
        print self.mail.dele(self.messages)
      self.messages=self.messages-1
      return(message[:headlines],message[headlines+1:],boundary)
    else:
      return(None,None,None)

  # CHECK IF MESSAGE IS SPAM
  # ========================
  def isspam(self,message):
    message=string.lower(string.join(message))
    # MAIL IS CONSIDERED SPAM IF IT CONTAINS ONE OF THE FOLLOWING STRINGS
    spamhints=["<html>"]
    for spamhint in spamhints:
      if (string.find(message,spamhint)!=-1): return(1)
    return(0)

  # EXTRACT SENDER FROM HEADER
  # ==========================
  def sender(self,header):
    for line in header:
      line=string.lower(string.strip(line))
      atpos=string.find(line,'@');
      if (line[:4]=="from" and atpos!=-1):
        start=end=atpos
        while (start>5 and line[start-1] not in [' ','<',':']): start=start-1
        while (end<len(line) and line[end] not in [' ','>']): end=end+1
        return(line[start:end])
    return(None)


#  ======================================================================
#    E M A I L   F U N C T I O N   G R O U P
#  ======================================================================

# SEND EMAIL
# ==========
# EMAIL message WITH subject IS SENT TO address
def eml_send(address,subject,msglist,server=None,sender=None):
  # HEADER
  if (sender==None): sender=nmvconf["EMAIL_SENDER"]
  if (server==None): server=nmvconf["EMAIL_SERVER"]
  message="From: "+sender+"\nTo: "+address+"\nSubject: "+\
          subject+"\n"
  # ADD MESSAGE BODY
  for line in msglist: message=message+line
  # SEND EMAIL
  server=smtplib.SMTP(server)
  server.sendmail(sender,address,message)
  server.quit()

# VALIDATE EMAIL
# ==============
# CHECK IF A STRING IS A VALID EMAIL ADRESS
def eml_validate(email):
  if len(email) > 6:
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
      return 1
  return 0

#  ======================================================================
#    B A C K U P   F U N C T I O N   G R O U P
#  ======================================================================

# COPY DIRECTORY
# ==============
# THIS FUNCTION JUST COPIES THE DIRECTORY TO THE SPECIFIED DISK
def bkp_copydir(orig_dir,bckp_path,logfile,flag='keep'):
  logfile.write("########################################\n")
  logfile.write("Uncompressed backup started. Backing up:\n%s\nto\n%s.\n"%(orig_dir,bckp_path))
  logfile.write("On my watch it's %s.\n"%time.ctime(time.time()))
  # DIR NAMES
  orig_dirname = os.path.split(orig_dir)[1]
  # CHECK IF THE ORIGINAL DIRECTORY IS PRESENT
  if os.path.exists(orig_dir):
    # CHECK IF THE BACKUP DIR IS REACHABLE
    if os.path.exists(bckp_path):
      # CHECK IF A BACKUP DIR IS ALREADY PRESENT
      bckp_dir = os.path.join(bckp_path,orig_dirname)
      if os.path.exists(bckp_dir):
        old_bckp_file=os.path.join(bckp_path,"%s_bckp.tar.gz"%orig_dirname)
        # DELETE THE BACKUP OF THE BACKUP
        if os.path.exists(old_bckp_file):
          os.remove(old_bckp_file)
        if flag=='keep':
          # CREATE A TARRED BACKUP OF THE UNTARRED BACKUP
          os.system("tar cfz %s %s"%(old_bckp_file,bckp_dir))
        # DELETE THE OLD BACKUP
        dsc_rmdir(bckp_dir)
      # BACK THE NEW DIR
      os.system("cp -r %s %s"%(orig_dir,bckp_path))
    else:
      logfile.write("The directory to back up to cannot be found or is unreachable.\n")
      logfile.write("Directory: %s\n"%orig_dir)
  else:
    logfile.write("The directory to back up cannot be found or is unreachable.\n")
    logfile.write("Directory: %s\n"%orig_dir)
  logfile.write("Backup finished.\n")
  logfile.write("On my watch it's %s.\n"%time.ctime(time.time()))
  logfile.write("########################################\n\n")
  logfile.flush()

# TAR GZ DIRECTORY
# ==============
# THIS FUNCTION TARS AND GZS DIR TO THE BACKUP DIR
def bkp_targzdir(orig_dir,bckp_path,logfile,flag='keep'):
  logfile.write("########################################\n")
  logfile.write("Compressed backup started. Backing up:\n%s\nto\n%s.\n"%(orig_dir,bckp_path))
  logfile.write("On my watch it's %s.\n"%time.ctime(time.time()))
  # DIR NAMES
  orig_dirname = os.path.split(orig_dir)[1]
  # CHECK IF THE ORIGINAL DIRECTORY IS PRESENT
  if os.path.exists(orig_dir):
    bckp_file     = os.path.join(bckp_path,"%s.tar.gz"%orig_dirname)
    old_bckp_file = os.path.join(bckp_path,"%s_bckp.tar.gz"%orig_dirname)
    # CHECK IF THE BACKUP PATH IS REACHABLE
    if os.path.exists(bckp_path):
      # CHECK IF WE ALREADY HAVE A BACKUP OF THE BACKUP
      if os.path.exists(old_bckp_file):
        # REMOVE BACKUP OF THE BACKUP
        os.remove(old_bckp_file)
      if os.path.exists(bckp_file):
        if flag=='keep':
          # CREATE BACKUP OF THE BACKUP
          os.rename(bckp_file,old_bckp_file)
        if flag=='delete':
          os.remove(bckp_file)
      # CREATE THE NEW BACKUP
      os.system("tar cfz %s %s"%(bckp_file,orig_dir))
    else:
      logfile.write("The directory to back up to cannot be found or is unreachable.\n")
      logfile.write("Directory: %s\n"%orig_dir)
  else:
    logfile.write("The directory to back up cannot be found or is unreachable.\n")
    logfile.write("Directory: %s\n"%orig_dir)
  logfile.write("Backup finished.\n")
  logfile.write("On my watch it's %s.\n"%time.ctime(time.time()))
  logfile.write("########################################\n\n")
  logfile.flush()


#  ======================================================================
#    S T R I N G   F U N C T I O N   G R O U P
#  ======================================================================

# INCREMENT A STRING (WITH NUMBERS AT THE END)
# ============================================
def str_inc(str):
  i=len(str)-1
  while (i>=0):
    ch=chr(ord(str[i])+1)
    if (ch>=':'): ch='0'
    str=str[:i]+ch+str[i+1:]
    if (ch!='0'): break
    i=i-1
  return(str)

# DECREMENT A STRING (WITH NUMBERS AT THE END)
# ============================================
def str_dec(str):
  i=len(str)-1
  while (i>=0):
    ch=chr(ord(str[i])-1)
    if (ch<='/'): ch='9'
    str=str[:i]+ch+str[i+1:]
    if (ch!='9'): break
    i=i-1
  return(str)


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
      elif residue=='W':
        return ['HD1']
      else:
        return ['HD1','HD2']
    elif name=='HD1#':
      return ['HD11','HD12','HD13']
    elif name=='HD2#':
      if residue=='N':
        return ['HD21','HD22']
      else:
        return ['HD21','HD22','HD23']
    elif name=='HE#':
      if residue=='Q':
        return ['HE21','HE22']
      if residue=='M':
        return ['HE1','HE2','HE3']
      if residue=='W':
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

# EXPORT FUNCTION
# ===============
# THIS SCRIPT EXPORTS A FUNCTION GROUP OR CLASS TO A SEPARATE FILE.
# groupnames  IS A LIST OF NAMES OF THE GROUPS OR CLASSES TO EXPORT
# srcfilename IS THE PYTHON SCRIPT CONTAINING THE FUNCTION GROUP.
# dstfilename IS THE NAME OF THE NEW PYTHON MODULE.
# imports     IS A STRING WITH MODULES TO IMPORT IN dstfilename.
def nmv_export(groupnames,srcfilename,dstfilename,imports):
  print "Exporting ..."
  output = []
  for groupname in groupnames:
    print groupname
    # READ SOURCE
    src=open(srcfilename).readlines()
    # GET THE SPACED GROUP NAME
    spacedname=""
    for i in range(len(groupname)):
      spacedname=spacedname+groupname[i]+" "
    spacedname=spacedname[:-1]
    # SEARCH FOR GROUP
    i=0
    while (string.find(src[i+1],spacedname)==-1): i=i+1
    src=src[i:]
    # CONVERT AND PROCEED TILL END
    i=0
    while (string.strip(src[i])!="" or
           string.strip(src[i+1])!="#  ======================================================================"):
      line=src[i]
      i=i+1
    src=src[:i]
    output += src
  # ADD IMPORTS
  if (imports): output=["import "+imports+"\n","\n"]+output
  # SAVE
  open(dstfilename,"w").writelines(output)
  print "Done."

#  ======================================================================

#  =============================================================================
#   S U B S C R I P T  1:  N O N - E N S E M B LE   N M R   S T R U C T U R E S
#  =============================================================================
#
#  THIS SCRIPT EXTRACTS ALL THE ENERGY MINIMIZED AVERAGE NMR STRUCTURES FROM THE PDB
def nmv_pdbselnmrmin(filename):
  print "Select NMR structures with one model"
  print "===================================="
  # OPEN AND READ THE PDBFINDER
  pdbfinder = pdb_finder(nmvconf["PDBFINDER"],"r",0,error)
  pdbfinder.read()
  print 'Writing output'
  file = open(filename,'w')
  if (pdbfinder.error): error("PDBFINDER not found, no structure selection possible")
  # RETRIEVE ALL NMR STRUCTURES WITH 1 MODELS
  while not pdbfinder.eof:
    method = pdbfinder.fieldvalue('Exp-Method')
    no_models = pdbfinder.fieldvalue(' N-Models')
    # SELECT NMR
    if method=='NMR':
      # SELECT STRUCTURES WITH ONE MODEL OR NO N-MODELS TAG
      if ((no_models=='1') or (not no_models)):
        file.write(pdbfinder.fieldvalue('ID')+'\n')
    pdbfinder.read()
  # CLOSE THE OUTPUT FILE
  file.close()
  print 'Output written to: '+filename
  print 'Finished'


#  ===========================================================================
#   S U B S C R I P T  2:   D I S T R I B U T I O N   O F   N O   M O D E L S
#  ===========================================================================
#
# THIS SCRIPT GENERATES THE DISTRIBUTION OF THE NUMBER OF MODELS PER NMR STRUCTURE
def nmv_pdbselmoddist(filename):
  print "Create distribution of number of models in NMR files"
  print "===================================================="
  # OPEN AND READ THE PDBFINDER
  pdbfinder = pdb_finder(nmvconf["PDBFINDER"],"r",0,error)
  pdbfinder.read()
  count = 0
  if (pdbfinder.error): error("PDBFINDER not found, no structure selection possible")
  print 'Selecting structures'
  # OPEN THE OUTPUT FILE
  file = open(filename,'w')
  # DEFINE THE DICTIONARY
  mod_occ = {}
  # RETRIEVE ALL NMR STRUCTURES WITH 1 MODELS
  while not pdbfinder.eof:
    method = pdbfinder.fieldvalue('Exp-Method')
    no_models = pdbfinder.fieldvalue(' N-Models')
    # SELECT NMR
    if method=='NMR':
      # IF N-MODELS IS UNDEFINED, IT SHOULD BE EQUAL TO 1
      if not no_models:
        no_models = '1'
      # IF NOT PRESENT YET, ADD KEY TO DICTIONARY, OTHERWISE INCREASE IT'S VALUE BY 1
      count = count + 1
      if not mod_occ.has_key(no_models):
        mod_occ[no_models]=1
      else:
        mod_occ[no_models]=mod_occ[no_models]+1
    # READ THE NEXT PDBFINDER ENTRY
    pdbfinder.read()
  print 'Writing output'
  # WRITE THE DICTIONARY TO FILE
  for key in mod_occ.keys():
    file.write(key+'\t%i\n'%mod_occ[key])
  # CLOSE THE OUTPUT FILE
  file.close()
  print 'Output written to: '+filename
  print 'Finished'


#  ================================================================
#   S U B S C R I P T  3:  C R E A T E   D O C U M E N T A T I O N
#  ================================================================
#
# THIS SCRIPT USES HAPPYDOC TO CREATE HTML DOCUMENTATION
def nmv_createdoc(path):
  print "NMR_VALIBASE Documentation"
  print "=========================="
  srcfilename=sys.argv[0]
  # READ SOURCE
  print "Converting source file %s..." % srcfilename
  src=open(srcfilename,"r").readlines()
  # WRITE TEMPORARY SOURCE, SUITED FOR HAPPYDOC
  tmpfilename="_"+os.path.basename(srcfilename)
  tmpfile=open(tmpfilename,"w")
  commentflag=0
  docstringflag=0
  for line in src:
    line2=string.strip(line)
    if (len(line2) and line2[0]=='#'):
      # SKIP "# ========" LINES
      if (line2[3:]=='='*(len(line2)-3)):
        commentflag=0
        line=line[:string.find(line,'#')+1]+'\n'
        tmpfile.write(line)
        continue
      # IS IT A SUBSCRIPT?
      pos=string.find(line,"S U B S C R I P T")
      if (pos!=-1):
        pos2=string.find(line,':')
        line=line[:pos]+line[pos2+1:]
        i=0
        while (i<len(line)):
          if (line[i]==' ' and line[i+1] in string.letters+string.digits):
            line=line[:i]+line[i+1:]
          else: i=i+1
        i=1
        while (i<len(line)):
          if (line[i-1] in string.letters):
            line=line[:i]+string.lower(line[i])+line[i+1:]
          i=i+1
      else:
        # WRITE EMPTY COMMENT LINE
        if (string.find(line2," - ")!=-1):
          tmpfile.write('#\n')
          commentflag=0
        # CONVERT TO LOWERCASE
        line=string.lower(line)
        i=0
        while (i<len(line)):
          if (line[i] in string.letters and not commentflag):
            line=line[:i]+string.upper(line[i])+line[i+1:]
            commentflag=1
          # UPPERCASE AFTER DOTS
          elif (line[i]=='.' or line[i]==':'): commentflag=0
          i=i+1
    elif (not docstringflag): commentflag=0
    if (line2[0:3]=='"""'): docstringflag=docstringflag^1
    # WRITE OUTPUT
    # ADD EMPTY LINE BEFORE EACH DOCSTRING -
    if (docstringflag and len(line2) and line2[0]=='-'): tmpfile.write('\n')
    tmpfile.write(line)
  tmpfile.close()
  # RUN HAPPYDOC
  print "Running HappyDoc"
  sys.stdout.flush()
  os.system(nmvconf["HAPPYDOC_RUN"]+" -d %s -t NMR_Valibase "%path+tmpfilename)
  os.remove(tmpfilename)
  print "Finished"


#  ==================================================
#   S U B S C R I P T  4:  C R E A T E   B A C K U P
#  ==================================================
#
# THIS SCRIPT CREATES A BACKUP OF IMPORTANT DIRS ON THIS MACHINE
def nmv_backup(flag):
  # DEFINE THE LOGFILE
  logfile = '/tmp/backup.log'
  # OPEN THE FILE
  file = open(logfile,'w')
  # DO THE BACK-UPPING
  backup_path = '/mnt/backup/cmbipc58'
  cmbibackup_path = '/mnt/home15/cc/snabuurs/backup/cmbipc58'
  # WEEKLY BACKUP
  if flag=='weekly':
    # FULL HOMEDIR BACKUP
    bkp_copydir('/home/snabuurs',cmbibackup_path,file,'delete')
  # DAILY BACKUP
  if flag=='daily':
    # ESSENTIAL DATA
    #bkp_copydir('/home/snabuurs/python',backup_path,file)
    #bkp_targzdir('/home/snabuurs/laptop',backup_path,file)
    #bkp_targzdir('/home/snabuurs/projects',backup_path,file,'delete')
    # ESSENTIAL DATA TO CMBI1
    bkp_targzdir('/home/snabuurs/python',cmbibackup_path,file)
    bkp_targzdir('/home/snabuurs/laptop',cmbibackup_path,file)
    bkp_targzdir('/home/snabuurs/projects',cmbibackup_path,file,'delete')
    # SYSTEM DATA
    #bkp_targzdir('/etc',backup_path,file)
    #bkp_targzdir('/var/db/pkg',backup_path,file)
  # CLOSE THE FILE
  file.close()
  # MAIL THE CONTENTS OF THE LOGFILE
  eml_send('snabuurs@cmbi.kun.nl','%s backup logfile'%flag,open(logfile,'r').readlines())


#  ====================================================================
#   S U B S C R I P T  5:  C O U N T   P D B R E P O R T   E R R O R S
#  ====================================================================
#
# THIS SCRIPT COUNTS THE ERRORS IN summary.txt OF THE PDB REPORTS
def nmv_pdbrerrorcount():
  print "COUNTING ERRORS IN SUMMARY.TXT"
  print "==============================="
  errors, notes, warnings = 0, 0, 0
  # OPEN, READ AND CLOSE THE INPUT FILE
  file = open(nmvconf["PDBREPORT_SUMM"],'r')
  content = file.readlines()
  file.close()
  # COUNT THE SEPARATE TYPES
  for line in content:
    words = string.split(line)
    try:
      if words[2]=='Error:':
        errors = errors + int(words[0])
      if words[2]=='Warning:':
        warnings = warnings + int(words[0])
      if words[2]=='Note:':
        notes = notes + int(words[0])
    except:
      pass
  # WRITE THE OUTPUT TO SCREEN
  print "\nPDBREPORT ERRORS"
  print "================"
  print "Notes: \t\t\t%i"%notes
  print "Warnings: \t\t%i"%warnings
  print "Errors: \t\t%i"%errors
  print
  print "Errors+Warnings: \t%i"%(errors+warnings)
  print "Total: \t\t\t%i"%(notes+warnings+errors)


#  ===================================================================================
#   S U B S C R I P T  6: L I S T  T Y P E S   O F   P D B  R E P O R T   E R R O R S
#  ===================================================================================
#
# THIS SCRIPT SHOWS A LIST OF THE PDBREPORT ERRORS WITH THEIR ASSOCIATED REVINDEX NUMBERS
def nmv_pdbrerrorlist():
  print "LIST OF ALL PDBREPORT ERRORS"
  print "============================"
  # OPEN, READ AND CLOSE THE INDEX FILE
  file = open(nmvconf["PDBREPORT_INDEX"],'r')
  content = file.readlines()
  file.close()
  # PARSE THE FILE
  for line in content:
    # FIRST THE SELECT THE RIGHT LINES
    if line[0:4]=='<H3>':
      # DETERMINE THE TYPE (NOTE, ERROR, WARNING)
      type = string.split(line[:-1])[0][4:]
      # DETERMINE THE ERROR
      begin_title = string.find(line,':')+1
      end_title = string.find(line,'</H3>')
      error = line[begin_title:end_title]
      # DETERMINE THE REVINDEX NUMBER
      begin_number = string.find(line,'revindex')+len('revindex')
      end_number = string.find(line,'.html>')
      number = line[begin_number:end_number]
      # PRINT THE ERRORS TO SCREEN
      print '%3s %8s%s'%(number,type,error)


#  =====================================================================================
#   S U B S C R I P T  7: C O U N T   S E V E R A L   P D B   R E P O R T   E R R O R S
#  =====================================================================================
#
# THIS SCRIPT COUNTS PDB REPORT ERRORS. REGENERATES THE NUMBER FROM THE
# 'ERRORS IN PROTEIN STRUCTURES' ARTICLE IN NATURE (1996)
def nmv_errprotstruct(year):
  print "Generating table with error counts"
  print "==================================="
  res_sum = 0
  # CREATE AN INSTANCE OF THE PDBFINDER CLASS
  print 'Building PDBFINDER dictionary.'
  pdbfinder = pdb_finder(nmvconf["PDBFINDER"],"r",0,error)
  while not pdbfinder.eof:
    pdbfinder.read()
  # DO THE PDB SELECTION
  print "Selecting the PDB entries until %s."%year
  selected_pdb = pdb_selectx(0,100,1900,year)
  # BUILD THE PDB LIST WE ONLY TAKE ENTRIES WITH AN EXISTING PDBREPORT!
  print "Selecting PDB entries with an existing PDB report."
  pdrlist = []
  for pdb in selected_pdb.keys():
    pdb_low = string.lower(pdb)
    # CONSTRUCT THE PATH FOR THE PDBREPORT
    pdbr_path = nmvconf["PDBREPORT"]+'/'+pdb_low[1:-1]+'/'+pdb_low+'/index.html'
    # CHECK IF THE PDBREPORT EXISTS
    if os.path.exists(pdbr_path):
      pdrlist.append(pdb_low)
      res_sum = res_sum + pdbfinder.aas[pdb]
  # DETERMINE THE NUMBER OF RESIDUES IN THE PDB SELECTION
  print "Determined total number of structures : %i\n"%len(pdrlist)
  print "Determined total number of residues   : %i\n"%res_sum
  # CREATE AN INSTANCE OF THE ERROR CLASS
  errors = pdb_error(nmvconf["PDBREPORT_INDEX"],'all',error)
  print '\n========================================'
  print 'A FEW OF THE ERRORS IN THE LITERATURE...'
  print '\n========================================\n\n'
  # CHECK SYMMETRY INFORMATION
  # ERROR 35
  # =====================================================
  print 'Inconsistent symmetry information:'
  errors.finderrors('35')
  cases = 0
  for pdb in pdrlist:
    if pdb in errors.pdbswitherror:
      cases = cases + 1
  print '%i files'%cases
  # CHECK TRANSFORMATION MATRIX
  # ERROR 40
  # =====================================================
  print 'Transformation matrix has determinant not equal to one:'
  errors.finderrors('40')
  cases = 0
  for pdb in pdrlist:
    if pdb in errors.pdbswitherror:
      cases = cases + 1
  print '%i cases'%cases
  # CHECK FOR D-AMINO ACIDS
  # ERROR ???
  # =====================================================
  print 'D amino acids:'
  errors.finderrors('74')
  cases = 0
  for pdb in pdrlist:
    if pdb in errors.pdbswitherror:
      pdb_low = string.lower(pdb)
      # CONSTRUCT THE PATH FOR THE PDBREPORT
      pdbr_path = nmvconf["PDBREPORT"]+'/'+pdb_low[1:-1]+'/'+pdb_low+'/index.html'
      # OPEN THE PDBREPORT
      file = open(pdbr_path,'r')
      found,read = 0,0
      while (1):
        line=file.readline()
        if (line==""): break
        # SEARCH FOR CA DEVIATIONS
        if (line[0:8]=="<A NAME="):
          if (string.find(line,"Chirality deviations detected")!=-1): found=1
        elif (line[0:5]=="<PRE>" and found==1): read=1
        elif (line[-7:-1]=="</PRE>"): break
        elif (found and read):
          # ERROR FOUND SEE IF CA IS INVOLVED
          if line[23:25]=='CA':
            value = float(line[37:44])
            if value < 0:
              cases = cases + 1
      file.close()
  print '%i cases'%cases
  # CHECK FOR ATOMS TOO CLOSE TO SYMMETRY AXIS
  # ERROR 98
  # =====================================================
  print 'Atom too close to symmetry axis leading to a clash:'
  errors.findentriespdblist(pdrlist,'98')
  print '%i cases'%errors.entries
  # CHECK FOR WRONG SPACE GROUP
  # ERROR ???
  # =====================================================
  print 'Structure probably solved in wrong space group:'
  errors.finderrors('11')
  cases = 0
  for pdb in pdrlist:
    if pdb in errors.pdbswitherror:
      cases = cases + 1
  print '%i files'%cases
  # CHECK MATTHEWS COEFFICIENT
  # ERROR 20
  # =====================================================
  print "Much too high Matthew's coefficient (Vm > 7.0):"
  errors.finderrors('20')
  cases = 0
  for pdb in pdrlist:
    if pdb in errors.pdbswitherror:
      cases = cases + 1
  print '%i files'%cases
  # CHECK B-FACTOR OVERREFINEMENT
  # ERROR 96
  # =====================================================
  print "B-factors over-refined:"
  errors.finderrors('96')
  cases = 0
  for pdb in pdrlist:
    if pdb in errors.pdbswitherror:
      cases = cases + 1
  print '%i files'%cases
  # CHECK FOR CELL DIMENSION OFF BY MORE THAN 0.5%
  # ERROR ???
  # =====================================================
  print 'Structure probably solved in wrong space group:'
  errors.finderrors('107')
  cases = 0
  for pdb in pdrlist:
    if pdb in errors.pdbswitherror:
      cases = cases + 1
  print '%i files'%cases
  # CHECK OCCUPANCIES OUTSIDE THE 0.0 - 1.0 RANGE
  # ERROR 78
  # =====================================================
  print 'Atomic occupancies negative or larger than 1.0:'
  errors.findentriespdblist(pdrlist,'78')
  print '%i cases'%errors.entries
  # CHECK FOR BOND LENGTHS THAT DEVIATE MORE THAN 4 SIGMA
  # ERROR 102
  # =====================================================
  print 'Bond lengths that deviate more than 4 sigma:'
  errors.findentriespdblist(pdrlist,'102')
  print '%i cases'%errors.entries
  # CHECK FOR BOND ANGLES THAT DEVIATE MORE THAN 4 SIGMA
  # ERROR 111
  # =====================================================
  print 'Bond angles that deviate more than 4 sigma:'
  errors.findentriespdblist(pdrlist,'111')
  print '%i cases'%errors.entries
  # CHECK FOR BOND ANGLES THAT DEVIATE MORE THAN 4 SIGMA
  # ERROR 164
  # =====================================================
  print 'Side chain of His,Asn of Gln needs 180 degree flip:'
  errors.findentriespdblist(pdrlist,'164')
  print '%i cases'%errors.entries


#  ======================================================
#   S U B S C R I P T  8:  M E R G E   P D B   F I L E S
#  ======================================================
#
# THIS SCRIPT MERGES PDBFILES INTO ONE BIG FILE WITH MANY MODELS.
def nmv_mergepdb(pdblist,resultfilename):
  print "Compiling NMR model collection at %s..." % resultfilename
  yas_joinpdb(nmvconf["YASARA_RUN"],pdblist,resultfilename)
  print "Finished.."


#  ==========================================================
#   S U B S C R I P T  9:  R E N U M B E R   P D B   F I L E
#  ==========================================================
#
# THE SCRIPT RENUMBERS A PDB FILE TO MAKE IT IDENTICAL TO THE ATOM NUMBERING IN THE
# NUMBERS_PDB FILE
def nmv_renumberpdb(numbers_pdb, in_pdb, out_pdb):
  print 'Renumbering pdb file %s according to %s.'%(in_pdb,numbers_pdb)
  print 'Output to pdb file %s'%out_pdb
  n_atom_sum, i_atom_sum = 0,0
  n_topology, i_topology = {}, {}
  # READ THE FILE WITH THE ORIGINAL NUMBERS
  file = open(numbers_pdb,'r')
  n_content = file.readlines()
  file.close()
  models, read = 0, 1
  for line in n_content:
    if line[0:5]=='MODEL':
      models+=1
      if models > 1:
        read = 0
    if line[0:4]=='ATOM' and models==0:
      models+=1
    # READ THE ATOMLIST
    if line[0:4]=='ATOM' and read:
      n_atom_sum += 1
      res_name = line[17:20]
      atom = line[11:17]
      res_num = int(line[22:26])
      atom_num = int(line[4:11])
      n_topology[atom_num] = {}
      n_topology[atom_num]['atom'] = atom
      n_topology[atom_num]['residue'] = res_name
      n_topology[atom_num]['res_num'] = res_num
  # CREATE LIST OF ATOM NUMBERS
  n_atom_nums = n_topology.keys()
  n_atom_nums.sort()
  print 'The reference system has %i atoms.'%(n_atom_sum)
  # READ THE FILE THAT HAS TO BE CONVERTED
  file = open(in_pdb,'r')
  i_content = file.readlines()
  file.close()
  m_found, models = 0,0
  for line in i_content:
    if line[0:5]=='MODEL':
      models+=1
      m_found=1
    if line[0:4]=='ATOM' and not m_found:
      models+=1
      m_found=1
  for line in i_content:
    # READ THE ATOMLIST
    if line[0:4]=='ATOM':
      i_atom_sum += 1
      res_name = line[17:20]
      atom = line[11:17]
      res_num = int(line[22:26])
      atom_num = int(line[4:11])
      i_topology[atom_num] = {}
      i_topology[atom_num]['atom'] = atom
      i_topology[atom_num]['residue'] = res_name
      i_topology[atom_num]['res_num'] = res_num
  # CREATE LIST OF ATOM NUMBERS
  i_atom_nums = i_topology.keys()
  i_atom_nums.sort()
  print 'The input system has %i atoms in %i models (%i atoms per model).'%(i_atom_sum,models,int(i_atom_sum/float(models)))
  if (int(i_atom_sum/float(models))) == n_atom_sum:
    file = open(out_pdb,'w')
    for line in i_content:
      sline = string.split(line)
      if sline[0]=='ATOM':
        atom_num = int(sline[1])
        for num in n_topology.keys():
          if i_topology[atom_num]['atom']==n_topology[num]['atom'] and i_topology[atom_num]['res_num']==n_topology[num]['res_num']:
            new_num = num
        newline = string.replace(line,'ATOM%7i'%atom_num,'ATOM%7i'%new_num)
        file.write(newline)
      else:
        file.write(line)
    file.close()
  else:
    print 'The two pdbfiles have a different number of atoms per model!'


#  ======================================================================
#   S U B S C R I P T  10: G E N E R A T E   S I M U L A T E D   N O E S
#  ======================================================================
#
# THE SCRIPT GENERATE SIMULATED NOE DISTANCE RESTRAINTS FROM A PDB FILE
def nmv_createnoes(inpdb,outnoe,cutoff,errorbound):
  # READ THE PDB FILE
  file = open(inpdb,'r')
  content = file.readlines()
  file.close()
  # OPEN THE OUTPUT FILE
  file = open(outnoe,'w')
  # GO THROUGH THE INPUT FILE
  atom = {}
  for line in content:
    if (line[0:4]=='ATOM') and ('H' in line[11:17]) and (line[11:17] not in ['CH2','NH1','NH2','OH']):
      fatom = int(line[4:11])
      atom[fatom]={}
      atom[fatom]['name']=line[11:17]
      atom[fatom]['x']=float(line[30:38])
      atom[fatom]['y']=float(line[38:46])
      atom[fatom]['z']=float(line[46:54])
      atom[fatom]['id']=line[22:26]
  # CALCULATE THE DISTANCES
  for key1 in atom.keys():
    for key2 in atom.keys():
      if key2 > key1:
        distance = math.sqrt((atom[key1]['x']-atom[key2]['x'])**2+(atom[key1]['y']-atom[key2]['y'])**2+(atom[key1]['z']-atom[key2]['z'])**2)
        if distance < cutoff:
          bound = float(errorbound)/100*distance
          file.write("assign ( resid %3s and name %4s ) ( resid %3s and name %4s )  %.3f %.3f %.3f !\n"%(atom[key1]['id'],atom[key1]['name'],atom[key2]['id'],atom[key2]['name'],distance,bound,bound))
  file.close()


#  ======================================================================
#   S U B S C R I P T  11: E X T R A C T   A N D   F O R M A T   N O E S
#  ======================================================================
#
# REFORMAT NOES AND REMOVE DOUBLE ASSIGNMENTS
def nmv_reformatrestraints(innoe,outnoe,type,informat='XPLOR',outformat='XPLOR'):
  print "Reformatting NOE table:"
  print "%s"%innoe
  rfile_check(innoe,outnoe,type,informat,outformat)
  print "Reformatted NOE table:"
  print "%s"%outnoe
  print "Done"


#  ====================================================
#   S U B S C R I P T  12: V I S U A L I Z E   N O E S
#  ====================================================
#
# THIS SCRIPT CREATES AN INPUT FILE FOR YASARA TO VISUALIZE
# NOES IN A STRUCTURES
def nmv_visualizenoes(projectname,datasetlist,pdbfile,cutoff=10000):
  print "Creating YASARA macro."
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],"che_%s"%datasetlist))
  rfile_visualize(tblpath,pdbfile,nmvconf["YASARA_RUN"],cutoff)
  print "Done."


#  ====================================================
#   S U B S C R I P T  13: A V E R A G E   C O L U M N
#  ====================================================
#
#  AVERAGE THE GIVEN COLUM IN THE GIVEN FILE
def nmv_avecolumn(filename,column):
  value = avg_filecolumn(filename,column)
  print "Averaging column %i of file %s"%(column,filename)
  print "Average: %.2f +/- %.2f"%(value[0],value[1])


#  ==================================================
#   S U B S C R I P T  14: E X T R A C T   M O D E L
#  ==================================================
#
#  EXTRACT THE GIVEN MODEL FROM THE GIVEN MULTI-MODEL PDB FILE
#  THE ORIGINAL HEADER WILL BE INCLUDED IN THE NEW FILE.
def nmv_extractmodel(inpdbfile,outpdbfile,model):
  print 'Extracting model %i from %s.'%(model,inpdbfile)
  # CREATE INSTANCE OF PDBFile
  inpdb = pdb_file.PDBFile(inpdbfile)
  outpdb = pdb_file.PDBFile(outpdbfile, mode='w')
  # READ THE FIRST LINE
  line = inpdb.readLine()
  model_found = 0
  while 1:
    # WRITE THE HEADER
    if line[0]=='HEADER':
      outpdb.writeLine(line[0],line[1])
    # CHECK THE MODEL NUMBER
    if line[0]=='MODEL':
      if line[1]['serial_number']==model:
        outpdb.writeLine(line[0],line[1])
        model_found = 1
      else:
        model_found = 0
    # WRITE COORDINATES FOR THE ATOMS
    if line[0]=='ATOM' and model_found:
      outpdb.writeLine(line[0],line[1])
    line = inpdb.readLine()
    if line[0]=='END': break
  print 'Wrote output to %s.'%outpdbfile
  print 'Done.'


#  ===========================================================
#   S U B S C R I P T  16:  C H E C K   S O U R C E   C O D E
#  ===========================================================
#
# THIS SCRIPT CHECKS THE WHAT_MODELBASE SOURCE CODE FOR ERRORS.
def nmv_checksource():
  print "NMR_VALIBASE Source Code Check"
  print "=============================="
  # RUN PyChecker
  srcfilename=sys.argv[0]
  chkfilename=dsc_tmpfilename("pychecker_output")
  os.system("pychecker -R 50 -L 3000 -B 1000 -J 1000 -5 1000 -K 1000 "+srcfilename+" >"+chkfilename)
  # FILTER ERROR MESSAGES
  src=open(srcfilename,"r").readlines()
  chk=open(chkfilename,"r").readlines()
  dsc_remove(chkfilename)
  for chkline in chk:
    chkline=string.strip(chkline)
    skipwarning=0
    pos=string.find(chkline,": Local variable")
    if (pos!=-1 and chkline[-8:]=="not used"):
      # SKIP WARNING ABOUT UNUSED LOOP VARIABLE
      srclineno=int(chkline[string.find(chkline,':')+1:pos])
      varname=chkline[string.find(chkline,'(')+1:string.rfind(chkline,')')]
      srcline=string.strip(src[srclineno-1])
      if (srcline[:14+len(varname)]=="for "+varname+" in range("): skipwarning=1
    # PRINT WARNING IF OK
    if (not skipwarning): print chkline
  print "Finished"


#  ===============================================
#   S U B S C R I P T  17:  A N A L Y Z E   P D B
#  ===============================================
#
# THIS SCRIPT SELECTS PDB STRUCTURES
def nmv_analysepdb(pdbfinderpath,plotpath,expmethod,yearstart,yearstop):
  # THE COMPLET SET OF CHECKS
  checks={ "Bonds"      : "  Bonds",
           "Angles"     : "  Angles",
           "Torsions"   : "  Torsions",
           "PhiPsi"     : "  Phi/psi",
           "Planarity"  : "  Planarity",
           "Chirality"  : "  Chirality",
           "Backbone"   : "  Backbone",
           "Peptplan"   : "  Peptide-Pl",
           "Rotamer"    : "  Rotamer",
           "Chi1chi2"   : "  Chi-1/chi-2",
           "Bumps"      : "  Bumps",
           "Packing1"   : "  Packing 1",
           "Packing2"   : "  Packing 2",
           "Inout"      : "  In/out",
           "Hbonds"     : "  H-Bonds",
           "Flips"      : "  Flips"}
  # ALL TWENTY RESIDUES
  residues={ "Pro":"P", "Gly":"G", "Ala":"A", "Arg":"R",
             "Asn":"N", "Asp":"D", "Cys":"C", "Gln":"Q",
             "Glu":"E", "His":"H", "Ile":"I", "Leu":"L",
             "Lys":"K", "Met":"M", "Phe":"F", "Ser":"S",
             "Thr":"T", "Trp":"W", "Tyr":"Y", "Val":"V" }
  print residues
  # THE CHECKS DONE ON A PER RESIDUE BASIS
  reschecks = {"Planarity": "  Planarity"}
  # THE RESIDUES WITH PLANAR GROUPS
  planres = {"Asp":"D", "Glu":"E", "Phe":"F", "His":"H",
             "Asn":"N", "Gln":"Q", "Arg":"R", "Trp":"W",
             "Tyr":"Y"}
  # THE CHECKS DONE FOR EACH REF. PROGRAM
  progchecks = {"Packing2":"  Packing 2",
                 "Bonds"  : "  Bonds",
                 "Angles"  : "  Angles",
                 "Bumps"  : "  Bumps",
                 "Packing1"  : "  Packing 1",
                 "Backbone" : "  Backbone",
                 "PeptidePl" : "  Peptide-Pl",
                 "Chi12" : "  Chi-1/chi-2"}
  # THE NUMBER STRUCTURES THAT HAVE TO BE ANALYZED
  # FOR A REF. PROG TO BE TAKEN INTO ACCOUNT
  prog_cutoff = {"X": 100, "NMR": 25}
  # THE PATH FOR ALL PLOTS
  plotpath = "%s%s/"%(plotpath,expmethod)

  # INDEX THE PDBFINDER
  #####################
  print 'Indexing PDBFINDER2.'
  # CREATE PDBFINDER INSTANCE
  indexpath = '/tmp/pdbfinder2.ind'
  pdbfinder = pdb_finder(pdbfinderpath,'r',1,error,indexpath)
  pdbfinder.buildindex()
  print '%i structures have been indexed.'%len(pdbfinder.recordpos.keys())

  # SELECT STRUCTURES WITH DESIRED METHOD
  # AND SOLVED BETWEEN THE DEFINED YEARS
  #######################################
  print 'Selecting %s structures, solved between %i and %i.'%(expmethod,yearstart,yearstop)
  structures = {}
  # GO TROUGH ALL ENTRIES
  for structure in pdbfinder.recordpos.keys():
    # READ THE ENTRY
    pdbfinder.read(structure)
    pdbyear = int(pdbfinder.fieldvalue(" Date")[:4])
    pdbmonth = int(pdbfinder.fieldvalue(" Date")[5:7])
    # CHECK FOR YEAR
    if pdbyear >= yearstart and pdbyear <= yearstop:
      # CHECK FOR METHOD
      if pdbfinder.fieldvalue("Exp-Method")==expmethod:
        # CREATE KEY IN STRUCTURES DICTIONARY
        structures[structure]={}
        # STORE YEAR & MONTH
        structures[structure]["year"]=pdbyear
        structures[structure]["month"]=pdbmonth
        structures[structure]["resolution"]=pdbfinder.resolution[structure]
        # STORE REFINEMENT PROGRAM
        if pdbfinder.fieldvalue("Ref-Prog"):
          structures[structure]["refprog"]=pdbfinder.fieldvalue("Ref-Prog")
        # STORE NUMBER AND TYPE OF RESIDUE
        structures[structure]["aas"]=pdbfinder.aas[structure]
        structures[structure]["nucs"]=pdbfinder.nucs[structure]
  print 'Found %i matching %s structures.'%(len(structures.keys()),expmethod)

  # TMP
  #######################################
  check = " Quality"
  dict = {}
  resdict = {}
  fileq = open('quality.dat','w')
  # CYCLE ALL STRUCTURES
  for structure in structures.keys():
    # READ THE STRUCTURE
    pdbfinder.read(structure)
    scores = []
    # THE STRUCTURE MOST CONTAIN AMINOACIDS
    if pdbfinder.aas[pdbfinder.id]>0:
      # CYCLE THE CHAINS
      for chain in pdbfinder.chainlist:
        # THERE HAVE TO BE AT LEAST 50 AMINOACIDS
        # 1e91 IS EXCLUDED
        if len(pdbfinder.chainseq[chain])>50 and pdbfinder.id!='1e91':
          # CHECK IS THE CHECK IS PRESENT
          if pdbfinder.qualstr[chain].has_key(check):
            score = pdbfinder.qualstr[chain][check]
            # TRY TO CONVERT THE SCORE
            try:
              score = float(score)
              # IF SCORE IS ONE, THE IS SOMETHING SUSPICIOUS
              if score == 1.0:
                print "%s\t%s\t%s\t%s"%(pdbfinder.id,chain,check,score)
              else:
                scores.append(score)
            # IF CONVERSION FAILS, THERE IS A BUG
            except:
              print "%s\t%s\t%s\t%s"%(pdbfinder.id,chain,check,score)
      # IF WE FOUND ANY SCORE
      if len(scores)>0:
        fileq.write("%5.3f\t%s\t%s\n"%(avg_list(scores)[0],pdbfinder.id,pdbfinder.fieldvalue("Exp-Method")))

        if structures[structure]["resolution"] < 4.0:
          # ADD THE SCORE TO EVERY RESO DICTIONARY
          res = "%3.1f"%structures[structure]["resolution"]
          resdict[res]=resdict.get(res,[])+[avg_list(scores)[0]]
  # WRITE THE LOGFILE
  logfile = open('res_vs_quality.dat','w')
  for res in resdict.keys():
    avg = avg_list(resdict[res])
    logfile.write("%s\t%4.2f\t%4.2f\n"%(res,avg[0],avg[1]))
  logfile.close()
  fileq.close()

  # TMP
  #######################################
  check = " Quality"
  dict = {}
  yeardict = {}
  # CYCLE ALL STRUCTURES
  for structure in structures.keys():
    # READ THE STRUCTURE
    pdbfinder.read(structure)
    scores = []
    # THE STRUCTURE MOST CONTAIN AMINOACIDS
    if pdbfinder.aas[pdbfinder.id]>0:
      # CYCLE THE CHAINS
      for chain in pdbfinder.chainlist:
        # THERE HAVE TO BE AT LEAST 50 AMINOACIDS
        # 1e91 IS EXCLUDED
        if len(pdbfinder.chainseq[chain])>50 and pdbfinder.id!='1e91':
          # CHECK IS THE CHECK IS PRESENT
          if pdbfinder.qualstr[chain].has_key(check):
            score = pdbfinder.qualstr[chain][check]
            # TRY TO CONVERT THE SCORE
            try:
              score = float(score)
              # IF SCORE IS ONE, THE IS SOMETHING SUSPICIOUS
              if score == 1.0:
                print "%s\t%s\t%s\t%s"%(pdbfinder.id,chain,check,score)
              else:
                scores.append(score)
            # IF CONVERSION FAILS, THERE IS A BUG
            except:
              print "%s\t%s\t%s\t%s"%(pdbfinder.id,chain,check,score)
      # IF WE FOUND ANY SCORE
      if len(scores)>0:
        # ADD THE SCORE TO EVERY AUTHORS DICTIONARY
        for author in pdbfinder.authors:
          author = string.upper(author)
          dict[author]=dict.get(author,[])+[avg_list(scores)[0]]
          year = structures[structure]["year"]
          yeardict[year]=yeardict.get(year,{})
          yeardict[year][author]=yeardict[year].get(author,[])+[avg_list(scores)[0]]
  # WRITE THE SECOND FILE
  author = "A.BAX"
  logfile2 = open('year_%s.dat'%author,'w')
  for year in yeardict.keys():
    avg = avg_list(yeardict[year].get(author,[]))
    logfile2.write("%i\t%4.2f\t%4.2f\n"%(year,avg[0],avg[1]))
  logfile2.close()
  # WRITE THE LOGFILE
  logfile = open('%s_author.dat'%expmethod,'w')
  for author in dict.keys():
    avg = avg_list(dict[author])
    # WE ONLY TAKE AUTHORS WITH A GIVEN NUMBER OF STRUCTURES
    if len(dict[author])>=10 or (avg[0]>0.55 and len(dict[author])>=5):
      logfile.write("%20s-%i\t%4.2f\t%4.2f\t%i\n"%(author,len(dict[author]),avg[0],avg[1],len(dict[author])))
  logfile.close()

  check = " Quality"
  dict = {}
  for structure in structures.keys()[10]:
    pdbfinder.read(structure)
    for chain in pdbfinder.chainlist:
      if pdbfinder.qualstr[chain].has_key(check):
        score = pdbfinder.qualstr[chain][check]
        if score != "0.00":
          try:
            year = structures[structure]["year"]
            dict[year]=dict.get(year,[]) + [float(score)]
          except:
            pass
  logfile = open('zut2.dat','w')
  for key in dict.keys():
    avg = avg_list(dict[key])
    logfile.write("%s\t%4.2f\t%4.2f\n"%(key,avg[0],avg[1]))
  logfile.close()

  # AVERGE THE CHECKS OVER ALL MATCHING STRUCTURES
  ################################################
  checks_avg = {}
  # OPEN THE PLOTFILE
  filename = plotpath+"all_checks.dat"
  file=open(filename,'w')
  # CYCLE THE DESIRED CHECKS
  for check in checks.keys():
    checks_avg[check]={}
    scorelist = []
    for structure in structures.keys():
      # READ THE ENTRY
      pdbfinder.read(structure)
      # CYCLE THE DIFFERENT CHAINS
      for chain in pdbfinder.chainlist:
        # CHECK IF THE CHECK RESULT EXISTS
        if pdbfinder.qualstr[chain].has_key(checks[check]):
          # EXTRACT THE AVERAGE SCORE
          # THIS SCORE SCALES FROM 0.0 (BAD) TO 1.0 (GOOD)
          erravg=float(string.split(pdbfinder.qualstr[chain][checks[check]],'|')[1])
          scorelist.append(erravg)
    # AVERAGE ALL SCORES FOR THIS CHECK
    checks_avg[check]["Average"]=avg_list(scorelist)
    checks_avg[check]["N-entries"]=len(scorelist)
    # WRITE TO FILE
    file.write("Check %10s\taverage %6.2f +/- %6.2f from %5i chains.\n"%(check,checks_avg[check]["Average"][0],checks_avg[check]["Average"][1],checks_avg[check]["N-entries"]))
  file.close()

  # CALCULATE AVERAGE PER YEAR IN THE DEFINED YEARS
  #################################################
  years = range(yearstart,yearstop+1)
  # DEFINE DICTIONARIES
  year_avg={}
  for year in years:
    year_avg[year]={}
    year_avg[year]["structures"]=[]
  # SORT THE STRUCTURES BY YEAR
  for structure in structures.keys():
    if year_avg.has_key(structures[structure]["year"]):
      year_avg[structures[structure]["year"]]["structures"].append(structure)
  # AVERAGE THE CHECKS FOR EVERY YEAR
  # CYCLE THE CHECKS
  for check in checks.keys():
    # OPEN THE CHECK SPECIFIC FILE
    filename = "%s%i-%i_%s.dat"%(plotpath,yearstart,yearstop,check)
    file=open(filename,'w')
    # CYCLE THROUGH THE YEARS
    for year in years:
      year_avg[year][check]={}
      scorelist = []
      # CYCLE THROUGH THE STRUCTURES
      for structure in year_avg[year]["structures"]:
        # READ STRUCTURE
        pdbfinder.read(structure)
        # CYCLE THE DIFFERENT CHAINS
        for chain in pdbfinder.chainlist:
          # CHECK IF THE CHECK RESULT EXISTS
          if pdbfinder.qualstr[chain].has_key(checks[check]):
            # EXTRACT THE AVERAGE SCORE
            # THIS SCORE SCALES FROM 0.0 (BAD) TO 1.0 (GOOD)
            erravg=float(string.split(pdbfinder.qualstr[chain][checks[check]],'|')[1])
            scorelist.append(erravg)
      # WE CALCULATE THE AVERAGE IF HITS HAVE BEEN FOUND
      year_avg[year][check]["Average"]=avg_list(scorelist)
      year_avg[year][check]["N-entries"]=len(scorelist)
      # WRITE TO LOG FILE
      file.write("%4i\t%8.2f\t%8.2f\t%8i\n"%(year,year_avg[year][check]["Average"][0],year_avg[year][check]["Average"][1],year_avg[year][check]["N-entries"]))
    file.close()

  # CHECK PLANARITY ON A PER RESIDUE BASIS
  ########################################
  # CYCLE THE PER RESIDUE CHECKS
  for check in reschecks:
    # CYCLE THE RESIDUES
    # !!! ONLY PLANAR RESIDUES ARE CYCLED !!!
    for res in planres.keys():
      # OPEN PLOTFILE
      filename = "%s%s_%s.dat"%(plotpath,res,check)
      file = open(filename,'w')
      # CYCLE THE YEARS
      for year in years:
        avglist=[]
        # CYCLE THE STRUCTURES FOR THE GIVEN YEAR
        for structure in year_avg[year]["structures"]:
          # READ STRUCTURE
          pdbfinder.read(structure)
          # GO THROUGH THE DIFFERENT CHAINS
          for chain in pdbfinder.chainlist:
            # CHECK IF THE QUALITY EXISTS FOR THAT CHAIN
            if pdbfinder.qualstr[chain].has_key(reschecks[check]):
              errstr=string.split(pdbfinder.qualstr[chain][reschecks[check]],'|')[0]
              # CHECK IF ERROR LENGTH MATCH SEQUENCE LENGTH
              if len(errstr)!=len(pdbfinder.chainseq[chain]):
                print "#############################################"
                print "Error string differs in length from sequence!"
                print pdbfinder.id, chain
                print "#############################################"
              # EXTRACT THE RELEVANT ERROR CODES
              for i in range(len(errstr)):
                if pdbfinder.chainseq[chain][i]==planres[res]:
                  if errstr[i] in string.digits:
                    avglist.append(int(errstr[i]))
        # CALCULATE THE AVERAGE OVER THE WHOLE YEAR
        avg=avg_list(avglist)
        # WRITE LOG FILE
        file.write("%i\t%8.2f\t%8.2f\t%i\n"%(year,avg[0],avg[1],len(avglist)))
      file.close()

  # CHECK DIFFERENT REFINEMENT PROGRAMS
  #####################################
  # CYCLE THE CHECK
  for check in progchecks:
    progscores = {}
    # CYCLE SELECTED STRUCTURES
    for key in structures.keys():
      # READ STRUCTURE
      pdbfinder.read(key)
      # IF REFINEMENT PROGRAM IS KNOWN
      if pdbfinder.refprog:
        # CREATE DICT KEY IF NECESSARY
        if not progscores.has_key(pdbfinder.refprog):
          progscores[pdbfinder.refprog]={ "scores":[],
                                          "structures":0 }
        # GO THROUGH THE CHAINS
        for i in range(len(pdbfinder.chainlist)):
          chain = pdbfinder.chainlist[i]
          # CHECK IF THE CHECK EXISTS
          if pdbfinder.qualstr[chain].has_key(progchecks[check]):
            # INCREASE THE COUNTER WITH ONE IF FIRST CHAIN
            if i==0: progscores[pdbfinder.refprog]["structures"]+=1
            # READ THE ERROR AVERAGE
            erravg=string.split(pdbfinder.qualstr[chain][progchecks[check]],'|')[1]
            # ADD THE SCORE
            progscores[pdbfinder.refprog]["scores"].append(float(erravg))
    # OPEN OUTPUT FILE
    filename = "%s%s_refprog.dat"%(plotpath,check)
    file=open(filename,'w')
    # WRITE AVG SCORES
    for key in progscores.keys():
      # AVERAGE THE SCORES
      avg = avg_list(progscores[key]["scores"])
      # WRITE TO FILE IF WE HAVE MORE STRUCTURES THEN THE DEFINED CUTOFF
      if progscores[key]["structures"]>prog_cutoff[expmethod]:
        file.write("%20s\t%8.2f\t%8.2f\t%i\t%i\n"%(key,avg[0],avg[1],progscores[key]["structures"],len(progscores[key]["scores"])))
    file.close()


#  =======================================================================
#   S U B S C R I P T  18:  G E N E R A T E   P S F  &  S T R U C T U R E
#  =======================================================================
#
# THIS SCRIPT GENERATES A PSF AND STUCTURE FILE FROM SEQUENCE OR COORDINATES
def nmv_generatepsf(projectname,inputfile,type="sequence"):
  print "Generating PSF and stucture files."
  print "=================================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  # GET THE INPUT FILE
  inputfile = nmv_adjust(nmvconf["NMRI_SEQ"],inputfile)
  inputfile = os.path.join(path,inputfile)
  # CHECK FOR PATCHES
  patchfile = os.path.join(path,nmvconf["NMRI_PATCHES"])
  patches = nmrinfo_readpatches(patchfile)
  # CHECK FOR DISULFIDES
  disulfidefile = os.path.join(path,nmvconf["NMRI_DISULFIDES"])
  patches["DISU"] = nmrinfo_readdisulfides(disulfidefile)
  # BUILD THE PSF FILE
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  xplor_buildstructure(psffile,inputfile,base=type,patches=patches)
  # BUILD THE PSF FILE
  pdbfile = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  xplor_generatetemplate(pdbfile,psffile)
  print "Finished."


#  ===================================================================
#   S U B S C R I P T  19:  C A L C U L A T E   U N C E R T A I N T Y
#  ===================================================================
#
# THIS SCRIPT GENERATE A PLOT WHICH DISPLAYS THE DECREASE IN UNCERTAINTY
# AS EXPERIMENTAL DATA IS ADDED TO THE SYSTEM.
def nmv_plotuncertainty(projectname,datasetlist):
  print "Calculating decrease in uncertainty."
  print "===================================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  # SET SOME DEFAULT VARS
  logpath = dsc_tmpdir(os.path.join(path,nmvconf["NMRI_LOG"]))
  dmtx = os.path.join(logpath,nmvconf["NMRI_TEMPMTX"])
  template = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  xplr = nmvconf["XPLOR"]
  para = nmvconf["NMRI_PAR"]
  # SET THE DATAFILE PATH
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  # SET THE LOGFILE
  plotfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"unc_%s"%datasetlist))
  # READ THE DATASET DESCRIPTION FILE
  set = nmrinfo_readdatafile(dataset)
  print "Found %i datafiles in dataset."%len(set)
  # KEEP AN OVERALL RESTRAINT COUTNER
  rcount = 0
  # SET THE PSF FILE PATH
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  # DEFINE THE PLOT FILE
  xmgr = graceplot(plotfile,'xy','w')
  xmgr.xlab = "number of restraints"
  xmgr.ylab = "information (%)"
  xmgr.writeheader()
  # INITIALIZE NMRINFO CLASS FOR BACKGROUND UNCERTAINTY
  ini_unc = nmr_info()
  unc = ini_unc.calcsetunc(xplr,para,psffile,{},dmtx,logpath,template)
  xmgr.write([rcount,unc])
  ini_unc.freemem()
  memoset = {}
  # CYCLE THE DATAFILE
  for filedict in set:
    xmgr.comment(filedict["NAME"])
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    # TAKE CARE OF THE RESTRAINTS
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # CYCLE THE RESTRAINTS
    for i in range(len(r.restraintlist)):
      # INITIALIZE NMRINFO CLASS FOR BACKGROUND UNCERTAINTY
      new_unc = nmr_info()
      rdict = {}
      rdict[filedict["TYPE"]]=r.restraintlist[:i+1]
      for mkey in memoset.keys():
        if rdict.has_key(mkey): rdict[mkey]+=memoset[mkey]
        else: rdict[mkey]=memoset[mkey]
      unc = new_unc.calcsetunc(xplr,para,psffile,rdict,dmtx,logpath,template)
      xmgr.write([i+1+rcount,unc,str(r.restraintlist[i])])
      new_unc.freemem()
    # REMEMBER SET
    if memoset.has_key(filedict["TYPE"]): memoset[filedict["TYPE"]]+=r.restraintlist
    else: memoset[filedict["TYPE"]]=r.restraintlist
    # RAISE THE RESTRAINT COUNTER
    rcount+=len(r.restraintlist)
  xmgr.close()
  print 'Removing temporary files.'
  dsc_rmdir(logpath)
  print "Finished."


#  ===================================================================
#   S U B S C R I P T  20:  C A L C U L A T E   I N F O R M A T I O N
#  ===================================================================
#
# THIS SCRIPT CALCULATES THE INFORMATION CONTENT OF EACH OF THE
# INDIVIDUAL RESTRAINTS IN AN NMR DATASET WITH RESPECT TO THE REMAINDER
# OF THE DATASET
# THIS SCRIPT IS PARALLELLIZABLE! USE EG. MPIRUN -NP 2 NMR_VALIBA.....
def nmv_restraintinformation(projectname,datasetlist):
  if myid==0:
    print "Calculating restraint information."
    print "=================================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  logpath = dsc_tmpdir(os.path.join(path,nmvconf["NMRI_LOG"]))
  # SET SOME DEFAULT VARS
  dmtx = os.path.join(logpath,nmvconf["NMRI_TEMPMTX"])
  template = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  xplr = nmvconf["XPLOR"]
  para = nmvconf["NMRI_PAR"]
  # SET THE DATAFILE PATH
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  # SET THE LOGFILE
  plotfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"inf_%s"%datasetlist))
  # READ THE DATASET DESCRIPTION FILE
  setlist = nmrinfo_readdatafile(dataset)
  if myid==0: print "Found %i datafiles in dataset."%len(setlist)
  # KEEP AN OVERALL RESTRAINT COUTNER
  rcount = 1
  # SET THE PSF FILE PATH
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  # WE ONLY CREATE A LOGFILE ON THE MASTER CPU
  if myid==0:
    xmgr = graceplot(plotfile,'xy','w')
    xmgr.title = "Restraint information"
    xmgr.xlab = "Restraint index"
    xmgr.ylab = "Fraction of total information (%)"
    xmgr.writeheader()
  # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
  fulldict = {}
  # CYCLE ALL AVAILABLE SETS
  for filedict in setlist:
    # CREATE A KEY IN THE DICTIONARY
    if not fulldict.has_key(filedict["TYPE"]):
      fulldict[filedict["TYPE"]] = []
    # CONSTRUCT THE TABLE PATH
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    # READ THE TABLE
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # STORE PARSED RESTRAINTS FOR FUTURE USE
    filedict["DATA"] = r.restraintlist
    fulldict[filedict["TYPE"]]+=r.restraintlist
  # INITIALIZE NMRINFO CLASS FOR BACKGROUND UNCERTAINTY
  bg_unc = nmr_info()
  bgunc = bg_unc.calcsetunc(xplr,para,psffile,{},dmtx,logpath,template)
  bg_unc.freemem()
  # INITIALIZE NMRINFO CLASS FOR FULL UNCERTAINTY
  full_unc = nmr_info()
  fullunc = full_unc.calcsetunc(xplr,para,psffile,fulldict,dmtx,logpath,template)
  full_unc.freemem()
  allinfo = bgunc-fullunc
  # A LIST IN WHICH WE JOIN ALL DATAPOINTS
  slist = []
  # AN OVERALL COUNTER
  rcount = 1
  # GO THROUGH ALL SETS AND DELETE THE RESTRAINTS ONE BY ONE
  for i in range(len(setlist)):
    # SET THE RANGE FOR MPI RUNS
    mylower,myupper=mpi_setrange(setlist[i]["DATA"],queen.myid,queen.numproc)
    print "Submitted %i restraints to CPU %i of %i."%(myupper-mylower,myid+1,numproc)
    # CALCULATE RESTRAINTINFO
    for k in range(mylower,myupper):
      # CLEAN THE DICTIONARY
      rdict = {}
      for set in setlist: rdict[set["TYPE"]]=[]
      for j in range(len(setlist)):
        # DELETE THE DESIRED RESTRAINT
        if i==j:
          templist = copy.copy(setlist[j]["DATA"])
          restraint = templist[k]
          del templist[k]
          rdict[setlist[j]["TYPE"]]+=templist
        # ADD THE REST OF THE DATA IN THE DATASET
        else:
          rdict[setlist[j]["TYPE"]]+=setlist[j]["DATA"]
      filedict = setlist[j]
      # DETERMINE THE INFO
      new_unc = nmr_info()
      unc = new_unc.calcsetunc(xplr,para,psffile,rdict,dmtx,logpath,template)
      # CALCULATE THE INFORMATION THE GIVEN RESTRAINT
      info = unc-fullunc
      slist.append([rcount+k,(info/allinfo)*100,restraint])
      new_unc.freemem()
    # RAISE THE OVERALL COUNTER FOR THIS DATASET
    rcount+=len(setlist[i]["DATA"])
  # COLLECT RESULTS ON MASTER
  if myid==0:
    print "Starting to collect results on CPU 0."
    for i in range(1,numproc):
      slist += pypar.receive(i)
  # SEND RESULTS ON OTHER CPUS
  else:
    pypar.send(slist,0)
  # FINISH UP ON THE MASTER CPU
  if myid==0:
    print "Collected %i restraints."%len(slist)
    slist.sort()
    xmgr.mwrite(slist)
    xmgr.close()
    # GENERATE POSTSCRIPT OUTPUT
    #print "Generating plots."
    #xmgr.output('ps')
  # REMOVE TEMPORARY FILES FROM ALL CPUS
  if myid==0: print 'Removing temporary files.'
  dsc_rmdir(logpath)
  if myid==0: print 'Finished.'
  #pypar.Finalize()

#  =============================================================================
#    S U B S C R I P T  21:  C A L C U L A T E   S E T   C O N T R I B U T I O N
#  =============================================================================
#
# THIS SCRIPT CALCULATES THE CONTRIBUTION OF EACH OF THE DATASETS
# TO THE COMPLETE UNCERTAINTY
def nmv_setinformation(projectname,dataset):
  print "Calculating set contributions."
  print "=============================="
  # SETUP QUEEN
  queen = qn_setup(nmvconf,projectname,myid,numproc)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # CALCULATE SET INFORMATION
  qn_setinformation(queen,xplr,dataset)
  print 'Finished.'


#  =====================================================================
#   S U B S C R I P T  22:  B U I L D   N O E   C O N T A C T   P L O T
#  =====================================================================
#
# SCRIPT TAKES AN NOE INFORMATION CONTENT FILE AND A PDBFILE
# AND BUILDS AN NOE CONTACT PLOT
def nmv_infocontactplot(projectname,datasetlist,type='sym'):
  print "Building restraint contact plot input file."
  print "==========================================="
  # SETUP QUEEN
  queen = qn_setup(nmvconf,projectname)
  xplr = qn_setupxplor(nmvconf,projectname)
  pdbfile = xplr.template
  # READ THE PDB FILE
  pdb = pdb_file.Structure(pdbfile)
  pdbn={}
  for chain in pdb.peptide_chains:
    for residue in chain:
      pdbn[residue.number]={}
      for atom in residue:
        pdbn[residue.number][atom.name]=atom.properties["serial_number"]
  # READ DATAFILE
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,datasetlist))
  # READ DATASETS
  data = qn_readdatasets(queen,datasets)
  restraints = data['data']
  # SET THE LOGFILE
  logfile = os.path.join(queen.outputpath,"2dcontact_%s.dat"%datasetlist)
  # SET THE INPUT FILES
  f1 = os.path.join(queen.outputpath,"Iuni_%s.dat"%datasetlist)
  if type=='sym':
    f2 = os.path.join(queen.outputpath,"Iuni_%s.dat"%datasetlist)
  if type=='nosym':
    f2 = os.path.join(queen.outputpath,"Iave_%s.dat"%datasetlist)
  # OPEN THE PLOT FILE
  xmgr = graceplot(logfile,'xysize','w')
  xmgr.title = "Restraint information."
  xmgr.xlab = "Atom (index)"
  xmgr.ylab = "Atom (index)"
  xmgr.square = 1
  xmgr.writeheader()
  files = [f1,f2]
  for i in range(2):
    # READ THE INFO FILE
    ifile = open(files[i],'r').readlines()
    scorelist = []
    for line in ifile:
      if line[0] not in ['@','#','&']:
        scorelist.append(float(string.split(line)[1]))
    divider = max(scorelist)*0.5
    # CYCLE IT AGAIN
    for line in ifile:
      if line[0] not in ['@','#','&']:
        sline = string.split(line)
        rstring = sline[-1][1:-1]
        # CYCLE ALL RESTRAINTS
        for restraint in restraints:
          # FIND THE RIGHT RESTRAINT
          if str(restraint)==rstring:
            # TAKE ALL ATOM COMBOS
            for k in range(len(restraint.data[0]["RESI"])):
              for l in range(len(restraint.data[1]["RESI"])):
                for residue in pdb.residues:
                  if residue.number == restraint.data[0]['RESI'][k]:
                    numk = residue.number
                    resk = residue.name
                  if residue.number == restraint.data[1]['RESI'][l]:
                    numl = residue.number
                    resl = residue.name
                atomk = restraint.data[0]['NAME'][k]
                atoml = restraint.data[1]['NAME'][l]
                for namek in nmcl_pseudoatoms(atomk,resk):
                  for namel in nmcl_pseudoatoms(atoml,resl):
                    if nmcl_pseudoatoms(atomk,resk).index(namek)==0 and \
                       nmcl_pseudoatoms(atoml,resl).index(namel)==0:
                      print numk,resk,atomk,namek,numl,resl,atoml,namel
                      ak = pdbn[numk][namek]
                      al = pdbn[numl][namel]
                      if i==0:
                        if ak>al:
                          xmgr.write([al,ak,float(sline[1])/divider])
                        else:
                          xmgr.write([ak,al,float(sline[1])/divider])
                      else:
                        if ak>al:
                          xmgr.write([ak,al,float(sline[1])/divider])
                        else:
                          xmgr.write([al,ak,float(sline[1])/divider])
  # CLOSE AND PRINT PLOT
  xmgr.close()
  xmgr.output('ps')
  print 'Finished.'


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


#  =========================================================
#   S U B S C R I P T  24:  G R O U P   R E S T R A I N T S
#  =========================================================
#
# THIS SCRIPT TAKES A DISTANCE RESTRAINT FILE AND GROUPS IT INTO
# LONG RANGE, MEDIUM RANGE, SEQENTIAL AND INTRA-RESIDUAL RESTRAINTS
def nmv_grouprestraints(restrainttbl,format="XPLOR"):
  print "Grouping distance restraints"
  print "============================"
  rfile_group(restrainttbl,format)
  print 'Finished.'


#  =====================================================================
#   S U B S C R I P T  25:  S U P E R I M P O S E   S T R U C T U R E S
#  =====================================================================
#
def nmv_fitensemble(inputfile,outputfile):
  print "Fitting structure ensemble"
  print "============================"
  pdb_models(inputfile)
  runpath = nmvconf["TMP"]
  fitlist = 'file.list'
  # REMEMBER CURRENT LOCATION
  cur_loc = os.getcwd()
  # CHANGE TO TMP DIR
  os.chdir(runpath)
  log = os.popen("%s %s"%(nmvconf["SPLITPDB"],inputfile))
  profitfile = open(os.path.join(runpath,fitlist),'w')
  for line in log:
    profitfile.write("%s\n"%string.split(line)[-1])
  profitfile.close()
  profit = profit_script(nmvconf["PROFIT"],runpath)
  profit.write("MULTI %s"%fitlist)
  profit.write("ITERATE")
  profit.write("FIT")
  profit.write("MWRITE")
  profit.submit()
  log = os.popen("%s -o %s %s*.fit"%(nmvconf["JOINPDB"],outputfile,os.path.split(inputfile)[1][:-4]))
  # BACK TO THE ORIGINAL LOCATION
  os.chdir(cur_loc)
  print 'Done.'


#  ===========================================================
#   S U B S C R I P T  26:  C R E A T E   N R   D A T A S E T
#  ===========================================================
#
# THIS SCRIPT CREATES A NON-REDUNDANT VERSION OF THE PROVIDED
# DATASET
def nmv_createnrdataset(projectname,datasetlist):
  print "Calculating non-redundant dataset"
  print "================================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  logpath = dsc_tmpdir(os.path.join(path,nmvconf["NMRI_LOG"]))
  # SET SOME DEFAULT VARS
  dmtx = os.path.join(logpath,nmvconf["NMRI_TEMPMTX"])
  template = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  xplr = nmvconf["XPLOR"]
  para = nmvconf["NMRI_PAR"]
  # SET THE DATAFILE PATH
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  # READ THE DATASET DESCRIPTION FILE
  setlist = nmrinfo_readdatafile(dataset)
  print "Found %i datafiles in dataset."%len(setlist)
  # SET THE PSF FILE PATH
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
  fulldict = {}
  for filedict in setlist:
    if not fulldict.has_key(filedict["TYPE"]):
      fulldict[filedict["TYPE"]] = []
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    nrtblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],"%snr_%s"%(filedict["FILE"],datasetlist)))
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # STORE PARSED RESTRAINTS FOR FUTURE USE
    filedict["DATA"] = r.restraintlist
    filedict["NRTBL"] = nrtblpath
    fulldict[filedict["TYPE"]]+=r.restraintlist
  # INITIALIZE NMRINFO CLASS FOR FULL UNCERTAINTY
  full_unc = nmr_info()
  fullunc = full_unc.calcsetunc(xplr,para,psffile,fulldict,dmtx,logpath,template)
  full_unc.freemem()
  # CYCLE THE RESTRAINTS UNTIL NO REDUNDANT RESTRAINTS ARE FOUND ANYMORE
  done = 0
  rcount,count,iskipcount,kskipcount = 0,0,-1,-1
  while 1:
    action = 1
    print "# Found %i redundant restraints. #"%rcount
    for i in range(len(setlist)):
      if i>iskipcount:
        for k in range(len(setlist[i]["DATA"])):
          if action and k>kskipcount:
            # CLEAN THE DICTIONARY
            rdict = {}
            for set in setlist: rdict[set["TYPE"]]=[]
            for j in range(len(setlist)):
              # DELETE THE DESIRED RESTRAINT
              if i==j:
                templist = copy.copy(setlist[j]["DATA"])
                restraint = templist[k]
                del templist[k]
                rdict[setlist[j]["TYPE"]]+=templist
              # ADD THE REST OF THE DATA IN THE DATASET
              else:
                rdict[setlist[j]["TYPE"]]+=setlist[j]["DATA"]
            # DETERMINE THE INFO
            new_unc = nmr_info()
            newunc = new_unc.calcsetunc(xplr,para,psffile,rdict,dmtx,logpath,template)
            # CALCULATE THE INFORMATION THE GIVEN RESTRAINT
            info = newunc-fullunc
            print "# %4i %4i %e %s"%(i,k,info,restraint)
            if info == 0.0:
              del setlist[i]["DATA"][k]
              rcount += 1
              action = 0
            else:
              kskipcount = k
              count += 1
            new_unc.freemem()
            sys.stdout.flush()
          if i==len(setlist)-1 and k==len(setlist[i]["DATA"])-1 and action==1: done = 1
        # RESET THE COUNTERS
        if k==len(setlist[i]["DATA"])-1 and action:
          action,kskipcount = 1,-1
          iskipcount+=1
    if done:
      for set in setlist:
        rfile = restraint_file(set["NRTBL"],'w',set["TYPE"])
        rfile.mwrite(set["DATA"])
        rfile.close()
      break
  print 'Removing temporary files.'
  dsc_rmdir(logpath)
  print 'Finished.'


#  ===================================================================
#   S U B S C R I P T  27:  C A L C U L A T E   D I S T   M A T R I X
#  ====================================================================
#
def nmv_calcdmtx(projectname,datasetlist):
  print "Calculating distance matrix."
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
  logfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"mtx_%s"%datasetlist))
  output = open(logfile,'w')
  # READ THE DATASET DESCRIPTION FILE
  setlist = nmrinfo_readdatafile(dataset)
  print "Found %i datafiles in dataset."%len(setlist)
  # SET THE PSF FILE PATH
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  logfile = open(logfile,'w')
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
  # INITIALIZE NMRINFO CLASS FOR FULL AND INITIAL UNCERTAINTY
  nmrinfo = nmr_info()
  nmrinfo.calcsetunc(xplr,para,psffile,fulldict,dmtx,logpath,template)
  output.write("%i\n"%nmrinfo.natoms)
  for i in range(nmrinfo.natoms):
    for j in range(nmrinfo.natoms):
      if i < j:
        target = (nmv.lower_bound(i,j)+nmv.upper_bound(i,j))/2
        error = nmv.upper_bound(i,j)-target
        output.write("%4i %4i %8.3f %8.3f\n"%(i+1,j+1,target,error))
  nmrinfo.freemem()
  output.close()
  print 'Finished.'


#  =============================================================================
#    S U B S C R I P T  28:  C O R R E L A T E   U N C E R T A I N T Y
#  =============================================================================
#
# THIS SCRIPT CORRELATES THE UNCERTAINTY OF GIVEN ATOMS
# WITH THE PROVIDED STRUCTURE
def nmv_correlateuncertainty(projectname,datasetlist,selection,pdbfile):
  print "Correlating atom uncertainty."
  print "============================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  uncfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"atom_%s_%s"%(datasetlist,selection)))
  corfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"cor_%s_%s"%(datasetlist,os.path.basename(pdbfile))))
  gfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"g_%s_%s"%(datasetlist,os.path.basename(pdbfile))))
  if os.path.exists(uncfile):
    print "Uncertainty file exists."
    # READ THE UNCERTAINTY FILE
    unc = open(uncfile,'r').readlines()
    ulist = []
    for line in unc:
      if line[0] not in ['#','@','&']:
        # CONVERT THE UNCERTAINTY
        ulist.append(float(string.split(line)[1]))
    # OPEN THE OUTPUT FILE
    xmgr = graceplot(corfile,'xy','w')
    xmgr.title = "Uncertainty vs. mean %s variation."%(selection)
    xmgr.subtitle = "%s - %s"%(projectname,datasetlist)
    xmgr.xlab = "%s uncertainty (bits)"%selection
    xmgr.ylab = "Mean %s-%s distance variation (A)"%(selection,selection)
    xmgr.writeheader()
    gplot = graceplot(gfile,'xy','w')
    gplot.writeheader()
    # CREATE STDEV MATRIX
    sqbase = Numeric.array([0.0])
    sbase = Numeric.array([0.0])
    residues = len(pdb_file.Structure(pdbfile).residues)
    sqarray = Numeric.resize(sqbase,(residues,residues))
    sarray = Numeric.resize(sbase,(residues,residues))
    # FILL THE STDEV MATRIX
    nomodels = pdb_models(pdbfile)
    for m in range(nomodels):
      pdb = pdb_file.Structure(pdbfile,model=m)
      print "Read model %i of %i."%(m+1,nomodels)
      for i in range(residues):
        for j in range(residues):
          d = pdb.cadistance(pdb.residues[i].number-1,pdb.residues[j].number-1)
          sqarray[i][j]+=d**2
          sarray[i][j]+=d
    # CALCULATE THE PER-RESIDUE SCORES
    dmax = 0.0
    for i in range(residues):
      for j in range(residues):
        dmax = max([dmax,sarray[i][j]/(nomodels)])
    for i in range(residues):
      g = 0.0
      for j in range(residues):
        # FROM NILGES, FEBS LETTERS 1988
        # w IS A WEIGHTING FACTOR
        w = (sarray[i][j]/(nomodels))/dmax
        # G = WEIGHTED MEAN ATOM DISTANCE VARIATION (ANGSTROM)
        try:
          sd = math.sqrt((sqarray[i][j]-((sarray[i][j]**2)/(nomodels)))/(nomodels-1))
        except ValueError:
          sd = 0.0
        g += w*sd
      g = (1.0/residues)*g
      # WRITE CORRELATION FILE
      xmgr.write([ulist[i],g,i+1])
      gplot.write([i+1,g])
    xmgr.close()
    xmgr.output('ps')
    gplot.close()
    gplot.output('ps')
  else:
    print "Please build uncertainty file first."
  print 'Finished.'


#  =====================================================================
#   S U B S C R I P T  29:  C R E A T E   M I N I M A L   D A T A S E T
#  =====================================================================
#
# THIS SCRIPT CREATES A MINIMAL VERSION OF THE PROVIDED DATASET
# FOR THE TIME BEING WE AIM FOR NOES ONLY... THIS COULD BECOME RATHER
# TIME CONSUMING ANYWAY
def nmv_createmindataset(projectname,datasetlist):
  if myid==0:
    print "Calculating minimal dataset"
    print "==========================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  logpath = dsc_tmpdir(os.path.join(path,nmvconf["NMRI_LOG"]))
  # SET SOME DEFAULT VARS
  dmtx = os.path.join(logpath,nmvconf["NMRI_TEMPMTX"])
  template = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  xplr = nmvconf["XPLOR"]
  para = nmvconf["NMRI_PAR"]
  # SET THE DATAFILE PATH
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  # SET THE LOGFILE
  logfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"min_%s"%datasetlist))
  mintblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],"min_%s"%(datasetlist)))
  # READ THE DATASET DESCRIPTION FILE
  setlist = nmrinfo_readdatafile(dataset)
  if myid==0: print "Found %i datafiles in dataset."%len(setlist)
  # SET THE PSF FILE PATH
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
  fulldict = {}
  for filedict in setlist:
    if not fulldict.has_key(filedict["TYPE"]):
      fulldict[filedict["TYPE"]] = []
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # STORE PARSED RESTRAINTS FOR FUTURE USE
    filedict["DATA"] = r.restraintlist
    filedict["MINTBL"] = mintblpath
    fulldict[filedict["TYPE"]]+=r.restraintlist
  # INITIALIZE NMRINFO CLASS FOR FULL UNCERTAINTY
  full_unc = nmr_info()
  fullunc = full_unc.calcsetunc(xplr,para,psffile,fulldict,dmtx,logpath,template)
  full_unc.freemem()
  # INITIALIZE NMRINFO CLASS FOR INITIAL UNCERTAINTY
  ini_unc = nmr_info()
  iniunc = ini_unc.calcsetunc(xplr,para,psffile,{},dmtx,logpath,template)
  ini_unc.freemem()
  # WE ONLY LOOK AT THE DISTANCE RESTRAINTS IN THIS STAGE
  rlist = fulldict["DIST"]
  # THE NEW SORTED LIST
  mlist = []
  if myid==0:
    # THE MINIMAL SUBSET RESTRAINT FILE
    mfile = restraint_file(mintblpath,'w')
    xmgr = graceplot(logfile,'xy','w')
    xmgr.title = "Number of restraints versus % info."
    xmgr.xlab  = "Number of restraints"
    xmgr.ylab  = "Information (%)."
    xmgr.writeheader()
    xmgr.write([0,0," "])
  # CYCLE THE RESTRAINTS
  count = 1
  while len(rlist)>0:
    info = 0
    # SET THE PER PROCESSOR RANGE FOR MPI RUNS
    # SET AND SHUFFLE THE RANGE LIST
    if myid==0:
      # SET THE TESTRANGE
      shuffle(rlist)
      # DISTRIBUTE THE LIST OVER THE NODES
      for m in range(1,numproc):
        pypar.send(rlist,m)
    else:
      # RECEIVE THE LIST
      rlist=pypar.receive(0)
    mylower,myupper=mpi_setrange(rlist,queen.myid,queen.numproc)
    print "Submitted %i restraints to CPU %i of %i."%(myupper-mylower,myid+1,numproc)
    # FIND THE HIGHEST INFO
    for i in range(mylower,myupper):
      tlist = copy.copy(mlist)
      tlist.append(rlist[i])
      unc = nmr_info()
      tunc = unc.calcsetunc(xplr,para,psffile,{"DIST":tlist},dmtx,logpath,template)
      tinfo = iniunc-tunc
      unc.freemem()
      if tinfo>info:
        info = tinfo
        sdict = {}
        sdict[i]=info
    # COLLECT RESULTS ON MASTER AND DETERMINE THE HIGHEST SCORING RESTRAINT
    if myid==0:
      print "Starting to collect results on CPU 1."
      for i in range(1,numproc):
        sdict.update(pypar.receive(i))
      finfo, fi = 0,0
      for key in sdict.keys():
        if sdict[key]>finfo:
          finfo=sdict[key]
          fi=key
    # SEND RESULTS ON OTHER CPUS
    else:
        pypar.send(sdict,0)
    # COMMUNICATE THE HIGHEST SCORING ID TO THE OTHER CPUS
    if myid==0:
      for i in range(1,numproc):
        pypar.send(fi,i)
    else:
      fi = pypar.receive(0)
    # ON ALL CPUS WE ADD THE HIGHEST SCORER
    # TO THE LIST OF NEW NOES!
    mlist.append(rlist[fi])
    # WRITE LOG
    if myid==0:
      # WRITE THE RESTRAINT TO THE NEW RESTRAINT FILE
      mfile.write(rlist[fi])
      # WRITE RESTRAINTFILE WITH THE CURRENT SET
      ttblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],"min_%s_%04i"%(datasetlist,count)))
      tfile = restraint_file(ttblpath,'w')
      tfile.mwrite(mlist)
      tfile.close()
      # WRITE TO THE LOGFILE
      xmgr.write([count,(float(finfo)/(iniunc-fullunc))*100,rlist[fi]])
      # RAISE THE COUNTER
      count+=1
    # DELETE THE RESTRAINT FROM THE OLD LIST
    del rlist[fi]
  # WRAP UP
  if myid==0:
    xmgr.close()
    #xmgr.output('ps')
  print 'Removing temporary files.'
  dsc_rmdir(logpath)
  #pypar.Finalize()
  print 'Finished.'


#  ===============================================================
#   S U B S C R I P T  30:  S E N D   B I R T H D A Y   M A I L S
#  ===============================================================
#
def nmv_birthdaymail(birthdayfile):
  content = open(birthdayfile,'r').readlines()
  list = []
  for line in content:
    if line[0]!='#':
      line = string.expandtabs(line)
      day = int(line[:2])
      month = int(line[8:10])
      naam = string.strip(line[16:40])
      email = string.strip(line[40:79])
      today = time.gmtime()
      if day==today[2] and month==today[1]:
        list.append(naam+'\n')
        message = ["Beste %s,\n\nVan harte gefeliciteerd met je verjaardag!\n\nBestuur en medewerkers Gryphus."%naam]
        eml_send(email,'Van harte!',message,sender='info@gryphus.nl')
  if len(list)>0:
    eml_send(nmvconf['MY_EMAIL'],'Vandaag zijn jarig...',list,sender='info@gryphus.nl')


#  =======================================================
#   S U B S C R I P T  31:  C H E C K  R A I D  A R R A Y
#  =======================================================
#
# SCRIPT CHECKS RAID ARRAY BY COMPARING TO A GOOD MDSTAT, IN THIS WAY WE
# DETECT ANY CHANGES. WHO KNOWS WHAT CRAZY STUFF COULD GO WRONG...
def nmv_checkraid(goodmdstat):
  # READ THE MDSTAT FILES
  current = open('/proc/mdstat','r').readlines()
  good = open(goodmdstat,'r').readlines()
  if current == good:
    # ONCE A MONTH WE SEND AN "I'M STILL ALIVE" MAIL
    if time.gmtime()[2]==1 and time.gmtime()[3]==0:
      eml_send(nmvconf["MY_EMAIL"],'Your RAID array is alive and kickin!',["This is montly mail to remind you.!"])
  # SOMETHING IS WRONG, SEND AN EMAIL
  else:
    eml_send(nmvconf["MY_EMAIL"],'Your RAID array needs attention!',current)


#  ==========================================================
#   S U B S C R I P T  32: P L O T   I N F O   V S   N O E S
#  ==========================================================
#
# THIS SCRIPT PLOT THE NUMBER OF NOES VERSUS THE AMOUNT OF INFORMATION IN
# THEM. ONLY NOES FOR NOW...
def nmv_noesvsinfo(projectname,datasetlist,ncycles=10):
  if myid==0:
    print "Plot %info versus %restraints."
    print "=============================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  logpath = dsc_tmpdir(os.path.join(path,nmvconf["NMRI_LOG"]))
  # SET SOME DEFAULT VARS
  dmtx = os.path.join(logpath,nmvconf["NMRI_TEMPMTX"])
  template = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  xplr = nmvconf["XPLOR"]
  para = nmvconf["NMRI_PAR"]
  # SET THE DATAFILE PATH
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  setlist = nmrinfo_readdatafile(dataset)
  # SET THE PSF FILE PATH
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  if myid==0:
    # SET THE LOGFILE
    plotfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"infvsnoe_%s"%datasetlist))
    xmgr = graceplot(plotfile,'xydy','w')
    xmgr.title = "Percentage information vs Percentage NOES."
    xmgr.xlab = "Number of NOEs (%)"
    xmgr.ylab = "Amount of infomation (%)"
    xmgr.square = 1
    xmgr.writeheader()
  # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
  fulldict = {}
  rcount = 0
  # CYCLE ALL AVAILABLE SETS
  for filedict in setlist:
    # CONSTRUCT THE TABLE PATH
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    # READ THE TABLE
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # STORE PARSED RESTRAINTS FOR FUTURE USE
    filedict["DATA"] = r.restraintlist
    fulldict[filedict["TYPE"]]=fulldict.get(filedict["TYPE"],[]) + r.restraintlist
    # COUNT THE NUMBER OF RESTRAINTS
    rcount += len(r.restraintlist)
  # INITIALIZE NMRINFO CLASS FOR FULL UNCERTAINTY
  full_unc = nmr_info()
  fullunc = full_unc.calcsetunc(xplr,para,psffile,fulldict,dmtx,logpath,template)
  full_unc.freemem()
  ini_unc = nmr_info()
  iniunc = ini_unc.calcsetunc(xplr,para,psffile,{},dmtx,logpath,template)
  ini_unc.freemem()
  # WE ONLY LOOK AT THE DISTANCE RESTRAINTS IN THIS STAGE
  # THAT MAKES LIFE A WHOLE LOT EASIER...
  rlist = fulldict["DIST"]
  scoredict = {0:[0.0]}
  # SET RANGE FOR MPI RUNS
  mylower,myupper=mpi_setrange(range(ncycles))
  # RUN THE CYCLES
  for i in range(mylower,myupper):
    print "Started cycle %i of %i on CPU %i."%(i-mylower+1,myupper-mylower,myid+1)
    # RANDOMIZE THE LIST
    shuffle(rlist)
    # DO THEM ALL
    for j in range(1,len(rlist)+1):
      tlist = rlist[:j]
      set_unc = nmr_info()
      setunc = set_unc.calcsetunc(xplr,para,psffile,{"DIST":tlist},dmtx,logpath,template)
      set_unc.freemem()
      scoredict[j]=scoredict.get(j,[])+[(iniunc-setunc)/(iniunc-fullunc)*100]
  # COLLECT RESULTS
  if myid==0:
    print "Starting to collect results on CPU 0."
    for i in range(1,numproc):
      recdict = pypar.receive(i)
      for key in recdict.keys():
        scoredict[key]=scoredict.get(key,[])+recdict[key]
  # SEND RESULTS ON OTHER CPUS
  else:
    pypar.send(scoredict,0)
  # BUILD PLOT AND EXIT
  if myid==0:
    # BUILD THE PLOT
    print "Averaging over cycles."
    keys = scoredict.keys()
    keys.sort()
    for key in keys:
      avg = avg_list(scoredict[key])
      xmgr.write([key,avg[0],avg[1]])
    xmgr.close()
    xmgr.output('ps')
    print "Finished."
  #pypar.Finalize()


#  ==========================================================
#   S U B S C R I P T  33: P L O T   R M S D   V S   N O E S
#  ==========================================================
#
def nmv_rmsdvsnoes(projectname,datasetlist):
  # SOME PARS
  nstruct = 40
  stepsize = 2
  atomsel = 'heavy'
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  # SET SOME DEFAULT VARS
  template = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  if myid==0:
    # THE LOGFILE
    logfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"rmsdvsnoes_%s"%datasetlist))
    xmgr = graceplot(logfile,'xydy','w')
    xmgr.title = "Percentage of restraints versus RMSD"
    xmgr.xlab = "Percentage of restraints"
    xmgr.ylab = "RMSD to reference"
    xmgr.writeheader()
    # SECOND LOGFILE
    avlogfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"rmsdavvsnoes_%s"%datasetlist))
    xmgrav = graceplot(avlogfile,'xydy','w')
    xmgrav.title = "Percentage of restraints versus RMSD"
    xmgrav.xlab = "Percentage of restraints"
    xmgrav.ylab = "RMSD average to average of complete set"
    xmgrav.writeheader()
  # DETERMINE THE AVAILABLE RESTRAINTSET
  tblpath = nmv_adjust(nmvconf["NMRI_DATATBL"],'min_%s_*'%datasetlist)
  tblpath = os.path.join(path,tblpath)
  setlist = glob.glob(tblpath)
  setlist.sort()
  if len(setlist)==0:
    print "Please build a minimal dataset first!"
    print "e.g. ./nmr_valibase.py -info_buildminset %s %s"%(projectname,datasetlist)
    return
  # CALCULATE THE REF STRUCTURE
  pdbprefix = os.path.join(path,nmvconf["NMRI_PDB"])
  pdbbase = "ref_%s_"%datasetlist
  pdbref = os.path.join(pdbprefix,"%save.pdb"%pdbbase)
  pdbref = '/home/snabuurs/python/nmr_valibase/pdb/1pgb.pdb'
  if myid==0:
    # SET THE DATAFILE PATH
    dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
    refset = nmrinfo_readdatafile(dataset)
    # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
    refdict = {}
    # CYCLE ALL AVAILABLE SETS
    for filedict in refset:
      # CREATE A KEY IN THE DICTIONARY
      if not refdict.has_key(filedict["TYPE"]):
        refdict[filedict["TYPE"]] = []
      # CONSTRUCT THE TABLE PATH
      tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
      # READ THE TABLE
      r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
      r.read()
      # STORE PARSED RESTRAINTS FOR FUTURE USE
      filedict["DATA"] = r.restraintlist
      refdict[filedict["TYPE"]]+=r.restraintlist
    print "Calculating reference structure on 1 processor."
    # CALCULATE
    xplor_calcstruct(os.path.join(pdbprefix,pdbbase),template,psffile,refdict,disulist,averaging='cent',naccepted=nstruct)
    print "Calculating average reference structure."
    xplor_calcave(os.path.join(pdbprefix,pdbbase),nstruct,psffile)
  pypar.Barrier()
  # SPLIT THE SETLIST
  nlist = []
  for i in range(0,101,stepsize):
    counter = int(round((i/100.0)*(len(setlist)-1)))
    nlist.append(setlist[counter])
  # SET THE RANGE FROM MPI JOBS
  mylower,myupper=mpi_setrange(nlist)
  results,avresults = [],[]
  for i in range(mylower,myupper):
    rdict = {}
    # READ THE TABLE - ONLY DISTANCE RESTRAINTS FOR NOW!!
    r = restraint_file(nlist[i],'r',format="XPLOR",type="DIST")
    r.read()
    rdict["DIST"]=rdict.get("DIST",[]) + r.restraintlist
    # CALCULATE STRUCTURES
    print "Calculating structures."
    pdbprefix = os.path.join(path,nmvconf["NMRI_PDB"])
    pdbbase = "min_%s_%04i_"%(datasetlist,i*stepsize)
    xplor_calcstruct(os.path.join(pdbprefix,pdbbase),template,psffile,rdict,disulist,averaging='cent',naccepted=nstruct)
    pdblist = glob.glob(os.path.join(pdbprefix,"min_%s_%04i_*.pdb"%(datasetlist,i*stepsize)))
    print "Calculating average structure."
    xplor_calcave(os.path.join(pdbprefix,pdbbase),nstruct,psffile)
    lref = os.path.join(pdbprefix,"%save.pdb"%pdbbase)
    # SUPERIMPOSE TO REF
    print "Fitting to reference structure."
    prft_fitref(lref,pdblist,runpath=pdbprefix)
    # CALCULATE RMSD OF ENSEMBLE
    print "Calculating RMSD of ensemble."
    pdblist = [lref]+pdblist[:-1]
    rmsdarray = prft_rmsdmtx(pdblist,selection=atomsel,runpath=pdbprefix)
    rmsdlist = []
    for j in range(len(rmsdarray)):
      for k in range(len(rmsdarray)):
        if j==0 and j!=k:
          rmsdlist.append(rmsdarray[j][k])
    print rmsdlist
    rmsd = avg_list(rmsdlist)
    # BUILD RETURN LIST
    results.append([i*stepsize, rmsd[0], rmsd[1]])
    # CALCULATE RMSD OF AVERAGE STRUCTURE
    print "Calculating RMSD of average."
    pdblist = [pdbref]+[os.path.join(pdbprefix,pdbbase)+'ave.pdb']
    rmsdarray = prft_rmsdmtx(pdblist,selection=atomsel,runpath=pdbprefix)
    rmsdlist = []
    print rmsdarray
    for j in range(len(rmsdarray)):
      for k in range(len(rmsdarray)):
        if j==0 and j!=k:
          rmsdlist.append(rmsdarray[j][k])
    print rmsdlist
    rmsd=avg_list(rmsdlist)
    # BUILD RETURN LIST
    avresults.append([i*stepsize, rmsd[0], rmsd[1]])
  # COLLECT RESULTS ON MASTER
  if myid==0:
    print "Starting to collect results on CPU 0."
    for i in range(1,numproc):
      receivedict = pypar.receive(i)
      results+=receivedict['ens']
      avresults+=receivedict['ave']
    xmgr.mwrite(results)
    xmgrav.mwrite(avresults)
    results = []
  # SEND RESULTS ON OTHER CPUS
  else:
    # BUILD A DICTIONARY TO SEND
    rmsdict = {'ens':results,'ave':avresults}
    # SEND IT
    pypar.send(rmsdict,0)
  pypar.Barrier()
  print "CPU %i finished"%(myid+1)
  # WRAP UP
  if myid==0:
    xmgr.close()
    xmgrav.close()
    xmgr.output('ps')
    xmgrav.output('ps')
    print "Done"
  #pypar.Finalize()

#  ==========================================================
#   S U B S C R I P T  33A: P L O T   R M S D   V S   N O E S
#  ==========================================================
#
def nmv_rmsdvsrandomnoes(projectname,datasetlist):
  for q in range(10):
    # SETUP QUEEN
    queen = qn_setup(nmvconf,projectname,myid,numproc)
    xplr  = qn_setupxplor(nmvconf,projectname)
    # SOME PARS
    nstruct = 40
    stepsize = 5
    atomsel = 'heavy'
    if myid==0:
      # THE LOGFILE
      logfile = os.path.join(queen.outputpath,"rmsdvsrandomnoes_%s_%i.dat"%(datasetlist,q))
      xmgr = graceplot(logfile,'xydy','w')
      xmgr.title = "Percentage of restraints versus RMSD"
      xmgr.xlab = "Percentage of restraints"
      xmgr.ylab = "RMSD to reference"
      xmgr.writeheader()
      # SECOND LOGFILE
      avlogfile = os.path.join(queen.outputpath,"rmsdavvsrandomnoes_%s_%i.dat"%(datasetlist,q))
      xmgrav = graceplot(avlogfile,'xydy','w')
      xmgrav.title = "Percentage of restraints versus RMSD"
      xmgrav.xlab = "Percentage of restraints"
      xmgrav.ylab = "RMSD average to average of complete set"
      xmgrav.writeheader()
    # CALCULATE THE REF STRUCTURE
    pdbprefix = queen.pdb
    pdbbase = "ref_%s_%i_"%(datasetlist,q)
    pdbref = os.path.join(pdbprefix,"%save.pdb"%pdbbase)
    pdbref = '1pgb_xplor.pdb'
    if myid==0:
      rlist = []
      # SET THE DATAFILE PATH
      dataset = nmv_adjust(queen.dataset,datasetlist)
      refset = qn_readdatafile(dataset)
      # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
      refdict = {}
      # CYCLE ALL AVAILABLE SETS
      for filedict in refset:
        # CREATE A KEY IN THE DICTIONARY
        if not refdict.has_key(filedict["TYPE"]):
          refdict[filedict["TYPE"]] = []
        # CONSTRUCT THE TABLE PATH
        tblpath = nmv_adjust(queen.table,filedict["FILE"])
        # READ THE TABLE
        r = restraint_file(tblpath,'r',type=filedict["TYPE"])
        r.read()
        # STORE PARSED RESTRAINTS FOR FUTURE USE
        rlist += r.restraintlist
        refdict[filedict["TYPE"]]+=r.restraintlist
      print "Calculating reference structure on 1 processor."
      # CALCULATE
      xplor_calcstruct(os.path.join(pdbprefix,pdbbase),xplr.template,xplr.psf,refdict,[],averaging='cent',naccepted=nstruct)
      print "Calculating average reference structure."
      xplor_calcave(os.path.join(pdbprefix,pdbbase),nstruct,xplr.psf)
      shuffle(rlist)
      for i in range(1,queen.numproc):
        pypar.send(rlist,i)
    else:
      rlist = pypar.receive(0)
    pypar.Barrier()
    # SPLIT THE RESTRAINTLIST
    setdict = {}
    setlist = []
    for i in range(0,101,stepsize):
      counter = int(round((i/100.0)*(len(rlist))))
      setlist.append(rlist[:counter])
      setdict[i]=rlist[:counter]
    # SET THE RANGE FROM MPI JOBS
    if myid==0:
      keys = setdict.keys()
      shuffle(keys)
      for i in range(1,numproc):
        pypar.send(keys,i)
    else:
      keys = pypar.receive(0)
    mylower,myupper=mpi_setrange(keys,myid,numproc)
    results,avresults = [],[]
    for i in range(mylower,myupper):
      rdict = {}
      rdict["DIST"] = setdict[keys[i]]
      # CALCULATE STRUCTURES
      print "Calculating structures."
      pdbprefix = queen.pdbpath
      pdbbase = "min_%s_%i_%04i_"%(datasetlist,q,keys[i])
      xplor_calcstruct(os.path.join(pdbprefix,pdbbase),xplr.template,xplr.psf,rdict,[],averaging='cent',naccepted=nstruct)
      pdblist = glob.glob(os.path.join(pdbprefix,"min_%s_%i_%04i_*.pdb"%(datasetlist,q,keys[i])))
      print "Calculating average structure."
      xplor_calcave(os.path.join(pdbprefix,pdbbase),nstruct,xplr.psf)
      lref = os.path.join(pdbprefix,"%save.pdb"%pdbbase)
      # SUPERIMPOSE TO REF
      print "Fitting to reference structure."
      prft_fitref(lref,pdblist,runpath=pdbprefix)
      # CALCULATE RMSD OF ENSEMBLE
      print "Calculating RMSD of ensemble."
      pdblist = [lref]+pdblist[:-1]
      rmsdarray = prft_rmsdmtx(pdblist,selection=atomsel,runpath=pdbprefix)
      rmsdlist = []
      for j in range(len(rmsdarray)):
        for k in range(len(rmsdarray)):
          if j==0 and j!=k:
            rmsdlist.append(rmsdarray[j][k])
      rmsd = avg_list(rmsdlist)
      # BUILD RETURN LIST
      results.append([keys[i], rmsd[0], rmsd[1]])
      # CALCULATE RMSD OF AVERAGE STRUCTURE
      print "Calculating RMSD of average."
      pdblist = [pdbref]+[os.path.join(pdbprefix,pdbbase)+'ave.pdb']
      rmsdarray = prft_rmsdmtx(pdblist,selection=atomsel,runpath=pdbprefix)
      rmsdlist = []
      for j in range(len(rmsdarray)):
        for k in range(len(rmsdarray)):
          if j==0 and j!=k:
            rmsdlist.append(rmsdarray[j][k])
      rmsd=avg_list(rmsdlist)
      # BUILD RETURN LIST
      avresults.append([keys[i], rmsd[0], rmsd[1]])
    # COLLECT RESULTS ON MASTER
    if myid==0:
      print "Starting to collect results on CPU 0."
      for i in range(1,numproc):
        receivedict = pypar.receive(i)
        results+=receivedict['ens']
        avresults+=receivedict['ave']
      xmgr.mwrite(results)
      xmgrav.mwrite(avresults)
      results = []
    # SEND RESULTS ON OTHER CPUS
    else:
      # BUILD A DICTIONARY TO SEND
      rmsdict = {'ens':results,'ave':avresults}
      # SEND IT
      pypar.send(rmsdict,0)
    pypar.Barrier()
    print "CPU %i finished"%(myid+1)
    # WRAP UP
    if myid==0:
      xmgr.close()
      xmgrav.close()
      print "Done"
    #pypar.Finalize()

#  ================================================
#   S U B S C R I P T  34:  C A L C U L A T E  S 2
#  ================================================
#
# CALCULATE ORDER PARAMETER FROM PROTEIN STRUCTURE
def nmv_calcs2(pdbfile,logfile):
  print "Calculating order parameter from structure:\n%s"%pdbfile
  # CALCULATE THE S2 VALUES
  s2dict = pdb_s2(pdbfile)
  print "Building plot."
  xmgr = graceplot(logfile,'xydy','w')
  xmgr.title = "Predicted order parameter"
  xmgr.subtitle = "%s"%pdbfile
  xmgr.xlab = "Residue number"
  xmgr.ylab = "1-S\S2"
  xmgr.writeheader()
  for key in s2dict.keys():
    avg = avg_list(s2dict[key])
    xmgr.write([key,avg[0],avg[1]])
  xmgr.close()
  print "Done."


#  ========================================================================
#   S U B S C R I P T  35:  C O R R E L A T E   U  V S   V A R I A T I O N
#  =========================================================================
#
# THIS SCRIPT CORRELATES THE UNCERTAINTY OF GIVEN ATOMS
# WITH THE PROVIDED STRUCTURE
def nmv_uncertaintyvsvariance(projectname,datasetlist,pdbfile):
  print "Correlating distance uncertainty with variation."
  print "================================================"
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  # SET THE DATAFILE PATH
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  setlist = nmrinfo_readdatafile(dataset)
  # SET THE LOGFILE
  logfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"uvsg_%s_%s"%(datasetlist,os.path.basename(pdbfile))))
  # OPEN THE OUTPUT FILE
  xmgr = graceplot(logfile,'xy','w')
  xmgr.title = ""
  xmgr.subtitle = ""
  xmgr.xlab = ""
  xmgr.ylab = ""
  xmgr.writeheader()
  # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
  fulldict = {}
  rcount = 0
  # CYCLE ALL AVAILABLE SETS
  for filedict in setlist:
    # CONSTRUCT THE TABLE PATH
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    # READ THE TABLE
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # STORE PARSED RESTRAINTS FOR FUTURE USE
    filedict["DATA"] = r.restraintlist
    fulldict[filedict["TYPE"]]=fulldict.get(filedict["TYPE"],[]) + r.restraintlist
    # COUNT THE NUMBER OF RESTRAINTS
    rcount += len(r.restraintlist)
  # INITIALIZE NMRINFO CLASS FOR UNCERTAINTY
  nmrunc = nmr_info()
  # CREATE STDEV MATRIX
  residues = len(pdb_file.Structure(pdbfile).residues)
  svarlist = []
  sqvarlist = []
  ulist = []
  # FILL THE STDEV MATRIX
  nomodels = pdb_models(pdbfile)
  for m in range(nomodels):
    pdb = pdb_file.Structure(pdbfile,model=m)
    print "Read model %i of %i."%(m+1,nomodels)
    # CYCLE ALL RESIDUES
    for i in range(residues):
      if m==0:
        svarlist.append(0.0)
        sqvarlist.append(0.0)
      # CALCULATE CA DISTANCE DISTANCE 2 CENTER
      d = pdb.distance2center(pdb.residues[i].number-1)
      sqvarlist[i]+=d**2
      svarlist[i]+=d
      # FULL THE UNCERTAINTY LIST ONLY ONCE!
      if m==0:
        for atomi in pdb.residues[i]:
          if atomi.name=='CA':
            natomi = atomi.properties["serial_number"]
            ulist.append(nmrunc.calcatomuncertainty(natomi))
  # CALCULATE THE PER-RESIDUE SCORES
  for i in range(residues):
    q = 0.0
    # MEAN ATOM DISTANCE 2 CENTER VARIATION (ANGSTROM)
    q = math.sqrt((sqvarlist[i]-((svarlist[i]**2)/(nomodels)))/(nomodels-1))
    xmgr.write([ulist[i],q,i])
  xmgr.close()
  xmgr.output('ps')
  # FREE THE MEMORY
  nmrunc.freemem()
  print 'Finished.'


#  ==============================================================
#   S U B S C R I P T  36:  C A L C U L A T E  S T R U C T U R E
#  ==============================================================
#
# CALCULATE PROTEIN STRUCTURE
def nmv_calcstruct(projectname,datasetlist,basename=None,nstruct=10):
  print "Calculating structures."
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  # SET SOME DEFAULT VARS
  template = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  disulfidefile = os.path.join(path,nmvconf["NMRI_DISULFIDES"])
  disulist = nmrinfo_readdisulfides(disulfidefile)
  # SET THE DATAFILE PATH
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  data = nmrinfo_readdatafile(dataset)
  # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
  datadict = {}
  # CYCLE ALL AVAILABLE SETS
  for filedict in data:
    # CREATE A KEY IN THE DICTIONARY
    if not datadict.has_key(filedict["TYPE"]):
      datadict[filedict["TYPE"]] = []
    # CONSTRUCT THE TABLE PATH
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    # READ THE TABLE
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # STORE PARSED RESTRAINTS FOR FUTURE USE
    filedict["DATA"] = r.restraintlist
    if filedict["TYPE"]=='DIST':
      averaging = filedict['AVER']
    datadict[filedict["TYPE"]]+=r.restraintlist
  # SET THE PREFIX
  pdbprefix = os.path.join(path,nmvconf["NMRI_PDB"])
  print pdbprefix
  if basename:
    pdbbase = "%s_%s_"%(basename,datasetlist)
  else:
    pdbbase = "str_%s_"%datasetlist
  # CALCULATE
  print "Calculating %i structures."%nstruct
  xplor_calcstruct(os.path.join(pdbprefix,pdbbase),template,psffile,datadict,disulist,averaging=averaging,naccepted=nstruct)
  print "Calculating average reference structure."
  xplor_calcave(os.path.join(pdbprefix,pdbbase),nstruct,psffile)
  print "Done."


#  ===============================================================
#   S U B S C R I P T  XX:  A V E R A G E   I N F O R M A T I O N
#  ===============================================================
#
def nmv_avinformation_old(projectname,datasetlist):
  if myid==0:
    print "Calculating average restraint information."
    print "=========================================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  logpath = dsc_tmpdir(os.path.join(path,nmvconf["NMRI_LOG"]))
  # SET SOME DEFAULT VARS
  dmtx = os.path.join(logpath,nmvconf["NMRI_TEMPMTX"])
  template = os.path.join(path,nmvconf["NMRI_TEMPLATE"])
  xplr = nmvconf["XPLOR"]
  para = nmvconf["NMRI_PAR"]
  # SET THE DATAFILE PATH
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  # SET THE LOGFILE
  plotfile = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"avinf_%s"%datasetlist))
  # READ THE DATASET DESCRIPTION FILE
  setlist = nmrinfo_readdatafile(dataset)
  if myid==0: print "Found %i datafiles in dataset."%len(setlist)
  # SET THE PSF FILE PATH
  psffile = os.path.join(path,nmvconf["NMRI_PSF"])
  # WE ONLY CREATE A LOGFILE ON THE MASTER CPU
  if myid==0:
    xmgr = graceplot(plotfile,'xydy','w')
    xmgr.title = "Average restraint information"
    xmgr.xlab = "Restraint index."
    xmgr.ylab = "Information (%)"
    xmgr.writeheader()
  # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
  fulldict = {}
  # CYCLE ALL AVAILABLE SETS
  for filedict in setlist:
    # CREATE A KEY IN THE DICTIONARY
    if not fulldict.has_key(filedict["TYPE"]):
      fulldict[filedict["TYPE"]] = []
    # CONSTRUCT THE TABLE PATH
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    # READ THE TABLE
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # STORE PARSED RESTRAINTS FOR FUTURE USE
    filedict["DATA"] = r.restraintlist
    fulldict[filedict["TYPE"]]+=r.restraintlist
  # INITIALIZE NMRINFO CLASS FOR BACKGROUND UNCERTAINTY
  bg_unc = nmr_info()
  bgunc = bg_unc.calcsetunc(xplr,para,psffile,{},dmtx,logpath,template)
  bg_unc.freemem()
  # INITIALIZE NMRINFO CLASS FOR FULL UNCERTAINTY
  full_unc = nmr_info()
  fullunc = full_unc.calcsetunc(xplr,para,psffile,fulldict,dmtx,logpath,template)
  full_unc.freemem()
  allinfo = bgunc-fullunc
  # CYCLE ALL RESTRAINTS
  rlist = fulldict["DIST"]
  total = 0
  # CYCLE ALL RESTRAINTS
  for i in range(len(rlist)):
    print "Restraint number %i started"%(i+1)
    # KEEP RESULTS PER RESTRAINT
    results = []
    # CREATE TEMPORARY LIST
    tlist = copy.copy(rlist)
    # DELETE THE RESTRAINT UNDER INVESTIGATION
    del tlist[i]
    # AND STORE IT
    restraint = rlist[i]
    # SET AND SHUFFLE THE RANGE LIST
    if myid==0:
      # SET THE TESTRANGE
      trange = range(0,101,1)
      shuffle(trange)
      # DISTRIBUTE THE LIST OVER THE NODES
      for m in range(1,numproc):
        pypar.send(trange,m)
    else:
      # RECEIVE THE LIST
      trange=pypar.receive(0)
    mylower,myupper=mpi_setrange(trange)
    # HANDLE THE ASSIGNED RANGE
    for j in trange[mylower:myupper]:
      # FOR NOW ONLY ONE RUN
      for k in range(1):
        # COPY THE TEMPLIST
        ttlist = copy.copy(tlist)
        random()
        shuffle(ttlist)
        # SET THE SECTION SLICER
        if j>0:
          section = int(round((j/100.0)*len(ttlist)))
        else:
          section = 0
        # SECTION UNC
        t_unc = nmr_info()
        tunc = t_unc.calcsetunc(xplr,para,psffile,{"DIST":ttlist[:section]},dmtx,logpath,template)
        t_unc.freemem()
        # SECTION + RESTRAINT UNC
        t_unc = nmr_info()
        nunc = t_unc.calcsetunc(xplr,para,psffile,{"DIST":ttlist[:section]+[restraint]},dmtx,logpath,template)
        t_unc.freemem()
        # RESTRAINT INFO
        info = tunc - nunc
        # STORE
        results.append(info)
    # COLLECT RESULTS
    if myid==0:
      for m in range(1,numproc):
        results+=pypar.receive(m)
    else:
      pypar.send(results,0)
    # WRITE OUTPUT
    if myid==0:
      avg = avg_list(results)
      xmgr.write([i+1,(avg[0]/allinfo)*100,(avg[1]/allinfo)*100,str(restraint)])
      total += (avg[0]/allinfo)*100
    pypar.Barrier()
  # FINISH UP ON THE MASTER CPU
  if myid==0:
    xmgr.close()
    # GENERATE POSTSCRIPT OUTPUT
    print "Generating plots."
    #xmgr.output('ps')
  # REMOVE TEMPORARY FILES FROM ALL CPUS
  if myid==0: print 'Removing temporary files.'
  dsc_rmdir(logpath)
  if myid==0: print 'Finished.', total
  #pypar.Finalize()

#  ===============================================================
#   S U B S C R I P T  37:  A V E R A G E   I N F O R M A T I O N
#  ===============================================================
#
def nmv_avinformation(projectname,dataset):
  if myid==0:
    print "Calculating average restraint information."
    print "=========================================="
  # SETUP QUEEN
  queen = qn_setup(nmvconf,projectname,myid,numproc)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # CALCULATE Iave
  qn_infave(queen,xplr,dataset)
  print 'Finished.'


#  =========================================================================
#   S U B S C R I P T  38:  C O M B I N E   A V G   A N D   U N I   I N F O
#  =========================================================================
#
def nmv_combineavguni(projectname,dataset):
  print "Building average info vs unique info plot."
  print "=========================================="
  # SETUP QUEEN
  queen = qn_setup(nmvconf,projectname,myid,numproc)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # PLOT Iave VS Iuni
  qn_avevsuni(queen,xplr,dataset)
  # WRITE SORTED RESTRAINTTABLE
  qn_sorttbl(queen,xplr,dataset)
  print "Done"


#  =============================================================================
#    S U B S C R I P T  39:  B U I L T   O R D E R E D   R E S T R    L I S T S
#  =============================================================================
#
# BUILT RESTRAINT TABLES SORTED BY UNIQUE INFORMATION, AVERAGE INFORMATION AND
# A COMBINATION OF BOTH. THIS WILL YIELD THE TABLE WITH THE MOST CHECKABLE
# RESTRAINTS
def nmv_infosortedlist(projectname,datasetlist):
  print "Building sorted restraint lists"
  print "==============================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  # SET THE DATAFILE PATH
  dataset = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATASET"],datasetlist))
  # SET FILEPATHS
  uni_file = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"inf_%s"%datasetlist))
  avg_file = os.path.join(path,nmv_adjust(nmvconf["NMRI_PLOT"],"avinf_%s"%datasetlist))
  # CHECK IF FILES ARE PRESENT
  if not os.path.exists(uni_file): error("Create restraint info file first!")
  if not os.path.exists(avg_file): error("Create average info file first!")
  # READ THE DATASET DESCRIPTION FILE
  setlist = nmrinfo_readdatafile(dataset)
  # BUILD A DICTIONARY WITH ALL DATA IN THE DATASET
  fulldict = {}
  for filedict in setlist:
    if not fulldict.has_key(filedict["TYPE"]):
      fulldict[filedict["TYPE"]] = []
    tblpath = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],filedict["FILE"]))
    r = restraint_file(tblpath,'r',format="XPLOR",type=filedict["TYPE"])
    r.read()
    # STORE PARSED RESTRAINTS FOR FUTURE USE
    filedict["DATA"] = r.restraintlist
    fulldict[filedict["TYPE"]]+=r.restraintlist
  # WE ONLY LOOK AT THE DISTANCE RESTRAINTS IN THIS STAGE
  rlist = fulldict["DIST"]
  rdict = {}
  for r in rlist:
    rdict[str(r)]=r
  # THE OUTPUT RESTRAINT FILES
  uni_rest = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],"uni_%s"%datasetlist))
  uni_r = restraint_file(uni_rest,'w')
  avg_rest = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],"avg_%s"%datasetlist))
  avg_r = restraint_file(avg_rest,'w')
  che_rest = os.path.join(path,nmv_adjust(nmvconf["NMRI_DATATBL"],"che_%s"%datasetlist))
  che_r = restraint_file(che_rest,'w')
  udict,adict,cdict={},{},{}
  sumdict = {}
  # READ AND CLEAN FILES
  comments = ['#','@','&']
  # UNIQUE
  umax = 0
  ufile = open(uni_file,'r').readlines()
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
  afile = open(avg_file,'r').readlines()
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
      uni_r.comment("%e %% unique information"%key)
      uni_r.write(rdict[rstr])
  uni_r.close()
  # WRITE SORTED UNIQUE
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
  # COMBINE AVG AND UNIQUE
  print "Done"


#  =================================================
#   S U B S C R I P T  40:  G E N E R A T E   S E Q
#  =================================================
#
# THIS SCRIPT GENERATES A SEQ FILE FROM COORDINATES
def nmv_generateseq(projectname,inputfile):
  print "Generating sequence files."
  print "=========================="
  # SET THE PROJECT PATH
  path = nmv_adjust(nmvconf["NMRI_PROJECT"],projectname)
  # SET THE OUTPUT FILE
  outputfile = nmv_adjust(nmvconf["NMRI_SEQ"],'protein.seq')
  outputfile = os.path.join(path,outputfile)
  if os.path.exists(outputfile): os.remove(outputfile)
  # BUILD THE SEQ FILE
  nmrinfo_createsequence(inputfile,outputfile)
  print "Finished."

#  ======================================================================
#   S U B S C R I P T  41: R E N U M B E R   N O E S
#  ======================================================================
#
# RENUMBER NOES
def nmv_renumberrestraints(innoe,outnoe,type,offset,informat='XPLOR',outformat='XPLOR'):
  print "Renumbering restraint table:"
  print "%s"%innoe
  # OPEN FILE
  rin = restraint_file(innoe,'r',type,format=informat)
  rout = restraint_file(outnoe,'w',type,format=outformat)
  # READ THE INPUT
  rin.read()
  rin.renumber(offset)
  # WRITE TO OUTPUT
  rout.mwrite(rin.restraintlist)
  print "Renumbered restraint table:"
  print "%s"%outnoe
  print "Done"


#  ======================================================================
#   S U B S C R I P T  42: C R E A T E   P D B P I C S
#  ======================================================================
#
def nmv_createpdbpics(outputpath):
  # INDEX PDBFINDER
  print 'Building PDBFINDER index.'
  indexpath = '/tmp/pdbfinder.ind'
  pdbfinder = pdb_finder(nmvconf["PDBFINDER2"],'r')
  pdbfinder.buildindex()
  print '%i structures have been indexed.'%len(pdbfinder.recordpos.keys())
  # TAKE STUFF WITH LESS THEN 5000 RESIDUES
  pdblist = []
  for structure in pdbfinder.recordpos.keys():
    pdbfinder.read(structure)
    method  = pdbfinder.fieldvalue('Exp-Method')
    nres    = pdbfinder.fieldvalue('T-Nres-Prot')
    if method=='NMR' and nres > 1:
      pdblist.append(structure)
  print '%i structures have been kept.'%len(pdblist)
  # DIVIDE LIST
  for structure in pdblist:
    path = os.path.join(outputpath,structure.lower())
    if not os.path.exists('%s.jpg'%path):
      # RUN YASARA
      color = randint(0,180)
      macro=ysr_macro(nmvconf["YASARA_RUN"],errorfunc=error)
      macro.write(["ErrorExit On",
                   "Screensize 800,800",
                   "LoadPDB %s"%(nmv_adjust(nmvconf["PDB"],structure.lower())),
                   "DelObj !1",
                   "Colbg White",
                   "ColorAll Grey",
                   "ColorRes SecStr Helix, %s"%color,
                   "ColorRes SecStr Strand, %s"%color,
                   "Style Ribbon",
                   #"LabelAll Format=%s,Height=1.0,Color=White,X=0.0,Y=2.75,Z=0.0"%structure.upper(),
                   #"LabelPar Font=Arial,Height=1.0,Color=White,OnTop=0,Shrink=1,Fog=0",
                   "RayTrace %s.bmp,X=150,Y=150,Zoom=1.0,Atoms=Balls,LabelShadow=No"%path,
                   "Shell convert -quality 95 %s.bmp %s.jpg"%(path,path),
                   "Delfile %s.bmp"%path,
                   "Exit"])
      ret = macro.submit()
      # ADJUST PERMISSION FOR WEB SERVER
      if os.path.exists('%s.jpg'%path): os.chmod('%s.jpg'%path,0644)
      if ret:
        shutil.copy(macro.script,'%s_ERR.scr'%path)


#  ======================================================================
#   S U B S C R I P T  43: C R E A T E   Q U E E N  D I R S
#  ======================================================================
#
def nmv_mkqueendir(projectname):
  print "Creating QUEEN directory structure for project %s."%projectname
  # THE PROJECT DIR
  qn_createproject(nmvconf,projectname)
  print "Done."


#  ======================================================================
#   S U B S C R I P T  44:  Q U E E N   E X P O R T
#  ======================================================================
#
#  SCRIPT EXPORTS QUEEN
def nmv_exportqueen(path):
  # EXPORT ALL FUNCTIONS
  functions = ['PROGRESS INDICATOR CLASS',
               'ERROR FUNCTION GROUP',
               'LOGFILE FUNCTION GROUP',
               'MPI FUNCTION GROUP',
               'PDB FILE FUNCTION GROUP',
               'AVERAGING FUNCTION GROUP',
               'LIST FUNCTION GROUP',
               'DICTIONARY FUNCTION GROUP',
               'XPLOR FUNCTION GROUP',
               'QUEEN FUNCTION GROUP',
               'NMV FUNCTION GROUP',
               'NMR FUNCTION GROUP',
               'NMR RESTRAINTS FUNCTION GROUP',
               'NOMENCLATURE FUNCTION GROUP',
               'XPLOR CLASS',
               'YASARA MACRO CLASS',
               'GRACEPLOT CLASS',
               'XPLOR_SCRIPT CLASS',
               'NMR_RESTRAINT CLASS',
               'RESTRAINT_FILE CLASS',
               'QUEENBASE CLASS']
  # SET THE IMPORTS
  imports = 'string,os,sys,math,socket,time,shutil,copy,'+\
            'types,random,glob,fnmatch,nmv,pdb_file'
  # EXPORT
  nmv_export(functions,nmvconf["NMR_VALIBASE"],
             path,imports)

#  ======================================================================
#   S U B S C R I P T  44:  Q U E E N   E X P O R T
#  ======================================================================
#
#  SCRIPT EXPORTS QUEEN
def nmv_exportweb(path):
  # EXPORT ALL FUNCTIONS
  functions = ['DICTIONARY FUNCTION GROUP',
               'ERROR FUNCTION GROUP',
               'QUEEN FUNCTION GROUP',
               'QUEENBASE CLASS',
               'PDB FILE FUNCTION GROUP',
               'XPLOR FUNCTION GROUP',
               'XPLOR CLASS',
               'XPLOR_SCRIPT CLASS',
               'NMR_RESTRAINT CLASS',
               'RESTRAINT_FILE CLASS',
               'NMR RESTRAINTS FUNCTION GROUP',
               'EMAIL FUNCTION GROUP',
               'EMAIL CLASS',
               'DATABASE CLASS']
  # SET THE IMPORTS
  imports = 'string,os,sys,math,socket,time,shutil,copy,'+\
            'types,smtplib,random,glob,fnmatch,re,pdb_file,base64'
  # EXPORT
  nmv_export(functions,nmvconf["NMR_VALIBASE"],
             path,imports)
  print "Done."

#  ======================================================================
#   S U B S C R I P T  45: P R O C E S S   R E S T R A I N T   S E T
#  ======================================================================
#
# PROCESS RESTRAINTS SETS FROM AART
def nmv_processrestraints(path):
  # READ THE DIRECTORY
  dirlist = glob.glob(os.path.join(path,'1*'))
  # HANDLE THE DIRS
  for dir in dirlist:
    project = os.path.basename(dir)
    # CREATE PROJECT DIRS
    path = os.path.join(nmvconf["Q_PROJECT"],project)
    if not os.path.exists(path):
      qn_createproject(nmvconf,project)
    # SETUP QUEEN
    print "Setting up queen"
    print dirlist.index(dir), project
    queen = qn_setup(nmvconf,project,myid,numproc)
    xplr  = qn_setupxplor(nmvconf,project)
    psf = xplr.psf
    # COPY THE PSF FILE
    if not os.path.exists(psf):
      cns_mtf2psf(nmvconf["CNS"],
                  os.path.join(dir,"%s_cns.mtf"%project),
                  psf)
    realpdb = '/pdb/pdb%s.ent'%project
    projectpdb = os.path.join(dir,"%s.pdb"%project)
    xplorpdb = os.path.join(queen.pdb,"%s.pdb"%project)
    # CONVERT ORIG PDB TO XPLOR FORMAT
    print "Convert PDB file to separate XPLOR models."
    yas_splitpdb2xplor(nmvconf["YASARA_RUN"],realpdb,queen.pdb,project)
    yas_pdb2xplor(nmvconf["YASARA_RUN"],realpdb,xplorpdb)
    print "Extracted %i XPLOR models."%len(glob.glob("%s/*"%queen.pdb))
    # CREATE DISULFIDE FILE
    disu = xplr.disulfides
    if not os.path.exists(disu):
      qn_writedisulfides(realpdb,disu)
    # CREATE HISTIDINE PATCHES
    patc = xplr.patches
    if not os.path.exists(patc):
      qn_writehispatches(projectpdb,patc)
    if os.path.exists(xplr.psf): os.remove(xplr.psf)
    if os.path.exists(xplr.template): os.remove(xplr.template)
    if not os.path.exists(queen.sequence):
      # GET SEQUENCE
      qn_pdb2seq(projectpdb,queen.sequence)
    # READ ALL PATCHES
    patches = {}
    if os.path.exists(disu):
      patches.update(qn_readdisulfides(disu))
    # CHECK FOR OTHER PATCHES
    # WE SKIP 1FHT BECAUSE THIS STRUCTURE HAS NO PROTONS IN THE PDB
    if os.path.exists(patc) and project!='1fht':
      patches.update(qn_readpatches(patc))
    if not os.path.exists(xplr.template):
      # BUILD PSF FILE WITHOUT PATCHES
      xplor_buildstructure(xplr.psf,queen.sequence,'sequence',
                           xplr.topology,xplr.peptide,nmvconf["XPLOR"])
      # RENUMBER PSF
      oldpsf = "%s.prenum"%xplr.psf
      shutil.copy(xplr.psf,oldpsf)
      os.remove(xplr.psf)
      xplor_renumberpsf(oldpsf,xplr.psf,realpdb)
      # PATCH PSF
      tmppsf = "%s.prepat"%xplr.psf
      shutil.copy(xplr.psf,tmppsf)
      os.remove(xplr.psf)
      xplor_patchstructure(tmppsf,xplr.psf,patches)
    # BUILD TEMPLATE
    template = xplr.template
    if not os.path.exists(template):
      xplor_generatetemplate(template,psf)
    # PARSE THE NOE RESTRAINTS
    outtbl = nmv_adjust(queen.table,'noe')
    if not os.path.exists(outtbl):
      rfile_check(os.path.join(dir,'unambig.tbl'),outtbl)
      # GROUP THE RESTRAINTS
      rfile_group(outtbl)
    # PARSE THE HBONDS RESTRAINTS
    hbotbl = nmv_adjust(queen.table,'hbonds')
    oritbl = os.path.join(dir,'hbonds.tbl')
    if os.path.exists(oritbl) and not os.path.exists(hbotbl):
      rfile_check(oritbl,hbotbl)
    # PARSE THE DIHEDRAL RESTRAINTS
    dihtbl = nmv_adjust(queen.table,'dihedral')
    oritbl = os.path.join(dir,'dihedrals.tbl')
    if os.path.exists(oritbl) and not os.path.exists(dihtbl):
      rfile_check(oritbl,dihtbl,'DIHE')
    # CREATE DATASET FILE
    dataset = nmv_adjust(queen.dataset,'noe')
    if not os.path.exists(dataset):
      file = open(dataset,'w')
      content=''
      if os.path.exists(nmv_adjust(queen.table,'noe_IR')):
        content+="""NAME = Intra residual NOE restraints
  TYPE = DIST
  FILE = noe_IR
  //
  """
      if os.path.exists(nmv_adjust(queen.table,'noe_SQ')):
        content+="""NAME = Sequential NOE restraints
  TYPE = DIST
  FILE = noe_SQ
  //
  """
      if os.path.exists(nmv_adjust(queen.table,'noe_MR')):
        content+="""NAME = Medium range NOE restraints
  TYPE = DIST
  FILE = noe_MR
  //
  """
      if os.path.exists(nmv_adjust(queen.table,'noe_LR')):
        content+="""NAME = Long range NOE restraints
  TYPE = DIST
  FILE = noe_LR
  //
  """
      file.write(content)
      file.close()
    # CREATE SET FOR TESTING IR EFFECT
    dataset = nmv_adjust(queen.dataset,'all_noIR')
    if not os.path.exists(dataset):
      file = open(dataset,'w')
      content=''
      if os.path.exists(nmv_adjust(queen.table,'noe_SQ')):
        content+="""NAME = Sequential NOE restraints
  TYPE = DIST
  FILE = noe_SQ
  //
  """
      if os.path.exists(nmv_adjust(queen.table,'noe_MR')):
        content+="""NAME = Medium range NOE restraints
  TYPE = DIST
  FILE = noe_MR
  //
  """
      if os.path.exists(nmv_adjust(queen.table,'noe_LR')):
        content+="""NAME = Long range NOE restraints
  TYPE = DIST
  FILE = noe_LR
  //
  """
      if os.path.exists(hbotbl):
        content +="""NAME = Hydrogen bond restraints
  TYPE = DIST
  FILE = hbonds
  //
  """
      if os.path.exists(dihtbl):
        content +="""NAME = Dihedral angle restraints
  TYPE = DIHE
  FILE = dihedral
  //
  """
      file.write(content)
      file.close()
    # CREATE DATASET FILE
    dataset = nmv_adjust(queen.dataset,'all')
    if not os.path.exists(dataset):
      file = open(dataset,'w')
      content=''
      if os.path.exists(nmv_adjust(queen.table,'noe')):
        content+="""NAME = NOE restraints
  TYPE = DIST
  FILE = noe
  //
  """
      if os.path.exists(hbotbl):
        content +="""NAME = Hydrogen bond restraints
  TYPE = DIST
  FILE = hbonds
  //
  """
      if os.path.exists(dihtbl):
        content +="""NAME = Dihedral angle restraints
  TYPE = DIHE
  FILE = dihedral
  //
  """
      file.write(content)
      file.close()
    ok = os.path.join(path,'okidee')
    if not os.path.exists(ok):
      qn_checkdata(queen,xplr,'all_noIR')
      file = open(ok,'w')
##    for file in [realpdb,xplr.template,projectpdb]:
##      sum = 0
##      pdb = pdb_file.Structure(file)
##      for chain in pdb.peptide_chains:
##        for residue in chain:
##          for atom in residue.atom_list:
##            sum +=1
##      print sum, file
##    # CALCULATE SET INFORMATION
##    for set in ['all','noe']:
##      infofile = os.path.join(queen.outputpath,'setinfo_%s.dat'%set)
##      if not os.path.exists(infofile):
##        qn_setinformation(queen,xplr,set)
##      else:
##        print "Set information for set \"%s\" exists already!"%set


#  ======================================================================
#   S U B S C R I P T  46:  A N A L Y S E   R E S T R A I N T   S E T S
#  ======================================================================
#
def nmv_anarestraints(projectpath,outputpath,dataset):
  # ANALYSIS FLAGS
  fl_year, fl_rejected, fl_rmsd = 0, 0, 1
  # REJECT STRUCTURES WITH DISULFIDES
  reject_disu = 0
  # READ THE DIRECTORY
  dirlist = glob.glob(os.path.join(projectpath,'1*'))
  projectlist = []
  comments = ['#','@','&']
  for dir in dirlist:
    project = os.path.basename(dir)
    # FILTER FOR DISULFIDES
    if reject_disu:
      qplor = qn_setupxplor(nmvconf,os.path.basename(dir))
      if len(open(qplor.disulfides,'r').readlines())==0:
        projectlist.append(project)
    elif fl_rmsd:
      wpath = '/home/snabuurs/projects/intraresidual/'
      if len(glob.glob(os.path.join(wpath,"%s/pdb/%s_all_a_*.pdb"%(project,project))))==20:
        projectlist.append(project)
    else:
      projectlist.append(os.path.basename(dir))
  print len(projectlist)
  # HANDLE THE DIRS
  iuni, iset, shape, rmsd, nres, nr, nrej = {},{},{},{},{},{},{}
  years = {}
  wifdump = os.path.join(nmvconf["TMP"],'shape.dump')
  if os.path.exists(wifdump):
    dump = open(wifdump,'r')
    shape = cPickle.load(dump)
    rmsd = cPickle.load(dump)
    dump.close()
  for project in projectlist:
    print project
    # SET QUEEN
    queen = qn_setup(nmvconf,project,myid,numproc)
    qplor = qn_setupxplor(nmvconf,project)
    if fl_year:
      # GET YEAR OF STRUCTURE
      pdbfinder = pdb_finder(nmvconf["PDBFINDER2"],'r')
      pdbfinder.buildindex()
      pdbfinder.read(project)
      pdbyear = int(pdbfinder.fieldvalue(" Date")[:4])
      years[pdbyear]=years.get(pdbyear,0) + 1
    if fl_rejected:
      # READ RESTRAINTS IN DATASET
      datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
      rlist,rejected = [],[]
      for filedict in datasets:
        table = nmv_adjust(queen.table,filedict["FILE"])
        if filedict["TYPE"]=='DIST':
          r = restraint_file(table,'r',type=filedict["TYPE"])
          r.read()
          rlist += r.restraintlist
          rjtable = "%s.rejected"%table
          if os.path.exists(rjtable):
            rj = restraint_file(rjtable,'r',type=filedict["TYPE"])
            rj.read()
            rejected += rj.restraintlist
      nr[project]=[len(rlist),len(rejected)]
      print "Read %i restraints."%len(rlist)
      print "Read %i rejected restraints."%len(rejected)
      print "%4.1f %% of restraints rejected"%(float(len(rejected))/(len(rejected)+len(rlist))*100)
##    # READ Iuni FILE
##    infofile = os.path.join(queen.outputpath,'Iuni_%s.dat'%dataset)
##    if os.path.exists(infofile):
##      content = open(infofile,'r').readlines()
##      iunidict = {}
##      for line in content:
##        if line[0] not in comments:
##          line = string.split(line)
##          iunidict[line[-1][1:-1]]=float(line[1])
##    iuni[project]=iunidict
    # READ SETINFO FILE
    setfile  = os.path.join(queen.outputpath,'setinfo_%s.dat'%dataset)
    if os.path.exists(setfile):
      content = open(setfile,'r').readlines()
      setdict = {}
      if content[0][0]=='#': lines = content[1:4]
      else: lines = content[0:3]
      for line in lines:
        line = line.split()
        setdict[line[0]]=float(line[2])
    else:
      print "Calculating setinfo for %s"%project
      qn_setinformation(queen,qplor,'all')
    iset[project]=setdict
    # DETERMINE SHAPE
    if not os.path.exists(wifdump):
      #models = pdb_models("/pdb/pdb%s.ent"%project)
      models = 20
      shapelist = []
      log = os.path.join(nmvconf["TMP"],'wiflog.dat')
      script = wif_script(nmvconf["GWHATIF_RUN"])
      pdb = os.path.join(wpath,"%s/pdb/%s_all.pdb"%(project,project))
      script.write("GETMOL %s"%pdb)
#      script.write("Y")
      script.write("%s"%project)
      script.write("1000")
      for i in range(models):
        script.write("DOLOG %s.%i\n"%(log,i+1))
        script.write("%cigar")
        script.write("m%i 0"%(i+1))
        script.write("NOLOG")
      script.write("FULLSTOP Y")
      script.submit()
      for i in range(models):
        content = open("%s.%i"%(log,i+1),'r').readlines()
        sval = float(content[-2].split()[-1])
        shapelist.append(sval)
        print sval,
      print project, avg_list(shapelist)[0]
      shape[project]=avg_list(shapelist)[0]
      print avg_list(shapelist)[0]
      filelist = glob.glob(os.path.join(wpath,"%s/pdb/%s_all_a_*.pdb"%(project,project)))
      rmsdlist = prft_rmsd(filelist,'heavy')
      score = avg_list(rmsdlist)
      rmsd[project]=score[0]
  wif = open(wifdump,'w')
  cPickle.dump(shape,wif)
  cPickle.dump(rmsd,wif)
  wif.close()
  # DO THE ANALYSIS
  #################
  if fl_year:
    # PLOT DISTRUBITION OVER THE YEARS
    xmgr = graceplot(os.path.join(outputpath,'distr_years.dat'),'xy','w')
    xmgr.xlab = "Year"
    xmgr.ylab = "Structures"
    xmgr.writeheader()
    yrs = years.keys()
    miny = min(yrs)
    maxy = max(yrs)
    for year in range(miny,maxy+1):
      if years.has_key(year): xmgr.write([year,years[year]])
      else: xmgr.write([year,0])
    xmgr.close()
  if fl_rejected:
    xmgr = graceplot(os.path.join(outputpath,'perc_rejected.dat'),'xy','w')
    xmgr.xlab = "Dataset"
    xmgr.ylab = "Percentage restraints rejected"
    xmgr.writeheader()
    i = 0
    for key in nr.keys():
      perc = (float(nr[key][1])/(nr[key][0]+nr[key][1]))*100
      xmgr.write([i,perc,key])
      i+=1
    xmgr.close()
  if fl_rmsd:
    # Hstructure|R versus shape
    output = os.path.join(outputpath,'HstR_shape.dat')
    xmgr = graceplot(output,'xy','w')
    xmgr.xlab = "v1/0.5(v2+v3)"
    xmgr.ylab = "H\sstructure|R\N (bits/atom\S2\N)"
    xmgr.writeheader()
    values = []
    for project in projectlist:
      #xmgr.write([shape[project],iset[project]['Hstructure|R'],"%s-%5.2f"%(project,rmsd[project])])
      xmgr.write([shape[project],iset[project]['Hstructure|R'],"%i"%(int(round(rmsd[project])))])
      values.append([shape[project],iset[project]['Hstructure|R'],rmsd[project]])
    xmgr.close()
    xlist = []
    x = [1,6]
    y = [3,6]
    xstep = 0.05
    ystep = xstep
    c = 0.15
    cutoff = 0.5
    for i in range(x[0]/xstep,x[1]/xstep+1.0): xlist.append(i*xstep)
    ylist = []
    for i in range(y[0]/ystep,y[1]/ystep+1.0): ylist.append(i*ystep)
    avg_surface(xlist,ylist,values,c,cutoff)
##  # REJECTED RESTRAINTS
##  xmgr = graceplot(os.path.join(outputpath,'restraints_rejected.dat'),'xy','w')
##  xmgr.add2header("@g0 type Chart")
##  xmgr.add2header("@g0 stacked true")
##  xmgr.add2header("@with g0")
##  xmgr.add2header("@    world ymax 100")
##  xmgr.add2header("@    world xmin -1")
##  xmgr.add2header("@    xaxis  ticklabel type spec")
##  xmgr.add2header("@    xaxis  tick type spec")
##  xmgr.add2header("@    xaxis  tick spec %i"%(len(projectlist)*2))
##  tickcount =0
##  for p in projectlist:
##    xmgr.add2header("@    xaxis ticklabel %i, \"%s\""%(tickcount,
##                                                       os.path.basename(p)))
##    for i in range(2):
##      xmgr.add2header("@    xaxis  tick major %i, %i"%(tickcount,tickcount+1))
##      tickcount += 1
##  scount,count = 0,0
##  xmgr.add2header("@target G0.S%i"%scount)
##  xmgr.add2header("@type bar")
##  xmgr.add2header("@G0.S%i line type 0"%scount)
##  for p in projectlist:
##    xmgr.write([count,(nr[p][0]-nr[p][1])/float(nr[p][0])*100])
##    count +=1
##    xmgr.write([count, 0.0])
##    count += 1
##  # Itotal versus Hstructure|0
##  output = os.path.join(outputpath,'Itot_Hst0.dat')
##  xmgr = graceplot(output,'xy','w')
##  xmgr.xlab = "H\sstructure|0\N (bits/atom\S2\N)"
##  xmgr.ylab = "I\stotal\N (bits/atom\S2\N)"
##  xmgr.writeheader()
##  for project in projectlist:
##    xmgr.write([iset[project]['Hstructure|0'],iset[project]['Itotal'],project])
##  xmgr.close()
##  # Itotal versus Hstructure|R
##  output = os.path.join(outputpath,'Itot_HstR.dat')
##  xmgr = graceplot(output,'xy','w')
##  xmgr.xlab = "H\sstructure|R\N (bits/atom\S2\N)"
##  xmgr.ylab = "I\stotal\N (bits/atom\S2\N)"
##  xmgr.writeheader()
##  for project in projectlist:
##    xmgr.write([iset[project]['Hstructure|R'],iset[project]['Itotal'],project])
##  xmgr.close()
##  # Itotal versus Nres
##  output = os.path.join(outputpath,'Itot_Nres.dat')
##  xmgr = graceplot(output,'xy','w')
##  xmgr.xlab = "Number of residues."
##  xmgr.ylab = "I\stotal\N (bits/atom\S2\N)"
##  xmgr.writeheader()
##  for project in projectlist:
##    xmgr.write([nres[project],iset[project]['Itotal'],project])
##  xmgr.close()
##  # Hstructure|0 versus Nres
##  output = os.path.join(outputpath,'Hst0_Nres.dat')
##  xmgr = graceplot(output,'xy','w')
##  xmgr.xlab = "Number of residues."
##  xmgr.ylab = "H\sstructure|0\N (bits/atom\S2\N)"
##  xmgr.writeheader()
##  for project in projectlist:
##    xmgr.write([nres[project],iset[project]['Hstructure|0'],project])
##  xmgr.close()
##  # Itotal versus shape
##  output = os.path.join(outputpath,'Itot_shape.dat')
##  xmgr = graceplot(output,'xy','w')
##  xmgr.xlab = "v1/0.5(v2+v3)"
##  xmgr.ylab = "I\stotal\N (bits/atom\S2\N)"
##  xmgr.writeheader()
##  for project in projectlist:
##    xmgr.write([shape[project],iset[project]['Itotal'],project])
##  xmgr.close()
##  # Hstructure|0 versus shape
##  output = os.path.join(outputpath,'Hst0_shape.dat')
##  xmgr = graceplot(output,'xy','w')
##  xmgr.xlab = "v1/0.5(v2+v3)"
##  xmgr.ylab = "H\sstructure|0\N (bits/atom\S2\N)"
##  xmgr.writeheader()
##  for project in projectlist:
##    xmgr.write([shape[project],iset[project]['Hstructure|0'],project])
##  xmgr.close()
##  # Hstructure|R versus shape
##  output = os.path.join(outputpath,'HstR_shape.dat')
##  xmgr = graceplot(output,'xy','w')
##  xmgr.xlab = "v1/0.5(v2+v3)"
##  xmgr.ylab = "H\sstructure|R\N (bits/atom\S2\N)"
##  xmgr.writeheader()
##  for project in projectlist:
##    xmgr.write([shape[project],iset[project]['Hstructure|R'],project])
##  xmgr.close()


#  ======================================================================
#   S U B S C R I P T  47:  A N A L Y Z E   I R   R E S T R A I N T S
#  ======================================================================
#
def nmv_analyzeir(queensetpath):
  # GET SETLIST
  setlist = glob.glob(os.path.join(queensetpath,"1*"))
  # STRUCTURES FOR WHICH NO CONVERGENCE IS FOUND...
  skiplist = ['1bbn','1cfc','1cw6','1d8v','1d9a','1e5b','1e8p','1ef5',\
+             '1eza','1ezo','1f7e','1f7m','1fad','1bf0','1e3y','1e8q',\
              '1e41','1e9k','1eot','1e8l','1ab7','1bno','1c05','1c06',\
              '1d1r','1e5c','1dx7','1du1']
  setlist = setlist
  # SET THE RANGE FOR MPI RUNS
  mylower,myupper = mpi_setrange(setlist,myid,numproc)
  # CYCLE ALL SETS
  for setpath in setlist[mylower:myupper]:
    project = os.path.basename(setpath)
    # CHECK IF SET CAN BE DONE
    if len(glob.glob(os.path.join(setpath,'pdb/*'))) > 0 and project not in skiplist:
      dataset = 'all'
      # AND GO!
      print "Setting up for %s."%project
      # SET INTRA RESIDUAL PROJECT DIRECTORY
      intra_path = nmvconf["INTRA_PATH"]
      projectpath = os.path.join(intra_path,project)
      pdbpath = os.path.join(projectpath,'pdb')
      if not os.path.exists(projectpath):
        print projectpath
        os.mkdir(projectpath)
        os.mkdir(pdbpath)
      # SETUP QUEEN AND XPLOR
      queen = qn_setup(nmvconf,project,myid,numproc)
      xplr  = qn_setupxplor(nmvconf,project)
      # READ RESTRAINTS IN DATASET
      datasets = [dataset,"%s_noIR"%dataset]
      rsets,quadict = [],{}
      for dat in datasets:
        print "\n## Reading data for dataset %s. ##"%dat
        # READ DATA
        data = qn_readdatafile(nmv_adjust(queen.dataset,dat))
        restraintlist = []
        for filedict in data:
          table = nmv_adjust(queen.table,filedict["FILE"])
          r = restraint_file(table,'r',type=filedict["TYPE"])
          r.read()
          restraintlist += r.restraintlist
        rsets.append(restraintlist)
        # CALCULATE STRUCTURES
        print "Converting MTF file."
        mtf = os.path.join(pdbpath,'protein.mtf')
        if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
        nstruct = 20
        print "Calculating %i structures."%nstruct
        pdbbase = os.path.join(pdbpath,"%s_%s"%(project,dat))
        # CHECK IF STRUCTURES EXIST
        pdblist = glob.glob("%s_a_*.pdb"%pdbbase)
        if len(pdblist)!=nstruct:
          cns_calcstructure(pdbbase,
                            xplr.template,
                            mtf,
                            restraintlist,
                            naccepted=nstruct)
        else:
          print "Structures already calculated!"
        # JOIN STRUCTURES IN ENSEMBLE
        pdblist = glob.glob("%s_a_*.pdb"%pdbbase)
        ensemble = "%s.pdb"%pdbbase
        print "Joining structures into an ensemble."
        if len(pdblist)!=nstruct:
          print "Structure calculations did not converge for %s!"%project
        if not os.path.exists(ensemble):
          yas_joinpdb(nmvconf["YASARA_RUN"],pdblist,ensemble,xplorflag=1)
        quafile = "%s.qua"%pdbbase
        if not os.path.exists(quafile):
          print "Generating quality file for ensemble."
          pdb_getqua(ensemble,quafile)
        # READ THE QUALITY FILE
        pdbfinder = pdb_finder(quafile,"r",1,error)
        pdbfinder.read()
        qua = pdbfinder.fieldvalue(" Quality")
        qdict = {}
        qdict[" Quality"]=float(qua)
        for el in ["  Phi/psi","  Backbone","  Packing 1","  Rotamer","  Chi-1/chi-2"]:
          qua = pdbfinder.fieldvalue(el)
          qua = qua.split('|')
          qua = float(qua[1])
          qdict[el]=qua
        quadict[dat]=qdict
      # BUILD A LIST OF THE IR RESTRAINTS
      print "\n## Sifting out intra-residual restraints. ##"
      table = nmv_adjust(queen.table,'noe_IR')
      if os.path.exists(table):
        r = restraint_file(table,'r',type="DIST")
        r.read()
        ir = r.restraintlist
      else:
        ir = []
      #ir = [val for val in rsets[0] if val not in rsets[1]]
      print "\nFound %i IR restraints."%(len(ir))
      sumfile = os.path.join(projectpath,'summary.dat')
      out = open(sumfile,'w')
      out.write("## %4s ##\n##########\n\n"%project)
      results = []
      # CHECK ACCEPTANCE
      for dat in datasets:
        print "\n## Checking acceptance for dataset %s ##"%dat
        pdbbase = os.path.join(pdbpath,"%s_%s"%(project,dat))
        # GET LIST OF ACCEPTED STRUCTURES
        pdbsel = "%s_a_*.pdb"%pdbbase
        pdblist = glob.glob(pdbsel)
        viol,rviol = xplor_violations(pdblist,xplr.psf,ir)
        results.append([viol,rviol])
      nstr = float(len(pdblist))
      # SORT OUT RESTRAINTS
      distlist,dihelist = [],[]
      for r in ir:
        if r.type=='DIST': distlist.append(r)
        if r.type=='DIHE': dihelist.append(r)
      # WRITE OUTPUT FILES
      viol_IR = results[0][0]
      violnIR = results[1][0]
      rviol_IR = results[0][1]
      rviolnIR = results[1][1]
      if len(dihelist)>0: types = ["DIST","DIHE"]
      else: types = ["DIST"]
      for type in types:
        out.write("## %s ##\n"%type)
        if len(ir)>0:
          perc = (violnIR["DIST"][">=0.5"]/(nstr*float(len(ir))))*100
        else:
          perc = 0.0
        out.write("%5i IR restraints - %5.2f %% violates\n"%(len(ir),perc))
        keys = viol_IR[type].keys()
        keys.sort()
        out.write("%5s %13s %13s\n"%("viol","with IR","without IR"))
        for key in keys:
          out.write("%5s %5.1f (%5i) %5.1f (%5i) %13.1f\n"%(key,
                                                            viol_IR[type][key]/nstr,
                                                            viol_IR[type][key],
                                                            violnIR[type][key]/nstr,
                                                            violnIR[type][key],
                                                            violnIR[type][key]/nstr-viol_IR[type][key]/nstr))
        out.flush()
        # calculate rms
        rms_IR,rms_nIR = 0,0
        if type == "DIST": list = distlist
        if type == "DIHE": list = dihelist
        for el in list:
          for viol in rviol_IR[str(el)]:
            rms_IR+=viol**2
          for viol in rviolnIR[str(el)]:
            rms_nIR+=viol**2
        if len(ir)>0:
          rms_IR = math.sqrt(rms_IR/(len(list)*nstr))
          rmsnIR = math.sqrt(rms_nIR/(len(list)*nstr))
        else:
          rms_IR = 0.0
          rmsnrIR = 0.0
        out.write("%5s %13.4f %13.4f %13.4f\n\n"%('rms',rms_IR,rmsnIR,rmsnIR-rms_IR))
      # write quality
      for key in quadict['all'].keys():
        keysh = string.strip(key)
        diff = abs(quadict['all'][key]-quadict['all_noIR'][key])
        sign = ' '
        if quadict['all'][key]<quadict['all_noIR'][key]:
          sign = '+'
        elif quadict['all'][key]>quadict['all_noIR'][key]:
          sign = '-'
        perc = abs(((quadict['all'][key]-quadict['all_noIR'][key])/quadict['all'][key])*100)
        out.write("%5s %13.3f %13.3f %13.2f%s%%\n"%(keysh[:5],
                                                    quadict['all'][key],
                                                    quadict['all_noIR'][key],
                                                    perc,
                                                    sign))
      out.write("\n")
##        if dat == "%s_noIR"%dataset:
##          # READ UNCERTAINTY FILE
##          unifile = os.path.join(queen.outputpath,'Iuni_%s.dat'%datasets[0])
##          inf = qn_readinffile(unifile)
##          # MAKE OUTPUT
##          outputfile = os.path.join(projectpath,'vcount_%s_vs_iuni.agr'%dat)
##          xmgr = graceplot(outputfile,'xy','w')
##          xmgr.xlab = "I\suni"
##          xmgr.ylab = "Number of violations of %i restraints in %s structures."%(len(ir),nstruct)
##          xmgr.writeheader()
##          for key in rviol.keys():
##            count = 0
##            for el in rviol[key]:
##              if el >=0.5:
##                count += 1
##            xmgr.write([inf[key][0],count,key])
##          xmgr.close()


#  =====================================================================
#   S U B S C R I P T  48: A N A L Y Z E  W A T R E F
#  ======================================================================
#
def nmv_analyzewatref(path):
  cutoff = 120
  # SET SOME CHECK FLAGS
  plotqua = 0
  violcheck = 0
  rcheck = 0
  builddress = 0
  setproperties = 0
  rperres = 1
  queenstuff = 0
  # PLOT PARAMETERS : [minval,maxval,stepszie]
  plotpar = {"Number of bumps per 100 residues":         [0,380,10],
             "Bond lengths":                             [0,1.80,0.1],
             "2nd generation packing quality":           [-10,3,1],
             "Overall Quality (According to E.Krieger)": [-110,0,5],
             "Unsatisfied buried hydrogen donors":       [0,70,5],
             "Allowed regions":                          [0,100,5],
             "Most favoured regions":                    [0,100,5],
             "Bond angles":                              [0,2.8,0.1],
             "Inside/Outside distribution":              [0.7,1.7,0.05],
             "Side chain planarity":                     [0,5.2,0.25],
             "1st generation packing quality":           [-10,2,1],
             "Ramachandran plot appearance":             [-10,2,1],
             "Generously allowed regions":               [0,50,2.5],
             "Average number of bumps":                  [0,500,10],
             "Backbone conformation":                    [-24,2,1],
             "Omega angle restraints":                   [0,2.2,0.1],
             "Average sum of bumps":                     [0,80,2],
             "Disallowed regions":                       [0,50,2.5],
             "chi-1/chi-2 rotamer normality":            [-6,5,1],
             "Unsatisfied buried hydrogen acceptors":    [0,5,1],
             "Improper dihedral distribution":           [0,2,0.1]}
  # BUILD DATABASE
  dbdict = {}
  # BUILD LIST OF PROJECTS
  allprojects = glob.glob(os.path.join(path,'*'))
  # SET SOME PATHS
  analysispath = os.path.join(path,'analysis')
  dressdbpath = '/home/snabuurs/secondary_data/dress/'
  dbpath = os.path.join(dressdbpath,'dress.db')
  # LIST OF EXCLUDED ID'S
  skiplist = ['analysis','1d8v','1c05','1c06','1e8l']
  # BUILD A CLEAN LIST OF PROJECTS
  projects = []
  for project in allprojects:
    name = os.path.basename(project)
    if name not in skiplist:
      projects.append(project)
      # ADD TO DB
      dbdict["ID"]=dbdict.get("ID",[])+[name]
  dbdict["ID"]=dbdict["ID"][:cutoff]
  # SKIP ANALYSIS DIRECTORY, CREATE IT IF IT DOESN'T EXIST
  if not os.path.exists(analysispath): os.mkdir(analysispath)
  # PLOT QUALITY
  deltaqua = {}
  if plotqua:
    # CYCLE AND ANALYZE THE PROJECTS
    quality, qua_all = {},{}
    for projectpath in projects[:cutoff]:
      list = glob.glob(os.path.join(projectpath,"%s_input/%s_*.pdb"%(set,set)))
      projectname = os.path.basename(projectpath)
      print "Parsing %s."%projectname
      # SET INPUT AND REFINED SUMMARY PATH
      ref_summary = os.path.join(projectpath,"refined_input/summary_refined.txt")
      inp_summary = os.path.join(projectpath,"analyzed_input/summary_analyzed.txt")
      qualist = []
      # CYCLE FILES
      summaries = [inp_summary,ref_summary]
      for i in range(len(summaries)):
        readflag = 0
        qua = {}
        # READ THE FILE
        inp = open(summaries[i],'r').readlines()
        for line in inp:
          line = line[:-1]
          # ONLY READ THE QUALITY SCORES HERE
          if not readflag:
            if line.find("PROCHECK")>-1: readflag=1
          else:
            # SKIP COMMENTS AND NON-INFORMATIVE LINES
            if line.find(':')>-1 and line[0]!='#' and len(line.split(':')[1])>1:
              line = line.split(':')
              # FILL QUALITY DICT
              score = float(line[1].split('+-')[0])
              sd = float(line[1].split('+-')[1])
              name = line[0].strip()
              qua[name]=[score,sd]
              # ADD TO DB
              dbval = "%7.2f +/- %7.2f"%(score,sd)
              if i == 0: dbkey = "INP-%s"%name
              elif i == 1: dbkey = "REF-%s"%name
              dbdict[dbkey]=dbdict.get(dbkey,[])+[dbval]
              qua_all[name] = qua_all.get(name,[])+[score]
              if name=="Overall Quality (According to E.Krieger)":
                qualist.append(score)
        # ADD TO QUALITY DICT
        quality[projectname]=quality.get(projectname,[])+[qua]
      # ADD TO DELTA DICT
      deltaqua[projectname]=abs(qualist[0]-qualist[1])
    # CREATE DELTA PLOT
    dplot = os.path.join(analysispath,'dqua.dat')
    file = open(dplot,'w')
    dq = deltaqua.items()
    dq.sort(lambda (k1,v1),(k2,v2): cmp(v2,v1) ) # sort by value, not by key
    for element in dq:
      file.write("%s %8.4f\n"%(element[0],element[1]))
    file.close()
    # CREATE SUMMARY
    summary = os.path.join(analysispath,'summary.dat')
    sum = open(summary,'w')
    # CREATE PLOTS
    for key in qua_all.keys():
      print "Generating plots for:"
      print key
      basename = os.path.join(analysispath,key.replace(' ','_').replace('/','-'))
      # SEPARATE REF SCORES FROM UNREF SCORES
      scores = {}
      for i in range(len(qua_all[key])):
        if i%2==0: scores['inp']=scores.get('inp',[]) + [qua_all[key][i]]
        else: scores['ref']=scores.get('ref',[]) + [qua_all[key][i]]
      # SUMMARY
      sum.write("%s\n"%key)
      inpavg = avg_list(scores['inp'])
      refavg = avg_list(scores['ref'])
      sum.write("inp : %5.2f +/- %5.2f\n"%(inpavg[0],inpavg[1]))
      sum.write("ref : %5.2f +/- %5.2f\n"%(refavg[0],refavg[1]))
      # CREATE PLOTS
      for set in ['inp','ref']:
        plotpath = "%s_%s.dat"%(basename,set)
        xmgr = graceplot(plotpath,'bar','w')
        xmgr.xlab = "%s"%key
        xmgr.ylab = "Counts"
        xmgr.writeheader()
        minval = plotpar[key][0]
        maxval = plotpar[key][1]
        step =   plotpar[key][2]
        # CREATE TEN BINS FOR EACH PLOT
        bins = {}
        pos = minval
        while pos <= maxval:
          bins[pos]=0
          pos += step
        # FILL THE BINS
        count = 0
        for val in scores[set]:
          binlist = bins.keys()
          binlist.sort()
          for bin in binlist:
            if val<=bin+0.5*step and val>bin-0.5*step:
              bins[bin]+=1
              count += 1
              break
        # MAKE THE PLOT
        count = 0
        for bin in binlist:
          xmgr.write([bin, bins[bin]])
          count += bins[bin]
        xmgr.close()
  if queenstuff:
    count = 0
    dataset = 'noe'
    sums = {'A':{},
            'N':{}}
    for projectpath in projects[:cutoff]:
      projectname = os.path.basename(projectpath)
      qpath = os.path.join(nmvconf["Q_PROJECT"],projectname)
      if os.path.exists(qpath):
        # SET UP QUEEN
        print "Setting up QUEEN for %s"%projectname
        queen = qn_setup(nmvconf,projectname,myid,numproc)
        xplr  = qn_setupxplor(nmvconf,projectname)
        setinfo = os.path.join(queen.outputpath,"setinfo_%s.dat"%dataset)
        if os.path.exists(setinfo):
          count += 1
          print projectname, count
          content = open(setinfo,'r').readlines()
          setdict = {}
          if content[0][0]=='#':
            lines1 = content[1:4]
            lines2 = content[7:]
          else:
            lines1 = content[0:3]
            lines2 = content[6:]
          for line in lines1:
            line = line.split()
            setdict[line[0]]=float(line[2])
          for line in lines2:
            line = line.split()
            sums["A"][line[4]]=sums["A"].get(line[4],[])+[float(line[0])]
            sums["N"][line[4]]=sums["N"].get(line[4],[])+[float(line[3])]
        else:
          # fix for 1du1
          if projectname == '1du1':
            table =  nmv_adjust(queen.table,'noe')
            rfile_check(table)
            rfile_group(table)
          qn_setinformation(queen,xplr,dataset)
          count += 1
          print projectname, count
    for key1 in sums.keys():
      print key1
      for key in sums[key1].keys():
        list = sums[key1][key]
        while len(list)<102:
          list.append(0.0)
        print key, avg_list(list)
  if rcheck:
    rdistcutoff = [0.1,0.3,0.5]
    rdihecutoff = [1.0,3.0,5.0]
    outputpath = os.path.join(analysispath,'rcheck')
    consistent = {'analyzed':[],
                  'refined':[]}
    numviol = {'analyzed':{},
               'refined':{}}
    for i in range(1,501):
      numviol['analyzed'][float(i)/10]=0
      numviol['refined'][float(i)/10]=0
    numlist = numviol['analyzed'].keys()
    numlist.sort()
    # CYCLE THE PROJECTS
    for projectpath in projects[:cutoff]:
      projectname = os.path.basename(projectpath)
      print "Checking violations in %s."%projectname
      nmvconf["Q_PROJECT"] = '/home/snabuurs/projects/watref/'
      # SET UP QUEEN
      print "Setting up QUEEN"
      queen = qn_setup(nmvconf,projectname,myid,numproc)
      xplr  = qn_setupxplor(nmvconf,projectname)
      # FOR CHRIS HIS 'CLEAN' VERSIONS
      xplr.psf = os.path.join(projectpath,"data/sequence/protein_clean.psf")
      # READ RESTRAINTS
      rlist = []
      for el in ['noe','hbonds','dihedral']:
        rfile = nmv_adjust(queen.table,'%s_clean'%el)
        if os.path.exists(rfile):
          type = 'DIST'
          if el=='dihedral': type='DIHE'
          r = restraint_file(rfile,'r',type=type)
          r.read()
          rlist+=r.restraintlist
      for set in ['analyzed','refined']:
        conscount = 0
        # BUILD LIST OF PDB FILES
        list = glob.glob(os.path.join(projectpath,"%s_input/%s_*.pdb"%(set,set)))
        # BUILD TOPSTR
        topval = ((len(list)/10)+1)*10
        topval = len(list)
        topstr = ''
        i = 1
        while i <= topval:
          if (i+1)%10==0 or i==1:
            if i!=1: topstr+="%i"%(i+1)
            else: topstr+="1"
            i+=len("%i"%(i+1))
          elif i%5==0 and i%10!=0:
            topstr+="."
            i+=1
          elif i==topval:
            val = "%i"%topval
            topstr+=val[-1]
            i+=1
          else:
            topstr+=" "
            i+=1
        # SORT OUT RESTRAINTS
        outputfile = os.path.join(outputpath,'%s_viol_%s.dat'%(projectname,
                                                               set))
        file = open(outputfile,'w')
        file.write('Ensemble\n')
        file.write('========\n')
        file.write('%i structures in ensemble.\n'%len(list))
        file.write('Index number below refer to the numbers used in\n')
        file.write('the following violation analyses.\n\n')
        file.write('index\tfilename\n')
        sortedlist = []
        for i in range(1,len(list)+1):
          filename = os.path.join(projectpath,"%s_input/%s_%i.pdb"%(set,set,i))
          file.write("%i\t%s\n"%(i,os.path.basename(filename)))
          sortedlist.append(filename)
        list = sortedlist
        file.write('\n')
        # CHECK VIOLATIONS
        viol,rviol=xplor_violations(list,xplr.psf,rlist)
        for type in ['DIST','DIHE']:
          typelist = [el for el in rlist if el.type==type]
          if type=='DIST' and len(typelist)>0:
            rcutoff = rdistcutoff
            file.write('Distance restraints\n')
            file.write('===================\n')
            file.write('_ = violation > %.1f A.\n~ = violation > %.1f A.\n'%(rcutoff[0],
                                                                             rcutoff[1]))
            file.write('* = violation > %.1f A.\n'%rcutoff[2])
            file.write('Vmax = maximum violation in A.\n\n')
            file.write('%s  Vmax restraint\n'%topstr)
          if type=='DIHE' and len(typelist)>0:
            rcutoff = rdihecutoff
            file.write('Dihedral angle restraints\n')
            file.write('=========================\n')
            file.write('_ = violation > %.1f degress.\n~ = violation > %.1f degrees.\n'%(rcutoff[0],rcutoff[1]))
            file.write('* = violation > %.1f degrees.\n'%rcutoff[2])
            file.write('Vmax = maximum violation in degrees.\n\n')
            file.write('%s  Vmax restraint\n'%topstr)
          for r in typelist:
            stri = ''
            consr = 0
            for elem in rviol[str(r)]:
              if elem >= rcutoff[2]:
                stri+='*'
                consr += 1
              elif elem >= rcutoff[1]:
                stri+='~'
                consr += 1
              elif elem >= rcutoff[0]:
                stri+='_'
              else:
                stri+='.'
              # COUNT THE VIOLATIONS
              if r.type=='DIST':
                cv = 0
                found = 0
                while not found:
                  if elem==0.0:
                    found = 1
                  elif elem <= numlist[cv]:
                    found = 1
                    numviol[set][numlist[cv]]+=1
                    if elem > 5.0:
                      print "#############"
                      print elem
                      print str(r)
                  elif cv==len(numlist)-1:
                    found = 1
                  else:
                    cv+=1
            file.write("%s %5.2f %s\n"%(string.ljust(stri,topval),max(rviol[str(r)]),str(r)))
            if consr > 0.5*len(list) and type=='DIST' and len(list)>=10:
              conscount += 1
          file.write("\n")
        if len(list)>10:
          consistent[set].append(conscount)
        file.close()
      for key in consistent.keys():
        print key, avg_list(consistent[key])
    for el in numlist:
      print "%4.2f %8i %8i"%(el,numviol['analyzed'][el],numviol['refined'][el])
  if violcheck:
    output = os.path.join(analysispath,'violations.dat')
    out = open(output,'w')
    dist_rms_inp, dist_rms_ref, dihe_rms_inp, dihe_rms_ref = [],[],[],[]
    # CHECK VIOLATIONS
    for projectpath in projects[:cutoff]:
      projectname = os.path.basename(projectpath)
      print "Checking violations in %s."%projectname
      # READ DATASET ALL
      dataset='all'
      nmvconf["Q_PROJECT"] = '/home/snabuurs/projects/watref/'
      print "Setting up QUEEN"
      queen = qn_setup(nmvconf,projectname,myid,numproc)
      xplr  = qn_setupxplor(nmvconf,projectname)
      # DIRTY HACK FOR CHRIS' CLEAN UPS
      queen.table = os.path.join(queen.path,"data/restraints/????_clean.tbl")
      dataset = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
      rlist = []
      # CYCLE ALL AVAILABLE SETS
      for filedict in dataset:
        # CONSTRUCT THE TABLE PATH
        tblpath = nmv_adjust(queen.table,filedict["FILE"])
        # READ THE TABLE
        r = restraint_file(tblpath,'r',type=filedict["TYPE"])
        r.read()
        # STORE PARSED RESTRAINTS FOR FUTURE USE
        rlist += r.restraintlist
      # BUILD LIST OF REFINED PDB FILE
      ref_list = glob.glob(os.path.join(projectpath,"refined_input/refined_*.pdb"))
      # BUILD LIST OF REFINED INPUT FILE
      inp_list = glob.glob(os.path.join(projectpath,"analyzed_input/analyzed_*.pdb"))
      if len(ref_list)!=len(inp_list): error("oops!")
      # DIRTY HACK FOR CHRIS' CLEAN UPS
      xplr.psf = os.path.join(projectpath,"data/sequence/protein_clean.psf")
      # SORT OUT RESTRAINTS
      distlist,dihelist = [],[]
      for r in rlist:
        if r.type=='DIST': distlist.append(r)
        if r.type=='DIHE': dihelist.append(r)
      # CHECK VIOLATIONS IN INPUT
      viol_inp,rviol_inp=xplor_violations(inp_list,xplr.psf,rlist)
      viol_ref,rviol_ref=xplor_violations(ref_list,xplr.psf,rlist)
      keys = viol_inp["DIST"].keys()
      keys.sort()
      dkeys = viol_inp["DIHE"].keys()
      dkeys.sort()
      nstr = float(len(inp_list))
      dbdict['nstructures']=dbdict.get('nstructures',[])+[str(int(nstr))]
      out.write("####\n%s\n####\n"%projectname)
      out.write("Distance restraints:\n")
      out.write("%5s %11s %11s\n"%("viol","input","refined"))
      for key in keys:
        out.write("%5s %4.1f (%4i) %4.1f (%4i)\n"%(key,
                                                   viol_inp["DIST"][key]/nstr,
                                                   viol_inp["DIST"][key],
                                                   viol_ref["DIST"][key]/nstr,
                                                   viol_ref["DIST"][key]))
      # violations bigger than 0.5
      dbdict["INP-0.5"]=dbdict.get("INP-0.5",[])+[str(viol_inp["DIST"][">=0.5"]/nstr)]
      dbdict["REF-0.5"]=dbdict.get("REF-0.5",[])+[str(viol_ref["DIST"][">=0.5"]/nstr)]
      # violations bigger than 0.3
      inpsum = viol_inp["DIST"][">=0.5"]/nstr + viol_inp["DIST"]["< 0.5"]/nstr + \
               viol_inp["DIST"]["< 0.4"]/nstr
      refsum = viol_ref["DIST"][">=0.5"]/nstr + viol_ref["DIST"]["< 0.5"]/nstr + \
               viol_ref["DIST"]["< 0.4"]/nstr
      dbdict["INP-0.3"]=dbdict.get("INP-0.3",[])+[str(inpsum)]
      dbdict["REF-0.3"]=dbdict.get("REF-0.3",[])+[str(refsum)]
      # calculate rms
      rms_ref,rms_inp = 0,0
      for el in distlist:
        for viol in rviol_ref[str(el)]:
          rms_ref+=viol**2
        for viol in rviol_inp[str(el)]:
          rms_inp+=viol**2
      rmsinp = math.sqrt(rms_inp/(len(distlist)*nstr))
      rmsref = math.sqrt(rms_ref/(len(distlist)*nstr))
      out.write("%5s %11.4f %11.4f\n"%('rms',
                                       rmsinp,
                                       rmsref))

      dist_rms_inp.append(rmsinp)
      dist_rms_ref.append(rmsref)
      # ADD TO DB
      dbdict["INP-distrms"]=dbdict.get("INP-distrms",[])+[str(rmsinp)]
      dbdict["REF-distrms"]=dbdict.get("REF-distrms",[])+[str(rmsref)]
      if len(dihelist)>0:
        out.write("Dihedral restraints:\n")
        out.write("%5s %11s %11s\n"%("viol","input","refined"))
        for key in dkeys:
          out.write("%5s %4.1f (%4i) %4.1f (%4i)\n"%(key,
                                                     viol_inp["DIHE"][key]/nstr,
                                                     viol_inp["DIHE"][key],
                                                     viol_ref["DIHE"][key]/nstr,
                                                     viol_ref["DIHE"][key]))
        # violations bigger than 5 degress
        dbdict["INP-5.0"]=dbdict.get("INP-5.0",[])+[str(viol_inp["DIHE"][">=5.0"]/nstr)]
        dbdict["REF-5.0"]=dbdict.get("REF-5.0",[])+[str(viol_ref["DIHE"][">=5.0"]/nstr)]
        # calculate rms
        rms_ref,rms_inp = 0,0
        for el in dihelist:
          for viol in rviol_ref[str(el)]:
            rms_ref+=viol**2
          for viol in rviol_inp[str(el)]:
            rms_inp+=viol**2
        rmsinp = math.sqrt(rms_inp/(len(dihelist)*nstr))
        rmsref = math.sqrt(rms_ref/(len(dihelist)*nstr))
        out.write("%5s %11.4f %11.4f\n"%('rms',
                                         rmsinp,
                                         rmsref))
        dihe_rms_inp.append(rmsinp)
        dihe_rms_ref.append(rmsref)
      else:
        dbdict["INP-5.0"]=dbdict.get("INP-5.0",[])+['']
        dbdict["REF-5.0"]=dbdict.get("REF-5.0",[])+['']
      if len(dihelist)>0:
        dbdict["INP-diherms"]=dbdict.get("INP-diherms",[])+[str(rmsinp)]
        dbdict["REF-diherms"]=dbdict.get("REF-diherms",[])+[str(rmsref)]
      else:
        dbdict["INP-diherms"]=dbdict.get("INP-diherms",[])+['']
        dbdict["REF-diherms"]=dbdict.get("REF-diherms",[])+['']
      # CALCULATE DISTRIBUTION OF NEW VIOLATIONS
      newviol,oldviol = [],[]
      for r in distlist:
        re = str(r)
        for i in range(len(rviol_inp[re])):
          if rviol_ref[re][i] > 0.0: newviol.append(r)
          if rviol_inp[re][i] > 0.0: oldviol.append(r)
      out.write("Distribution of input violations.\n")
      group = r_group(oldviol)
      keys = group.keys()
      keys.sort()
      for key in keys:
        out.write("%s %4i %5.2f %%\n"%(key,
                                       len(group[key]),
                                       float(len(group[key]))/len(oldviol)*100))
        print "%s %4i %5.2f %%"%(key,
                                 len(group[key]),
                                 float(len(group[key]))/len(oldviol)*100)
      out.write("Distribution of refined violations.\n")
      group = r_group(newviol)
      keys = group.keys()
      keys.sort()
      for key in keys:
        out.write("%s %4i %5.2f %%\n"%(key,
                                     len(group[key]),
                                     float(len(group[key]))/len(newviol)*100))
        print "%s %4i %5.2f %%"%(key,
                                 len(group[key]),
                                 float(len(group[key]))/len(newviol)*100)
      out.flush()
    # WRITE OVERALL RMS's TO OUTPUT
    out.write("####\nRMS summary\n####\n")
    distrmsinp = avg_list(dist_rms_inp)
    out.write("RMS dist inp: %7.5f +- %7.5f\n"%(distrmsinp[0],distrmsinp[1]))
    distrmsref = avg_list(dist_rms_ref)
    out.write("RMS dist ref: %7.5f +- %7.5f\n"%(distrmsref[0],distrmsref[1]))
    dihermsinp = avg_list(dihe_rms_inp)
    out.write("RMS dihe inp: %7.5f +- %7.5f\n"%(dihermsinp[0],dihermsinp[1]))
    dihermsref = avg_list(dihe_rms_ref)
    out.write("RMS dihe ref: %7.5f +- %7.5f\n"%(dihermsref[0],dihermsref[1]))
  if builddress:
    # DRESS PATH
    dresspath = dressdbpath
    # CYCLE PROJECTS
    cdih = {}
    noe = {}
    reso = {}
    for project in projects[:cutoff]:
      name = os.path.basename(project)
      print name
      namepath = os.path.join(dresspath,name)
      # SEE IF DIR EXISTS ALREADY
      if not os.path.exists(namepath):
        os.mkdir(namepath)
      # COPY REFINED ENSEMBLE
      refensin = os.path.join(project,'refined_input/ensemble_refined.pdb')
      refensou = os.path.join(namepath,'%s_refined.pdb'%name)
      if not os.path.exists(refensou):
        yas_xplor2pdb(nmvconf["YASARA_RUN"],refensin,refensou)
      # COPY ORIGINAL ENSEMBLE
      pdbensin = os.path.join(project,'analyzed_input/ensemble_analyzed.pdb')
      pdbensou = os.path.join(namepath,'%s_original.pdb'%name)
      if not os.path.exists(pdbensou):
        yas_xplor2pdb(nmvconf["YASARA_RUN"],pdbensin,pdbensou)
      # COPY PROCHECK FILES
      proin  = os.path.join(project,'analyzed_input/procheck.tgz')
      proout = os.path.join(namepath,'%s_original_procheck.tgz'%name)
      if not os.path.exists(proout):
        shutil.copy(proin,proout)
      proin  = os.path.join(project,'refined_input/procheck.tgz')
      proout = os.path.join(namepath,'%s_refined_procheck.tgz'%name)
      if not os.path.exists(proout):
        shutil.copy(proin,proout)
      # COPY WHATCHECK FILES
      whcin  = os.path.join(project,'analyzed_input/whatcheck.tgz')
      whcout = os.path.join(namepath,'%s_original_whatcheck.tgz'%name)
      if not os.path.exists(whcout):
        shutil.copy(whcin,whcout)
      whcin  = os.path.join(project,'refined_input/whatcheck.tgz')
      whcout = os.path.join(namepath,'%s_refined_whatcheck.tgz'%name)
      if not os.path.exists(whcout):
        shutil.copy(whcin,whcout)
      # TAR AND COPY THE RESTRAINTS
      dist_in = os.path.join(project,'data/restraints/noe_clean.tbl')
      dihe_in = os.path.join(project,'data/restraints/dihedral_clean.tbl')
      hbon_in = os.path.join(project,'data/restraints/hbonds_clean.tbl')
      tfile = os.path.join(namepath,'%s_restraints.tgz'%name)
      if not os.path.exists(tfile):
        tf = tarfile.open(tfile,"w:gz")
        for el in [dist_in,dihe_in,hbon_in]:
          if os.path.exists(el):
            tf.add(el,os.path.join('restraints',os.path.basename(el)))
        tf.close()
      # TAR AND COPY THE RESTRAINT ANALYSES
      analpath = os.path.join(analysispath,'rcheck')
      tfile = os.path.join(namepath,'%s_refined_violanalysis.tgz'%name)
      if not os.path.exists(tfile):
        tf = tarfile.open(tfile,"w:gz")
        el = os.path.join(analpath,'%s_viol_refined.dat'%name)
        tf.add(el,os.path.join('violationanalysis','%s_viol_refined.dat'%name))
        list = glob.glob(os.path.join(project,'refined_input/refined_*.pdb'))
        for el in list:
          tf.add(el,os.path.join('violationanalysis',os.path.basename(el)))
        tf.close()
      # TAR AND COPY THE RESTRAINT ANALYSES
      analpath = os.path.join(analysispath,'rcheck')
      tfile = os.path.join(namepath,'%s_original_violanalysis.tgz'%name)
      if not os.path.exists(tfile):
        tf = tarfile.open(tfile,"w:gz")
        el = os.path.join(analpath,'%s_viol_analyzed.dat'%name)
        tf.add(el,os.path.join('violationanalysis','%s_viol_original.dat'%name))
        list = glob.glob(os.path.join(project,'analyzed_input/analyzed_*.pdb'))
        for el in list:
          tf.add(el,os.path.join('violationanalysis',os.path.basename(el)))
        tf.close()
  if violcheck and plotqua:
    # WRITE FINAL DB
    print len(dbdict["ID"])
    print dbdict.keys()
    for key in dbdict.keys():
      print len(dbdict[key]), key, dbdict[key]
    print dbpath
    db = data_base(dbpath,fieldlist=dbdict.keys())
    for i in range(len(dbdict["ID"])):
      values = []
      for key in dbdict.keys():
        values.append(dbdict[key][i])
      db.addvaluelist(values)
    db.save()
    print db.valuesforkey("ID")
  if setproperties:
    # INITIALIZE PDBFINDER2
    pdbfinder2 = pdb_finder(nmvconf["PDBFINDER2"],"r",0,error)
    pdbfinder2.buildindex()
    # CYCLE THE PROJECTS
    years,sizes = {},{}
    for project in projects:
      pdb = os.path.basename(project)
      pdbfinder2.read(pdb)
      year = int(pdbfinder2.fieldvalue(' Date')[0:4])
      years[year]=years.get(year,0)+1
      nres = int(pdbfinder2.fieldvalue('T-Nres-Prot'))
      sizes[nres]=sizes.get(nres,0)+1
    steps = []
    stepsize = 0.5
    for i in range(6/stepsize):
      steps.append(i*stepsize)
    for resval in steps:
      xrays = {}
      for key in ['pack','rota','rama','bb']:
        xrays[key]=[]
      for key in pdbfinder2.resolution.keys():
        res = pdbfinder2.resolution[key]
        nres = pdbfinder2.amacs[key]
        if res <= resval+stepsize/2 and res > resval-stepsize/2 and nres < 370 and nres > 20:
          pdbfinder2.read(key)
          # PACKING
          pck = pdbfinder2.fieldvalue('  Packing 2')
          # ROTAMER
          rot = pdbfinder2.fieldvalue('  Chi-1/chi-2')
          # RAMA
          ram = pdbfinder2.fieldvalue('  Phi/psi')
          # BB
          bb = pdbfinder2.fieldvalue('  Backbone')
          if pck and ram and rot and bb:
            pckval = float(pck.split('|')[1])*6.0-3
            xrays['pack']=xrays.get('pack',[])+[pckval]
            rotval = float(rot.split('|')[1])*8.0-4
            xrays['rota']=xrays.get('rota',[])+[rotval]
            ramval = float(ram.split('|')[1])*8.0-4
            xrays['rama']=xrays.get('rama',[])+[ramval]
            bbval = float(bb.split('|')[1])
            xrays['bb']=xrays.get('bb',[])+[bbval]
      # CYCLE THE YEARS
      yk = years.keys()
      yk.sort()
      # CYCLE THE SIZE
      sk = sizes.keys()
      sk.sort()
      # CYCLE THE X-RAY STRUCTURES
      print "###########################"
      print "from %.2f to %.2f"%(resval-stepsize/2,resval+stepsize/2)
      print len(xrays['pack'])
      print 'pack ',avg_list(xrays['pack'])
      print 'rama ',avg_list(xrays['rama'])
      print 'rota ',avg_list(xrays['rota'])
      print 'bb   ',avg_list(xrays['bb'])
  if rperres:
    outputfile1 = os.path.join(analysispath,'restraintsperresidue_all.dat')
    outputfile2 = os.path.join(analysispath,'restraintsperresidue_sec.dat')
    alllist,seclist=[],[]
    # READ THE PDBFINDER
    pdbfinder = pdb_finder(nmvconf["PDBFINDER2"],'r',1,error)
    pdbfinder.buildindex()
    print '%i structures have been indexed.'%len(pdbfinder.recordpos.keys())
    # CYCLE THE PROJECTS
    modelcount = 0
    for projectpath in projects[:cutoff]:
      set = 'analyzed'
      list = glob.glob(os.path.join(projectpath,"%s_input/%s_*.pdb"%(set,set)))
      modelcount+= len(list)
      projectname = os.path.basename(projectpath)
      nmvconf["Q_PROJECT"] = '/home/snabuurs/projects/watref/'
      # SET UP QUEEN
      print "Setting up QUEEN for %s"%projectname
      queen = qn_setup(nmvconf,projectname,myid,numproc)
      xplr  = qn_setupxplor(nmvconf,projectname)
      # READ THE TEMPLATE
      pdb = pdb_file.Structure(xplr.template)
      for chain in pdb.peptide_chains:
        residues = len(chain)
        print "%i residues."%residues
      # GET RESIDUES IN SEC STRUCT
      pdbfinder.read(projectname)
      count = 0
      dssp = pdbfinder.fieldvalue(" DSSP")
      for el in dssp:
        if len(dssp)!=residues:
          error('oeps')
        if el!='C':
          count+=1
      secstr = count
      print "%i residues in secondary structure."%secstr
      # READ RESTRAINTS
      for el in ['noe']:
        rfile = nmv_adjust(queen.table,'%s_clean'%el)
        if os.path.exists(rfile):
          type = 'DIST'
          if el=='dihedral': type='DIHE'
          r = restraint_file(rfile,'r',type=type)
          r.read()
          restraints = len(r.restraintlist)
          print "%i restraints."%restraints
      score1 = int(round(float(restraints)/residues))
      score2 = int(round(float(restraints)/secstr))
      print "## %4i %4i %s "%(score1,score2,projectname)
      alllist.append(score1)
      seclist.append(score2)
    # BIN THE LISTS
    all, sec = {},{}
    minval = min(alllist+seclist)
    maxval = max(alllist+seclist)
    print minval,maxval
    for i in range(minval-1,maxval+2):
      all[i]=0
      sec[i]=0
    for el in alllist: all[el]=all.get(el,0)+1
    for el in seclist: sec[el]=sec.get(el,0)+1
    xmgr = graceplot(outputfile1,'bar','w')
    xmgr.writeheader()
    for key in all.keys(): xmgr.write([key,all[key]])
    xmgr.close()
    xmgr = graceplot(outputfile2,'bar','w')
    xmgr.writeheader()
    for key in sec.keys(): xmgr.write([key,sec[key]])
    print avg_list(alllist)
    print avg_list(seclist)
    xmgr.close()
    print "%i models in DRESS"%modelcount


#  ======================================================================
#   S U B S C R I P T  49:  T E S T   B E T T E R    N O E S
#  ======================================================================
#
def nmv_testbetter(project,dataset,pdbfile,precision=None,nres=None):
  nmvconf["Q_PROJECT"] = '/home/snabuurs/projects/better/'
  # SETUP QUEEN AND XPLOR
  queen = qn_setup(nmvconf,project,myid,numproc)
  xplr  = qn_setupxplor(nmvconf,project)
  # GET PDBFILE BASE NAME
  pdbb = os.path.basename(pdbfile).split('.')[0]
  # ADJUST THE RESTRAINT FILE TO THE PROVIDED PDB FILE
  dataset = qn_readdatafile(nmv_adjust(queen.dataset,dataset))[0]
  intbl = nmv_adjust(queen.table,dataset["FILE"])
  # OPEN PLOT FILES
  xmgrbb = graceplot(os.path.join(queen.outputpath,'bb.dat'),'xy','w')
  xmgrbb.xlab = "Number of residues adjusted"
  xmgrbb.ylab = "Pairwise BB RMSD"
  xmgrhv = graceplot(os.path.join(queen.outputpath,'hv.dat'),'xy','w')
  xmgrhv.xlab = "Number of residues adjusted"
  xmgrhv.ylab = "Pairwise Heavy Atom RMSD"
  for nres in [659,10,25,50,100,200,400]:
    # SET PRECISION LEVEL
    if precision and not nres:
      base = "a_%s_%s_%s"%(dataset["FILE"],pdbb,precision)
    elif precision and nres:
      base = "a_%s_%s_%s_%s"%(dataset["FILE"],pdbb,precision,nres)
    else:
      base = "a_%s_%s"%(dataset["FILE"],pdbb)
    outtbl = nmv_adjust(queen.table,base)
    # IF NO LIMIT IS SET, WE DO'M ALL
    if not nres:
      # ADJUST RESTRAINT FILE
      rfile_adjust(intbl,outtbl,pdbfile,precision=precision)
    # ADJUST SET, SET REMAINDER TO FIXED BOUND
    # THIS PREVENTS MIXING OF TWO DIFFERENT DATASETS
    else:
      # READ THE TABLE
      ri = restraint_file(intbl,'r')
      ri.read()
      ri.close()
      # ADJUST nres RESTRAINTS
      pdb = pdb_file.Structure(pdbfile)
      adjusted = r_adjust(ri.restraintlist[:nres],pdb,precision=precision)
      # FIX THE OTHER RESTRAINTS WITH A LOWER OF 0.0 AND AN UPPER OF 6.0 ANGSTROM
      fixed = r_set(ri.restraintlist[nres:],0.0,6.0)
      # WRITE OUTPUT TABLE
      r = restraint_file(outtbl,'w')
      r.comment("%i adjusted restraints according to %s."%(nres,pdbfile))
      r.mwrite(adjusted)
      r.comment("Fixed restraints.")
      r.mwrite(fixed)
      r.close()
    # READ THE ADJUSED TABLE
    r = restraint_file(outtbl,'r')
    r.read()
    rlist = r.restraintlist
    # CREATE MTF FILE
    print "Creating MTF file for CNS."
    mtf = "%s.mtf"%xplr.psf[:-3]
    if os.path.exists(mtf): os.remove(mtf)
    cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
    # CALCULATE STRUCTURES
    nstruct = 20
    print "Calculating %i structures."%nstruct
    pdbbase = os.path.join(queen.pdb,base)
    cns_calcstructure(pdbbase,
                      xplr.template,
                      mtf,
                      rlist,
                      naccepted=nstruct)
    # SUPER IMPOSE STRUCTURES ONTO REFERENCE STRUCTURES
    pdblist = glob.glob("%s*.pdb"%pdbbase)
    print "Superimposing %i structures."%len(pdblist)
    # FIT REFERENCE
    prft_fitref(pdbfile,pdblist,selection='heavy')
    print "Calculating pairwise RMSD values."
    # CALCULATE PAIRWISE RMSD
    rmsds = prft_rmsd([pdbfile]+pdblist,selection='heavy')
    print "Heavy atom RMSD: %05.2f"%rmsds[0]
    xmgrhv.write([nres,rmsds[0]])
    rmsds = prft_rmsd([pdbfile]+pdblist,selection='bb')
    print "BB atom RMSD:    %05.2f"%rmsds[0]
    xmgrbb.write([nres,rmsds[0]])


#  ======================================================================
#   S U B S C R I P T  50: A N A L Y Z E   N R   R E S T R A I N T S
#  ======================================================================
#
# !!!! UNDER CONSTRUCTION !!!!!
def nmv_ananrrestraints(path):
  dataset = 'noe'
  # OUTPUTPATH
  outpath = os.path.join(path,'analysis')
  xmgr = graceplot(os.path.join(outpath,'distribution2.dat'),'xy','w')
  # READ THE DIRECTORY
  dirlist = glob.glob(os.path.join(path,'1*'))
  skiplist = ['1fry','1h7d','1h7j']
  dirlist = [el for el in dirlist if os.path.basename(el) not in skiplist]
  print len(dirlist)
  dirlist = dirlist
  id = 1
  plotlist = []
  plotkeys = []
  # HANDLE THE DIRS
  for dir in dirlist:
    project = os.path.basename(dir)
    print project
    # SET QUEEN
    queen = qn_setup(nmvconf,project,myid,numproc)
    # READ INFO FROM SETINFO
    setfile = os.path.join(queen.outputpath,'setinfo_%s.dat'%dataset)
    content = open(setfile,'r').readlines()
    setdict = {}
    for line in content[7:]:
      setdict[line[32:-1]]=float(line.split()[0])
    # READ RESTRAINTS IN DATASET
    datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
    rcount = 0
    rdict = {}
    for filedict in datasets:
      if filedict["NAME"] not in plotkeys: plotkeys.append(filedict["NAME"])
      table = nmv_adjust(queen.table,filedict["FILE"])
      r = restraint_file(table,'r',type=filedict["TYPE"])
      r.read()
      rdict[filedict["NAME"]]=r.restraintlist
      rcount += len(r.restraintlist)
    rdict["SUM"]=float(rcount)
    # CHECK NON-REDUNDANT RESTRAINTS
    nrcount = 0
    nrdict = {}
    for filedict in datasets:
      table = os.path.join(queen.outputpath,'nr_%s.tbl'%(filedict["FILE"]))
      r = restraint_file(table,'r',type=filedict["TYPE"])
      r.read()
      nrdict[filedict["NAME"]]=r.restraintlist
      nrcount += len(r.restraintlist)
    nrdict["SUM"]=float(nrcount)
    plotlist.append([rdict,setdict])
    for filedict in datasets:
      key = filedict["NAME"]
      print "%5.2f\t%5.2f\t%5.2f\t%s"%(len(rdict[key])/float(rcount)*100,len(nrdict[key])/float(nrcount)*100,setdict[key],key)
    id+=1
  # COMBINE AND WRITE OUTPUT
  count = 0
  nsets = len(plotlist[0])
  xmgr.add2header("@g0 type Chart")
  xmgr.add2header("@g0 stacked true")
  xmgr.add2header("@with g0")
  xmgr.add2header("@    world ymax 110")
  xmgr.add2header("@    world xmin -1")
  xmgr.add2header("@    xaxis  ticklabel type spec")
  xmgr.add2header("@    xaxis  tick type spec")
  xmgr.add2header("@    xaxis  tick spec %i"%(len(dirlist)*(nsets+1)))
  tickcount = 0
  for dir in dirlist:
    xmgr.add2header("@    xaxis ticklabel %i, \"%s\""%(tickcount,
                                                       os.path.basename(dir).upper()))
    for i in range(nsets+1):
      xmgr.add2header("@    xaxis  tick major %i, %i"%(tickcount,tickcount+1))
      tickcount += 1
  scount = 0
  for key in plotkeys:
    print key
    xmgr.add2header("@target G0.S%i"%scount)
    xmgr.add2header("@type bar")
    xmgr.add2header("@G0.S%i line type 0"%scount)
    scount+=1
    count = 0
    for i in range(len(dirlist)):
      for j in range(nsets):
        dict = plotlist[i][j]
        if dict.get(key):
          if j==1 and nsets==3:
            print i,j
            xmgr.write([count, len(dict[key])/plotlist[i][0]["SUM"]*100, dirlist[i]])
          elif j==0:
            xmgr.write([count, len(dict[key])/dict["SUM"]*100, dirlist[i]])
          else:
            xmgr.write([count, dict[key], dirlist[i]])
        else:
          xmgr.write([count, 0.0, dirlist[i]])
        count += 1
      xmgr.write([count, 0.0, 0.0])
      count += 1
    xmgr.newset()


#  ======================================================================
#   S U B S C R I P T  51: C O M P A R E   X R A Y   W I T H   N M R
#  ======================================================================
#
# THIS SCRIPT WILL ANALYZE AND COMPARE PDB FILES DETERMINED BOTH BY XRAY
# AND NMR
# !!!! UNDER CONSTRUCTION !!!!!
def nmv_anaxrayandnmr():
  nmvconf["Q_PROJECT"] = '/data/db_queen'
  # STRUCTURES WITH KNOWN PROBLEMS
  xskiplist = ['2lzh']
  nskiplist = []
  # SET THE DATASET
  dataset = 'noe'
  # DO THE WORK
  projectpath = '/projects/xraynmr/'
  pdblist = os.path.join(projectpath,'pdb.list')
  # RETRIEVE STRUCTURES THAT ARE WORTH ANALYZING
  if not os.path.exists(pdblist):
    # USE PDBFINDER2 TO GET STRUCTURES WITH IDENTICAL SEQUENCE,
    # SAME NUMBER OF HETGROUPS AND THE EXPERIMENTAL RESTRAINTS
    # AVAILABLE FOR THE NMR MODEL
    nmrdict,hetdict,xdict = {},{},{}
    pdbfinder = pdb_finder(nmvconf["PDBFINDER2"],"r",0,error)
    pdbfinder.buildindex()
    pdbfinder.read()
    count = 1
    # GET PAIRS
    while not pdbfinder.eof:
      hetdict[pdbfinder.id]=pdbfinder.fieldvalue("HET-Groups")
      method = pdbfinder.fieldvalue("Exp-Method")
      if method=="NMR" and pdbfinder.id.lower() not in nskiplist:
        if len(pdbfinder.chain)==1:
          nmrdict[pdbfinder.id]=pdbfinder.sequence
          print "%5i %4s\r"%(count,pdbfinder.id),
          sys.stdout.flush()
          count +=1
      elif method=="X" and pdbfinder.id.lower() not in xskiplist:
        if len(pdbfinder.chain)==1:
          xdict[pdbfinder.id]=pdbfinder.sequence
      pdbfinder.read()
    print
    count = 0
    # CHECK FOR NO HETGROUPS
    pairs = {}
    for nmr in nmrdict.keys():
      print "Checking %s..."%nmr
      for xray in xdict.keys():
        if hetdict[nmr]==hetdict[xray]==None:
          if nmrdict[nmr][0].find(xdict[xray][0])!=-1 or \
             xdict[xray][0].find(nmrdict[nmr][0])!=-1:
            pairs[nmr]=pairs.get(nmr,[])+[xray]
            print "%5i %4s %4s\r"%(count,nmr,xray),
            count += 1
    print
    file = open(pdblist,'w')
    for nmr in pairs:
      if pdb_hasrestraints(nmr,nmvconf["FTPPDB"]):
        file.write("%s = "%nmr.lower())
        for xray in pairs[nmr]:
          file.write("%s "%xray.lower())
        file.write("\n")
    file.close()
  # PARSE PDB SELECTION AND PROCEED
  else:
    # READ THE PDBLIST FILE
    pdbpairs = {}
    content = open(pdblist,'r').readlines()
    for line in content:
      line = line.split()
      pdbpairs[line[0]]=line[2:]
    # BUILD DIRECTORY TREES
    for nmr in pdbpairs:
      nmrpath = os.path.join(projectpath,nmr)
      pdbpath = os.path.join(nmrpath,'pdb')
      if not os.path.exists(nmrpath):
        # MAKE DIRECTORY
        os.mkdir(nmrpath)
        os.mkdir(pdbpath)
        # COPY NMR PDB FILE
        inpdb = nmv_adjust(nmvconf["PDB"],nmr)
        outpdb = os.path.join(pdbpath,"nmr_%s.pdb"%nmr)
        yas_cleanpdb(nmvconf["YASARA_RUN"],inpdb,outpdb)
        # COPY XRAY PDB FILES
        for xry in pdbpairs[nmr]:
          if xry not in xskiplist:
            inpdb = nmv_adjust(nmvconf["PDB"],xry)
            outpdb = os.path.join(pdbpath,"xry_%s.pdb"%xry)
            yas_cleanpdb(nmvconf["YASARA_RUN"],inpdb,outpdb)
##        # SUPERIMPOSE STRUCTURES
##        for xry in pdbpairs[nmr]:
##          refpdb = os.path.join(pdbpath,"xry_%s.pdb"%xry)
##          mobpdb = os.path.join(pdbpath,"nmr_%s.pdb"%nmr)
##          scene = os.path.join(pdbpath,"%s_vs_%s.sce"%(nmr,xry))
##          if not os.path.exists(scene):
##            rmsds = yas_superimpose(nmvconf["YASARA_RUN"],refpdb,
##                                    mobpdb,flipflag=1,savescene=scene)
##            avg = "%04.1f"%avg_list(rmsds)[0]
##            avg = avg.replace('.','-')
##            outfile = os.path.join(pdbpath,"%s_vs_%s_%s.rmsd"%(nmr,xry,avg))
##            file = open(outfile,'w')
##            for rmsd in rmsds:
##              file.write("%7.3f\n"%rmsd)
##            file.close()
      # CHECK IF QUEEN ANALYSIS EXISTS
      qpath = os.path.join(nmvconf["Q_PROJECT"],nmr)
      if os.path.exists(qpath) and nmr not in ['1gb1']:
        print qpath
##        print qpath
##        # SETUP QUEEN AND XPLOR
##        queen = qn_setup(nmvconf,nmr)
##        xplr = qn_setupxplor(nmvconf,nmr)
##        # READ THE UNIQUE INFORMATION FILE
##        inffile = os.path.join(queen.outputpath,"Iuni_%s.dat"%dataset)
##        if not os.path.exists(inffile):
##          qn_infuni(queen,xplr,dataset)
##        Iuni = qn_readinffile(inffile)
##        # READ DATAFILE
##        datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
##        # READ DATASETS
##        data = qn_readdatasets(queen,datasets)
##        # SPLIT NMR PDB FILE
##        inpdb = os.path.join(pdbpath,"nmr_%s.pdb"%nmr)
##        if len(glob.glob(os.path.join(pdbpath,'xplor_%s*.pdb'%nmr)))==0:
##          yas_splitpdb2xplor(nmvconf["YASARA_RUN"],inpdb,
##                             pdbpath,'xplor_%s'%nmr)
##        # CHECK VIOLATIONS IN THE NMR MODELS
##        models = glob.glob(os.path.join(pdbpath,'xplor_%s*.pdb'%nmr))
##        psf = os.path.join(pdbpath,'xplor_%s.psf'%nmr)
##        xplor_pdb2psf(models[0],psf,xplorflag=1)
##        viol_nmr,rviol_nmr=xplor_violations(models,psf,data["data"])
##        # CORRELATE VIOLATIONS WITH UNIQUE INFORMATION
##        xmgr = graceplot(os.path.join(nmrpath,"Iuni_vs_viol_%s.dat"%nmr),'xydy','w')
##        xmgr.xlab = "Unique information (bits/atom\S2\N)"
##        xmgr.ylab = "Average violations over %i models"%(len(models))
##        xmgr.writeheader()
##        for el in data["data"]:
##          key = str(el)
##          viol = avg_list(rviol_nmr[key])
##          xmgr.write([Iuni[key][0],viol[0],viol[1],key])
##        xmgr.close()
##        # CLEAN UP MODELS
##        dsc_remove(psf)
##        # PRINT VIOLATIONS
##        keys = viol_nmr["DIST"].keys()
##        keys.sort()
##        for key in keys:
##          print key,float(viol_nmr["DIST"][key])/len(models)
##        # CHECK VIOLATIONS IN THE XRAY MODELS
##        print pdbpairs[nmr]
##        for xry in pdbpairs[nmr]:
##          print xry
##          inpdb = os.path.join(pdbpath,"xry_%s.pdb"%xry)
##          # CONVERT XRAY FILE TO XPLOR FORMAT
##          outpdb = os.path.join(pdbpath,'xplor_%s.pdb'%xry)
##          yas_pdb2xplor(nmvconf["YASARA_RUN"],inpdb,outpdb)
##          # SYNCHRONIZE CHAIN NAMES
##          # CRITICAL FOR VIOLATION ANALYSES...
##          tmppdb = dsc_tmpfilename(outpdb)
##          pdb_syncchainnames(nmvconf["YASARA_RUN"],
##                             outpdb,
##                             tmppdb,
##                             models[0],
##                             xplorflag=1)
##          shutil.copy(tmppdb,outpdb)
##          # CREATE PSF FILE FOR XRAY FILE
##          psf = os.path.join(pdbpath,'xplor_%s.psf'%xry)
##          xplor_pdb2psf(outpdb,psf,xplorflag=1)
####          # SUPERIMPOSE ON NMR
####          suppdb = "%s.sup"%outpdb[:-4]
####          yas_superimpose(nmvconf["YASARA_RUN"],
####                          models[0],
####                          outpdb,
####                          outpdb=suppdb,
####                          xplorflag=1,
####                          flipflag=0)
##          print outpdb
##          # ANALYZE VIOLATIONS
##          viol_xry,rviol_xry=xplor_violations(outpdb,psf,data["data"])
##          # CORRELATE VIOLATIONS WITH UNIQUE INFORMATION
##          xmgr = graceplot(os.path.join(nmrpath,"Iuni_vs_viol_%s.dat"%xry),'xydy','w')
##          xmgr.xlab = "Unique information (bits/atom\S2\N)"
##          xmgr.ylab = "Average violations over xray model %s"%(xry)
##          xmgr.writeheader()
##          for el in data["data"]:
##            key = str(el)
##            viol = avg_list(rviol_xry[key])
##            xmgr.write([Iuni[key][0],viol[0],viol[1],key])
##          xmgr.close()
##          # CLEAN UP PSF
##          dsc_remove(psf)
##        #dsc_remove(models)


#  ======================================================================
#   S U B S C R I P T  52: C O R R E L A T E   U N I Q U E   I N F O
#  ======================================================================
#
# !!!! UNDER CONSTRUCTION !!!!
def nmv_correlateiuni(projectname,dataset):
  # SETUP QUEEN AND XPLOR
  queen = qn_setup(nmvconf,projectname,myid,numproc)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # READ RESTRAINTS
  data = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  restraintlist=[]
  for filedict in data:
    table = nmv_adjust(queen.table,filedict["FILE"])
    r = restraint_file(table,'r',type=filedict["TYPE"])
    r.read()
    restraintlist += r.restraintlist
  # READ UNIQUE INFORMATION
  iunifile = os.path.join(queen.outputpath,'Iuni_%s.dat'%dataset)
  if not os.path.exists(iunifile):
    qn_infuni(queen,xplr,dataset)
  comments = ['#','@','&']
  content = open(iunifile,'r').readlines()
  infdict = {}
  for line in content:
    if len(line)>0 and line[0] not in comments:
      # PARSE RESRAINT AND INFORMATION
      line = line.split()
      rstring = line[2].strip("\"")
      inf = float(line[1])
      infdict[rstring]=inf
  # READ PDBFILE
  pdb = pdb_file.Structure(xplr.template)
  sumdict = {}
  for chain in pdb.peptide_chains:
    for residue in chain:
      hcount = 0
      for atom in residue:
        if 'H' in atom.name:
          hcount+=1
      n = residue.number
      sumdict[n]=sumdict.get(n,[])
      # CYCLE THE RESTRAINTS
      for re in restraintlist:
        for i in range(2):
          if n in re.data[i]["RESI"]:
            sumdict[n]+=[infdict[str(re)]]
  file = open('test1_%s.dat'%projectname,'w')
  for key in sumdict.keys():
    file.write("%i %e\n"%(key,avg_list(sumdict[key])[0]))
  # CHECK VIOLATIONS
  xray = os.path.join(queen.pdb,'1pgb.pdb')
  viol,rviol = xplor_violations(xray,xplr.psf,restraintlist)
  file = open('test2_%s.dat'%projectname,'w')
  for re in restraintlist:
   file.write("%e %e %s\n"%(rviol[str(re)][0],
                            infdict[str(re)],
                            str(re)))


#  =======================================================================
#   S U B S C R I P T  53: C O U N T  N M R  W I T H   R E S T R A I N T S
#  =======================================================================
#
# THIS SCRIPT WILL MAKE A PLOT OF THE PERCENTAGE OF NMR STRUCTURES
# DEPOSITED IN EACH YEAR WHICH HAS EXPERIMENTAL RES
def nmv_createrestraintdist(outputfile):
  # INDEX PDBFINDER
  pdbfinder2 = pdb_finder(nmvconf["PDBFINDER2"],"r",0,error)
  pdbfinder2.buildindex()
  pdbfinder2.read()
  # CYCLE THE PDBFINDER
  percentages, yearlist, pdblist = {},[], []
  count = 0
  while not pdbfinder2.eof:
    # CHECK IF NMR
    method = pdbfinder2.fieldvalue("Exp-Method")
    if method == 'NMR':
      pdblist.append(pdbfinder2.id)
      # EXTRACT YEAR
      year = int(pdbfinder2.fieldvalue(' Date')[0:4])
      if year not in yearlist: yearlist.append(year)
      # ADD TO DICT
      percentages[year]=percentages.get(year,[])+[string.lower(pdbfinder2.id)]
    pdbfinder2.read()
  # GET LIST OF PDBS WITH RESTRAINTS
  hasrestraints = pdb_hasrestraints(pdblist,nmvconf["FTPPDB"])
  # WRITE OUT PERCENTAGES
  xmgr = graceplot(outputfile,'xy','w')
  startyear = min(yearlist)
  endyear = max(yearlist)
  sum = 0
  for year in range(startyear,endyear+1):
    sum += len(yearlist)
    if percentages.has_key(year):
      yearlist = percentages[year]
      list = [el for el in yearlist if el in hasrestraints]
      perc = (len(list)/float(len(yearlist)))*100
      xmgr.write([year,perc])
    else:
      xmgr.write([year,0.0])
    print year, len(yearlist), len([el for el in yearlist if el in hasrestraints])
  print sum
  xmgr.close()


#  =======================================================================
#   S U B S C R I P T  55: C O N S T R U C T   R M S D   S U R F A C E
#  =======================================================================
#
def nmv_constructrmsdsurface(projectpath,
                             dataset,
                             outputfile,
                             nstruct=25,
                             wifdump='/tmp/wifsurf.dump'):
  # VARIABLES
  # SURFACE
  sigma     = 0.075
  varc      = 2*(sigma**2)
  varcutoff = 5
  xstep     = varc
  # PLOT
  xrange    = [0.5,3.5]
  yrange    = [3.0,6.0]
  #yrange    = [0.0,2.0]
  # ERROR ALLOWED ON RG
  rgerror   = 0.25
  # TEST FRACTION
  tfrac     = 0.10
  # MAXIMUM RMSD
  maxrmsd   = 100
  # BUILD A LIST OF PROJECT DIRECTORIES
  dirlist = glob.glob(os.path.join(projectpath,'*'))
  # CYCLE DIRLIST AND BUILD PROJECTLIST
  skiplist,projectlist = [],[]
  projectpdb,projectpdbs = {},{}
  for dir in dirlist:
    project = os.path.basename(dir)
    # CONTINUE IF NOT IN SKIPLIST
    if project not in skiplist:
      pdbpath = os.path.join(projectpath,"%s/pdb"%project)
      # LIST OF PDBFILES FOR THE PROJECT
      pdblist = glob.glob(os.path.join(pdbpath,"%s_cns_w_*.pdb"%(project)))
      # INCLUDE ONLY IF ALL STRUCTURES ARE PRESENT
      if len(pdblist)==nstruct:
        projectlist.append(project)
        # THE ENSEMBLE
        projectpdb[project]=os.path.join(pdbpath,"%s_ensemble.pdb"%(project))
        # ALL SEPARATE MEMBERS
        projectpdbs[project]=pdblist
  # READ WIFDUMP IF EXISTS ELSE REBUILD IT
  match = 0
  if os.path.exists(wifdump):
    print "Reading WHAT IF dump file."
    dump = open(wifdump,'r')
    shape = cPickle.load(dump)
    rmsd = cPickle.load(dump)
    dump.close()
    # CHECK IF WE STILL MATCH
    shapes = shape.keys()
    inboth = [el for el in projectlist if el in shapes]
    if len(inboth)==len(projectlist):
      match = 1
      print "Dump file still in sync."
    else:
      print "Dump file out of sync, rebuilding..."
  # IF THE DUMP DOESN'T EXISTS OR DOESN'T MATCH
  # THE CURRENT PROJECTLIST WE NEED TO REBUILD IT
  if not match:
    # CALCULATE SHAPE FACTOR
    shape, rmsd = {}, {}
    log = os.path.join(nmvconf["TMP"],'wiflog.dat')
    # CYCLE THE PROJECTS
    for project in projectlist:
      script = wif_script(nmvconf["GWHATIF_RUN"])
      pdb = projectpdb[project]
      script.write("GETMOL %s"%pdb)
      script.write("%s"%project)
      script.write("1000")
      for i in range(nstruct):
        script.write("DOLOG %s.%i\n"%(log,i+1))
        script.write("%cigar")
        script.write("m%i 0"%(i+1))
        script.write("NOLOG")
      script.write("FULLSTOP Y")
      script.submit()
      shapelist = []
      # PARSE OUTPUT FILE
      for i in range(nstruct):
        content = open("%s.%i"%(log,i+1),'r').readlines()
        # EXTRACT THE SHAPE VALUE
        sval = float(content[-2].split()[-1])
        shapelist.append(sval)
      # AVERAGE OVER THE ENSEMBLE MEMBERS
      shape[project]=avg_list(shapelist)[0]
      # CALCULATE AVERAGE RMSD
      rmsdlist = prft_rmsd(projectpdbs[project],'heavy')
      score = avg_list(rmsdlist)
      # STORE THE RMSD
      rmsd[project]=score[0]
    # PICKLE THE SHAPE AND RMSD DICTIONARIES
    wif = open(wifdump,'w')
    cPickle.dump(shape,wif)
    cPickle.dump(rmsd,wif)
    wif.close()
  # CONSTRUCT DICT WITH RG RATIOS
  rgratio = {}
  rgdump = os.path.join(nmvconf["TMP"],'rg.dump')
  if os.path.exists(rgdump):
    dump = open(rgdump,'r')
    rgratio = cPickle.load(dump)
    dump.close()
  for project in projectlist:
    if not rgratio.has_key(project):
      rgratio[project] = pdb_radiusofgyration(projectpdbs[project],getratio=1)
      dump = open(rgdump,'w')
      cPickle.dump(rgratio,dump)
      dump.close()
  # CLEAN OUT STRUCTURES WHICH WE DO NOT WANT
  rgdel = 0
  for i in range(len(projectlist)-1,-1,-1):
    project = projectlist[i]

    if rgratio[project] > 1+rgerror or rgratio[project] < 1-rgerror or rmsd[project]>maxrmsd:
      del projectlist[i]
      rgdel += 1
  print "Deleted %i structures for poor RG ratio."%rgdel
  # SHUFFLE OR SORT THE LIST
  projectlist.sort()
  shuffle(projectlist)
  # DIVIDE INTO TEST AND WORKING SET
  print len(projectlist)
  cnt = int((1.0-tfrac)*len(projectlist))
  testlist = projectlist[cnt:]
  projectlist = projectlist[:cnt]
  print "Found %i projects for surface."%(len(projectlist)+len(testlist))
  print "Using %i projects to build surface."%(len(projectlist))
  print "Using %i projects for validation."%(len(testlist))
  # CHECK IF QUEEN PROJECT EXISTS
  setinfo = {}
  for project in projectlist+testlist:
    setdict = {}
    # SETUP QUEEN AND XPLOR
    queen = qn_setup(nmvconf,project,myid,numproc)
    xplor = qn_setupxplor(nmvconf,project)
    # READ SETINFO FILE
    setfile  = os.path.join(queen.outputpath,'setinfo_%s.dat'%dataset)
    if not os.path.exists(setfile):
      print projectlist.index(project)
      print "Calculating setinfo for %s"%project
      qn_setinformation(queen,xplor,'all')
    content = open(setfile,'r').readlines()
    # DIFFERENTIATE BETWEEN DIFFERENT VERSIONS OF QUEEN
    if content[0][0]=='#': lines = content[1:4]
    else: lines = content[0:3]
    for line in lines:
      line = line.split()
      setdict[line[0]]=float(line[2])
    # STORE QUEEN INFO FOR EACH PROJECT
    setinfo[project]=setdict
  print "Read QUEEN information values for %i datasets."%(len(setinfo))
  rmsdedump = '/tmp/rmsde.dump'
  if not os.path.exists(rmsdedump):
    rmsde = {}
    # CALCULATE AND GENERATE RMSDE VALUES
    for project in projectlist+testlist:
      # SETUP QUEEN AND XPLOR
      queen = qn_setup(nmvconf,project,myid,numproc)
      xplr = qn_setupxplor(nmvconf,project)
      # READ RESTRAINTS
      data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
      restraints = data["data"]+data["bckg"]
      rmsdeval = queen.rmsde(xplr,restraints)
      rmsde[project]=rmsdeval
      print project,rmsdeval
      dump = open(rmsdedump,'w')
      cPickle.dump(rmsde,dump)
      dump.close()
  else:
    dump = open(rmsdedump,'r')
    rmsde = cPickle.load(dump)
    dump.close()
  # DELETE PROJECT FOR WHICH NO QUEEN INFO IS PRESENT
  projectlist = [el for el in projectlist if el in setinfo.keys()]
  testlist = [el for el in testlist if el in setinfo.keys()]
  print "Continueing with %i sets."%(len(projectlist)+len(testlist))
  print "Using %i projects to build surface."%(len(projectlist))
  print "Using %i projects for validation."%(len(testlist))
##  # NORMALIZE RMSD FOR RMSD100
##  nresdump = '/tmp/nres.dump'
##  normrmsd = {}
##  normH = {}
##  if not os.path.exists(nresdump):
##    nresd = {}
##    for project in projectlist+testlist:
##      pdb = projectpdbs[project][0]
##      pdbf = pdb_file.Structure(pdb)
##      nres = 0.0
##      for chain in pdbf.peptide_chains:
##        nres += len(chain)
##      nresd[project]=nres
##    dump = open(nresdump,'w')
##    cPickle.dump(nresd,dump)
##    dump.close()
##  else:
##    dump = open(nresdump,'r')
##    nresd = cPickle.load(dump)
##    dump.close()
##  for project in projectlist+testlist:
##    normrmsd[project]=rmsd[project]/(1+math.log(math.sqrt(nresd[project]/100.0)))
##    #normH[project]=setinfo[project]['Hstructure|R']/(1+math.log(math.sqrt(nresd[project]/100.0)))
##    normH[project]=setinfo[project]['Hstructure|R']/(2.2*pow(nresd[project],0.38))
##    #normH[project]=(setinfo[project]['Hstructure|0']-setinfo[project]['Hstructure|R'])/setinfo[project]['Hstructure|0']
  # BUILD THE PLOT FILE
  print "Generating output file."
  xmgr = graceplot(outputfile,'xy','w')
  xmgr.ylab = "RMSD"
  xmgr.xlab = "H\sstructure|R\N"
  xmgr.writeheader()
  # WRITE ALL DATA POINTS
  # x = shape
  # y = H
  # z = RMSD
  values,valdict = [],{}
  # ONLY THE PROJECTLIST NOW
  for project in projectlist:
    plotlist = [shape[project],setinfo[project]['Hstructure|R'],rmsd[project]]
    #plotlist = [shape[project],rmsde[project]/1000,rmsd[project]]
    xmgr.write(plotlist)
    # STORE ALL VALUES IN A LIST
    values.append(plotlist)
    # AND IN A DICTIONARY
    valdict[project]=plotlist
  xmgr.close()
  # CHECK DOUBLES
  flist,dcount = [],0
  for key1 in valdict.keys():
    for key2 in valdict.keys():
      if key1!=key2 and valdict[key1][:2]==valdict[key2][:2] and [key2,key1] not in flist:
        dcount += 1
        flist.append([key1,key2])
  print "Found %i double entries in working set!"%dcount
  # CONSTRUCT THE SURFACE FILE
  # THE STEPSIZE
  ystep = xstep
  # CONSTRUCT THE AXIS LISTS
  xlist = []
  for i in range(int(xrange[0]/xstep),int(xrange[1]/xstep+1)): xlist.append(i*xstep)
  ylist = []
  for i in range(int(yrange[0]/ystep),int(yrange[1]/ystep+1)): ylist.append(i*ystep)
  # BUILD THE ACTUAL SURFACE
  xydict = avg_surface(xlist,ylist,values,c=varc,cutoff=varcutoff)
  # WRITE SURFACE FILE FOR YASARA
  surffile = outputfile+'.surf'
  out = open(surffile,'w')
  for x in xlist:
    for y in ylist:
      out.write("%10.5f "%xydict[x][y])
    out.write("\n")
  out.close()
  # WRITE SURFACE FILE FOR XFARBE
  farbfile = outputfile+'.farb'
  symbfile = outputfile+'.sym'
  out = open(farbfile,'w')
  out.write("%i %i\n"%(len(ylist),len(xlist)))
  sout = open(symbfile,'w')
  sout.write('\n\n')
  for x in xlist:
    for y in ylist:
      out.write("%10.5f "%xydict[x][y])
      sout.write("1 0.1 6 %10.5f %10.5f\n"%(x,y))
    out.write("\n")
  out.write("%3.1f %3.1f\n"%(yrange[0],yrange[1]))
  out.write("%3.1f %3.1f\n"%(xrange[0],xrange[1]))
  out.close()
  sout.close()
  # CHECK THE RANGES
  rangecount = 0
  dlist = []
  for value in values:
    if value[0] > max(xlist) or value[0] < min(xlist) or \
       value[1] > max(ylist) or value[1] < min(ylist):
      rangecount += 1
      dlist.append(values.index(value))
  warning("%i datapoint(s) out of range"%rangecount)
  dlist.sort()
  dlist.reverse()
  for el in dlist:
    del values[el]
  print "%i elements removed from values."%len(dlist)
  # BUILD THE DATAFILE AND RMSDFILE
  datafile = outputfile+'.data'
  rmsdfile = outputfile+'.rmsd'
  # STORE ALL DATA IN DICTIONARY
  datadict = {}
  # CYCLE ALL DATAPOINTS
  for value in values:
    # ROUND DATAPOINTS OF TO AXIS MEMBERS
    dat = []
    for el in value[:2]:
      dat += [round(el/xstep)*xstep]
      # SANITY CHECK
      d = round(el/xstep)*xstep
      if d not in xlist and d not in ylist:
        warning("Corrected datapoint of axes!")
    datadict[dat[0]] = datadict.get(dat[0],{})
    if not datadict[dat[0]].has_key(dat[1]):
      datadict[dat[0]][dat[1]] = []
    datadict[dat[0]][dat[1]].append(value[2])
  # FIND THE MAXIMUM VALUE LEFT
  # FOR SCALE CORRECTION IN YASARA...
  maxdat = 0.0
  for x in xlist:
    for y in ylist:
      if datadict.has_key(x):
        if datadict[x].has_key(y) and xydict[x][y]!=0.0:
          maxdat = max(avg_list(datadict[x][y])[0],maxdat)
  # STORE OUTPUT IN FILES
  rmsdsum,rmsdcount,incount,outcount = 0,0,0,0
  data = open(datafile,'w')
  rmsdf = open(rmsdfile,'w')
  # LIST OF DEVIATIONS
  devlist = []
  for x in xlist:
    for y in ylist:
      if datadict.has_key(x):
        if datadict[x].has_key(y):
          # AVERAGE OVER DOUBLE ENTRIES
          avg = avg_list(datadict[x][y])[0]
          # ONLY POINTS INCLUDED IN THE SURFACE (value !=0.0)
          # ARE INCLUDED IN THE RMSD CALCULATION
          if xydict[x][y]!=0.0:
            data.write("%10.5f "%avg)
            rmsdf.write("%10.5f "%(avg-xydict[x][y]))
            # STORE DEVIATION FROM SURFACE
            devlist.append(avg-xydict[x][y])
            # CALCULATE RMSD
            for el in datadict[x][y]:
              rmsdsum += (el-xydict[x][y])**2
              rmsdcount += 1
            # NUMBER OF DATAPOINTS IN SURFACE
            incount += len(datadict[x][y])
          else:
            # NUMBER OF DATAPOINTS OUTSIDE SURFACE
            outcount += len(datadict[x][y])
        else:
          data.write("%10.5f "%(0.0))
          rmsdf.write("%10.5f "%(0.0))
      else:
        # THE FINAL POINT ON THE AXIS HAS THE CALIBRATION POINT
        # FOR YASARA
        if x==max(xlist) and y==max(ylist):
          data.write("%10.f "%(maxdat))
          rmsdf.write("%10.f "%(maxdat))
        # NORMAL POINT
        else:
          data.write("%10.f "%(0.0))
          rmsdf.write("%10.f "%(0.0))
    data.write("\n")
    rmsdf.write("\n")
  data.close()
  rmsdf.close()
  # THE NUMBER OF EXCLUDED PONTS
  print "%i of %i datapoint(s) excluded in the surface"%(outcount,len(projectlist))
  # ARE ALL POINTS ACCOUNTED FOR?
  if (outcount+rmsdcount+rangecount)!=len(projectlist):
    dif = abs(len(projectlist)-(outcount+rmsdcount+rangecount))
    warning("There seem to be %i points missing from the working set"%dif)
  else:
    print "All datapoint in working set accounted for!"
  # CALCULATE RMSD
  rmsdval = math.sqrt((1.0/rmsdcount)*rmsdsum)
  print "\n### WORKING SET ###"
  print "%i datapoints"%incount
  print "RMSD of surface : %5.2f Angstrom"%rmsdval
  print "Maximum dev.    : %5.2f A"%max(devlist)
  print "Minimum dev.    : %5.2f A"%min(devlist)
  avg = avg_list(devlist)
  print "Average dev.    : %5.2f A (+- %5.3f)\n"%(avg[0],avg[1])
  # CALCULATE RMSD FOR TEST SET
  # STORE TESTVALUES
  tvalues = []
  for project in testlist:
    tvalues.append([shape[project],setinfo[project]['Hstructure|R'],rmsd[project]])
    #tvalues.append([shape[project],rmsde[project]/1000,rmsd[project]])
  # STORE TEST DATA IN DATADICT
  tdatadict = {}
  for value in tvalues:
    dat = []
    for el in value[:2]:
      dat += [round(el/xstep)*xstep]
    tdatadict[dat[0]] = tdatadict.get(dat[0],{})
    if not tdatadict[dat[0]].has_key(dat[1]):
      tdatadict[dat[0]][dat[1]] = []
    tdatadict[dat[0]][dat[1]].append(value[2])
  # CHECK THE RANGES
  rangecount = 0
  dlist = []
  for value in tvalues:
    if value[0] > max(xlist) or value[0] < min(xlist) or \
       value[1] > max(ylist) or value[1] < min(ylist):
      rangecount += 1
      dlist.append(tvalues.index(value))
  warning("%i datapoint(s) out of range"%rangecount)
  dlist.sort()
  dlist.reverse()
  for el in dlist:
    del tvalues[el]
  print "%i elements removed from values."%len(dlist)
  # CALCULATE RMSD
  rmsdsum,rmsdcount,incount,outcount = 0,0,0,0
  tdevlist = []
  #print "%3s %3s %4s %4s %3s"%('x','y','pred','true','dev')
  pred,true=[],[]
  for x in xlist:
    for y in ylist:
      if tdatadict.has_key(x):
        if tdatadict[x].has_key(y):
          avg = avg_list(tdatadict[x][y])[0]
          if xydict[x][y]!=0.0:
            tdevlist.append(avg-xydict[x][y])
            # PRINT TO SCREEN
            #print "%3.1f %3.1f %4.1f %4.1f %4.1f"%(x,y,
            #                                       xydict[x][y],
            #                                       avg,
            #                                       avg-xydict[x][y]),
            #if abs(avg-xydict[x][y]) > 1.0: print "*"
            #else: print
            for el in tdatadict[x][y]:
              rmsdsum += (el-xydict[x][y])**2
              rmsdcount += 1
              pred.append(el)
              true.append(xydict[x][y])
            incount += len(tdatadict[x][y])
          else:
            outcount += len(tdatadict[x][y])
  rmsdval = math.sqrt((1.0/rmsdcount)*rmsdsum)
  # THE NUMBER OF EXCLUDED PONTS
  print "%i of %i datapoint(s) excluded in the surface"%(outcount,len(testlist))
  # ARE ALL POINTS ACCOUNTED FOR?
  if (outcount+rmsdcount+rangecount)!=len(testlist):
    dif = abs(len(testlist)-(outcount+rmsdcount+rangecount))
    warning("There seem to be %i points missing from the test set"%dif)
  else:
    print "All datapoint in test set accounted for!"
  print "\n## TEST SET ##"
  print "%i datapoints"%incount
  print "RMSD of surface : %5.2f Angstrom"%rmsdval
  print "Maximum dev.    : %5.2f A"%max(tdevlist)
  print "Minimum dev.    : %5.2f A"%min(tdevlist)
  avg = avg_list(tdevlist)
  print "Average dev.    : %5.2f A (+- %5.3f)\n"%(avg[0],avg[1])
  print "\nCorrelation PRED-TRUE : %5.2f"%list_cc(pred,true)
  print "Chi-2 PRED-TRUE       : %5.2f"%(math.sqrt(list_chi2(pred,true)/len(pred)))
  log = open('cc.txt','w')
  for i in range(len(pred)):
    log.write("%5.2f %5.2f\n"%(pred[i],true[i]))
  # FIRE OFF YASARA
  ysr = ysr_macro(nmvconf["YASARA_RUN"])
  ysr.write("Showtab %s"%surffile)
  ysr.write("Showtab %s"%datafile)
  ysr.write("Showtab %s"%rmsdfile)
  ysr.submit()


#  =======================================================================
#   S U B S C R I P T   5 6 :   A N A L Y Z E   H   S T R U C T U R E
#  =======================================================================
#
def nmv_analyzeHstructure(projectname='3gb1',dataset='noe',
                          adjustdata=True,reference='/pdb/pdb1pgb.ent'):
  if projectname in ['3gb1']:
    dipoflag = 1
  dipoflag = 0
  # OVERWRITE Q_PROJECT
  nmvconf["Q_PROJECT"]='/storage/projects/datavsqual'
  # SOME PARAMETERS
  subsets     = [100.,95.,90.,85.,80.,75.,70.,65.,60.]
  nsets       = 5
  nstructures = 20
  precision   = 0.5
  # SETUP QUEEN
  queen = qn_setup(nmvconf,projectname,myid,numproc)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # SET FILENAME BASE
  if adjustdata:
    fnbase = '%s_%03.2f'%(dataset,precision)
    intbl = os.path.join(queen.outputpath,"%s_%03.2f.tbl"%(dataset,precision))
  else:
    fnbase = '%s'%(dataset)
    intbl = nmv_adjust(queen.table,dataset)
  # READ DIPOLAR COUPLINGS
  if dipoflag:
    rdctbl = nmv_adjust(queen.table,'dipo_bicelle_hn')
    rdc = restraint_file(rdctbl,'r',type='DIPO',Daxi=-9.7,Drho=-2.23)
    rdc.read()
  # READ RESTRAINTS
  r = restraint_file(intbl,'r')
  r.read()
  completelist = copy.copy(r.restraintlist)
  # IMPORT RESTRAINTS
  unc_ini = queen.uncertainty(xplr,[])
  unc_all = queen.uncertainty(xplr,r.restraintlist)
  inf_all = unc_ini-unc_all
  # READ SETS WITH CERTAIN LEVELS OF INFORMATION
  sets = []
  for subset in subsets:
    print "Subset %3i of %3i."%(subsets.index(subset)+1,len(subsets))
    for i in range(nsets):
      print "Set    %3i of %3i."%(i+1,nsets)
      pdbbase = "cv_%s_%05.1f_%i"%(fnbase,subset,i+1)
      # READ RESTRAINTS
      print "Reading restraints."
      intbl = nmv_adjust(queen.table,"%s_%05.1f_%i"%(fnbase,subset,i+1))
      r = restraint_file(intbl,'r')
      r.read()
      # CHECK IF WE HAVE ANY STRUCTURES
      pdblist = glob.glob(os.path.join(queen.pdb,"%s*"%pdbbase))
      if len(pdblist)<nstructures:
        print "Calculating structures."
        # CREATE MTF
        mtf = os.path.join(queen.pdb,'%s.mtf'%projectname)
        if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
        if len(r.restraintlist)<10:
          print "Alert: probably unable to partition!"
        cnsbase = os.path.join(queen.pdb,pdbbase)
        resultfile = "%s__trial.results"%cnsbase
        print resultfile
        # CALCULATE THE STRUCTURES
        if not os.path.exists(resultfile):
          cns_calcstructurecv(cnsbase,
                              xplr.template,
                              mtf,
                              r.restraintlist,
                              naccepted=nstructures)
      # LIST CALCULATED STRUCTURES
      pdblist = glob.glob(os.path.join(queen.pdb,"%s*.pdb"%pdbbase))
      # BUILD LIST OF CV RESTRAINTS
      cvlist = [el for el in completelist if el not in r.restraintlist]
      print 'Sanitycheck: %4i + %4i = %4i'%(len(cvlist),len(r.restraintlist),
                                            len(completelist))
      # VALIDATE THE CV RMSRESTRAINTS
      if len(cvlist) > 0:
        viol, rviol = xplor_violations(pdblist,xplr.psf,cvlist)
        rmslist = []
        for j in range(len(pdblist)):
          rms = 0.0
          for el in cvlist:
            rms += rviol[str(el)][j]**2
          rms = math.sqrt(rms/(len(cvlist)))
          rmslist.append(rms)
        rms = avg_list(rmslist)
      else:
        rms = [0.,0.]
      print 'RMS: %6.4f'%rms[0]
      # CALCULATE UNCERTAINTY
      unc = queen.uncertainty(xplr,r.restraintlist)
      inf = unc_ini-unc
      score = (inf/inf_all)*100
      # STORE DICTIONARY WITH INFO
      set = {}
      set['info']   = score
      set['data']   = r.restraintlist
      set['runid']  = i+1
      set['target'] = subset
      set['rms']    = rms
      sets.append(set)
##  # CONVERT MTF TO PSF FILE
##  mtf = "%s.mtf"%xplr.psf[:-4]
##  if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
##  # CALCULATE THE STRUCTURES
##  for set in sets:
##    print "Calculating %i structures with %6.2f %% of information."%(nstruct,set['info'])
##    restraintlist = set['data']
##    if len(restraintlist)<10:
##      print "Alert: probably unable to partition!"
##    pdbbase = os.path.join(queen.pdb,"%s_%06.2f_%i"%(dataset,set['target'],set['runid']))
##    resultfile = "%s__trial.results"%pdbbase
##    print resultfile
##    if not os.path.exists(resultfile):
##      cns_calcstructurecv(pdbbase,
##                          xplr.template,
##                          mtf,
##                          restraintlist,
##                          naccepted=nstruct)
  # OUTPUTFILE: H VERSUS CV-RMS-NOE
  outputfile = os.path.join(queen.outputpath,'H-vs-CVrms_%s.dat'%(fnbase))
  xmgr = graceplot(outputfile,'xydy','w')
  xmgr.xlab = "Information content (%)"
  xmgr.ylab = "Cross-validated RMS of NOE (A)"
  xmgr.writeheader()
  for set in sets:
    pdbbase = os.path.join(queen.pdb,"cv_%s_%05.1f_%i"%(fnbase,set['target'],set['runid']))
    resultfile = "%s__trial.results"%pdbbase
    print "Processing set with %6.2f %% of information."%set['info']
    rmsdlist = []
    for i in range(1,nstructures+1):
      content = open("%s_a_%i.pdb"%(pdbbase,i),'r').readlines()
      cvrmsd = float(content[60].split()[2])
      rmsdlist.append(cvrmsd)
    avg = avg_list(rmsdlist)
    set['avg'] = avg[0]
    set['sd']  = avg[1]
    xmgr.write([set['info'],avg[0],avg[1]])
  xmgr.type = 'xydxdy'
  xmgr.newset()
  for subset in subsets:
    xlist,ylist=[],[]
    for set in sets:
      if subset==set['target']:
        xlist.append(set['info'])
        ylist.append(set['avg'])
    xavg = avg_list(xlist)
    yavg = avg_list(ylist)
    xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
  xmgr.close()
  # OUTPUTFILE: H VERSUS CV-RMS-NOE2
  outputfile = os.path.join(queen.outputpath,'H-vs-CVrms2_%s.dat'%(fnbase))
  xmgr = graceplot(outputfile,'xydy','w')
  xmgr.xlab = "Information content (%)"
  xmgr.ylab = "Cross-validated RMS of NOE (A)"
  xmgr.writeheader()
  for set in sets:
    xmgr.write([set['info'],set['rms'][0],set['rms'][1]])
  xmgr.type = 'xydxdy'
  xmgr.newset()
  for subset in subsets:
    xlist,ylist=[],[]
    for set in sets:
      if subset==set['target']:
        xlist.append(set['info'])
        ylist.append(set['rms'][0])
    xavg = avg_list(xlist)
    yavg = avg_list(ylist)
    xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
  xmgr.close()
  # OUTPUTFILE: Nrestraints VERSUS CV-RMS-NOE
  outputfile = os.path.join(queen.outputpath,'Nrestraints-vs-CVrms_%s.dat'%(fnbase))
  xmgr = graceplot(outputfile,'xydy','w')
  xmgr.xlab = "Number of restraints"
  xmgr.ylab = "Cross-validated RMS of NOE (A)"
  xmgr.writeheader()
  for set in sets:
    pdbbase = os.path.join(queen.pdb,"cv_%s_%05.1f_%i"%(fnbase,set['target'],set['runid']))
    resultfile = "%s__trial.results"%pdbbase
    print "Processing set with %6.2f %% of information."%set['info']
    xmgr.write([len(set['data']),set['avg'],set['sd']])
  xmgr.type = 'xydxdy'
  xmgr.newset()
  for subset in subsets:
    xlist,ylist=[],[]
    for set in sets:
      if subset==set['target']:
        xlist.append(len(set['data']))
        ylist.append(set['avg'])
    xavg = avg_list(xlist)
    yavg = avg_list(ylist)
    xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
  xmgr.close()
  # OUTPUTFILE: Nrestraints VERSUS CV-RMS-NOE2
  outputfile = os.path.join(queen.outputpath,'Nrestraints-vs-CVrms2_%s.dat'%(fnbase))
  xmgr = graceplot(outputfile,'xydy','w')
  xmgr.xlab = "Number of restraints"
  xmgr.ylab = "Cross-validated RMS of NOE (A)"
  xmgr.writeheader()
  for set in sets:
    print "Processing set with %6.2f %% of information."%set['info']
    xmgr.write([len(set['data']),set['rms'][0],set['rms'][1]])
  xmgr.type = 'xydxdy'
  xmgr.newset()
  for subset in subsets:
    xlist,ylist=[],[]
    for set in sets:
      if subset==set['target']:
        xlist.append(len(set['data']))
        ylist.append(set['rms'][0])
    xavg = avg_list(xlist)
    yavg = avg_list(ylist)
    xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
  xmgr.close()
  if dipoflag:
    # OUTPUTFILE: H VERSUS RDC-Rfactor
    outputfile = os.path.join(queen.outputpath,'H-vs-R_%s.dat'%(fnbase))
    xmgr = graceplot(outputfile,'xydy','w')
    xmgr.xlab = "Information content (%)"
    xmgr.ylab = "RDC R-factor (%)"
    xmgr.writeheader()
    for set in sets:
      pdbbase = os.path.join(queen.pdb,"cv_%s_%05.1f_%i"%(fnbase,set['target'],set['runid']))
      print "Processing set with %6.2f %% of information."%set['info']
      rlist = []
      for i in range(1,nstructures+1):
        pdbfile = "%s_a_%i.pdb"%(pdbbase,i)
        r = xplor_qfactor(pdbfile,xplr.psf,rdc.restraintlist)
        rlist.append(r)
      avg = avg_list(rlist)
      set['ravg'] = avg[0]
      set['rsd']  = avg[1]
      xmgr.write([set['info'],avg[0],avg[1]])
    xmgr.type = 'xydxdy'
    xmgr.newset()
    for subset in subsets:
      xlist,ylist=[],[]
      for set in sets:
        if subset==set['target']:
          xlist.append(set['info'])
          ylist.append(set['ravg'])
      xavg = avg_list(xlist)
      yavg = avg_list(ylist)
      xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
    xmgr.close()
    # OUTPUTFILE: Nrestraints VERSUS RDC-Rfactor
    outputfile = os.path.join(queen.outputpath,'Nrestraints-vs-R_%s.dat'%(fnbase))
    xmgr = graceplot(outputfile,'xydy','w')
    xmgr.xlab = "Number of restraints"
    xmgr.ylab = "RDC R-factor (A)"
    xmgr.writeheader()
    for set in sets:
      print "Processing set with %6.2f %% of information."%set['info']
      xmgr.write([len(set['data']),set['ravg'],set['rsd']])
    xmgr.type = 'xydxdy'
    xmgr.newset()
    for subset in subsets:
      xlist,ylist=[],[]
      for set in sets:
        if subset==set['target']:
          xlist.append(len(set['data']))
          ylist.append(set['ravg'])
      xavg = avg_list(xlist)
      yavg = avg_list(ylist)
      xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
    xmgr.close()
  # OUTPUTFILE: H VERSUS RMSD
  outputfile = os.path.join(queen.outputpath,'H-vs-RMSD_%s.dat'%(fnbase))
  xmgr = graceplot(outputfile,'xydy','w')
  xmgr.xlab = "Information content (%)"
  xmgr.ylab = "RMSD of ensemble (A)"
  xmgr.writeheader()
  for set in sets:
    pdbbase = os.path.join(queen.pdb,"cv_%s_%05.1f_%i"%(fnbase,set['target'],set['runid']))
    print "Processing set with %6.2f %% of information."%set['info']
    pdblist = glob.glob("%s*.pdb"%pdbbase)
    print "Superimposing %i structures"%len(pdblist)
    rmsdlist = prft_rmsd(pdblist,selection='all')
    set['rmsd']=rmsdlist
    avg = avg_list(rmsdlist)
    xmgr.write([set['info'],avg[0],avg[1]])
  xmgr.type = 'xydxdy'
  xmgr.newset()
  for subset in subsets:
    xlist,ylist=[],[]
    for set in sets:
      if subset==set['target']:
        xlist.append(set['info'])
        ylist.append(avg_list(set['rmsd'])[0])
    xavg = avg_list(xlist)
    yavg = avg_list(ylist)
    xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
  xmgr.close()
  # OUTPUTFILE: Nrestraints VERSUS RMSD
  outputfile = os.path.join(queen.outputpath,'Nrestraints-vs-RMSD_%s.dat'%(fnbase))
  xmgr = graceplot(outputfile,'xydy','w')
  xmgr.xlab = "Number of restraints"
  xmgr.ylab = "RMSD of ensemble (A)"
  xmgr.writeheader()
  for set in sets:
    pdbbase = os.path.join(queen.pdb,"cv_%s_%05.1f_%i"%(fnbase,set['target'],set['runid']))
    print "Processing set with %6.2f %% of information."%set['info']
    avg = avg_list(set['rmsd'])
    xmgr.write([len(set['data']),avg[0],avg[1]])
  xmgr.type = 'xydxdy'
  xmgr.newset()
  for subset in subsets:
    xlist,ylist=[],[]
    for set in sets:
      if subset==set['target']:
        xlist.append(len(set['data']))
        ylist.append(avg_list(set['rmsd'])[0])
    xavg = avg_list(xlist)
    yavg = avg_list(ylist)
    xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
  xmgr.close()
##  # OUTPUTFILE: Nrestraints VERSUS RMSD
##  outputfile = os.path.join(queen.outputpath,'Nrestraints-vs-Unc_%s.dat'%(dataset))
##  xmgr = graceplot(outputfile,'xydy','w')
##  xmgr.xlab = "Number of restraints"
##  xmgr.ylab = "RMSD of ensemble (A)"
##  xmgr.writeheader()
##  for set in sets:
##    pdbbase = os.path.join(queen.pdb,"cv_%s_%05.1f_%i"%(fnbase,set['target'],set['runid']))
##    print "Processing set with %6.2f %% of information."%set['info']
##    avg = avg_list(set['rmsd'])
##    xmgr.write([len(set['data']),avg[0],avg[1]])
##  xmgr.type = 'xydxdy'
##  xmgr.newset()
##  for subset in subsets:
##    xlist,ylist=[],[]
##    for set in sets:
##      if subset==set['target']:
##        xlist.append(len(set['data']))
##        ylist.append(avg_list(set['rmsd'])[0])
##    xavg = avg_list(xlist)
##    yavg = avg_list(ylist)
##    xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
##  xmgr.close()


#  =======================================================================
#   S U B S C R I P T   5 7 :   B U I L D   D R E S S
#  =======================================================================
#

def nmv_builddress(inpath,outpath):
  # LIMIT TO NUMBER OF STRUCTURES
  cutoff = 1
  # DB PARAMETERS
  dbdict = {}
  dbpath = os.path.join(outpath,'dress.db')
  # SUMMARY
  sum_checks,sum_data = {},{}
  sumpath = os.path.join(outpath,'dress.sum')
  # ANALYSIS PATH
  analysispath = os.path.join(inpath,'analysis')
  if not os.path.exists(analysispath):
    os.mkdir(analysispath)
  # BUILD LIST OF PROJECTS
  allprojects = glob.glob(os.path.join(inpath,'*'))
  skiplist = ['analysis']
  # BUILD A CLEAN LIST OF PROJECTS
  projects = []
  for project in allprojects:
    name = os.path.basename(project)
    if name not in skiplist:
      projects.append(project)
      # ADD TO DB
      dbdict["ID"]=dbdict.get("ID",[])+[name]
  # SET THE LIMIT
  dbdict["ID"]=dbdict["ID"][:cutoff]
  print "Building DRESS database with %i structures."%len(dbdict["ID"])
  print "Analyzing validation output."
  # STORE QUALITY SCORES
  ######################
  for projectpath in projects[:cutoff]:
    projectname = os.path.basename(projectpath)
    print "Parsing %s.\r"%projectname,
    sys.stdout.flush()
    for run in ['analyzed','refined']:
      summary = os.path.join(projectpath,"%s/summary_%s.txt"%(run,run))
      # READ THE FILE
      inp = open(summary,'r').readlines()
      readflag = 0
      for line in inp:
        line = line[:-1]
        # ONLY READ THE QUALITY SCORES HERE
        if not readflag:
          if line.find("PROCHECK")>-1: readflag=1
        else:
          # SKIP COMMENTS AND NON-INFORMATIVE LINES
          if line.find(':')>-1 and line[0]!='#' and len(line.split(':')[1])>1:
            line = line.split(':')
            # FILL QUALITY DICT
            score = float(line[1].split('+-')[0])
            sd = float(line[1].split('+-')[1])
            name = line[0].strip()
            # ADD TO DB
            dbval = "%7.2f +/- %7.2f"%(score,sd)
            if run == 'analyzed': dbkey = "INP-%s"%name
            elif run == 'refined': dbkey = "REF-%s"%name
            dbdict[dbkey]=dbdict.get(dbkey,[])+[dbval]
            # ADD TO SUMMARY DICTIONARY
            sum_checks[dbkey]=sum_checks.get(dbkey,[])+[score]
  print "Done.        "
  print "Analyzing restraint violations."
  # ANALYZE RESTRAINT VIOLATIONS
  ##############################
  rdistcutoff = [0.1,0.3,0.5]
  rdihecutoff = [1.0,3.0,5.0]
  # PATH FOR FILE STORAGE
  rcheckpath = os.path.join(analysispath,'rcheck')
  if not os.path.exists(rcheckpath):
    os.mkdir(rcheckpath)
  # CREATE DICTIONARIES FOR STORAGE
  numviol = {'analyzed':{},
             'refined':{}}
  # VIOLATIONS DICTONARY
  maxviol = 10
  for i in range(1,(maxviol*10)+1):
    numviol['analyzed'][float(i)/10]=0
    numviol['refined'][float(i)/10]=0
  numlist = numviol['analyzed'].keys()
  numlist.sort()
  # CYCLE THE PROJECTS
  for projectpath in projects[:cutoff]:
    projectname = os.path.basename(projectpath)
    print "Parsing %s.\r"%projectname,
    sys.stdout.flush()
    # SET QUEENPATH
    nmvconf["Q_PROJECT"] = inpath
    queen = qn_setup(nmvconf,projectname,myid,numproc)
    xplr  = qn_setupxplor(nmvconf,projectname)
    # FOR CHRIS HIS 'CLEAN' VERSIONS
    xplr.psf = os.path.join(projectpath,"data/sequence/protein_clean.psf")
    # READ RESTRAINTS
    rlist = []
    for el in ['noe','hbonds','dihedral']:
      rfile = nmv_adjust(queen.table,'%s_clean'%el)
      if os.path.exists(rfile):
        type = 'DIST'
        if el=='dihedral': type='DIHE'
        r = restraint_file(rfile,'r',type=type)
        r.read()
        rlist+=r.restraintlist
    # DO THE ANALYSIS
    for run in ['analyzed','refined']:
      conscount = 0
      # BUILD LIST OF PDB FILES
      list = glob.glob(os.path.join(projectpath,"%s/%s_*.pdb"%(run,run)))
      # STORE THE NUMBER OF STRUCTURES
      nstr = len(list)
      if run=='analyzed':
        dbdict['nstructures']=dbdict.get('nstructures',[])+[str(nstr)]
      nstr = float(nstr)
      if run == 'analyzed': dbkey = "INP"
      elif run == 'refined': dbkey = "REF"
      # CONSTRUCT HEADER FOR RESTRAINT ANALYSIS FILE
      topval = len(list)
      topstr, i = '', 1
      while i <= topval:
        if (i+1)%10==0 or i==1:
          if i!=1: topstr+="%i"%(i+1)
          else: topstr+="1"
          i+=len("%i"%(i+1))-1
        elif i%5==0 and i%10!=0: topstr+="."
        elif i==topval:
          val = "%i"%topval
          topstr+=val[-1]
        else: topstr+=" "
        i+=1
      # DO THE RESTRAINT ANALYSIS
      outputfile = os.path.join(rcheckpath,'%s_viol_%s.dat'%(projectname,
                                                             run))
      # CHECK VIOLATIONS
      dumpfile = os.path.join(rcheckpath,'%s_viol_%s.dump'%(projectname,
                                                            run))
      if os.path.exists(dumpfile):
        dump = open(dumpfile,'r')
        viol = cPickle.load(dump)
        rviol = cPickle.load(dump)
        dump.close()
      else:
        viol,rviol=xplor_violations(list,xplr.psf,rlist)
        dump = open(dumpfile,'w')
        cPickle.dump(viol,dump)
        cPickle.dump(rviol,dump)
        dump.close()
      file = open(outputfile,'w')
      file.write('Ensemble\n')
      file.write('========\n')
      file.write('%i structures in ensemble.\n'%len(list))
      file.write('Index number below refer to the numbers used in\n')
      file.write('the following violation analyses.\n\n')
      file.write('index\tfilename\n')
      sortedlist = []
      for i in range(1,len(list)+1):
        filename = os.path.join(projectpath,"%s/%s_%i.pdb"%(run,run,i))
        file.write("%i\t%s\n"%(i,os.path.basename(filename)))
        sortedlist.append(filename)
      list = sortedlist
      file.write('\n')
      # SORT OUT VIOLATIONS
      for type in ['DIST','DIHE']:
        # SORT OUT THE RESTRAINT OF THE CURRENT TYPE
        typelist = [el for el in rlist if el.type==type]
        # DISTANCE VIOLATIONS
        if type == "DIST":
          if len(typelist)>0:
            # violations bigger than 0.5
            dbdict["%s-0.5"%dbkey]=dbdict.get("%s-0.5"%dbkey,[]) + \
                                    [str(viol[type][">=0.5"]/nstr)]
            sum_data["%s-dist-0.5"%dbkey]=sum_data.get("%s-dist-0.5"%dbkey,[]) + \
                                           [viol[type][">=0.5"]/nstr]
            # violations bigger than 0.3
            sum = viol[type][">=0.5"]/nstr + viol[type]["< 0.5"]/nstr + \
                  viol[type]["< 0.4"]/nstr
            dbdict["%s-0.3"%dbkey]=dbdict.get("%s-0.3"%dbkey,[])+[str(sum)]
            sum_data["%s-dist-0.3"%dbkey]=sum_data.get("%s-dist-0.3"%dbkey,[]) + \
                                           [sum]
            # CALCULATE RMS
            rms = 0
            for el in typelist:
              for vi in rviol[str(el)]:
                rms += vi**2
            rms = math.sqrt(rms/(len(typelist)*nstr))
            # ADD TO DB
            dbdict["%s-distrms"%dbkey]=dbdict.get("%s-distrms"%dbkey,[])+[str(rms)]
            # SUMDICT
            sum_data["%s-distrms"%dbkey]=sum_data.get("%s-distrms"%dbkey,[])+[rms]
          else:
            dbdict["%s-0.5"%dbkey]=dbdict.get("%s-0.5"%dbkey,[])+['']
            dbdict["%s-0.3"%dbkey]=dbdict.get("%s-0.3"%dbkey,[])+['']
            dbdict["%s-distrms"%dbkey]=dbdict.get("%s-distrms"%dbkey,[])+['']
        if type == "DIHE":
          if len(typelist)>0:
            # violations bigger than 5 degress
            dbdict["%s-5.0"%dbkey]=dbdict.get("%s-5.0"%dbkey,[])+[str(viol[type][">=5.0"]/nstr)]
            sum_data["%s-dihe-5.0"%dbkey]=sum_data.get("%s-dihe-5.0"%dbkey,[]) + \
                                           [viol[type][">=5.0"]/nstr]
            # calculate rms
            rms = 0
            for el in typelist:
              for vi in rviol[str(el)]:
                rms += vi**2
            rms = math.sqrt(rms/(len(typelist)*nstr))
            # ADD TO DB
            dbdict["%s-diherms"%dbkey]=dbdict.get("%s-diherms"%dbkey,[])+[str(rms)]
            # SUMDICT
            sum_data["%s-diherms"%dbkey]=sum_data.get("%s-diherms"%dbkey,[])+[rms]
          else:
            dbdict["%s-5.0"%dbkey]=dbdict.get("%s-5.0"%dbkey,[])+['']
            dbdict["%s-diherms"%dbkey]=dbdict.get("%s-diherms"%dbkey,[])+['']
        # DISTANCE RESTRAINTS
        if type=='DIST' and len(typelist)>0:
          rcutoff = rdistcutoff
          file.write('Distance restraints\n')
          file.write('===================\n')
          file.write('_ = violation > %.1f A.\n~ = violation > %.1f A.\n'%(rcutoff[0],
                                                                           rcutoff[1]))
          file.write('* = violation > %.1f A.\n'%rcutoff[2])
          file.write('Vmax = maximum violation in A.\n\n')
          file.write('%s  Vmax restraint\n'%topstr)
        # DIHEDRAL ANGLE RESTRAINTS
        if type=='DIHE' and len(typelist)>0:
          rcutoff = rdihecutoff
          file.write('Dihedral angle restraints\n')
          file.write('=========================\n')
          file.write('_ = violation > %.1f degress.\n~ = violation > %.1f degrees.\n'%(rcutoff[0],rcutoff[1]))
          file.write('* = violation > %.1f degrees.\n'%rcutoff[2])
          file.write('Vmax = maximum violation in degrees.\n\n')
          file.write('%s  Vmax restraint\n'%topstr)
        # CYCLE THE RESTRAINT LIST
        for r in typelist:
          stri = ''
          # CYCLE THE VIOLATIONS
          for elem in rviol[str(r)]:
            # BUILD SUMMARY STRING
            if elem >= rcutoff[2]: stri+='*'
            elif elem >= rcutoff[1]: stri+='~'
            elif elem >= rcutoff[0]: stri+='_'
            else: stri+='.'
          # WRITE THE OUTPUT TO FILE
          file.write("%s %5.2f %s\n"%(string.ljust(stri,topval),max(rviol[str(r)]),str(r)))
      file.write("\n")
      file.close()
  print "Done.        "
  print "Copying files to DRESS repository."
  # COPY ALL THE FILES TO THE DATABASE DIRECTORY
  for project in projects[:cutoff]:
    name = os.path.basename(project)
    print "Copying files for %s.\r"%name,
    sys.stdout.flush()
    namepath = os.path.join(outpath,name)
    # SEE IF DIR EXISTS ALREADY
    if not os.path.exists(namepath):
      os.mkdir(namepath)
    # COPY REFINED ENSEMBLE
    if not os.path.exists(os.path.join(project,'refined/ensemble_refined.pdb')):
      refensin = os.path.join(project,'refined/refined_1.pdb')
      refensou = os.path.join(namepath,'%s_refined.pdb'%name)
    else:
      refensin = os.path.join(project,'refined/ensemble_refined.pdb')
      refensou = os.path.join(namepath,'%s_refined.pdb'%name)
    if not os.path.exists(refensou):
      yas_xplor2pdb(nmvconf["YASARA_RUN"],refensin,refensou)
    # COPY ORIGINAL ENSEMBLE
    if not os.path.exists(os.path.join(project,'refined/ensemble_refined.pdb')):
      pdbensin = os.path.join(project,'analyzed/analyzed_1.pdb')
      pdbensou = os.path.join(namepath,'%s_original.pdb'%name)
    else:
      pdbensin = os.path.join(project,'analyzed/ensemble_analyzed.pdb')
      pdbensou = os.path.join(namepath,'%s_original.pdb'%name)
    if not os.path.exists(pdbensou):
      yas_xplor2pdb(nmvconf["YASARA_RUN"],pdbensin,pdbensou)
    # COPY PROCHECK FILES
    proin  = os.path.join(project,'analyzed/procheck.tgz')
    proout = os.path.join(namepath,'%s_original_procheck.tgz'%name)
    if not os.path.exists(proout):
      shutil.copy(proin,proout)
    proin  = os.path.join(project,'refined/procheck.tgz')
    proout = os.path.join(namepath,'%s_refined_procheck.tgz'%name)
    if not os.path.exists(proout):
      shutil.copy(proin,proout)
    # COPY WHATCHECK FILES
    whcin  = os.path.join(project,'analyzed/whatcheck.tgz')
    whcout = os.path.join(namepath,'%s_original_whatcheck.tgz'%name)
    if not os.path.exists(whcout):
      shutil.copy(whcin,whcout)
    whcin  = os.path.join(project,'refined/whatcheck.tgz')
    whcout = os.path.join(namepath,'%s_refined_whatcheck.tgz'%name)
    if not os.path.exists(whcout):
      shutil.copy(whcin,whcout)
    # TAR AND COPY THE RESTRAINTS
    dist_in = os.path.join(project,'data/restraints/noe_clean.tbl')
    dihe_in = os.path.join(project,'data/restraints/dihedral_clean.tbl')
    hbon_in = os.path.join(project,'data/restraints/hbonds_clean.tbl')
    tfile = os.path.join(namepath,'%s_restraints.tgz'%name)
    if not os.path.exists(tfile):
      tf = tarfile.open(tfile,"w:gz")
      for el in [dist_in,dihe_in,hbon_in]:
        if os.path.exists(el):
          tf.add(el,os.path.join('restraints',os.path.basename(el)))
      tf.close()
    # TAR AND COPY THE RESTRAINT ANALYSES
    analpath = os.path.join(analysispath,'rcheck')
    tfile = os.path.join(namepath,'%s_refined_violanalysis.tgz'%name)
    if not os.path.exists(tfile):
      tf = tarfile.open(tfile,"w:gz")
      el = os.path.join(analpath,'%s_viol_refined.dat'%name)
      tf.add(el,os.path.join('violationanalysis','%s_viol_refined.dat'%name))
      list = glob.glob(os.path.join(project,'refined/refined_*.pdb'))
      for el in list:
        tf.add(el,os.path.join('violationanalysis',os.path.basename(el)))
      tf.close()
    # TAR AND COPY THE RESTRAINT ANALYSES
    analpath = os.path.join(analysispath,'rcheck')
    tfile = os.path.join(namepath,'%s_original_violanalysis.tgz'%name)
    if not os.path.exists(tfile):
      tf = tarfile.open(tfile,"w:gz")
      el = os.path.join(analpath,'%s_viol_analyzed.dat'%name)
      tf.add(el,os.path.join('violationanalysis','%s_viol_original.dat'%name))
      list = glob.glob(os.path.join(project,'analyzed/analyzed_*.pdb'))
      for el in list:
        tf.add(el,os.path.join('violationanalysis',os.path.basename(el)))
      tf.close()
  print "Done.                         "
  # WRITE THE DRESS DB FILE
  print "Writing DRESS database with %i entries."%len(dbdict["ID"])
  db = data_base(dbpath,fieldlist=dbdict.keys())
  for i in range(len(dbdict["ID"])):
    values = []
    for key in dbdict.keys():
      values.append(dbdict[key][i])
    db.addvaluelist(values)
  db.save()
  # WRITE SUMMARY FILE
  print "Writing DRESS summary file to:"
  print sumpath
  checks = sum_checks.keys()
  checks.sort()
  checks = checks[:(len(checks)/2)]
  file = open(sumpath,'w')
   # WHAT CHECK VALIDATION SUMMARY
  file.write("* WHAT CHECK validation scores *\n")
  file.write("********************************\n\n")
  file.write("%40s    %15s    %15s\n"%('check','input','refined'))
  file.write("%s\n"%(78*'-'))
  # PRINT SUMMARY
  for check in checks:
    if 'bumps' not in check and 'region' not in check:
      check_gen = check[4:]
      inpavg = avg_list(sum_checks["INP-%s"%check_gen])
      refavg = avg_list(sum_checks["REF-%s"%check_gen])
      file.write("%40s   %6.2f +/- %5.2f   %6.2f +/- %5.2f\n"%(check_gen,
                                                               inpavg[0],
                                                               inpavg[1],
                                                               refavg[0],
                                                               refavg[1]))
  file.write("\n")
  # PROCHECK VALIDATION SUMMARY
  file.write("* PROCHECK validation scores *\n")
  file.write("******************************\n\n")
  file.write("%40s    %15s    %15s\n"%('check','input','refined'))
  file.write("%s\n"%(78*'-'))
  # PRINT SUMMARY
  prochecks = []
  for check in checks:
    if 'region' in check: prochecks.append(check)
  prochecks.reverse()
  for check in prochecks:
    check_gen = check[4:]
    inpavg = avg_list(sum_checks["INP-%s"%check_gen])
    refavg = avg_list(sum_checks["REF-%s"%check_gen])
    file.write("%40s   %6.2f +/- %5.2f   %6.2f +/- %5.2f\n"%(check_gen,
                                                             inpavg[0],
                                                             inpavg[1],
                                                             refavg[0],
                                                             refavg[1]))
  file.write("\n")
  # BUMPS SUMMARY
  file.write("* Bumps scores *\n")
  file.write("****************\n\n")
  file.write("%40s    %15s    %15s\n"%('check','input','refined'))
  file.write("%s\n"%(78*'-'))
  # PRINT SUMMARY
  for check in checks:
    if 'bumps' in check:
      check_gen = check[4:]
      inpavg = avg_list(sum_checks["INP-%s"%check_gen])
      refavg = avg_list(sum_checks["REF-%s"%check_gen])
      file.write("%40s   %6.2f +/- %5.2f   %6.2f +/- %5.2f\n"%(check_gen,
                                                               inpavg[0],
                                                               inpavg[1],
                                                               refavg[0],
                                                               refavg[1]))
  file.write("\n")
  # DATA SUMMARY
  file.write("* Data scores *\n")
  file.write("***************\n\n")
  file.write("%40s    %15s    %15s\n"%('check','input','refined'))
  file.write("%s\n"%(78*'-'))
  # PRINT DATA
  checks = sum_data.keys()
  checks.sort()
  checks = checks[:(len(checks)/2)]
  for check in checks:
    check_gen = check[4:]
    inpavg = avg_list(sum_data["INP-%s"%check_gen])
    refavg = avg_list(sum_data["REF-%s"%check_gen])
    file.write("%40s   %6.2f +/- %5.2f   %6.2f +/- %5.2f\n"%(check_gen,
                                                             inpavg[0],
                                                             inpavg[1],
                                                             refavg[0],
                                                             refavg[1]))
  file.close()
  print "Done."


#  =======================================================================
#   S U B S C R I P T   5 8 :   I M P O R T   B M R B   D B
#  =======================================================================
#
def nmv_importdb(dbpath,outpath,max=5000):
  # SET TEMPORARY PATH
  tmppath = dsc_tmpdir(outpath)
  # BUILD LIST OF FILES
  files = glob.glob(os.path.join(dbpath,'*.tgz'))
  files = files[:max]
  print "Found %i entries."%len(files)
  cnt = 0
  # CYCLE THE FILES
  for file in files:
    cnt += 1
    # GET PROJECTNAME
    pname = os.path.splitext(os.path.basename(file))[0]
    print "Processing set %03i of %03i. Setname %s."%(cnt,len(files),pname)
    ppath = os.path.join(outpath,pname)
    # BUILD PROJECT TREE
    if not os.path.exists(ppath):# and os.path.exists(os.path.join(ppath,'data')):
      qn_createproject(nmvconf,pname,outpath)
      # SETUP QUEEN AND XPLOR VARIABLES
      queen = qn_setup(nmvconf,pname,projectpath=outpath)
      xplr  = qn_setupxplor(nmvconf,pname,projectpath=outpath)
      # OPEN TARFILE AND EXTRACT IT
      tf = tarfile.open(file,"r:gz")
      for tarinfo in tf:
        tf.extract(tarinfo,path=tmppath)
      tf.close()
      tmpproj = os.path.join(tmppath,pname)
      # CONVERT THE MTF FILE
      mtf = os.path.join(tmpproj,'%s_cns.mtf'%pname)
      cns_mtf2psf(nmvconf["CNS"],
                  mtf,
                  xplr.psf)
      # OPEN THE DATASET DESCRIPTION FILE
      dataset = nmv_adjust(queen.dataset,'all')
      datasetf = open(dataset,'w')
      # COPY THE FILES AND BUILD DATASET FILE
      for el in ['unambig','dihedrals','hbonds']:
        fname = os.path.join(tmpproj,"%s.tbl"%el)
        if os.path.exists(fname):
          fout = nmv_adjust(queen.table,el)
          if el=='unambig':
            content = open(fname,'r').readlines()
            count = 0
            for line in content:
              if line[:4].upper()=="ASSI" or line[:4].upper()==" ASS" : count += 1
            # READ THE ORIGINAL DATA
            r = restraint_file(fname,'r',"DIST")
            r.read()
            print "Expected: %5i, Read: %5i."%(count,len(r.restraintlist))
            if count!=len(r.restraintlist):
              print "######## WARNING #########"
              x = raw_input()
            r.close()
            # WRITE THE NEW DATA
            rout = restraint_file(fout,'w',"DIST")
            rout.mwrite(r.restraintlist)
            rout.close()
            r.close()
            # DATASET INFO
            datasetf.write("NAME = Distance restraints\n")
            datasetf.write("TYPE = DIST\n")
            datasetf.write("FILE = unambig\n")
            datasetf.write("//\n")
          elif el=='dihedrals':
            content = open(fname,'r').readlines()
            count = 0
            for line in content:
              if line[:4].upper()=="ASSI" or line[:4].upper()==" ASS" : count += 1
            # READ THE ORIGINAL DATA
            r = restraint_file(fname,'r',"DIHE")
            r.read()
            print "Expected: %5i, Read: %5i."%(count,len(r.restraintlist))
            if count!=len(r.restraintlist):
              print "######## WARNING #########"
              x = raw_input()
            r.close()
            # WRITE THE NEW DATA
            rout = restraint_file(fout,'w',"DIHE")
            rout.mwrite(r.restraintlist)
            rout.close()
            r.close()
            # DATASET INFO
            datasetf.write("NAME = Dihedral angle restraints\n")
            datasetf.write("TYPE = DIHE\n")
            datasetf.write("FILE = dihedrals\n")
            datasetf.write("//\n")
          elif el=='hbonds':
            content = open(fname,'r').readlines()
            count = 0
            for line in content:
              if line[:4].upper()=="ASSI" or line[:4].upper()==" ASS" : count += 1
            # READ THE ORIGINAL DATA
            r = restraint_file(fname,'r',"DIST")
            r.read()
            print "Expected: %5i, Read: %5i."%(count,len(r.restraintlist))
            if count!=len(r.restraintlist):
              print "######## WARNING #########"
            r.close()
            # WRITE THE NEW DATA
            rout = restraint_file(fout,'w',"DIST")
            rout.mwrite(r.restraintlist)
            rout.close()
            r.close()
            # DATASET INFO
            datasetf.write("NAME = Hydrogen bond restraints\n")
            datasetf.write("TYPE = DIST\n")
            datasetf.write("FILE = hbonds\n")
            datasetf.write("//\n")
      datasetf.close()
      # COPY A STRUCTURE AS TEMPLATE
      inpdb = os.path.join(tmpproj,"str/wt/%s_cns_w_1.pdb"%pname)
      shutil.copy(inpdb,
                  xplr.template)
      # COPY ALL STRUCTURES
      pdbs = glob.glob(os.path.join(tmpproj,"str/wt/%s_cns_w_*.pdb"%pname))
      for pdb in pdbs:
        shutil.copy(pdb,
                    os.path.join(queen.pdb,os.path.basename(pdb)))
      # JOIN INTO ENSEMBLE
      ensemble = os.path.join(queen.pdb,'%s_ensemble.pdb'%pname)
      yas_joinpdb(nmvconf["YASARA_RUN"],pdbs,ensemble,xplorflag=1)
      # TEST RUN
      print "Checking data for usage with QUEEN"
      if pname == '1cs7v':
        qn_checkdata(queen,xplr,'all',iterate=1)
      else:
        qn_checkdata(queen,xplr,'all')
      # DELETE TMP PROJECT PATH
      dsc_rmdir(tmpproj)
  # DELETE TMPPATH
  dsc_rmdir(tmppath)

#  ===========================================================================
#   S U B S C R I P T   6 0 :  C O R R E L A T E   I N F O - S T R U C T U R E
#  ===========================================================================
#
def nmv_Iunivsmodelquality(projectpath,dataset,outputpath):
  print "Correlating information with structural properties."
  skiplist = []
  # BUILD LIST OF SUITABLE PROJECTS
  projectdirs = glob.glob(os.path.join(projectpath,'*'))
  projects = {}
  for projectdir in projectdirs:
    id = os.path.basename(projectdir)
    # CHECK IF PDB FILES ARE PRESENT
    id_ensemble = os.path.join(projectdir,'pdb/%s_ensemble.pdb'%id)
    if os.path.exists(id_ensemble) and id not in skiplist:
      projects[id] = {}
      projects[id]['ensemble'] = id_ensemble
  print "Found %i projects suitable for analysis."%len(projects)
  # CREATE QUALITY INFORMATION FOR ALL ENSEMBLES
  for id in projects:
    id_quafile = "%s.qua"%projects[id]['ensemble'][:-4]
    # CHECK IF QUALITY EXISTS, OTHERWISE BUILD IT
    if not os.path.exists(id_quafile):
      pdb_getqua(projects[id]['ensemble'],id_quafile)
    projects[id]['quafile'] = id_quafile
  # DICTIONARY FOR AVERAGES CC'S
  ccs={}
  # EXTRACT INFORMATION SCORES
  for id in projects:
    print "* %s *"%id
    # SETUP QUEEN
    queen = qn_setup(nmvconf,id)
    # READ RESTRAINTS
    data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
    restraints = data["data"]+data["bckg"]
    # CHECK IF Iuni FILE EXISTS
    iuni_file = os.path.join(queen.outputpath,'Iuni_%s.dat'%dataset)
    # IF NOT CREATE Iuni FILE
    if not os.path.exists(iuni_file):
      xplr  = qn_setupxplor(nmvconf,id)
      qn_infuni(queen,xplr,dataset)
    # CORRELATE Iuni TO PDBFILE
    ipr = qn_Iuniperres(iuni_file,restraints,projects[id]['ensemble'])
    # LETS CHECK THAT WE ARE STILL ON TRACK HERE
    before,after = 0.0,0.0
    # TOTAL UNI INFO BEFORE
    uni = qn_readinffile(iuni_file)
    for r in restraints:
      if r.type=='DIST' and not r.ambiguous:
        before += uni[str(r)][0]
    # TOTAL UNI INFO AFTER
    for chain in ipr:
      for residue in ipr[chain]:
        after += ipr[chain][residue]
    # WARN USER IF NECESSARY
    if str(before)!=str(after):
      warning("Information seems to missing!")
    # WRITE OUTPUT FILE
    outputfile = os.path.join(outputpath,'Iuni_res_%s.dat'%id)
    xmgr = graceplot(outputfile,'xy','w')
    xmgr.xlab = "Residue Number"
    xmgr.ylab = "Unique information (%)"
    xmgr.writeheader()
    for chain in ipr:
      residues = ipr[chain].keys()
      residues.sort()
      for residue in residues:
        xmgr.write([residue,ipr[chain][residue]])
      xmgr.newset()
    xmgr.close()
    # READ QUALITY FILE
    print "Reading quality information."
    pdbfinder = pdb_finder(projects[id]['quafile'],'r',1,error)
    pdbfinder.read()
    # THE CHECKS WE LOOK AT
    checks = [' Access','  Packing-1','  Packing-2','  Phi/psi', '  Backbone','  Bumps']
    checkd = {}
    for chain in ipr:
      checkd[chain] = {}
      for check in checks:
        quastr =  pdbfinder.fieldvalue(check)
        checkd[chain][check]=checkd[chain].get(check,[])
        qualist = quastr.split('|')[0]
        # ADD ALL TO LIST, SET ? TO -1
        for ch in qualist:
          if ch!='?': checkd[chain][check].append(int(ch))
          else: checkd[chain][check].append(-1)
    # CORRELATE CHECK AGAINST INFO
    print "Correlating quality with restraint information."
    for chain in ipr:
      print "Chain: '%s'"%chain
      # BUILD LIST OF IUNI
      iuni = []
      for residue in ipr[chain]:
        iuni.append(ipr[chain][residue])
      for check in checks:
        # STRIP CHECK NAME
        checkn = check.strip()
        checkn = checkn.replace('/','-')
        # CALCULATE CORRELATION COEFFICIENT
        chelist = [el for el in checkd[chain][check] if el!=-1]
        inflist = []
        for i in range(len(iuni)):
          if checkd[chain][check][i]!=-1: inflist.append(iuni[i])
        # WRITE CORRELATION PLOT
        file = os.path.join(outputpath,'cc_Iuni_vs_%s_%s.dat'%(checkn,
                                                               id))
        xmgr = graceplot(file,'xy','w')
        xmgr.square = 1
        xmgr.xlab = 'Unique information per residue (%)'
        xmgr.ylab = 'Normalized quality score - %s.'%checkn
        xmgr.writeheader()
        for i in range(len(inflist)):
          xmgr.write([inflist[i],chelist[i],i])
        xmgr.close()
        # CALCULATE CORRELATION COEFFICIENT
        cc = list_cc(inflist,chelist)
        if cc!=None :
          print "%11s: %6.2f"%(check,cc)
          # WRITE TO SUMMARY FILE
          file = os.path.join(outputpath,'sum_cc_Iuni_vs_%s.dat'%checkn)
          # CREATE HEADER
          if not os.path.exists(file):
            xmgr=graceplot(file,'xy','w')
            xmgr.xlab = 'PDB entry'
            xmgr.ylab = 'Correlation coefficient'
            xmgr.title = 'Correlation Iuni vs %s'%checkn
            xmgr.writeheader()
            xmgr.close()
          # ADD DATAPOINTS
          else:
            xmgr=graceplot(file,'xy','a')
            xmgr.write([projects.keys().index(id),cc,id])
            xmgr.close()
          # STORE IN DICTIONARY
          ccs[checkn]=ccs.get(checkn,[])+[cc]
        else:
          warning('list_cc zerodivision')
  # WRITE SUMMARY
  file = os.path.join(outputpath,'sum_cc_Iuni_vs_all.dat')
  file = open(file,'w')
  for key in ccs:
    avg = avg_list(ccs[key])
    file.write("%12s: %7.3f +-/ %7.3f\n"%(key,avg[0],avg[1]))
  file.close()


#  =======================================================================
#   S U B S C R I P T   6 1  :   P R E P A R E  D R E S S
#  =======================================================================
#
def nmv_preparedress(inpath,outpath):
  # SET TEMPORARY PATH
  tmppath = dsc_tmpdir(outpath)
  # GET LIST OF ENTRIES
  filelist = glob.glob(os.path.join(inpath,'*.tgz'))
  # SKIPLIST ENTRIES
  # 1k5o : backbone atoms missing
  # 1nwb : backbone atoms missing
  # 3ci2 : backbone atoms missing
  # second list are entries with missing atoms or additional atoms
  skiplist = ['1k5o','1nwb','3ci2']
  nmismatches, mismatches = 0,[]
  # CYCLE ENTRIES
  for file in filelist:
    pdbid = os.path.basename(file)[:-4]
    # PATH DEFINITION
    pdb_path = os.path.join(outpath,pdbid)
    if not os.path.exists(pdb_path) and pdbid not in skiplist \
           and not os.path.exists(os.path.join(outpath,"%s_mismatch"%pdbid)):
      print "Creating directory structure."
      qn_createproject(nmvconf,pdbid,projectpath=outpath)
      queen = qn_setup(nmvconf,pdbid,projectpath=outpath)
      xplor = qn_setupxplor(nmvconf,pdbid,projectpath=outpath)
      # CONVERT PDB FILES
      pdb_orig = nmv_adjust(nmvconf["PDB"],pdbid)
      yas_splitpdb2xplor(nmvconf["YASARA_RUN"],
                         pdb_orig,
                         queen.pdb,
                         pdbid)
      # OPEN TARFILE AND EXTRACT IT
      tf = tarfile.open(file,"r:gz")
      for tarinfo in tf:
        tf.extract(tarinfo,path=tmppath)
      tf.close()
      tmp = os.path.join(tmppath,pdbid)
      # CONVERT THE MTF FILE
      mtf_file = os.path.join(tmp,'%s_cns.mtf'%pdbid)
      cns_mtf2psf(nmvconf["CNS"],
                  mtf_file,
                  xplor.psf)
      # COPY THE RESTRAINT FILES
      rfiles = glob.glob(os.path.join(tmp,'*.tbl'))
      # OPEN DATASET DESCRIPTION FILE
      dset = open(nmv_adjust(queen.dataset,'all'),'w')
      # DISTANCE RESTRAINTS
      for rfile in rfiles:
        # EXTRACT CORE NAME
        fname = os.path.basename(rfile).split('.')[0]
        # COPY THE FILE
        shutil.copy(rfile,
                    nmv_adjust(queen.table,fname))
        # WRITE TO DATASET DESCRIPTION FILE
        if fname == 'unambig':
          dset.write("NAME = Distance restraints\nTYPE = DIST\n")
        elif fname == 'dihedrals':
          dset.write("NAME = Dihedral angle restraints\nTYPE = DIHE\n")
        elif fname == 'hbonds':
          dset.write("NAME = Hydrogen bond restraints\nTYPE = DIST\n")
        dset.write("FILE = %s\n"%fname)
        dset.write("//\n")
      # DELETE TEMPORARY PATH
      dsc_rmdir(tmp)
    if pdbid not in skiplist and not os.path.exists(os.path.join(outpath,"%s_mismatch"%pdbid)) :
      print pdbid
      # SETUP QUEEN AND XPLOR
      queen = qn_setup(nmvconf,pdbid,projectpath=outpath)
      xplor = qn_setupxplor(nmvconf,pdbid,projectpath=outpath)
      # SOME BASIC DATA VALIDATION
      psf = open(xplor.psf,'r').readlines()
      for line in psf:
        if "!NATOM" in line:
          natoms_psf = int(line.split()[0])
          break
      natoms_pdb = 0
      pdbfile = os.path.join(queen.pdb,"%s_001.pdb"%pdbid)
      pdb = pdb_file.Structure(pdbfile)
      for chain in pdb.peptide_chains:
        for residue in chain:
          for atom in residue:
            natoms_pdb += 1
      # WARNING
      if natoms_psf != natoms_pdb:
        print "* %s *"%pdbid
        print "PDB: %5i - PSF: %5i"%(natoms_pdb,natoms_psf)
        warning("Atom mismatch for PDB %s"%pdbid)
        newname = queen.path+'_mismatch'
        os.rename(queen.path,newname)
        nmismatches += 1
      else:
        if not os.path.exists(xplor.template):
          shutil.copy(pdbfile,
                      xplor.template)
          if os.path.exists('/home/snabuurs/secondary_data/db_queen/%s/log/'%pdbid):
            if qn_checkdata(queen,xplor,'all')==0:
              print "Project %s seems to be fine!"%pdbid
            else:
              newname = queen.path+'_mismatch'
              os.rename(queen.path,newname)
              nmismatches += 1
          else:
            newname = queen.path+'_mismatch'
            os.rename(queen.path,newname)
            nmismatches += 1
  print "%i mismatches."%nmismatches
  # DELETE TMP PATH
  dsc_rmdir(tmppath)



#  =======================================================================
#   S U B S C R I P T   6 2  :   R E F I N E  S T R U C T U R E S
#  =======================================================================
#
# REFINE A STRUCTURE FOR THE DRESS RUN ON THE CLUSTER
def nmv_dressproject(projectname,dataset):
  # SET PROJECTPATH FOR NOW
  nmvconf["Q_PROJECT"]='/storage/data/db_dress/'
  # CUTOFFS FOR VIOLATION ANALYSIS
  dslist = [el*0.1 for el in range(1,6)]
  dhlist = [el for el in range(1,6)]
  cutoff={"DIST":dslist,"DIHE":dhlist}
  thr_noe, thr_dih = 0.5, 5
  # INITIALIZE SETUP AND XPLOR
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # SEE IF WE NEED TO CONTINUE
  if not os.path.exists(os.path.join(queen.path,'pdb_%s_dress.tgz'%projectname)):
    # READ DATA
    data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
    # COMBINE ALL DATA, WE ALSO CHECK THE BACKGROUND INFORMATION!
    restraints = data["data"] + data["bckg"]
    # EXTRACT THE TARFILE WITH THE STRUCTURES
    pdblist_input = []
    tfile_input = os.path.join(queen.path,'pdb_input.tgz')
    tf = tarfile.open(tfile_input,"r:gz")
    for tarinfo in tf:
      # FILE?
      if tarinfo.isreg():
        fname = os.path.join(queen.path,tarinfo.name)
        pdblist_input.append(fname)
        # IF ORIGINAL FILE DOES NOT EXIST EXTRACT
        if not os.path.exists("%s.ori"%fname[:-4]):
          tf.extract(tarinfo,path=queen.path)
      # ELSE EXTRACT
      else:
        tf.extract(tarinfo,path=queen.path)
    tf.close()
    # BUILD THE PDB LIST
    for pdb in pdblist_input:
      # RENAME STRUCTURES
      outpdb = "%s.ori"%pdb[:-4]
      if not os.path.exists(outpdb):
        os.rename(pdb,outpdb)
    # REBUILD THE HYDROGENS
    print "Rebuilding hydrogens."
    pdblist_ori = glob.glob(os.path.join(queen.pdb,'*.ori'))
    for pdb in pdblist_ori:
      outpdb = "%s.pdb"%pdb[:-4]
      if not os.path.exists(outpdb):
        print "%s\r"%pdb,
        sys.stdout.flush()
        xplor_hbuild(pdb,outpdb,xplr.psf)
    print "\nDone."
    # DO THE VIOLATION ANALYSIS ON THE INPUT
    outputfile = os.path.join(queen.outputpath,'viol_%s.txt'%projectname)
    if not os.path.exists(outputfile):
      xplor_violanalysis(pdblist_input,xplr.psf,restraints,outputfile,cutoff)
    # TAR THE INPUT STRUCTURES
    tfile = os.path.join(queen.path,'pdb_%s_clean.tgz'%projectname)
    tf = tarfile.open(tfile,'w:gz')
    for pdb in pdblist_input:
      tf.add(pdb,
             'pdb/%s'%os.path.basename(pdb))
    tf.close()
    # REFINE THE STRUCTURES
    print "Refining structures and checking acceptance."
    allaccepted,trial,maxtrial = 0,1,5
    while trial <= maxtrial and not allaccepted:
      # SET THE SEED
      if trial == 1: seed = 1234567
      else: seed = randint(1,1000000)
      # DO THE REFINEMENT
      pdblist_output = []
      for pdb in pdblist_input:
        outpdb = "%s_dress.pdb"%pdb[:-4]
        pdblist_output.append(outpdb)
        if not os.path.exists(outpdb):
          print "%s\r"%pdb,
          sys.stdout.flush()
          xplor_refstruct(pdb,outpdb,xplr.psf,restraints,
                          thr_noe=thr_noe,thr_dih=thr_dih,seed=seed)
      # CHECK ACCEPTANCE
      allaccepted = 1
      for pdb in pdblist_output:
        if not xplor_accept(pdb,xplr.psf,restraints,
                            thr_noe=thr_noe,thr_dih=thr_dih):
          allaccepted = 0
          os.remove(pdb)
      trial += 1
    print "\nDone"
    # DO THE VIOLATION ANALYSIS ON THE REFINED STRUCTURES
    pdblist = glob.glob(os.path.join(queen.pdb,'*_dress.pdb'))
    outputfile = os.path.join(queen.outputpath,'viol_%s_dress.txt'%projectname)
    if not os.path.exists(outputfile):
      xplor_violanalysis(pdblist,xplr.psf,restraints,outputfile,cutoff)
    # TAR THE REFINED STRUCTURES
    tfile = os.path.join(queen.path,'pdb_%s_dress.tgz'%projectname)
    tf = tarfile.open(tfile,'w:gz')
    pdblist = glob.glob1(queen.pdb,'*_dress.pdb')
    for pdb in pdblist:
      tf.add(os.path.join(queen.pdb,pdb),
             'pdb/%s'%os.path.basename(pdb))
    tf.close()
    # REMOVE THE PDB DIRECTORY
    time.sleep(1)
    shutil.rmtree(queen.pdb)



#  ========================================================================
#   S U B S C R I P T   6 3  :   B U I L D   W H A T I F   D A T A B A S E
#  ========================================================================
#
def nmv_buildwifdb(dbpath,inputpath='/home/snabuurs/secondary_data/db_queen'):
  print "Building WHAT IF NMR database."
  dirlist = glob.glob(os.path.join(inputpath,'*'))
  listfile = os.path.join(dbpath,'PDB.LIS')
  print "Evaluating %i NMR ensembles."%len(dirlist)
  # FILTER OUT PROJECTS WITH STRUCTURES
  pdbd = {}
  for dir in dirlist:
    pdbid = os.path.basename(dir)
    pdblist = glob.glob(os.path.join(dir,'pdb/%s_cns_w_*.pdb'%pdbid))
    if len(pdblist)==25:
      pdbd[pdbid]={}
      pdbd[pdbid]['structures'] = pdblist
      pdbd[pdbid]['ensemble'] = os.path.join(dir,'pdb/%s_ensemble.pdb'%pdbid)
      pdbd[pdbid]['quafile'] = os.path.join(dir,'pdb/%s_ensemble.qua'%pdbid)
  print "%i structures suitable for QUEEN."%len(pdbd.keys())
  # FILTER BASED ON QUALITY INDICATORS
  print "Reading quality indicators."
  qualist = []
  for pdbid in pdbd:
    print "%s\r"%pdbid,
    sys.stdout.flush()
    quafile = pdbd[pdbid]['quafile']
    pdbfinder = pdb_finder(quafile,"r",1,error)
    pdbfinder.read()
    qua = float(pdbfinder.fieldvalue(' Quality'))
    pdbd[pdbid]['quality'] = qua
    qualist.append(qua)
  print
  avg = avg_list(qualist)
  qua_avg, qua_sd = avg[0], avg[1]
  qua_upp = qua_avg + qua_sd
  qua_low = qua_avg - qua_sd
  # FILTER BASED ON RMSD
  print "Determining RMSD values."
  rmsddump = '/tmp/buildwifdb_rmsd.dump'
  rmsdlist = []
  if os.path.exists(rmsddump):
    dump = open(rmsddump,'r')
    rmsdd = cPickle.load(dump)
    dump.close()
    for pdbid in pdbd:
      pdbd[pdbid]['rmsd']=rmsdd[pdbid]
      rmsdlist.append(rmsdd[pdbid])
  else:
    rmsdd = {}
    for pdbid in pdbd:
      print "%s\r"%pdbid,
      sys.stdout.flush()
      rmsd_pdb = prft_rmsd(pdbd[pdbid]['structures'],selection='bb')
      rmsd = avg_list(rmsd_pdb)[0]
      rmsdlist.append(rmsd)
      pdbd[pdbid]['rmsd']=rmsd
      rmsdd[pdbid] =rmsd
    dump = open(rmsddump,'w')
    cPickle.dump(rmsdd,dump)
    dump.close()
    print
  avg = avg_list(rmsdlist)
  rmsd_avg, rmsd_sd = avg[0], avg[1]
  rmsd_upp = rmsd_avg + rmsd_sd
  rmsd_low = rmsd_avg - rmsd_sd
  # CYCLE AGAIN AND DO THE FILTERING
  print "Filtering acceptable structures."
  outfile = open(listfile,'w')
  naccepted = 0
  for pdbid in pdbd:
    print "%s\r"%pdbid,
    sys.stdout.flush()
    fname = 'pdb%s.ent'%pdbid
    qua = pdbd[pdbid]['quality']
    rmsd = pdbd[pdbid]['rmsd']
    if qua <= qua_upp and qua >= qua_low and \
       rmsd <= rmsd_upp and rmsd >= rmsd_low:
      naccepted += 1
      outfile.write('%s\n'%pdbid)
      if not os.path.exists(os.path.join(dbpath,fname)):
        yas_xplor2pdb(nmvconf['YASARA_RUN'],
                      pdbd[pdbid]['structures'][0],
                      os.path.join(dbpath,fname))
  print
  print "%i structures meet acceptable criteria."%naccepted
  print "Done."


#  =======================================================================
#   S U B S C R I P T   6 4  :   O P T I M I Z E   R M S D   S U R F A C E
#  =======================================================================
#
def nmv_optimizermsdsurface(projectdir,dataset,outputpath):
  print "Building and optimizing RMSD surface."
  # SET AXIS RESOLUTION AND AXIS LENGTH
  xstep = ystep = 0.1
  xrange = [0.5, 3.5]
  yrange = [3.0, 6.0]
  # BUILD LIST OF PROJECT DIRECTORIES
  dirlist = glob.glob(os.path.join(projectdir,'*'))
  # BUILD DICTIONARY
  projects = {}
  # CYCLE THE PROJECTS
  for dir in dirlist:
    # GET PROJECTNAME
    project = os.path.basename(dir)
    # CHECK IF WE HAVE ASSOCIATED STRUCTURES
    pdblist = glob.glob(os.path.join(dir,'pdb/%s_cns_w_*.pdb'%project))
    # AND THE QUALITY SUMMARY EXISTS
    pdbqua  = os.path.join(dir,'pdb/%s_ensemble.qua'%project)
    if len(pdblist)==25 and os.path.exists(pdbqua):
      # STORE IN PROJECTS DIR
      projects[project] = {}
      # STORE THE QUALITY FILE LOCATION
      projects[project]['quality'] = pdbqua
      # STORE THE LOCATIONS OF THE INDIVIDUAL STRUCTURES
      projects[project]['structures'] = pdblist
      # STORE THE ENSEMBLE LOCATION
      projects[project]['ensemble'] = os.path.join(dir,'pdb/%s_ensemble.pdb'%project)
      # STORE SET INFORMATION
      setdict = {}
      setfile = os.path.join(dir,'output/setinfo_%s.dat'%dataset)
      content = open(setfile,'r').readlines()
      # DIFFERENTIATE BETWEEN DIFFERENT VERSIONS OF QUEEN
      if content[0][0]=='#': lines = content[1:4]
      else: lines = content[0:3]
      for line in lines: setdict[line.split()[0]]=float(line.split()[2])
      # STORE QUEEN INFO FOR EACH PROJECT
      projects[project]['Hstructure|R'] = float(setdict['Hstructure|R'])
  # CALCULATE SHAPE VALUES
  dump_shape = os.path.join(nmvconf["TMP"],'optimize_rmsd_surface_SHAPE_tmp.dump')
  recalculate_shape = True
  # READ SHAPE DUMP
  if os.path.exists(dump_shape):
    print "Reading shape dictionary from cPickled file."
    # LOAD SHAPE DICT
    shape = cpi_load(dump_shape)
    # CHECK IF STILL IN SYNC
    shapedprojects = [el for el in projects.keys() if el in shape.keys()]
    if len(shapedprojects) == len(projects.keys()):
      recalculate_shape = False
      print "Shape file still in sync."
    else: print "Shape file out of sync."
    # PLOT SHAPE DISTRUBUTION
    dct_bin(shape,binsize=0.1,plot2screen=True)
  # CALCULATE SHAPE IF NECESSARY
  if recalculate_shape:
    print "(Re)calculating shape dictionary."
    shape = {}
    for project in projects:
      shape[project] = pdb_anisotropy(projects[project]['structures'],
                                      nmvconf["GWHATIF_RUN"])
    # DUMP SHAPE DICTIONARY
    cpi_dump(shape,dump_shape)
  # CALCULATE THE RMSD VALUES
  dump_rmsd = os.path.join(nmvconf["TMP"],'optimize_rmsd_surface_RMSD_tmp.dump')
  recalculate_rmsd = True
  # READ RMSD DUMP
  if os.path.exists(dump_rmsd):
    print "Reading rmsd dictionary from cPickled file."
    # LOAD RMSD DICT
    rmsd = cpi_load(dump_rmsd)
    # CHECK IF STILL IN SYNC
    rmsdprojects = [el for el in projects.keys() if el in rmsd.keys()]
    if len(rmsdprojects) == len(projects.keys()):
      recalculate_rmsd = False
      dct_bin(rmsd,binsize=0.4,plot2screen=True)
      print "RMSD file still in sync."
    else: print "RMSD file out of sync."
  # CALCULATE RMSD IF NECESSARY
  if recalculate_rmsd:
    print "(Re)calculating rmsd dictionary."
    rmsd = {}
    for project in projects:
      rmsdlist = prft_rmsd(projects[project]['structures'],
                           selection='heavy')
      rmsd[project] = avg_list(rmsdlist)[0]
    # DUMP RMSD DICTIONARY
    cpi_dump(rmsd,dump_rmsd)
  # CALCULATE THE PDB RMSD VALUES
  dump_pdbrmsd = os.path.join(nmvconf["TMP"],'optimize_rmsd_surface_PDBRMSD_tmp.dump')
  recalculate_pdbrmsd = True
  # READ RMSD DUMP
  if os.path.exists(dump_pdbrmsd):
    print "Reading PDB rmsd dictionary from cPickled file."
    # LOAD RMSD DICT
    pdbrmsd = cpi_load(dump_pdbrmsd)
    # CHECK IF STILL IN SYNC
    pdbrmsdprojects = [el for el in projects.keys() if el in pdbrmsd.keys()]
    if len(pdbrmsdprojects) == len(projects.keys()):
      recalculate_pdbrmsd = False
      #dct_bin(rmsd,binsize=0.4,plot2screen=True)
      print "PDB RMSD file still in sync."
    else: print "PDB RMSD file out of sync."
  # CALCULATE RMSD IF NECESSARY
  if recalculate_pdbrmsd:
    print "(Re)calculating PDB rmsd dictionary."
    pdbrmsd = {}
    for project in projects:
      # SPLIT PDB FILE
      inpdb = nmv_adjust(nmvconf["PDB"],project)
      if os.path.exists(inpdb):
        print project
        pdblist = yas_splitpdb2xplor(nmvconf["YASARA_RUN"],
                                     inpdb,
                                     nmvconf["TMP"],
                                     project)
        # CALCULATE RMSD
        pdbrmsdlist = prft_rmsd(pdblist,
                                selection='heavy')
        if pdbrmsdlist:
          rmsdval = avg_list(pdbrmsdlist)[0]
          pdbrmsd[project] = rmsdval
          print "%3i %s %8.3f %8.3f"%(projects.keys().index(project),
                                      project,rmsdval,rmsd[project])
        else:
          pdbrmsd[project] = None
          print "Profit Error!"
        # DELETE FILES
        for file in pdblist:
          os.remove(file)
      else:
        pdbrmsd[project] = None
    # DUMP RMSD DICTIONARY
    cpi_dump(pdbrmsd,dump_pdbrmsd)
  # CONSTRUCT XYZ DATAPOINTS
  for project in projects.keys():
    x = shape[project]
    y = projects[project]['Hstructure|R']
    z = rmsd[project]
    # STORE DATAPOINT
    projects[project]['datapoint']=[x,y,z]
  # CONSTRUCT THE AXIS LISTS
  xlist = [el*xstep for el in range(int(xrange[0]/xstep),int(xrange[1]/xstep)+1)]
  ylist = [el*ystep for el in range(int(yrange[0]/ystep),int(yrange[1]/ystep)+1)]
  # LISTS TO SAMPLE
  deltas = [0.125] #[0.075,0.100,0.125,0.150]
  npoint = [10] #[0,5,10,15,20,25]
  # OPEN SURFACE FILES
  par_rmsd   = open(os.path.join(outputpath,'param_rmsd.dat'),'w')
  par_r      = open(os.path.join(outputpath,'param_r.dat'),'w')
  par_perc   = open(os.path.join(outputpath,'param_perc.dat'),'w')
  par_rxrmsd = open(os.path.join(outputpath,'param_rxrmsd.dat'),'w')
  # WRITE NUMBER OF POINTS
  for file in [par_rmsd,par_r,par_perc,par_rxrmsd]:
    file.write("%i %i\n"%(len(npoint),len(deltas)))
    file.flush()
  # SAMPLE DELTA IN OUR GAUSSION SMOOTHING
  for delta in deltas:
    # SAMPLE NUMBER OF POINTS
    for npoints in npoint:
      print "\n# npoints: %5i"%npoints
      print "#   delta: %5.3f"%delta
      print "###############"
      # CREATE DATALIST
      data = [projects[project]['datapoint'] for project in projects.keys()
              if projects[project].has_key('datapoint')]
      print "%4i datapoints"%len(data)
      # CYCLE THE PROJECTS
      surface = surf_avg(xlist,ylist,data,
                         delta=delta,
                         cutoff=npoints)
      # PLACE DATA POINTS ON GRID
      ongrid  = surf_placeongrid(data,xstep,ystep)
      # TAKE POINTS INCLUDED IN FIT
      nonzero = surf_infit(surface,ongrid)
      # CALCULATE RMSD OF FIT
      rmsd_surf = surf_rmsd(surface,nonzero)
      r_surf = surf_corr(surface,nonzero)
      print "     RMSD:     %5.3f"%rmsd_surf
      print "        r:     %5.3f"%r_surf
      # WRITE SURFACE FILE
      outputfile = os.path.join(outputpath,'surf_%04.2f_%02i.dat'%(delta,
                                                                  npoints))
      out = open(outputfile,'w')
      out.write("%i %i\n"%(len(ylist),len(xlist)))
      for x in xlist:
        for y in ylist:
          out.write("%10.5f "%surface[x][y])
        out.write("\n")
      out.write("%3.1f %3.1f\n"%(yrange[0],yrange[1]))
      out.write("%3.1f %3.1f\n"%(xrange[0],xrange[1]))
      out.close()
      # CALCULATE PREDICTIVE POWER
      rmsdlist,rlist,lennonzero = [],[],[]
      outputfile = os.path.join(outputpath,'corr_%04.2f_%02i.dat'%(delta,
                                                                   npoints))
      xmgr = graceplot(outputfile,'xy','w')
      xmgr.square = 1
      xmgr.xlab = 'measured RMSD (A)'
      xmgr.ylab = 'predicted RMSD (A)'
      xmgr.writeheader()
      for i in range(10):
        projectlist = [project for project in projects.keys()
                       if projects[project].has_key('datapoint')]
        start = i*(len(projectlist)/10)
        end   = (i+1)*(len(projectlist)/10)
        # DIVIDE SETS
        testset = projectlist[start:end]
        workingset = projectlist[:start] + projectlist[end:]
        # BUILD SURFACE
        surfvalues = [projects[el]['datapoint'] for el in workingset
                      if projects[el].has_key('datapoint')]
        surface = surf_avg(xlist,ylist,surfvalues,
                           delta,npoints)
        # CHECK TEST VALUES
        testvalues = [projects[el]['datapoint'] for el in testset
                      if projects[el].has_key('datapoint')]
        # PLACE ON GRID
        ongrid = surf_placeongrid(testvalues,xstep,ystep)
        # DELETE EXCLUDED POINTS
        nonzero = surf_infit(surface,ongrid)
        lennonzero.append(len(nonzero))
        if len(nonzero)>5:
          # ADD RMSD AND R
          rmsdlist.append(surf_rmsd(surface,nonzero))
          rlist.append(surf_corr(surface,nonzero))
        # WRITE CORRELATION TO PLOT
        for value in nonzero:
          xmgr.write([value[2],surface[value[0]][value[1]]])
      # CLOSE CORRELATION PLOT
      xmgr.close()
      nz = avg_list(lennonzero)[0]
      rmsd_avg = avg_list(rmsdlist)
      print " selected:     %5.3f %%"%((nz/len(ongrid))*100)
      print " avg RMSD:     %5.3f +/- %5.3f"%(rmsd_avg[0],rmsd_avg[1])
      r_avg = avg_list(rlist)
      print "    avg r:     %5.3f +/- %5.3f"%(r_avg[0],r_avg[1])
      # WRITE VALUES TO LOG FILE
      par_rmsd.write("%5.2f "%(rmsd_avg[0]))
      par_r.write("%5.2f "%(r_avg[0]))
      par_perc.write("%5.2f "%(nz/len(ongrid)*100))
      par_rxrmsd.write("%5.2f "%(rmsd_avg[0]*r_avg[0]))
    # END BLOCK
    for file in [par_rmsd,par_r,par_perc,par_rxrmsd]:
      file.write("\n")
  # ADD AXIS TO PLOT
  for file in [par_rmsd,par_r,par_perc,par_rxrmsd]:
    file.write("%8.3f %8.3f\n"%(min(npoint),max(npoint)))
    file.write("%8.3f %8.3f\n"%(min(deltas),max(deltas)))
  print "Done."

#  ===========================================================================
#   S U B S C R I P T   6 5 :  C O R R E L A T E   I N F O - X R A Y    D E V
#  ===========================================================================
#
# NOTE: only seqcutoffs of 100 are implemented for the time being...
def nmv_Iunivsxraydeviation(projectpath,dataset,outputpath,seqcutoff=100):
  print "Correlating information with deviation from X-ray structure."
  skiplist = []
  # BUILD LIST OF SUITABLE PROJECTS
  projectdirs = glob.glob(os.path.join(projectpath,'*'))
  projects = {}
  for projectdir in projectdirs:
    id = os.path.basename(projectdir)
    # CHECK IF PDB FILES ARE PRESENT
    id_ensemble = os.path.join(projectdir,'pdb/%s_ensemble.pdb'%id)
    if os.path.exists(id_ensemble) and id not in skiplist:
      projects[id] = {}
      projects[id]['ensemble'] = id_ensemble
      projects[id]['path'] = projectdir
  print "Found %i projects suitable for analysis."%len(projects)
  # CREATE QUALITY INFORMATION FOR ALL ENSEMBLES
  for id in projects:
    id_quafile = "%s.qua"%projects[id]['ensemble'][:-4]
    # CHECK IF QUALITY EXISTS, OTHERWISE BUILD IT
    if not os.path.exists(id_quafile):
      pdb_getqua(projects[id]['ensemble'],id_quafile)
    projects[id]['quafile'] = id_quafile
  # INITIALIZE PDB FINDER
  pdbfinder = pdb_finder(nmvconf["PDBFINDER2"],'r',1)
  pdbfinder.buildindex()
  # FIND HOMOLOGOUS XRAY STRUCTURES BY BLASTING AGAINST THE PDB
  for id in projects:
    print "## Blasting for %s ##"%id
    # GET SEQUENCE FROM PDB FILE
    pdbf = pdb_file.Structure(projects[id]['ensemble'])
    for chain in pdbf.peptide_chains:
      # ADJUST CHAIN ID
      if chain.segment_id == '': chainid = '_'
      else: chainid = chain.segment_id
      # CONSTRUCT SEQUENCE STRING
      sequence = ''
      for residue in chain:
        sequence+=nmcl_aminoacid(residue.name)[0]
      # CHECK IF BLAST FILE EXIST
      blastf = os.path.join(projects[id]['path'],
                            'pdb/%s|%s_pdb_homologs.blast'%(id,
                                                            chainid))
      if not os.path.exists(blastf):
        # DO A BLAST WITH THE SEQUENCE
        bhits = seq_netblastpdb(sequence,outputfile=blastf)
      else:
        # PARSE THE BLAST FILE
        bhits = seq_netblastpdb(sequence,blastfile=blastf)
    # CHECK IF THE ORIGINAL ID IS RETRIEVED
    key = '%s|%s'%(id.upper(),chainid.upper())
    if key not in bhits.keys() or bhits[key]!=100:
      warning("Blast does not return 100% hit!")
    # SORT HITS BY IDENTITY
    elems = bhits.items()
    elems.sort(lambda (k1,v1),(k2,v2): cmp(v2,v1))
    # ONLY TAKE THE TOP FIVE BLAST HITS
    elems = elems[:5]
    # CYCLE ELEMENTS
    for elem in elems:
      # TAKE ONLY GOOD BLAST HITS
      if elem[1] >= seqcutoff:
        # EXTRACT XRAY ID AND CHAINID
        xid = elem[0][:4]
        xchainid = elem[0][5]
        # CHECK IF WE NEED TO CONTINUE
        file = os.path.join(outputpath,'cc_%s_%s.dat'%(id,(xid+xchainid).lower()))
        if not os.path.exists(file):
          # GET INFO ON THE STRUCTURE
          pdbfinder.read(xid)
          method  = pdbfinder.fieldvalue('Exp-Method')
          xdssp   = pdbfinder.chainsecstr(xchainid)
          # CHECK FOR CHAIN BREAKS IN THE X-RAY STRUCTURE
          breaks  = pdbfinder.fieldvalue('  Break')
          if breaks: breaks = int(breaks)
          else: breaks = 0
          # COMPARE THE SEQUENCES
          if method == 'X' and breaks==0 and os.path.exists(nmv_adjust(nmvconf["PDB"],
                                                                       id)):
            print id, chainid, xid, xchainid
            # GET XRAY SEQUENCE
            xseq = pdbfinder.chainseq(xchainid)
            # STORE NMR SEQUENCE
            pdbfinder.read(id)
            nseq = pdbfinder.chainseq(chainid)
            # FIND REGION IN COMMON
            if nseq.find(xseq)!=-1:
              pos = nseq.find(xseq)
              xsta, xend = 0,len(xseq)
              nsta, nend = pos, pos+len(xseq)
            elif xseq.find(nseq)!=-1:
              pos = xseq.find(nseq)
              xsta, xend = pos,pos+len(nseq)
              nsta, nend = 0,len(nseq)
            else:
              xsta, xend = 0,len(nseq)
              nsta, nend = 0,len(xseq)
            # SANITY CHECK
##            print "X",xseq
##            print "N",nseq
##            print xsta,xend,nsta,nend
##            print "X",xseq[xsta:xend]
##            print "N",nseq[nsta:nend]
            if nseq[nsta:nend]==xseq[xsta:xend]: print 'Sequences OK'
            else:
              print "N",len(nseq)
              print "X",len(xseq)
              warning('Sequences not OK')
              break
            # DETERMINE SECSTR RESIDUES IN CRYSTAL STRUCTURE
            suppos = []
            for i in range(len(xdssp[xsta:xend])):
              if xdssp[xsta:xend][i] in ['H','E','T','S']:
                suppos.append(i+1)
            # READ PDBFILES AND TRY TO SUPERIMPOSE THEM ON THE SUPPOS RESIDUES
            npdb = projects[id]['ensemble']
            xpdb = nmv_adjust(nmvconf["PDB"],xid.lower())
            # BUILD THE YASARA SCRIPT
            ysr = ysr_macro(nmvconf["YASARA_RUN"])
            table = os.path.join(nmvconf["TMP"],"yas_%i.tab"%os.getpid())
            ysr.write(["LoadPDB %s"%npdb,
                       "RenameMol %s,A"%chainid])
            for i in range(1,26): ysr.write(["RenumberRes Obj %i,First=1"%i])
            ysr.write(["DelRes not Res %i-%i Obj 1-25"%(nsta+1,nend)])
            for i in range(1,26): ysr.write(["RenumberRes Obj %i,First=1"%i])
            ysr.write(["LoadPDB %s"%xpdb,
                       "DelMol !%s and Obj 26"%(xchainid),
                       "RenameMol %s,A"%xchainid,
                       "RenumberRes Obj 26,First=1",
                       "DelRes Obj 26 not Res %i-%i and not Obj !26"%(xsta+1,xend),
                       "RenumberRes Obj 26,First=1"])
            # FIRST CONSTRUCT A RESIDUE STRING WE HAVE TO DO THIS, AS THE YASARA
            # COMMAND SEEMS TO BE GETTING TO LONG
            resstr,current,grouping = '',-99,0
            for el in suppos:
              if suppos.index(el)==(len(suppos)-1) and grouping==1: resstr +='-%i '%el
              elif suppos.index(el)==(len(suppos)-1) and not grouping: resstr += ' %i'%el
              else:
                if not grouping and el!=current+1: resstr += ' %i'%el
                else:
                  if el == current+1: grouping = 1
                  else:
                    resstr += '-%i %i'%(current,el)
                    grouping = 0
              current = el
            # ADD IT INTO THE YASARA COMMAND AND  DO THE SUPERPOSITIONING
            ysr.write(["SupAtom CA res %s and Obj 1-25, \
            CA res %s and Obj 26,Match=Yes,Flip=No"%(resstr,resstr)])
            #ysr.write(["SupAtom CA and Obj 1-25, CA and Obj 26,Match=Yes,Flip=No"])
            for i in range(1,len(nseq[nsta:nend])+1):
              ysr.write(["AddTab RmsdAtom CA and res %i and Obj 1-25, \
              CA and res %i and Obj 26"%(i,i)])
            ysr.write(["SaveTab %s,2,%%7.3f"%table,
                      "Exit"])
            ysr.submit(conflag=1)
            # READ OUTPUT
            content = open(table,'r').readlines()
            rmsds = []
            # PARSE IT AND WRITE RMSD PLOT
            file = os.path.join(outputpath,'rmsd_%s_%s.dat'%(id,
                                                             (xid.lower()+xchainid.lower())))
            xmgr = graceplot(file,'xydy','w')
            xmgr.xlab = "Residue"
            xmgr.ylab = "Ca RMSD to crystal structure (A)"
            for i in range(1,len(content)):
              rmsd = float(content[i].split()[0])
              sd = float(content[i].split()[1])
              rmsds.append(rmsd)
              xmgr.write([i,rmsd,sd])
            xmgr.close()
            # GET INFORMATION SCORE
            queen = qn_setup(nmvconf,id)
            # READ RESTRAINTS
            data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
            restraints = data["data"]+data["bckg"]
            # THE IUNI FILE
            iuni_file = os.path.join(queen.outputpath,'Iuni_%s.dat'%dataset)
            # CALCULATE IUNI PER RESIDUE (IPR)
            ipr = qn_Iuniperres(iuni_file,restraints,projects[id]['ensemble'])
            scores = []
            for key in ipr[chain.segment_id].keys()[nsta:nend]:
              scores.append(ipr[chain.segment_id][key])
            # CLEAN OUT THE LIST
            xdssp = xdssp[xsta:xend]
            for i in range(len(xdssp)-1,-1,-1):
              if xdssp[i] not in ['H','T','E','S']:
                del scores[i]
                del rmsds[i]
            if len(scores)!=len(rmsds):
              print len(scores)
              print len(rmsds)
              error("MATCHING PROBLEM: scores vs rmsds!")
            # CALCULATE CORRELATION COEFFICIENT
            cc = list_cc(scores,rmsds)
            print "CC: %7.3f"%cc
            if cc!=None :
              # WRITE TO SUMMARY FILE
              file = os.path.join(outputpath,'sum_cc_Iuni_vs_X-ray.dat')
              # CREATE HEADER
              if not os.path.exists(file):
                xmgr=graceplot(file,'xy','w')
                xmgr.xlab = 'PDB entry'
                xmgr.ylab = 'Correlation coefficient'
                xmgr.title = 'Correlation Iuni vs X-ray deviation'
                xmgr.writeheader()
                xmgr.close()
              # ADD DATAPOINTS
              xmgr=graceplot(file,'xy','a')
              xmgr.write([projects.keys().index(id),cc,"%s_%s"%(id,(xid+xchainid).lower())])
              xmgr.close()
            else:
              warning('list_cc zerodivision')
            # CREATE OUTPUT FILE
            file = os.path.join(outputpath,'cc_%s_%s.dat'%(id,(xid+xchainid).lower()))
            xmgr = graceplot(file,'xy','w')
            xmgr.xlab = 'Fraction unique information (%)'
            xmgr.ylab = 'RMSD from x-ray (A)'
            xmgr.square = 1
            xmgr.writeheader()
            for i in range(len(scores)):
              xmgr.write([scores[i],rmsds[i],i])
            xmgr.close()

#  ===========================================================================
#   S U B S C R I P T   6 6 :  T E S T   W H E A T S H E A F
#  ===========================================================================
#
def nmv_testwheatsheaf(projectpath,dataset,outputpath):
  # BUILD PROJECTLIST
  dirlist = glob.glob(os.path.join(projectpath,'*'))[:24]
  # THE QUALITY DICT
  q = {}
  # THE CHECKS
  checks = ['  Phi/psi','  Packing-1','  Packing-2','  Chi-1/chi-2','  Backbone',
            '  Bonds','  Angles','  Torsions','  Planarity','  Chirality',
            '  Peptide-Pl','  Rotamer','  H-Bonds','  Bumps']
  for dir in dirlist:
    projectname = os.path.basename(dir)
    print projectname
    # THE XPLOR PDB FILE
    xpdb = os.path.join(dir,'pdb/%s_ensemble.pdb'%projectname)
    pdbx = os.path.join(dir,'pdb/%s_cns_w_1.pdb'%projectname)
    if os.path.exists(xpdb):
      # READ AND CHECK IT
      tpdb = pdb_file.Structure(xpdb)
      # COUNT RESIDUES AND MODELS
      for chain in tpdb.peptide_chains:
        rcount = len(chain)
      # DETERMINE THE NUMBER OF MODELS
      no_models = pdb_models(xpdb)
      print rcount, no_models, rcount*10
      # CAN WE WHEATSHEAF?
      if rcount < 128 and no_models < 128 and 10*rcount < 9000:
        q[projectname]={}
        # THE PDB PDB FILE AND QUA
        pdb  = os.path.join(outputpath,'%s_ensemble.pdb'%projectname)
        qua_ori  = "%s.qua"%pdb[:-4]
        # THE AVERAGE FILE AND QUA
        avg  = os.path.join(outputpath,'%s_averaged.pdb'%projectname)
        avgx = os.path.join(outputpath,'%s_averaged_x.pdb'%projectname)
        qua_avg  = "%s.qua"%avg[:-4]
        if not os.path.exists(pdb):
          # CONVERT ENSEMBLE TO PDB FORMAT
          yas_xplor2pdb(nmvconf["YASARA_RUN"],
                        xpdb,
                        pdb,
                        no_models=10)
          # GET QUALITY OF THE CONVERTED FILE
          pdb_getqua(pdb,qua_ori)
        else:
          if not os.path.exists(qua_avg):
            # DO ANALYSIS ON THE AVERAGE
            pdb_getqua(avg,qua_avg)
          # READ THE QUALITY FILES
          for quafile in [qua_ori,qua_avg]:
            p = projectname
            # READ THE QUALITY FILE
            pdbfinder = pdb_finder(quafile,"r",1,error)
            pdbfinder.read()
            # GET OVERAL QUALITY
            qua = pdbfinder.fieldvalue(" Quality")
            q[p]["CASP-4"] = q[p].get("CASP-4",[]) + [float(qua)]
            # CHECK
            for qual in checks:
              quastr = pdbfinder.fieldvalue(qual)
              quaval = float(quastr.split('|')[1])
              if qual=='  Packing-1':
                quaval = quaval*10-5
              elif qual=='  Backbone':
                quaval = quaval
              elif qual=='  Packing-2':
                quaval = quaval*6-3
              elif qual=='  Phi/psi':
                quaval = quaval*8-4
              elif qual=='  Chi-1/chi-2':
                quaval = quaval*8-4
              q[p][qual]=q[p].get(qual,[])+[quaval]
  out = os.path.join(outputpath,'summary.txt')
  file = open(out,'w')
  # WRITE SUMMARY
  toprint = checks+['CASP-4']
  file.write("%15s %8s %8s %8s\n"%('','ensemble','wheatsheaf','delta'))
  for id in q:
    file.write("%s\n####\n\n"%id)
    for key in toprint:
      sc_ens = q[id][key][0]
      sc_avg = q[id][key][1]
      file.write("%14s: %8.3f %8.3f %8.2f\n"%(key,
                                              sc_ens,
                                              sc_avg,
                                              sc_avg-sc_ens))
    file.write("\n")
  # AVERAGES
  file.write("\nON AVERAGE (%3i structures)\n###########################\n\n"%len(q.keys()))
  file.write("%15s %21s %21s %8s\n"%('','ensemble avg','wheatsheaf avg','delta'))
  for key in toprint:
    avgs = []
    for i in range(2):
      avglist = []
      for pdb in q:
        avglist.append(q[pdb][key][i])
      avg = avg_list(avglist)
      avgs.append(avg)
    file.write("%14s: %8.3f +/- %8.3f %8.3f +/- %8.3f %8.2f\n"%(key,
                                                                avgs[0][0],
                                                                avgs[0][1],
                                                                avgs[1][0],
                                                                avgs[1][1],
                                                                avgs[1][0]-avgs[0][0]))



#  ================================================================================
#   S U B S C R I P T   6 6 :  C O R R E L A T E   B B   U N C  - S T R U C T U R E
#  =================================================================================
#
def nmv_bbuncvsmodelquality(projectpath,dataset,outputpath,windowsize=11):
  print "Correlating local backbone uncertainty with structural properties."
  skiplist = []
  # BUILD LIST OF SUITABLE PROJECTS
  projectdirs = glob.glob(os.path.join(projectpath,'*'))
  projects = {}
  for projectdir in projectdirs:
    id = os.path.basename(projectdir)
    # CHECK IF PDB FILES ARE PRESENT
    id_ensemble = os.path.join(projectdir,'pdb/%s_ensemble.pdb'%id)
    if os.path.exists(id_ensemble) and id not in skiplist:
      projects[id] = {}
      projects[id]['ensemble'] = id_ensemble
  print "Found %i projects suitable for analysis."%len(projects)
  # CREATE QUALITY INFORMATION FOR ALL ENSEMBLES
  for id in projects:
    id_quafile = "%s.qua"%projects[id]['ensemble'][:-4]
    # CHECK IF QUALITY EXISTS, OTHERWISE BUILD IT
    if not os.path.exists(id_quafile):
      pdb_getqua(projects[id]['ensemble'],id_quafile)
    projects[id]['quafile'] = id_quafile
  # DICTIONARY FOR AVERAGES CC'S
  ccs={}
  # EXTRACT INFORMATION SCORES
  for id in projects:
    print "* %s *"%id
    # SETUP QUEEN
    queen = qn_setup(nmvconf,id)
    xplr  = qn_setupxplor(nmvconf,id)
    # CORRELATE LOCAL UNC TO PDBFILE
    upr = qn_bbuncperresidue(queen,xplr,dataset,windowsize=windowsize)
    # WRITE OUTPUT FILE
    outputfile = os.path.join(outputpath,'Lunc_res_%s.dat'%id)
    xmgr = graceplot(outputfile,'xy','w')
    xmgr.xlab = "Residue Number"
    xmgr.ylab = "Local BB uncertainty (window size = %i)"%windowsize
    xmgr.writeheader()
    for chain in upr:
      residues = upr[chain].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        xmgr.write([residue.number,upr[chain][residue]])
      xmgr.newset()
    xmgr.close()
    # READ QUALITY FILE
    print "Reading quality information."
    pdbfinder = pdb_finder(projects[id]['quafile'],'r',1,error)
    pdbfinder.read()
    # THE CHECKS WE LOOK AT
    checks = [' Access','  Packing-1','  Packing-2','  Phi/psi', '  Backbone','  Bumps']
    checkd = {}
    for chain in upr:
      checkd[chain] = {}
      for check in checks:
        quastr =  pdbfinder.fieldvalue(check)
        checkd[chain][check]=checkd[chain].get(check,[])
        qualist = quastr.split('|')[0]
        # ADD ALL TO LIST, SET ? TO -1
        cutoff = (windowsize-1)/2
        for ch in qualist[cutoff:-cutoff]:
          if ch!='?': checkd[chain][check].append(int(ch))
          else: checkd[chain][check].append(-1)
    # CORRELATE CHECK AGAINST INFO
    print "Correlating quality with restraint information."
    for chain in upr:
      print "Chain: '%s'"%chain
      # BUILD LIST OF IUNI
      iuni = []
      residues = upr[chain].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        iuni.append(upr[chain][residue])
      for check in checks:
        # STRIP CHECK NAME
        checkn = check.strip()
        checkn = checkn.replace('/','-')
        # CALCULATE CORRELATION COEFFICIENT
        chelist = [el for el in checkd[chain][check] if el!=-1]
        inflist = []
        for i in range(len(iuni)):
          if checkd[chain][check][i]!=-1: inflist.append(iuni[i])
        # WRITE CORRELATION PLOT
        file = os.path.join(outputpath,'cc_Lunc_vs_%s_%s.dat'%(checkn,
                                                               id))
        xmgr = graceplot(file,'xy','w')
        xmgr.square = 1
        xmgr.xlab = 'Unique information per residue (%)'
        xmgr.ylab = 'Normalized quality score - %s.'%checkn
        xmgr.writeheader()
        for i in range(len(inflist)):
          xmgr.write([inflist[i],chelist[i],i])
        xmgr.close()
        # CALCULATE CORRELATION COEFFICIENT
        if len(inflist)!=len(chelist): warning("List lengths differ!")
        cc = list_cc(inflist,chelist)
        if cc!=None :
          print "%11s: %6.2f"%(check,cc)
          # WRITE TO SUMMARY FILE
          file = os.path.join(outputpath,'sum_cc_Lunc_vs_%s.dat'%checkn)
          # CREATE HEADER
          if not os.path.exists(file):
            xmgr=graceplot(file,'xy','w')
            xmgr.xlab = 'PDB entry'
            xmgr.ylab = 'Correlation coefficient'
            xmgr.title = 'Correlation Lunc vs %s'%checkn
            xmgr.writeheader()
            xmgr.close()
          # ADD DATAPOINTS
          else:
            xmgr=graceplot(file,'xy','a')
            xmgr.write([projects.keys().index(id),cc,id])
            xmgr.close()
          # STORE IN DICTIONARY
          ccs[checkn]=ccs.get(checkn,[])+[cc]
        else:
          warning('list_cc zerodivision')
  # WRITE SUMMARY
  file = os.path.join(outputpath,'sum_cc_Lunc_vs_all.dat')
  file = open(file,'w')
  for key in ccs:
    avg = avg_list(ccs[key])
    file.write("%12s: %7.3f +-/ %7.3f\n"%(key,avg[0],avg[1]))
  file.close()


#  ===========================================================================
#   S U B S C R I P T   6 7 :  C O R R E L A T E   I N F - S T R U C T U R E
#  ===========================================================================
#
def nmv_infovsmodelquality(projectpath,dataset,outputpath):
  print "Correlating local backbone information with structural properties."
  skiplist = []
  # BUILD LIST OF SUITABLE PROJECTS
  projectdirs = glob.glob(os.path.join(projectpath,'*'))
  projects = {}
  for projectdir in projectdirs:
    id = os.path.basename(projectdir)
    # CHECK IF PDB FILES ARE PRESENT
    id_ensemble = os.path.join(projectdir,'pdb/%s_ensemble.pdb'%id)
    if os.path.exists(id_ensemble) and id not in skiplist:
      projects[id] = {}
      projects[id]['ensemble'] = id_ensemble
  print "Found %i projects suitable for analysis."%len(projects)
  # CREATE QUALITY INFORMATION FOR ALL ENSEMBLES
  for id in projects:
    id_quafile = "%s.qua"%projects[id]['ensemble'][:-4]
    # CHECK IF QUALITY EXISTS, OTHERWISE BUILD IT
    if not os.path.exists(id_quafile):
      pdb_getqua(projects[id]['ensemble'],id_quafile)
    projects[id]['quafile'] = id_quafile
  # DICTIONARY FOR AVERAGES CC'S
  ccs={}
  # EXTRACT INFORMATION SCORES
  for id in projects:
    print "* %s *"%id
    # SETUP QUEEN
    queen = qn_setup(nmvconf,id)
    xplr  = qn_setupxplor(nmvconf,id)
    # CORRELATE LOCAL INF TO PDBFILE
    ipr = qn_infperresidue(queen,xplr,dataset)
    # WRITE OUTPUT FILE
    outputfile = os.path.join(outputpath,'I_res_%s.dat'%id)
    xmgr = graceplot(outputfile,'xy','w')
    xmgr.xlab = "Residue Number"
    xmgr.ylab = "Local BB information content"
    xmgr.writeheader()
    for chain in ipr:
      residues = ipr[chain].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        xmgr.write([residue.number,ipr[chain][residue]])
      xmgr.newset()
    xmgr.close()
    # READ QUALITY FILE
    print "Reading quality information."
    pdbfinder = pdb_finder(projects[id]['quafile'],'r',1,error)
    pdbfinder.read()
    # THE CHECKS WE LOOK AT
    checks = [' Access','  Packing-1','  Packing-2','  Phi/psi', '  Backbone','  Bumps']
    checkd = {}
    for chain in ipr:
      checkd[chain] = {}
      for check in checks:
        quastr =  pdbfinder.fieldvalue(check)
        checkd[chain][check]=checkd[chain].get(check,[])
        qualist = quastr.split('|')[0]
        # ADD ALL TO LIST, SET ? TO -1
        for ch in qualist:
          if ch!='?': checkd[chain][check].append(int(ch))
          else: checkd[chain][check].append(-1)
    # CORRELATE CHECK AGAINST INFO
    print "Correlating quality with restraint information."
    for chain in ipr:
      print "Chain: '%s'"%chain
      # BUILD LIST OF INF VALUES
      inf = []
      residues = ipr[chain].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        inf.append(ipr[chain][residue])
      for check in checks:
        # STRIP CHECK NAME
        checkn = check.strip()
        checkn = checkn.replace('/','-')
        # CALCULATE CORRELATION COEFFICIENT
        chelist = [el for el in checkd[chain][check] if el!=-1]
        inflist = []
        for i in range(len(inf)):
          if checkd[chain][check][i]!=-1: inflist.append(inf[i])
        # WRITE CORRELATION PLOT
        file = os.path.join(outputpath,'cc_I_vs_%s_%s.dat'%(checkn,
                                                            id))
        xmgr = graceplot(file,'xy','w')
        xmgr.square = 1
        xmgr.xlab = 'Information content per residue'
        xmgr.ylab = 'Normalized quality score - %s.'%checkn
        xmgr.writeheader()
        for i in range(len(inflist)):
          xmgr.write([inflist[i],chelist[i],i])
        xmgr.close()
        # CALCULATE CORRELATION COEFFICIENT
        if len(inflist)!=len(chelist): warning("List lengths differ!")
        cc = list_cc(inflist,chelist)
        if cc!=None :
          print "%11s: %6.2f"%(check,cc)
          # WRITE TO SUMMARY FILE
          file = os.path.join(outputpath,'sum_cc_I_vs_%s.dat'%checkn)
          # CREATE HEADER
          if not os.path.exists(file):
            xmgr=graceplot(file,'xy','w')
            xmgr.xlab = 'PDB entry'
            xmgr.ylab = 'Correlation coefficient'
            xmgr.title = 'Correlation Lunc vs %s'%checkn
            xmgr.writeheader()
            xmgr.close()
          # ADD DATAPOINTS
          else:
            xmgr=graceplot(file,'xy','a')
            xmgr.write([projects.keys().index(id),cc,id])
            xmgr.close()
          # STORE IN DICTIONARY
          ccs[checkn]=ccs.get(checkn,[])+[cc]
        else:
          warning('list_cc zerodivision')
  # WRITE SUMMARY
  file = os.path.join(outputpath,'sum_cc_I_vs_all.dat')
  file = open(file,'w')
  for key in ccs:
    avg = avg_list(ccs[key])
    file.write("%12s: %7.3f +-/ %7.3f\n"%(key,avg[0],avg[1]))
  file.close()


#  ===========================================================================
#   S U B S C R I P T   6 8 :  R E C O O R D   V S   S H I F T X
#  ===========================================================================
#
def nmv_recoordvsshiftx(projectpath,dataset,shiftxpath):
  print "Reading entry names from RefDB."
  refdbn = {}
  # BUILD A DICTIONARY OF REFDB SEQUENCES
  refdblist = os.path.join(shiftxpath,'bmrpdb.html')
  content = open(refdblist,'r').readlines()
  for line in content:
    # TRY TO FIND BMRB KEY
    if line.find('bmrb.wisc.edu') != -1:
      pos1 = line.find('>bmr')
      pos2 = line.find('.str<')
      id = int(line[pos1+4:pos2])
      refdbn[id] = {}
    # FIND PDB ID
    elif line.find('www.rcsb.org') != -1:
      pos1 = line.find('?pdbId')
      pos2 = line.find('(')
      pos3 = line.find(')')
      # GET PDB ID AND SEQ ID AND METHOD
      pdbid = line[pos1+13:pos1+17]
      chaid = line[pos1+17]
      method = line[pos2+1:pos3]
      refdbn[id]['pdb']=pdbid
      refdbn[id]['chain']=chaid
      refdbn[id]['method']=method
  print "Read %i entry names."%(len(refdbn.keys()))
  # READ CHEMICAL SHIFTS FROM REFDB
  print "Reading chemical shifts from RefDB in SHIFTY format."
  refdbN = os.path.join(shiftxpath,'RefDB-N.db')
  content = open(refdbN,'r').readlines()
  refdb = {}
  for line in content:
    line = line.split()
    # GET ID
    if len(line)>1 and line[0] == '#DBBANK':
      id = int(line[2])
      refdb[id]={}
    # GET SHIFTS
    if len(line)>1 and line[0][0] not in ['>','#']:
      resnum = int(line[0])
      shifts = []
      for el in line[3:]:
        if el == '****': shifts.append('?')
        else: shifts.append(float(el))
      refdb[id][resnum]=shifts
  print "Read %i entries."%(len(refdb.keys()))
  match = [el for el in refdb.keys() if el in refdbn.keys()]
  print "Found %i good pairs."%(len(match))
  print "Cycling projects."
  cnt = 0
  dirlist = glob.glob(os.path.join(projectpath,'*'))
  origcc,refcc=[],[]
  for dir in dirlist:
    projectname = os.path.basename(dir)
    print '* %s *'%projectname
    # CHECK FOR ENSEMBLE
    ens = os.path.join(dir,'pdb/%s_ensemble.pdb'%projectname)
    if os.path.exists(ens):
      # BUILD SEQUENCE FOR ENSEMBLE
      pdbf = pdb_file.Structure(ens)
      for chain in pdbf.peptide_chains:
        # ADJUST CHAIN ID
        if chain.segment_id == '': ens_chainid = '_'
        else: ens_chainid = chain.segment_id
        # CONSTRUCT SEQUENCE STRING
        sequence = ''
        for residue in chain: sequence+=nmcl_aminoacid(residue.name)[0]
        # BLAST AGAINS REFDB
        refdbf = '/home/snabuurs/projects/dress_vs_shiftx/refdb.fasta'
        # DO A BLAST WITH THE SEQUENCE
        bhits = seq_blastrefdb(nmvconf["BLAST_RUN"],
                               sequence,
                               refdbf)
        # CYCLE THE HITS
        for hit in bhits:
          # ONLY TAKE FULL HITS FO R NOW, THAT'S EASIER
          if bhits[hit]==100:
            # GET BMRB ID
            bmrbid = int(hit[3:hit.find('.')])
            # STORE PDBID AND CHAINID
            if bmrbid in refdbn.keys():
              pdbid = refdbn[bmrbid]['pdb']
              chaid = refdbn[bmrbid]['chain']
              # GET REFDB SEQUENCE
              pdb = nmv_adjust(nmvconf["PDB"],pdbid.lower())
              if os.path.exists(pdb):
                # READ PDB FILE
                pdbf = pdb_file.Structure(pdb)
                for chain in pdbf.peptide_chains:
                  if chain.chain_id =='': chain_id = '_'
                  else: chain_id = chain.chain_id
                  # GET THE CORRECT CHAIN
                  if chain_id == chaid:
                    # BUILD THE SEQUENCE
                    xsequence = ''
                    for residue in chain:
                      xsequence+=nmcl_aminoacid(residue.name)[0]
                    # STORE THE SEQUENCE
                    refdbn[bmrbid]['sequence']=xsequence
                # COMPARE SHIFTS IF WE HAVE HIT
                if sequence==xsequence and bmrbid in match:
                  cnt += 1
                  print hit, bhits[hit], cnt, refdbn[bmrbid]['pdb'], \
                        refdbn[bmrbid]['method']
                  # THE STRUCTURE FOR WHICH DATA EXISTS
                  pdb1 = nmv_adjust(nmvconf['PDB'],refdbn[bmrbid]['pdb'].lower())
                  # THE TEST STRUCTURE
                  pdb2 = ens
                  pdb3 = nmv_adjust(nmvconf['PDB'],projectname)
                  # GET SHIFTS FOR REF DB STRUCTURE
                  shft = shiftx(nmvconf['SHIFTX_RUN'])
                  shft.predict(pdb1,refdbn[bmrbid]['chain'])
                  lpred = shft.nuclei['N']
                  lmeas = []
                  for res in refdb[bmrbid]:
                    lmeas.append(refdb[bmrbid][res][0])
                  if len(lmeas)==len(lpred):
                    lpred = [el for el in lpred if lmeas[lpred.index(el)]!='?']
                    lmeas = [float(el) for el in lmeas if el !='?']
                  if len(lmeas) == len(lpred):
                    print list_cc(lmeas,lpred)
                  else: print "Lists differ!"
                  # GET SHIFTS FOR PDB NMR STRUCTURE
                  shft = shiftx(nmvconf['SHIFTX_RUN'])
                  shft.predict(pdb3)
                  lpred = shft.nuclei['N']
                  lmeas = []
                  for res in refdb[bmrbid]:
                    lmeas.append(refdb[bmrbid][res][0])
                  if len(lmeas) == len(lpred):
                    lpred = [el for el in lpred if lmeas[lpred.index(el)]!='?']
                    lmeas = [float(el) for el in lmeas if el !='?']
                  if len(lmeas) == len(lpred):
                    cc = list_cc(lmeas,lpred)
                    print cc
                    origcc.append(cc)
                  else: print "Lists differ!"
                  # GET SHIFTS FOR DRESS
                  shft = shiftx(nmvconf['SHIFTX_RUN'])
                  shft.predict(pdb2)
                  lpred = shft.nuclei['N']
                  lmeas = []
                  for res in refdb[bmrbid]:
                    lmeas.append(refdb[bmrbid][res][0])
                  if len(lmeas) == len(lpred):
                    lpred = [el for el in lpred if lmeas[lpred.index(el)]!='?']
                    lmeas = [float(el) for el in lmeas if el !='?']
                  if len(lmeas) == len(lpred):
                    cc = list_cc(lmeas,lpred)
                    print cc
                    refcc.append(cc)
                  else: print "Lists differ!"
  print avg_list(origcc)
  print avg_list(refcc)




#  ===========================================================================
#   S U B S C R I P T   6 9 :  C O R R E L A T E   U N C - S T R U C T U R E
#  ===========================================================================
#
def nmv_uncvsmodelquality(projectpath,dataset,outputpath):
  nmvconf["Q_PROJECT"]=projectpath
  print "Correlating local backbone uncertainty with structural properties."
  skiplist = []
  # BUILD LIST OF SUITABLE PROJECTS
  projectdirs = glob.glob(os.path.join(projectpath,'*'))
  projects = {}
  for projectdir in projectdirs:
    id = os.path.basename(projectdir)
    # CHECK IF PDB FILES ARE PRESENT
    id_ensemble = os.path.join(projectdir,'pdb/%s_ensemble.pdb'%id)
    if os.path.exists(id_ensemble) and id not in skiplist:
      projects[id] = {}
      projects[id]['ensemble'] = id_ensemble
  print "Found %i projects suitable for analysis."%len(projects)
  # CREATE QUALITY INFORMATION FOR ALL ENSEMBLES
  for id in projects:
    id_quafile = "%s.qua2"%projects[id]['ensemble'][:-4]
    # CHECK IF QUALITY EXISTS, OTHERWISE BUILD IT
    if not os.path.exists(id_quafile):
      pdb_getqua(projects[id]['ensemble'],id_quafile,type='ascii')
    projects[id]['quafile'] = id_quafile
  # DICTIONARY FOR AVERAGES CC'S
  ccs={}
  # EXTRACT INFORMATION SCORES
  for id in projects:
    print "* %s *"%id
    # SETUP QUEEN
    queen = qn_setup(nmvconf,id)
    xplr  = qn_setupxplor(nmvconf,id)
    # CORRELATE LOCAL INF TO PDBFILE
    ipr = qn_uncperresidue(queen,xplr,dataset)
    # WRITE OUTPUT FILE
    outputfile = os.path.join(outputpath,'I_res_%s.dat'%id)
    xmgr = graceplot(outputfile,'xy','w')
    xmgr.xlab = "Residue Number"
    xmgr.ylab = "Local BB information content"
    xmgr.writeheader()
    for chain in ipr:
      residues = ipr[chain].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        xmgr.write([residue.number,ipr[chain][residue]])
      xmgr.newset()
    xmgr.close()
    # READ QUALITY FILE
    print "Reading quality information."
    pdbfinder = pdb_finder(projects[id]['quafile'],'r',1,error)
    pdbfinder.read()
    # THE CHECKS WE LOOK AT
    #checks = [' Access','  Packing-1','  Packing-2',
    #          '  Phi/psi', '  Backbone','  Bumps',
    checks = ['  Chi-1/chi-2']
    checkd = {}
    for chain in ipr:
      checkd[chain] = {}
      for check in checks:
        quastr =  pdbfinder.fieldvalue(check)
        checkd[chain][check]=checkd[chain].get(check,[])
        qualist = quastr.split('|')[0]
        # ADD ALL TO LIST, SET ? TO -1
        for ch in qualist:
          if ch!='?':
            # INT PDBFII
            #checkd[chain][check].append(int(ch))
            # ASCI PDBFII
            checkd[chain][check].append(ord(ch))
          else:
            checkd[chain][check].append(-1)
    # CORRELATE CHECK AGAINST INFO
    print "Correlating quality with restraint information."
    for chain in ipr:
      print "Chain: '%s'"%chain
      # BUILD LIST OF INF VALUES
      inf = []
      residues = ipr[chain].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        inf.append(ipr[chain][residue])
      for check in checks:
        # STRIP CHECK NAME
        checkn = check.strip()
        checkn = checkn.replace('/','-')
        # CALCULATE CORRELATION COEFFICIENT
        chelist = [el for el in checkd[chain][check] if el!=-1]
        inflist = []
        for i in range(len(inf)):
          if checkd[chain][check][i]!=-1: inflist.append(inf[i])
        # WRITE CORRELATION PLOT
        file = os.path.join(outputpath,'cc_HstructureR_vs_%s_%s.dat'%(checkn,
                                                                      id))
        xmgr = graceplot(file,'xy','w')
        xmgr.square = 1
        xmgr.xlab = 'H\sstructure|R\N per residue'
        xmgr.ylab = 'Normalized quality score - %s.'%checkn
        xmgr.writeheader()
        for i in range(len(inflist)):
          xmgr.write([inflist[i],chelist[i],i])
        xmgr.close()
        # CALCULATE CORRELATION COEFFICIENT
        if len(inflist)!=len(chelist): warning("List lengths differ!")
        cc = list_cc(inflist,chelist)
        if cc!=None :
          print "%11s: %6.2f"%(check,cc)
          # WRITE TO SUMMARY FILE
          file = os.path.join(outputpath,'sum_cc_HstructureR_vs_%s.dat'%checkn)
          # CREATE HEADER
          if not os.path.exists(file):
            xmgr=graceplot(file,'xy','w')
            xmgr.xlab = 'PDB entry'
            xmgr.ylab = 'Correlation coefficient'
            xmgr.title = 'Correlation H\sstructure|R\N vs %s'%checkn
            xmgr.writeheader()
            xmgr.close()
          # ADD DATAPOINTS
          else:
            xmgr=graceplot(file,'xy','a')
            xmgr.write([projects.keys().index(id),cc,id])
            xmgr.close()
          # STORE IN DICTIONARY
          ccs[checkn]=ccs.get(checkn,[])+[cc]
        else:
          warning('list_cc zerodivision')
  # WRITE SUMMARY
  file = os.path.join(outputpath,'sum_cc_HstructureR_vs_all.dat')
  file = open(file,'w')
  for key in ccs:
    avg = avg_list(ccs[key])
    file.write("%12s: %7.3f +-/ %7.3f\n"%(key,avg[0],avg[1]))
  file.close()


#  ================================================================================
#   S U B S C R I P T   7 0 :  C O R R E L A T E   LOCAL UNC  - S T R U C T U R E
#  ================================================================================
#
def nmv_localuncvsmodelquality(projectpath,dataset,outputpath,cutoff=12):
  print "Correlating local uncertainty with structural properties."
  skiplist = []
  # BUILD LIST OF SUITABLE PROJECTS
  projectdirs = glob.glob(os.path.join(projectpath,'*'))
  projects = {}
  for projectdir in projectdirs:
    id = os.path.basename(projectdir)
    # CHECK IF PDB FILES ARE PRESENT
    id_ensemble = os.path.join(projectdir,'pdb/%s_ensemble.pdb'%id)
    id_qua2 = os.path.join(projectdir,'pdb/%s_ensemble.qua2'%id)
    if os.path.exists(id_qua2) and id not in skiplist:
      projects[id] = {}
      projects[id]['ensemble'] = id_ensemble
  print "Found %i projects suitable for analysis."%len(projects)
  # CREATE QUALITY INFORMATION FOR ALL ENSEMBLES
  for id in projects:
    id_quafile = "%s.qua2"%projects[id]['ensemble'][:-4]
    # CHECK IF QUALITY EXISTS, OTHERWISE BUILD IT
    if not os.path.exists(id_quafile):
      pdb_getqua(projects[id]['ensemble'],id_quafile)
    projects[id]['quafile'] = id_quafile
  # DICTIONARY FOR AVERAGES C
  ccs={}
  # EXTRACT INFORMATION SCORES
  for id in projects:
    print "* %s *"%id
    # SETUP QUEEN
    queen = qn_setup(nmvconf,id)
    xplr  = qn_setupxplor(nmvconf,id)
    # CORRELATE LOCAL UNC TO PDBFILE
    upr = qn_localuncperresidue(queen,xplr,dataset,cutoff=cutoff)
    # WRITE OUTPUT FILE
    outputfile = os.path.join(outputpath,'Lunc_res_%s_%02i.dat'%(id,cutoff))
    xmgr = graceplot(outputfile,'xy','w')
    xmgr.xlab = "Residue Number"
    xmgr.ylab = "Local CA uncertainty (cutoff = %i A)"%cutoff
    xmgr.writeheader()
    for chain in upr:
      residues = upr[chain].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        xmgr.write([residue.number,upr[chain][residue]])
      xmgr.newset()
    xmgr.close()
    # READ QUALITY FILE
    print "Reading quality information."
    pdbfinder = pdb_finder(projects[id]['quafile'],'r',1,error)
    pdbfinder.read()
    # THE CHECKS WE LOOK AT
    checks = [' Access','  Packing-1','  Packing-2','  Phi/psi', '  Backbone','  Bumps']
    checkd = {}
    for chain in upr:
      checkd[chain] = {}
      for check in checks:
        quastr =  pdbfinder.fieldvalue(check)
        checkd[chain][check]=checkd[chain].get(check,[])
        qualist = quastr.split('|')[0]
        # ADD ALL TO LIST, SET ? TO -1
        for ch in qualist:
          # FOR THE 'NUM' PDBFINDER
          #if ch!='?': checkd[chain][check].append(int(ch))
          # FOR THE 'ASCII' PDBFINDER
          if ch!='?': checkd[chain][check].append(ord(ch))
          else: checkd[chain][check].append(-1)
    # CORRELATE CHECK AGAINST INFO
    print "Correlating quality with restraint information."
    for chain in upr:
      print "Chain: '%s'"%chain
      # BUILD LIST OF IUNI
      unc = []
      residues = upr[chain].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        unc.append(upr[chain][residue])
      for check in checks:
        # STRIP CHECK NAME
        checkn = check.strip()
        checkn = checkn.replace('/','-')
        # CALCULATE CORRELATION COEFFICIENT
        chelist = [el for el in checkd[chain][check] if el!=-1]
        inflist = []
        for i in range(len(unc)):
          if checkd[chain][check][i]!=-1: inflist.append(unc[i])
        # WRITE CORRELATION PLOT
        file = os.path.join(outputpath,'cc_Lunc_vs_%s_%s_%02i.dat'%(checkn,
                                                                    id,
                                                                    cutoff))
        xmgr = graceplot(file,'xy','w')
        xmgr.square = 1
        xmgr.xlab = 'Local uncertainty per residue (%)'
        xmgr.ylab = 'Normalized quality score - %s.'%checkn
        xmgr.writeheader()
        for i in range(len(inflist)):
          xmgr.write([inflist[i],chelist[i],i])
        xmgr.close()
        # WRITE SEPARATE PLOTS
        file = os.path.join(outputpath,'%s_%s_%02i.dat'%(checkn,id,cutoff))
        xmgr = graceplot(file,'xy','w')
        xmgr.writeheader()
        for i in range(len(chelist)): xmgr.write([i,chelist[i]])
        xmgr.newset()
        for i in range(len(inflist)): xmgr.write([i,inflist[i]])
        xmgr.close()
        # CALCULATE CORRELATION COEFFICIENT
        if len(inflist)!=len(chelist): warning("List lengths differ!")
        cc = list_cc(inflist,chelist)
        if cc!=None :
          print "%11s: %6.2f"%(check,cc)
          # WRITE TO SUMMARY FILE
          file = os.path.join(outputpath,'sum_cc_Lunc_vs_%s_%02i.dat'%(checkn,
                                                                       cutoff))
          # CREATE HEADER
          if not os.path.exists(file):
            xmgr=graceplot(file,'xy','w')
            xmgr.xlab = 'PDB entry'
            xmgr.ylab = 'Correlation coefficient'
            xmgr.title = 'Correlation Lunc vs %s'%checkn
            xmgr.writeheader()
            xmgr.close()
          # ADD DATAPOINTS
          else:
            xmgr=graceplot(file,'xy','a')
            xmgr.write([projects.keys().index(id),cc,id])
            xmgr.close()
          # STORE IN DICTIONARY
          ccs[checkn]=ccs.get(checkn,[])+[cc]
        else:
          warning('list_cc zerodivision')
  # WRITE SUMMARY
  file = os.path.join(outputpath,'sum_cc_Lunc_vs_all_%02i.dat'%cutoff)
  file = open(file,'w')
  for key in ccs:
    avg = avg_list(ccs[key])
    file.write("%12s: %7.3f +-/ %7.3f\n"%(key,avg[0],avg[1]))
  file.close()

#  ===========================================================================
#   S U B S C R I P T   7 1 :  D R E S S   V S   S H I F T X
#  ===========================================================================
#
def nmv_dressvsshiftx(projectpath,dataset,shiftxpath):
  # THE OUTPUTPATH
  outputpath = os.path.join(shiftxpath,'output')
  print "Reading entry names from RefDB."
  refdbn = {}
  # BUILD A DICTIONARY OF REFDB SEQUENCES
  refdblist = os.path.join(shiftxpath,'bmrpdb.html')
  content = open(refdblist,'r').readlines()
  for line in content:
    # TRY TO FIND BMRB KEY
    if line.find('bmrb.wisc.edu') != -1:
      pos1 = line.find('>bmr')
      pos2 = line.find('.str<')
      id = int(line[pos1+4:pos2])
      refdbn[id] = {}
    # FIND PDB ID
    elif line.find('www.rcsb.org') != -1:
      pos1 = line.find('?pdbId')
      pos2 = line.find('(')
      pos3 = line.find(')')
      # GET PDB ID AND SEQ ID AND METHOD
      pdbid = line[pos1+13:pos1+17]
      chaid = line[pos1+17]
      method = line[pos2+1:pos3]
      refdbn[id]['pdb']=pdbid
      refdbn[id]['chain']=chaid
      refdbn[id]['method']=method
  print "Read %i BMRD IDs."%(len(refdbn.keys()))
  # READ CHEMICAL SHIFTS FROM REFDB-N
  print "Reading chemical shifts from RefDB-N in SHIFTY format."
  refdbN = os.path.join(shiftxpath,'RefDB-N.db')
  content = open(refdbN,'r').readlines()
  refdb = {}
  refnucs = {}
  # INITIALIZE PROGRESS BAR
  prog = progress_indicator(len(content))
  cnt = 1
  id = None
  for line in content:
    line = line.split()
    # INCREMENT BAR
    prog.increment(cnt)
    cnt += 1
    # GET ID
    if len(line)>1 and line[0] == '#DBBANK':
      # IF WE GO TO NEW ID, STORE THE OLD SEQUENCE
      if id: refdb[id]['sequence']=sequence
      id = int(line[2])
      refdb[id]={}
      refnucs[id]={}
      sequence = ''
    # GET SHIFTS
    if len(line)>1 and line[0][0] not in ['>','#']:
      resnum = int(line[0])
      sequence += line[1]
      shifts = []
      spos,lpos = 3,3
      for el in line[spos:]:
        index = line.index(el,lpos)
        # WE NEED TO KEEP TRACK OF THE LAST POSITION FOR INDEXING
        lpos += 1
        if el == '****':
          shifts.append('?')
          if   index == 3: refnucs[id]['N']=refnucs[id].get('N',[])+['?']
          elif index == 4: refnucs[id]['H']=refnucs[id].get('H',[])+['?']
        else:
          shifts.append(float(el))
          if   index == 3: refnucs[id]['N']=refnucs[id].get('N',[])+[float(el)]
          elif index == 4: refnucs[id]['H']=refnucs[id].get('H',[])+[float(el)]
      # STORE THE SHIFTS FOR EACH RESIDUE
      refdb[id][resnum]=shifts
  print "Read %i chemical shift entries."%(len(refdb.keys()))

  match = [el for el in refdb.keys() if el in refdbn.keys()]
  print "Found %i good pairs."%(len(match))
  # READ AND CHECK DRESS ENTRIES
  print "Reading and checking DRESS entries."
  dirlist = glob.glob(os.path.join(projectpath,'*'))
  dirlist = [el for el in dirlist if os.path.basename(el)[:5]!='dress']
  pairs = {}
  # CREATE PROGRESS BAR
  prog = progress_indicator(len(dirlist))
  for dir in dirlist:
    prog.increment(dirlist.index(dir)+1)
    # GET PROJECTNAME
    projectname = os.path.basename(dir)
    # GET THE ENSEMBLES
    ens_ori = os.path.join(dir,'%s_original.pdb'%projectname)
    ens_ref = os.path.join(dir,'%s_refined.pdb'%projectname)
    # BUILD SEQUENCES FOR ENSEMBLE
    pdbf = pdb_file.Structure(ens_ori)
    for chain in pdbf.peptide_chains:
      # ADJUST CHAIN ID
      if chain.segment_id == '': chainid = '_'
      else: chainid = chain.segment_id
      # CONSTRUCT SEQUENCE STRING
      sequence = ''
      for residue in chain: sequence+=nmcl_aminoacid(residue.name)[0]
      # BLAST SEQUENCE AGAINST REFDB
      refdbf = os.path.join(shiftxpath,'refdb.fasta')
      # DO THE BLAST
      bhits = seq_blastrefdb(nmvconf["BLAST_RUN"],
                             sequence,
                             refdbf)
      # CYCLE THE HITS
      hits = [hit for hit in bhits if bhits[hit]==100]
      for hit in hits:
        # GET BMRB ID
        bmrbid = int(hit[3:hit.find('.')])
        # STORE PDBID AND CHAINID
        if bmrbid in refdbn.keys() and bmrbid in match:
          rdb_pdbid = refdbn[bmrbid]['pdb']
          rdb_chaid = refdbn[bmrbid]['chain']
          # GET REFDB SEQUENCE
          rdb_pdb = nmv_adjust(nmvconf["PDB"],rdb_pdbid.lower())
          # DO WE HAVE HIT? IF SO, STORE IT
##          print bmrbid, rdb_pdbid
##          print sequence
##          print refdb[bmrbid]['sequence']
          seqmatch = 0
          s1,s2 = '',''
          if len(sequence) == len(refdb[bmrbid]['sequence']):
            for i in range(len(sequence)):
              if refdb[bmrbid]['sequence'][i]!='*':
                s1 += sequence[i]
                s2 += refdb[bmrbid]['sequence'][i]
            if s1==s2: seqmatch = 1
##          print seqmatch
          if seqmatch:
            p = projectname
            pairs[p]={}
            pairs[p]['rdb_id']=bmrbid
            pairs[p]['rdb_pdbid']=rdb_pdbid.lower()
            pairs[p]['rdb_chaid']=rdb_chaid
            pairs[p]['rdb_seq']=refdb[bmrbid]['sequence']
            pairs[p]['chaid']=chaid
            pairs[p]['seq']=sequence
            pairs[p]['ens_ori']=ens_ori
            pairs[p]['ens_ref']=ens_ref
  # DO THE CHEMICAL SHIFT PREDICTIONS
  print "Found the following matching pairs."
  for pair in pairs:
    id = pairs[pair]['rdb_id']
    print pair, pairs[pair]['rdb_pdbid'], id, refdbn[id]['method']
  print "Cycling the different pairs."
  nuclist = ['N','H']
  ccd = {}
  for pair in pairs:
    rdb_id = pairs[pair]['rdb_id']
    print "*****"
    print "RefDB entry: %i"%rdb_id
    print "Projectname: %s"%pair
    # CYCLE THE DIFFENT STRUCTURES1
    structures = [pairs[pair]['ens_ori'],pairs[pair]['ens_ref']]
    pred = []
    for i in range(2):
      struct = structures[i]
      # SPLIT THE STRUCTURE INTO TEMPORARY FILES
      tmpdir = dsc_tmpdir(nmvconf["TMP"])
      tmpbase = os.path.join(tmpdir,'tmp')
      pdblist = yas_splitpdb(nmvconf["YASARA_RUN"],
                             struct,
                             tmpbase)
      # CYCLE THE PDBFILES
      pdict = {}
      prog = progress_indicator(len(pdblist))
      for el in pdblist:
        prog.increment(pdblist.index(el)+1)
        # GET SHIFTS FOR REF DB STRUCTURE
        shft = shiftx(nmvconf['SHIFTX_RUN'])
        shft.predict(el)
        for nuc in nuclist:
          pdict[nuc] = pdict.get(nuc,[]) + [shft.nuclei[nuc]]
      # ADD TO DICT
      pred.append(pdict)
      # REMOVE TMPDIR
      dsc_rmdir(tmpdir)
    # BUILD MEASURED LIST
    for nuc in nuclist:
      print "Nucleus: %s"%nuc
      # DICT FOR STORAGE
      ccd[nuc]=ccd.get(nuc,{})
      # MEASURED LIST
      lmeas = refnucs[rdb_id][nuc]
      # PREDICTED LIST
      cclist = []
      # WRITE PLOT
      for i in range(2):
        ccs = []
        for el in pred[i][nuc]:
          lpred = el
          # CLEAR RESIDUES WITHOUT CS DATA (? IN LMEAS)
          cpred, cmeas = [],[]
          if len(lpred)==len(lmeas):
            for i in range(len(lpred)):
              if lmeas[i]!='?':
                cpred.append(lpred[i])
                cmeas.append(lmeas[i])
            ccs.append(list_cc(cpred,cmeas))
        if len(lpred)==len(lmeas):
          cclist.append(ccs)
      # PRINT
      if len(cclist)==2:
        avg = avg_list(cclist[0])
        ccd[nuc]['id'] = ccd[nuc].get('id',[])+[pair]
        ccd[nuc]['original'] = ccd[nuc].get('original',[])+[avg]
        print "  Original: %7.3f +/- %7.3f"%(avg[0],avg[1])
        avg = avg_list(cclist[1])
        ccd[nuc]['refined'] = ccd[nuc].get('refined',[])+[avg]
        print "   Refined: %7.3f +/- %7.3f"%(avg[0],avg[1])
      else:
        print "   Mismatch between measured and predicted."
        print len(lpred), len(lmeas)
  # MAKE A PLOT
  for nuc in nuclist:
    ppath = os.path.join(outputpath,'cc_sum_%s.dat'%nuc)
    xmgr = graceplot(ppath,'xydy','w')
    xmgr.xlab = "Structure index"
    xmgr.ylab = "Correlation Coefficient"
    xmgr.writeheader()
    for el in ['original','refined']:
      plist = ccd[nuc][el]
      for i in range(len(plist)):
        xmgr.write([i,plist[i][0],plist[i][1],ccd[nuc]['id'][i]])
      xmgr.newset()
    xmgr.close()


#  ===========================================================================
#   S U B S C R I P T   7 2 :  R E F I N E   P R O J E C T
#  ===========================================================================
#
def nmv_refineproject(projectname,dataset):
  p = projectname
  # SETUP QUEEN
  queen = qn_setup(nmvconf,p)
  xplr  = qn_setupxplor(nmvconf,p)
  # COPY THE INPUT PDB FILE
  pdb = os.path.join(queen.pdb,"%s.pdb"%p)
  # SPLIT THE PDB FILE
  originals = yas_splitpdb2xplor(nmvconf["YASARA_RUN"],
                                 pdb,queen.pdb,'original',rebuildh=0)
  # READ DATA
  data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
  # COMBINE ALL DATA, WE ALSO CHECK THE BACKGROUND INFORMATION!
  restraints = data["data"] + data["bckg"]
##  # REBUILD THE HYDROGENS
##  print "Rebuilding hydrogens."
##  pdblist_ori = glob.glob(os.path.join(queen.pdb,'original*.pdb'))
##  # CYCLE THE ORIGINAL AND MAKE A DUPLICATE
##  clist = []
##  for el in pdblist_ori:
##    newname = "%s.ori"%el[:-4]
##    if not os.path.exists(newname):
##      os.rename(el,newname)
##      clist.append(newname)
##  # DO THE RE-BUILDING
##  for pdb in clist:
##    outpdb = "%s.pdb"%pdb[:-4]
##    if not os.path.exists(outpdb):
##      print "%s\r"%pdb,
##      sys.stdout.flush()
##      xplor_hbuild(pdb,outpdb,xplr.psf)
##  print "\nDone."
  # DO THE VIOLATION ANALYSIS ON THE INPUT
  outputfile = os.path.join(queen.outputpath,'viol_%s_%s_original.txt'%(p,dataset))
  # CUTOFFS FOR VIOLATION ANALYSIS
  dslist = [el*0.1 for el in range(0,11,1)]
  dhlist = [el for el in range(0,31,5)]
  cutoff={"DIST":dslist,"DIHE":dhlist}
  if not os.path.exists(outputfile):
    xplor_violanalysis(originals,xplr.psf,
                       restraints,outputfile,cutoff)
  # DO THE REFINEMENT
  refined = []
  for pdb in originals:
    print "Refining %s."%pdb
    n = originals.index(pdb)+1
    outpdb = os.path.join(queen.pdb,'refined_%s_%03i.pdb'%(dataset,n))
    if not os.path.exists(outpdb):
      xplor_refstruct(pdb,outpdb,xplr.psf,restraints,
                      thr_noe=0.5,thr_dih=10)
    refined.append(outpdb)
  # DO THE VIOLATION ANALYSIS ON THE REFINED STRUCTURES
  outputfile = os.path.join(queen.outputpath,'viol_%s_%s_refined.txt'%(p,dataset))
  if not os.path.exists(outputfile):
    xplor_violanalysis(refined,xplr.psf,restraints,outputfile,cutoff)
  # CREATE ENSEMBLES
  ens_ori = os.path.join(queen.pdb,'ens_original.pdb')
  if not os.path.exists(ens_ori):
    yas_joinpdb(nmvconf["YASARA_RUN"],
                originals,ens_ori)
  ens_ref = os.path.join(queen.pdb,'ens_%s_refined.pdb'%dataset)
  if not os.path.exists(ens_ref):
    yas_joinpdb(nmvconf["YASARA_RUN"],
                refined,ens_ref)
  # CREATE QUALITY FILES
  for el in [ens_ori,ens_ref]:
    qua = os.path.join(queen.outputpath,
                       os.path.basename("%s.qua"%el[:-4]))
    if not os.path.exists(qua):
      pdb_getqua(el,qua)


#  ===========================================================================
#   S U B S C R I P T   7 5 :  S E L E C T   E N S E M B L E
#  ===========================================================================
#
def nmv_selectensemble(projectname,dataset,criterion,nstructures):
  if criterion not in ['rms','energy']:
    error("%s is an invalid selection criterion."%criterion)
  print "Building structural ensemble of size %i,"%nstructures
  print "using %s as selection criterion."%criterion
  # INITIALIZE QUEEN AND XPLOR
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # THE VARIOUS PARAMETERS
  parameters = ['ener.total','ener.noe','ener.cdih','rms.noe','rms.cdih']
  parscaling = [ 0.01       , 0.1      , 10.       , 100.     , 10.      ]
  # BUILD LIST OF REFINED STRUCTURES
  pdbfiles = glob.glob(os.path.join(queen.pdb,'refined_*.pdb'))
  print "Found %03i structures."%len(pdbfiles)
  pdb = {}
  # CYCLE STRUCTURES AND READ HEADER
  for file in pdbfiles:
    # CREATE DICT ENTRY
    id = file
    pdb[id] = {}
    # READ FILE
    content = open(file,'r')
    remark = 1
    while remark:
      # READ LINE
      line = content.readline()
      if line[:6] != 'REMARK': remark = 0
      line = line.split()
      # RETRIEVE INFO
      for par in ['ener.total','ener.noe','ener.cdih','rms.noe','rms.cdih']:
        for el in line:
          if el.find(par) != -1:
            # STORE INFO
            val = float(el.split('=')[1])
            pdb[id][par]=val
  # SORT STRUCTURES
  if criterion == 'rms': par = 'rms.noe'
  elif criterion == 'energy': par = 'ener.total'
  sorted = pdb.items()
  sorted.sort(lambda (k1,v1),(k2,v2): cmp(v2[par],v1[par]))
  sorted.reverse()
  # WRITE OVERVIEW PLOT
  plot = os.path.join(queen.outputpath,'selectens_%s_%s.dat'%(dataset,criterion))
  print "Writing overview file to:\n%s"%plot
  xmgr = graceplot(plot,'xy','w')
  xmgr.xlab = "Structure index"
  xmgr.ylab = "Criterion"
  xmgr.writeheader()
  for i in range(len(parameters)):
    par = parameters[i]
    sca = parscaling[i]
    for j in range(len(sorted)):
      val = sorted[j]
      xmgr.write([j,val[1][par]*sca,val[0]])
    xmgr.newset()
  xmgr.close()
  # JOIN ENSEMBLE
  outputpdb = os.path.join(queen.outputpath,'ensemble_%s_%s_%i.pdb'%(dataset,
                                                                     criterion,
                                                                     nstructures))
  print "Writing ensemble to:\n%s"%outputpdb
  towrite = []
  for i in range(nstructures):
    towrite.append(sorted[i][0])
  print towrite
  yas_joinpdb(nmvconf["YASARA_RUN"],
              towrite,
              outputpdb)
  print "Done."

#  ===========================================================================
#   S U B S C R I P T   7 5 :  S T R U C T U R A L   G E N O M I C S
#  ===========================================================================
#
def nmv_analyzestructuralgenomics():
  # SET PARAMETERS
  path = '/projects/structuralgenomics/'
  xmlf = os.path.join(path,'targets.xml')
  # THE CHECKS
  checks = ['Packing2','PhiPsi','Chi1Chi2','Backbone']
  # SKIPLIST
  skiplist = ['1xmo','1pjd','1pje','1pjf','1rwd','1rws','1sf0','1zn5','1k0p','1x2l']
  # DUMP DICTIONARY
  dict = os.path.join(path,'labd.dic')
  if os.path.exists(dict):
    print "Found pickled target dictionary!"
    file = open(dict,"r")
    labd = cPickle.load(file)
    file.close()
  else:
    print "Not found pickled target dictionary!"
    print "Reading target.xml...."
    # READ PDBFINDER2 FOR DATES
    pdbfinder = pdb_finder(nmvconf["PDBFINDER2"],'r',1,error)
    pdbfinder.buildindex()
    # READ THE INPUT XML FILE
    parser = Xml2Obj()
    targets = parser.Parse(xmlf)
    print "Found %i possible targets."%len(targets.children)
    pdbcount,labd = 0,{}
    # CYCLE THE TARGET LIST
    for target in targets.children:
      lab = target.getElements('lab')[0].getData()
      if lab == 'SPINE-EU: Regensberg': lab = 'SPINE-EU'
      elif lab == 'SPINE-EU: Magnetic Resonance Center (CERM) Florence':
        lab = 'SPINE-EU'
      elif lab == 'Northeast Structural Genomics Consortium':
        lab = 'NESGC'
      pdbid = None
      nmr,xray = 0,0
      # CHECK THE STATUS IF A STRUCTURE IS FINISHED
      for stat in target.getElements('status'):
        if stat.cdata == 'NMR Structure':
          nmr = 1
        elif stat.cdata == 'Crystal Structure':
          xray = 1
      # WE HAVE AN NMR STRUCTURE !
      if nmr:
        for dbref in target.getElements('databaseRef'):
          for dbname in dbref.getElements('databaseName'):
            if dbname.getData() == "PDB":
              pdbid = dbref.getElements('databaseId')[0].getData()
              pdbf  = nmv_adjust(nmvconf["PDB"],pdbid.lower())
              # READ PDBFINDER2
              print pdbf
              if os.path.exists(pdbf) and pdbid.lower() not in skiplist:
                pdbfinder.read(pdbid)
                date   = pdbfinder.fieldvalue(' Date')
                if date: year = int(date[:4])
                else: year = 0
                if year >= 2003 and len(pdbfinder.sequence[0])>45:
                  labd[lab]=labd.get(lab,{})
                  labd[lab]['pdbid']=labd[lab].get('pdbid',[])
                  labd[lab]['pdbid'].append(pdbid.lower())
                  pdbcount += 1
    print "Of those %i targets are in the PDB!"%pdbcount
    # DUMP THE DICTIONARY
    file = open(dict,'w')
    cPickle.dump(labd,file)
    file.close()
  print "Distribution over the consortia:"
  # SORT ON CONSORTIUM
  elems = labd.items()
  elems.sort(lambda (k1,v1),(k2,v2): cmp(len(v2['pdbid']),len(v1['pdbid'])))
  for elem in elems:
    if len(elem[1]['pdbid'])>0:
      print "%03i - %s"%(len(elem[1]['pdbid']),elem[0])
  print "Press Enter to continue."
  x = raw_input()
  # ANALYZE CONSORTIA
  print "Validating structure ensembles."
  dict = os.path.join(path,'validation.dic')
  vald = {}
  if os.path.exists(dict):
    print "Found pickled validation dictionary!"
    file = open(dict,"r")
    vald = cPickle.load(file)
    file.close()
  # DO THE ANALYSIS
  lablist = []
  maxstruct = 1000
  for lab in labd:
    print lab
    # ONLY LABS WITH MORE THEN 0 ENTRIES
    if len(labd[lab]['pdbid']) >= 0:
      lablist.append(lab)
      for pdb in labd[lab]['pdbid'][:maxstruct]:
        pdbf = nmv_adjust(nmvconf["PDB"],pdb.lower())
        # CHECK IF VALIDATION NEEDS TO BE PERFORMED
        if not pdb in vald.keys():
          # PERFORM THE CHECKS
          checkd = pdb_check_global(pdbf,checks)
          # STORE THE CHECKS
          vald[pdb] = checkd
          # AND PICKLE THE MAIN DICT
          file = open(dict,'w')
          cPickle.dump(vald,file)
          file.close()
  # CREATE TIE FIGHTER PLOTS
  for check in checks:
    outputpath = os.path.join(path,'output')
    outputfile = os.path.join(outputpath,"ovw_%s.dat"%(check.strip()))
    xmgr = graceplot(outputfile,'xy','w')
    xmgr.xlab = "Structural Genomics Center"
    xmgr.ylab = "%s"%check
    xmgr.writeheader()
    cnt = 1
    # STORAGE LISTS
    l_perc1090, l_perc2575 = [],[]
    l_avg, l_outliers      = [],[]
    # CYCLE THE LABS
    for lab in lablist:
      # STORE ALL SCORES IN A LIST
      scorelist = []
      # CYCLE THE PDBFILE
      for pdb in labd[lab]['pdbid'][:maxstruct]:
        scorelist.extend(vald[pdb][check])
      # BUILD THE TIE FIGHTER DICTIONARY
      tie = avg_list_tiefighter(scorelist)
      # STORE PERCENTILES
      l_perc1090.append([cnt,tie[50],tie[90]-tie[50],tie[50]-tie[10]])
      l_perc2575.append([cnt,tie[50],tie[75]-tie[50],tie[50]-tie[25]])
      # STORE OUTLIERS
      for el in tie['outliers']:
        l_outliers.append([cnt,el])
      # STORE AVERAGE
      l_avg.append([cnt,tie['avg'],tie['sd'],
                    "%s-%03i"%(lab,len(labd[lab]['pdbid']))])
      cnt += 1
    # WRITE GRACE OUTPUT
    xmgr.mwrite(l_outliers)
    xmgr.type = 'xydydy'
    xmgr.newset()
    xmgr.mwrite(l_perc1090)
    xmgr.newset()
    xmgr.mwrite(l_perc2575)
    xmgr.type = 'xydy'
    xmgr.newset()
    xmgr.mwrite(l_avg)
    # CLOSE FILE
    xmgr.close()
  # CREATE OVERAL TIE FIGHTER PLOT
  outputpath = os.path.join(path,'output')
  outputfile = os.path.join(outputpath,"ovw_overall.dat")
  xmgr = graceplot(outputfile,'xy','w')
  xmgr.xlab = "Quality indicator"
  xmgr.ylab = "Z-score"
  xmgr.writeheader()
  # STORAGE LISTS
  l_perc1090, l_perc2575 = [],[]
  l_avg, l_outliers      = [],[]
  l_1tgq = [[0.85,-2.0760],
            [1.85,-6.6025],
            [2.85 -5.7835],
            [3.85,-5.3530]]
  # STORE ALL SCORES IN A LIST
  cnt = 0.85
  checkcnt = 0
  for check in checks:
    print check
    # CYCLE THE LABS
    scorelist = []
    for lab in lablist:
      # CYCLE THE PDBFILE
      for pdb in labd[lab]['pdbid'][:maxstruct]:
        avg = avg_list(vald[pdb][check],sdflag=0)
        scorelist.append(avg)
        checkcnt += 1./len(checks)
        if avg < -10 or avg > 2:
          print pdb, check, avg
#        if pdb == '1tgq':
#          print "################"
#          l_1tgq.append([cnt,avg_list(vald[pdb][check],sdflag=0)])
    # BUILD THE TIE FIGHTER DICTIONARY
    tie = avg_list_tiefighter(scorelist)
    # STORE PERCENTILES
    l_perc1090.append([cnt,tie[50],tie[90]-tie[50],tie[50]-tie[10]])
    l_perc2575.append([cnt,tie[50],tie[75]-tie[50],tie[50]-tie[25]])
    # STORE OUTLIERS
    for el in tie['outliers']:
      l_outliers.append([cnt,el])
    # STORE AVERAGE
    l_avg.append([cnt,tie['avg'],tie['sd'],check])
    cnt += 1
  print "Checked %03i structural genomics structures."%checkcnt
  # WRITE GRACE OUTPUT
  xmgr.mwrite(l_outliers)
  xmgr.type = 'xydydy'
  xmgr.newset()
  xmgr.mwrite(l_perc1090)
  xmgr.newset()
  xmgr.mwrite(l_perc2575)
  xmgr.type = 'xydy'
  xmgr.newset()
  xmgr.mwrite(l_avg)
  xmgr.type = 'xy'
  xmgr.newset()
  xmgr.mwrite(l_1tgq)
  # CLOSE FILE
  xmgr.close()

#  ===========================================================================
#   S U B S C R I P T   7 5 A :  S T R U C T U R A L   G E N O M I C S
#  ===========================================================================
#
def nmv_analyzenonstructuralgenomics():
  # SET PARAMETERS
  path = '/projects/nonstructuralgenomics/'
  maxstruct = 417
  xmlf = os.path.join(path,'targets.xml')
  # THE CHECKS
  checks = ['Packing2','PhiPsi','Chi1Chi2','Backbone']
  # SKIPLIST
  skiplist = ['1xmo','1pjd','1pje','1pjf','1rwd','1rws','1sf0','1zn5','1k0p']
  # DUMP DICTIONARY FROM analyzestructuralgenomics()
  sgdict = os.path.join(path,'labd.dic')
  if os.path.exists(sgdict):
    print "Found pickled SG  dictionary!"
    file = open(sgdict,"r")
    sgd = cPickle.load(file)
    file.close()
  else:
    error( "Please run analyzestructuralgenomics() first!" )
  # BUILD LIST OF SG NMR STRUCTURES SINCE 2003
  sglist = []
  for key in sgd:
    sglist.extend(sgd[key]['pdbid'])
  # DUMP DICTIONARY WITH TRADITIONAL NMR STRUCTURES
  nmrdict = os.path.join(path,'nmr.dic')
  if os.path.exists(nmrdict):
    print "Found picked NMR dictionay!"
    file = open(nmrdict,"r")
    regd = cPickle.load(file)
    file.close()
  else:
    cnt = 0
    regd = {}
    # READ PDBFINDER2
    pdbfinder = pdb_finder(nmvconf["PDBFINDER2"],'r',1,error)
    pdbfinder.buildindex()
    pdbfinder.read()
    while not pdbfinder.eof:
      # GET DATE
      date   = pdbfinder.fieldvalue(' Date')
      if date: year = int(date[:4])
      else: year = 0
      # SET SG FLAG
      sg = 0
      if pdbfinder.id.lower() in sglist:
        sg = 1
        cnt += 1
      if year >= 2003 and sg == 0 and pdbfinder.id.lower() not in skiplist:
        # ONLY PROTEINS
        if pdbfinder.peptidechains > 0 and pdbfinder.nucleotidechains == 0 and len(pdbfinder.sequence[0])>45:
          # NO HET GROUPS
          if pdbfinder.fieldvalue("HET-Groups")==None:
            # GET METHOD
            method = pdbfinder.fieldvalue('Exp-Method')
            if method == 'NMR':
              id = pdbfinder.id.lower()
              regd[method]=regd.get(method,[]) + [id]
      pdbfinder.read()
    # DUMP THE DICTIONARY
    file = open(nmrdict,'w')
    cPickle.dump(regd,file)
    file.close()
  # LIST OF REGULAR NMR PDB FILES
  reglist = regd["NMR"]
  shuffle(reglist)
  print "Found %i NMR structures."%len(reglist)
  # ANALYZE CONSORTIA
  print "Validating structure ensembles."
  dict = os.path.join(path,'validation.dic')
  vald = {}
  if os.path.exists(dict):
    print "Found pickled validation dictionary!"
    file = open(dict,"r")
    vald = cPickle.load(file)
    file.close()
  # DO THE ANALYSIS
  for pdb in reglist[:maxstruct]:
    pdbf = nmv_adjust(nmvconf["PDB"],pdb.lower())
    # CHECK IF VALIDATION NEEDS TO BE PERFORMED
    if not pdb in vald.keys():
      # PERFORM THE CHECKS
      checkd = pdb_check_global(pdbf,checks)
      # STORE THE CHECKS
      vald[pdb] = checkd
      # AND PICKLE THE MAIN DICT
      file = open(dict,'w')
      cPickle.dump(vald,file)
      file.close()
##  # CREATE TIE FIGHTER PLOTS
##  for check in checks:
##    outputpath = os.path.join(path,'output')

##    outputfile = os.path.join(outputpath,"ovw_%s.dat"%(check.strip()))
##    xmgr = graceplot(outputfile,'xy','w')
##    xmgr.xlab = "Structural Genomics Center"
##    xmgr.ylab = "%s"%check
##    xmgr.writeheader()
##    cnt = 1
##    # STORAGE LISTS
##    l_perc1090, l_perc2575 = [],[]
##    l_avg, l_outliers      = [],[]
##    # CYCLE THE LABS
##    for lab in lablist:
##      # STORE ALL SCORES IN A LIST
##      scorelist = []
##      # CYCLE THE PDBFILE
##      for pdb in labd[lab]['pdbid'][:maxstruct]:
##        scorelist.extend(vald[pdb][check])
##      # BUILD THE TIE FIGHTER DICTIONARY
##      tie = avg_list_tiefighter(scorelist)
##      # STORE PERCENTILES
##      l_perc1090.append([cnt,tie[50],tie[90]-tie[50],tie[50]-tie[10]])
##      l_perc2575.append([cnt,tie[50],tie[75]-tie[50],tie[50]-tie[25]])
##      # STORE OUTLIERS
##      for el in tie['outliers']:
##        l_outliers.append([cnt,el])
##      # STORE AVERAGE
##      l_avg.append([cnt,tie['avg'],tie['sd'],
##                    "%s-%03i"%(lab,len(labd[lab]['pdbid']))])
##      cnt += 1
##    # WRITE GRACE OUTPUT
##    xmgr.mwrite(l_outliers)
##    xmgr.type = 'xydydy'
##    xmgr.newset()
##    xmgr.mwrite(l_perc1090)
##    xmgr.newset()
##    xmgr.mwrite(l_perc2575)
##    xmgr.type = 'xydy'
##    xmgr.newset()
##    xmgr.mwrite(l_avg)
##    # CLOSE FILE
##    xmgr.close()
  # CREATE OVERAL TIE FIGHTER PLOT
  outputpath = os.path.join(path,'output')
  outputfile = os.path.join(outputpath,"ovw_overall.dat")
  xmgr = graceplot(outputfile,'xy','w')
  xmgr.xlab = "Quality indicator"
  xmgr.ylab = "Z-score"
  xmgr.writeheader()
  # STORAGE LISTS
  l_perc1090, l_perc2575 = [],[]
  l_avg, l_outliers      = [],[]
  l_1tgq = []
  # STORE ALL SCORES IN A LIST
  cnt = 1.15
  for check in checks:
    print check
    # CYCLE THE LABS
    scorelist = []
    # CYCLE THE PDBFILE
    for pdb in reglist[:maxstruct]:
      avg = avg_list(vald[pdb][check],sdflag=0)
      scorelist.append(avg)
      if avg < -10 or avg > 2:
        print pdb, check, avg
    # BUILD THE TIE FIGHTER DICTIONARY
    tie = avg_list_tiefighter(scorelist)
    # STORE PERCENTILES
    l_perc1090.append([cnt,tie[50],tie[90]-tie[50],tie[50]-tie[10]])
    l_perc2575.append([cnt,tie[50],tie[75]-tie[50],tie[50]-tie[25]])
    # STORE OUTLIERS
    for el in tie['outliers']:
      l_outliers.append([cnt,el])
    # STORE AVERAGE
    l_avg.append([cnt,tie['avg'],tie['sd'],check])
    cnt += 1
  # WRITE GRACE OUTPUT
  xmgr.mwrite(l_outliers)
  xmgr.type = 'xydydy'
  xmgr.newset()
  xmgr.mwrite(l_perc1090)
  xmgr.newset()
  xmgr.mwrite(l_perc2575)
  xmgr.type = 'xydy'
  xmgr.newset()
  xmgr.mwrite(l_avg)
  xmgr.type = 'xy'
  xmgr.newset()
  xmgr.mwrite(l_1tgq)
  # CLOSE FILE
  xmgr.close()

#  ===========================================================================
#   S U B S C R I P T   7 5 :  A N A L Y Z E   I N F O   V S   Q U A L I T Y
#  ===========================================================================
#
def nmv_infovsquality(projectname='3gb1',dataset='noe',
                      adjustdata=True,reference='/pdb/pdb1pgb.ent'):
  # OVERWRITE Q_PROJECT
  nmvconf["Q_PROJECT"]='/storage/projects/datavsqual'
  # SET PARAMETERS
  if projectname == '3gb1':
    precision   = 0.5
    checks      = ['  Phi/psi','  Backbone']
    subsets     = [100.,95.,90.,85.,80.,75.,70.,65.,60.]
    subsets     = [100.,90.,80.,70.]
    nsets       = 5
    nstructures = 20
  elif projectname == '1d3z':
    precision   = 1.5
    checks      = ['  Phi/psi','  Backbone']
    subsets     = [100.,95.,90.,85.,80.,75.,70.,65.,60.]
    subsets     = [100.,90.,80.,70.]
    nsets       = 5
    nstructures = 20
  else:
    checks      = ['  Phi/psi','  Backbone']
    subsets     = [100.,90.,80.,70.]
    nsets       = 5
    nstructures = 20
  # INITIALIZE QUEEN AND XPLOR
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # SET FILENAME BASE
  if adjustdata: fnbase = '%s_%03.2f'%(dataset,precision)
  else:          fnbase = '%s'%(dataset)
  # THE OUTPUT RESTRAINT FILE
  tblpath = os.path.join(queen.outputpath,"%s.tbl"%fnbase)
  print tblpath
  # READ THE RESTRAINTS
  data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
  restraints = data["data"]+data["bckg"]
  # WRITE TO OUTFILE, IF ADJUSTMENT IS NOT NEEDED
  if not adjustdata:
    r = restraint_file(tblpath,'w',format="XPLOR")
    r.mwrite(restraints)
    r.close()
  # READ PDB FILE
  print "Reading reference PDB file."
  pdbx = os.path.join(queen.pdb,"reference.pdb")
  if not os.path.exists(pdbx):
    yas_pdb2xplor(nmvconf["YASARA_RUN"],reference,pdbx)
    xplor_pdbmatchsegi(pdbx,xplr.template)
    tmp = pdbx+'tmp'
    os.rename(pdbx,tmp)
    xplor_hbuild(tmp,pdbx,xplr.psf)
    os.remove(tmp)
  # CREATE QUALITY FILE
  xqua = os.path.join(queen.pdb,"%s.qua"%projectname)
  if not os.path.exists(xqua):
    pdb_getqua(pdbx,xqua,type='ascii')
  # READ QUALITY FILE
  pdbfinder = pdb_finder(xqua,'r',1,error)
  pdbfinder.read()
  xquad = {}
  for check in checks:
    quastr = pdbfinder.fieldvalue(check)
    qualist = []
    for ch in quastr:
      if ch!='?': qualist.append(ord(ch))
      else: qualist.append(-1)
      # STORE LIST
      xquad[check]=qualist
  # READING PDBFINDER2 INFO
  print "Reading PDBFINDER II."
  pdbfinder = pdb_finder(nmvconf["PDBFINDER2"],'r',1,error)
  pdbfinder.buildindex()
  pdbfinder.read(projectname)
  pdbsecstr = pdbfinder.secstr[0]
  seq = pdbfinder.sequence[0]
  # A SMALL HACK FOR 1OZI
  if projectname=='1ozi':
    pdbsecstr = 'CCCCCCCC'+pdbsecstr
    seq       = 'MHHHHHHM'+seq
  pdb  = pdb_file.Structure(pdbx)
  # CHECK IF RESTRAINT FILE EXISTS
  if os.path.exists(tblpath):
    print "Reading adjusted restraints."
    # READ FILE
    r = restraint_file(tblpath,'r',format="XPLOR")
    r.read()
    r.close()
    r_adjusted = r.restraintlist
  else:
    print "Adjusting restraints based on structure."
    # ADJUST THE RESTRAINTS
    r_adjusted = r_adjust(restraints,pdb,precision=precision)
    # WRITE RESTRAINT
    r = restraint_file(tblpath,'w',format="XPLOR")
    r.mwrite(r_adjusted)
    r.close()
  # GENERATE LESS OPTIMAL SETS
  for subset in subsets:
    completed = 1
    # CHECK IF WORK IS DONE...
    for i in range(nsets):
      outtbl = nmv_adjust(queen.table,"%s_%05.1f_%i"%(fnbase,subset,i+1))
      if not os.path.exists(outtbl): completed = 0
    if not completed:
      # CREATE SUBSETS FROM FULL LIST
      datasets = qn_generatedataset(queen,xplr,r_adjusted,
                                    subset,maxerr=1,nsets=nsets)
      cnt = 1
      for dataset in datasets:
        # WRITE AN OUTPUT FILE
        outtbl = nmv_adjust(queen.table,"%s_%05.1f_%i"%(fnbase,subset,cnt))
        rfile = restraint_file(outtbl,'w')
        rlist = dataset['restraints']
        rfile.mwrite(rlist)
        rfile.close()
        cnt += 1
  # CALCULATE STRUCTURE FOR THE SETS
  for subset in subsets:
    print "Subset %3i of %3i."%(subsets.index(subset)+1,len(subsets))
    for i in range(nsets):
      print "Set    %3i of %3i."%(i+1,nsets)
      pdbbase = "%s_%05.1f_%i"%(fnbase,subset,i+1)
      # READ RESTRAINTS
      print "Reading restraints."
      intbl = nmv_adjust(queen.table,"%s_%05.1f_%i"%(fnbase,subset,i+1))
      r = restraint_file(intbl,'r')
      r.read()
      # CHECK IF WE HAVE ANY STRUCTURES
      pdblist = glob.glob(os.path.join(queen.pdb,"%s_a*"%pdbbase))
      if len(pdblist)<nstructures:
        print "Calculating structures."
        # CREATE MTF
        mtf = os.path.join(queen.pdb,'%s.mtf'%projectname)
        if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
        # CALCULATE THE STRUCTURES
        cns_calcstructure(os.path.join(queen.pdb,pdbbase),
                          xplr.template,
                          mtf,
                          r.restraintlist,
                          naccepted=nstructures)
      # LIST CALCULATED STRUCTURES
      pdblist = glob.glob(os.path.join(queen.pdb,"%s_a*"%pdbbase))
      # DO THE VIOLATION ANALYSIS ON THE STRUCTURES
      outputfile = os.path.join(queen.outputpath,'viol_%s.txt'%pdbbase)
      dslist = [el*0.1 for el in range(1,10)]
      cutoff={"DIST":dslist}
      if not os.path.exists(outputfile):
        xplor_violanalysis(pdblist,xplr.psf,
                           r.restraintlist,outputfile,cutoff)
      # REFINE THE GENERATED STRUCTURES
      reflist = []
      print "Refining structures."
      for pdb in pdblist:
        prefix = os.path.dirname(pdb)
        fname  = os.path.basename(pdb)
        refpdb = os.path.join(prefix,"ref_%s"%fname)
        reflist.append(refpdb)
        if not os.path.exists(refpdb):
          xplor_refstruct(pdb,refpdb,xplr.psf,r.restraintlist,seed=54321,
                          mdheat=10,mdhot=100,mdcool=10)
      # CHECK VIOLATIONS IN REFINED
      outputfile = os.path.join(queen.outputpath,'viol_ref_%s.txt'%pdbbase)
      if not os.path.exists(outputfile):
        xplor_violanalysis(reflist,xplr.psf,
                           r.restraintlist,outputfile,cutoff)
      # GENERATE QUALITY FILES
      for structure in reflist:
        quaf = "%s.qua"%os.path.basename(structure)[:-4]
        quafile = os.path.join(queen.outputpath,quaf)
        if not os.path.exists(quafile):
          pdb_getqua(structure,quafile,type='ascii')
      # CREATE CUSTOM RAMACHANDRAN PLOT FILES
      quafile = os.path.join(queen.outputpath,pdbbase)
      if not os.path.exists(quafile+'_PhiPsi.dat'):
        pdb_plotchecks(reflist,
                       'PhiPsi',
                       quafile)
  # BUILD DICTIONARY WITH STRUCTURAL AND QUALITY INFO
  print "Building data dictionary."
  d = {}
  # BUILD H0 PER RESIDUE
  ipr = qn_uncperresidue(queen,xplr,[])
  d["H0"] = []
  for c in ipr:
    residues = ipr[c].keys()
    residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
    for i in range(len(residues)): d["H0"].append(ipr[c][residues[i]])
  # BUILD HR PER RESIDUE
  ipr = qn_uncperresidue(queen,xplr,r_adjusted)
  d["HR"] = []
  for c in ipr:
    residues = ipr[c].keys()
    residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
    for i in range(len(residues)): d["HR"].append(ipr[c][residues[i]])
  # CYCLE THE SUBSETS
  for s in subsets:
    d[s]=d.get(s,{})
    for n in range(1,nsets+1):
      d[s][n]=d[s].get(n,{})
      # READ DATA BELONGING TO THE SET
      tab = "%s_%05.1f_%i"%(fnbase,s,n)
      tbl = nmv_adjust(queen.table,tab)
      r = restraint_file(tbl,'r')
      r.read()
      # CALCULATE THE PERC OF INFO PER RESIDUE
      ipr = qn_uncperresidue(queen,xplr,r.restraintlist)
      Ir = []
      for c in ipr:
        residues = ipr[c].keys()
        residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
        for i in range(len(residues)):
          res = residues[i]
          Ir.append(100*((d["H0"][i]-ipr[c][res])/(d["H0"][i]-d["HR"][i])))
      # STORE THE INFO
      d[s][n]["Iset"] = Ir
      for i in range(1,nstructures+1):
        d[s][n][i]=d[s][n].get(i,{})
        # READING QUALITY FILES
        quaf = "ref_%s_%05.1f_%i_a_%i.qua"%(fnbase,s,n,i)
        quafile = os.path.join(queen.outputpath,quaf)
        # EXTRACT QUALITY INFO
        pdbfinder = pdb_finder(quafile,'r',1,error)
        pdbfinder.read()
        #seq = pdbfinder.fieldvalue("Sequence")[:len(residues)]
        for check in checks:
          # GET QUALITY STRING
          quastr = pdbfinder.fieldvalue(check)
          quastr = quastr[:len(residues)]
          # CONVERT TO SCORES
          qualist = []
          cnt = 1
          for ch in quastr:
            if ch!='?':
              qualist.append(ord(ch))
            else:
              if cnt!=1 and cnt!=len(quastr):
                print '!!',cnt, len(quastr)
                print quaf
              qualist.append(-1)
            cnt += 1
          # STORE LIST
          d[s][n][i][check]=qualist
          if qualist[2]==-1:
            print quaf
      # READ THE CUSTOM PHIPSI SCORES
      file = os.path.join(queen.outputpath,tab+'_PhiPsi.dat')
      print file
      xmgr = graceplot(file,'xydy','r')
      xmgr.read()
      d[s][n]['PhiPsi'] = [-1]+[val[1] for val in xmgr.data]+[-1]
  # CALCULATE CORRELATIONS
  print "Calculating correlations..."
  checks = checks + ['PhiPsi']
  for check in checks:
    print check
    # STRIP CHECK NAME
    checkn = check.strip()
    checkn = checkn.replace('/','-')
    # CREATE OUTPUT PATH
    checkdir = os.path.join(queen.outputpath,"%s_%s"%(fnbase,checkn))
    if os.path.exists(checkdir): dsc_rmdir(checkdir)
    os.mkdir(checkdir)
    # SUMMARY FILE FOR ALL CORRELATIONS (MAYBE DO SLOPES HERE?)
    out2 = os.path.join(checkdir,"cc_%s_%s.dat"%(fnbase,checkn))
    xmgr2 = graceplot(out2,'xy','w')
    xmgr2.writeheader()
    out3 = os.path.join(checkdir,"all_%s_%s.dat"%(fnbase,checkn))
    xmgr3 = graceplot(out3,'xydxdy','w')
    xmgr3.writeheader()
    out4 = os.path.join(checkdir,"sl_%s_%s.dat"%(fnbase,checkn))
    xmgr4 = graceplot(out4,'xy','w')
    xmgr4.writeheader()
    out5 = os.path.join(checkdir,"xf_%s_%s.dat"%(fnbase,checkn))
    xmgr5 = graceplot(out5,'xy','w')
    xmgr5.writeheader()
    out6 = os.path.join(checkdir,"pl_%s_%s.dat"%(fnbase,checkn))
    xmgr6 = graceplot(out6,'xydy','w')
    xmgr6.square = 1
    xmgr6.writeheader()
    xmgr3final = []
    # CYCLE THE RESIDUES
    tmpstr = ''
    for el in residues:
      tmpstr += nmcl_aminoacid(el.name)[0]
    for i in range(len(residues)):
      rnum = residues[i].number
      # MAKE VECTORS
      iv,qv = [],[]
      isum,qsum = [],[]
      for s in subsets:
        isumt,qsumt = [],[]
        for n in range(1,nsets+1):
          # STORE INFO
          iv.append(d[s][n]["Iset"][i])
          # STORE INFO FOR AVERAGE
          isumt.append(d[s][n]["Iset"][i])
          # AVERAGE THE QUALITY SCORE
          if check != 'PhiPsi':
            tmp = []
            for q in range(1,nstructures+1):
              tmp.append(d[s][n][q][check][i])
            if -1 not in tmp:
              qavg = avg_list(tmp)
              qv.append(qavg)
              qsumt.append(qavg[0])
            # ADD -1 IF QUALITY IS NOT DETERMINED
            else:
              #if rnum!=1 and rnum!=len(residues):
              #  print check, s, n , q, i, rnum, len(residues)
              #  print d[s][n][q][check]
              qv.append(-1)
          else:
            tmp = d[s][n]['PhiPsi'][i]
            if tmp != -1:
              qv.append([tmp,0.])
              qsumt.append(tmp)
            else:
              qv.append(-1)
        # STORE AVERAGES PER SUBSET
        isum.append(avg_list(isumt))
        qsum.append(avg_list(qsumt))
      #print len(isum), isum
      #print len(qsum), qsum
      # CORRELATE ONLY VALID LISTS...
      if -1 not in iv and -1 not in qv:
        # CORRELATE VECTORS
        ccqv = [el[0] for el in qv]
        cc = list_cc(iv,ccqv)
        [ic,slope] = list_slope(iv,ccqv)
        # CALCULATE FIT FOR AVERAGES
        l1 = [el[0] for el in isum]
        l2 = [el[0] for el in qsum]
        cc2 = list_cc(l1,l2)
        # WRITE VALID CC AND GENERATE LABEL FOR PLOT
        if cc!=None:
          xmgr2.write([rnum,abs(cc2)])
          xmgr4.write([rnum,slope])
          xmgr5.write([rnum,abs(cc2)*slope*100])
          xmgr6.write([abs(cc2)*slope*100,qsum[0][0],qsum[0][1],rnum])
          lab = '%03i/%03i'%(int(100*abs(cc)),int(100*abs(cc2)))
        else: lab = 'NaN/NaN'
        # WRITE XY PLOT FOR SHOWING THE CORRELATION
        out1 = os.path.join(checkdir,"%s_%03i_%s_%s_%s_%s.dat"%(fnbase,
                                                                rnum,
                                                                seq[i],
                                                                pdbsecstr[i],
                                                                checkn,
                                                                lab.replace('/','-')))
        xmgr1 = graceplot(out1,'xydy','w')
        #xmgr1.square = 1
        #xmgr1.title = "res: %03i - cc: %s - ss: %s"%(rnum,lab,pdbsecstr[i])
        #xmgr1.xlab = "Information content (%)"
        #xmgr1.ylab = "Ramachandran plot quality score"
        xmgr1.writeheader()
        # WRITE DATAPOINTS
        for c in range(len(iv)):
          xmgr1.write([iv[c],qv[c][0],qv[c][1]])
        xmgr1.type = 'xy'
        xmgr1.newset()
        xmgr3.type = 'xy'
        xmgr3.newset()
        # WRITE FIT
        for c in range(-5,106,10):
          xmgr1.write([c,ic+c*slope])
          xmgr3.write([c,ic+c*slope])
        xmgr1.type = 'xydxdy'
        xmgr1.newset()
        # WRITE THE AVERAGES
        for c in range(len(isum)):
          xmgr1.write([isum[c][0],qsum[c][0],isum[c][1],qsum[c][1]])
          xmgr3final.append([isum[c][0],qsum[c][0],isum[c][1],qsum[c][1]])
        if check != 'PhiPsi':
          # WRITE THE XRAY VALUE
          xmgr1.type = 'xy'
          xmgr1.newset()
          xmgr1.write([100.0,xquad[check][i]])
        xmgr1.close()
        # WRITE POSTSCRIPT OUTPUT
        xmgr1.output(parameter=os.path.join(queen.outputpath,'%s.par'%checkn))
    # CLOSE OUTPUT
    xmgr2.close()
    xmgr3.type = 'xydxdy'
    xmgr3.newset()
    for el in xmgr3final:
      xmgr3.write(el)
    xmgr3.close()
  print "Done."


#  ===========================================================================
#   S U B S C R I P T   7 6 : A N A L Y Z E   C O N C O O R D
#  ===========================================================================
#
def nmv_analyzeconcoord(projectname='3gb1',dataset='distancedata'):
  maxstruct = 100
  # FOR THE WATERREFINEMENTS
  heatsteps = 200
  hotsteps  = 2000
  coolsteps = 200
  # OVERRIDE QUEEN SETUP
  nmvconf["Q_PROJECT"] = nmvconf["CNC_PROJECT_TEST"]
  # INITIALIZE QUEEN AND XPLOR
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # READ DISTANCE DATA
  data  = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
  restraints = data["data"]
  # STORE UNCERTAINTY IN A LIST AND CREATE A PLOT
  ulist = []
  plotname = os.path.join(queen.outputpath,'unc.dat')
  if not os.path.exists(plotname):
    # DETERMINE UNCERTAINTY PER RESIDUE
    upr = qn_uncperresidue(queen,xplr,dataset)
    xmgr = graceplot(plotname,'xy','w')
    xmgr.xlab = "Residue number"
    xmgr.ylab = "Uncertainty (bits/atom\S2\N)"
    xmgr.writeheader()
    for c in upr.keys():
      residues = upr[c].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        val = upr[c][residue]
        ulist.append(val)
        xmgr.write([residue.number,val])
    xmgr.close()
  else:
    xmgr = graceplot(plotname,'xy','r')
    xmgr.read()
    for el in xmgr.data:
      ulist.append(el[1])
  # CHECK IF CONCOORD STRUCTURES ARE PRESENT
  cnclist = glob.glob(os.path.join(queen.pdb,'*concoord*.pdb'))
  # CHECK IF WE ARE IN THE RIGHT NOMENCLATURE ...
  tmplist = []
  if len(cnclist)!=0:
    # RENAME CNC STRUCTURES
    print "Renaming CONCOORD structures."
    for el in cnclist:
      newname = os.path.join(queen.pdb,"cnc_%03i.pdb"%(cnclist.index(el)+1))
      os.rename(el,newname)
      tmplist.append(newname)
    # COPY NEW LIST OF CONCOORD NAMES
    cnclist = tmplist
  else:
    cnclist = glob.glob(os.path.join(queen.pdb,'cnc_*.pdb'))
  # DO A SHORT EM AND A WATER REFINEMENT OF THE CONCOORD STRUCTURES
  cnclist.sort()
  cnclist = cnclist[:maxstruct]
  print "Found %03i CONCOORD structures."%len(cnclist)
  print "Performing EM and refinement of CONCOORD structures."
  # DO THE REFINEMENTS
  prog = progress_indicator(len(cnclist))
  for i in range(len(cnclist)):
    prog.increment(i+1)
    # MATCH SEGID
    xplor_pdbmatchsegi(cnclist[i],xplr.template)
    # THE EM
    inpdb  = cnclist[i]
    outpdb = os.path.join(queen.pdb,"cnce_%03i.pdb"%(i+1))
    if not os.path.exists(outpdb):
      #print "EM:"
      #print inpdb
      #print outpdb
      xplor_emstruct(inpdb,
                     outpdb,
                     xplr.psf,
                     restraints,
                     thr_noe=0.4)
    # THE WATER REFINEMENT
    outpdb = os.path.join(queen.pdb,"cncu_%03i.pdb"%(i+1))
    if not os.path.exists(outpdb):
      #print "WR:"
      #print inpdb
      #print outpdb
      xplor_refstruct(inpdb,
                      outpdb,
                      xplr.psf,
                      restraints,
                      thr_noe=0.4,
                      mdheat=heatsteps,
                      mdhot=hotsteps,
                      mdcool=coolsteps)
  # CHECK IF CNS STRUCTURES ARE PRESENT
  cnslist = glob.glob(os.path.join(queen.pdb,'cns_*.pdb'))
  if len(cnslist)==0:
    cnslist = []
    # CALCULATE 100 CNS STRUCTURES
    mtf = "%s.mtf"%xplr.psf[:-4]
    if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
    pdbbase = os.path.join(queen.pdb,'cnstmp')
    cns_calcstructure(pdbbase,
                      xplr.template,
                      mtf,
                      restraints,
                      thr_noe=0.4,
                      naccepted=maxstruct)
    # RENAME THEM INTO OUR FORMAT
    pdblist = glob.glob("%s_*.pdb"%pdbbase)
    for i in range(len(pdblist)):
      newname = os.path.join(queen.pdb,'cns_%03i.pdb'%(i+1))
      os.rename(pdblist[i],
                newname)
      cnslist.append(newname)
  # DO A REFINEMENT OF THE CNS STRUCTURES
  cnslist.sort()
  cnslist = cnslist[:maxstruct]
  print "Found %03i CNS structures."%len(cnslist)
  print "Performing refinement of CNS strutures."
  prog = progress_indicator(len(cnslist))
  for i in range(len(cnslist)):
    prog.increment(i+1)
    inpdb  = cnslist[i]
    outpdb = os.path.join(queen.pdb,"cnsu_%03i.pdb"%(i+1))
    if not os.path.exists(outpdb):
      #print "WR:"
      #print inpdb
      #print outpdb
      xplor_refstruct(inpdb,
                      outpdb,
                      xplr.psf,
                      restraints,
                      thr_noe=0.4,
                      mdheat=heatsteps,
                      mdhot=hotsteps,
                      mdcool=coolsteps)
  # CHECK IF XPL STRUCTURES ARE PRESENT
  xpllist = glob.glob(os.path.join(queen.pdb,'xpl_*.pdb'))
  if len(xpllist)!=maxstruct:
    # CALCULATE 100 XPL STRUCTURES
    pdbbase = os.path.join(queen.pdb,'xpl')
    xpllist = xplornih_anneal(pdbbase,
                              xplr.template,
                              xplr.psf,
                              restraints,
                              thr_noe=0.4,
                              naccepted=maxstruct,
                              ntrial=50)
  # DO A REFINEMENT OF THE XPL STRUCTURES
  xpllist.sort()
  xpllist = xpllist[:maxstruct]
  print "Found %03i XPL structures."%len(xpllist)
  print "Performing refinement of XPL strutures."
  prog = progress_indicator(len(xpllist))
  for i in range(len(xpllist)):
    prog.increment(i+1)
    inpdb  = xpllist[i]
    outpdb = os.path.join(queen.pdb,"xplu_%03i.pdb"%(i+1))
    if not os.path.exists(outpdb):
      #print "WR:"
      #print inpdb
      #print outpdb
      xplor_refstruct(inpdb,
                      outpdb,
                      xplr.psf,
                      restraints,
                      thr_noe=0.4,
                      mdheat=heatsteps,
                      mdhot=hotsteps,
                      mdcool=coolsteps)
  # MATCH SEQID FOR VDW TRIAL
  for setname in ['cnsvdw','dshvdw','yam','yamber',
                  'yamber_vdwtol','yamber_plan','oplsaa',
                  'yamber_plan2','5_yam','5_yam_tightgeom','5_yam_vdwopt']:
    pdblist = glob.glob(os.path.join(queen.pdb,'%s_*.pdb'%setname))
    for pdb in pdblist:
      xplor_pdbmatchsegi(pdb,xplr.template)
    # DO A REFINEMENT OF THE STRUCTURES
    pdblist.sort()
    pdblist = pdblist[:maxstruct]
    print "Found %03i %s structures."%(len(pdblist),setname.upper())
    print "Performing refinement of %s strutures."%setname.upper()
    prog = progress_indicator(len(pdblist)*2)
    cnt = 1
    for i in range(len(pdblist)):
      prog.increment(cnt)
      cnt += 1
      inpdb  = pdblist[i]
      # WATER REFINEMENT
      outpdb = os.path.join(queen.pdb,"%sw_%03i.pdb"%(setname,i+1))
      if not os.path.exists(outpdb):
        xplor_refstruct(inpdb,
                        outpdb,
                        xplr.psf,
                        restraints,
                        thr_noe=0.4,
                        mdheat=heatsteps,
                        mdhot=hotsteps,
                        mdcool=coolsteps)
      # EM
      prog.increment(cnt)
      cnt += 1
      outpdb = os.path.join(queen.pdb,"%se_%03i.pdb"%(setname,i+1))
      if not os.path.exists(outpdb):
        xplor_emstruct(inpdb,
                       outpdb,
                       xplr.psf,
                       restraints,
                       thr_noe=0.4)
  # CYCLE THE DIFFERENT SETS
  if projectname == '3gb1':
    setlist = ['cnc','cncw','cnsw','cns','cnce','xpl','xplw',
               'cnsvdw','dshvdw','cnsvdwe','dshvdwe','cnsvdww','dshvdww',
               'yam','yame','yamw','yambere','yamberw','yamber_vdwtole',
               'yamber_vdwtolw','yamber_plane','yamber_planw','oplsaa',
               'oplsaae','oplsaaw','yamber_plan2e','yamber_plan2w',
               '5_yam','5_yame','5_yamw','5_yam_tightgeom','5_yam_tightgeome',
               '5_yam_tightgeomw','5_yam_vdwopt','5_yam_vdwopte','5_yam_vdwoptw']
  elif projectname == '1d3z':
    setlist = ['cnc','cncw','cnsw','cns','cnce','xpl','xplw',
               'yambere','yamberw','yamber_vdwtole','yamber_vdwtolw',
               'yamber_plan2e','yamber_plan2w',
               '5_yam','5_yame','5_yamw','5_yam_tightgeom','5_yam_tightgeome',
               '5_yam_tightgeomw','5_yam_vdwopt','5_yam_vdwopte','5_yam_vdwoptw']
  elif projectname == '1q2n':
    setlist = ['yambere','yamberw','yamber_plan2e','yamber_plan2w',
               'cns','cnsw','xpl','xplw']
  else:
    setlist = []
  for setname in setlist:
    print "Analyzing %s structures."%setname
    print "############################"
    pdblist = glob.glob(os.path.join(queen.pdb,'%s_*.pdb'%setname))
    pdblist = pdblist[:maxstruct]
    # DO A VIOLATION ANALYSIS
    plotname = os.path.join(queen.outputpath,'%s_viol.txt'%setname)
    if not os.path.exists(plotname):
      xplor_violanalysis(pdblist,xplr.psf,restraints,plotname,
                         {"DIST":[0.5,0.4,0.3,0.2,0.1],
                          "DIHE":[5.0,4.0,3.0,2.0,1.0]})
    # CALCULATE RDC R-FACTOR
    if projectname == '3gb1':
      rdcsets = ['dipo_bicelle_hn',
                 'dipo_tabacco_hn']
    elif projectname == '1d3z' :
      rdcsets = ['dipo_bicelle_1_hn',
                 'dipo_bicelle_2_hn']
    elif projectname == '2ezx':
      rdcsets = ['dipo']
    elif projectname == '1q2n':
      rdcsets = ['dipo']
    else: rdcsets = []
    plotname = os.path.join(queen.outputpath,'%s_rfac.txt'%setname)
    if not os.path.exists(plotname):
      # DETERMINE AVERAG RFACTOR
      rdcd = {}
      for rdcset in rdcsets:
        print "Calculating RDC R-factors for set: %s."%rdcset
        rdcdata = qn_readdata(queen,nmv_adjust(queen.dataset,rdcset))
        rdcrestraints = rdcdata['data']
        rlist = []
        prog = progress_indicator(len(pdblist))
        for el in pdblist:
          prog.increment(pdblist.index(el)+1)
          r = xplor_qfactor(el,xplr.psf,rdcrestraints)
          rlist.append(r)
        avg = avg_list(rlist)
        rdcd[rdcset]=avg
      # WRITE R-FACTORS TO OUTPUT FILE
      outf = open(plotname,'w')
      for rdcset in rdcsets:
        outf.write("%20s : %5.2f +/- %5.2f\n"%(rdcset,
                                               100*rdcd[rdcset][0],
                                               100*rdcd[rdcset][1]))
      outf.close()
    # DETERMINE RAMACHANDRAN PLOT Z-SCORE AND NUMBER OF BUMPS
    rplotname = os.path.join(queen.outputpath,'%s_rama.txt'%setname)
    bplotname = os.path.join(queen.outputpath,'%s_bump.txt'%setname)
    if not os.path.exists(bplotname) or not os.path.exists(rplotname):
      ramaz,bumps = [],[]
      for el in pdblist:
        z = pdb_getramazscore(nmvconf['WHATIF_RUN'],el)
        ramaz.append(z)
        b100 = pdb_getnobumpsper100(nmvconf["WHATIF_RUN"],el)
        bumps.append(b100)
      avg = avg_list(ramaz)
      # WRITE RAMA TO FILE
      outf = open(rplotname,'w')
      str = "Ramachandran Z-score  : %5.2f +/- %5.2f"%(avg[0],avg[1])
      outf.write("%s\n"%str)
      outf.close()
      print str
      # WRITE BUMPS TO FILE
      avg = avg_list(bumps)
      outf = open(bplotname,'w')
      str = "Number bumps per 100  : %5.2f +/- %5.2f"%(avg[0],avg[1])
      outf.write("%s\n"%str)
      outf.close()
      print str
    # SUPERIMPOSE THE STRUCTURES USING PROFIT
    print "Superimposing %03i structures using ProFit."%len(pdblist)
    fitlist = glob.glob(os.path.join(queen.pdb,'%s_*.fit'%setname))
    if len(fitlist)!=len(pdblist):
      fitlist = prft_superimpose(pdblist,overwrite=0)
    # DETERMINE RMSD MTX OF STRUCTURES
    plotname = os.path.join(queen.outputpath,'%s_rmsd.txt'%setname)
    print plotname
    if not os.path.exists(plotname):
      print plotname
      # METHOD 1
      rmsdmtx = yas_rmsdmtxfast(nmvconf["YASARA_RUN"],fitlist,['CA','N','C'],
                                unit='Obj',fitflag=0)
      rmsdlist = []
      for i in range(len(pdblist)):
        #for el in rmsdmtx[i]:
        #  print "%5.2f"%el,
        #print
        del rmsdmtx[i][i]
        rmsdlist.append(avg_list(rmsdmtx[i],sdflag=0))
      avg = avg_list(rmsdlist)
      # WRITE RMSDS TO FILE
      outf = open(plotname,'w')
      str = "Pairwise backbone RMSD: %5.2f +/- %5.2f"%(avg[0],avg[1])
      outf.write("%s\n"%str)
      outf.close()
      print str
    # DETERMINE NUMBER OF RESIDUES
    pdbf = pdb_file.Structure(pdblist[0])
    nres = 0
    for chain in pdbf.peptide_chains: nres += len(chain)
    # DETERMINE THE PER RESIDUE RMSD SCORES
    plotname = os.path.join(queen.outputpath,'%s_rmsd_bb.dat'%setname)
    bbrmsd = []
    if not os.path.exists(plotname):
      # METHOD 1
      # CALCULATE RMSD SCORES
      plotlist = []
      # BUILD LIST OF RESIDUE NUMBERS
      residues = []
      for residue in range(1,nres+1): residues.append(residue)
      # CALCULATE LIST OF RMSD MATRICES
      rmsdmtxlist = yas_rmsdmtxfast(nmvconf["YASARA_RUN"],fitlist,['CA','N','C'],
                                    unit='Res',fitflag=0)
      # CYCLE THE RESIDUES
      for r in residues:
        rmsdmtx = rmsdmtxlist[residues.index(r)]
        rmsdlist = []
        for i in range(len(pdblist)):
          del rmsdmtx[i][i]
          rmsdlist.append(avg_list(rmsdmtx[i],sdflag=0))
        avg = avg_list(rmsdlist)
        bbrmsd.append(avg[0])
        print "Pairwise RMSD residue %03i: %5.2f +/- %5.2f"%(r,avg[0],avg[1])
        plotlist.append([r,avg[0],avg[1]])
##      # METHOD 2
##      plotlist = []
##      bbrmsds = yas_ensemblermsd(nmvconf['YASARA_RUN'],fitlist,'bb')
##      for q in range(len(bbrmsds)):
##        plotlist.append([q+1,bbrmsds[q]])
##        bbrmsd.append(bbrmsds[q])
      # WRITE PLOT
      xmgr = graceplot(plotname,'xy','w')
      xmgr.xlab = "Residue number"
      xmgr.ylab = "Backbone RMSD (A)"
      xmgr.writeheader()
      xmgr.mwrite(plotlist)
      xmgr.close()
    else:
      xmgr = graceplot(plotname,'xy','r')
      xmgr.read()
      for el in xmgr.data:
        bbrmsd.append(el[1])
    # CORRELATE RMSD WITH UNCERTAINTY
    print "%5s cc RMSD vs UNC: %05.2f"%(setname,list_cc(bbrmsd,ulist)*100)
    # AND WRITE A PLOT
    plotname = os.path.join(queen.outputpath,'%s_rmsd_vs_unc.dat'%setname)
    if not os.path.exists(plotname):
      xmgr = graceplot(plotname,'xy','w')
      xmgr.xlab = "Uncertainty (bits/atom\S2\N)"
      xmgr.ylab = "Backbone RMSD (A)"
      xmgr.writeheader()
      for i in range(len(ulist)):
        xmgr.write([ulist[i],bbrmsd[i]])
      xmgr.close()

#  ===========================================================================
#   S U B S C R I P T   7 6 : V A L I D A T E  C O N C O O R D
#  ===========================================================================
#
def nmv_validateconcoord(projectname='3gb1',dataset='noe'):
  print "Validating CONCOORD calculations for %s."%projectname
  # THE MAXIMUM NUMBER OF STRUCTURES
  # PARAMETERS FOR THE WATER REFINEMENTS
  maxstruct = 100
  heatsteps = 100
  hotsteps  = 1000
  coolsteps = 100
  # THE DIFFERENT PROTOCOLS
  protocols = ['xpl', # XPLOR NIH PROTOCOL
               'cns'] # STANDARD CNS PROTOCOL
  # ADD CONCOORD PROTOCOL
  if projectname in ['3gb1','1d3z']:
    protocols.append('cnc5')
  if projectname in ['1kdf','1r63']:
    protocols.append('cnc6')
  # ADD X-RAY STRUCTURES
  if projectname in ['3gb1','1d3z','1r63','1kdf','1beg']:
    protocols.append('xray')
  if projectname in ['3gb1','1d3z']:
    protocols.append(projectname)
  # ADD FORCEFIELD TESTS
##  if projectname in ['3gb1']:
##    protocols.extend(['142_050','142_055','142_060',
##                      '142_065','142_070'])
##    protocols.extend(['nb2_030','nb2_035','nb2_040',
##                      'nb2_045','nb2_050','nb2_055',
##                      'nb2_060'])
  # A SMALL HACK: WE OVERRIDE QUEEN SETUP
  nmvconf["Q_PROJECT"] = '/storage/projects/concoord/'
  # INITIALIZE QUEEN AND XPLOR
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # SET XRAY STRUCTURE
  if 'xray' in protocols:
    xray = os.path.join(queen.pdb,'xray_001.pdb')
  # READ THE EXPERIMENTAL DATA
  data    = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
  restraints = data["data"]
  # READ COMPLETE SET
  alldata = qn_readdata(queen,nmv_adjust(queen.dataset,'all'))
  allrestraints = alldata["data"]
  # WRITE RESTRAINTS TO CONCOORD FORMAT
  cnctbl = nmv_adjust(queen.table,dataset)[:-3]+'cnc'
  if not os.path.exists(cnctbl):
    cnc_writeconcoord(xplr.psf,xplr.template,restraints,cnctbl)
  # STORE UNCERTAINTY IN A LIST AND CREATE A PLOT
  ulist = []
  plot = os.path.join(queen.outputpath,'qunc_%s.dat'%dataset)
  if not os.path.exists(plot):
    # DETERMINE UNCERTAINTY PER RESIDUE
    upr = qn_uncperresidue(queen,xplr,dataset)
    xmgr = graceplot(plot,'xy','w')
    xmgr.xlab = "Residue number"
    xmgr.ylab = "Uncertainty (bits/atom\S2\N)"
    xmgr.writeheader()
    for c in upr.keys():
      residues = upr[c].keys()
      residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
      for residue in residues:
        val = upr[c][residue]
        ulist.append(val)
        xmgr.write([residue.number,val])
    xmgr.close()
  # IF PLOT EXISTS, WE READ THE UNCERTAINTY VALUES
  else:
    xmgr = graceplot(plot,'xy','r')
    xmgr.read()
    for el in xmgr.data:
      ulist.append(el[1])
  # STRUCTURE GENERATION STEP
  # =========================
  # CYCLE THE DIFFERENT PROTOCOLS
  for protocol in protocols:
    structures = glob.glob(os.path.join(queen.pdb,'%s_*.pdb'%protocol))
    structures.sort()
    structures = structures[:maxstruct]
    # CNS PROTOCOL
    if protocol == 'cns':
      # CALCULATE THE NECESSARY CNS STRUCTURES
      if len(structures) < maxstruct:
        print "Calculating %i CNS structures."%maxstruct
        # GENERATE AN MTF FILE
        mtf = "%s.mtf"%xplr.psf[:-4]
        if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
        # CREATE MAXSTRUCT TEMPORARY STRUCTURES
        pdbbase = os.path.join(queen.pdb,'%s_tmp'%protocol)
        cns_calcstructure(pdbbase,
                          xplr.template,
                          mtf,
                          restraints,
                          naccepted=maxstruct)
        # RENAME TEMPORARY STRUCTURES
        tmplist = glob.glob("%s_a_*.pdb"%pdbbase)
        tmplist.sort()
        for i in range(len(tmplist)):
          newname = os.path.join(queen.pdb,'cns_%03i.pdb'%(i+1))
          os.rename(tmplist[i],
                    newname)
      else:
        print "Found %i CNS structures."%len(structures)
    # XPLOR-NIH PROTOCOL
    elif protocol == 'xpl':
      # CALCULATE THE NECESSARY STRUCTURES
      if len(structures) < maxstruct:
        print "Calculating %i XPL structures."%maxstruct
        # CALCULATE MAXSTRUCT XPL STRUCTURES
        pdbbase = os.path.join(queen.pdb,'xpl')
        xpllist = xplornih_anneal2(pdbbase,
                                   xplr.template,
                                   xplr.psf,
                                   restraints,
                                   naccepted=maxstruct,
                                   ntrial=10)
      else:
        print "Found %i XPL structures."%len(structures)
    # OTHER PROTOCOLS WE SKIP FOR NOW...
    else:
      pass
  # THE REFINEMENT STEP
  # ===================
  # CYCLE THE DIFFERENT PROTOCOLS
  for protocol in protocols:
    structures = glob.glob(os.path.join(queen.pdb,'%s_*.pdb'%protocol))
    structures.sort()
    structures = structures[:maxstruct]
    # DO THE EM AND WATER REFINEMENT
    prog = progress_indicator(len(structures))
    print "Performing water refinement of %s structures."%(protocol.upper())
    for i in range(len(structures)):
      prog.increment(i+1)
      # MATCH SEGID
      xplor_pdbmatchsegi(structures[i],xplr.template)
      if protocol in ['cnc5','cnc6','xray',projectname]:
        # SHUFFLE ATOMS
        xplor_setatoms(structures[i],xplr.psf)
      inpdb  = structures[i]
      if protocol[:2] not in ['14','nb']:
        # THE WATER REFINEMENT
        outpdb = os.path.join(queen.pdb,"%sw_%03i.pdb"%(protocol,i+1))
        if not os.path.exists(outpdb):
          if projectname == '1r63': thr_dih = 15.
          else: thr_dih = 10.
          xplor_refstruct(inpdb,
                          outpdb,
                          xplr.psf,
                          allrestraints,
                          mdheat=heatsteps,
                          mdhot=hotsteps,
                          mdcool=coolsteps,
                          maxtry=10,
                          thr_dih=thr_dih)
  # EXTEND THE LIST OF PROTOCOLS
  nprotocols = []
  for protocol in protocols:
    nprotocols.append(protocol)
    if protocol[:2] not in ['14','nb']:
      nprotocols.append("%sw"%protocol)
  protocols = nprotocols
  # THE VALIDATION STEP
  # ===================
  # CYCLE THE DIFFERENT PROTOCOLS
  for protocol in protocols:
    print "Validating %s structures."%protocol
    structures = glob.glob(os.path.join(queen.pdb,'%s_*.pdb'%protocol))
    structures.sort()
    structures = structures[:maxstruct]
    # DO THE VIOLATION ANALYSIS
    if len(structures)>0:
      plot = os.path.join(queen.outputpath,'%s_violations.txt'%protocol)
    else:
      plot = os.path.join(queen.outputpath,'%s_trial_violations.txt'%protocol)
      structures = glob.glob(os.path.join(queen.pdb,'trial_*.pdb'))
    print "Performing violation analysis of %s structures."%(protocol.upper())
    if not os.path.exists(plot) and len(structures)>0:
      xplor_violanalysis(structures,xplr.psf,restraints,plot,
                         {"DIST":[0.5,0.4,0.3,0.2,0.1],
                          "DIHE":[5.0,4.0,3.0,2.0,1.0]})
    print "Done."
##    # CALCULATE RDC R-FACTOR
##    if projectname == '1c06':
##      rdcsets = ['dipo']
##    elif projectname == '1cmz':
##      rdcsets = ['dipo_bice_hn','dipo_phag_hn']
##    elif projectname == '1d3z':
##      rdcsets = ['dipo_bice1_hn','dipo_bice2_hn']
##    elif projectname == '1e8l':
##      rdcsets = ['dipo_bic1','dipo_bic2']
##    elif projectname == '1ghh':
##      rdcsets = ['dipo_bice_hn','dipo_phag_hn']
##    elif projectname == '1khm':
##      rdcsets = ['dipo_hn']
##    elif projectname == '1m12':
##      rdcsets = ['dipo_pha1','dipo_pha2']
##    elif projectname == '1op1':
##      rdcsets = ['dipo_phag','dipo_poly']
##    elif projectname == '1plo':
##      rdcsets = ['dipo_hn']
##    elif projectname == '1q2n':
##      rdcsets = ['dipo_hn']
##    elif projectname == '1ud7':
##      rdcsets = ['dipo_hn']
##    elif projectname == '3gb1':
##      rdcsets = ['dipo_bice_hn','dipo_taba_hn']
##    else:
    rdcsets = []
    plotname = os.path.join(queen.outputpath,'%s_rfactor.txt'%protocol)
    if not os.path.exists(plotname):
      # DETERMINE AVERAG RFACTOR
      rdcd = {}
      for rdcset in rdcsets:
        print "Calculating RDC R-factors for set: %s."%rdcset
        rdcdata = qn_readdata(queen,nmv_adjust(queen.dataset,rdcset))
        rdcrestraints = rdcdata['data']
        rlist = []
        prog = progress_indicator(len(structures))
        # BUILT A LIST OF R-FACTORS
        for el in structures:
          prog.increment(structures.index(el)+1)
          rflist = []
          for i in range(10):
            rflist.append(xplor_qfactor(el,xplr.psf,rdcrestraints))
          r = min(rflist)
          rlist.append(r)
        # STORE THE AVERAGE
        avg = avg_list(rlist)
        rdcd[rdcset]=avg
        # STORE A HISTOGRAM OF THE R-FACTORS
        print len(rlist)
        bins = list_bin(rlist,binsize=0.025,plot2screen=False)
        # PLOT THE BINS
        bplotname = os.path.join(queen.outputpath,'%s_rfac_%s.dat'%(protocol,rdcset))
        xmgr = graceplot(bplotname,'bar','w')
        xmgr.xlab = "R-factor (%)"
        xmgr.ylab = "Occurence (%)"
        xmgr.writeheader()
        rvals = bins.keys()
        rvals.sort()
        for rval in rvals:
          xmgr.write([float(rval),bins[rval]])
        xmgr.close()
      # WRITE R-FACTORS TO OUTPUT FILE
      outf = open(plotname,'w')
      for rdcset in rdcsets:
        outf.write("%20s : %5.2f +/- %5.2f\n"%(rdcset,
                                               100*rdcd[rdcset][0],
                                               100*rdcd[rdcset][1]))
      outf.close()
    # DETERMINE RAMACHANDRAN PLOT Z-SCORE AND NUMBER OF BUMPS
    rplotname = os.path.join(queen.outputpath,'%s_rama.txt'%protocol)
    bplotname = os.path.join(queen.outputpath,'%s_bump.txt'%protocol)
    if not os.path.exists(bplotname) or not os.path.exists(rplotname):
      ramaz,bumps = [],[]
      for el in structures:
        z = pdb_getramazscore(nmvconf['WHATIF_RUN'],el)
        ramaz.append(z)
        b100 = pdb_getnobumpsper100(nmvconf["WHATIF_RUN"],el)
        bumps.append(b100)
      avg = avg_list(ramaz)
      # WRITE RAMA TO FILE
      outf = open(rplotname,'w')
      str = "Ramachandran Z-score  : %5.2f +/- %5.2f"%(avg[0],avg[1])
      outf.write("%s\n"%str)
      outf.close()
      # WRITE BUMPS TO FILE
      avg = avg_list(bumps)
      outf = open(bplotname,'w')
      str = "Number bumps per 100  : %5.2f +/- %5.2f"%(avg[0],avg[1])
      outf.write("%s\n"%str)
      outf.close()
    # SUPERIMPOSE THE STRUCTURES USING PROFIT
    print "Superimposing %03i structures using ProFit."%len(structures)
    fitlist = glob.glob(os.path.join(queen.pdb,'%s_*.fit'%protocol))
    fitlist = fitlist[:maxstruct]
    if len(fitlist)<len(structures):
      fitlist = prft_superimpose(structures,overwrite=0)
    # DETERMINE RMSD MTX OF STRUCTURES
    plotname = os.path.join(queen.outputpath,'%s_rmsd.txt'%protocol)
    if not os.path.exists(plotname):
      # Backbone RMSD
      rmsdmtx = yas_rmsdmtxfast(nmvconf["YASARA_RUN"],fitlist,['CA','N','C'],
                                unit='Obj',fitflag=0)
      rmsdlist = []
      if len(fitlist)>1:
        for i in range(len(fitlist)):
          del rmsdmtx[i][i]
          rmsdlist.append(avg_list(rmsdmtx[i],sdflag=0))
        avg = avg_list(rmsdlist)
      else: avg = [0.,0.]
      # WRITE RMSDS TO FILE
      outf = open(plotname,'w')
      str = "Pairwise backbone RMSD: %5.2f +/- %5.2f"%(avg[0],avg[1])
      outf.write("%s\n"%str)
      outf.close()
      print str
      # HEAVY ATOM RMSD
      rmsdmtx = yas_rmsdmtxfast(nmvconf["YASARA_RUN"],fitlist,['Element !H'],
                                unit='Obj',fitflag=0)
      rmsdlist = []
      if len(fitlist)>1:
        for i in range(len(fitlist)):
          del rmsdmtx[i][i]
          rmsdlist.append(avg_list(rmsdmtx[i],sdflag=0))
        avg = avg_list(rmsdlist)
      else: avg = [0.,0.]
      # WRITE RMSDS TO FILE
      outf = open(plotname,'a')
      str = "Pairwise heavy atom RMSD: %5.2f +/- %5.2f"%(avg[0],avg[1])
      outf.write("%s\n"%str)
      outf.close()
      print str
      # XRAY DEVIATION
      rmsdlist = yas_superimpose(nmvconf["YASARA_RUN"],
                                 xray,fitlist,
                                 selection='bb')
      xavg = avg_list(rmsdlist)
      # WRITE XRAY RMSD TO FILE
      outf = open(plotname,'a')
      str = "X-ray backbone RMSD: %5.2f +/- %5.2f"%(xavg[0],xavg[1])
      outf.write("%s\n"%str)
      outf.close()
      print str
      rmsdlist = yas_superimpose(nmvconf["YASARA_RUN"],
                                 xray,fitlist,
                                 selection='heavy')
      xavg = avg_list(rmsdlist)
      # WRITE XRAY RMSD TO FILE
      outf = open(plotname,'a')
      str = "X-ray heavy atom RMSD: %5.2f +/- %5.2f"%(xavg[0],xavg[1])
      outf.write("%s\n"%str)
      outf.close()
      print str
    if len(fitlist) > 1:
      # DETERMINE NUMBER OF RESIDUES
      pdbf = pdb_file.Structure(structures[0])
      nres = 0
      for chain in pdbf.peptide_chains: nres += len(chain)
      # DETERMINE THE PER RESIDUE RMSD SCORES
      plotname = os.path.join(queen.outputpath,'%s_rmsd_bb.dat'%protocol)
      bbrmsd = []
      if not os.path.exists(plotname):
        # CALCULATE RMSD SCORES
        plotlist = []
        # BUILD LIST OF RESIDUE NUMBERS
        residues = []
        for residue in range(1,nres+1): residues.append(residue)
        # CALCULATE LIST OF RMSD MATRICES
        rmsdmtxlist = yas_rmsdmtxfast(nmvconf["YASARA_RUN"],fitlist,['CA','N','C'],
                                      unit='Res',fitflag=0)
        # CYCLE THE RESIDUES
        for r in residues:
          rmsdmtx = rmsdmtxlist[residues.index(r)]
          rmsdlist = []
          for i in range(len(structures)):
            del rmsdmtx[i][i]
            rmsdlist.append(avg_list(rmsdmtx[i],sdflag=0))
          avg = avg_list(rmsdlist)
          bbrmsd.append(avg[0])
          print "Pairwise RMSD residue %03i: %5.2f +/- %5.2f"%(r,avg[0],avg[1])
          plotlist.append([r,avg[0],avg[1]])
        # WRITE PLOT
        xmgr = graceplot(plotname,'xy','w')
        xmgr.xlab = "Residue number"
        xmgr.ylab = "Backbone RMSD (A\v{0.8}\h{-0.52}\z{0.6}o\z{}\h{0.19}\v{})"
        xmgr.writeheader()
        xmgr.mwrite(plotlist)
        xmgr.close()
      else:
        xmgr = graceplot(plotname,'xy','r')
        xmgr.read()
        for el in xmgr.data:
          bbrmsd.append(el[1])
      # CORRELATE RMSD WITH UNCERTAINTY
      print "%5s cc RMSD vs UNC: %05.2f"%(protocol,list_cc(bbrmsd,ulist)*100)
      plotname = os.path.join(queen.outputpath,'%s_cc.txt'%protocol)
      if not os.path.exists(plotname):
        output = open(plotname,'w')
        output.write("cc : %05.2f\n"%(list_cc(bbrmsd,ulist)*100))
        output.close()
      # AND WRITE A PLOT
      plotname = os.path.join(queen.outputpath,'%s_rmsd_vs_unc.dat'%protocol)
      if not os.path.exists(plotname):
        xmgr = graceplot(plotname,'xy','w')
        xmgr.xlab = "Uncertainty (bits/atom\S2\N)"
        xmgr.ylab = "Backbone RMSD (A)"
        xmgr.writeheader()
        for i in range(len(ulist)):
          xmgr.write([ulist[i],bbrmsd[i]])
        xmgr.close()


#  ===========================================================================
#   S U B S C R I P T   7 7 : X P L O R   2   C O N C O O R D
#  ===========================================================================
#
def nmv_writeconcoord(projectname,dataset,outtbl):
  print "Converting dataset %s for projects %s\nto CONCOORD format."%(projectname,
                                                                      dataset)
  # SETUP QUEEN & XPLOR
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # READ RESTRAINTS
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  data = qn_readdatasets(queen,datasets)
  restraintlist = data['data'] + data['bckg']
  # DO THE CONVERSION
  cnc_writeconcoord(xplr.psf,xplr.template,restraintlist,outtbl)
  print "The converted file can be found at:\n%s"%outtbl


#  ===========================================================================
#   S U B S C R I P T   7 8 : C A L C   C N C   S T R U C T U R E S
#  ===========================================================================
#
def nmv_cnccalcstruct(projectname,setname,cnctbl,nstruct):
  # SETUP QUEEN & XPLOR
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # SET THE BASENAME
  base = os.path.join(queen.pdb,'%s'%setname)
  # INITIALIZE CONCOORD
  cnc = cncrd(nmvconf["CNCRDDEV_PATH"])
  # RUN DIST
  cnc.dist_nmr(base,xplr.template,cnctbl)
  # RUN DISCO
  cnc.disco_nmr(base,nstruct,viol=1,bs=5,iter=10000)

#  ===========================================================================
#   S U B S C R I P T   7 9 : G E T   R D C   S T R U C T U R E S
#  ===========================================================================
#
def nmv_getpdbrdc(outputfile):
  print "Searching for NMR PDB files with RDC data."
  # READ DICT IF OUTPUT FILE EXISTS
  if os.path.exists(outputfile):
    dct = dct_read(outputfile)
  else:
    dct = {}
  # READ THE PDBFINDER
  pdbfinder = pdb_finder(nmvconf["PDBFINDER"],"r",0,error)
  pdbfinder.buildindex()
  # START PROGRESS BAR
  npdb = len(pdbfinder.recordpos.keys())
  prog = progress_indicator(npdb)
  prog.increment(0)
  cnt = 0
  dctl = dct.keys()
  # READ FIRST RECORD
  for el in pdbfinder.recordpos.keys():
    pdbfinder.read(el)
    if pdbfinder.id not in dctl:
      method = pdbfinder.fieldvalue('Exp-Method')
      #print pdbfinder.id,
      date   = pdbfinder.fieldvalue(' Date')
      if date: year  = int(date[:4])
      else: year = 2000
      #print year, method
      # CHECK FOR NMR AND YEAR >= 1997
      if method == 'NMR' and year >= 1997:
        # OPEN THE PDB FILE
        pdbf = nmv_adjust(nmvconf["PDB"],pdbfinder.id.lower())
        rdc = 0
        if os.path.exists(pdbf):
          file = open(pdbf,'r')
          line = file.readline()
          while line[:4]!='ATOM':
            # SWITCH TO LOWERCASE
            line = line.lower()
            # THE WORDLIST
            words = ['dipolar','liquid crystal','dipolar coupling',
                     'residual dipolar','alignment tensor','bicelle',
                     'aligned','alignment']
            # CHECK IF ANY OF THE WORDS ARE PRESENT
            for el in words:
              if el in line: rdc = 1
            line = file.readline()
            if len(line)<=1: break
          # STORE THE RESULTS
          if rdc: dct[pdbfinder.id]='yes'
          else: dct[pdbfinder.id]='no'
      # ELSE WE SET IT TO NO
      else:
        dct[pdbfinder.id]='no'
    # WRITE THE DICTIONARY AFTER EACH 500 FILES
    if cnt%500==0: dct_write(dct,outputfile)
    cnt += 1
    prog.increment(cnt)
  # WRITE FINAL DICT
  dct_write(dct,outputfile)
  # PRINT RESULT
  pdbl = [el for el in dct.keys() if dct[el]=='yes']
  print "Found %i structures."%len(pdbl)
  # CHECK WHICH ARE IN OUR DB
  ppath = '/home/snabuurs/secondary_data/db_queen_dataonly'
  targets = []
  for el in pdbl:
    path = os.path.join(ppath,el.lower())
    if os.path.exists(path):
      targets.append(el)
  print "We found %i easy targets:"%len(targets)
  for target in targets:
    print target
  print "Done."

#  ===========================================================================
#   S U B S C R I P T   8 0 : T E S T   C N C   C O N V E R G E N C E
#  ===========================================================================
#
def nmv_cncconvergence(rdcdict,projectpath):
  print 'Testing structures with RDC data for CNC convergence.'
  # READ THE DICTIONARY
  dct = dct_read(rdcdict)
  # CHECK IF WE HAVE SETS IN OUT DATABASE
  datapath = '/home/snabuurs/secondary_data/db_queen_dataonly/'
  projectlist = []
  pdbl = dct.keys()
  for pdb in pdbl:
    if dct[pdb]=='yes':
      pdb = pdb.lower()
      ppath = os.path.join(datapath,pdb)
      npath = os.path.join(projectpath,pdb)
      # ADD IT IF PATH EXISTS AND COPY DATA
      if os.path.exists(ppath):
        projectlist.append(pdb)
        if not os.path.exists(npath):
          shutil.copytree(ppath,npath)
  print "Found %i suitable datasets."%(len(projectlist))
  # CYCLE THE PROJECTS
  for project in projectlist:
    print "## %s ##"%project
    # SET PROJECTPATH
    nmvconf["Q_PROJECT"]=projectpath
    # READ DISTANCE DATA
    print "Converting distance data to CONCOORD format."
    queen = qn_setup(nmvconf,project)
    xplr  = qn_setupxplor(nmvconf,project)
    data  = qn_readdata(queen,nmv_adjust(queen.dataset,'all'))
    restraints = [el for el in data['data'] if el.type=='DIST']
    # CONVERT TO CNC FORMAT
    cnctbl= os.path.join(os.path.dirname(queen.table),'noe.cnc')
    if not os.path.exists(cnctbl):
      cnc_writeconcoord(xplr.psf,xplr.template,restraints,cnctbl)
    # SET CNC BASENAME
    setname = 'test'
    base = os.path.join(queen.pdb,setname)
    # INITIALIZE CONCOORD
    cnc = cncrd(nmvconf["CNCRDDEV_PATH"])
    # RUN DIST
    datfile = os.path.join(queen.pdb,'%s.dat'%setname)
    if not os.path.exists(datfile):
      cnc.dist_nmr(base,xplr.template,cnctbl)
      # RUN DISCO
      cnc.disco_nmr(base,nstruct=1,maxtry=5,viol=1,bs=5,iter=10000)
  print "Done."

#  ===========================================================================
#   S U B S C R I P T   8 1 : S U M M A R I Z E   C O N C O O R D
#  ===========================================================================
#
def nmv_summarizeconcoord():
  print "Summarizing CONCOORD runs."
  # LIST OF PROJECTS
  projectlist = ['3gb1',
                 '1d3z',
                 '1kdf',
                 '1beg',
                 '1r63']
  # LIST OF APPLIED METHODS
  methodlist = ['xpl','xplw',
                'cns','cnsw',
                'cnc5','cnc5w',
                'cnc6','cnc6w',
                'xray','xrayw']
  # STORAGE DICTIONARY
  dct = {}
  # CYCLE THE PROJECTLIST
  # =====================
  checklist = []
  for project in projectlist:
    print "# %s #\n########"%project
    path = os.path.join(nmvconf["CNC_PROJECT"],'%s/output'%project)
    dct[project] = dct.get(project,{})
    finalmethodlist = copy.copy(methodlist)
##    if project in ['3gb1']:
##      vdw = ['142_050','142_055','142_060','142_065','142_070','nb2_030','nb2_035','nb2_040','nb2_045','nb2_050','nb2_055','nb2_060']
##      for i in range(len(vdw)):
##        finalmethodlist.extend([vdw[i]])
##        #finalmethodlist.extend([vdw[i],"%se"%vdw[i],"%sw"%vdw[i]])
    # ADD PDB ENTRIES
    finalmethodlist.append('%s'%project)
    finalmethodlist.append('%sw'%project)
    for method in finalmethodlist:
      # INITIALIZE DICTIONARY
      dct[project][method]=dct.get(method,{})
      # READ THE VIOLATIONS
      # ===================
      fname = os.path.join(path,'%s_violations.txt'%method)
      # VALUES
      rms = None
      if os.path.exists(fname):
        content = open(fname,'r').readlines()
        # GET RMS
        rmsline = content[5].split()
        rms = [float(rmsline[3]),float(rmsline[5])]
      # STORE RESULTS
      dct[project][method]['rms']=rms
      if 'rms' not in checklist: checklist.append('rms')
      # READ THE RFACTORS
      # =================
      fname = os.path.join(path,'%s_rfactor.txt'%method)
      # VALUES
      rf1,rf2 = None,None
      if os.path.exists(fname):
        content = open(fname,'r').readlines()
        if len(content)>0:
          rline = content[0].split()
          rf1 = [float(rline[2]),float(rline[4])]
          if len(content)==2:
            rline = content[1].split()
            rf2 = [float(rline[2]),float(rline[4])]
      # STORE RESULTS
      dct[project][method]['Rf1']=rf1
      if 'Rf1' not in checklist: checklist.append('Rf1')
      dct[project][method]['Rf2']=rf2
      if 'Rf2' not in checklist: checklist.append('Rf2')
      # READ RAMACHANDRAN
      # =================
      fname = os.path.join(path,'%s_rama.txt'%method)
      rama = None
      if os.path.exists(fname):
        content = open(fname,'r').readlines()
        ramaline = content[0].split()
        rama = [float(ramaline[3]),float(ramaline[5])]
      # STORE RESULTS
      dct[project][method]['rama']=rama
      if 'rama' not in checklist: checklist.append('rama')
      # READ BUMPS
      # ==========
      fname = os.path.join(path,'%s_bump.txt'%method)
      bump = None
      if os.path.exists(fname):
        content = open(fname,'r').readlines()
        bumpline = content[0].split()
        bump = [float(bumpline[5]),float(bumpline[7])]
      # STORE RESULTS
      dct[project][method]['bump']=bump
      if 'bump' not in checklist: checklist.append('bump')
      # READ RMSD
      # =========
      fname = os.path.join(path,'%s_rmsd.txt'%method)
      rmsdhv,rmsdbb,rmsdxhv,rmsdxbb = None,None,None,None
      if os.path.exists(fname):
        content = open(fname,'r').readlines()
        rmsdbbline = content[0].split()
        rmsdbb = [float(rmsdbbline[3]),float(rmsdbbline[5])]
        rmsdhvline = content[1].split()
        rmsdhv = [float(rmsdhvline[4]),float(rmsdhvline[6])]
        if len(content) > 2:
          rmsdxbbline = content[2].split()
          rmsdxbb = [float(rmsdxbbline[3]),float(rmsdxbbline[5])]
          rmsdxhvline = content[3].split()
          rmsdxhv = [float(rmsdxhvline[4]),float(rmsdxhvline[6])]
      # STORE RESULTS
      dct[project][method]['rmsdbb']=rmsdbb
      if 'rmsdbb' not in checklist: checklist.append('rmsdbb')
      dct[project][method]['rmsdhv']=rmsdhv
      if 'rmsdhv' not in checklist: checklist.append('rmsdhv')
      dct[project][method]['rmsdxbb']=rmsdxbb
      if 'rmsdxbb' not in checklist: checklist.append('rmsdxbb')
      dct[project][method]['rmsdxhv']=rmsdxhv
      if 'rmsdxhv' not in checklist: checklist.append('rmsdxhv')
      # READ QUEEN CC
      # =============
      fname = os.path.join(path,'%s_cc.txt'%method)
      cc = None
      if os.path.exists(fname):
        content = open(fname,'r').readlines()
        ccline = content[0].split()
        cc = [float(ccline[2])]
      # STORE RESULTS
      dct[project][method]['cc']=cc
      if 'cc' not in checklist: checklist.append('cc')
  # WRITE SUMMARY FILE
  fname = os.path.join(nmvconf["CNC_PROJECT"],'concoord.sum')
  output = open(fname,'w')
  for project in projectlist:
    print project
    if project == '1kdf': refset = 'cnc6'
    else: refset = 'cnc5'
    finalmethodlist = copy.copy(methodlist)
##    if project == '3gb1':
##      finalmethodlist.append('%sx'%project)
##      vdw = ['142_050','142_055','142_060','142_065','142_070','nb2_030','nb2_035','nb2_040','nb2_045','nb2_050','nb2_055','nb2_060']
##      for i in range(len(vdw)):
##        finalmethodlist.extend([vdw[i]])
##        #finalmethodlist.extend([vdw[i],"%se"%vdw[i],"%sw"%vdw[i]])
    # ADD PDB ENTRIES
    finalmethodlist.append('%s'%project)
    finalmethodlist.append('%sw'%project)
    output.write("## %s ##\n\n"%project)
    # THE HEADER
    header = '%10s'%' '
    base   = '='*10
    for check in checklist:
      # SOME EXCEPTIONS:
      if check == 'rms'      : check = "RMS violations (A)"
      elif check == 'Rf1'    : check = "R-factor 1 (%)"
      elif check == 'Rf2'    : check = "R-factor 2 (%)"
      elif check == 'rama'   : check = "Ramachandran (Z)"
      elif check == 'bump'   : check = "Bumps (100 res)"
      elif check == 'rmsdbb' : check = "Backbone RMSD (A)"
      elif check == 'rmsdhv' : check = "All atom RMSD (A)"
      elif check == 'rmsdxbb': check = "Backb XR RMSD (A)"
      elif check == 'rmsdxhv': check = "Heavy XR RMSD (A)"
      elif check == 'cc'     : check = "QUEEN cc (%)"
      header += check.ljust(20)
      base   += "="*20
    output.write("%s\n%s\n"%(header,base))
    # THE DATA
    count = 0
    # CYCLE METHODS
    for method in finalmethodlist:
      data = "%10s"%method.ljust(10)
      # CYCLE CHECK
      for check in checklist:
        dat = dct[project][method][check]
        # IF NO VALUE IS KNOWN
        if not dat:
          str   = "%9s"%('-')
          data += str.ljust(17)
        # IF ONLY ONE VALUE IS STORED
        elif len(dat)==1:
          str = "%6.2f"%(dat[0])
          data += str.ljust(20)
        # IF VALUE + SD IS STORED
        elif len(dat)==2:
          # SOME EXCEPTIONS
          if check == 'rms': str = "%6.4f +/- %6.4f"%(dat[0],dat[1])
          # RMSDS FOR XRAY STRUCTURES
          elif check in ['rmsdbb','rmsdhv','rmsdxbb','rmsdxhv'] and dat == [0.,0.]:
            str = "%9s"%'-'
          else:
            str = "%6.2f +/- %5.2f"%(dat[0],dat[1])
          data += str.ljust(17)
        # CHECK IF SIGNIFICANTLY DIFFERENT
        if (not dat) or len(dat)!=2 or dat[1] == 0.:
          str = '   '
        else:
          # TAKE CNC AS REFERENCE
          if method[-1]=='w':
            ref = dct[project]['%sw'%refset][check]
          else:
            ref = dct[project]['%s'%refset][check]
          if not ref: ref = [0.,0.]
          ucal = abs(dat[0]-ref[0])/math.sqrt(((dat[1]**2)/100)+((ref[1]**2)/100))
          if ucal > 1.96: str = ' * '
          else: str = ' . '
        data += str
      # WRITE OUTPUT
      output.write("%s\n"%data)
      count += 1
      # WRITE SEPARATOR
      if count%2==0: output.write('----------\n')
    output.write("\n")
  output.close()
##  for project in projectlist:
##    path = os.path.join(nmvconf["CNC_PROJECT"],'%s/output'%project)
##    if project == '3gb1':
##      # WRITE INPUT FOR FIGURE 2
##      for set in ['142','nb2']:
##        for check in ['rmsdbb','bump','Rf1','Rf2']:
##          fname = os.path.join(path,'fig2_%s_%s.dat'%(set,check))
##          xmgr = graceplot(fname,'xydy','w')
##          xmgr.writeheader()
##          for el in vdw:
##            if el.split("_")[0]==set:
##              dat = dct[project][el][check]
##              xmgr.write([float(el[-3:])/100,dat[0],dat[1]/10.0])
##          xmgr.close()
  print "Done."


#  ===========================================================================
#   S U B S C R I P T   82 :  A N A L Y Z E   R E S T R A I N T S
#  ===========================================================================
#
def nmv_anasubsets(projectname='3gb1',dataset='noe'):
  # OVERWRITE Q_PROJECT
  nmvconf["Q_PROJECT"]='/storage/projects/datavsqual'
  # SET PARAMETERS
  subsets     = [100.,95.,90.,85.,80.,75.,70.,65.,60.]
  nsets       = 5
  # INITIALIZE QUEEN AND XPLOR
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # THE OUTPUT RESTRAINT FILE
  tblpath = os.path.join(queen.outputpath,"%s.tbl"%dataset)
  # READ THE RESTRAINTS
  r = restraint_file(tblpath,'r',format="XPLOR")
  r.read()
  r.close()
  # CALCULATE INFO SCORES
  print "Calculating information content full set."
  unc_ini = queen.uncertainty(xplr,[])
  unc_all = queen.uncertainty(xplr,r.restraintlist)
  inf_all = unc_ini-unc_all
  numberr = len(r.restraintlist)
  fullist = copy.copy(r.restraintlist)
  sets = []
  # CALCULATE INFOCONTENT FOR THE SETS
  for subset in subsets:
    print "Subset %3i of %3i."%(subsets.index(subset)+1,len(subsets))
    for i in range(nsets):
      print "Set    %3i of %3i."%(i+1,nsets)
      # READ RESTRAINTS
      print "Reading restraints."
      intbl = nmv_adjust(queen.table,"%s_%05.1f_%i"%(dataset,subset,i+1))
      r = restraint_file(intbl,'r')
      r.read()
      # CALCULATE INFO
      unc  = queen.uncertainty(xplr,r.restraintlist)
      inf  = unc_ini - unc
      perc = (inf/inf_all)*100.
      # STORE DICT WITH INFO
      set = {}
      set['info']   = perc
      set['data']   = (float(len(r.restraintlist))/numberr)*100
      set['runid']  = i+1
      set['target'] = subset
      sets.append(set)
  # OUTPUTFILE A
  outputfile = os.path.join(queen.outputpath,'fig2_A_%s.dat'%(dataset))
  print outputfile
  xmgr = graceplot(outputfile,'xy','w')
  xmgr.xlab = "Information content (%)"
  xmgr.ylab = "Number of restraints"
  xmgr.square = 1
  xmgr.writeheader()
  # PLOT ALL DATAPOINTS
  for set in sets:
    xmgr.write([set['info'],set['data']])
  xmgr.type = 'xydxdy'
  xmgr.newset()
  # CALCULATE AVG FOR EACH SUBSET
  for subset in subsets:
    xlist,ylist = [],[]
    for set in sets:
      if set['target']==subset:
        xlist.append(set['info'])
        ylist.append(set['data'])
    xavg = avg_list(xlist)
    yavg = avg_list(ylist)
    xmgr.write([xavg[0],yavg[0],xavg[1],yavg[1]])
  xmgr.close()
  # OUTPUTFILE B
  outputfile = os.path.join(queen.outputpath,'fig2_B_%s.dat'%(dataset))
  print outputfile
  xmgr = graceplot(outputfile,'xy','w')
  xmgr.ylab = "Information content (%)"
  xmgr.xlab = "Number of restraints"
  xmgr.square = 1
  xmgr.writeheader()
  avglist = []
  #subsets = []
  #for i in range(20):
  #  subsets.append(i*5.0)
  # CALCULATE AVG FOR EACH SUBSET
  for subset in subsets:
    print "Subset %3i of %3i."%(subsets.index(subset)+1,len(subsets))
    ylist = []
    for i in range(nsets):
      print "Set    %3i of %3i."%(i+1,nsets)
      # SHUFFLE THE LIST
      shuffle(fullist)
      # TAKE A SUBSET
      cnt = int((subset/100)*numberr)
      tstlist = fullist[:cnt]
      # CALCULATE INFO
      unc  = queen.uncertainty(xplr,tstlist)
      inf  = unc_ini - unc
      perc = (inf/inf_all)*100.
      # WRITE DATAPOINT
      xmgr.write([perc,subset])
      ylist.append(perc)
    avg = avg_list(ylist)
    avglist.append([avg[0],subset,avg[1]])
  # PLOT AVERAGES
  xmgr.type = 'xydx'
  xmgr.newset()
  xmgr.mwrite(avglist)
  xmgr.close()
  print "Done."

#  ===========================================================================
#   S U B S C R I P T   8 3 :  C A L C U L A T E   S T R U C T U R E S
#  ===========================================================================
#
def nmv_calculatestructures(projectname,dataset,nstructures=20):
  # PARAMS
  thr_noe = 0.5
  thr_dih = 10
  # SETUP QUEEN
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  # READ DATA
  data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
  # COMBINE ALL DATA, WE ALSO CHECK THE BACKGROUND INFORMATION!
  restraints = data["data"] + data["bckg"]
  # CALCULATE BASENAME
  base = os.path.join(queen.pdb,'n_%s'%dataset)
  annealed = glob.glob("%s_a_*.pdb"%base)
  if len(annealed) != nstructures:
    print "Calculating %i structures."%nstructures
    # CALCULATE STRUCTURES
    mtf = os.path.join(queen.pdb,'protein.mtf')
    if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
    cns_calcstructure(base,
                      xplr.template,
                      mtf,
                      restraints,
                      naccepted=nstructures,
                      thr_noe=thr_noe,
                      thr_dih=thr_dih,
                      ntrial=25)
    annealed = glob.glob("%s_a_*.pdb"%base)
  else:
    print "Found %i structures."%nstructures
  # REFINE STRUCTURES
  refined = []
  print "Refining %i structures."%len(annealed)
  for pdb in annealed:
    n = annealed.index(pdb)+1
    outpdb = os.path.join(queen.pdb,'n_ref_%s_%03i.pdb'%(dataset,n))
    if not os.path.exists(outpdb):
      xplor_refstruct(pdb,outpdb,xplr.psf,restraints,
                      thr_noe=thr_noe,
                      thr_dih=thr_dih,
                      mdheat  = 200,
                      mdhot   = 1000,
                      mdcool  = 200)
    refined.append(outpdb)
    print "Completed %i refinements.\r"%len(refined),
  # VIOLATION ANALYSIS
  print "Performing violation analysis."
  for el in ['n_%s_a'%dataset,'n_ref_%s'%dataset]:
    fname = os.path.join(queen.outputpath,
                         '%s_viol.txt'%el)
    if not os.path.exists(fname):
      pdblist = glob.glob(os.path.join(queen.pdb,"%s_*.pdb"%el))
      xplor_violanalysis(pdblist,
                         xplr.psf,
                         restraints,
                         outputfile=fname)
  # CREATE CHECK PLOTS
  print "Generating quality plots."
  checks = ['Backbone','Packing1','Phipsi','Bumps']
  basename = os.path.join(queen.outputpath,
                          'n_ref_%s'%dataset)
  if not os.path.exists(basename+'_%s.dat'%checks[-1]):
    pdb_plotchecks(refined,checks,basename)
  print "\nDone."


#  ===========================================================================
#   S U B S C R I P T   8 3 :  C A L C U L A T E   S T R U C T U R E S
#  ===========================================================================
#
def nmv_anapdbblunder():
  # SET PATH
  nmvconf["Q_PROJECT"] = '/projects/pdbblunder'
  # PROJECTLIST
  projectlist = ['1tgq',
                 '1y4o']
  # DATASETS
  datasetlist = ['noedih','inter','hbonds','simset']
  # CHECKLIST
  checklist = ['Backbone',
               'PhiPsi',
               'Chi1Chi2',
               'Bumps',
               'Packing1',
               'Packing2',
               'InOut']
  # CYCLE PROJECTS AND ANALYSE ENSEMBLE
  # -----------------------------------
  for projectname in projectlist:
    print "Analyzing the %s ensemble."%projectname
    # INITIALIZE QUEEN
    queen = qn_setup(nmvconf,projectname)
    xplr  = qn_setupxplor(nmvconf,projectname)
    # BUILD PDBLIST
    pdblist = glob.glob(os.path.join(queen.pdb,
                                     '%s_ensemble_0*.pdb'%projectname))
    print "Found %i structures."%len(pdblist)
    for dataset in datasetlist:
      print "Analyzing dataset '%s'"%dataset
      data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
      restraints = data["data"] + data["bckg"]
      output = os.path.join(queen.outputpath,
                            'viol_%s_ensemble_%s.txt'%(projectname,dataset))
      if not os.path.exists(output):
        print "Performing violation analysis for %i structures."%len(pdblist)
        xplor_violanalysis(pdblist,xplr.psf,restraints,output)
  # REFINE BOTH ENSEMBLES
  projectlist = ['1tgq','1y4o']
  for projectname in projectlist:
    if   projectname == '1y4o': datasetlist = ['noedih']
    elif projectname == '1tgq': datasetlist = ['simset']
    # REFINE USING DIFFERENT DATASETS
    for dataset in datasetlist:
      # READ THE RESTRAINTS
      queen = qn_setup(nmvconf,projectname)
      xplr  = qn_setupxplor(nmvconf,projectname)
      data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
      restraints = data["data"] + data["bckg"]
      # BUILD A LIST OF INPUT FILES
      pdblist = glob.glob(os.path.join(queen.pdb,
                                       '%s_ensemble_0*.pdb'%projectname))
      pdblist.sort()
      # ANALYZE QUALITY OF INPUT STRUCTURES
      # -----------------------------------
      outbase = os.path.join(queen.outputpath,'qua_%s_ensemble'%(projectname))
      outlist = glob.glob("%s*.dat"%outbase)
      if len(outlist)<len(checklist):
        pdb_plotchecks(pdblist,checklist,outbase)
      # GLOBAL SUMMARY
      outfile = os.path.join(queen.outputpath,'quasum_%s_ensemble.txt'%(projectname))
      if not os.path.exists(outfile):
        pdb_sumcheck_global(pdblist,checklist,outfile)
      # PLOT PER-RESIDUE RMSD
      # ---------------------
      outfile = os.path.join(queen.outputpath,
                             'rmsd_%s_ensemble.dat'%(projectname))
      if not os.path.exists(outfile):
        pdb_plotrmsd(pdblist,outfile,fitflag=1)
      # DO THE REFINEMENT
      # -----------------
      for i in range(len(pdblist)):
        inpdb  = pdblist[i]
        outpdb = os.path.join(queen.pdb,
                              '%s_ensemble_ref_%s_%03i.pdb'%(projectname,
                                                             dataset,i+1))
        if not os.path.exists(outpdb):
          print "Refining %s."%inpdb
          xplor_refstruct(inpdb,outpdb,
                          xplr.psf,restraints,
                          thr_noe=0.5,thr_dih=15.,maxtry=20,
                          mdheat=200,mdhot=2000,mdcool=200)
      # ANALYSE THE REFINED STRUCTURES
      # ------------------------------
      reflist = glob.glob(os.path.join(queen.pdb,
                                       '%s_ensemble_ref_%s_0*.pdb'%(projectname,
                                                                    dataset)))
      reflist.sort()
      # CHECK IF ALL ARE SUCCESSFULLY REFINED
      if len(reflist)!=len(pdblist):
        warning("Refinement failed for %i structures"%(len(pdblist)-len(reflist)))
      # OUTPUT FILE
      output = os.path.join(queen.outputpath,
                            'viol_%s_ensemble_ref_%s.txt'%(projectname,dataset))
      if not os.path.exists(output):
        print "Performing violation analysis for %i structures."%len(reflist)
        xplor_violanalysis(reflist,xplr.psf,restraints,output)
      # ANALYZE QUALITY OF REFINED STRUCTURES
      # -------------------------------------
      outbase = os.path.join(queen.outputpath,'qua_%s_ensemble_ref_%s'%(projectname,dataset))
      outlist = glob.glob("%s*.dat"%outbase)
      if len(outlist)!=len(checklist):
        pdb_plotchecks(reflist,checklist,outbase)
      # GLOBAL SUMMARY
      outfile = os.path.join(queen.outputpath,'quasum_%s_ensemble_ref.txt'%(projectname))
      if not os.path.exists(outfile):
        pdb_sumcheck_global(reflist,checklist,outfile)
      # PLOT PER-RESIDUE RMSD
      # ---------------------
      outfile = os.path.join(queen.outputpath,
                             'rmsd_%s_ensemble_ref_%s.dat'%(projectname,dataset))
      if not os.path.exists(outfile):
        pdb_plotrmsd(reflist,outfile,fitflag=1)
  # REPRODUCE 1TGQ STRUCTURES USING 1Y4O DATA
  projectname = '1tgq'
  dataset     = 'test'
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
  restraints = data["data"] + data["bckg"]
  # CALCULATE 20 ACCEPTED STRUCTURES USING NOEs ONLY
  mtf = os.path.join(queen.outputpath,'protein.mtf')
  if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
  # SET BASE NAME
  base = os.path.join(queen.pdb,'1tgq_simset')
  annealed = glob.glob("%s_a_*.pdb"%base)
  nstructures = 20
  if len(annealed) != nstructures:
    print "Calculating %i structures."%nstructures
    cns_calcstructure(base,
                      xplr.template,
                      mtf,
                      restraints,
                      naccepted=nstructures,
                      thr_noe=0.5,
                      thr_dih=15.,
                      ntrial=25)
  else:
    print "Found %i structures."%nstructures
  annealed = glob.glob("%s_a_*.pdb"%base)
  # CALCULATE AVERAGE STRUCTURE
  avgpdb = "%s_ave.pdb"%base
  if not os.path.exists(avgpdb):
    print "Calculating average from ensemble."
    xplor_calcave("%s_a_"%base,
                  20,
                  xplr.psf)
    # RENAME FILE
    os.rename("%s_a_ave.pdb"%base,"%s_ave.pdb"%base)
    # REFINE AVERAGE STRUCTURE
    print "Refining %s."%avgpdb
    outpdb = "%s_ave_ref.pdb"%base
    xplor_refstruct(avgpdb,outpdb,
                    xplr.psf,restraints,
                    thr_noe=0.5,thr_dih=15.,maxtry=20,
                    mdheat=200,mdhot=2000,mdcool=200)
  # DO SOME ADDITIONAL ANALYSES
  # ---------------------------
  # ANALYZE THE REFINED ENSEMBLES WITH NOEDIH AND SIMULATED DATA
  for dataset in ['noedih','inter']:
    for projectname in ['1tgq','1y4o']:
      # SET THE SET USED IN THE REFINEMENT
      if projectname == '1tgq': refset = 'simset'
      elif projectname == '1y4o': refset = 'noedih'
      # READ THE RESTRAINTS
      queen = qn_setup(nmvconf,projectname)
      xplr  = qn_setupxplor(nmvconf,projectname)
      data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
      restraints = data["data"] + data["bckg"]
      # SET OUTPUT FILENAME
      output = os.path.join(queen.outputpath,
                            'viol_%s_ensemble_ref_%s_%s.txt'%(projectname,refset,dataset))
      if not os.path.exists(output):
        reflist = glob.glob(os.path.join(queen.pdb,
                                         '%s_ensemble_ref_%s_0*.pdb'%(projectname,
                                                                      refset)))
        reflist.sort()
        print "Performing violation analysis for %i structures."%len(reflist)
        xplor_violanalysis(reflist,xplr.psf,restraints,output)
  # FINISHED
  print "Done."


def nmv_mkpbs(path,pbspath):
  cluster = 'beoclus'
  nodes = 1
  datasets = ['all']
  # SWITCH PRINT LINE FOR 'n'!
  jobs = ['dress']
  for job in jobs:
    for dataset in datasets:
      print job,dataset
      submitfile = os.path.join(pbspath,'submit_%s_%s.csh'%(job,dataset))
      submit = open(submitfile,'w')
      submit.write("#!/bin/sh\n")
      # READ THE DIRECTORY
      dirlist = glob.glob(os.path.join(path,'*'))
      dirlist.sort()
      for dir in dirlist:
        project = os.path.basename(dir)
        #path = os.path.join(nmvconf["Q_PROJECT"],project)
        if os.path.exists(os.path.join(dir,'data')):
          queen = qn_setup(nmvconf,project,myid,numproc)
          pbs = os.path.join(pbspath,'%s_%s_%s.pbs'%(job,project,dataset))
          submit.write("qsub %s_%s_%s.pbs\n"%(job,project,dataset))
          submit.write("sleep 1\n")
          setname = dataset
          if cluster == 'beoclus':
            file = """#!/bin/sh
    ### Job name
    #PBS -N %s_%s_%s
    ### Queue name
    #PBS -q dque@beoclus
    # Keep stout,-error in
    #PBS -k eo
    # Merge std error to stdout
    #PBS -j oe
    # How many and nodes are requested?
    #PBS -l nodes=%s:ppn=1
    ### Script Commands
    cd $PBS_O_WORKDIR

    echo \"Running LAM/MPI\"

    lamboot $PBS_NODEFILE
    /bin/sleep 60
    ###mpirun.lam -np %i python2.2 /data/home/vuister/snabuurs/python/nmr_valibase/nmr_valibase.py -xplr_refineproject %s %s
    lamclean
    lamhalt

    echo \"LAM/MPI complete\"
    echo
    exit 0
    """%(job,project,dataset,nodes,nodes,project,setname)
#  """%(job,project,dataset,nodes,1,job,project,setname)
##        elif cluster == 'octopus':
##          file = """#!/bin/sh
##  ### Job name
##  #PBS -N %s_%s
##  ### Queue name
##  #PBS -q workq
##  # Keep stout,-error in
##  #PBS -k eo
##  # Merge std error to stdout
##  #PBS -j oe
##  # How many and nodes are requested?
##  #PBS -l nodes=%i:ppn=2
##  ### Script Commands
##  cd $PBS_O_WORKDIR

##  echo \"Running LAM/MPI\"

##  #### BEGIN: This is not necessary in normal PBS LAM scripts ##############
##  lam_profile=/etc/profile.d/mpi-01lam.sh
##  . $lam_profile
##  #### but it seems to be necessary on our cluster! ########################

##  $LAMMPI/bin/lamboot $PBS_NODEFILE
##  $LAMMPI/bin/mpirun -np %i python2 /home/snabuurs/python/queen/queen.py -%s %s %s
##  $LAMMPI/bin/lamclean
##  $LAMMPI/bin/lamhalt

##  echo \"LAM/MPI complete\"
##  echo
##  exit 0
##  """%(job,project,nodes,nodes*2,job,project,setname)
          open(pbs,'w').write(file)
      submit.close()

def nmv_mk1pbs(path,pbspath):
  nodes = 4
  jobs = ['u']
  # READ THE DIRECTORY
  dirlist = glob.glob(os.path.join(path,'*'))
  for job in jobs:
    pbs = os.path.join(pbspath,'%s.pbs'%job)
    file = open(pbs,'w')
    file.write("""#!/bin/sh
### Job name
#PBS -N %s
### Queue name
#PBS -q dque@beoclus
# Keep stout,-error in
#PBS -k eo
# Merge std error to stdout
#PBS -j oe
# How many and nodes are requested?
#PBS -l nodes=%i:ppn=2
### Script Commands
cd $PBS_O_WORKDIR

echo \"Running LAM/MPI\"

lamboot $PBS_NODEFILE
"""%(job,nodes))
    for dir in dirlist:
      project = os.path.basename(dir)
      setname = 'all'
      file.write("lamexec /bin/sleep 60")
      #file.write("mpirun.lam -np %i python2.2 /data/home/vuister/snabuurs/python/queen_dev/queen.py -m -%s %s %s\n"%(nodes*2,job,project,setname))
    file.write("""lamclean
lamhalt

echo \"LAM/MPI complete\"
echo
exit 0
""")

def tine_dmtx(pdbfile,offset):
  import Numeric
  # DETERMINE THE NUMBER OF MODELS
  no_models = pdb_models(pdbfile)
  # READ THE PDBFILE, ALL MODELS
  print "Reading %i models."%no_models
  pdb = pdb_file.Structure(pdbfile,endmodel=no_models)
  print "Read %i models."%len(pdb.peptide_chains)
  nres = len(pdb.peptide_chains[0])
  print "Done."
  # A CHECK FOR THE FUTURE
  if no_models!=len(pdb.peptide_chains):
    print "It looks like this ensemble does not contain monomeric structures!"
  ddict = {}
  # CYCLE ALL MODELS
  print "Storing inter Ca distances..."
  for pdbchain in pdb.peptide_chains:
    chain = pdbchain.chain_id
    ddict[chain]=ddict.get(chain,{})
    if pdbfile.find('1gm1')>-1:
      for i in range(offset,nres+5+offset):
        ddict[chain][i]=ddict[chain].get(i,{})
        for j in range(offset,nres+5+offset):
          ddict[chain][i][j]=ddict[chain][i].get(j,[])+[]
    # CYCLE ALL RESIDUES
    for residue1 in pdbchain:
      if pdbfile.find('1gm1')>-1:
        rn = residue1.number
        if rn > 30: rn1 = rn+5
        else: rn1 = rn
        if rn==31:
          for i in range(31,36):
            ddict[chain][i]=ddict[chain].get(i,{})
            for j in range(nres+5):
              ddict[chain][i][j+offset]=ddict[chain][i].get(j+offset,[])+[]
      else:
        rn1 = residue1.number
      ddict[chain][rn1]=ddict[chain].get(rn1,{})
      # CYCLE THE ATOMS
      for atom in residue1:
        if atom.name == 'CA':
          # STORE THE COORDINATES
          ca1 = atom["position"]
      for residue2 in pdbchain:
        if pdbfile.find('1gm1')>-1:
          rn = residue2.number
          if rn > 30: rn2 = rn+5
          else: rn2 = rn
        else: rn2 = residue2.number
        # CYCLE THE ATOMS
        for atom in residue2:
          if atom.name == 'CA':
            # STORE THE COORDINATES
            ca2 = atom["position"]
        dist = nmr_distance(ca1,ca2)
        ddict[chain][rn1][rn2]=ddict[chain][rn1].get(rn2,[])+[dist]
  print "Done storing inter CA distances."
  # AN ARRAY IN WHICH WE STORE ALL COORDINATES
  if pdbfile.find('1gm1')>-1:
    base = Numeric.array([0.0])
    darray=Numeric.resize(base,(nres+5,nres+5))
    sdarray=Numeric.resize(base,(nres+5,nres+5))
    carray=Numeric.resize(base,(nres+5,nres+5))
    for i in range(nres+5):
      for j in range(nres+5):
        avg = avg_list(ddict[chain][i+offset][j+offset])
        darray[i][j] = avg[0]
        sdarray[i][j] = avg[1]
        try:
          carray[i][j] = (avg[1]/avg[0])*100
        except ZeroDivisionError:
          carray[i][j] = 0.0
  else:
    base = Numeric.array([0.0])
    darray=Numeric.resize(base,(nres-1,nres-1))
    sdarray=Numeric.resize(base,(nres-1,nres-1))
    carray=Numeric.resize(base,(nres-1,nres-1))
    for i in range(0,nres-1):
      for j in range(0,nres-1):
        avg = avg_list(ddict[chain][i+offset+1][j+offset+1])
        darray[i][j] = avg[0]
        sdarray[i][j] = avg[1]**2
        try:
          carray[i][j] = (avg[1]/avg[0])*100
        except ZeroDivisionError:
          carray[i][j] = 0.0
  return darray,sdarray,carray

def wim():
  # IMPORTS
  from memops.general.Io import loadXmlProjectFile
  from ccpnmr.format.converters.CnsFormat import CnsFormat
  # LOAD PROJECT
  project = loadXmlProjectFile('.','/home/snabuurs/projects/ccpnmr/example.xml')
  # GET THE SEQUENCE
  # TAKE FIRST MOLSYSTEM
  molSys = project.molSystems[0]
  chainDict = {}
  # TAKE ALL CHAINS
  for chain in molSys.chains:
    chainDict[chain.code] = []
    for residue in chain.residues:
      chainDict[chain.code].append(residue.molResidue.ccpCode)
  format = CnsFormat(project)
  # TAKE FIRST STRUCTURE GENERATION
  strucGen = project.structureGenerations[0]
  # CYCLE RESTRAINTLIST
  for cslist in strucGen.constraintLists:
    # HANDLE DISTANCE RESTRAINTS
    constraintType,constrainttype = 'distance','DIST'
    # DO THE CONVERSION
    format.writeConstraints(fileName ='',
                            constraintList = cslist,
                            constraintType = constraintType,
                            minimalPrompts = 1,
                            noWrite = 1,
                            compressResonances = 1 )
  # CYCLE THE CONSTRAINTS
  for constraint in format.constraintFile.constraints:
    # DEFINE RESTRAINTS
    r = nmr_restraint(type=constrainttype)
    r.target = constraint.targetDist
    r.lowerb = constraint.targetDist - constraint.minusDist
    r.upperb = constraint.targetDist + constraint.plusDist
    for item in constraint.items:
      members = item.members
      for i in range(2):
        r.data[i]["RESI"].append(members[i].seqCode)
        if members[i].chainCode != ' ':
          r.data[i]["SEGI"].append(members[i].chainCode)
        r.data[i]["NAME"].append(members[i].atomName)
      print "++++++++++++++++++++++++++++++++++++"
      print r.format("XPLOR")
  # HANDLE DIHEDRAL ANGLE RESTRAINTS
  if cslist.className == 'DihedralConstraintList':
    constraintType,constrainttype = 'dihedral','DIHE'
    # DO THE CONVERSION
    format.writeConstraints(fileName ='',
                            constraintList = cslist,
                            constraintType = constraintType,
                            minimalPrompts = 1,
                            noWrite = 1,
                            compressResonances = 1 )
    # CYCLE THE CONSTRAINTS
    for constraint in format.constraintFile.constraints:
      # DEFINE RESTRAINTS
      r = nmr_restraint(type=constrainttype)
      r.angle = constraint.targetAngle
      r.range = constraint.devAngle
      # CYCLE ITEMS IN THE CONSTRAINT
      for item in constraint.items:
        members = item.members
        for i in range(4):
          r.data[i]["RESI"].append(members[i].seqCode)
          if members[i].chainCode != ' ':
            r.data[i]["SEGI"].append(members[i].chainCode)
          r.data[i]["NAME"].append(members[i].atomName)
        print r.format("XPLOR")


# ======================================================================
#                          T E M P
# ======================================================================

def nmv_temp():
  # DO A DRESS RUN FOR CHRISSY
  dress_input = '/mnt/homec/staf/cspronk/dress/dress'
  dress2_path = '/mnt/homec/staf/snabuurs/projects/refinement_validation'
  datapath    = '/mnt/homec/staf/snabuurs/projects/dress_db'
  skiplist = ['1ezo','1eza']
  # BUILD PROJECTLIST
  dirlist = glob.glob(os.path.join(dress_input,"*"))
  idlist  = []
  for dir in dirlist:
    if os.path.isdir(dir):
      id = os.path.basename(dir)
      if os.path.exists(os.path.join(datapath,id)) and id not in skiplist:
        idlist.append(os.path.basename(dir))
  # CYCLE THE ID'S
  for id in idlist:
    print "Processing entry %s."%id.upper()
    ori_pdb = os.path.join(datapath,"%s/data/sequence/protein.pdb"%id)
    ori_psf = os.path.join(datapath,"%s/data/sequence/protein.psf"%id)
    res_tgz = os.path.join(dress_input,"%s/%s_restraints.tgz"%(id,id))
    # CREATE NEW QUEEN PROJECTS
    qnpath  = os.path.join(dress2_path,id)
    if not os.path.exists(qnpath):
      qn_createproject(nmvconf,id,projectpath=dress2_path)
    # SET UP PROJECT
    queen=qn_setup(nmvconf,id,projectpath=dress2_path)
    # SET UP XPLOR
    xplr = qn_setupxplor(nmvconf,id,projectpath=dress2_path)
    # COPY THE PDB FILE
    if not os.path.exists(xplr.template):
      shutil.copy(ori_pdb,xplr.template)
    # CREATE PSF FILE
    if not os.path.exists(xplr.psf):
      shutil.copy(ori_psf,xplr.psf)
    # OPEN TARFILE AND EXTRACT IT
    tf = tarfile.open(res_tgz,"r:gz")
    for tarinfo in tf:
      tf.extract(tarinfo,path=os.path.join(queen.path,'data'))
    tf.close()

    # THE INPUT RESTRAINTS
    rfiles = ['noe_clean','hbonds_clean']
    rlist = []
    for rfile in rfiles:
      rpath = nmv_adjust(queen.table,rfile)
      if os.path.exists(rpath):
        r = restraint_file(rpath,'r')
        r.read()
        rlist += copy.copy(r.restraintlist)
        print "Read %04i restraints."%(len(r.restraintlist))
    print "Read %04i restraints in total."%(len(rlist))
    # CALCULATING INFORMATION CONTEN
    unc_ini = queen.uncertainty(xplr,[])
    unc_all = queen.uncertainty(xplr,rlist)
    inf_all = unc_ini-unc_all
    print "Initial uncertainty: %8e bits/atom2."%unc_ini
    print "  Final uncertainty: %8e bits/atom2."%unc_all
    print "Information content: %8e bits/atom2."%inf_all
    # GENERATE RANDOM SET WITH GIVEN INFO
    for content in [90.,95.]:
      rfile_cal = nmv_adjust(queen.table,"dist_%03i_cal"%int(content))
      rfile_val = nmv_adjust(queen.table,"dist_%03i_val"%int(content))
      if not os.path.exists(rfile_cal):
        # CALCULATE THE PARTITIONING
        myset = qn_generatedataset(queen,xplr,rlist,content,maxerr=1.,nsets=1)[0]
        print "Final set:"
        print "%04i restraints (%8e)"%(len(myset['restraints']),myset['info'])
        # WRITE RESTRAINT TO FILE
        rfile = restraint_file(rfile_cal,'w')
        rfile.comment("Restraint file for validation of water refinements.")
        rfile.comment("This file contains the 'calculation' set.")
        rfile.comment("Information target value   = %6.2f %%"%myset['target'])
        rfile.comment("Actual information content = %6.2f %%"%myset['info'])
        rfile.comment("Generated using QUEEN")
        rfile.mwrite(myset['restraints'])
        rfile.close()
        # BUILD REMAINING SET
        remaining = []
        for el in rlist:
          if el not in myset['restraints']:
            remaining.append(el)
        print "Remaining set:"
        print "%04i restraints"%(len(remaining))
        # WRITE RESTRAINT TO FILE
        rfile = restraint_file(rfile_val,'w')
        rfile.comment("Restraint file for validation of water refinements.")
        rfile.comment("This file contains the 'validation' set.")
        # SOME SANITY CHECKING
        unc_val   = queen.uncertainty(xplr,remaining)
        inf_val   = unc_ini-unc_val
        score_val = (inf_val/inf_all)*100
        rfile.comment("Information content        = %6.2f %%"%(score_val))
        rfile.comment("Generated using QUEEN")
        rfile.mwrite(remaining)
        rfile.close()
  return



  nmv_analyzestructuralgenomics()
  shutil.copy('/projects/structuralgenomics/labd.dic',
              '/projects/nonstructuralgenomics/labd.dic')
  nmv_analyzenonstructuralgenomics()
  raise SystemExit
  for pdb in ['3gb1','1h95','1d3z','1ozi','1h7d']:
    pdbl = glob.glob('/home/snabuurs/tmp/tmp/%s/pdb%s_*.ent'%(pdb,pdb))
    pdbl = pdbl[:20]
    base = '/home/snabuurs/tmp/tmp/%s'%pdb
    pdb_plotchecks(pdbl,['Backbone'],base)
  raise SystemExit
  for pdb in ['1x9l','1x7l','1ozi','1q7x']:
    pdbl = glob.glob('/home/snabuurs/tmp/tmp/%s/pdb%s_*.ent'%(pdb,pdb))
    pdbl = pdbl[:20]
    base = '/home/snabuurs/tmp/tmp/%s'%pdb
    pdb_plotchecks(pdbl,['Backbone'],base)
  raise SystemExit
  rdctbl = '/home/snabuurs/1ozi/hn_1ozi.tbl'
  rdcf   = restraint_file(rdctbl,'r',type='DIPO',Daxi=-5.055,Drho=-0.26)
  rdcf.read()
  #for set in ['1q7x','1ozi']:
  for set in ['1ozi','1q7x']:
    psf  = '/storage/projects/queen/%s/data/sequence/protein.psf'%set
    if set == '1ozi':
      pdbl = glob.glob('/projects/queen/%s/pdb/n_all_*.pdb'%(set))
    else:
      pdbl = glob.glob('/home/snabuurs/1ozi/%s/%s_*.pdb'%(set,set))
    rl = []
    for pdbf in pdbl:
      r = xplor_qfactor(pdbf,psf,rdcf.restraintlist)
      rl.append(r)
      #print "%7.3f - %s"%(r,os.path.basename(pdbf))
    print set, avg_list(rl)
  raise SystemExit
  nmv_infovsquality(projectname='1tgq',dataset='noe2',
                    adjustdata=False,
                    reference='/projects/pdbblunder/1tgq/pdb/1tgq_ensemble_ref_simset_001.pdb')
  #nmv_infovsquality(projectname='1tgq',dataset='noe',
  #                  adjustdata=False,
  #                  reference='/projects/pdbblunder/1tgq/pdb/1tgq_ensemble_ref_simset_001.pdb')
  raise SystemExit
  # SUMMARIZE DRESS
  path     = '/storage/data/dress_040705'
  pdbpaths = glob.glob(os.path.join(path,'1*'))
  valf     = os.path.join(path,'vald.dic')
  # CHECKS
  checks = ['PhiPsi','Backbone','Chi1Chi2','Packing2']
  # CYCLE PROJECTS
  for pdbpath in pdbpaths:
    # READ VALIDATION DICT
    if not os.path.exists(valf): vald = {}
    else:
      file = open(valf,"r")
      vald = cPickle.load(file)
      file.close()
    # CONSTRUCT PATHS
    pdb    = os.path.basename(pdbpath)
    oripdb = os.path.join(pdbpath,'%s_original.pdb'%pdb)
    refpdb = os.path.join(pdbpath,'%s_refined.pdb'%pdb)
    if pdb not in vald.keys():
      # BUILD SUMMARY FILES
      checkd = pdb_check_global(oripdb,checks)
      vald[pdb] = {}
      vald[pdb]['ori'] = checkd
      checkd = pdb_check_global(refpdb,checks)
      vald[pdb]['ref'] = checkd
      # STORE VALIDATION DICT
      file = open(valf,"w")
      cPickle.dump(vald,file)
      file.close()
  # CALCULATE AVERAGES
  file = open(valf,"r")
  vald = cPickle.load(file)
  file.close()
  # CYCLE THE CHECKS
  for check in checks:
    refl, oril = [],[]
    for pdb in vald.keys():
      oril.append(avg_list(vald[pdb]['ori'][check],sdflag=0))
      refl.append(avg_list(vald[pdb]['ref'][check],sdflag=0))
    avgr = avg_list(refl)
    avgo = avg_list(oril)
    print "%10s    %6.3f +/-%6.3f    %6.3f +/-%6.3f"%(check,avgo[0],avgo[1],
                                                    avgr[0],avgr[1])
  raise SystemExit
  nmv_infovsquality(projectname='1tgq',dataset='noe',
                    adjustdata=False,reference='/projects/pdbblunder/1tgq/pdb/1tgq_ensemble_ref_simset_001.pdb')
  raise SystemExit
  content = open('crystal.list','r').readlines()
  cncpath = '/projects/cnctest/'
  for line in content:
    path = line.strip()
    name = os.path.basename(path)
    print name
    if os.path.exists(os.path.join(path,'data')):
      shutil.copytree(path,os.path.join(cncpath,name))
      shutil.copy('noe.list',os.path.join(cncpath,'%s/data/datasets/'%name))
  raise SystemExit
##  xplor_renumberpsf('/storage/projects/pdbblunder/1tgq/data/sequence/protein.psf.prenum',
##                    '/storage/projects/pdbblunder/1tgq/data/sequence/protein.psf',
##                    '/storage/projects/pdbblunder/1tgq/pdb/1tgq_ensemble_001.pdb',
##                    0)
##  raise SystemExit
  nmvconf["Q_PROJECT"] = '/projects/pdbblunder'
  projectname = '1tgq'
  dataset     = 'simset'
  queen = qn_setup(nmvconf,projectname)
  xplr  = qn_setupxplor(nmvconf,projectname)
  data = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
  restraints = data["data"] + data["bckg"]
  pdblist = glob.glob(os.path.join(queen.pdb,'*%s*-20'%dataset))
  fname = '1tgq_trial.txt'
  xplor_violanalysis(pdblist,
                     xplr.psf,
                     restraints,
                     outputfile=fname)
  raise SystemExit

  nmv_infovsquality(projectname='1h95',adjustdata=False)
  nmv_infovsquality(projectname='1ozi',adjustdata=False)
  nmv_infovsquality(projectname='1h7d',adjustdata=False)
  #nmv_infovsquality(projectname='3gb1',adjustdata=True,reference='/pdb/pdb1pgb.ent')
  nmv_infovsquality(projectname='3gb1',adjustdata=False)
  nmv_infovsquality(projectname='1d3z',adjustdata=False)
  #nmv_infovsquality(projectname='1d3z',adjustdata=True,reference='/pdb/pdb1ubq.ent')
  #nmv_infovsquality(projectname='3gb1',dataset='distancedata',adjustdata=False)
  raise SystemExit

  for set in ['cnc5','cns','xpl']:#,'cnc5w','xplw','cnsw']:
    pdblist  = glob.glob('/storage/projects/concoord/3gb1/pdb/%s_*.pdb'%set)
    intbl    = '/storage/projects/concoord/3gb1/data/restraints/noe_LR.tbl'
    refpdb   = '/storage/projects/concoord/3gb1/pdb/xray_001.pdb'
    plotfile = '3gb1_dist_%s.dat'%set
    rfile_plotbounds(intbl,plotfile,pdblist,refpdb,normalize=2)
  raise SystemExit
##  tblpath = '/storage/projects/concoord/1beg/data/restraints'
##  intbl = os.path.join(tblpath,'unambig.tbl')
##  tbl1 = os.path.join(tblpath,'hbonds.tbl')
##  tbl2 = os.path.join(tblpath,'noe.tbl')
##  r = restraint_file(intbl,'r')
##  r.read()
##  hb, noe = r_extracthbonds(r.restraintlist)
##  r.close()
##  r1 = restraint_file(tbl1,'w')
##  r1.mwrite(hb)
##  r1.close()
##  r1 = restraint_file(tbl2,'w')
##  r1.mwrite(noe)
##  r1.close()
##  raise SystemExit
  #projectlist = glob.glob('/storage/data/db_dress/*')
  #for project in projectlist:
  #  project = os.path.basename(project)
  #  print project
  #  nmv_dressproject(project,'all')
  #for set in ['1y4o','1tgq']:
  #  pdblist = glob.glob('/storage/projects/queen/%s/pdb/original_*.pdb'%set)
  #  checklist = ['Phipsi','Backbone','Bumps','Packing1']
  #  base = set
  #  pdb_plotchecks(pdblist,checklist,base)
  #raise SystemExit

  # HANDLE PDBBLUNDERS
  # ==================
  # GROUP ORIGINAL RESTRAINTS
  for set in ['noe','hbonds']:
    infile  = '/projects/queen/1y4o/data/restraints/complete/%s.tbl'%set
    outfile = '/projects/queen/1y4o/data/restraints/%s_XX.tbl'%set
    Alist, Blist, ABlist = [], [], []
    # READ RESTRAINTS
    fin = restraint_file(infile,'r')
    fin.read()
    fin.close()
    # CYCLE RESTRAINTS
    for r in fin.restraintlist:
      A, B = 0, 0
      # SET TYPE
      for i in range(2):
        n = r.data[i]["RESI"]
        for el in n:
          el = int(el)
          if el < 200: A = 1
          elif el > 200: B = 1
      if A and B: ABlist.append(r)
      elif A and not B: Alist.append(r)
      elif B and not A: Blist.append(r)
    # WRITE OUTPUT
    fou = restraint_file(outfile.replace('XX','A'),'w')
    fou.mwrite(Alist)
    fou.close()
    fou = restraint_file(outfile.replace('XX','B'),'w')
    fou.mwrite(Blist)
    fou.close()
    fou = restraint_file(outfile.replace('XX','AB'),'w')
    fou.mwrite(ABlist)
    fou.close()
  # MERGE INTERMOLECULAR RESTRAINTS
  for set in ['noe','hbonds']:
    infile  = '/projects/queen/1y4o/data/restraints/%s_AB.tbl'%set
    outfile = '/projects/queen/1y4o/data/restraints/%s_AB_merge.tbl'%set
    # READ RESTRAINTS
    fin = restraint_file(infile,'r')
    fin.read()
    fin.close()
    # CYCLE RESTRAINTS
    merged = []
    for r in fin.restraintlist:
      # SET TYPE
      for i in range(2):
        n = r.data[i]["RESI"]
        new = []
        for el in n:
          el = int(el)
          if el > 200: el = el - 200
          new.append(el)
        r.data[i]["RESI"] = new
      merged.append(r)
    # WRITE OUTPUT
    fou = restraint_file(outfile,'w')
    fou.mwrite(merged)
    fou.close()
  raise SystemExit




  #nmv_infovsquality(projectname='1h7d',adjustdata=False)
  #raise SystemExit
  nmv_infovsquality(projectname='1d3z',adjustdata=False,
                    reference='/pdb/pdb1ubq.ent')
  raise SystemExit
  #nmv_infovsquality(projectname='3gb1',adjustdata=True,
  #                  reference='/pdb/pdb1pgb.ent')
  #nmv_analyzeHstructure()
  raise SystemExit

  #nmv_infovsquality(projectname='3gb1',adjustdata=False,reference='/pdb/pdb1pgb.ent')
  raise SystemExit
  nmv_createpdbpics('/home/snabuurs/pdbpics')
  raise SystemExit

##  list = glob.glob('/storage/projects/concoord/3gb1/pdb/xpl_*.fit')
##  yas_rmsdcolensemble(nmvconf["YASARA_RUN"],
##                      list,refval=1.55,fitflag=0)
##  raise SystemExit
##  p = '3gb1'
##  dataset = 'noe'
##  queen = qn_setup(nmvconf,p)
##  xplr  = qn_setupxplor(nmvconf,p)
##  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
##  data = qn_readdatasets(queen,datasets)
##  restraintlist = data['data']
##  outtbl = '/home/snabuurs/projects/queen/3gb1/data/restraints/noe.cnc'
##  cnc_writeconcoord(xplr.psf,xplr.template,restraintlist,outtbl)
##  raise SystemExit
##  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
##  data = qn_readdatasets(queen,datasets)
##  restraintlist = data['data']
##  pdbbase = os.path.join(queen.pdb,'xplnih')
##  anneald = xplornih_anneal(pdbbase,
##                            xplr.template,
##                            xplr.psf,
##                            restraintlist,
##                            naccepted=10,
##                            thr_noe=0.5,
##                            thr_dih=5.,
##                            ntrial=5)
##  if myid==0:
##    viol = os.path.join(queen.pdb,'viol.txt')
##    if len(anneald)>0:
##      xplor_violanalysis(anneald,
##                         xplr.psf,
##                         restraintlist,
##                         outputfile=viol)
##    failed = glob.glob(os.path.join(queen.pdb,'trial*pdb'))
##    if len(failed)>0:
##      viol = os.path.join(queen.pdb,'trial.txt')
##      xplor_violanalysis(failed,
##                         xplr.psf,
##                         restraintlist,
##                         outputfile=viol)


  #mtf = "%s.mtf"%xplr.psf[:-4]
  #if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
  # calculate
  #cns_calcstructure(pdbbase,
  #                  xplr.template,
  #                  mtf,
  #                  restraintlist,
  #                  thr_noe=5,
  #                  naccepted=20)
  #pdblist = glob.glob(os.path.join(queen.pdb,'cns_a_*.pdb'))
  #for el in pdblist:
  #  outpdb = el+'w'
  #  xplor_refstruct(el,outpdb,xplr.psf,restraintlist,thr_noe=0.5)
  #pdblist = glob.glob(os.path.join(queen.pdb,'cns_a_*.pdbw'))
  #output  = os.path.join(queen.pdb,'viol_wref.txt')
  #xplor_violanalysis(pdblist,xplr.psf,restraintlist,output)
  #raise SystemExit

##  pdblist = glob.glob('/home/snabuurs/projects/concoord/3gb1/pdb/cnc_*.pdb')
##  fitlist = prft_superimpose(pdblist,overwrite=0)
##  mtx1 = wif_rmsdmtx(fitlist)
##  for row in mtx1:
##    for el in row:
##      print "%5.2f"%el,
##    print
##  mtx2 = yas_rmsdmtx(nmvconf["YASARA_RUN"],fitlist,['CA'],fitflag=0)
##  for row in mtx2:
##    for el in row:
##      print "%5.2f"%el,
##    print
##  raise SystemExit
##  p = '3gb1'
##  dataset     = 'distancedata'
##  queen = qn_setup(nmvconf,p)
##  xplr = qn_setupxplor(nmvconf,p)
##  # CALCULATE 100 3gb1 structures with NOE only
##  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
##  data = qn_readdatasets(queen,datasets)
##  restraintlist = data['data']
##  pdbbase = os.path.join(queen.pdb,'anneal_01_cns')
##  mtf = "%s.mtf"%xplr.psf[:-4]
##  if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
##  # calculate
##  cns_calcstructure(pdbbase,
##                    xplr.template,
##                    mtf,
##                    restraintlist,
##                    thr_noe=0.1,
##                    naccepted=100)
##  raise SystemExit

##  #nmv_infovsquality(projectname='1d3z',adjustdata=False,pdbf='/pdb/pdb1ubq.ent')

#  --------------
##  projectname = '3gb1'
##  dataset     = 'dipo_tabacco'
##  queen       = qn_setup(nmvconf,projectname)
##  xplr        = qn_setupxplor(nmvconf,projectname)
##  data        = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
##  restraints  = data["data"] + data["bckg"]
##  d = {}
##  for i in range(70,101,5):
##    d[i]=d.get(i,{})
##    d[i]['ref']=d[i].get('ref',[])
##    d[i]['ori']=d[i].get('ori',[])
##    for j in range(1,5):
##      for k in range(1,11):
##        pdbl  = glob.glob(os.path.join(queen.pdb,
##                                       'info_%05.1f_%i_a_%i.pdb'%(i,j,k)))
##        refl  = glob.glob(os.path.join(queen.pdb,
##                                       'ref_info_%05.1f_%i_a_%i.pdb'%(i,j,k)))
##        for l in range(len(pdbl)):
##          q1 = xplor_qfactor(pdbl[l],xplr.psf,restraints)
##          d[i]['ori'].append(q1)
##          q2 = xplor_qfactor(refl[l],xplr.psf,restraints)
##          d[i]['ref'].append(q2)
##          if q2<=q1: flag = '+'
##          else: flag = '-'
##          print "%5.2f %5.2f %s %25s %25s"%(q1,q2,flag,
##                                            os.path.basename(pdbl[l]),
##                                            os.path.basename(refl[l]))
##  xmgr = graceplot('%s.dat'%dataset,'xydy','w')
##  xmgr.xlab = "Information"
##  xmgr.ylab = "R-factor"
##  xmgr.writeheader()
##  for i in range(70,101,5):
##    print "Set %03i."%i
##    avg = avg_list(d[i]['ori'])
##    print "ORI: %5.2f +/- %5.2f"%(avg[0],avg[1])
##    xmgr.write([i,avg[0],avg[1]])
##  xmgr.newset()
##  for i in range(70,101,5):
##    print "Set %03i."%i
##    avg = avg_list(d[i]['ref'])
##    print "REF: %5.2f +/- %5.2f"%(avg[0],avg[1])
##    xmgr.write([i,avg[0],avg[1]])
##  xmgr.close()
##  raise SystemExit

  ppath = '/script/concoord-nmr/'
  outputpath = os.path.join(ppath,'output')
  # CALCULATE QUEEN UNCERTAINTY
  projectname = '3gb1'
  dataset = 'distancedata'
  queen   = qn_setup(nmvconf,projectname)
  xplr    = qn_setupxplor(nmvconf,projectname)
  upr     = qn_uncperresidue(queen,xplr,dataset)
  data         = qn_readdata(queen,nmv_adjust(queen.dataset,dataset))
  drestraints  = data["data"] + data["bckg"]
  # REFINE STRUCTURES
  print "Refining structures."
  for sname in ['margin_1-4','margin_nb']:
    plist = glob.glob(os.path.join(ppath,'%s*'%sname))
    for el in plist:
      pdbsel = os.path.join(el,'CONCOORD_EM/refined/*.pdb')
      pdblist = glob.glob(pdbsel)
      print "Refining:"
      for pdb in pdblist:
        outpdb = pdb+'w'
        if not os.path.exists(outpdb):
          print "%s"%outpdb
          xplor_refstruct(pdb,outpdb,xplr.psf+'zut',drestraints,
                          mdheat=10,mdhot=100,mdcool=10)
  # READ DIPOS
  rdcdata     = 'dipo_bicelle'
  data        = qn_readdata(queen,nmv_adjust(queen.dataset,rdcdata))
  restraints  = data["data"] + data["bckg"]
  print "Read %i DIPOs"%len(restraints)
  # STORE UNCERTAINTY IN A LIST
  ulist = []
  xmgr = graceplot(os.path.join(outputpath,'unc.dat'),'xy','w')
  xmgr.xlab = "Residue number"
  xmgr.ylab = "Uncertainty"
  xmgr.writeheader()
  for c in upr.keys():
    residues = upr[c].keys()
    residues.sort(lambda r1,r2: cmp(r1.number,r2.number))
    for residue in residues:
      val = upr[c][residue]
      ulist.append(val)
      xmgr.write([residue.number,val])
  xmgr.close()
  # READ CHEMICAL SHIFTS
  csfile      = '/home/snabuurs/python/nmr_valibase/1gb1.cs'
  content = open(csfile,'r').readlines()
  cnt, cs = 1, {}
  for line in content:
    try:
      cs_n  = float(line[8:13])
      cs_hn = float(line[16:21])
    except:
      cs_n, cs_hn = 99, 99
    cs[cnt]=cs.get(cnt,{})
    cs[cnt]['N']  = cs_n
    cs[cnt]['H'] = cs_hn
    cnt += 1
  # CALCULATE CS CORRELATIONS
  shft = shiftx(nmvconf['SHIFTX_RUN'])
  for nuc in []: #['N','H']:
    for sname in ['cns_anneal']: #['margin_1-4','margin_nb','xpl_anneal']:
      cscc = {}
      # BUILD LIST OF PDB FILES
      plist = glob.glob(os.path.join(ppath,'%s*'%sname))
      for el in plist:
        val = el.split('_')[-1]
        cclist = []
        # BUILD LIST OF PDB FILES
        pdbsel = os.path.join(el,'CONCOORD_EM/refined/*.pdb')
        pdblist = glob.glob(pdbsel)
        for pdb in pdblist:
          shft.predict(pdb)
          lpred = shft.nuclei[nuc]
          lmeas = []
          for key in cs.keys(): lmeas.append(cs[key][nuc])
          #lpred = [el for el in lpred if lmeas[lpred.index(el)]!=99]
          #lmeas = [float(el) for el in lmeas if el !=99]
          lpred = lpred[1:]
          lmeas = lmeas[1:]
          if len(lmeas)==len(lpred):
            cc = list_cc(lmeas,lpred)
          else:
            print "List mismatch!", len(lmeas), len(lpred)
          print "%5.2f %5s %s"%(cc*100,val,os.path.basename(pdb))
          cclist.append(cc)
        cscc[val]=avg_list(cclist)
      # SORT THE VALUE LIST
      vlist = cscc.keys()
      vlist.sort()
      # WRITE A PLOT
      xmgr = graceplot(os.path.join(outputpath,'csfit_%s_%s.dat'%(sname,nuc)),'xydy','w')
      xmgr.writeheader()
      for el in vlist:
        dat = [float(el),cscc[el][0],cscc[el][1]]
        xmgr.write(dat)
      par = os.path.join(outputpath,'parameters/csfit_%s.par'%sname)
      xmgr.output(parameter=par)
      xmgr.close()

  # CALCULATE DIPO SCORES
  for sname in ['margin_1-4','margin_nb']: #['margin_1-4','margin_nb','xpl_anneal','cns_anneal']:
    # BUILD LIST OF PDB FILES
    plist = glob.glob(os.path.join(ppath,'%s*'%sname))
    rd = {}
    for el in plist:
      val = el.split('_')[-1]
      # BUILD LIST OF PDB FILES
      pdbsel = os.path.join(el,'CONCOORD_EM/refined/*.pdbw')
      pdblist = glob.glob(pdbsel)
      for pdb in pdblist:
        if sname == 'cns_anneal':
          r = xplor_qfactor(pdb,xplr.psf,restraints)
        else:
          r = xplor_qfactor(pdb,xplr.psf+'zut',restraints)
        print "%5.2f %s"%(r,os.path.basename(el))
        rd[val] = rd.get(val,[])+[r]
    # SORT THE VALUE LIST
    vlist = rd.keys()
    vlist.sort()
    # WRITE A PLOT
    xmgr = graceplot(os.path.join(outputpath,'rfactor_%s_%s_w.dat'%(sname,rdcdata)),'xydy','w')
    xmgr.writeheader()
    for el in vlist:
      avg = avg_list(rd[el])
      dat = [float(el),avg[0],avg[1]]
      xmgr.write(dat)
    par = os.path.join(outputpath,'parameters/rfactor_%s.par'%sname)
    xmgr.output(parameter=par)
    xmgr.close()

  # CALCULATE RAMA Z-SCORE
  for sname in []: #['margin_1-4','margin_nb']: #['xpl_anneal','cns_anneal']:
    # BUILD LIST OF PDB FILES
    plist = glob.glob(os.path.join(ppath,'%s*'%sname))
    rama = {}
    for el in plist:
      val = el.split('_')[-1]
      # BUILD LIST OF PDB FILES
      pdbsel = os.path.join(el,'CONCOORD_EM/refined/*.pdb')
      pdblist = glob.glob(pdbsel)
      for pdb in pdblist:
        z = pdb_getramazscore(nmvconf["WHATIF_RUN"],pdb)
        print "%5.2f %s"%(z,os.path.basename(el))
        rama[val] = rama.get(val,[])+[z]
    # SORT THE VALUE LIST
    vlist = rama.keys()
    vlist.sort()
    # WRITE A PLOT
    xmgr = graceplot(os.path.join(outputpath,'rama_%s.dat'%(sname)),'xydy','w')
    xmgr.ylab = "Ramachandran plot Z-score."
    xmgr.writeheader()
    for el in vlist:
      avg = avg_list(rama[el])
      dat = [float(el),avg[0],avg[1]]
      xmgr.write(dat)
    #par = os.path.join(outputpath,'parameters/rama_%s.par'%sname)
    #xmgr.output(parameter=par)
    xmgr.close()

  # CALCULATE BUMP SCORES
  for sname in ['margin_1-4','margin_nb']: #,'xpl_anneal','cns_anneal']:
    # BUILD LIST OF PDB FILES
    plist = glob.glob(os.path.join(ppath,'%s*'%sname))
    bumps = {}
    for el in plist:
      val = el.split('_')[-1]
      # BUILD LIST OF PDB FILES
      pdbsel = os.path.join(el,'CONCOORD_EM/refined/*.pdbw')
      pdblist = glob.glob(pdbsel)
      for pdb in pdblist:
        b100 = pdb_getnobumpsper100(nmvconf["WHATIF_RUN"],pdb)
        print "%5.2f %s"%(b100,os.path.basename(el))
        bumps[val] = bumps.get(val,[])+[b100]
    # SORT THE VALUE LIST
    vlist = bumps.keys()
    vlist.sort()
    # WRITE A PLOT
    xmgr = graceplot(os.path.join(outputpath,'bumps_%s_w.dat'%(sname)),'xydy','w')
    xmgr.writeheader()
    for el in vlist:
      avg = avg_list(bumps[el])
      dat = [float(el),avg[0],avg[1]]
      xmgr.write(dat)
    par = os.path.join(outputpath,'parameters/bumps_%s.par'%sname)
    xmgr.output(parameter=par)
    xmgr.close()

  # DETERMINE RMSD VERSUS UNCERTAINTY AND RADIUS OF GYRATION PLOTS
  for sname in ['margin_1-4','margin_nb']: #,'cns_anneal','xpl_anneal']: #'verfijnd','annealed'
    # BUILD LIST OF PDB FILES
    plist = glob.glob(os.path.join(ppath,'%s*'%sname))
    # DATA DICTIONARY
    data = {}
    for el in plist:
      print el
      val = el.split('_')[-1]
      data[val] = {}
      # BUILD LIST OF PDB FILES
      pdbsel = os.path.join(el,'CONCOORD_EM/refined/*.pdbw')
      pdblist = glob.glob(pdbsel)
      fitsel = os.path.join(el,'CONCOORD_EM/refined/*.fitw')
      fitlist = glob.glob(fitsel)
      # CALCULATE RMSDS
      #rmsds = prft_rmsd_perres(pdblist,selection='bb')
      if len(fitlist)!=len(pdblist):
        fitlist = prft_superimpose(pdblist,overwrite=0)
      # BUILD RMSD MTX
      rmsdmtxlist = yas_rmsdmtxfast(nmvconf["YASARA_RUN"],fitlist,['CA','N','C'],
                                    unit='Res',fitflag=0)
      # DETERMINE NUMBER OF RESIDUES
      pdbf = pdb_file.Structure(pdblist[0])
      nres = 0
      for chain in pdbf.peptide_chains: nres += len(chain)
      rmsds = []
      for r in range(nres):
        rmsdmtx = rmsdmtxlist[r]
        rmsdlist = []
        for i in range(len(pdblist)):
          del rmsdmtx[i][i]
          rmsdlist.append(avg_list(rmsdmtx[i],sdflag=0))
        avg = avg_list(rmsdlist)
        rmsds.append(avg[0])
      # WRAP UP
      print list_cc(rmsds,ulist)
      data[val]['rmsds']=rmsds
      xmgr = graceplot(os.path.join(outputpath,'rmsd-unc_%s_%04.2f_w.dat'%(sname,float(val))),'xy','w')
      xmgr.square=1
      xmgr.xlab = "Uncertainty"
      xmgr.ylab = "RMSD"
      xmgr.title = "%s - %s - cc: %04.2f"%(sname,val,list_cc(ulist,rmsds))
      xmgr.writeheader()
      for i in range(len(rmsds)):
        xmgr.write([ulist[i],rmsds[i]])
      par = os.path.join(outputpath,'parameters/rmsdunc.par')
      xmgr.output(parameter=par)
      xmgr.close()
      # CALCULATE RADIUS OF GYRATION
      rg = pdb_radiusofgyration(pdblist,getratio=1)
      data[val]['rg'] = rg
    # SORT THE VALUE LIST
    vlist = data.keys()
    vlist.sort()
    # WRITE A PLOT FOR THE RMSD TRENDS
    xmgr = graceplot(os.path.join(outputpath,'rmsd_%s_w.dat'%sname),'xydy','w')
    xmgr.ylab = "Backbone RMSD (A)"
    xmgr.writeheader()
    for el in vlist:
      avg = avg_list(data[el]['rmsds'])
      dat = [float(el),avg[0],avg[1]]
      xmgr.write(dat)
    par = os.path.join(outputpath,'parameters/rmsd_%s.par'%sname)
    xmgr.output(parameter=par)
    xmgr.close()
    # WRITE A PLOT FOR RMSD-UNC CORRELATION
    xmgr = graceplot(os.path.join(outputpath,'cc-rmsd-unc_%s_w.dat'%sname),'xy','w')
    xmgr.ylab = "Correlation coefficient uncertainty-rmsd"
    xmgr.square = 1
    xmgr.writeheader()
    for el in vlist:
      cc = list_cc(ulist,data[el]['rmsds'])
      dat = [float(el),cc]
      xmgr.write(dat)
    par = os.path.join(outputpath,'parameters/cc_%s.par'%sname)
    xmgr.output(parameter=par)
    xmgr.close()
    # WRITE A PLOT FOR THE RADIUS OF GYRATION
    xmgr = graceplot(os.path.join(outputpath,'rg_%s_w.dat'%sname),'xydy','w')
    xmgr.ylab = "Radius of gyration (Angstrom)"
    xmgr.square = 1
    xmgr.writeheader()
    for el in vlist:
      dat = [float(el),data[el]['rg'][0],data[el]['rg'][1]]
      xmgr.write(dat)
    xmgr.close()
  raise SystemExit


# OTHER STUFF
#############
  pdblist = glob.glob('/home/snabuurs/secondary_data/dress/*')
  d = {}
  print len(pdblist)
  for entry in pdblist:
    pdbf = pdb_file.Structure(os.path.join(entry,'data/sequence/protein.pdb'))
    nres = len(pdbf.peptide_chains[0])
    d[nres]=d.get(nres,[])+[entry]
    print nres, entry
  list = d.keys()
  list.sort()
  for entry in list:
    print entry
    if int(entry)<50:
      for el in d[entry]:
        print el
  raise SystemExit
##  shft = shiftx(nmvconf["SHIFTX_RUN"])

##  shft.predict('/pdb/pdb1crn.ent')
##  for residue in shft.predictions:
##    print residue, shft.predictions[residue]['HA']
##  for atom in shft.nuclei:
##    print atom, avg_list(shft.nuclei[atom])
##  raise SystemExit
##  nmv_dressvsshiftx('/home/snabuurs/data/dress_05072004',
##                    'all',
##                    '/home/snabuurs/projects/dress_vs_shiftx')
##  raise SystemExit
  # REBUILD QUA FILES
  path = '/home/snabuurs/secondary_data/db_queen/'
  dirlist = glob.glob(os.path.join(path,'*'))
  for dir in dirlist:
    p = os.path.basename(dir)
    ens = os.path.join(dir,'pdb/%s_ensemble.pdb'%p)
    qua = os.path.join(dir,'pdb/%s_ensemble.qua2'%p)
    if os.path.exists(ens) and not os.path.exists(qua):
      pdb_getqua(ens,qua,type='ascii')
  raise SystemExit
  nmv_testwheatsheaf('/home/snabuurs/secondary_data/db_queen/',
                     'all',
                     '/home/snabuurs/projects/wheatsheaf')
  raise SystemExit
##  # BUILD A LIST OF IDS
##  idlist = glob.glob('/home/snabuurs/secondary_data/db_queen/*')
##  # OUTPUT FILE
##  output = open('correlation_infovsqual_log.txt','a')
##  logdict = {}
##  # CURRENT SCORES
##  scores = [[],[],[],[],[]]
##  dumpfile = 'correlation_infovsqual.dump'
##  if os.path.exists(dumpfile):
##    dump = open(dumpfile,'r')
##    scores = cPickle.load(dump)
##    dump.close()
##  skiplist = ['1BZ9','1BPO','1QXP','1Q1S','1RB1','1EZO','1EZP']
##  # CYCLE IDS
##  for idpath in idlist:
##    id = os.path.basename(idpath)
##    print id
##    pdbf = '/home/snabuurs/secondary_data/db_queen/%s/pdb/%s_ensemble.pdb'%(id,id)
##    pdbq = "%s.qua"%(pdbf[:-4])
##    outf = '/home/snabuurs/tmp/plots/%s.dat'%id
##    if not os.path.exists(outf) and os.path.exists(pdbf) and id.upper() not in skiplist:
##      x = nmv_infovsqual(id,'all',pdbfile=pdbf,plotfile=outf)
##      # do not use pdbid as there is often a numbering mismatch!
##      #x = nmv_infovsqual(id,'all',pdbid=id,plotfile=outf)
##      output.write("%s\n"%id)
##      output.flush()
##      output.write("%s\n"%x)
##      for i in range(len(x)):
##        scores[i].append(x[i])
##        output.write("%3i %5.2f\n"%(i, avg_list(scores[i])[0]))
##        output.flush()
##        dump = open(dumpfile,'w')
##        cPickle.dump(scores,dump)
##        dump.close()
##  output.close()
##  raise SystemExit


##  pdbfinder = pdb_finder(nmvconf["PDBFINDER2"],'r',1,error)
##  pdbfinder.buildindex()
##  print '%i structures have been indexed.'%len(pdbfinder.recordpos.keys())
##  skiplist = ['1BZ9','1BPO','1QXP','1Q1S','1RB1','1EZO','1EZP']
##  for chyear in [2004]:
##    print "# %4i #"%chyear
##    print "#######"
##    structures = {}
##    # CYCLE STRUCTURES
##    for id in pdbfinder.recordpos.keys():
##      # FILTER PROBLEMATIC FILES
##      if id not in skiplist:
##        pdbfinder.read(id)
##        # EXTRACT YEAR
##        year = int(pdbfinder.fieldvalue(' Date')[0:4])
##        # ONLY chyear
##        if year == chyear:
##          # ONLY PROTEINS
##          if pdbfinder.peptidechains > 0 and pdbfinder.nucleotidechains == 0:
##            # NO HET GROUPS
##            if pdbfinder.fieldvalue("HET-Groups")==None:
##              # GET METHOD
##              method = pdbfinder.fieldvalue('Exp-Method')
##              if method in ['X','NMR']:
##                # STORE ID'S
##                structures[method]=structures.get(method,[]) + [id]
##    # EXTRACT QUALITY INDICATORS
##    quals = ['  Packing-1','  Packing-2','  Phi/psi','  Chi-1/chi-2']
##    qua = {}
##    okeelist = []
##    print structures.keys()
##    for method in structures:
##      for id in structures[method]:
##        pdbfinder.read(id)
##        # CHECK IF ALL QUALS ARE PRESENT
##        okidee = 1
##        for check in quals:
##          ch = pdbfinder.fieldvalue(check)
##          if ch==None: okidee = 0
##        # IF SO, CONTINUE
##        if okidee:
##          okeelist.append(id)
##          for qual in quals:
##            qua[method]=qua.get(method,{})
##            quastr = pdbfinder.fieldvalue(qual)
##            quaval = float(quastr.split('|')[1])
##            if qual=='  Packing-1':
##              quaval = quaval*10-5
##            elif qual=='  Packing-2':
##              quaval = quaval*6-3
##            elif qual=='  Phi/psi':
##              quaval = quaval*8-4
##            elif qual=='  Chi-1/chi-2':
##              quaval = quaval*8-4
##            qua[method][qual]=qua[method].get(qual,[])+[quaval]
##    # CALCULATE BUMPS AND BBC
##    scores = {}
##    scores['bumps']={}
##    scores['bbc']={}
##    dumpfile = 'run.dump'
##    if os.path.exists(dumpfile):
##      dump = open(dumpfile,'r')
##      scores = cPickle.load(dump)
##      dump.close()
##    quals.append('      Bumps')
##    quals.append('   Backbone')
##    print structures.keys()
##    for method in structures:
##      for id in structures[method]:
##        if id in okeelist and id not in scores['bumps'].keys():
##          pdbf = nmv_adjust(nmvconf["PDB"],id.lower())
##          scores['bumps'][id] = pdb_getnobumpsper100(nmvconf["WHATIF_RUN"],pdbf)
##          scores['bbc'][id] = pdb_getbbc(nmvconf["WHATIF_RUN"],pdbf)
##          dump = open(dumpfile,'w')
##          cPickle.dump(scores,dump)
##          dump.close()
##    # NOW ADD TO QUADICT
##    for method in structures:
##      qua[method]['      Bumps'] = []
##      qua[method]['   Backbone'] = []
##      for id in structures[method]:
##        if id in okeelist:
##          qua[method]['      Bumps'].append(scores['bumps'][id])
##          qua[method]['   Backbone'].append(scores['bbc'][id])
##    # PRINT RESULT
##    for method in structures:
##      print "METHOD %s: %i structures."%(method,len(structures[method]))
##    # PRINT AVERAGES
##    for method in qua:
##      print "METHOD: %s"%method
##      print len(structures[method])
##      for qual in quals:
##        print "  CHECK: %s"%qual
##        avg = avg_list(qua[method][qual])
##        print "    AVG: %5.2f +- %5.2f from %i entries from %s."%(avg[0],avg[1],
##                                                                  len(qua[method][qual]),
##                                                                  method)
##  raise SystemExit


##  unifile = '/home/snabuurs/projects/queen/1mo7/output/Iuni_all_ISML.dat'
##  unisort = '/home/snabuurs/projects/queen/1mo7/output/Iuni_all_ISML_sorted.tbl'
  p = '1gb1'
  dataset = 'all'
  # setup
  queen = qn_setup(nmvconf,p)
  xplr = qn_setupxplor(nmvconf,p)
  qn_bbuncperresidue(queen,xplr,'all')
  raise SystemExit
##  # READ DATAFILE
##  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
##  # CYCLE THE AVAILABE SETS
##  datadict = {}
##  rlist = []
##  for filedict in datasets:
##    table = nmv_adjust(queen.table,filedict["FILE"])
##    # READ THE RESTRAINT FILE
##    r = restraint_file(table,'r',type=filedict["TYPE"])
##    r.read()
##    # STORED RESTRAINTS FOR FUTURE USE
##    rlist += r.restraintlist
##    datadict[r.type] = datadict.get(r.type,[]) + r.restraintlist
##  # WE ONLY LOOK AT THE DISTANCE RESTRAINTS IN THIS STAGE
##  rdict = {}
##  for r in rlist:
##    rdict[str(r)]=r
##  # UNIQUE
##  umax = 0
##  comments = ['#','!','@']
##  udict,sumdict = {},{}
##  ufile = open(unifile,'r').readlines()
##  for line in ufile:
##    try:
##      if line[0] not in comments:
##        line=line.split()
##        key = float(line[1])
##        val = line[-1][1:-1]
##        udict[key]=udict.get(key,[])+[val]
##        umax = max(umax,key)
##    except IndexError:
##      pass
##  # WRITE SORTED UNIQUE
##  ukeylist = udict.keys()
##  ukeylist.sort()
##  ukeylist.reverse()
##  uni_r = restraint_file(unisort,'w')
##  for key in ukeylist:
##    for rstr in udict[key]:
##      sumdict[rstr]=sumdict.get(rstr,0)+key/umax
##      uni_r.comment("%e %% unique information"%key)
##      uni_r.write(rdict[rstr])
##  uni_r.close()
  # PROJECT
  p = '1ezo'
  dataset = 'all'
  # SETUP
  queen = qn_setup(nmvconf,p)
  xplr = qn_setupxplor(nmvconf,p)
  # PDBLIST
##  pdblist = yas_splitpdb2xplor(nmvconf["YASARA_RUN"],
##                               '/pdb/pdb%s.ent'%p,
##                               nmvconf["TMP"],
##                               p)
  pdblist = glob.glob('/home/snabuurs/secondary_data/db_queen/%s/pdb/%s_cns_*.pdb'%(p,p))
  # BUILD RESTRAINTLIST
  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
  data = qn_readdatasets(queen,datasets)
  rlist = data["data"] + data["bckg"]
  dslist = [el*0.1 for el in range(1,11)]
  dhlist = [el for el in range(2,22,2)]
  # RUN THE ANALYSIS SCRIPT
  xplor_violanalysis(pdblist,xplr.psf,rlist,'viol.txt',
                     cutoff={"DIST":dslist,
                             "DIHE":dhlist})

##  print len(rlist)
##  viol,rviol=xplor_violations(pdblist,psf,rlist)
##  for key in viol:
##    nviol = 0
##    for key2 in viol[key]:
##      if key=='DIST':
##        vsum = 0.0
##        if key2 in ['>=0.5','< 0.5','< 0.4','< 0.3']:
##          nviol += viol[key][key2]
##      if key=='DIHE':
##        vsum = 0.0
##        if key2 in ['>=5.0','< 5.0','< 4.0','< 3.0']:
##          nviol += viol[key][key2]
##    print "VIOL %s: %7.3f\n"%(key,nviol/float(len(pdblist)))
##  cutoff = .2
##  vlist = []
##  for i in range(len(pdblist)):
##    sumviol = 0.0
##    for key in rviol:
##      if rviol[key][i] >= cutoff:
##        sumviol += 1
##    vlist.append(sumviol)
##  print avg_list(vlist)
##  for key in viol:
##    rms = 0.0
##    for el in rlist:
##      if el.type == key:
##        for viol in rviol[str(el)]:
##          rms+=viol**2
##    rms = math.sqrt(rms/(len(rlist)*len(pdblist)))
##    print "RMS %s: %7.3f\n"%(key,rms)
##  rdistcutoff = [0.2,0.4,0.5]
##  rdihecutoff = [2.0,4.0,5.0]
##  # BUILD TOPSTR
##  topval = ((len(pdblist)/10)+1)*10
##  topval = len(pdblist)
##  topstr = ''
##  i = 1
##  while i <= topval:
##    if (i+1)%10==0 or i==1:
##      if i!=1: topstr+="%i"%(i+1)
##      else: topstr+="1"
##      i+=len("%i"%(i+1))
##    elif i%5==0 and i%10!=0:
##      topstr+="."
##      i+=1
##    elif i==topval:
##      val = "%i"%topval
##      topstr+=val[-1]
##      i+=1
##    else:
##      topstr+=" "
##      i+=1
##  for type in ['DIST','DIHE']:
##    typelist = [el for el in rlist if el.type==type]
##    if type=='DIST' and len(typelist)>0:
##      rcutoff = rdistcutoff
##      file.write('Distance restraints\n')
##      file.write('===================\n')
##      file.write('_ = violation > %.1f A.\n~ = violation > %.1f A.\n'%(rcutoff[0],
##                                                                       rcutoff[1]))
##      file.write('* = violation > %.1f A.\n'%rcutoff[2])
##      file.write('Vmax = maximum violation in A.\n\n')
##      file.write('%s  Vmax restraint\n'%topstr)
##    if type=='DIHE' and len(typelist)>0:
##      rcutoff = rdihecutoff
##      file.write('Dihedral angle restraints\n')
##      file.write('=========================\n')
##      file.write('_ = violation > %.1f degress.\n~ = violation > %.1f degrees.\n'%(rcutoff[0],rcutoff[1]))
##      file.write('* = violation > %.1f degrees.\n'%rcutoff[2])
##      file.write('Vmax = maximum violation in degrees.\n\n')
##      file.write('%s  Vmax restraint\n'%topstr)
##    for r in typelist:
##      stri = ''
##      consr = 0
##      for elem in rviol[str(r)]:
##        if elem >= rcutoff[2]:
##          stri+='*'
##          consr += 1
##        elif elem >= rcutoff[1]:
##          stri+='~'
##          consr += 1
##        elif elem >= rcutoff[0]:
##          stri+='_'
##        else:
##          stri+='.'
##      file.write("%s %5.2f %s\n"%(string.ljust(stri,topval),max(rviol[str(r)]),str(r)))
##  # convert mtf
##  mtf = "%s.mtf"%xplr.psf[:-4]
##  if not os.path.exists(mtf): cns_psf2mtf(nmvconf["CNS"],xplr.psf,mtf)
##  # read restraints
##  datasets = qn_readdatafile(nmv_adjust(queen.dataset,dataset))
##  data = qn_readdatasets(queen,datasets)
##  restraintlist = data['data']
##  pdbbase = os.path.join(queen.pdb,'run')
##  # calculate
##  cns_calcstructurecv(pdbbase,
##                      xplr.template,
##                      mtf,
##                      restraintlist,
##                      naccepted=50)
##  # READ OLD STUFF
##  content = open('data.dat','r').readlines()
##  info = {}
##  for line in content:
##    line = line.split()
##    id = line[3][1:-1]
##    info[id]={}
##    info[id]['H']=float(line[0])
##    info[id]['rmsd']=float(line[1])
##  content = open('whatif.dat','r').readlines()
##  for line in content:
##    line = line.split()
##    info[line[0]]['whatif']=float(line[1])
##  content = open('radiusofgyration.dat','r').readlines()
##  for line in content:
##    line = line.split()
##    info[line[0]]['rg']=float(line[1])
##  # WRITE NEW FILE
##  out = open('secstructure.dat','w')
##  for key in info.keys():
##    pdb = "/home/snabuurs/secondary_data/db_queen/%s/pdb/%s_ensemble.pdb"%(key,key)
##    out.write("\"%s\" %7.3f\n"%(key,
##                                yas_percsecstr(nmvconf["YASARA_RUN"],pdb)))
##  out.close()
#  nmv_mkpbs('/home/snabuurs/secondary_data/db_queen/','/tmp/pbs')
##  dbpath = '/home/snabuurs/secondary_data/db_queen/'
##  tgpath = '/home/snabuurs/secondary_data/db_queen_tgz/'
##  tfile  = os.path.join(tgpath,'db.tgz')
##  tf = tarfile.open(tfile,'w:gz')
##  pathlist = glob.glob(os.path.join(dbpath,'*'))
##  for path in pathlist:
##    project = os.path.basename(path)
##    print project
##    if os.path.exists(os.path.join(path,'data/')):
##      tf.add(os.path.join(path,'data/'),'%s/data/'%project)
##      tf.add(os.path.join(path,'log/'),'%s/log/'%project)
##      tf.add(os.path.join(path,'output/'),'%s/output/'%project)
##      tf.add(os.path.join(path,'pdb/'),'%s/pdb/'%project,recursive=False)
##      tf.add(os.path.join(path,'plot/'),'%s/pdb/'%project)
##  tf.close()

#  ======================================================================
#  ======================================================================

# PRINT WELCOME SCREEN
if myid==0:
  txt_header()

# READ CONFIGURATION FILE AND BUILD DICTIONARY NMVCONF OF THE ENTRIES
if (string.find(sys.argv[0],"pychecker")==-1):
  # LOCAL
  if (socket.gethostname() in mymachines):
    if myid==0: print "Reading configuration file nmr_valibase.conf...\n"
    nmvconf=dct_read(os.path.join(os.path.dirname(sys.argv[0]),"nmr_valibase.conf"))
  # ON OUR CLUSTER
  if ((socket.gethostname() in nmr_nodes) or (socket.gethostname() in octopus_nodes)):
    print "Reading configuration file nmr_valibase.node...\n"
    nmvconf=dct_read(os.path.join(os.path.dirname(sys.argv[0]),"nmr_valibase.node"))

# CHECK WHICH OF THE SUBSCRIPTS SHOULD BE RUN (FIRST COMMAND LINE ARGUMENT)
argv=len(sys.argv)
if (argv>1):

  # TEMP FUNCTION
  # ==============
  if (sys.argv[1]=='-hidden'):
    # RUN THE TEMP FUNCTION
    if (argv!=2): error("Number of command line parameters does not match -hidden option");
    nmv_temp()
    raise SystemExit

  # HELP FUNCTIONS
  # ==============
  if (sys.argv[1]=="-doc"):
    # GENERATE HTML OR PDF DOCUMENTATION
    if (argv!=3): error("Number of command line parameters does not match -doc option");
    nmv_createdoc(sys.argv[2])
    raise SystemExit

  if (sys.argv[1]=="-check"):
    # CHECK SOURCE CODE
    if (argv!=2): error("Number of command line parameters does not match -check option");
    nmv_checksource()
    raise SystemExit

  # OTHER FUNCTIONS
  # ===============
  if (sys.argv[1]=="-birthday"):
    # SEND BIRTHDAY EMAILS
    nmv_birthdaymail('/home/snabuurs/datfiles/verjaardagen.dat')
    raise SystemExit

  if (sys.argv[1]=="-raidcheck"):
    # CHECK RAID ARRAY
    nmv_checkraid(nmvconf["RAIDCHECK"])
    raise SystemExit

  if (sys.argv[1]=="-exportqueen"):
    # CHECK RAID ARRAY
    nmv_exportqueen(nmvconf["EXP_QUEEN"])
    raise SystemExit

  if (sys.argv[1]=="-exportweb"):
    # CHECK RAID ARRAY
    nmv_exportweb(nmvconf["EXP_WEB"])
    raise SystemExit

  # NMR INFO FUNCTIONS:
  # ===================
  if (sys.argv[1]=='-info_buildseq'):
    # BUILD SEQ FILE
    if (argv!=4): error("Number of command line parameters does not match -info_buildseq option")
    nmv_generateseq(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_buildpsf'):
    # BUILD PSF FILE
    if (argv>5): error("Number of command line parameters does not match -info_buildpsf option")
    if argv==5:
      nmv_generatepsf(sys.argv[2],sys.argv[3],sys.argv[4])
    else:
      nmv_generatepsf(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_plotuncertainty'):
    # PLOT UNCERTAINTY UPON ADDITION OF DATA
    if (argv!=4): error("Number of command line parameters does not match -info_plotuncertainty option")
    nmv_plotuncertainty(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_restraintinfo'):
    # CALCULATE INFORMATION PER RESTRAINT
    if (argv!=4): error("Number of command line parameters does not match -info_restraintinfo option")
    nmv_restraintinformation(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_averageinfo'):
    # CALCULATE INFORMATION PER RESTRAINT
    if (argv!=4): error("Number of command line parameters does not match -info_averageinfo option")
    nmv_avinformation(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_sort'):
    # CALCULATE INFORMATION PER RESTRAINT
    if (argv!=4): error("Number of command line parameters does not match -info_averageinfo option")
    # SETUP QUEEN
    projectname = sys.argv[2]
    dataset = sys.argv[3]
    queen = qn_setup(nmvconf,projectname,myid,numproc)
    xplr  = qn_setupxplor(nmvconf,projectname)
    qn_infsort(queen,xplr,dataset)
    raise SystemExit

  if (sys.argv[1]=='-info_univsavginfo'):
    # CALCULATE INFORMATION PER RESTRAINT
    if (argv!=4): error("Number of command line parameters does not match -info_univsavginfo option")
    nmv_combineavguni(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_2drestraintinfo'):
    # PLOT 2D RESTRAINTINFO
    if (argv!=4): error("Number of command line parameters does not match -info_2drestraintinfo option")
    nmv_infocontactplot(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-noe_visualize'):
    # VISUALIZE RESTRAINTS COLOURED BY INFO CONTENT
    if (argv!=5): error("Number of command line parameters does not match -info_visualizenoes");
    nmv_visualizenoes(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-info_noesvsinfo'):
    # PLOT INFO VS NOES
    if (argv!=4): error("Number of command line parameters does not match -info_infovsnoes option")
    nmv_noesvsinfo(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_rmsdvsnoes'):
    # PLOT RMSD VS NOES
    if (argv!=4): error("Number of command line parameters does not match -info_rmsdvsnoes option")
    nmv_rmsdvsnoes(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_buildnrset'):
    # BUILD NON REDUNDANT DATASET
    if (argv!=4): error("Number of command line parameters does not match -info_buildnrset option")
    nmv_createnrdataset(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_buildminset'):
    # BUILD MINIMAL DATASET
    if (argv!=4): error("Number of command line parameters does not match -info_buildminset option")
    nmv_createmindataset(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_setinfo'):
    # CALCULATE INFORMATION PER DATASET
    if (argv!=4): error("Number of command line parameters does not match -info_setinfo option")
    nmv_setinformation(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-info_atomuncertainty'):
    # CALCULATE UNCERTAINTY OF (GROUPS OF) ATOMS
    if (argv!=5): error("Number of command line parameters does not match -info_atomuncertainty option")
    nmv_atomuncertainty(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-info_corruncertainty'):
    # CORRELATE UNCERTAINTY OF (GROUPS OF) ATOMS
    if (argv!=6): error("Number of command line parameters does not match -info_corruncertainty option")
    nmv_correlateuncertainty(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    raise SystemExit

  if (sys.argv[1]=='-info_buildmtx'):
    # CALCULATE DISTANCE MATRIX
    if (argv!=4): error("Number of command line parameters does not match -info_buildmtx option")
    nmv_calcdmtx(sys.argv[2],sys.argv[3])
    raise SystemExit

  # NOE FUNCTIONS:
  # ==============
  if (sys.argv[1]=='-noe_generate'):
    # CHECKED
    # GENERATE NOES BASED ON STRUCTURE
    if (argv!=6): error("Number of command line parameters does not match -noe_noegenerate option");
    nmv_createnoes(sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]))
    raise SystemExit

  #PDB ANALYSIS FUNCTIONS:
  #=======================
  if (sys.argv[1]=='-pdb_selnmrmin'):
    # SELECT ENERGY MINIMIZED NMR STRUCTURES FROM THE PDB
    if (argv!=3): error("Number of command line parameters does not match -pdb_selnmrmin option");
    nmv_pdbselnmrmin(sys.argv[2])
    raise SystemExit

  if (sys.argv[1]=='-pdb_selmoddist'):
    # GENERATES THE DISTRIBUTION OF THE NUMBER OF MODELS PER NMR STRUCTURE
    if (argv!=3): error("Number of command line parameters does not match -pdb_selmoddist option");
    nmv_pdbselmoddist(sys.argv[2])
    raise SystemExit

  if (sys.argv[1]=='-pdb_restraintdist'):
    # GENERATES THE DISTRIBUTION OF THE NUMBER OF PDB FILES WITH NMR RESTRAINTS
    if (argv!=3): error("Number of command line parameters does not match -pdb_selmoddist option");
    nmv_createrestraintdist(sys.argv[2])
    raise SystemExit

  if (sys.argv[1]=='-pdb_rdcdata'):
    # EXTRACT ALL NMR STRUCTURES WITH RDC DATA AVAILABLE
    if (argv!=3): error("Number of command line parameters does not match -pdb_rdcdata option");
    nmv_getpdbrdc(sys.argv[2])
    raise SystemExit

  #PROJECT ANALYSIS FUNCTIONS:
  #===========================
  if (sys.argv[1]=='-ana_watref'):
    # ANALYZE A SET OF WATER REFINED NMR STRUCTURES BY CHRIS
    if (argv!=3): error("Number of command line parameters does not match -ana_watref option");
    nmv_analyzewatref(sys.argv[2])
    raise SystemExit

  if (sys.argv[1]=='-ana_pdbblunder'):
    # ANALYZE A SET OF WATER REFINED NMR STRUCTURES BY CHRIS
    if (argv!=2): error("Number of command line parameters does not match -ana_watref option");
    nmv_anapdbblunder()
    raise SystemExit


  if (sys.argv[1]=='-ana_concoord'):
    # ANALYZE A SET OF CONCOORD GENERATED STRUCTURES
    if (argv!=3): error("Number of command line parameters does not match -ana_concoord option");
    nmv_validateconcoord(sys.argv[2])
    raise SystemExit

  if (sys.argv[1]=='-ana_sumconcoord'):
    # ANALYZE A SET OF CONCOORD GENERATED STRUCTURES
    if (argv!=2): error("Number of command line parameters does not match -ana_sumconcoord option");
    nmv_summarizeconcoord()
    raise SystemExit

  if (sys.argv[1]=='-ana_builddress'):
    # ANALYZE A SET OF WATER REFINED NMR STRUCTURES BY CHRIS
    if (argv!=4): error("Number of command line parameters does not match -ana_builddress option");
    nmv_builddress(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-ana_buildwifdb'):
    # ANALYZE AND BUILD WHATIF INTERNAL DATABASE
    if (argv!=3): error("Number of command line parameters does not match -ana_builwifdb option");
    nmv_buildwifdb(sys.argv[2])
    raise SystemExit

  if (sys.argv[1]=='-ana_preparedress'):
    # ANALYZE A SET OF STRUCTURE FOR A WATER REFINEMENT BY CHRIS
    if (argv!=4): error("Number of command line parameters does not match -ana_watref option");
    nmv_preparedress(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-ana_importdb'):
    # IMPORT DB
    if (argv!=4): error("Number of command line parameters does not match -ana_watref option");
    nmv_importdb(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=='-ana_xraynmr'):
    # COMPARE XRAY AND NMR STRUCTURES
    if (argv!=2): error("Number of command line parameters does not match -ana_xraynmr option");
    nmv_anaxrayandnmr()
    raise SystemExit

  if (sys.argv[1]=='-ana_rmsdsurface'):
    # BUILD RMSD SURFACE
    nmv_constructrmsdsurface(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-ana_optsurface'):
    # BUILD RMSD SURFACE
    nmv_optimizermsdsurface(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-ana_uncvsmodelquality'):
    # CORRELATE INFORMATION AGAINST STRUCTURAL MODELS
    nmv_uncvsmodelquality(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-ana_bbuncvsmodelquality'):
    # CORRELATE INFORMATION AGAINST STRUCTURAL MODELS
    nmv_bbuncvsmodelquality(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-ana_localuncvsmodelquality'):
    # CORRELATE INFORMATION AGAINST STRUCTURAL MODELS
    nmv_localuncvsmodelquality(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-ana_Iunivsmodelquality'):
    # CORRELATE INFORMATION AGAINST STRUCTURAL MODELS
    nmv_Iunivsmodelquality(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-ana_infovsmodelquality'):
    # CORRELATE INFORMATION AGAINST STRUCTURAL MODELS
    nmv_infovsmodelquality(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-ana_Iunivsxraydeviation'):
    # CORRELATE INFORMATION AGAINST STRUCTURAL MODELS
    nmv_Iunivsxraydeviation(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-ana_ir'):
    # ANALYZE A SET OF WATER REFINED NMR STRUCTURES BY CHRIS
    if (argv!=3): error("Number of command line parameters does not match -ana_watref option");
    nmv_analyzeir(sys.argv[2])
    raise SystemExit

  if (sys.argv[1]=='-ana_Hstructure'):
    if (argv!=5): error("Number of command line parameters does not match -ana_Hstructure option");
    nmv_analyzeHstructure(sys.argv[2],sys.argv[3],int(sys.argv[4]))
    raise SystemExit

  if (sys.argv[1]=='-ana_subsets'):
    if (argv!=4): error("Number of command line parameters does not match -ana_subsets option");
    nmv_anasubsets(sys.argv[2],sys.argv[3])
    raise SystemExit

  #PDB REPORT ANALYSIS FUNCTIONS:
  #=======================
  if (sys.argv[1]=='-pdbr_count'):
    # COUNT THE ERRORS IN summary.txt OF THE PDBREPORTS
    if (argv!=2): error("Number of command line parameters does not match -pdbr_count option");
    nmv_pdbrerrorcount()
    raise SystemExit

  if (sys.argv[1]=='-pdbr_listerrors'):
    # SHOW THE DIFFERENT TYPE OF ERRORS IN THE PDBREPORT WITH THEIR ASSOCIATED REVINDEX NUMBERS
    if (argv!=2): error("Number of command line parameters does not match -pdbr_listerrors option");
    nmv_pdbrerrorlist()
    raise SystemExit

  # NMR ENSEMBLE ANALYSIS FUNCTIONS
  # ===============================
  if (sys.argv[1]=="-nmr_fitensemble"):
    # FIT ENSEMBLE
    if (argv!=4): error("Number of command line parameters does not match -nmr_fitensemble option");
    nmv_fitensemble(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=="-nmr_calcs2"):
    # CALCULATE ENSEMBLE S2
    if (argv!=4): error("Number of command line parameters does not match -nmr_calcs2 option");
    nmv_calcs2(sys.argv[2],sys.argv[3])
    raise SystemExit

  # REFINEMENT FUNCTIONS
  if (sys.argv[1]=="-dress_refineproject"):
    # FIT ENSEMBLE
    if (argv!=4): error("Number of command line parameters does not match -xplr_refineproject option");
    nmv_dressproject(sys.argv[2],sys.argv[3])
    raise SystemExit

  # REFINEMENT FUNCTIONS
  if (sys.argv[1]=="-xplr_refineproject"):
    # REFINE STRUCTURES
    if (argv!=4): error("Number of command line parameters does not match -xplr_refineproject option");
    nmv_refineproject(sys.argv[2],sys.argv[3])
    raise SystemExit

  # REFINEMENT FUNCTIONS
  if (sys.argv[1]=="-xplr_calcproject"):
    # REFINE STRUCTURES
    if (argv!=5): error("Number of command line parameters does not match -xplr_calcproject option");
    nmv_calculatestructures(sys.argv[2],sys.argv[3],int(sys.argv[4]))
    raise SystemExit

  # REFINEMENT FUNCTIONS
  if (sys.argv[1]=="-xplr_selectensemble"):
    # SELECT ENSEMBLE
    if (argv!=6): error("Number of command line parameters does not match -xplr_selectensemble option");
    nmv_selectensemble(sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]))
    raise SystemExit


  # CONCOORD FUNCTIONS
  # ==================
  # CONVERT RESTRAINTS
  if (sys.argv[1]=="-cnc_testconvergence"):
    # REFINE STRUCTURES
    if (argv!=4): error("Number of command line parameters does not match -cnc_writeconcoord option");
    nmv_cncconvergence(sys.argv[2],sys.argv[3])
    raise SystemExit

  # CONVERT RESTRAINTS
  if (sys.argv[1]=="-cnc_writeconcoord"):
    # REFINE STRUCTURES
    if (argv!=5): error("Number of command line parameters does not match -cnc_writeconcoord option");
    nmv_writeconcoord(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  # REFINEMENT FUNCTIONS
  if (sys.argv[1]=="-cnc_calcstruct"):
    # SELECT ENSEMBLE
    if (argv!=6): error("Number of command line parameters does not match -cnc_calcstruct option");
    nmv_cnccalcstruct(sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]))
    raise SystemExit

  # DATA CONVERSION FUNCTIONS
  # =========================
  if (sys.argv[1]=="-pdbtoqua"):
    # CONVERT PDB OR CHECKDB FILE TO QUALITY FILE
    if (argv!=4): error("Number of command line parameters does not match %s option" % sys.argv[1]);
    pdb_getqua(sys.argv[2],sys.argv[3])
    raise SystemExit

  # DATA CONVERSION FUNCTIONS
  # =========================
  if (sys.argv[1]=="-pdb_cor2pdb"):
    # CONVERT PDB OR CHECKDB FILE TO QUALITY FILE
    if (argv!=4): error("Number of command line parameters does not match %s option" % sys.argv[1]);
    pdb_cor2pdb(sys.argv[2],sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=="-pdb_pdb2fasta"):
    # CONVERT PDB OR CHECKDB FILE TO SEQUENCE FILE
    if (argv!=5): error("Number of command line parameters does not match %s option" % sys.argv[1]);
    pdb_pdb2fasta(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=="-pdb_merge"):
    # MERGE PDB FILES INTO NMR MODEL COLLECTION
    if (argv!=4): error("Number of command line parameters does not match -mergepdb option")
    # CREATE FILELIST
    searchpath = string.replace(sys.argv[2],'xxxx','*')
    mergelist = glob.glob(searchpath)
    print 'Joining %i structures in ensemble.'%len(mergelist)
    # MERGE FILES
    nmv_mergepdb(mergelist,sys.argv[3])
    raise SystemExit

  if (sys.argv[1]=="-pdb_split"):
    # MERGE PDB FILES INTO NMR MODEL COLLECTION
    if (argv!=5): error("Number of command line parameters does not match -pdb_split option")
    yas_splitpdb(nmvconf["YASARA_RUN"],sys.argv[2],sys.argv[3],format=sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=="-pdb_renumber"):
    # MERGE PDB FILES INTO NMR MODEL COLLECTION
    if (argv!=5): error("Number of command line parameters does not match -renumberpdb option")
    # CREATE FILELIST
    print 'Renumbering pdb file.'
    # MERGE FILES
    nmv_renumberpdb(sys.argv[2],sys.argv[3],sys.argv[4].lower())
    raise SystemExit

  if (sys.argv[1]=="-pdb_extractmodel"):
    # EXTRACT MODEL FROM PDB FILE
    if (argv!=5): error("Number of command line parameters does not match -pdbextractmodel option")
    nmv_extractmodel(sys.argv[2],sys.argv[3],int(sys.argv[4]))
    raise SystemExit

  if (sys.argv[1]=='-noe_reformatrestraints'):
    # REFORMAT RESTRAINTS AND REMOVE DOUBLES
    if (argv!=5): error("Number of command line parameters does not match -reformatrestraints option");
    nmv_reformatrestraints(sys.argv[2],sys.argv[3],sys.argv[4])
    raise SystemExit

  if (sys.argv[1]=='-renumberrestraints'):
    # RENUMBER RESTRAINTS
    if (argv!=6): error("Number of command line parameters does not match -renumberrestraints option");
    nmv_renumberrestraints(sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]))
    raise SystemExit

  if (sys.argv[1]=='-grouprestraints'):
    # GROUP DISTANCE RESTRAINTS
    if (argv!=3): error("Number of command line parameters does not match -grouprestraints option");
    nmv_grouprestraints(sys.argv[2])
    raise SystemExit

  if (sys.argv[1]=='-xsy_deassignpeaks'):
    # GROUP DISTANCE RESTRAINTS
    if (argv!=4): error("Number of command line parameters does not match -grouprestraints option");
    xeasy_deassignpeaks(sys.argv[2],sys.argv[3])
    raise SystemExit


  # STATISTICAL FUNCTIONS
  # =====================
  if (sys.argv[1]=='-ave_column'):
    # AVERAGE THE GIVEN COLUMN
    if (argv!=4): error("Number of command line parameters does not match -ave_column option");
    nmv_avecolumn(sys.argv[2],int(sys.argv[3]))
    raise SystemExit

  #BACKUP FUNCTIONS:
  #=====================
  if (sys.argv[1]=='-backup'):
    # BACKUP CRITICAL DIRECTORIES
    if (argv!=3): error("Number of command line parameters does not match -backup option");
    nmv_backup(sys.argv[2])
    raise SystemExit

# INVALID OR MISSING COMMAND LINE PARAMETER?
if len(sys.argv)==1 and myid==0:
  # YES - PRINT HELP SCREEN
  print "Use the following command line options:\n"
  print
  print "HELP FUNCTIONS:"
  print "==============="
  print "nmr_valibase.py           "
  print "                          >>> Prints this help screen"
  print
  print "GENERAL FUNCTIONS:"
  print "=================="
  print "nmr_valibase.py -doc"
  print "                          >>> Generate NMR_Valibase documentation"
  print "nmr_valibase.py -check"
  print "                          >>> Check source code"
  print
  print "ANALYZE PROJECTS:"
  print "================="
  print "nmr_valibase.py -ana_watref projectsdir"
  print "                          >>> Analyze water refined NMR structures."
  print "nmr_valibase.py -ana_builddress watrefdir outputpath"
  print "                          >>> Build DRESS database."
  print "nmr_valibase.py -ana_buildwifdb outputpath"
  print "                          >>> Build WHAT IF database."
  print "nmr_valibase.py -ana_prepareress structuresdir outputpath"
  print "                          >>> Prepare DRESS database."
  print "nmr_valibase.py -ana_importdb dbdir outpath"
  print "                          >>> Import db of recalculated structures."
  print "nmr_valibase.py -ana_xrayandnmr"
  print "                          >>> Analyze identical XRAY and NMR structures."
  print "nmr_valibase.py -ana_restraints projectsdir"
  print "                          >>> Analyze QUEEN analysis of NMR datasets."
  print "nmr_valibase.py -ana_rmsdsurface projectsdir dataset outputfile"
  print "                          >>> Create RMSD surface for projects in projectdir"
  print "nmr_valibase.py -ana_optsurface projectsdir dataset outputfile"
  print "                          >>> Optimize RMSD surface for projects in projectdir"
  print "nmr_valibase.py -ana_localuncvsmodelquality projectsdir dataset outputpath"
  print "                          >>> Compare local uncertainty against structural model"
  print "nmr_valibase.py -ana_uncvsmodelquality projectsdir dataset outputpath"
  print "                          >>> Compare residue uncertainty against structural model"
  print "nmr_valibase.py -ana_infovsmodelquality projectsdir dataset outputpath"
  print "                          >>> Compare info content  against structural model"
  print "nmr_valibase.py -ana_Iunivsmodelquality projectsdir dataset outputpath"
  print "                          >>> Compare uncertainty against structural model"
  print "nmr_valibase.py -ana_Iunivsxraydeviation projectsdir dataset outputpath"
  print "                          >>> Compare info content against X-ray models"
  print "nmr_valibase.py -ana_4concepts projectsdir dataset"
  print "                          >>> Do the analysis for the Concepts paper"
  print
  print "PDB ANALYSIS FUNCTIONS:"
  print "======================="
  print "nmr_valibase.py -pdb_selnmrmin"
  print "                          >>> Selects from the PDB all the NMR structures which contain only 1 model"
  print "nmr_valibase.py -pdb_selmoddist"
  print "                          >>> Generates the distribution of the number of models per NMR structure"
  print "nmr_valibase.py -pdb_restraintsdist outputfile.agr"
  print "                          >>> Generates the distribution of percentage of structures that have restraints depostied."
  print
  print "nmr_valibase.py -pdb_rdcdata outputfile"
  print "                          >>> Tries to extract all NMR files with RDC data."
  print
  print "XPLOR FUNCTIONS:"
  print "================"
  print "nmr_valibase.py -xplr_refineproject projectname dataset"
  print "                          >>> Refine the structures in project with dataset."
  print "nmr_valibase.py -xplr_calcproject projectname dataset nstructures"
  print "                          >>> Calculate structures for project with dataset."
  print "nmr_valibase.py -xplr_selectensemble projectname dataset criterion nstruct"
  print "                          >>> Select ensemble base on criterion (rms|energy)."
  print
  print "CONCOORD FUNCTIONS:"
  print "==================="
  print
  print "nmr_valibase.py -cnc_testconvergence rdcdict outputpath"
  print "                          >>> Test convergence of PDB files with RDCs"
  print "nmr_valibase.py -cnc_writeconcoord projectname dataset cnctbl"
  print "                          >>> Convert data in dataset to CNC format."
  print "nmr_valibase.py -cnc_calcstruct projectname basename cnctbl nstruct"
  print "                          >>> Calculate nstruct structures for dataset."
  print
  print "PDB REPORT ANALYSIS FUNCTIONS:"
  print "=============================="
  print "nmr_valibase.py -pdbr_count"
  print "                          >>> Count the errors in 'summary.txt' of the PDBREPORTS"
  print "nmr_valibase.py -pdbr_listerrors"
  print "                          >>> Show all existing error types in the PDBREPORTS"
  print
  print "ERROR ANALYSIS FUNCTIONS:"
  print "========================="
  print "nmr_valibase.py -err_protstruct year"
  print "                          >>> Redo the Nature protein analysis table."
  print
  print "NMR ENSEMBLE FUNCTIONS:"
  print "======================="
  print "nmr_valibase.py -nmr_fitensemble inpdb outpdb"
  print "                          >>> Fit the stucture in the ensemble."
  print "nmr_valibase.py -nmr_calcs2 inpdb s2file"
  print "                          >>> Calculate S2 from PDB file."
  print
  print "NMR INFO FUNCTIONS:"
  print "==================="
  print "nmr_valibase.py -info_buildseq projectname pdbfile"
  print "                          >>> Build a seq file based on coordinates."
  print "nmr_valibase.py -info_buildpsf seqfile|coordfile type='sequence'|'coordinates'"
  print "                          >>> Build a psf file based on sequence or coordinates."
  print "nmr_valibase.py -info_plotuncertainty projectname dataset"
  print "                          >>> Plot the uncertainty vs the number of added restraints."
  print "nmr_valibase.py -info_restraintinfo projectname dataset"
  print "                          >>> Calculate the information of individual restraints."
  print "nmr_valibase.py -info_averageinfo projectname dataset"
  print "                          >>> Calculate the average info of indiv. restraints."
  print "nmr_valibase.py -info_univsavginfo projectname dataset"
  print "                          >>> Combine unique and avg info."
  print "nmr_valibase.py -info_buildnrset projectname dataset"
  print "                          >>> Calculate non redundant dataset."
  print "nmr_valibase.py -info_buildminset projectname dataset"
  print "                          >>> Calculate minimal dataset."
  print "nmr_valibase.py -info_setinfo projectname dataset"
  print "                          >>> Calculate the information of different sets."
  print "nmr_valibase.py -info_atomuncertainty projectname dataset selection"
  print "                          >>> Calculate the uncertainty of (groups of) atoms."
  print
  print "NOE FUNCTIONS:"
  print "=============="
  print "nmr_valibase.py -noe_generate pdbfile noefile cutoff error"
  print "                          >>> Generate NOE file, upto given cutoff with given error."
  print "nmr_valibase.py -grouprestraints distancetable"
  print "                          >>> Group restraints in IR,SQ,MR and LR."
  print "nmr_valibase.py -noe_visualize projectname dataset pdbfile"
  print "                          >>> Visualize NOEs in PDB file."
  print "nmr_valibase.py -noe_reformatrestraints infile outfile type"
  print "                          >>> Reformat an restraint file to somewhat of a standard format."
  print "nmr_valibase.py -renumberrestraints infile outfile type offset"
  print "                          >>> Renumber a restraintfile with the given offset."
  print "nmr_valibase.py -groupnoe restraintfile"
  print "                          >>> Group NOEs in IR,SQ,ME and LR."
  print
  print "PDB FILE FUNCTIONS:"
  print "==================="
  print "nmr_valibase.py -pdb_merge PDBFilexxxx.pdb NMRFile"
  print "                          >>> Merge numbered PDB files into one big file"
  print "nmr_valibase.py -pdb_split PDBFile basename PDB|XPLOR"
  print "                          >>> Split a PDB file into separate models."
  print "nmr_valibase.py -pdb_renumber numbers.pdb infile.pdb outfile.pdb"
  print "                          >>> Renumber infile.pdb according to numbers.pdb"
  print "nmr_valibase.py -pdb_extractmodel in.pdb out.pdb model_number"
  print "                          >>> Extract the model with the given number from in.pdb."
  print
  print "DATA CONVERSION FUNCTIONS:"
  print "=========================="
  print "nmr_valibase.py -pdbtoqua PDBFile ResultFile"
  print "                          >>> Convert PDB to QUA file"
  print "nmr_valibase.py -pdb_cor2pdb CORFile PDBFile"
  print "                          >>> Convert CYANA COR file to PDB file"
  print "nmr_valibase.py -pdb_pdb2fasta PDBFile FastaFile xplor|pdb"
  print "                          >>> Convert CYANA COR file to PDB file"
  print
  print "XEASY FUNCTIONS:"
  print "================"
  print "nmr_valibase.py -xsy_deassignpeaks inpeakfile outpeakfile"
  print "                          >>> Deassign all peaks in the peak file."
  print
  print "STATISTICAL FUNCTIONS:"
  print "======================"
  print "nmr_valibase.py -ave_column filename column"
  print "                          >>> Average the values in the given column in the given file"
  print
  print "BACKUP FUNCTIONS:"
  print "====================="
  print "nmr_valibase.py -backup daily|weekly"
  print "                          >>> Backup important directories"
  print
  raise SystemExit
