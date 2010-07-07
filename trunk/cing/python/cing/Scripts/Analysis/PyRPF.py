#@PydevCodeAnalysisIgnore

# TBD Later
# Notifiers, in on valid objects, peak Lists, ensembles

# What about atoms we don't have a chemical shift for?

# Isotope labelling schemes

# Possible:

# [Separate Unexplained Peak List]
# Are you sure you want to move these peaks to a separate list?
# JFD: if it was a question to me then I would answer yes.
#
# Run like:
# python -u $CINGROOT/python/cing/Scripts/Analysis/PyRPF.py

from ccp.util.Software import getMethodStore
from ccpnmr.analysis.core.AssignmentBasic import clearPeakDim, assignResToDim
from ccpnmr.analysis.core.AssignmentBasic import findMatchingPeakDimShifts, getBoundResonances
from ccpnmr.analysis.core.ConstraintBasic import getPeakDimTolerance
from ccpnmr.analysis.core.ExperimentBasic import getOnebondDataDims, getDataDimIsotopes, findSpectrumDimsByIsotope
from ccpnmr.analysis.core.ExperimentBasic import getThroughSpacePeakLists, getDataDimRefFullRange, getPrimaryDataDimRef
from ccpnmr.analysis.core.MarkBasic import createNonPeakMark
from ccpnmr.analysis.core.MoleculeBasic import getNumConnectingBonds, areResonancesBound, getBoundAtoms
from ccpnmr.analysis.core.PeakBasic import pickPeak, setupPeak
from ccpnmr.analysis.core.StructureBasic import getAtomSetCoords
from ccpnmr.analysis.core.StructureBasic import getAtomSetsDistance
from ccpnmr.analysis.core.Util import getAnalysisDataDim
from ccpnmr.analysis.core.Util import getAnalysisPeakList
from ccpnmr.analysis.core.WindowBasic import getDataDimAxisMapping
from ccpnmr.analysis.frames.PeakTableFrame import PeakTableFrame # This is the table for missing peaks with built-in functionalities
from math import sqrt
from memops.editor.BasePopup import BasePopup
from memops.gui.ButtonList import UtilityButtonList, ButtonList
from memops.gui.CheckButton import CheckButton
from memops.gui.FloatEntry import FloatEntry
from memops.gui.Frame import Frame
from memops.gui.Label import Label
from memops.gui.MessageReporter import showOkCancel
from memops.gui.PartitionedSelector import PartitionedSelector
from memops.gui.ProgressBar import ProgressBar
from memops.gui.PulldownList import PulldownList
from memops.gui.ScrolledGraph import ScrolledGraph
from memops.gui.ScrolledMatrix import ScrolledMatrix
from memops.gui.TabbedFrame import TabbedFrame
import time
#from ccpnmr.analysis.core.WindowBasic import getWindowPaneName #@UnusedImport
#from memops.gui.Button import Button #@UnusedImport
#from ccpnmr.analysis.core.AssignmentBasic import makeResonanceGuiName #@UnusedImport
#from ccpnmr.analysis.core.Util import getDataDimAssignmentTolerance #@UnusedImport
#from ccpnmr.analysis.frames.PeakTableFrame import PeakTableFrame #@UnusedImport









# Colours for graphs
RPF_COLORS = ['#4000B0','#FFA000','#A0A0A0', '#606060']

# Max num Ca to H intra residue bonds
MAX_BONDS = {'Ala':2, 'Cys':3, 'Asp':2, 'Glu':3,
             'Phe':6, 'Gly':2, 'His':5, 'Ile':4,
             'Lys':6, 'Leu':4, 'Met':5, 'Asn':4,
             'Pro':3, 'Gln':5, 'Arg':7, 'Ser':3,
             'Thr':3, 'Val':3, 'Trp':7, 'Tyr':7}


# Used to calulate aximum Ca to Ca distance for any of a residue's protons
# to be possibly touching
MAX_BOND_LEN = 1.5

nn = ('N','N')
cn = ('C','N')
nc = ('N','C')
cc = ('C','C')

# This dictionary says how different numbers of 13C, 15N bound
# dimensions limits which protons would be visible in a spectrum
# given 13C or 15N connectivity
# Context is ('N','N),('C','N'),('C','C') for 2D NOESY i.e. any 1H to any 1H
# ('N','N),('C','N') for 3D HSQC-NOESY, ('C','C') for 4D HCCH NOESY etc..

CN_DIM_CONTEXT_DICT = {(0,0):(cc, cn, nc, nn),
                       (1,0):(cc, cn, nc),
                       (0,1):(cn, nc, nn),
                       (1,1):(cn, nc),
                       (2,0):(cc,),
                       (0,2):(nn,),}

# Colour scheme for missing peaks, according to distance

DISTANCE_COLORS = {0:'#FF8080',1:'#FFA080',
                   2:'#FFC080',3:'#FFE080',
                   4:'#FFFF80',5:'#C0FF80',
                   6:'#80FF80',7:'#80FF80'}

PROG = 'RPF'
RECALL  = 'Recall'
PRECISION = 'Precision'
F_MEASURE = 'F-Measure'
DP_SCORE = 'DP-Score'
RECALL_ALL  = 'Overall_Recall'
PRECISION_ALL = 'Overall_Precision'
F_MEASURE_ALL= 'Overall_F-Measure'
PKLIST_VALID = 'PeakListValidation'
PEAK_VALID = 'PeakValidation'
SHIFT_VALID = 'NmrMeasurementValidation'
UNEXPLAINED = 'Unexplained_Peak'
RESIDUE_VALID = 'ResidueValidation'
MISSING_PEAK = 'Shift_Missing_Peak'
MISSING_PEAK_LIST_TAG = 'RPF Missing Peaks'

DEFAULT_DISTANCE_THRESHOLD = 4.8 # Angstrom units default to runRPF was 5.0 before.
DEFAULT_PROCHIRAL_EXCLUSION_SHIFT = 0.04 # PPM units
DEFAULT_DIAGONAL_EXCLUSION_SHIFT = 0.3 # PPM units default to runRPF was 0.1 before.
DEFAULT_CONSIDER_ALIASED_POSITIONS = True
RPF_USE = "rpfUse"

def pyRpfMacro(argServer):

  popup = PyRpfPopup(argServer.parent, argServer.getProject()) #@UnusedVariable

class PyRpfPopup(BasePopup):

  def __init__(self, parent, project):

    self.parent = parent
    self.project = project
    self.nmrProject = project.currentNmrProject
    self.analysisProject = project.currentAnalysisProject
    self.peakList = None
    self.ensemble = None
    self.validStore = None
    self.validPeakList = None
    self.mark = None

    BasePopup.__init__(self, parent, title='PyRPF')

  def body(self, guiFrame):

    self.geometry('800x600')

    guiFrame.grid_columnconfigure(0, weight=1)
    guiFrame.grid_rowconfigure(0, weight=1)

    options = ['Peak Lists','Ensembles','Results Table',
               'Unexplained Peaks','Missing Peaks','Graph']
    self.tabbedFrame = TabbedFrame(guiFrame, options=options,
                                   callback=self.selectTab)
    frameA, frameB, frameC, frameD, frameE, frameF = self.tabbedFrame.frames
    self.tabbedFrame.grid(row=0, column=0, sticky='nsew')

    #
    # Peak Lists
    #

    frameA.grid_columnconfigure(0, weight=1)
    frameA.grid_rowconfigure(1, weight=1)

    frame = Frame(frameA)
    frame.grid(row=0, column=0, sticky='ew')
    frame.grid_columnconfigure(6, weight=1)

    label = Label(frame, text='Diagonal Exclusion (PPM):')
    label.grid(row=0,column=0, sticky='w')
    self.diagonalEntry = FloatEntry(frame, text=str(DEFAULT_DIAGONAL_EXCLUSION_SHIFT), width=8)
    self.diagonalEntry.grid(row=0,column=1, sticky='w')

    label = Label(frame, text='Consider Aliased Positions?')
    label.grid(row=0,column=2, sticky='w')
    self.aliasedSelect = CheckButton(frame, selected=DEFAULT_CONSIDER_ALIASED_POSITIONS)
    self.aliasedSelect.grid(row=0,column=3, sticky='w')

    label = Label(frame, text='Prochiral Exclusion (PPM):')
    label.grid(row=0,column=4, sticky='w')
    self.prochiralEntry = FloatEntry(frame, text=str(DEFAULT_PROCHIRAL_EXCLUSION_SHIFT), width=8)
    self.prochiralEntry.grid(row=0,column=5, sticky='w')

    headingList = ['Spectrum','Peak List','Use?','Num Peaks']
    editGetCallbacks = [None, None, self.togglePeakList, None]
    editSetCallbacks = [None] * 4
    editWidgets = [None] * 4

    self.peakListTable = ScrolledMatrix(frameA, headingList=headingList,
                                    editSetCallbacks=editSetCallbacks,
                                    editGetCallbacks=editGetCallbacks,
                                    editWidgets=editWidgets,
                                    callback=self.selectPeakList)
    self.peakListTable.grid(row=1, column=0, sticky='nsew')

    #
    # Ensembles
    #
    frameB.grid_columnconfigure(0, weight=1)
    frameB.grid_rowconfigure(1, weight=1)

    frame = Frame(frameB)
    frame.grid(row=0, column=0, sticky='ew')
    frame.grid_columnconfigure(2, weight=1)

    label = Label(frame, text=u'Distance Threshold (\u00C5)')
    label.grid(row=0,column=0, sticky='w')
    self.distanceEntry = FloatEntry(frame, text=str(DEFAULT_DISTANCE_THRESHOLD), width=8)
    self.distanceEntry.grid(row=0,column=1, sticky='w')

    editGetCallbacks = [None, None, self.toggleEnsemble, None]
    editSetCallbacks = [None] * 4
    editWidgets = [None] * 4
    headingList = ['Mol System','Ensemble','Use?','Num Models']
    self.ensembleTable = ScrolledMatrix(frameB, headingList=headingList,
                                        editSetCallbacks=editSetCallbacks,
                                        editGetCallbacks=editGetCallbacks,
                                        editWidgets=editWidgets,
                                        multiSelect=True,
                                        callback=self.selectEnsemble)
    self.ensembleTable.grid(row=1, column=0, sticky='nsew')

    texts = ['Enable Selected','Disable Selected']
    commands = [self.enableSelectedEnsembles, self.disbleSelectedEnsembles]
    self.ensembleButtons = ButtonList(frameB, texts=texts, commands=commands)
    self.ensembleButtons.grid(row=2, column=0, sticky='ew')

    #
    # Results table
    #
    frameC.grid_columnconfigure(0, weight=1)
    frameC.grid_rowconfigure(0, weight=1)

    headingList = ['Ensemble', 'PeakList(s)',
                   'Recall', 'Precision', 'F-measure',
                   'DP Score', 'Unexplained\nPeaks',
                   'Missing\nPeaks']
    self.resultsTable = ScrolledMatrix(frameC, headingList=headingList,
                                       multiSelect=True,
                                       callback=self.selectResult)
    self.resultsTable.grid(row=0, column=0, sticky='nsew')

    texts = ['Show Unexplained Peaks','Show Missing Peaks',
             'Show Residue Graph','Delete Results']
    commands = [self.showUnexplainedPeaks, self.showMissingPeaks,
                self.showResidueGraph, self.deleteResults]
    self.resultsButtons = ButtonList(frameC, texts=texts, commands=commands)
    self.resultsButtons.grid(row=1, column=0, sticky='ew')

    #
    # Unexplained peaks
    #

    frameD.grid_columnconfigure(2, weight=1)
    frameD.grid_rowconfigure(1, weight=1)

    label = Label(frameD, text='Result Set:')
    label.grid(row=0,column=0, sticky='w')
    self.resultPulldownA = PulldownList(frameD, self.changeResultSet)
    self.resultPulldownA.grid(row=0,column=1, sticky='w')

    texts = ['Next Location','Prev Location']
    commands = [self.nextUnexplainedPeak, self.prevUnexplainedPeak]
    self.unexplainedPeakButtons = ButtonList(frameD, texts=texts, commands=commands)
    self.unexplainedPeakButtons.grid(row=0, column=3,  sticky='w')

    self.unexplainedPeakTable = RpfPeakTable(frameD, self.parent, self)
    self.unexplainedPeakTable.grid(row=1, column=0, columnspan=4, sticky='nsew')

    #
    # Missing peaks
    #

    frameE.grid_columnconfigure(2, weight=1)
    frameE.grid_rowconfigure(1, weight=1)

    label = Label(frameE, text='Result Set:')
    label.grid(row=0,column=0, sticky='w')
    self.resultPulldownB = PulldownList(frameE, self.changeResultSet)
    self.resultPulldownB.grid(row=0,column=1, sticky='w')

    texts = ['Next Location','Prev Location']
    commands = [self.nextMissingPeak, self.prevMissingPeak]
    self.missingPeakButtons = ButtonList(frameE, texts=texts, commands=commands)
    self.missingPeakButtons.grid(row=0, column=3,  sticky='w')

    self.missingPeakTable = RpfPeakTable(frameE, self.parent, self)
    self.missingPeakTable.grid(row=1, column=0, columnspan=4, sticky='nsew')

    #
    # Graph
    #

    frameF.grid_columnconfigure(1, weight=1)
    frameF.grid_rowconfigure(2, weight=1)

    label = Label(frameF, text='Result Set:')
    label.grid(row=0,column=0, sticky='w')
    self.resultPulldownC = PulldownList(frameF, self.changeResultSet)
    self.resultPulldownC.grid(row=0,column=1, sticky='w')

    labels = [RECALL, PRECISION, F_MEASURE, DP_SCORE]
    self.graphSelector = PartitionedSelector(frameF, self.updateResidueGraph,
                                             labels=labels, objects=labels,
                                             selected=labels, colors=RPF_COLORS)
    self.graphSelector.grid(row=1, column=0, columnspan=2, sticky='ew')


    self.residueScoreGraph = ScrolledGraph(frameF, graphType='line',
                                    width=600, height=400)
    self.residueScoreGraph.grid(row=2, column=0, columnspan=2, sticky='nsew')

    #
    # Main
    #

    texts = ['Run RPF',]
    commands = [self.runRpf,]
    self.utilButtons = UtilityButtonList(self.tabbedFrame.sideFrame,
                                         texts=texts, commands=commands)
    self.utilButtons.grid(row=0, column=0, sticky='e')
    self.utilButtons.buttons[0].config(bg='#B0B0FF')

    self.updatePeakLists()
    self.updateEnsembles()
    self.updateResultPulldowns()
    self.administerNotifiers(self.registerNotify)

  def open(self):

    self.updatePeakLists()
    self.updateEnsembles()
    self.updateWindows()
    self.updateResultPulldowns()

    BasePopup.open(self)

  def destroy(self):

    self.administerNotifiers(self.unregisterNotify)
    BasePopup.destroy(self)

  def administerNotifiers(self, notifyFunc):

    # Peak Tables

    for func in ('__init__', 'delete'):
      for clazz in ('ccp.nmr.Nmr.PeakDimContrib',):
        notifyFunc(self.unexplainedPeakTable.contribUpdateAfter, clazz, func)
        notifyFunc(self.missingPeakTable.contribUpdateAfter, clazz, func)

    for func in ('__init__', 'delete','setName'):
      notifyFunc(self.unexplainedPeakTable.updateWindowListsAfter, 'ccpnmr.Analysis.SpectrumWindow', func)
      notifyFunc(self.missingPeakTable.updateWindowListsAfter, 'ccpnmr.Analysis.SpectrumWindow', func)

    for func in ('__init__', 'delete','setAnnotation','setDetails','setFigOfMerit'):
      notifyFunc(self.unexplainedPeakTable.updatePeaksAfter, 'ccp.nmr.Nmr.Peak', func)
      notifyFunc(self.missingPeakTable.updatePeaksAfter, 'ccp.nmr.Nmr.Peak', func)

    for func in ('setAnnotation','setPosition','setNumAliasing','setLineWidth'):
      notifyFunc(self.unexplainedPeakTable.peakDimUpdateAfter, 'ccp.nmr.Nmr.PeakDim', func)
      notifyFunc(self.missingPeakTable.peakDimUpdateAfter, 'ccp.nmr.Nmr.PeakDim', func)

    for func in ('__init__', 'delete', 'setValue'):
      notifyFunc(self.unexplainedPeakTable.intensityUpdateAfter, 'ccp.nmr.Nmr.PeakIntensity', func)
      notifyFunc(self.missingPeakTable.intensityUpdateAfter, 'ccp.nmr.Nmr.PeakIntensity', func)

  def changeResultSet(self, result):

    if result and (result != (self.validStore, self.validPeakList)):
      self.validStore, self.validPeakList = result
      # Only need to update the selected panel
      self.selectTab(self.tabbedFrame.selected)


  def updateResultPulldowns(self):

    index = 0
    names = []
    resultSets = []

    # For missing peaks, which conly considers individial lists
    indexP = 0
    namesP = []
    resultSetsP = []

    # For per-residue sccores, which considers all peak lists
    indexR = 0
    namesR = []
    resultSetsR = []

    for ensemble in getEnsembles(self.project):

      if hasattr(ensemble, 'rpfUse') and not ensemble.rpfUse:
        continue

      validStore = getEnsembleValidationStore(ensemble)
      rpfdu = getOverallRpfValidation(validStore)
      recall, _precision, _fMeasure, dpScore, _unexplained, _missing = rpfdu

      ensembleText = 'Ensemble %s:%d' % (ensemble.molSystem.code, ensemble.ensembleId)

      if dpScore is None:
        continue

      result = (validStore, None)
      name = '%s, <All peak lists>' % (ensembleText)

      names.append(name)
      resultSets.append(result)

      namesR.append(name)
      resultSetsR.append(result)

      for peakList in recall.peakLists:
        spectrum = peakList.dataSource
        peakListText = 'Peak List %s:%s:%d' % (spectrum.experiment.name,
                                               spectrum.name,
                                               peakList.serial)

        names.append('%s, %s' % (ensembleText,peakListText))
        namesP.append('%s, %s' % (ensembleText,peakListText))
        resultSets.append((validStore, peakList))
        resultSetsP.append((validStore, peakList))

    if resultSets:
      result = (self.validStore, self.validPeakList)

      if result not in resultSets:
        result = resultSets[0]

      index = resultSets.index(result)

    else:
      self.changeResultSet((None, None))

    if resultSetsP:
      result = (self.validStore, self.validPeakList)

      if result not in resultSetsP:
        result = resultSetsP[0]
        self.changeResultSet(result)

      indexP = resultSetsP.index(result)

    if resultSetsR:
      result = (self.validStore, None)

      if result not in resultSetsR:
        result = resultSetsR[0]

      indexR = resultSetsR.index(result)

    # All pulldowns are coordinated
    self.resultPulldownA.setup(names, resultSets, index)
    self.resultPulldownB.setup(namesP, resultSetsP, indexP)
    self.resultPulldownC.setup(namesR, resultSetsR, indexR)


  def nextMissingPeak(self):

    table = self.missingPeakTable.scrolledMatrix
    objectList = table.objectList

    if objectList:
      obj = table.currentObject
      if obj:
        index = objectList.index(obj)
        index += 1

        if index >= len(objectList):
          index = 0

      else:
        index = 0

      table.selectNthObject(index)
      self.missingPeakTable.findPeak()

  def prevMissingPeak(self):

    table = self.missingPeakTable.scrolledMatrix
    objectList = table.objectList

    if objectList:

      obj = table.currentObject
      if obj:
        index = objectList.index(obj)
        index -= 1
        if index < 0:
          index = len(objectList)-1

      else:
        index = 0

      table.selectNthObject(index)
      self.missingPeakTable.findPeak()

  def nextUnexplainedPeak(self):

    table = self.unexplainedPeakTable.scrolledMatrix
    objectList = table.objectList

    if objectList:
      obj = table.currentObject
      if obj:
        index = objectList.index(obj)
        index += 1

        if index >= len(objectList):
          index = 0

      else:
        index = 0

      table.selectNthObject(index)
      self.unexplainedPeakTable.findPeak()

  def prevUnexplainedPeak(self):

    table = self.unexplainedPeakTable.scrolledMatrix
    objectList = table.objectList

    if objectList:

      obj = table.currentObject
      if obj:
        index = objectList.index(obj)
        index -= 1
        if index < 0:
          index = len(objectList)-1

      else:
        index = 0

      table.selectNthObject(index)
      self.unexplainedPeakTable.findPeak()

  def selectShifts(self, shifts, row, col):

    if self.window and self.validStore and self.validPeakList:

      peakList = self.validPeakList
      spectrum = peakList.dataSource


      dimMapping = getDataDimAxisMapping(spectrum, self.window)
      boundDims  = getOnebondDataDims(spectrum)
      print "boundDims: %s" % boundDims
      shiftPairs = []
      for shift in shifts:
        print "looking at shift: %s" % shift
        bound = getBoundResonances(shift.resonance) or []

        shiftX = None
        if len(bound) == 1:
          resonanceX = bound[0]
          shiftX = resonanceX.findFirstShift(parentList=shift.parentList)

        shiftPairs.append((shift, shiftX))

      dataDims = spectrum.sortedDataDims()

      axisDict = {}
      for axis in dimMapping.keys():
        axisDict[dimMapping[axis]] = axis

      position = {}

      # Map bound shifts to bound dataDims
      for dataDim1, dataDim2 in boundDims:
        print "looking at dataDim1: %s" % dataDim1
        print "looking at dataDim2: %s" % dataDim2
        dataDimRef1 = getPrimaryDataDimRef(dataDim1)
        dataDimRef2 = getPrimaryDataDimRef(dataDim2)

        ppmMin1, ppmMax1 = getDataDimRefFullRange(dataDimRef1)
        ppmMin2, ppmMax2 = getDataDimRefFullRange(dataDimRef2)

        isotopes1 = getDataDimIsotopes(dataDim1)
        isotopes2 = getDataDimIsotopes(dataDim2)

        for shift, shiftX in shiftPairs:

          if not shiftX:
            continue

          if not (ppmMin1 < shift.value < ppmMax1):
            continue

          if not (ppmMin2 < shiftX.value < ppmMax2):
            continue

          isotopeA = shift.resonance.isotopeCode
          isotopeB = shiftX.resonance.isotopeCode

          if (isotopeA in isotopes1) and (isotopeB in isotopes2):
            position[axisDict[dataDim1]] = shift.value
            position[axisDict[dataDim2]] = shiftX.value
            dataDims.remove(dataDim1)
            dataDims.remove(dataDim2)
            shiftPairs.remove((shift, shiftX))
            break
          elif (isotopeB in isotopes1) and (isotopeA in isotopes2):
            position[axisDict[dataDim2]] = shift.value
            position[axisDict[dataDim1]] = shiftX.value
            dataDims.remove(dataDim1)
            dataDims.remove(dataDim2)
            shiftPairs.remove((shift, shiftX))
            break

      # Map remaining dims by isotope
      for dataDim in dataDims:
        isotopes = getDataDimIsotopes(dataDim)

        for shift, shiftX in shiftPairs:
          if shift.resonance.isotopeCode in isotopes:
             position[axisDict[dataDim]] = shift.value
             shiftPairs.remove((shift, shiftX))
             break
          elif shiftX and (shiftX.resonance.isotopeCode in isotopes):
             position[axisDict[dataDim]] = shift.value
             shiftPairs.remove((shift, shiftX))
             break

      # Navigate in window frame
      windowFrame = self.window.getWindowFrame()
      windowFrame.gotoPosition(position=position)

      # Place marker lines
      ppms = []
      axisTypes = []
      for axis in position:
        ppms.append(position[axis])
        axisPanel = self.window.findFirstAxisPanel(label=axis)
        axisTypes.append(axisPanel.axisType)

      if self.mark and not self.mark.isDeleted:
        self.mark.delete()

      self.mark = createNonPeakMark(ppms, axisTypes, lineWidth=1,
                                    dashLength=2, gapLength=2, color=None)

  def selectResult(self, obj, row, col):

    validStore, peakList = obj
    self.validStore = validStore
    self.validPeakList = peakList


#  def getNoeTolerances(self, peakList):
#
#    dimTolerances = []
#    spectrum = peakList.dataSource
#
#    for dataDim in spectrum.sortedDataDims():
#
#      analysisDataDim = getAnalysisDataDim(dataDim)
#
#      #tol = getAnalysisDataDim(dataDim).noeTolerance or \
#      tol = analysisDataDim.assignTolerance
#
#      dimTolerances.append([dataDim, tol, 1, tol])
#
#    return dimTolerances

  def runRpf(self):

    peakLists = [pl for pl in self.peakListTable.objectList if pl.rpfUse]
    ensembles = [e for e in self.ensembleTable.objectList if e.rpfUse]

    progressBar = ProgressBar(self,  text='RPF')
    diagonalExclusion = self.diagonalEntry.get() or 0.0
    doAlised = self.aliasedSelect.get()
    prochiralExclusion = self.prochiralEntry.get() or 0.0
    distThreshold = self.distanceEntry.get() or DEFAULT_DISTANCE_THRESHOLD

    validResultStores = []

    if peakLists and ensembles:
      tolerances = []

      for peakList in peakLists:
        tolerances.append(getNoeTolerances(peakList))

      validResultStores = calcRPF(ensembles, peakLists, tolerances,
                                  distThreshold, prochiralExclusion,
                                  diagonalExclusion, doAlised,
                                  progressBar=progressBar)

    progressBar.destroy()

    self.updateResultsTable()

    self.tabbedFrame.select(2)

    return validResultStores

  def selectTab(self, index):

    funcs = {2:self.updateResultsTable,
             3:self.updateUnexplainedPeaks,
             4:self.updateMissingPeaks,
             5:self.updateResidueGraph}

    updateFunc = funcs.get(index)
    if updateFunc:
      updateFunc()

    self.updateResultPulldowns()

  def updateMissingPeaks(self):

    if self.validStore:
      validObj = getOverallRpfValidation(self.validStore)[5]

      if self.validPeakList:
        synthetic = getSyntheticMissingPeaksList(self.validPeakList)
        peaks = [p for p in validObj.sortedPeaks() if p.peakList is synthetic]
      else:
        peaks = validObj.sortedPeaks()

    else:
      peaks = []

    self.missingPeakTable.peaks = peaks
    self.missingPeakTable.updatePeaksAfter()


  def updateUnexplainedPeaks(self):

    if self.validStore:
      validObj = getOverallRpfValidation(self.validStore)[4]

      if self.validPeakList:
        selected = self.validPeakList
        peaks = [p for p in validObj.peaks if p.peakList is selected]
      else:
        peaks = validObj.peaks

    else:
      peaks = []

    self.unexplainedPeakTable.peaks = peaks
    self.unexplainedPeakTable.updatePeaksAfter()


  def showUnexplainedPeaks(self):

    if self.validStore:
      # self.selectEnsembleU(self.validStore)
      # self.selectPeakListU(self.validPeakList)

      self.tabbedFrame.select(3)

  def showMissingPeaks(self):

    if self.validStore:
      # self.selectEnsembleM(self.validStore)

      self.tabbedFrame.select(4)

  def showResidueGraph(self):

    if self.validStore:
      # self.selectEnsembleR(self.validStore)

      self.tabbedFrame.select(5)

  def deleteResults(self):

    msg = 'Really delete selected RPF results?'
    if not showOkCancel('Confirm', msg, parent=self):
      return

    validStores = set()
    for validStore, peakList in self.resultsTable.currentObjects: #@UnusedVariable
      validStores.add(validStore)

    for validStore in validStores:
      validStore.delete()

    self.validStore = None
    self.validPeakList = None
    self.updateResultsTable()

  def updateResultsTable(self):

    textMatrix = []
    objectList = []
    textMatrixAppend = textMatrix.append
    objectListAppend = objectList.append

    ensembles = getEnsembles(self.project)
    for ensemble in ensembles:

      if hasattr(ensemble, 'rpfUse') and not ensemble.rpfUse:
        continue

      validStore = getEnsembleValidationStore(ensemble)

      ensembleText = '%s:%d' % (ensemble.molSystem.code, ensemble.ensembleId)

      rpfdu = getOverallRpfValidation(validStore)
      recall, precision, fMeasure, dpScore, unexplained, missing = rpfdu

      if dpScore is None:
        continue

      datum = [ensembleText, '<All>',
               recall.floatValue, precision.floatValue,
               fMeasure.floatValue, dpScore.floatValue,
               len(unexplained.peaks), len(missing.peaks)]

      textMatrix.append(datum)
      objectList.append((validStore, None))

      peakLists = recall.peakLists

      numUnexplained = {}
      numMissing = {}
      for peakList in peakLists:
        numUnexplained[peakList] = 0
        syntheticPeakList = getSyntheticMissingPeaksList(peakList)
        numMissing[syntheticPeakList] = 0

      for peak in unexplained.peaks:
        numUnexplained[peak.peakList] += 1

      for peak in missing.peaks:
        numMissing[peak.peakList] += 1

      for peakList in peakLists:
        spectrum = peakList.dataSource
        peakListData = (spectrum.experiment.name, spectrum.name, peakList.serial)
        peakListText = '%s:%s:%d' % peakListData
        syntheticPeakList = getSyntheticMissingPeaksList(peakList)
        recall, precision, fMeasure, dpScore = getPeakListRpfValidation(validStore, peakList)

        datum = [ensembleText, peakListText,
                 recall.floatValue, precision.floatValue,
                 fMeasure.floatValue, dpScore.floatValue,
                 numUnexplained[peakList],
                 numMissing[syntheticPeakList]]

        textMatrixAppend(datum)
        objectListAppend((validStore, peakList))

    self.resultsTable.update(textMatrix=textMatrix, objectList=objectList)

  def updateResidueGraph(self, null=None):

    symbols0 = ['triangle','circle','square','square']
    dataNames0 = [RECALL, PRECISION, F_MEASURE, DP_SCORE]
    symbols = []
    dataSets = []
    dataNames = []
    dataColors = []
    indices = []

    for i, state in enumerate(self.graphSelector.state):
      if state:
        dataSets.append([])
        dataNames.append(dataNames0[i])
        symbols.append(symbols0[i])
        indices.append(i)
        dataColors.append(RPF_COLORS[i])

    if self.validStore:
      validStore = self.validStore
      ensemble = self.validStore.structureEnsemble

      for chain in ensemble.sortedCoordChains():
        for residue in chain.sortedResidues():
           rpfd = getResidueRpfValidation(validStore, residue)
           seqCode = residue.seqCode

           for i, j  in enumerate(indices):
             if rpfd[j] is None:
               continue
             dataSets[i].append((seqCode, rpfd[j].floatValue))

    self.residueScoreGraph.update(dataSets=dataSets, dataNames=dataNames,
                           symbols=symbols, dataColors=dataColors,
                           xLabel='Residue', yLabel='Score',
                           title='RPF Ensemble Analysis ')
    self.residueScoreGraph.draw()


  def selectPeakList(self, peakList, row, col):

    self.peakList = peakList

  def selectEnsemble(self, ensemble, row, col):

    self.ensemble = ensemble

  def disbleSelectedEnsembles(self):

    ensembles = self.ensembleTable.currentObjects
    for ensemble in ensembles:
       ensemble.rpfUse = False
    self.updateEnsembles()

  def enableSelectedEnsembles(self):

    ensembles = self.ensembleTable.currentObjects
    for ensemble in ensembles:
       ensemble.rpfUse = True
    self.updateEnsembles()


  def togglePeakList(self, peakList):

    peakList.rpfUse = not peakList.rpfUse
    self.updatePeakLists()

  def toggleEnsemble(self, ensemble):

    ensemble.rpfUse = not ensemble.rpfUse
    self.updateEnsembles()

  def getActivePeakLists(self):

    peakLists = []

    for peakList in getThroughSpacePeakLists(self.project):
      if not peakList.peaks:
        continue

      if hasattr(peakList, 'rpfUse') and (peakList.rpfUse is True):
        peakLists.append(peakList)

    return peakLists

  def updatePeakLists(self):

    peakLists = getThroughSpacePeakLists(self.project)


    textMatrix = []
    colorList = []
    objectList = []

    for peakList in peakLists:
      if not peakList.peaks:
        continue

      if peakList.isSimulated:
        continue

      spectrum = peakList.dataSource
      experiment = spectrum.experiment

      specName = '%s:%s' % (experiment.name, spectrum.name)

      if not hasattr(peakList, 'rpfUse'):
        peakList.rpfUse = True

      if peakList.rpfUse:
        useText = 'Yes'
        colors = ['#B0FFB0'] * 4

      else:
        useText = 'No'
        colors = [None] * 4

      datum = [specName,
               peakList.serial,
               useText,
               len(peakList.peaks),]

      objectList.append(peakList)
      textMatrix.append(datum)
      colorList.append(colors)

    self.peakListTable.update(textMatrix=textMatrix,
                              objectList=objectList,
                              colorMatrix=colorList)

#  def getEnsembles(self):
#
#    ensembles = []
#
#    for molSystem in self.project.molSystems:
#      for ensemble in molSystem.structureEnsembles:
#        ensembles.append((molSystem.code, ensemble.ensembleId, ensemble))
#
#    ensembles.sort()
#
#    return [x[2] for x in ensembles]

  def updateEnsembles(self):

    ensembles = getEnsembles(self.project)

    textMatrix = []
    colorList = []

    for ensemble in ensembles:

      if not hasattr(ensemble, 'rpfUse'):
        ensemble.rpfUse = False

      if ensemble.rpfUse:
        useText = 'Yes'
        colors = ['#B0FFB0'] * 4
      else:
        useText = 'No'
        colors = [None] * 4


      datum = [ensemble.molSystem.code,
               ensemble.ensembleId,
               useText,
               len(ensemble.models)]
      textMatrix.append(datum)
      colorList.append(colors)

    self.ensembleTable.update(textMatrix=textMatrix,
                              objectList=ensembles,
                              colorMatrix=colorList)

class RpfPeakTable(PeakTableFrame):

  def __init__(self, parent, analysis, rpf, nmrProject=None, peakList=None,
               peaks=None, simplified=True, *args, **kw):

    self.rpf = rpf
    PeakTableFrame.__init__(self, parent, analysis, nmrProject, peakList,
                            peaks, simplified, *args, **kw)
  def updateButtons(self):

    buttons = list(self.bottomButtons1.buttons)
    buttons += self.bottomButtons2.buttons
    n = len(buttons)

    if self.peak:
      for i in range(1,n):
        buttons[i].enable()

      self.windowLabel.config(fg = 'black')
      #self.windowPulldown.activate()

    else:
      for i in range(1,n):
        buttons[i].disable()


  def getHeadings(self, n):

    dataList, tipTexts = PeakTableFrame.getHeadings(self, n)

    dataList.insert(n+3, 'Dist.')
    tipTexts.insert(n+3, 'Structure distance between hydrogens')
    return dataList, tipTexts

  def getPeakData(self, peak, n, simplified=True):

    data = PeakTableFrame.getPeakData(self, peak, n, simplified)
    validStore = self.rpf.validStore
    colors = [None] * 14

    if validStore:
      ensemble = validStore.structureEnsemble
      distDims = self.getDistanceDimensions(peak.peakList.dataSource)
      atomSets = []
      peakDims = peak.sortedPeakDims()
      peakDimA = peakDims[distDims[0]]
      peakDimB = peakDims[distDims[1]]
      for peakDim in (peakDimA, peakDimB):
        assignedSets = []

        for contrib in peakDim.peakDimContribs:
          resonanceSet = contrib.resonance.resonanceSet

          if resonanceSet:
            assignedSets.extend( list(resonanceSet.atomSets) )

        atomSets.append( assignedSets )

      if atomSets and atomSets[0] and atomSets[1]:
        dist = getAtomSetsDistance(atomSets[0], atomSets[1],
                                   ensemble, method='min')

        colors[n+3] = DISTANCE_COLORS.get(int(dist))

      else:
        dist = None

    else:
      dist = None

    data.insert(n+3, dist)

    return data, colors

  def showStructConnections(self):

    validStore = self.rpf.validStore
    if validStore:
      ensemble = validStore.structureEnsemble

      peaks = list(self.scrolledMatrix.currentObjects)
      if peaks:
        self.analysisApp.viewStructure(ensemble)
        popup = self.analysisApp.popups['view_structure']
        popup.clearConnections()

        for peak in peaks:
          popup.showPeakConnection(peak)

  def getEditData(self, n):

    editWidgets, editGetCallbacks, editSetCallbacks = PeakTableFrame. getEditData(self, n)

    editWidgets.insert(n+3, None)
    editGetCallbacks.insert(n+3, None)
    editSetCallbacks.insert(n+3, None)

    return editWidgets, editGetCallbacks, editSetCallbacks

  def updatePeaksFromSelection(self):

    self.peaks = [pk for pk in self.peaks if not pk.isDeleted]

#    textMatrix = []
    peaks = self.peaks

    n = 0
    for peak in peaks:
      m = peak.peakList.dataSource.numDim
      if m > n:
        n = m

    simplified = self.simplified
    getPeakData = self.getPeakData
    textMatrix = []
    colorMatrix = []
    for peak in peaks:
      datum, colors = getPeakData(peak,n, simplified)
      textMatrix.append(datum)
      colorMatrix.append(colors)

    (editWidgets,editGetCallbacks,editSetCallbacks) = self.getEditData(n)

    headingList, tipTexts = self.getHeadings(n)
    self.scrolledMatrix.update(objectList=peaks,
                               textMatrix=textMatrix,
                               colorMatrix=colorMatrix,
                               editWidgets=editWidgets,
                               editGetCallbacks=editGetCallbacks,
                               editSetCallbacks=editSetCallbacks,
                               tipTexts=tipTexts,
                               headingList=headingList)

    self.scrolledMatrix.refreshScrollbars()

    if len(peaks) == 1:
      self.scrolledMatrix.selectObject(peaks[0])

    self.waiting = False

def calcRPF(ensembles, peakLists, tolerances,
            distThreshold=DEFAULT_DISTANCE_THRESHOLD,
            prochiralTolerance=DEFAULT_PROCHIRAL_EXCLUSION_SHIFT,
            diagonalTolerance=DEFAULT_DIAGONAL_EXCLUSION_SHIFT,
            aliasing=DEFAULT_CONSIDER_ALIASED_POSITIONS,
            progressBar=None,
            verbose=False):
  """Descrn: Function to calculate recall, precision and F-Measure
             for the comparison between close 1H distances in
             structures and the possible ambiguous assignments in NOESY
             peakLists. Currently only the first float in the tolerance
             sub-list is used. If peak positions are within 1H prochiral
             threshold then only one crosspeak is expected.
             Boooleans to set whether diagonal peaks are considered and
             whether aliased resonance positions should be considered (slow)
             Optional progress bar is for graphical display.
     Inputs: List of MolStructure.StructureEnsembles, List of Nmr.PeakLists,
             List of 4-List of (Nmr.DataDim, Float (Tolerance), Float, Float),
             Float (Angstrom), Float (PPM), Float (PPM), Boolean,
             memops.gui.ProgressBar
     Output: Dict of Resonance:[Dict of Resonance:Float]
             - i.e. dict[resonance1][resonance2] = dist
  """

  # First work out which heteroatoms are required to be connected
  heteroAtomContexts = set()
  peakListHeteroAtomContexts = {}
  badDist = distThreshold+1.0
  badNoe = badDist**-6.0

  # Loop through input peak lists
  for peakList in peakLists:

    # spectrum is parent link form peak list
    spectrum = peakList.dataSource

    # Initialise counters for number of N & C spectrum dims
    nitrogenDims = 0
    carbonDims = 0

    # Use ExperimentBasic function from Analysis to
    # get the bounds data (spectrum) dimension objects
    for dataDim1, dataDim2 in getOnebondDataDims(spectrum):

      # Use nother Experiment basic funxtion to get isotope types
      isotopes = list(getDataDimIsotopes(dataDim1)) + \
                 list(getDataDimIsotopes(dataDim2))

      # Count N & C
      # Mixed N+C axes do not count as they don't filter
      if '15N' in isotopes:
        if '13C' not in isotopes: # Not mixed N/C axis
          nitrogenDims += 1

      if '13C' in isotopes:
        if '15N' not in isotopes: # Not mixed N/C axis
          carbonDims += 1

    # Get the heteroatom contexts from the global dict
    contexts = CN_DIM_CONTEXT_DICT.get((carbonDims,nitrogenDims))

    # Check num of N & C dims makes sense
    if not contexts:
      print 'Peak list %s has unusable axes' % peakList
      continue

    # Which heteroatoms are required to be
    # connected in this peakList
    peakListHeteroAtomContexts[peakList] = contexts

    # Add heteroatom contexts to current available set
    heteroAtomContexts.update(contexts)



  # Collect ambiguous peak-resonance assignments

  t0 = time.time()
  print  "Getting resonance-resonance possible peak assignments within tolerances"
  resonancePeaks = {}
  peakPossibilities = {}
  unexplainedPeaksDict = {}


  for i, peakList in enumerate(peakLists):
    spec = peakList.dataSource
    pId = '%s:%s:%d' % (spec.experiment.name, spec.name, peakList.serial)
    print 'Peak List %s' % pId

    if progressBar:
      progressBar.text = 'Searching %s \npeaks for possible assignments' % pId
      progressBar.open()
      progressBar.set(0)
      progressBar.update()

    data = getAmbigNoeConn([peakList,], [tolerances[i],],
                            diagonalTolerance, aliasing, progressBar)

    resonanceData, peakData, unexplained = data
    resonancePeaks[peakList] = resonanceData
    peakPossibilities[peakList] = peakData
    unexplainedPeaksDict[peakList] = unexplained

  print "  Time taken:", time.time() - t0

  print "Getting resonance-resonance NOE distances"

  resonanceDists = {}

  # Collect resonances that are close in structure
  for ensemble in ensembles:
    t0 = time.time()

    if progressBar:
      eId = '%s:%d' % (ensemble.molSystem.code, ensemble.ensembleId)
      progressBar.text = 'Searching structure %s\nfor close atoms' % eId
      progressBar.open()
      progressBar.set(0)
      progressBar.update()

    print "Ensemble", ensemble.ensembleId
    resonanceDists[ensemble] = getProtonDistsConn(ensemble,
                                                  heteroAtomContexts,
                                                  distThreshold,
                                                  progressBar)

    print "  Time taken:", time.time() - t0

  t0 = time.time()
  print  "Calculating scores and making CCPN validation objects"

  # List for CCPN validation objects
  validationResults = []

  # Loop through each ensemble
  for ensemble in ensembles:
    # Fetch resonance distances for this ensemble
    rDists = resonanceDists[ensemble]

    if progressBar:
      eId = '%s:%d' % (ensemble.molSystem.code, ensemble.ensembleId)
      progressBar.text = 'Calculating & storing\nscores for ensmble %s' % eId

    # List for false neg result peaks
    unexplainedPeaks = set()

    # List for false pos result shift intersections
    missingPeaks = set()

    # The list of working resonances is simply
    # the list of objects used as keys in the dictionary
    # of structurally close resonances
    resonances = rDists.keys()
    n = len(resonances)

    # Find or make an object to store the results in the CCPN model
    validStore = getEnsembleValidationStore(ensemble)

    # Store validation object for output
    validationResults.append(validStore)

    # Initialise all-peakList counters
    # Note triples are used to store the full,
    # local & free chain counts for determining DP score
    truePosA = [0,0,0]
    truePosNoeA = [0.0,0.0,0.0]
    falsePosNoeA = [0.0,0.0,0.0]
    falseNegA = [0,0,0]


    # Initialise per-residue counter dictionaries
    truePosR = {}
    truePosNoeR = {}
    falsePosNoeR = {}
    falseNegR = {}

    # Dictionary to quickly get from mol system residue to
    # the ensemble residue
    ensembleResidueDict = {}

    # Set per-residue counters to zero for each residue
    for chain in ensemble.coordChains:
      for residue in chain.residues:
         # Use triples for full, local and free chain scores
         truePosR[residue] = [0,0,0]
         truePosNoeR[residue] = [0.0,0.0,0.0]
         falsePosNoeR[residue] = [0.0,0.0,0.0]
         falseNegR[residue] = [0,0,0]

         # Link from molSystem residue to ensemble residue for later
         ensembleResidueDict[residue.residue] = residue

    for peakList in peakLists:
      # Get peak list's spectrum (dataSource)
      spectrum = peakList.dataSource

      # Determine which dimensions are bound
      boundDims  = {}
      for dataDim1, dataDim2 in getOnebondDataDims(spectrum):
        boundDims[dataDim1] = dataDim2
        boundDims[dataDim2] = dataDim1

      # Get the PPM ranges of the 1H dims
      rangesPpm = []
      for dataDim in spectrum.dataDims:
        dataDimRef = getPrimaryDataDimRef(dataDim)

        if '1H' in dataDimRef.expDimRef.isotopeCodes:
          hRange = getDataDimRefFullRange(dataDimRef)
          xRange = (None, None)
          xIsotopes = ()
          boundDim = boundDims.get(dataDim)

          if boundDim:
            boundDimRef = getPrimaryDataDimRef(boundDim)
            xRange = getDataDimRefFullRange(boundDimRef)
            xIsotopes = boundDimRef.expDimRef.isotopeCodes

          rangesPpm.append( (hRange,xRange,xIsotopes) )


      # Get correct shift list from this peak lists experiment
      shiftList = spectrum.experiment.shiftList

      # Get valid hetero atom contexts for this peak list
      # e.g. ('N','C') or ('C','N') or ('N','N') for 15N HSQC NOESY
      hetContexts = peakListHeteroAtomContexts[peakList]

      # Fetch ambig assign possibilities for this peakList
      rPeaks = resonancePeaks[peakList]
      peakPoss = peakPossibilities[peakList]

      # Initialise counters for this peak list
      # Use triples for full, local and free chain scores
      truePos = [0,0,0]
      truePosNoe = [0.0,0.0,0.0]
      falsePosNoe = [0.0,0.0,0.0]
      falseNeg = [0,0,0]

      # Dictionary to check if we've seen a pair of potentially
      # ambiguous prochiral resonances before
      prochiralCheck = {}

      # Pairs of close chemical shifts which
      # should have a peak but don't
      shiftsMissingPeaks = []

      # Dict to lookup explained peaks, for speed
      explainedPeaks = {}
      explainedPeaksFree = {}

      if progressBar:
        progressBar.total = n-1
        progressBar.set(0)
        progressBar.open()

      # Compare close resonances
      # with those possibly represented by peaks
      for i in range(n-1):
        resonance1 = resonances[i]

        # Check resonance has a chemical shift
        shift1 = resonance1.findFirstShift(parentList=shiftList)
        if not shift1:
          continue

        # Get chemical shift in ppm
        ppm1 = shift1.value

        # Get bound Resonance
        ppm1x = None
        xIsotope1 = None
        hetElements = []
        for bound in getBoundResonances(resonance1):
          xIsotope1 = bound.isotopeCode
          shiftX = bound.findFirstShift(parentList=shiftList)

          if shiftX and bound.isotope:
            ppm1x = shiftX.value

            # Get list of bound hetero atom types
            hetElements.append(bound.isotope.chemElement.symbol)


        # Check within spectrum ppm range
        # Other ppm check depends on this result
        otherRangesPpm = []
        for r, (hRange, xRange, xIsotopes) in enumerate(rangesPpm):
          ppmMin, ppmMax = hRange
          ppmMinX, ppmMaxX = xRange

          if ppmMin <=  ppm1 <= ppmMax:
            if ppmMinX is not None:
              if (xIsotope1 in xIsotopes)  and (ppmMinX <= ppm1x <= ppmMaxX):
                # Matches, next resonance must match _other_ range
                otherRangesPpm.append(rangesPpm[1-r])

            else:
              # Matches, next resonance must match _other_ range
              otherRangesPpm.append(rangesPpm[1-r])

        # If nothing within range, skip this resonance
        if not otherRangesPpm:
          continue

        # Get resonance set (link between prochirals)
        resonanceSet1 = resonance1.resonanceSet

        # Get atoms & residue
        atomSet1 = resonanceSet1.findFirstAtomSet()
        atom1 = atomSet1.findFirstAtom()
        residue1 = ensembleResidueDict.get(atom1.residue)
        if not residue1:
          # Residue is missing in structure
          continue

        for j in range(i+1, n):
          resonance2 = resonances[j]
          resonanceSet2 = resonance2.resonanceSet
          atom2 = resonanceSet2.findFirstAtomSet().findFirstAtom()

          ppm2x = None
          xIsotope2 = None
          hetElements2 = hetElements[:]
          for bound in getBoundResonances(resonance2):
            xIsotope2 = bound.isotopeCode
            shiftX = bound.findFirstShift(parentList=shiftList)

            if shiftX and bound.isotope:
              ppm2x = shiftX.value
              hetElements2.append(bound.isotope.chemElement.symbol)

          # Check bound resonances are the right kind for spectrum
          if tuple(hetElements2) not in hetContexts:
            continue

          shift2 = resonance2.findFirstShift(parentList=shiftList)
          if not shift2:
            continue

          ppm2 = shift2.value

          # If shifts similar, expect no peak, so skip
          if abs(ppm1-ppm2) < diagonalTolerance:
            continue

          # Check within spectrum ppm range
          for hRange, xRange, xIsotopes in otherRangesPpm:
            ppmMin, ppmMax = hRange
            ppmMinX, ppmMaxX = xRange

            if ppmMin <=  ppm2 <= ppmMax:
              if ppmMinX is None:
                break

              elif (xIsotope2 in xIsotopes) and (ppmMinX <=  ppm2x <= ppmMaxX):
                break

          else:
            # Not in a range, skip
            continue

          # Check if seen this assignment pairing before
          # e.g. from the other resonances of two prochiral pairs
          prochiralShifts = prochiralCheck.get((resonanceSet1, resonanceSet2))
          if prochiralShifts:
            # If have seem prochiral before
            # skip if other resonance has very similar shift
            if abs(ppm1-prochiralShifts[0]) < prochiralTolerance:
              continue
            if abs(ppm2-prochiralShifts[1]) < prochiralTolerance:
              continue

          else:
            # Cache shifts for subsequent prochiral checks
            prochiralCheck[(resonanceSet1, resonanceSet2)] = (ppm1, ppm2)
            prochiralCheck[(resonanceSet2, resonanceSet1)] = (ppm2, ppm1)

          atomSet2 = resonanceSet2.findFirstAtomSet()
          residue2 = ensembleResidueDict.get(atomSet2.findFirstAtom().residue)
          if not residue2:
            # Residue is missing in structure
            continue

          # Get resonance distances
          # Get equiv NOE
          dist, noe = rDists[resonance1].get(resonance2, (badDist, badNoe))


          # Number of connecting bonds
          nBonds = getNumConnectingBonds(atom1, atom2, limit=10) or 0

          if dist < distThreshold:
            close = True
          else:
            close = False

          # See if resonance represented in peak assign dict
          if rPeaks.get(resonance1):
            # This could give None if the two resonances do
            # not coincide at a peak
            peak = rPeaks[resonance1].get(resonance2)
          else:
            peak = None

          #if not peak:
          #  for peakListB in peakLists:
          #    subDict = resonancePeaks[peakListB].get(resonance1)
          #
          #    if subDict:
          #      peak = subDict.get(resonance2)
          #
          #    if peak:
          #      break

          if close and peak:

            # Counts & Noes
            truePos[0] += 1
            truePosA[0] += 1
            truePosR[residue1][0] += 1
            truePosNoe[0] += noe
            truePosNoeA[0] += noe
            truePosNoeR[residue1][0] += noe
            if residue1 is not residue2:
              truePosR[residue2][0] += 1
              truePosNoeR[residue2][0] += noe

            explainedPeaks[peak] = True

            # Get local counts for estimating ideal Fmeasure
            if 1 < nBonds < 4:
              truePos[1] += 1
              truePosA[1] += 1
              truePosR[residue1][1] += 1
              truePosNoe[1] += noe
              truePosNoeA[1] += noe
              truePosNoeR[residue1][1] += noe
              if residue1 is not residue2:
                truePosR[residue2][1] += 1
                truePosNoeR[residue2][1] += noe

          elif close and (not peak):

            falsePosNoe[0] += noe
            falsePosNoeA[0] += noe
            falsePosNoeR[residue1][0] += noe
            if residue1 is not residue2:
              falsePosNoeR[residue2][0] += noe

            # Get local counts for estimating ideal Fmeasure
            if 1 < nBonds < 4:
              falsePosNoe[1] += noe
              falsePosNoeA[1] += noe
              falsePosNoeR[residue1][1] += noe
              if residue1 is not residue2:
                falsePosNoeR[residue2][1] += noe

            # Store close chemical shifts without peaks
            shifts = frozenset([shift1, shift2])
            shiftsMissingPeaks.append((dist, shifts))

          elif (not close) and peak and (peak.peakList is peakList):

            # Check to see whether we've seen this peak before
            # e.g. from another pair of resonances
            if not explainedPeaks.has_key(peak):

              # Check no other resonance pairs are close for this peak
              for resonance3, resonance4, atom3, atom4 in peakPoss[peak]:
                if not rDists.get(resonance3):
                  continue

                dist2, _noe2 = rDists[resonance3].get(resonance4, (badDist, badNoe))

                if dist2 < distThreshold:
                  # Found another close resonance pair
                  explainedPeaks[peak] = True
                  break

              else:
                # Otherwise nothing explains this peak
                falseNeg[0] += 1
                falseNegA[0] += 1

                # Spread the per-residue precision violations
                # over all the resonance pairs that match the peak
                matchingResonances = peakPoss[peak]
                if matchingResonances:
                  frac = 1.0/len(matchingResonances)
                  for resonance3, resonance4, atom3, atom4 in peakPoss[peak]:
                    residue3 = ensembleResidueDict.get(atom3.residue)
                    residue4 = ensembleResidueDict.get(atom4.residue)

                    if residue3:
                      falseNegR[residue3][0] += frac

                      if residue4 and (residue3 is not residue4):
                        falseNegR[residue4][0] += frac

                unexplainedPeaks.add(peak)
                explainedPeaks[peak] = False

          elif not close and not peak:
            # True negative
            pass


          # Repeat logic, but for the null-hypothesis
          # i.e. a freely rotating chain

          if not nBonds: # Gave up, too many bonds
            closeFree = False
            freeNoe = 0.0

          else:
            freeNoe =  sqrt(getRandomChainDist(nBonds))**-6.0
            if getRandomChainDist(nBonds) < (distThreshold*distThreshold):
              # Use null-hypothesis (free chain) distance squared
              closeFree = True

            else:
              closeFree = False

          if closeFree and peak:
            truePos[2] += 1
            truePosA[2] += 1
            truePosR[residue1][2] += 1
            truePosNoe[2] += freeNoe
            truePosNoeA[2] += freeNoe
            truePosNoeR[residue1][2] += freeNoe
            if residue1 is not residue2:
              truePosR[residue2][2] += 1
              truePosNoeR[residue2][2] += freeNoe

            explainedPeaksFree[peak] = True

          elif closeFree and (not peak):
            falsePosNoe[2] += freeNoe
            falsePosNoeA[2] += freeNoe
            falsePosNoeR[residue1][2] += freeNoe
            if residue1 is not residue2:
              falsePosNoeR[residue2][2] += freeNoe

          elif (not closeFree) and peak and (peak.peakList is peakList):

            # Check to see whether we've seen this peak before
            # e.g. from another pair of resonances
            if not explainedPeaksFree.has_key(peak):

              # Check no other resonance pairs are close for this peak
              for resonance3, resonance4, atom3, atom4 in peakPoss[peak]:
                nBonds = getNumConnectingBonds(atom3, atom4, limit=6)

                if nBonds:
                  dist2 = getRandomChainDist(nBonds)

                  if dist2 < (distThreshold*distThreshold):
                    # Found another close resonance pair
                    explainedPeaksFree[peak] = True
                    break

              else:
                # Otherwise nothing explains this peak
                falseNeg[2] += 1
                falseNegA[2] += 1

                # Spread the per-residue precision violations
                # over all the resonance pairs that match the peak
                matchingResonances = peakPoss[peak]
                if matchingResonances:
                  frac = 1.0/len(matchingResonances)
                  for resonance3, resonance4, atom3, atom4 in peakPoss[peak]:
                    residue3 = ensembleResidueDict.get(atom3.residue)
                    residue4 = ensembleResidueDict.get(atom4.residue)

                    if residue3:
                      falseNegR[residue3][2] += frac

                      if residue4 and (residue3 is not residue4):
                        falseNegR[residue4][2] += frac

                #unexplainedPeaks.add(peak)
                explainedPeaksFree[peak] = False

          elif not closeFree and not peak:
            pass

        if progressBar:
          progressBar.increment()

      # Add-in peaks missed by all resonances
      falseNeg[0] += len(unexplainedPeaksDict[peakList])
      falseNeg[2] += len(unexplainedPeaksDict[peakList])

      # Calculate reporting parameters
      # Values for only for this ensemble and one peak list
      recall, precision, fMeasure = countsToRpf(truePos[0], falseNeg[0],
                                                truePosNoe[0], falsePosNoe[0])
      dpScore = calcDpScore(fMeasure, truePos, falseNeg,
                            truePosNoe, falsePosNoe)

      if progressBar:
        progressBar.close()

      # Predict missing peak locations
      #print peakList.dataSource.name
      peakListM = predictMissingPeaks(peakList, shiftsMissingPeaks, progressBar)
      missingPeaks.update(peakListM.peaks)

      # Store results in CCPN objects
      storePeakListRpfValidation(validStore, peakList, recall,
                                 precision, fMeasure, dpScore)

    # Overall values for ensemble
    for peakList in peakLists:
      falseNegA[0] += len(unexplainedPeaksDict[peakList])
      falseNegA[2] += len(unexplainedPeaksDict[peakList])
      unexplainedPeaks.update(set(unexplainedPeaksDict[peakList]))

    recall, precision, fMeasure = countsToRpf(truePosA[0], falseNegA[0],
                                              truePosNoeA[0], falsePosNoeA[0])
    dpScore = calcDpScore(fMeasure, truePosA, falseNegA,
                          truePosNoeA, falsePosNoeA)

    # Update CCPN objects to store overall results
    storeOverallRpfValidation(validStore, peakLists,
                              unexplainedPeaks, missingPeaks,
                              recall, precision, fMeasure, dpScore)


    for residue in truePosR.keys():

      rpf = countsToRpf(truePosR[residue][0],
                        falseNegR[residue][0],
                        truePosNoeR[residue][0],
                        falsePosNoeR[residue][0])

      recall, precision, fMeasure = rpf

      if sum([recall, precision, fMeasure]):
        dpScore = calcDpScore(fMeasure, truePosR[residue],
                              falseNegR[residue],
                              truePosNoeR[residue],
                              falsePosNoeR[residue])

        # Store per-residue validation objects
        storeResidueRpfValidation(validStore, residue, recall,
                                  precision, fMeasure, dpScore)

  print "  Time taken:", time.time() - t0

  return validationResults

def countsToRpf(truePos, falseNeg, truePosNoe, falsePosNoe, verbose=False):
  """Descrn: Calculate recall, precision & F-measure from
             counts of missing peaks (falsePos),
             unexplained peaks (falseNeg) & found peaks (truePos)
     Inputs: Float, Float, Float
     Output: Float, Float, Float
  """

  if verbose:
    print "countsToRpf", falseNeg, truePos, truePosNoe, falsePosNoe

  if not truePos:
    return 0.0, 0.0, 0.0

  # Unexplained peaks
  recall = truePos / float(truePos + falseNeg)

  # Missing peaks
  precision = truePosNoe / float(truePosNoe + falsePosNoe)

  fMeasure = 2*recall*precision / (recall+precision)

  return recall, precision, fMeasure


def getRandomChainDist(n, l=1.50, a=0.33333333333333333):
  """Descrn: Get the average distance squared between atoms separated by a
             given number of bonds, assuming a freely rotating chain.
     Inputs: Int, Float, Float
     Output: Float
  """

  ma = 1.0-a

  r2 = n * l * l * (((1.0+a)/ma) - ((2*a*(1.0-pow(a,n)))/(n*ma*ma)))

  return r2

def calcDpScore(fMeasure, truePos, falseNeg, truePosNoe, falsePosNoe, verbose=False):
  """Descrn: Calculate descriminating Power score by comparing F-measure
             with its expected upper and lower limits
     Inputs: Float, 3-List of Floats,  3-List of Floats, 3-List of Floats,
     Output: Float
  """

  #if verbose:
  #  print "calcDpScore", fMeasure, truePos, falseNeg, truePosNoe, falsePosNoe

  if not (truePosNoe[1] + falsePosNoe[1]):
    return 0.0

  rFree, pFree, fFree = countsToRpf(truePos[2], falseNeg[2], truePosNoe[2], falsePosNoe[2])
  #rIdeal, pIdeal, fIdeal = countsToRpf(truePos[1], falseNeg[1], truePosNoe[1], falsePosNoe[1])
  rQuery, pQuery, fQuery = countsToRpf(truePos[0], falseNeg[0], truePosNoe[0], falsePosNoe[0])

  pIdeal = truePosNoe[1]/ (truePosNoe[1] + falsePosNoe[1])

  rIdeal = 1.0
  fIdeal = 2*pIdeal / (rIdeal + pIdeal)


  if verbose:
    print " Free  %.3f, %.3f, %.3f" % (rFree,  pFree, fFree)
    print " Ideal %.3f, %.3f, %.3f" % (rIdeal, pIdeal, fIdeal)
    print " Query %.3f, %.3f, %.3f" % (rQuery, pQuery, fQuery)

  if not fIdeal-fFree:
    return 0.0

  dpScore = (fMeasure-fFree)/(fIdeal-fFree)

  # Bounding required for per-residue scores
  # due to low counts
  return min(1.0, max(0.0, dpScore))

def getSyntheticMissingPeaksList(peakList):
  """Descrn: For a regular peak list fetch any existing, or make a new
             sister peak list (same spectrum) that can hold predictions
             for missing NOE peaks.
     Inputs: Nmr.PeakList
     Output: Nmr.PeakList
  """

  dataSource = peakList.dataSource

  syntheticPeakList = dataSource.findFirstPeakList(name=MISSING_PEAK_LIST_TAG,
                                                 isSimulated=True)
  if not syntheticPeakList:
    syntheticPeakList = dataSource.newPeakList(name=MISSING_PEAK_LIST_TAG,
                          details='Missing peaks expected from structure',
                          isSimulated=True)

  analysisPeakList = getAnalysisPeakList(syntheticPeakList)

  color = '#FF0000'
  analysisPeakList.symbolStyle = '+'
  analysisPeakList.symbolColor = color
  analysisPeakList.textColor = color

  return syntheticPeakList

def predictMissingPeaks(peakList, shiftPairs, progressBar=None):
  """Descrn: Store chemical shift intersections as synthetic 'missing'
             peaks.
     Inputs: Nmr.PeakList,  List of 2-Tuples of (2-Set of Nmr.Shifts, Float)
             memops.gui.ProgressBar
     Output: None
  """

  spectrum = peakList.dataSource
  unit = spectrum.experiment.shiftList.unit
  dataDims = spectrum.sortedDataDims()
  boundDims = getOnebondDataDims(spectrum)
  nDim = len(dataDims)

  syntheticPeakList = getSyntheticMissingPeaksList(peakList)

  dataDimDict = {}
  for dataDim in dataDims:
    dataDimRef = getPrimaryDataDimRef(dataDim)
    ppmMin, ppmMax = getDataDimRefFullRange(dataDimRef)
    isotopes = getDataDimIsotopes(dataDim)
    dataDimDict[dataDim] = (dataDimRef, ppmMin, ppmMax, isotopes)

  peakDict = {}
  peaks = syntheticPeakList.sortedPeaks()
  for j, peak in enumerate(peaks):
    peakDict[j] = peak

  nShifts = len(shiftPairs)
  shiftPairs.sort()

  if progressBar:
    sName = spectrum.name
    eName = spectrum.experiment.name
    progressBar.text = 'Making synthetic "missing" peaks\nfor %s:%s' % (eName, sName)
    progressBar.total = nShifts
    progressBar.open()
    progressBar.set(0)
    progressBar.update()

  for i, (_dist, shifts) in enumerate(shiftPairs):
    shiftPairs = []

    for shift in shifts:
      bound = getBoundResonances(shift.resonance) or []

      shiftX = None
      if len(bound) == 1:
        resonanceX = bound[0]
        shiftX = resonanceX.findFirstShift(parentList=shift.parentList)

      shiftPairs.append((shift, shiftX))

    position = [None] * nDim
    assignment = [None] * nDim

    for dataDim1, dataDim2 in boundDims:
      _dataDimRef1, ppmMin1, ppmMax1, isotopes1 = dataDimDict[dataDim1]
      _dataDimRef2, ppmMin2, ppmMax2, isotopes2 = dataDimDict[dataDim2]
      dim1 = dataDim1.dim-1
      dim2 = dataDim2.dim-1

      for shift, shiftX in shiftPairs:

        if not shiftX:
          continue

        if not (ppmMin1 < shift.value < ppmMax1):
          continue

        if not (ppmMin2 < shiftX.value < ppmMax2):
          continue

        resonanceA = shift.resonance
        resonanceB = shiftX.resonance

        isotopeA = resonanceA.isotopeCode
        isotopeB = resonanceB.isotopeCode

        if (isotopeA in isotopes1) and (isotopeB in isotopes2):
          position[dim1] = shift.value
          position[dim2] = shiftX.value
          assignment[dim1] = resonanceA
          assignment[dim2] = resonanceB
          shiftPairs.remove((shift, shiftX))
          break
        elif (isotopeB in isotopes1) and (isotopeA in isotopes2):
          position[dim2] = shift.value
          position[dim1] = shiftX.value
          assignment[dim2] = resonanceA
          assignment[dim1] = resonanceB
          shiftPairs.remove((shift, shiftX))
          break

    # Map remaining dims by isotope
    for dataDim in dataDims:
      dim = dataDim.dim - 1

      if position[dim] is not None:
        continue

      dataDimRef, ppmMin, ppmMax, isotopes = dataDimDict[dataDim]

      for shift, shiftX in shiftPairs:
        resonance = shift.resonance

        if resonance.isotopeCode in isotopes:
           position[dim] = shift.value
           assignment[dim] = resonance
           shiftPairs.remove((shift, shiftX))
           break
        elif shiftX and (shiftX.resonance.isotopeCode in isotopes):
           position[dim] = shiftX.value
           assignment[dim] = shiftX.resonance
           shiftPairs.remove((shift, shiftX))
           break

    if None in position:
      continue

    peak = peakDict.get(i)
    if peak:
      peakDims = peak.sortedPeakDims()
      for k, peakDim in enumerate(peakDims):
        peakDim.value = position[k]
        clearPeakDim(peakDim)

      setupPeak(peak, doFit=False)

    else:
      peak = pickPeak(syntheticPeakList, position, unit, doFit=False)
      peakDims = peak.sortedPeakDims()

    for k, peakDim in enumerate(peakDims):
      assignResToDim(peakDim, assignment[k])

    if progressBar:
      progressBar.increment()

  nOrig = len(peaks)
  if nOrig > nShifts:
    for peak in peaks[nShifts+1:]:
      peak.delete()

  if progressBar:
    progressBar.close()

  return syntheticPeakList

def getEnsembleValidationStore(ensemble):
  """Descrn: Get a CCPN object to store validation results for an ensemble
     Inputs: MolStructure.StructureEnsemble
     Output: Validation.ValidationStore
  """

  memopsRoot = ensemble.root
  eid = '%s_%s' % (PROG, ensemble.guid)
  validStore = ensemble.findFirstValidationStore(name=eid)

  if validStore is None:
    software = getSoftware(memopsRoot)
    validStore = memopsRoot.newValidationStore(name=eid, software=software,
                                               structureEnsemble=ensemble)

  validStore.nmrProject = memopsRoot.currentNmrProject

  keywordStore = memopsRoot.findFirstKeywordDefinitionStore(context=PROG)

  if not keywordStore:
    keywordStore = memopsRoot.newKeywordDefinitionStore(context=PROG)

  for keyword in (RECALL,PRECISION, F_MEASURE, UNEXPLAINED, MISSING_PEAK,
                  RECALL_ALL, PRECISION_ALL, F_MEASURE_ALL, DP_SCORE):
    if not keywordStore.findFirstKeywordDefinition(keyword=keyword):
      keywordStore.newKeywordDefinition(keyword=keyword)

  return validStore

def storeResidueRpfValidation(validStore, residue, recall,
                              precision, fMeasure, dpScore):
  """Descrn: Store the RPF results for an ensemble, over all peak lists
             in CCPN validation objects.
     Inputs: Validation.ValidationStore,
             MolStructure.Residue, Float, Float, Float, Float
     Output: 3-Tuple of Validation.ResidueValidation
  """
  # define data model call for new result
  newValidation = validStore.newResidueValidation

  # Find any existing residue validation objects
  rpfd = getResidueRpfValidation(validStore, residue)
  residueRecall, residuePrecision, residueFmeasure, residueDpScore = rpfd
  residues = [residue,]

  # Check or make residue 'Recall' validation result object
  if not residueRecall:
    residueRecall = newValidation(context=PROG, keyword=RECALL, residues=residues)

  # Check or make residue 'Precision' validation result object
  if not residuePrecision:
    residuePrecision = newValidation(context=PROG, keyword=PRECISION, residues=residues)

  # Check or make residue 'Fmeasure' validation result object
  if not residueFmeasure:
    residueFmeasure = newValidation(context=PROG, keyword=F_MEASURE, residues=residues)

  # Check or make residue 'DpScore' validation result object
  if not residueDpScore:
    residueDpScore = newValidation(context=PROG, keyword=DP_SCORE, residues=residues)

  # Set values
  residueRecall.floatValue = recall
  residuePrecision.floatValue = precision
  residueFmeasure.floatValue = fMeasure
  residueDpScore.floatValue = dpScore

  return residueRecall, residuePrecision, residueFmeasure, residueDpScore


def getResidueRpfValidation(validStore, residue):
  """Descrn: Get any existing RPF residue validation results from data model
     Inputs: Validation.ValidationStore, MolStructure.Residue
     Output: 3-Tuple of Validation.PeakListValidation
  """
  # Define data model call to find existing result
  findValidation = residue.findFirstResidueValidation

  residueRecall = findValidation(validationStore=validStore,
                                 context=PROG, keyword=RECALL)

  residuePrecision = findValidation(validationStore=validStore,
                                    context=PROG, keyword=PRECISION)

  residueFmeasure = findValidation(validationStore=validStore,
                                   context=PROG, keyword=F_MEASURE)

  residueDpScore = findValidation(validationStore=validStore,
                                   context=PROG, keyword=DP_SCORE)

  return residueRecall, residuePrecision, residueFmeasure, residueDpScore



def storeOverallRpfValidation(validStore, peakLists, peaksU, peaksM,
                              recall, precision, fMeasure, dpScore):
  """Descrn: Store the RPF results for a an ensemble, over all peak lists
             in CCPN validation objects.
     Inputs: Validation.ValidationStore,
             List of Nmr.PeakLists, List if Nmr.Peaks,
             Float, Float, Float, Float
     Output: 3-Tuple of Validation.PeakListValidation
  """

  # Get any existing RPF all-peaklist results
  validObjs = getOverallRpfValidation(validStore)
  allRecall, allPrecision, allFmeasure, allDpScore = validObjs[:4]
  unexplainedPeaks, missingPeaks = validObjs[4:]

  # define data model call for new result
  newValidation = validStore.newPeakListValidation

  # Check or make new 'Recall' validation result for ensemble
  if not allRecall:
    allRecall = newValidation(context=PROG, keyword=RECALL_ALL)

  # Check or make new ;'Precision' validation result for ensemble
  if not allPrecision:
    allPrecision = newValidation(context=PROG, keyword=PRECISION_ALL)

  # Check or make new 'Fmeasure' validation result for ensemble
  if not allFmeasure:
    allFmeasure = newValidation(context=PROG, keyword=F_MEASURE_ALL)

  # Check or make new 'DpScore' validation result for ensemble
  if not allDpScore:
    allDpScore = newValidation(context=PROG, keyword=DP_SCORE)

  # Check or make validation result for unexplained peaks
  if not unexplainedPeaks:
    unexplainedPeaks = validStore.newPeakValidation(context=PROG, keyword=UNEXPLAINED)

  # Check or make validation result for missing peaks
  if not missingPeaks:
    missingPeaks = validStore.newPeakValidation(context=PROG, keyword=MISSING_PEAK)

  # Refresh peakLists
  allRecall.peakLists = peakLists
  allPrecision.peakLists = peakLists
  allFmeasure.peakLists = peakLists
  allDpScore.peakLists = peakLists

  # Refresh peaks
  unexplainedPeaks.peaks = peaksU
  missingPeaks.peaks = peaksM

  # Store the actual values
  allRecall.floatValue = recall
  allPrecision.floatValue = precision
  allFmeasure.floatValue = fMeasure
  allDpScore.floatValue = dpScore

  # Return validation objects
  return allRecall, allPrecision, allFmeasure, allDpScore, unexplainedPeaks

def getOverallRpfValidation(validStore):
  """Descrn: Get any existing RPF all-peaklist results from CCPN validation objects.
     Inputs: Validation.ValidationStore
     Output: 3-Tuple of Validation.PeakListValidation
  """
  # Define data model call to find existing result
  findValidation = validStore.findFirstValidationResult

  allRecall = findValidation(className=PKLIST_VALID, context=PROG, keyword=RECALL_ALL)
  allPrecision = findValidation(className=PKLIST_VALID, context=PROG, keyword=PRECISION_ALL)
  allFmeasure = findValidation(className=PKLIST_VALID, context=PROG, keyword=F_MEASURE_ALL)
  allDpScore = findValidation(className=PKLIST_VALID, context=PROG, keyword=DP_SCORE)
  unexplainedPeaks = findValidation(className=PEAK_VALID, context=PROG, keyword=UNEXPLAINED)
  missingPeaks = findValidation(className=PEAK_VALID, context=PROG, keyword=MISSING_PEAK)

  return allRecall, allPrecision, allFmeasure, allDpScore, unexplainedPeaks, missingPeaks


def getPeakListRpfValidation(validStore, peakList):
  """Descrn: Get any existing RPF peaklist validation results from data model
     Inputs: Validation.ValidationStore, Nmr.PeakList
     Output: 3-Tuple of Validation.PeakListValidation
  """
  # Define data model call to find exting result
  findValidation = peakList.findFirstPeakListValidation

  peakListRecall = findValidation(validationStore=validStore,
                                  context=PROG, keyword=RECALL)

  peakListPrecision = findValidation(validationStore=validStore,
                                    context=PROG, keyword=PRECISION)

  peakListFmeasure = findValidation(validationStore=validStore,
                                    context=PROG, keyword=F_MEASURE)

  peakListDpScore = findValidation(validationStore=validStore,
                                   context=PROG, keyword=DP_SCORE)

  return peakListRecall, peakListPrecision, peakListFmeasure, peakListDpScore


def storePeakListRpfValidation(validStore, peakList, recall, precision, fMeasure, dpScore):
  """Descrn: Store the RPF results for a peak list and ensemble in
             CCPN validation objects.
     Inputs: Validation.ValidationStore,
             Nmr.PeakList, Float, Float, Float, Float
     Output: 4-Tuple of Validation.PeakListValidation
  """

  # Get any existing RPF peaklist results
  validObjs = getPeakListRpfValidation(validStore, peakList)
  peakListRecall, peakListPrecision, peakListFmeasure, peakListDpScore = validObjs

  # Define data model call for any new result objects
  newValidation = validStore.newPeakListValidation

  # Check or make Peak list 'Recall' validation result object
  if not peakListRecall:
    peakListRecall = newValidation(context=PROG, keyword=RECALL)
    peakListRecall.peakLists = [peakList,]

  # Check or makePeak list 'Precision' validation result object
  if not peakListPrecision:
    peakListPrecision = newValidation(context=PROG, keyword=PRECISION,
                                      peakLists=[peakList,])

  # Check or makePeak list 'Fmeasure' validation result object
  if not peakListFmeasure:
    peakListFmeasure = newValidation(context=PROG, keyword=F_MEASURE,
                                     peakLists=[peakList,])

  # Check or makePeak list 'DpScore' validation result object
  if not peakListDpScore:
    peakListDpScore = newValidation(context=PROG, keyword=DP_SCORE,
                                     peakLists=[peakList,])

  # Set values
  peakListRecall.floatValue = recall
  peakListPrecision.floatValue = precision
  peakListFmeasure.floatValue = fMeasure
  peakListDpScore.floatValue = dpScore

  # Return validation objects
  return peakListRecall, peakListPrecision, peakListFmeasure, peakListDpScore


def getProtonDistsConn(ensemble, heteroAtomContexts, distThreshold=DEFAULT_DISTANCE_THRESHOLD,
                       progressBar=None):
  """Descrn: Function to get a dictionary of H-H distances, keyed
             by resonances, with filtering of available hetero atom
             types. Optional progreessbar for graphical display.
     Inputs: MolStructure.StructureEnsemble,
             Set of 2-Tuples of ChemAtom.elementSymbols
             memops.gui.ProgressBar
     Output: Dict of Resonance:[Dict of Resonance:Float]
             - i.e. dict[resonance1][resonance2] = dist
  """

  badDist = distThreshold+2.5


  # Convert available heteroatom contexts
  # to dict for quick lookup
  contextDict = {}
  for a1, a2 in heteroAtomContexts:
    contextDict[(a1,a2)] = True

  hydrogens = set()

  # Loop though chains for structure
  for chain in ensemble.coordChains:

    # Loop though residues of chain
    for residue in chain.residues:
      #hydrogens = set()

      # Get Ca atomSet so we can exclude whole distal residues
      # Default to none, just in case we have a strange residue
      caAtomSet = None

      # residue.residue because we go from the
      # ensmble residue to mol system residue
      caAtom = residue.findFirstAtom(name='CA')
      if caAtom:
        caAtomSet = caAtom.atom.atomSet

      if not caAtomSet:
        continue

      # A blank set to store all assigned hydrogen atom sets & resonances
      # for this residue - using a Python set to avoid repeats
      # e.g. methyl has three atom in the same atom set

      # Loop though atoms of residue
      for atom in residue.atoms:

        # Check if atom is hydrogen
        if atom.elementSymbol != 'H':
          continue

        # Check we have a link to molSystem atom
        msAtom = atom.atom
        if not msAtom:
          continue

        # Skip invisble fast exchangeable atoms
        if msAtom.chemAtom.waterExchangeable:
          continue

        # Check we have an NMR atom set
        atomSet = msAtom.atomSet
        if not atomSet:
          continue

        # Check we have an assignment
        resonanceSets = atomSet.resonanceSets
        if not resonanceSets:
          continue

        # Get the bound heteroatom type
        boundAtom = getBoundAtoms(msAtom)[0]
        boundType = boundAtom.chemAtom.elementSymbol

        # Get resonance and equivalent atom sets
        # atomSets could be multiple if ambif prochiral
        for resonanceSet in resonanceSets:
          resonances = list(resonanceSet.resonances)
          atomSets   = resonanceSet.atomSets

          if not resonances[0].shifts:
            continue

          if len(atomSets) == 1:
            resonance = resonances[0]

          else:
            # Trick to map ambigous prochiral atomSets to resonance
            index = min(len(resonances)-1, list(atomSets).index(atomSet))
            resonance = resonances[index]

        # Add to hydrogens: atom sets, resonance and heteroatom type
        hydrogens.add((atomSets, resonance, boundType))

      #maxResBonds[caAtom] = MAX_BONDS.get(msResidue.ccpCode,7)
      #residueHydrogens[caAtom] = hydrogens

  # Store close resonance distances as dict
  hydrogens = list(hydrogens)
  resonanceDistances = {}

  for atomSets, resonance, boundType in hydrogens:
    resonanceDistances[resonance] = {}

  if progressBar:
    progressBar.total = len(hydrogens)-1

  models = ensemble.models
  ensembleCoords = []
  ensembleCoordsAppend = ensembleCoords.append

  for i, (atomSets, resonance, boundType) in enumerate(hydrogens):

    coordList1 = []
    coordList1Append = coordList1.append
    xl = []
    for model in models:

      xa = 0.0
      nc = 0.0
      coords = []
      for atomSet in atomSets:
        for coord in getAtomSetCoords(atomSet, ensemble, model):
          x = coord.x
          y = coord.y
          z = coord.z
          coords.append((x,y,z))
          xa += x
          nc += 1.0

      xl.append(xa/nc)
      coordList1Append(coords)

    if coordList1:
      ensembleCoordsAppend((xl, i, coordList1))

  nModels = float(len(models))
  ensembleCoords.sort()

  for k, (x1, i, coordList1) in enumerate(ensembleCoords[:-1]):
    if progressBar:
      progressBar.increment()

    (atomSets1, resonance1, boundType1) = hydrogens[i]

    for x2, j, coordList2 in ensembleCoords[k:]:

      (atomSets2, resonance2, boundType2) = hydrogens[j]

      context = (boundType1, boundType2)
      # Check that the heteroatoms fit the spectrum types
      if not contextDict.get(context):
        continue

      for a, x1a in enumerate(x1):
        if (x2[a]-x1a) < badDist:
          break
      else:
        break

      if atomSets1 == atomSets2:
        if len(atomSets1) == 2:
          atomSets0 = list(atomSets1)
          for resonanceSet in atomSets0[0].resonanceSets:
            if resonanceSet in atomSets0[1].resonanceSets: # Prochiral
              atomSetsA = [atomSets0[0],]
              atomSetsB = [atomSets0[1],]
              noeDist = getAtomSetsDistance(atomSetsA, atomSetsB,
                                            ensemble, method='noe')
              noe = noeDist**-6.0
              resonanceDistances[resonance1][resonance2] = noeDist, noe
              resonanceDistances[resonance2][resonance1] = noeDist, noe
              break

        if atomSets1 == atomSets2: # Not prochiral
          continue

      else:

        noeEnsemble = 0.0

        for m, model in enumerate(models):
          coords2 = coordList2[m]
          coords1 = coordList1[m]

          noeSum = 0.0

          for xa,ya,za in coords1:
            for xb,yb,zb in coords2:
              dx = xa - xb
              dy = ya - yb
              dz = za - zb
              dist2 = (dx*dx) + (dy*dy) + (dz*dz)

              if dist2 > 0:
                noeSum += dist2 ** -3.0

          noeEnsemble += noeSum

        noeEnsemble /= nModels

        if noeEnsemble:
          noeDist = noeEnsemble ** (-1/6.0)
          resonanceDistances[resonance1][resonance2] = noeDist, noeEnsemble
          resonanceDistances[resonance2][resonance1] = noeDist, noeEnsemble

  return resonanceDistances



def getAmbigNoeConn(peakLists, toleranceList, diagonalTolerance=0.1,
                    aliasing=False, progressBar=None):
  """ Descrn:Function to get the ambiguous resonance connectivity
             for peaklists by comparing resonance shifts to peak positions
             within tolerances. Currently only the first float in the tolerance
             sub-list is used. Tolerance to ignore matching to diagonal peaks.
             Optional progress bar can be passed in for graphival display.
     Inputs: List of Nmr.PeakLists,
             List of 4-List of (Nmr.DataDim, Float (Tolerance), Float, Float),
             Float, memops.gui.ProgressBar
     Output: Dict of Resonance:[Dict of Resonance:Peak],
             Dict of Peak:2-Tuple(Resonance, Resonance)
  """

  resonanceConnectivity = {}

  peakPossibilities = {}
  unexplained = []

  # Loop through peak list
  for k, peakList in enumerate(peakLists):

    # Get tolerances for this peak list
    tolerances = toleranceList[k]

    # Navigate up model to get spectrum & experiment
    spectrum     = peakList.dataSource

    # Find 1H spectrum dimension numbers
    hydrogenDims = findSpectrumDimsByIsotope(spectrum, '1H')

    # Get the peaks in the peak list
    peaks = peakList.peaks

    # Must have exactly 2 1H dimensions
    if len(hydrogenDims) != 2:
      continue

    # Make a dictionary that links bonded dimensions together
    bondedDims = {}
    for dataDim1, dataDim2 in getOnebondDataDims(spectrum):
      bondedDims[dataDim1] = dataDim2
      bondedDims[dataDim2] = dataDim1

    # Convert tolerances to a dictionary keyed by dimension
    tolDict = {}
    for (dataDim,minT,maxT,multi) in tolerances:
      tolDict[dataDim] = (minT,maxT,multi)

    # Loop thorough the peaks in this list
    # and fill in a filtered list to work with
    workingPeaks = []
    for peak in peaks:

      # filter out diagonals
      if diagonalTolerance:

        # Get peak dimensions from 1H dim numbers
        peakDims = peak.sortedPeakDims()
        peakDim1 = peakDims[hydrogenDims[0]]
        peakDim2 = peakDims[hydrogenDims[1]]

        # Get 1H ppm values
        ppm1 = peakDim1.value
        ppm2 = peakDim2.value

        if peakDim1.value is None:
          print "Peak %s does not have a peakDim1.value" % peak
          continue

        # Check if ppm values similar
        delta = abs(ppm1-ppm2)
        #if (delta <= tolDict[peakDim1.dataDim][0] ) \
        #    or (delta <= tolDict[peakDim2.dataDim][0]):
        if delta < diagonalTolerance:

          # Find any spectrum dims bound to 1H dims
          dataDimA = bondedDims.get(peakDim1.dataDim)
          dataDimB = bondedDims.get(peakDim2.dataDim)

          # Two bound spectrum dims means we have to check
          # the closeness of these hetero dimensions too
          if dataDimA and dataDimB :

            # Get bound hetero peak dims
            peakDimA = peak.findFirstPeakDim(dataDim=dataDimA)
            peakDimB = peak.findFirstPeakDim(dataDim=dataDimB)

            # Get hetero ppm values
            ppmA = peakDimA.value
            ppmB = peakDimB.value

            # Check for closeness
            delta2 = abs(ppmA-ppmB)
            if (delta2 <= tolDict[dataDimA][0] ) \
                or (delta2 <= tolDict[dataDimB][0]):
              continue

            else:
            # Otherwise exclude peak because 1H ppms are close
              continue

      workingPeaks.append(peak)




    # Loop through peaks in filtered list

    nPeaks = len(workingPeaks)
    if progressBar:
      progressBar.total = nPeaks

    for c, peak in enumerate(workingPeaks):

      # Get peak dimension objects in order
      peakDims = peak.sortedPeakDims()

      peakResonances = []

      # For each 1H dimension find matching chemical shifts
      for i in hydrogenDims:

        # List to contain matching resonances
        resonances = []

        # Get peak and spectrum dims for this 1H dim number
        peakDim = peakDims[i]
        dataDim = peakDim.dataDim

        # Recall tolerances for this spectrum dimension
        (minT,maxT,multi) = tolDict[dataDim]

        # Convert this into a peak tolerance
        # - In the future below considers line widths
        tolerance = getPeakDimTolerance(peakDim,minT,maxT,multi)


        # Find chemical shifts that match 1H dim
        # - use a switch to find only atom assigned resonances
        shifts = findMatchingPeakDimShifts(peakDim, tolerance=tolerance,
                                           aliasing=aliasing,
                                           findAssigned=True)

        # Check if this 1H dim bound to a heteroatom
        # only if we have some matching 1H shifts to work from
        bondedDim = bondedDims.get(dataDim)
        if bondedDim and shifts:
          # If so, check that both bound dim possibilities are within tolerances

          # Get bound peak dim from spectrum dim
          peakDim2 = peak.findFirstPeakDim(dataDim=bondedDim)

          # Get tolerances for bound hetero dim
          (min2T,max2T,multi2) = tolDict[bondedDim]
          tolerance2 = getPeakDimTolerance(peakDim2,min2T,max2T,multi2)


          # Find any matching hetero chemical shifts
          # - In the future below considers line widths
          shifts2 = findMatchingPeakDimShifts(peakDim2, aliasing=aliasing,
                                              tolerance=tolerance2,
                                              findAssigned=True)

          # Loop though pairs of 1H and hetero atom shifts
          for shift in shifts:
            resonance = shift.resonance

            for shift2 in shifts2:
              resonance2 = shift2.resonance

              # Accept a chemical shift match only if the resonances
              # are known to be bound together, otherwise they cannot
              # possibly contribute to this peak
              if areResonancesBound(resonance, resonance2):
                resonances.append(resonance)
                break

        else:
          # Otherwise no bound hetero dim
          # Simply take all matching 1H resonances

          for shift in shifts:
            resonance = shift.resonance
            resonances.append(resonance)

        # Store the matching resonances for this peak dimension
        peakResonances.append( resonances )

      # Store possible resonance pairs for this peak
      peakPossibilities[peak] = []

      # If we have matching resonances for both 1H dims
      if peakResonances[0] and peakResonances[1]:

        # Create interaction resonance pairs from the
        # list for each 1H dim
        for resonance0 in peakResonances[0]:
          for resonance1 in peakResonances[1]:

            # Double check resonances not same: i.e. diagonal
            if diagonalTolerance:
              if resonance1 is resonance0:
                continue

            if resonanceConnectivity.get(resonance0) is None:
              resonanceConnectivity[resonance0] = {}

            if resonanceConnectivity.get(resonance1) is None:
              resonanceConnectivity[resonance1] = {}

            # Store connection, symmetrically
            resonanceConnectivity[resonance0][resonance1] = peak
            resonanceConnectivity[resonance1][resonance0] = peak

            # Get atoms for calculating free rotation dist
            # and for making per-residue scores
            atom0 = resonance0.resonanceSet.findFirstAtomSet().findFirstAtom()
            atom1 = resonance1.resonanceSet.findFirstAtomSet().findFirstAtom()

            # Connection info from peak perspective
            peakPossibilities[peak].append((resonance0, resonance1, atom0, atom1))

      else:
        unexplained.append(peak)

      if progressBar and (c % 20 == 0):
        progressBar.set(c)

    if progressBar:
      progressBar.set(nPeaks)

  return resonanceConnectivity, peakPossibilities, unexplained

# get software if it exists, otherwise create
def getSoftware(project):

  name = 'PyRPF'
  version = '0.4'

  methodStore = getMethodStore(project)
  software = methodStore.findFirstSoftware(name=name, version=version)
  if (not software):
    software = methodStore.newSoftware(name=name, version=version)

  return software

def getNoeTolerances(peakList):
    dimTolerances = []
    spectrum = peakList.dataSource
    for dataDim in spectrum.sortedDataDims():
      analysisDataDim = getAnalysisDataDim(dataDim)
      tol = analysisDataDim.assignTolerance
      dimTolerances.append([dataDim, tol, 1, tol])
    return dimTolerances

def getEnsembles(project):
  ensembles = []
  for molSystem in project.molSystems:
      for ensemble in molSystem.structureEnsembles:
          ensembles.append((molSystem.code, ensemble.ensembleId, ensemble))
  ensembles.sort()
  return [x[2] for x in ensembles]

def pyRpfApp(ensembles, peakLists, tolerances, distThreshold=5.0,
             prochiralTolerance=0.04, diagonalTolerance=0.3, aliasing=True):

  calcRPF(ensembles, peakLists, tolerances, distThreshold,
          prochiralTolerance, diagonalTolerance, aliasing)

if __name__ == '__main__':

  from memops.general.Io import loadProject

  from ccpnmr.analysis.Analysis import Analysis

  #projectDirectory = '/home/tjs23/nmr/montelione/rpf/1brv_cs_pk_2mdl/'
#  projectDirectory = '/home/tjs23/nmr/montelione/rpf/AtT13Org/'
  projectDirectory = '/Users/jd/tmp/cingTmp/1brv_cs_pk_2mdl/'

  rootProject = loadProject(projectDirectory)

  app = Analysis(64)

  app.initProject(rootProject)

  peakLists = getThroughSpacePeakLists(rootProject)

  ensembles = getEnsembles(rootProject)

  tolerances = [getNoeTolerances(pl) for pl in peakLists]

  pyRpfApp(ensembles, peakLists, tolerances, distThreshold=5.0,
           prochiralTolerance=0.04, diagonalTolerance=0.3, aliasing=True,)
