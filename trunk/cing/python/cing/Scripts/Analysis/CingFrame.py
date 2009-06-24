#@PydevCodeAnalysisIgnore
import os, sys, Tkinter

from memops.gui.Button          import Button
from memops.gui.ButtonList      import ButtonList
from memops.gui.RadioButtons    import RadioButtons
from memops.gui.CheckButton     import CheckButton
from memops.gui.Entry           import Entry
from memops.gui.FileSelect      import FileType
from memops.gui.FileSelectPopup import FileSelectPopup
from memops.gui.Frame           import Frame
from memops.gui.Label           import Label
from memops.gui.LabelFrame      import LabelFrame
from memops.gui.LabelDivider    import LabelDivider
from memops.gui.MessageReporter import showWarning, showOkCancel, showInfo, showYesNo
from memops.gui.PulldownList    import PulldownList
from memops.gui.ScrolledMatrix  import ScrolledMatrix
from memops.gui.WebBrowser      import WebBrowser

from memops.editor.Util      import createDismissHelpButtonList

from ccpnmr.analysis.popups.EditCalculation import NmrSimRunFrame

from nijmegen.cing import iCingRobot

# TBD
# Retrieve ROG results
# Store calc params

DEFAULT_URL = 'https://nmr.cmbi.ru.nl/'

CING_BLUE = '#78B8F0'

HTML_RESULTS_URL = 'HtmlResultsUrl'

ICING_BASE_URL = 'iCingBaseUrl'

CHECK_INTERVAL = 30000 # Miliseconds

APP_NAME = 'CING'

class CingFrame(NmrSimRunFrame):

  def __init__(self, parent, application, *args, **kw):

    project = application.project
    simStore = project.findFirstNmrSimStore(application=APP_NAME) or \
               project.newNmrSimStore(application=APP_NAME, name=APP_NAME)

    self.application = application
    self.residue = None
    self.structure = None
    self.serverCredentials = None
    self.iCingBaseUrl = DEFAULT_URL
    self.resultsUrl = None
    self.chain = None
    self.nmrProject = application.nmrProject
    self.serverDone = False

    NmrSimRunFrame.__init__(self, parent, project, simStore, *args, **kw)

    # # # # # # New Structure Frame # # # # #

    self.structureFrame.grid_forget()

    tab = self.tabbedFrame.frames[0]

    frame = Frame(tab, grid=(1,0))
    frame.expandGrid(2,1)

    div = LabelDivider(frame, text='Structures', grid=(0,0), gridSpan=(1,2))

    label = Label(frame, text='Ensemble: ', grid=(1,0))
    self.structurePulldown = PulldownList(frame, callback=self.changeStructure, grid=(1,1))

    headingList = ['Model','Use']
    editWidgets      = [None,None]
    editGetCallbacks = [None,self.toggleModel]
    editSetCallbacks = [None,None,]
    self.modelTable = ScrolledMatrix(frame, grid=(2,0), gridSpan=(1,2),
                                     callback=self.selectStructModel,
                                     editWidgets=editWidgets,
                                     editGetCallbacks=editGetCallbacks,
                                     editSetCallbacks=editSetCallbacks,
                                     headingList=headingList)

    texts = ['Activate Selected','Inactivate Selected']
    commands = [self.activateModels, self.disableModels]
    buttons = ButtonList(frame, texts=texts, commands=commands, grid=(3,0), gridSpan=(1,2))


    # # # # # # Submission frame # # # # # #

    tab = self.tabbedFrame.frames[1]
    tab.expandGrid(1,0)

    frame = LabelFrame(tab, text='Server Job Submission', grid=(0,0))
    frame.expandGrid(None,2)

    srow = 0
    label = Label(frame, text='iCing URL:', grid=(srow, 0))
    urls = [DEFAULT_URL,]
    self.iCingBaseUrlPulldown = PulldownList(frame, texts=urls, objects=urls, index=0, grid=(srow,1))


    srow +=1
    label = Label(frame, text='Results File:', grid=(srow, 0))
    self.resultFileEntry = Entry(frame, bd=1, text='', grid=(srow,1), width=50)
    self.setZipFileName()
    button = Button(frame, text='Choose File', bd=1, sticky='ew',
                    command=self.chooseZipFile, grid=(srow, 2))

    srow +=1
    label = Label(frame, text='Results URL:', grid=(srow, 0))
    self.resultUrlEntry = Entry(frame, bd=1, text='', grid=(srow,1), width=50)
    button = Button(frame, text='View Results HTML', bd=1, sticky='ew',
                    command=self.viewHtmlResults, grid=(srow, 2))

    srow +=1
    texts    = ['Submit Project!', 'Check Run Status',
                'Purge Server Result', 'Download Results']
    commands = [self.runCingServer, self.checkStatus,
                self.purgeCingServer, self.downloadResults]

    self.buttonBar = ButtonList(frame, texts=texts, commands=commands,
                                grid=(srow, 0), gridSpan=(1,3))

    for button in self.buttonBar.buttons[:1]:
      button.config(bg=CING_BLUE)

    # # # # # # Residue frame # # # # # #

    frame = LabelFrame(tab, text='Residue Options', grid=(1,0))
    frame.expandGrid(1,1)

    label = Label(frame, text='Chain: ')
    label.grid(row=0,column=0,sticky='w')
    self.chainPulldown = PulldownList(frame, callback=self.changeChain)
    self.chainPulldown.grid(row=0,column=1,sticky='w')

    headingList = ['#','Residue','Linking','Decriptor','Use?']
    editWidgets      = [None,None,None,None,None]
    editGetCallbacks = [None,None,None,None,self.toggleResidue]
    editSetCallbacks = [None,None,None,None,None,]
    self.residueMatrix = ScrolledMatrix(frame,
                                        headingList=headingList,
                                        multiSelect=True,
                                        editWidgets=editWidgets,
                                        editGetCallbacks=editGetCallbacks,
                                        editSetCallbacks=editSetCallbacks,
                                        callback=self.selectResidue)
    self.residueMatrix.grid(row=1, column=0, columnspan=2, sticky = 'nsew')

    texts = ['Activate Selected','Inactivate Selected']
    commands = [self.activateResidues, self.deactivateResidues]
    self.resButtons = ButtonList(frame, texts=texts, commands=commands,)
    self.resButtons.grid(row=2, column=0, columnspan=2, sticky='ew')

    """
    # # # # # # Validate frame # # # # # #

    frame = LabelFrame(tab, text='Validation Options', grid=(2,0))
    frame.expandGrid(None,2)

    srow = 0
    self.selectCheckAssign = CheckButton(frame)
    self.selectCheckAssign.grid(row=srow, column=0,sticky='nw' )
    self.selectCheckAssign.set(True)
    label = Label(frame, text='Assignments and shifts')
    label.grid(row=srow,column=1,sticky='nw')

    srow += 1
    self.selectCheckResraint = CheckButton(frame)
    self.selectCheckResraint.grid(row=srow, column=0,sticky='nw' )
    self.selectCheckResraint.set(True)
    label = Label(frame, text='Restraints')
    label.grid(row=srow,column=1,sticky='nw')

    srow += 1
    self.selectCheckQueen = CheckButton(frame)
    self.selectCheckQueen.grid(row=srow, column=0,sticky='nw' )
    self.selectCheckQueen.set(False)
    label = Label(frame, text='QUEEN')
    label.grid(row=srow,column=1,sticky='nw')

    srow += 1
    self.selectCheckScript = CheckButton(frame)
    self.selectCheckScript.grid(row=srow, column=0,sticky='nw' )
    self.selectCheckScript.set(False)
    label = Label(frame, text='User Python script\n(overriding option)')
    label.grid(row=srow,column=1,sticky='nw')

    self.validScriptEntry = Entry(frame, bd=1, text='')
    self.validScriptEntry.grid(row=srow,column=2,sticky='ew')

    scriptButton = Button(frame, bd=1,
                          command=self.chooseValidScript,
                          text='Browse')
    scriptButton.grid(row=srow,column=3,sticky='ew')
    """

    # # # # # # # # # #

    self.update(simStore)

    self.administerNotifiers(application.registerNotify)

  def downloadResults(self):

    if not self.run:
      msg = 'No current iCing run'
      showWarning('Failure', msg, parent=self)
      return

    credentials = self.serverCredentials
    if not credentials:
      msg = 'No current iCing server job'
      showWarning('Failure', msg, parent=self)
      return

    fileName = self.resultFileEntry.get()
    if not fileName:
      msg = 'No save file specified'
      showWarning('Failure', msg, parent=self)
      return

    if os.path.exists(fileName):
      msg = 'File %s already exists. Overwite?' % fileName
      if not showOkCancel('Query', msg, parent=self):
        return

    url = self.iCingBaseUrl
    iCingUrl = self.getServerUrl(url)
    logText = iCingRobot.iCingFetch(credentials, url, iCingUrl, fileName)
    print logText

    msg = 'Results saved to file %s\n' % fileName
    msg += 'Purge results from iCing server?'
    if showYesNo('Query',msg, parent=self):
      self.purgeCingServer()


  def getServerUrl(self, baseUrl):

    iCingUrl = os.path.join(baseUrl, 'icing/serv/iCingServlet')
    return iCingUrl

  def viewHtmlResults(self):

    resultsUrl = self.resultsUrl
    if not resultsUrl:
      msg = 'No current iCing results URL'
      showWarning('Failure', msg, parent=self)
      return

    webBrowser = WebBrowser(self.application, popup=self.application)
    webBrowser.open(self.resultsUrl)


  def runCingServer(self):

    if not self.project:
      return

    run = self.run
    if not run:
      msg = 'No CING run setup'
      showWarning('Failure', msg, parent=self)
      return

    structure = self.structure
    if not structure:
      msg = 'No structure ensemble selected'
      showWarning('Failure', msg, parent=self)
      return

    ensembleText = getModelsString(run)
    if not ensembleText:
      msg = 'No structural models selected from ensemble'
      showWarning('Failure', msg, parent=self)
      return

    residueText = getResiduesString(structure)
    if not residueText:
      msg = 'No active residues selected in structure'
      showWarning('Failure', msg, parent=self)
      return

    url = self.iCingBaseUrlPulldown.getObject()
    url.strip()
    if not url:
      msg = 'No iCing server URL specified'
      showWarning('Failure', msg, parent=self)
      self.iCingBaseUrl = None
      return

    msg = 'Submit job now? You will be informed when the job is done.'
    if not showOkCancel('Confirm', msg, parent=self):
      return

    self.iCingBaseUrl = url
    iCingUrl = self.getServerUrl(url)
    self.serverCredentials, results, tarFileName = iCingRobot.iCingSetup(self.project, userId='ccpnAp', url=iCingUrl)

    if not results:
      # Message already issued on failure
      self.serverCredentials = None
      self.resultsUrl = None
      self.update()
      return

    else:
      credentials = self.serverCredentials
      os.unlink(tarFileName)

    entryId = iCingRobot.iCingProjectName(credentials, iCingUrl).get(iCingRobot.RESPONSE_RESULT)
    baseUrl, htmlUrl, logUrl, zipUrl = iCingRobot.getResultUrls(credentials, entryId, url)

    self.resultsUrl = htmlUrl

    # Save server data in this run for persistence

    setRunParameter(run, iCingRobot.FORM_USER_ID, self.serverCredentials[0][1])
    setRunParameter(run, iCingRobot.FORM_ACCESS_KEY, self.serverCredentials[1][1])
    setRunParameter(run, ICING_BASE_URL, url)
    setRunParameter(run, HTML_RESULTS_URL, htmlUrl)
    self.update()

    run.inputStructures = structure.sortedModels()

    # select residues from the structure's chain
    #iCingRobot.iCingResidueSelection(credentials, iCingUrl, residueText)

    # Select models from ensemble
    #iCingRobot.iCingEnsembleSelection(credentials, iCingUrl, ensembleText)

    # Start the actual run
    self.serverDone = False
    iCingRobot.iCingRun(credentials, iCingUrl)

    # Fetch server progress occasionally, report when done
    # this function will call itself again and again
    self.after(CHECK_INTERVAL, self.timedCheckStatus)

    self.update()

  def timedCheckStatus(self):

    if not self.serverCredentials:
      return

    if self.serverDone:
      return

    status = iCingRobot.iCingStatus(self.serverCredentials, self.getServerUrl(self.iCingBaseUrl))

    if not status:
      #something broke, already warned
      return

    result = status.get(iCingRobot.RESPONSE_RESULT)
    if result == iCingRobot.RESPONSE_DONE:
      self.serverDone = True
      msg = 'CING run is complete!'
      showInfo('Completion', msg, parent=self)
      return

    self.after(CHECK_INTERVAL, self.timedCheckStatus)

  def checkStatus(self):

    if not self.serverCredentials:
      return

    status = iCingRobot.iCingStatus(self.serverCredentials, self.getServerUrl(self.iCingBaseUrl))

    if not status:
      #something broke, already warned
      return

    result = status.get(iCingRobot.RESPONSE_RESULT)
    if result == iCingRobot.RESPONSE_DONE:
      msg = 'CING run is complete!'
      showInfo('Completion', msg, parent=self)
      self.serverDone = True
      return

    else:
      msg = 'CING job is not done.'
      showInfo('Processing', msg, parent=self)
      self.serverDone = False
      return


  def purgeCingServer(self):

    if not self.project:
      return

    if not self.run:
      msg = 'No CING run setup'
      showWarning('Failure', msg, parent=self)
      return

    if not self.serverCredentials:
      msg = 'No current iCing server job'
      showWarning('Failure', msg, parent=self)
      return

    url = self.iCingBaseUrl
    results = iCingRobot.iCingPurge(self.serverCredentials, self.getServerUrl(url))

    if results:
      showInfo('Info','iCing server results cleared')
      self.serverCredentials = None
      self.iCingBaseUrl = None
      self.serverDone = False
      deleteRunParameter(self.run, iCingRobot.FORM_USER_ID)
      deleteRunParameter(self.run, iCingRobot.FORM_ACCESS_KEY)
      deleteRunParameter(self.run, HTML_RESULTS_URL)
    else:
      showInfo('Info','Purge failed')

    self.update()

  def chooseZipFile(self):

    fileTypes = [  FileType('Zip', ['*.zip']), ]
    popup = FileSelectPopup(self, file_types=fileTypes, file=self.resultFileEntry.get(),
                            title='Results zip file location', dismiss_text='Cancel',
                            selected_file_must_exist=False)

    fileName = popup.getFile()

    if fileName:
      self.resultFileEntry.set(fileName)
    popup.destroy()

  def setZipFileName(self):

    zipFile = '%s_CING_report.zip' % self.project.name
    self.resultFileEntry.set(zipFile)

  def selectStructModel(self, model, row, col):

    self.model = model

  def selectResidue(self, residue, row, col):

    self.residue = residue

  def deactivateResidues(self):

    for residue in self.residueMatrix.currentObjects:
      residue.useInCing = False

    self.updateResidues()

  def activateResidues(self):

    for residue in self.residueMatrix.currentObjects:
      residue.useInCing = True

    self.updateResidues()

  def activateModels(self):

    if self.run:
      for model in self.modelTable.currentObjects:
        if model not in self.run.inputStructures:
          self.run.addInputStructure(model)

      self.updateModels()

  def disableModels(self):

    if self.run:
      for model in self.modelTable.currentObjects:
        if model in self.run.inputStructures:
          self.run.removeInputStructure(model)

      self.updateModels()

  def toggleModel(self, *opt):

    if self.model and self.run:
      if self.model in self.run.inputStructures:
        self.run.removeInputStructure(self.model)
      else:
        self.run.addInputStructure(self.model)

      self.updateModels()

  def toggleResidue(self, *opt):

    if self.residue:
      self.residue.useInCing = not self.residue.useInCing
      self.updateResidues()


  def updateResidues(self):

    if self.residue and (self.residue.topObject is not self.structure):
      self.residue = None

    textMatrix = []
    objectList = []
    colorMatrix = []

    if self.chain:
      chainCode = self.chain.code

      for residue in self.chain.sortedResidues():
        msResidue = residue.residue

        if not hasattr(residue, 'useInCing'):
          residue.useInCing = True

        if residue.useInCing:
          colors = [None, None, None, None, CING_BLUE]
          use = 'Yes'

        else:
          colors = [None, None, None, None, None]
          use = 'No'

        datum = [residue.seqCode,
                 msResidue.ccpCode,
                 msResidue.linking,
                 msResidue.descriptor,
                 use,]

        textMatrix.append(datum)
        objectList.append(residue)
        colorMatrix.append(colors)

    self.residueMatrix.update(objectList=objectList,
                              textMatrix=textMatrix,
                              colorMatrix=colorMatrix)


  def updateChains(self):

    index = 0
    names = []
    chains = []
    chain = self.chain

    if self.structure:
      chains = self.structure.sortedCoordChains()
      names = [chain.code for chain in chains]

      if chains:
        if chain not in chains:
          chain = chains[0]
          index = chains.index(chain)

        self.changeChain(chain)

    self.chainPulldown.setup(names, chains, index)


  def updateStructures(self):

    index = 0
    names = []
    structures = []
    structure = self.structure

    if self.run:
      model = self.run.findFirstInputStructure()
      if model:
        structure = model.structureEnsemble

      structures0 = [(s.ensembleId, s) for s in self.project.structureEnsembles]
      structures0.sort()

      for eId, structure in structures0:
        name = '%s:%s' % (structure.molSystem.code, eId)
        structures.append(structure)
        names.append(name)

    if structures:
      if structure not in structures:
        structure = structures[-1]

      index = structures.index(structure)

    self.changeStructure(structure)

    self.structurePulldown.setup(names, structures, index)


  def updateModels(self):

    textMatrix = []
    objectList = []
    colorMatrix = []

    if self.structure and self.run:
      used = self.run.inputStructures

      for model in self.structure.sortedModels():


        if model in used:
          colors = [None, CING_BLUE]
          use = 'Yes'

        else:
          colors = [None, None]
          use = 'No'

        datum = [model.serial,use]

        textMatrix.append(datum)
        objectList.append(model)
        colorMatrix.append(colors)

    self.modelTable.update(objectList=objectList,
                           textMatrix=textMatrix,
                           colorMatrix=colorMatrix)


  def changeStructure(self, structure):

    if self.project and (self.structure is not structure):
      self.project.currentEstructureEnsemble = structure
      self.structure = structure

      if self.run:
        self.run.inputStructures = structure.sortedModels()

      self.updateModels()
      self.updateChains()


  def changeChain(self, chain):

    if self.project and (self.chain is not chain):
      self.chain = chain
      self.updateResidues()

  def chooseValidScript(self):

    # Prepend default Cyana file extension below
    fileTypes = [  FileType('Python', ['*.py']), ]
    popup = FileSelectPopup(self, file_types = fileTypes,
                            title='Python file', dismiss_text='Cancel',
                            selected_file_must_exist = True)

    fileName = popup.getFile()
    self.validScriptEntry.set(fileName)
    popup.destroy()

  def updateAll(self, project=None):

    if project:
      self.project = project
      self.nmrProject = project.currentNmrProject
      simStore = project.findFirstNmrSimStore(application='CING') or \
                 project.newNmrSimStore(application='CING', name='CING')
    else:
      simStore = None

    if not self.project:
      return

    self.setZipFileName()
    if not self.project.currentNmrProject:
      name = self.project.name
      self.nmrProject = self.project.newNmrProject(name=name)
    else:
      self.nmrProject = self.project.currentNmrProject

    self.update(simStore)

  def update(self, simStore=None):

    NmrSimRunFrame.update(self, simStore)

    run = self.run
    urls = [DEFAULT_URL,]
    index = 0

    if run:
      userId = getRunParameter(run, iCingRobot.FORM_USER_ID)
      accessKey = getRunParameter(run, iCingRobot.FORM_ACCESS_KEY)
      if userId and accessKey:
        self.serverCredentials = [(iCingRobot.FORM_USER_ID, userId),
                                  (iCingRobot.FORM_ACCESS_KEY, accessKey)]

      url = getRunParameter(run, ICING_BASE_URL)
      if url:
        htmlUrl = getRunParameter(run, HTML_RESULTS_URL)
        self.iCingBaseUrl = url
        self.resultsUrl = htmlUrl # May be None

      self.resultUrlEntry.set(self.resultsUrl)

      if self.iCingBaseUrl and self.iCingBaseUrl not in urls:
        index = len(urls)
        urls.append(self.iCingBaseUrl)

    self.iCingBaseUrlPulldown.setup(urls, urls, index)

    self.updateButtons()
    self.updateStructures()
    self.updateModels()
    self.updateChains()

  def updateButtons(self, event=None):

    buttons = self.buttonBar.buttons
    if self.project and self.run:
      buttons[0].enable()

      if self.resultsUrl and self.serverCredentials:
        buttons[1].enable()
        buttons[2].enable()
        buttons[3].enable()

      else:
        buttons[1].disable()
        buttons[2].disable()
        buttons[3].disable()

    else:
      buttons[0].disable()
      buttons[1].disable()
      buttons[2].disable()
      buttons[3].disable()

def getModelsString(run):

  models = run.inputStructures
  serials = [m.serial for m in models]

  if not serials:
    return

  ranges = []
  start = serials[0]
  end = start
  for i in serials[1:]:
    if i == end+1:
      end = i
    else:
      ranges.append((start,end))
      start = end = i

  ranges.append((start,end))

  texts = []
  for start, end in ranges:
    if start == end:
      text = '%d' % (start)
    else:
      text = '%d-%d' % (start,end)

    texts.append(text)

  return ','.join(texts)

def getResiduesString(structure):

  texts = []
  chains = structure.sortedCoordChains()

  for chain in chains:
    seqCodes = []
    for residue in chain.residues:
      if not hasattr(residue, 'useInCing') or residue.useInCing:
        seqCodes.append(residue.seqCode)
    seqCodes.sort()

    if len(chains) > 1:
      prefix = chain.code
    else:
      prefix = ''

    ranges = []
    start = seqCodes[0]
    end = start
    for i in seqCodes[1:]:
      if i == end+1:
        end = i
      else:
        ranges.append((start,end))
        start = end = i

    ranges.append((start,end))

    for start, end in ranges:
      if start == end:
        text = '%s%d' % (prefix,start)
      else:
        text = '%s%d-%d' % (prefix,start,end)

      texts.append(text)

  return ','.join(texts)

def deleteRunParameter(run, code, idNum=1):

  runParameter = run.findFirstRunParameter(code=code, id=idNum)

  if runParameter:
    return runParameter.delete()

def setRunParameter(run, code, textValue, idNum=1):

  runParameter = run.findFirstRunParameter(code=code, id=idNum) or \
                 run.newRunParameter(code=code, id=idNum)
  runParameter.textValue = textValue

def getRunParameter(run, code, idNum=1):

  runParameter = run.findFirstRunParameter(code=code, id=idNum)

  if runParameter:
    return runParameter.textValue

