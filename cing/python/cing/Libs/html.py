"""
Adds html generation methods
"""
from cing import authorList
from cing import cingDirData
from cing import cingPythonCingDir
from cing import cingRevision
from cing import cingRevisionUrl
from cing import cingRoot
from cing import cingVersion
from cing import programName
from cing.Libs.Imagery import convert2Web
from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.find import find2 # Important to differ from NTutil's otherwise from string import find
from cing.PluginCode.required.reqMatplib import MATPLIB_STR
from cing.PluginCode.required.reqMolgrap import MOLGRAP_STR
from cing.PluginCode.required.reqNih import * #@UnusedWildImport
from cing.PluginCode.required.reqNmrStar import * #@UnusedWildImport
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.PluginCode.required.reqX3dna import X3DNA_STR
from cing.STAR.Utils import getHumanTagName
from cing.core.classes2 import getIndexRealResList
from cing.core.parameters import cingPaths
from cing.core.parameters import directories
from cing.core.parameters import htmlDirectories
from cing.core.parameters import moleculeDirectories
from cing.core.parameters import plugins
from glob import glob1
import cPickle
import shutil

HTML_TAG_PRE = "<PRE>"
HTML_TAG_PRE2 = "</PRE>"

# class is a reserved keyword in python so encapsulate in dictonary.
checkBoxClassAttr = {"class": "mediumCheckbox"}

# Specific for the CING project is the code UA-4413187-1
# It's inserted only into the top level index.html; one per cing report.
GOOGLE_ANALYTICS_TEMPLATE = """
<!-- The script below will anonymously report usage data to Google Analytics by any javascript enabled browser. -->
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-4413187-1");
pageTracker._trackPageview();
} catch(err) {}</script>
"""

NO_CHAIN_TO_GO_TO = 'no chain to go to'

image2DdihedralWidth  = 500
image2Ddihedralheight = 500
#imageSmall2DdihedralWidth  = 300 # Scale only the height so no extra coding is needed to distinguish the 1D & 2D varying sizes.
imageSmall2Ddihedralheight = 300

cingPlotList = []
cingPlotList.append( ('_01_cv_rms','cv/rms') )
cingPlotList.append( ('_02_Qfactor_cs','Q-factor CS') )
cingPlotList.append( ('_03_Cb4N_Cb4C','D1D2') )
cingPlotList.append( ('_04_bb','Backbone dihedrals') )

def createHtmlCing(project, ranges=None):
    """ Read out cingPlotList to see what get's created. """

    if not getDeepByKeysOrAttributes(plugins, MATPLIB_STR, IS_INSTALLED_STR):
#        nTdebug('Skipping createHtmlCing because no matplib installed.')
        return
    from cing.PluginCode.matplib import MoleculePlotSet #@UnresolvedImport

    # The following object will be responsible for creating a (png/pdf) file with
    # possibly multiple pages
    # Level 1: row
    # Level 2: against main or alternative y-axis
    # Level 3: plot parameters dictionary (extendable).
    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ PHI_STR, CV_STR ]
    plotAttributesRowMain[ KEY_LIST2_STR] = [ PSI_STR, CV_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ 'cv_backbone' ]
    plotAttributesRowMain[ YLABEL_STR] = 'cv phi/psi'
    plotAttributesRowAlte[ YLABEL_STR] = 'cv backbone'
    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
    plotAttributesRowMain[ USE_MAX_VALUE_STR] = 1.0
    keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])

    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ CHI1_STR, CV_STR ]
    plotAttributesRowMain[ KEY_LIST2_STR] = [ CHI2_STR, CV_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ 'cv_sidechain' ]
    plotAttributesRowMain[ YLABEL_STR] = 'cv chi1/2'
    plotAttributesRowAlte[ YLABEL_STR] = 'cv sidechain'
    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
    plotAttributesRowMain[ USE_MAX_VALUE_STR]   = 1.0
    keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])

    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ RMSD_STR, BACKBONE_AVERAGE_STR, VALUE_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ RMSD_STR, HEAVY_ATOM_AVERAGE_STR, VALUE_STR ]
    plotAttributesRowMain[ YLABEL_STR] = BACKBONE_AVERAGE_STR
    plotAttributesRowAlte[ YLABEL_STR] = HEAVY_ATOM_AVERAGE_STR
    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
    keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])
    printLink = project.moleculePath( 'analysis', project.molecule.name + cingPlotList[0][0] + ".pdf" )
    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )

    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ QSHIFT_STR, ALL_ATOMS_STR]
    plotAttributesRowMain[ KEY_LIST2_STR] = [ QSHIFT_STR, BACKBONE_STR]
    plotAttributesRowMain[ KEY_LIST3_STR] = [ QSHIFT_STR, HEAVY_ATOMS_STR]
    plotAttributesRowMain[ KEY_LIST4_STR] = [ QSHIFT_STR, PROTONS_STR]
    plotAttributesRowMain[ YLABEL_STR] = 'QCS all/bb/hvy/prt'
    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
    plotAttributesRowMain[ USE_MAX_VALUE_STR] = 0.5
    keyLoLoL.append([ [plotAttributesRowMain] ])
    printLink = project.moleculePath( 'analysis', project.molecule.name + cingPlotList[1][0] + ".pdf" )
    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )

    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ CHK_STR, RAMACHANDRAN_CHK_STR, VALUE_LIST_STR]
    plotAttributesRowMain[ YLABEL_STR] = 'Z RAM'
    plotAttributesRowMain[ USE_MIN_VALUE_STR] = -3 # autoscaling is failing here at the moment.
    plotAttributesRowMain[ USE_MAX_VALUE_STR] = 3
    keyLoLoL.append([ [plotAttributesRowMain] ])

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ CHK_STR, CHI1CHI2_CHK_STR, VALUE_LIST_STR]
    plotAttributesRowMain[ YLABEL_STR] = 'Z JAN'
    plotAttributesRowMain[ USE_MIN_VALUE_STR] = -3 # autoscaling is failing here at the moment.
    plotAttributesRowMain[ USE_MAX_VALUE_STR] = 3
    keyLoLoL.append([ [plotAttributesRowMain] ])

    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ CHK_STR, D1D2_CHK_STR, VALUE_LIST_STR]
    plotAttributesRowMain[ YLABEL_STR] = 'Z D1D2'
    plotAttributesRowMain[ USE_MIN_VALUE_STR] = -3 # autoscaling is failing here at the moment.
    plotAttributesRowMain[ USE_MAX_VALUE_STR] = 3
    keyLoLoL.append([ [plotAttributesRowMain] ])

    printLink = project.moleculePath( 'analysis', project.molecule.name + cingPlotList[2][0] + ".pdf" )
    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )


#    keyLoLoL = []
#    plotAttributesRowMain = NTdict()
#    plotAttributesRowAlte = NTdict()
#    plotAttributesRowMain[ KEY_LIST_STR] = [ PHI_STR, CV_STR ]
#    plotAttributesRowMain[ KEY_LIST2_STR] = [ PSI_STR, CV_STR ]
#    plotAttributesRowAlte[ KEY_LIST_STR] = [ 'cv_backbone' ]
#    plotAttributesRowMain[ YLABEL_STR] = 'cv phi/psi'
#    plotAttributesRowAlte[ YLABEL_STR] = 'cv backbone'
#    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
#    plotAttributesRowMain[ USE_MAX_VALUE_STR] = 1.0
#    keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])
#
#    plotAttributesRowMain = NTdict()
#    plotAttributesRowAlte = NTdict()
#    plotAttributesRowMain[ KEY_LIST_STR] = [ CHI1_STR, CV_STR ]
#    plotAttributesRowMain[ KEY_LIST2_STR] = [ CHI2_STR, CV_STR ]
#    plotAttributesRowAlte[ KEY_LIST_STR] = [ 'cv_sidechain' ]
#    plotAttributesRowMain[ YLABEL_STR] = 'cv chi1/2'
#    plotAttributesRowAlte[ YLABEL_STR] = 'cv sidechain'
#    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
#    plotAttributesRowMain[ USE_MAX_VALUE_STR]   = 1.0
#    keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])
#
#    plotAttributesRowMain = NTdict()
#    plotAttributesRowAlte = NTdict()
#    plotAttributesRowMain[ KEY_LIST_STR] = [ RMSD_STR, BACKBONE_AVERAGE_STR, VALUE_STR ]
#    plotAttributesRowAlte[ KEY_LIST_STR] = [ RMSD_STR, HEAVY_ATOM_AVERAGE_STR, VALUE_STR ]
#    plotAttributesRowMain[ YLABEL_STR] = BACKBONE_AVERAGE_STR
#    plotAttributesRowAlte[ YLABEL_STR] = HEAVY_ATOM_AVERAGE_STR
#    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
#    keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])
#    printLink = project.moleculePath( 'analysis', project.molecule.name + cingPlotList[0][0] + ".pdf" )
#    moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
#    moleculePlotSet.renderMoleculePlotSet( printLink, createPngCopyToo=True  )

#end def

# pylint: disable=R0903
class HistogramsForPlotting():
    """
    Class for enabling load on demand
    Funny doesn't seem to speed booting up. And it really doesn't get loaded.
    """
    
    def __init__(self):
        self.histRamaCombined                = None
        self.histRamaBySsAndResType          = None
        self.histRamaCtupleBySsAndResType    = None
        self.histRamaBySsAndCombinedResType  = None
        self.histJaninBySsAndResType         = None
        self.histJaninCtupleBySsAndResType   = None
        self.histJaninBySsAndCombinedResType = None             
        self.histd1BySs0AndResTypes           = None # Note the plural s in ResTypes it is hashed by not one but two residue types.
        self.histd1BySs1AndResTypes           = None # This one is hashed by the Ss of the preceding residue type.
        # NB hasing is: ssType, resType, resTypePrev, resTypeNext (just adding resTypeNext wrt histd1BySsAndResTypes
        #               3        20        20        20 = 2400 tuples of 2 floats precalculated.
        self.histd1CtupleBySsAndResTypes    = None
        self.histd1ByResTypes               = None
        self.histd1BySs0                    = None
        self.histd1BySs1                    = None
        self.histd1                         = None

        self.histDir = os.path.join( cingDirData, 'PluginCode', 'WhatIf')

    def initHist(self):
        if hPlot.histRamaBySsAndCombinedResType != None:
            nTdebug("Doing HistogramsForPlotting#initHist even though it was done before.")

        if True:
#            nTdebug("Loading Ramachandran histograms")
            dbase_file_abs_name =  os.path.join( self.histDir, 'phipsi_wi_db.dat' )
            #dbaseTemp = shelve.open( dbase_file_abs_name )
            dbase_file = open(dbase_file_abs_name, 'rb') # read binary
            dbaseTemp = cPickle.load(dbase_file)
        #    pprint.pprint(dbaseTemp)
            self.histRamaCombined                   = dbaseTemp[ 'histRamaCombined' ]
            self.histRamaBySsAndResType             = dbaseTemp[ 'histRamaBySsAndResType' ]
            self.histRamaCtupleBySsAndResType       = dbaseTemp[ 'histRamaCtupleBySsAndResType' ]
            self.histRamaBySsAndCombinedResType     = dbaseTemp[ 'histRamaBySsAndCombinedResType' ]
        #    pprint(histRamaCombined)
            dbase_file.close()
            #dbaseTemp.close()
#            sumHist = core.sum(self.histRamaCombined, axis=None)
#            nTdebug("Rama          sum: %d" % sumHist)
#            sumHist = core.sum(self.histRamaBySsAndResType['H']['HIS'])
#            nTdebug("Rama [H][HIS] sum: %d" % sumHist)

        if True:
#            nTdebug("Loading Janin histograms")
            dbase_file_abs_name = os.path.join( self.histDir, 'chi1chi2_wi_db.dat' )
            dbase_file = open(dbase_file_abs_name, 'rb') # read binary
            dbaseTemp = cPickle.load(dbase_file)
            self.histJaninBySsAndResType            = dbaseTemp[ 'histJaninBySsAndResType' ]
            self.histJaninCtupleBySsAndResType      = dbaseTemp[ 'histJaninCtupleBySsAndResType' ]
            self.histJaninBySsAndCombinedResType    = dbaseTemp[ 'histJaninBySsAndCombinedResType' ]
            dbase_file.close()
#            sumHist = core.sum(self.histJaninBySsAndResType['H']['HIS'])
#            nTdebug("Janin [H][HIS] sum: %d" % sumHist)

        if True:
#            nTdebug("Loading D1D2 histograms")
            dbase_file_abs_name = os.path.join( self.histDir, 'cb4ncb4c_wi_db.dat' )
            dbase_file = open(dbase_file_abs_name, 'rb') # read binary
            dbaseTemp = cPickle.load(dbase_file)
            self.histd1BySs0AndResTypes             = dbaseTemp[ 'histd1BySs0AndResTypes' ]
            self.histd1BySs1AndResTypes             = dbaseTemp[ 'histd1BySs1AndResTypes' ]
            self.histd1CtupleBySsAndResTypes        = dbaseTemp[ 'histd1CtupleBySsAndResTypes' ]
            self.histd1ByResTypes                   = dbaseTemp[ 'histd1ByResTypes' ]
            self.histd1BySs0                        = dbaseTemp[ 'histd1BySs0' ]
            self.histd1BySs1                        = dbaseTemp[ 'histd1BySs1' ]
            self.histd1                             = dbaseTemp[ 'histd1' ]
            dbase_file.close()
#            sumHist = core.sum(self.histd1)
#            nTdebug("D1D2               sum: %d" % sumHist)
#            sumHist = core.sum(self.histd1BySsAndResTypes['H']['HIS']['HIS'])
#            nTdebug("D1D2 [H][HIS][HIS] sum: %d" % sumHist)
# end class

hPlot = HistogramsForPlotting()

def makeDihedralPlot( project, residueList, dihedralName1, dihedralName2,
                      plotTitle = None, plotCav = True, htmlOnly=False ):
    '''Return NTplotSet instance with plot of dihedralName1 vrs dihedralName2 or
       None on error
       Called with: eg ['PHI',  'PSI',  'Ramachandran', 'PHI_PSI']

       Note that residue can also be a list of residues. A single plot will
       be created for all together were the appropriate background histograms
       will be picked.

       plotCav determines if the circular variance average is plotted.

       Return None on error or ps on success.
    '''

    if not project:
        nTerror( 'in makeDihedralPlot called without project' )
        return None
    if not residueList:
        nTerror( 'makeDihedralPlot called without residues in list' )
        return None

    if not getDeepByKeysOrAttributes(plugins, MATPLIB_STR, IS_INSTALLED_STR):
        nTdebug('Skipping plots in html#makeDihedralPlot() because no matplib installed.')
        return None

    from cing.PluginCode.matplib import NTplot #@UnresolvedImport
    from cing.PluginCode.matplib import NTplotSet #@UnresolvedImport

    if hPlot.histRamaBySsAndCombinedResType == None:
        hPlot.initHist()

    # Set residue to first residue. For looping over multiple residues the var
    # res will be used.
    residue = residueList[0]
    # Note if all types are the same for selection of background.
#    allSameResType = True
#    for res in residueList:
#        if res.resName != residue.resName:
#            allSameResType = False
#            break
    if dihedralName1 not in residue or residue[dihedralName1] == None:
#        nTdebug( 'in makeDihedralPlot not in residue dihedral 1: '+dihedralName1 )
        return None

    if dihedralName2 not in residue or residue[dihedralName2] == None:
#        nTdebug( 'in makeDihedralPlot not in residue dihedral 2: '+dihedralName2 )
        return None
    if htmlOnly:
        return True # indicating success

    isSingleResiduePlot = len(residueList) == 1

    if not plotTitle:
        if isSingleResiduePlot:
            plotTitle = residue.cName(2)
        else:
            plotTitle = '%d residues'


#    nTdebug("Creating a 2D dihedral angle plot for plotItem: %s %s %s", residue, dihedralName1, dihedralName2)

    plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
    plotparams2 = project.plotParameters.getdefault(dihedralName2,'dihedralDefault')

    ps =NTplotSet() # closes any previous plots
    ps.hardcopySize = (image2DdihedralWidth,image2Ddihedralheight)
    plot = NTplot( title  = plotTitle,
      xRange = (plotparams1.min, plotparams1.max),
      xTicks = range(int(plotparams1.min), int(plotparams1.max+1), plotparams1.ticksize),
      xLabel = dihedralName1,
      yRange = (plotparams2.min, plotparams2.max),
      yTicks = range(int(plotparams2.min), int(plotparams2.max+1), plotparams2.ticksize),
      yLabel = dihedralName2)
    ps.addPlot(plot)

    doingNewD1D2plot = False
    minPercentage =  MIN_PERCENTAGE_RAMA
    maxPercentage = MAX_PERCENTAGE_RAMA
    scaleBy = SCALE_BY_MAX

    if dihedralName1=='PHI' and dihedralName2=='PSI':
        histBySsAndCombinedResType = hPlot.histRamaBySsAndCombinedResType
        histBySsAndResType         = hPlot.histRamaBySsAndResType
    elif dihedralName1=='CHI1' and dihedralName2=='CHI2':
        histBySsAndCombinedResType = hPlot.histJaninBySsAndCombinedResType
        histBySsAndResType         = hPlot.histJaninBySsAndResType
    elif dihedralName1==DIHEDRAL_NAME_Cb4N and dihedralName2==DIHEDRAL_NAME_Cb4C:
        histBySsAndResType         = hPlot.histd1BySs0AndResTypes
#        histBySsAndResType         = None
        if True:
            minPercentage =  MIN_PERCENTAGE_D1D2
            maxPercentage = MAX_PERCENTAGE_D1D2
            scaleBy = SCALE_BY_SUM
        else:
            minPercentage =  MIN_Z_D1D2
            maxPercentage = MAX_Z_D1D2
            scaleBy = SCALE_BY_Z
        doingNewD1D2plot = True
    else:
        nTcodeerror("makeDihedralPlot called for non Rama/Janin/d1d2")
        return None

    histList = []
    ssTypeList = histBySsAndResType.keys() #@UndefinedVariable
    ssTypeList.sort()
    # The assumption is that the derived residues can be represented by the regular.
    resName = getDeepByKeysOrDefault(residue, residue.resName, 'nameDict', PDB)
    if len( resName ) > 3: # The above line doesn't work. Manual correction works 95% of the time.
        resName = resName[:3]  # .pdb files have a max of 3 chars in their residue name.
#    nTdebug('Looked up residue.resName %s to resName %s' % ( residue.resName,resName ))

    if doingNewD1D2plot:
        # depending on doOnlyOverall it will actually return an array of myHist.
        myHistList = residue.getTripletHistogramList( doOnlyOverall = False, doNormalize = False )
        if myHistList == None:
            nTdebug("Failed to get the d1d2 hist for %s" % residue)
            return None
        if len(myHistList) == 0:
#            nTdebug("Found no histogram for %s" % residue)
            return None
        histList += myHistList # extend the list.
    else:
        for ssType in ssTypeList:
            if isSingleResiduePlot:
                myHist = getDeepByKeys(histBySsAndResType,ssType,resName)
            else:
                myHist = getDeepByKeys(histBySsAndCombinedResType,ssType)
            if myHist == None:
#                nTdebug("Failed to get the non-d1d2 hist for %s" % residue) # happens for 1bus cPro
                return None
        #            nTdebug('Appending for ssType %s and resName %s' % ( ssType,resName ))
            histList.append(myHist)
    if histList:
#        nTdebug('Will do dihedralComboPlot')
        plot.dihedralComboPlot(histList, minPercentage =  minPercentage, maxPercentage = maxPercentage, scaleBy = scaleBy)



    # Plot restraint ranges for single residue plots.
    for res in residueList:
        if isSingleResiduePlot:
            # res is equal to residue
            for useTalos in ( False, True ):
#                nTdebug("Plotting with useTalos %s" % useTalos)
                dr1 = _matchDihedrals(res, dihedralName1,useTalos=useTalos)
                dr2 = _matchDihedrals(res, dihedralName2,useTalos=useTalos)

                if dr1 and dr2:
                    lower1, upper1 = dr1.lower, dr1.upper
                    lower2, upper2 = dr2.lower, dr2.upper
                elif dr1:
                    lower1, upper1 = dr1.lower, dr1.upper
                    lower2, upper2 = plotparams2.min, plotparams2.max
                elif dr2:
                    lower2, upper2 = dr2.lower, dr2.upper
                    lower1, upper1 = plotparams1.min, plotparams1.max

                if dr1 or dr2:
                    if useTalos:
                        if dihedralName1=='PHI' and dihedralName2=='PSI':
                            classification = getDeepByKeys(res, TALOSPLUS_STR, TALOSPLUS_CLASS_STR)
                            if classification == 'Good':
                                talosPlus = getDeepByKeys(res, TALOSPLUS_STR)
                                phi = getDeepByKeys(talosPlus, 'phi')
                                psi = getDeepByKeys(talosPlus, 'psi')
                                dev1 = NUMBER_OF_SD_TALOS * phi.error
                                lower1 = phi.value - dev1
                                upper1 = phi.value + dev1
                                dev2 = NUMBER_OF_SD_TALOS * psi.error
                                lower2 = psi.value - dev2
                                upper2 = psi.value + dev2
#                                nTdebug("Plotting TALOSPLUS for %s" % res)
                                # fill is important to change
                                plot.plotDihedralRestraintRanges2D(lower1, upper1,lower2, upper2, fill = False, fillColor='red') 
                            # end if classification
                        else:
                            nTcodeerror("Expected dihedrals to be present and to be phi/psi if useTalos is on")
                        # end check on Rama
                    else:
#                        nTdebug("Plotting regular dihedral for %s" % res)
                        plot.plotDihedralRestraintRanges2D(lower1, upper1,lower2, upper2)
                    # end else
                # end if
            # end for useTalos
        # end if isSingleResiduePlot
        d1 = res[dihedralName1]
        d2 = res[dihedralName2]

        if not len(d1):
#            nTdebug( 'in makeDihedralPlot dihedrals had no defining atoms for 1: %s or', dihedralName1 ) # happens in 1bus for cPro13.
            return None
        if not len(d2):
#            nTdebug( 'in makeDihedralPlot dihedrals had no defining atoms for 2: %s'   , dihedralName2 )
            return None
        d1cav = d1.cav
        d2cav = d2.cav

        # Plot data points on top for painters algorithm without alpha blending.
        myPoint = plusPoint.copy()
        myPoint.pointColor = 'green'
        myPoint.pointSize = 6.0 # was 6.0
#        myPoint.pointSize = 10.0
        myPoint.pointEdgeWidth = 1.0
        if res.resName == 'GLY':
            myPoint.pointType = 'triangle'
        if res.resName == 'PRO':
            myPoint.pointType = 'square'

#        if dihedralName1=='Cb4N' and dihedralName2=='Cb4C':
#        if doingNewD1D2plot:
            # Plot individually.
#            bbList = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR)
#            myPoint.pointColor='blue'
#            for i,d1Element in enumerate(d1):
#                if not bbList:
#                    myPoint.pointColor='blue'
#                else:
#                    bb = bbList[i]
##                    nTdebug('BBCCHK %f' % bb)
#                    if bb > BBCCHK_CUTOFF:
#                        myPoint.pointColor='red'
#                    else:
#                        myPoint.pointColor='green'
#                plot.point( (d1Element, d2[i]), attributes=myPoint )
#        else: # plot all at once.
        plot.points( zip( d1, d2 ), attributes=myPoint )

        # Plot the cav point for single residue plots.
        if isSingleResiduePlot and plotCav:
            myPoint = myPoint.copy()
            myPoint.pointSize = 8.0
            myPoint.pointType = 'circle'
            myPoint.pointColor = 'blue'
            myPoint.fill = False
            plot.point( (d1cav, d2cav),myPoint )

    return ps
#end def



def _matchDihedrals(residue, dihedralName, useTalos=False):
    """Matches considering useTalos
    useTalos = None -> neglect filtering on it
                True -> needs to be from Talos
                False -> needs to NOT be from Talos; DEFAULT so not too many changes in code are needed.

    Returns None or dihedral.
    """
    for dih in residue.dihedralRestraints:
        if dih.angle == '%s_%i' % (dihedralName, residue.resNum):
            if useTalos == None:
#                nTdebug("Returning dihedral regardless of useTalos: %s" % dih)
                return dih

            isFromTalos = dih.parent.isFromTalos()
            if useTalos == True and isFromTalos:
#                nTdebug("Returning dihedral because is from Talos: %s" % dih)
                return dih
            if useTalos == False and not isFromTalos:
#                nTdebug("Returning dihedral because is NOT from Talos: %s" % dih)
                return dih
    return None
#end def


def setupHtml(project):
    '''Description: create all folders and subfolders related to a Cing Project
                    under Molecule/HTML directory and initialize attribute html
                    for the due Cing objects.
       Inputs:      project instance
       Output:      returns None on success or True on failure.
    '''

    if not project.molecule:
        nTerror('setupHtml: no molecule defined')
        return True
    #end if

    nTmessage('==> Initializing HTML objects')
    HTMLfile.killHtmlObjects()

    molecule = project.molecule

    ProjectHTMLfile( project )
    MoleculeHTMLfile( project, molecule )
    for chain in molecule.allChains():
        ChainHTMLfile( project, chain )
    for res in molecule.allResidues():
        ResidueHTMLfile( project, res )

    DihedralByProjectListHTMLfile( project)
    project.dihedralByProjectList.append(NTtree("dummy")) # circumvent check on emptiness.
#    print "now  project.dihedralByProjectList initialized: " , project.dihedralByProjectList
#    print "now tmp initialized: " , tmp
#    print "now tmp initialized: " , tmp.dihedralByProjectList
#    print "now it's initialized: " , project.dihedralByProjectList.html

    if hasattr(molecule, 'atomList'):
        AtomsHTMLfile( project, molecule.atomList )
    else:
        # reduced verbosity here because gets tested in test_NTutils3.py.
        nTwarning("Failed to create AtomsHTMLfile because no molecule.atomList")

    if hasattr(molecule, 'ensemble'):
        EnsembleHTMLfile( project, molecule.ensemble )
#    else:
#        nTdebug("Not creating EnsembleHTMLfile because no ensemble")

    for restraintList in project.allRestraintLists():
        RestraintListHTMLfile( project, restraintList )

    for peakList in project.peaks:
        PeakListHTMLfile( project, peakList )

##end def


def generateHtml( project, htmlOnly=False ):
    """
    Generate all CING html output
    """
    if not project.molecule:
        nTerror('generateHtml: no molecule defined')
        return True
    #end if

    nTmessageNoEOL('==> Generating CING HTML code')
    if htmlOnly:
        nTmessage('.')
    else:
        nTmessage(' and images.')

    project.html.generateHtml(htmlOnly=htmlOnly)
    nTmessageNoEOL('==> Generating molecule HTML code')
    project.molecule.html.generateHtml(htmlOnly=htmlOnly)
    for chain in project.molecule.allChains():
        chain.html.generateHtml(htmlOnly=htmlOnly)
        nTmessage("Html for chain %s and its residues", chain.name)
        for res in NTprogressIndicator(chain.allResidues(), CHARS_PER_LINE_OF_PROGRESS):
            res.html.generateHtml(htmlOnly=htmlOnly)
    #end for

    nTmessage("Html for dihedrals by Project and Residue")
    project.dihedralByProjectList.html.generateHtml(htmlOnly=htmlOnly)

    nTmessage("Html for atoms and models")
    if hasattr(project.molecule, 'atomList'):
        project.molecule.atomList.html.generateHtml(htmlOnly=htmlOnly)
    if hasattr(project.molecule, 'ensemble'):
        project.molecule.ensemble.html.generateHtml(htmlOnly=htmlOnly)

    nTmessage('Html for peaks and restraints')
    for myList in NTprogressIndicator(project.peaks+project.allRestraintLists(), CHARS_PER_LINE_OF_PROGRESS):
        if hasattr(myList,'html'):
            myList.html.generateHtml(htmlOnly=htmlOnly)
    #end for
#end def

def renderHtml(project):
    '''Description: render HTML content for a Cing.Molecule or for just a
               Cing.Chain, Cing.Residue or Cing.Atom.
       Inputs: a Cing.Molecule, Cing.Chain, Cing.Residue or Cing.Atom.
       Output: return None for success is standard.
    '''
    nTmessage('==> Rendering HTML pages')
    for htmlObj in htmlObjects:
        htmlObj.render()
    #end for
#end def

def _navigateHtml( obj ):
    """
    Create navigation code for NTtree object in header of obj.html
    """
    obj.html.insertHtmlLink( obj.html.header, obj, obj.html.project, text = 'Home', title = 'goto Home of project' )
    # Refs to move to previous, next residue or UP
    previous = obj.sibling(-1)
    if previous:
        name = previous.cName(-1)
        obj.html.insertHtmlLink( obj.html.header, obj, previous, text = name, id=HTMLfile.headerSectionId,
                                 title = sprintf('goto %s', name)
                               )

    if obj._parent:
        name = obj._parent.cName(-1)
        obj.html.insertHtmlLink( obj.html.header, obj, obj._parent, text = 'UP',
                                 title = sprintf('goto %s', name)
                               )

    next = obj.sibling(1)
    if next:
        name = next.cName(-1)
        obj.html.insertHtmlLink( obj.html.header, obj, next, text = next.cName(-1), id=HTMLfile.headerSectionId,
                                 title = sprintf('goto %s', name)
                               )
#end def

class MakeHtmlTable:
    """Iterative class that generates rows of html Table
        columnFormats:     a list of (header, dict()) tuples describing the column
                             header can be None for no header above column

    Using <col width=99> statements to format columns did not render properly for align=right.

    JFD mentions: it should be possible to format a whole column without repeating the formatting for every cell.
    Now done in CSS files.

    Usage can be found in test_html.py

    NB without calling __iter__() thru rows() or so this thing won't render a <table> tag; weird.

    The classId parameter was introduced because the word class is a reserved word in Python.
    """
    def __init__(self, html, classId="genericClassTable", showHeader=True, showFooter=False, id=None, columnFormats=[], **kwds):
        self.html = html
        self.columnFormats = columnFormats
        self.classId = classId
        self.showFooter = showFooter
        self.id = id
        self._rows = None
        self._iter = -1
        self._columnOpen    = False
        self._currentColumn = -1
        self._doingHeader = False # temporarily set when filling header row.
        self.showHeader = showHeader # Doesn't remove it but just disables showing it.
        self.kwds = kwds
    #end def

    def __call__(self, tag, *args, **kwds):
        self.html( tag, *args, **kwds)
    #end def

    def getRows(self):
        return self._rows

    def rows(self, rows):
        self._rows = rows
        return self
    #end def

    def __iter__( self ):
        """iteration routine: loop of rows
        Which also starts the table tag!
        """
#        print 'iter>', self._rows, self._iter
        if self._rows == None: 
            return None

        self._iter = 0
        self._len  = len(self._rows)
        self._columnOpen    = False
        self._currentColumn = -1

        kwdsTable = {}
        kwdsTable.update(self.kwds)
        if self.classId:
            kwdsTable[ 'class' ] = self.classId
        if self.id:
            kwdsTable[ 'id' ] = self.id

        self.html('table',closeTag=False, **kwdsTable)
        if self._mkColumnHeaders():
            return None # should make the code fail.
        self.html('tbody',closeTag=False)
        return self
    #end def

    def next( self ):
#        print 'next>', self._rows, self._iter
        if self._iter > 0:
            if self._columnOpen:
                self.closeColumn()
            self.html('tr', openTag=False)

        if self._iter >= self._len:
            self.html('table', openTag=False)
            raise StopIteration
#            return None
        # end if
        self.html('tr', closeTag=False)
        s = self._rows[self._iter]
        self._iter += 1
        self._currentColumn = -1
        self._columnOpen = False
        return s
    #end def

    def openColumn(self, columnIndex=-1, *args, **kwds):
        """<td> or <th> statements with redefined column formats
        kwds can override/expand
        """

        tagId = 'td'
        if self._doingHeader:
            tagId = 'th'

        if columnIndex >=0 and columnIndex < len(self.columnFormats):
            _tmp,formats = self.columnFormats[columnIndex]
            formats.update(kwds)
            self.html(tagId,closeTag=False, *args, **formats)
        else:
            self.html(tagId,closeTag=False, *args, **kwds)
#        self.html('td',closeTag=False)
        self._columnOpen = True
    #end def

    def closeColumn(self):
        tagId = 'td'
        if self._doingHeader:
            tagId = 'th'
        self.html(tagId,openTag=False)
        self._columnOpen = False
    #end def

    def nextColumn(self, *args, **kwds):
        """Switch to the next cell. First close the column if started then
        open the next column.
        """
        if self._currentColumn >= 0:
            self.closeColumn()
        self.openColumn(self._currentColumn+1, *args, **kwds)
        self._currentColumn += 1
#        if len(args)>0:
#            self.html(*args)
    #end def

    def _mkColumnHeaders(self, doFooter=False):
        """Make column headers NEED TO BE DEFINED
        TODO: add foot functionality.
        """
        headers = nTzap(self.columnFormats, 0)
        #print "headers>", headers
#        doHeaders = False
#        for h in headers:
#            if h != None:
#                doHeaders = True
#                break
#        #end for
#        if not doHeaders:
#            nTerror("in MakeHtmlTable#_mkColumnHeaders Headers are now mandatory")
#            return True

        tagId = 'thead'
        if doFooter:
            tagId = 'tfoot'

        formats = {}
        if not self.showHeader:
            formats = { 'style': "display:none;"}
        self.html(tagId, closeTag=False, **formats)
        self.html('tr', closeTag=False)
        self._doingHeader = True
        for i,h in enumerate(headers):
            self.openColumn(i)
            if h:
#                self.html('i', h) # Formating done in js/css.
                self.html(None, h)
            self.closeColumn()
        #end for
        self.html('tr', openTag=False)
        self.html(tagId, openTag=False)
        self._doingHeader = False
    #end def
#end class


def _makeDihedralByProjectTableHtml( obj, residues, text=None, ncols=10, pictureBaseName = None,
#            imageWidth = imageSmall2DdihedralWidth,
            imageHeight = imageSmall2Ddihedralheight ):
    """
    Make a table with links to residues in html.main of obj

    If the pictureBaseName is not None then insert it from it's residue directory
    if it's present.

    Return True on error.
    """

    width = '6.0em' # reserve some space per residue in chain table
    kwds = { 'style': "width: %s" % width }
    kwds['align'] = 'right'

    html = obj.html
    main = html.main
#    if text:
#        main('h1',text)
    if not residues:
        nTerror("Failed to _makeResidueTableHtml")
        return True

    r0 = residues[0]
    r1 = r0.resNum
    r2 = r0.resNum/ncols *ncols + ncols-1
    main('table', closeTag=False)
    main('tr', closeTag=False)
    main( 'td',sprintf('%d-%d',r1,r2), **kwds )
    for _emptyCell in range( r0.resNum%ncols ):
        main('td', **kwds)
#        main('td')

    prevRes = None
    project = obj.html.project
    for res in residues:
        chainBreakDetected = (prevRes!=None) and (prevRes.resNum != (res.resNum - 1))
        if chainBreakDetected or res.resNum%ncols == 0:
            r1 = res.resNum/ncols *ncols
            r2 = r1+ncols-1
            main('tr', openTag=False)
            main('tr', closeTag=False)
            main('td',sprintf('%d-%d',r1,r2), **kwds)
            for _emptyCell in range( res.resNum%ncols ):
                main('td', **kwds)

        # add residue to table
        main('td', closeTag=False, **kwds)

        html.insertHtmlLink(main, obj, res, text=res.name)
        if pictureBaseName:
            # file:///Users/jd/tmp/cingTmp/1brv.cing/1brv/HTML/Dihedrals/Ramachandran.html#_top
            tailLink = os.path.join( htmlDirectories.molecule, res.chain.name, res.name,  pictureBaseName + ".png" )
            relLink = os.path.join('../', tailLink)
            absLink = os.path.join( project.moleculePath(), moleculeDirectories.html, tailLink )
#            print tailLink, relLink, absLink
            main('br')
            if os.path.exists(absLink):
#            if True:
                main('a',   "",         href = relLink, closeTag=False )
                main('img', "",         src=relLink, height=imageHeight)#, width=imageWidth )
                main('a',   "",         openTag=False )
            else:
                main('a', "n/a")
        # end if
        main('td', openTag=False)
        prevRes = res
    #end for over res in residues

    main('tr', openTag=False)
    main('table', openTag=False)
#end def

def _makeDihedralByResidueTableHtml( obj, residues, text=None, #ncols=10, pictureBaseName = None,
#            imageWidth = imageSmall2DdihedralWidth,
            imageHeight = imageSmall2Ddihedralheight ):
    """
    Make a table with aligned dihedral angle plots of one row per residue.

    Per chain it will check if a dihedral is present at all for any residue and not bother to show it
    if it's absent for all. This does involve some queries to filesystem twice but this is assumed not
    to be an insignificant slowdown. It is clever enough to scan only the dihedrals expected for it
    being protein or nucleic acid. Mixed chains (containing AA and NA) will be shown well.

    Return True on error.
    """

    dihedralListAA = """    Ramachandran Janin D1D2
                            PHI PSI OMEGA
                            CHI1 CHI2 CHI3 CHI4 CHI5 CHI6
                            CHI32 CHI42
                      """.split()

    dihedralListNA = """    ALPHA BETA GAMMA DELTA EPSILON ZETA
                            NU0 NU1 NU2 NU3 NU4 CHI
                    """.split()

    width = '6.0em' # reserve some space per residue in chain table
    kwds = { 'style': "width: %s" % width }
    kwds['align'] = 'right'

    html = obj.html
    main = html.main
#    if text:
#        main('h1',text)
    if not residues:
        nTerror("Failed to _makeAllDihedralTableHtml because there are no residues given.")
        return True

    project = obj.html.project
    dihedralColumnNameHash = {} # use hash for speed.
    for res in residues:
        if not (res.hasProperties('protein') or res.hasProperties('nucleic')):
#            nTdebug("Skipping non-standard residue")
            continue
        if res.hasProperties('protein'):
            dihedralList = dihedralListAA
        if res.hasProperties('nucleic'):
            dihedralList = dihedralListNA
        for dihedralName in dihedralList:
            if dihedralColumnNameHash.has_key(dihedralName):
                continue
            tailLink = os.path.join( htmlDirectories.molecule, res.chain.name, res.name,  dihedralName + ".png" )
            absLink = os.path.join( project.moleculePath(), moleculeDirectories.html, tailLink )
#            nTdebug( "tailLink, absLink %s %s" %(tailLink, absLink))
            if os.path.exists(absLink):
#                nTdebug("Adding %s" % dihedralName)
                dihedralColumnNameHash[dihedralName] = None
#            else:
#                dihedralColumnNameHash[dihedralName] = None # Disable when done debugging.

    dihedralColumnNameList = []
    dihedralListAny = dihedralListAA + dihedralListNA
    for dihedralName in dihedralListAny:
        if not dihedralColumnNameHash.has_key(dihedralName):
            continue
        dihedralColumnNameList.append(dihedralName)

    if not dihedralColumnNameList:
#        nTdebug("Failed to find any dihedral plot on file")
        main('h2', "No plots available")
        return

    main('table', closeTag=False)
    main('td', "Residue")
    for dihedralName in dihedralColumnNameList:
        main('td', closeTag=False, **kwds)
        relLink = dihedralName + '.html'
        main('a',   dihedralName,      href = relLink, id=dihedralName, closeTag=False )
        main('a',  openTag=False )
        main('td', openTag=False)
    #end for

    for res in residues:
        if not (res.hasProperties('protein') or res.hasProperties('nucleic')):
#            nTdebug("Skipping non-standard residue such as water.")
            continue
        if not res.hasCoordinates():
#            nTdebug("Skipping residue without any coordinates for any of it's atoms.")
            continue

        # Start to writ the residue on one row.
        main('tr', closeTag=False, **kwds)
        main('td', closeTag=False, **kwds)
        html.insertHtmlLink(main, obj, res, text=res.name)
        for dihedralName in dihedralColumnNameList:
            main('td', closeTag=False, **kwds)
            tailLink = os.path.join( htmlDirectories.molecule, res.chain.name, res.name,  dihedralName + ".png" )
            relLink = os.path.join('../', tailLink)
            absLink = os.path.join( project.moleculePath(), moleculeDirectories.html, tailLink )
#            nTdebug( "tailLink, relLink, absLink %s %s %s" %(tailLink, relLink, absLink))
            if os.path.exists(absLink): # enable check when done debuging.
#            if True:
                main('a',   "",         href = relLink, closeTag=False )
                main('img', "",         src=relLink, height=imageHeight)#, width=imageWidth )
                main('a',   "",         openTag=False )
            else:
                main('a', "n/a")
            main('td', openTag=False)
        #end for over res in residues

    main('tr', openTag=False)
    main('table', openTag=False)
#end def

# A list of all htmlobject for rendering purposes
htmlObjects = NTlist()

class HTMLfile:
    '''Description: Class to create a Html file; to be used with cing.css layout.
       Inputs: file name, title
       Output: a Html file.

       gv 1 Sep 2008: Implemented 'None' tag
       gv 3 Sep 2008: Moved out of classes file in cing/core
       gv 3 Sep 2008: implemented kwds to insertHtmlLink and insertHtmlLinkInTag
    '''

    NotAvailableText = 'Not available'
    OpenText         = 'Open'
    help_html        = 'help.html'
    top              = '#_top'
    headerSectionId  = 'header'

    def __init__( self, fileName, project, title = None, **kwds ):
        '''Description: __init__ for HTMLfile class.
           Inputs: file name, title
           Output: an instantiated HTMLfile obj.

           GV Not any longer as I do not see the need: The file is immediately tested by a quick open for writing and closing.
        '''

        self.fileName = nTmkdir( fileName )
#        self.rootPath, _tmp, _tmp = nTpath( fileName )
#        self.stream = open( self.fileName, 'w' )
#        self.stream.close()

        # definition of content-less  tags
        self.noContent = [ 'base','basefont','br','col','frame','hr','img',
                           'input','link','meta','ccsrule']#, 'script' ]

        self.title   = title
        self.project = project
        self.reset()
        htmlObjects.append( self )

        for key,value in kwds.iteritems():
            setattr(self,key,value)
    #end def

    def reset(self):
        """
        Reset all HTML code
        """
        self.indent  = 0
        self._header = NTlist()
        self._call   = NTlist()
        self._main   = NTlist()
        self._left   = NTlist()
        self._right  = NTlist()
        self._footer = NTlist()
    #end def

    def _resetCingContent(self):
        """
        Reset HTML content (call, main, left, right) code
        """
        self._header = NTlist()
        self._main   = NTlist()
        self._left   = NTlist()
        self._right  = NTlist()
        self._footer = NTlist()
    #end def

    # Having a del method might upset the gc.
#    def __del__(self):
#        print '>>deleting>', self.title, self.fileName
#        print self
#        if self in htmlObjects:
#            htmlObjects.remove(self)
#        del( self )
#    #end def

    def killHtmlObjects():  # note there is no 'self', it's going to be a static method!
        """ Remove all objects from the htmlObjects list
            """
        while htmlObjects.pop():
            pass # I think this should work to clear the list
    #end def
    killHtmlObjects = staticmethod( killHtmlObjects)

    def _appendTag( self, htmlList, tag, *args, **kwds ):
        '''Description: core routine for generating Tags.
           Inputs: HTMLfile obj, list, tag, openTag, closeTag, *args, **kwds.
           Output: list.
        '''
        self.indent += 1
        if tag:
            htmlList.append( self._generateTag( tag, *args, **kwds ) )
        else:
            for arg in args:
                htmlList.append( str(arg) )
        self.indent -= 1
    #end def

    def _generateTag( self, tag, *args, **kwds ):
        '''Description: core routine for generating Tags.
           Inputs: HTMLfile obj, tag, openTag, closeTag,
                   newLine, *args, **kwds.
           Output: list.
        '''

        #self.indent += 1

        if kwds.has_key('openTag'):
            openTag = kwds['openTag']
            del kwds['openTag']
        else:
            openTag = True

        if kwds.has_key('closeTag'):
            closeTag = kwds['closeTag']
            del kwds['closeTag']
        else:
            closeTag = True

        if kwds.has_key('newLine'):
            newLine = kwds['newLine']
            del kwds['newLine']
        else:
            newLine = True
        v = { True: None, False: -1 }

        #print '****', htmlList,'*',tag,'*', openTag,'*', closeTag, '*', args

        if openTag and closeTag:
            s = ( self.openTag( tag, *args, **kwds )[:-1] +
                  self.closeTag(tag)[self.indent:v[newLine]] )
        elif openTag:
            s = ( self.openTag( tag, *args, **kwds ) )
        elif closeTag:
            s = ( self.closeTag( tag, *args, **kwds ) )
        #end if
        #self.indent -=1

        return s
    #end def

    def header( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._header, tag, *args, **kwds )
        self.indent -=1
    #end def

    def __call__( self, tag, *args, **kwds ):
        "Write openTag, content, closeTag (if appropriate)"
        self.indent +=1
        self._appendTag( self._call, tag, *args, **kwds )
        self.indent -=1
    #end def

    def main( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._main, tag, *args, **kwds )
        self.indent -=1
    #end def

    def left( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._left, tag, *args, **kwds )
        self.indent -=1
    #end def

    def right( self, tag, *args, **kwds ):
        self.indent +=1
        self._appendTag( self._right, tag, *args, **kwds )
        self.indent -=1
    #end def

    def footer( self, tag, *args, **kwds ):
        self._appendTag( self._footer, tag, *args, **kwds )
    #end def

    def generateHtml(self, htmlOnly=False):
        """This is a prototype and this method should be superseeded
        """
        pass
    #end def


    def insertMinimalHeader( self, src ):
        self.insertHtmlLink( self.header, src, self.project, text = 'Home' )
        self.insertHtmlLink( self.header, src, self.project.molecule, text = 'Molecule' )

    def render(self):
        '''Description: write container to file Html.
           Inputs: a HTMLfile obj.
           Output: written lines and closed file.

           JFD notes it is simpler to code this as constructing the whole content
           first and then writing. It would be just as fast for the size
           of html files we render.
        '''

        self.stream = open( self.fileName, 'w' )
#        nTdebug('writing to file: %s' % self.fileName)
        self.indent = 0
        # JFD proposes to drop the below tags because they hinder javascript beyond my knowledge.
        # AWSS updated it: it should work fine with javascript
        self.stream.write(self.openTag('!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'))
        self.stream.write(self.openTag('html'))
        self.stream.write(self.openTag('head'))
        if self.title:
            self.stream.write( self._generateTag( 'title', self.title ))

        relativePath = self.relativePath()

        icon_emailSrc = os.path.join(relativePath, "icon_email.gif")
        # other util JS utilities
        # multiline popups by JavaScript
        # jQuery JS utilities
        # custom JS utilities for working with jQuery
        importJsListStr = """
            multilineTitles.js
            util.js
            jquery.js
            customTables.js
            dataTableMedia/js/jquery.dataTables.js
            dataTableMedia/js/TableTools.js
            dataTableMedia/ZeroClipboard/ZeroClipboard.js
            """

        importCssListStr = """
            cing.css
            dataTableMedia/css/demo_table.css
            dataTableMedia/css/TableTools.css
            """

#<link media="screen" href="../cing.css" type="text/css" rel="stylesheet"/>
        for css in importCssListStr.split():
            css = os.path.join(relativePath, css)
            self.stream.write(self._generateTag( 'link',
                href=css, type="text/css", media="screen", rel="stylesheet" ))

        for js in importJsListStr.split():
            js = os.path.join(relativePath, js)
#            nTdebug("Working on %s" % js)
            self.stream.write(self._generateTag( 'script',
                src=js, type="text/javascript"))


        self.stream.write(self.closeTag('head'))
        self.stream.write(self.openTag('body'))
        self.stream.write(self.openTag('div', id="container"))
        self.indent += 1

        #header
        self.stream.write( self.openTag('div', id = 'header') )
        self.stream.writelines(self._header)
        fprintf(self.stream, '%s%s', '\t' * self.indent,'<!-- end header -->')
        self.stream.write( self.closeTag('div') )

        #main
        self.stream.write( self.openTag('div', id = 'main') )
        self.stream.write( self._generateTag('a', id=self.top, name=self.top) )
#        self.stream.write( self.closeTag('a') )
        self.stream.writelines(self._call + self._main)

        # left section
        if self._left:
            self.indent += 1
            self.stream.write( self.openTag('div', id = 'left') )
            self.stream.writelines(self._left)
            fprintf(self.stream, '%s%s', '\t' * self.indent,'<!-- end left -->')
            self.stream.write(self.closeTag('div'))
            self.indent -= 1
        #end if

        # right section
        if self._right:
            self.indent += 1
            self.stream.write( self.openTag('div', id = 'right') )
            self.stream.writelines(self._right)
            fprintf(self.stream, '%s%s', '\t' * self.indent,'<!-- end right -->')
            self.stream.write(self.closeTag('div'))
            self.indent -= 1
        #end if

        fprintf(self.stream, '%s%s', '\t' * self.indent,'<!-- end main -->')
        self.stream.write(self.closeTag('div'))
        self.stream.write(self._generateTag( 'br', style="clear: both;" ))

        self.indent = 0
        fprintf(self.stream, '%s%s', '\t' * self.indent,'<!-- end container -->')
        self.stream.write(self.closeTag('div'))

        self.stream.write(self.openTag('div', id = 'footer'))
        # Append a default footer
        defaultFooter = NTlist()
        self._appendTag( defaultFooter, 'p', closeTag=False)
        self._appendTag( defaultFooter, None, sprintf( ' %s version %s ', programName, cingVersion) )

#        if not cingRevision:
#            nTdebug("Trying to get CING revision; again...")
#            cingRevision = getSvnRevision()

#        nTdebug("CING revision [%s]" % cingRevision)
        if cingRevision:
            cingRevisionUrlStr = cingRevisionUrl + repr(cingRevision)
            self._appendTag( defaultFooter, None, '(' , closeTag=False)
            self._appendTag( defaultFooter, 'a', 'r'+repr(cingRevision), href=cingRevisionUrlStr)
            self._appendTag( defaultFooter, None, ')' , openTag=False)

        self._appendTag( defaultFooter, None, ' ' )
        n = len(authorList)-1
        for i,author in enumerate(authorList):
            self._appendTag( defaultFooter, None, author[0] )
            self._appendTag( defaultFooter, 'a', href=sprintf("mailto:%s", author[1]), closeTag=False)
            self._appendTag( defaultFooter, 'img', src=icon_emailSrc)
            self._appendTag( defaultFooter, 'a', openTag=False)
            if i==(n-1):
                self._appendTag( defaultFooter, None,' and ')
            elif i<n:
                self._appendTag( defaultFooter, None, ', ')
        #end for
        self._appendTag( defaultFooter, 'p',openTag=False)
        self.stream.writelines(self._footer + defaultFooter)
        fprintf(self.stream, '%s%s', '\t' * self.indent,'<!-- end footer -->')
        self.stream.write(self.closeTag('div'))

        self.indent=0

        # Text has to be right before the closing body tag.
        # Othersise JFD would have customized footer of subclass ProjectHTMLfile
        if isinstance(self, ProjectHTMLfile):
#            nTdebug("Writing google spy to project html footer")
            self.stream.write(GOOGLE_ANALYTICS_TEMPLATE)

        self.stream.write(self.closeTag('body'))
        self.stream.write(self.closeTag('html'))

        self.stream.close()
    #end def

    def tag( self, tag, *args, **kwds ):
        "Return (openingTag, content, closingTag) triple"

        #print '*****', tag, [args], (kwds)
        openTag = sprintf('<%s',tag)
        for key,value in kwds.iteritems():
            openTag = openTag + sprintf(' %s="%s"', key, value)
        #end for

        if (tag in self.noContent):
            openTag = openTag +  '/>'
        else:
            openTag = openTag +  '>'
        #end if

        # JFD found bug with using "from cgi import escape"; didn't work for me. Changed to below is also good
        # idea because of security according to first comment at: http://code.activestate.com/recipes/52220/
        # Can't seem to get this fixed so jus inlining the method.
        content = ''
        if args:
            content = self.escape(''.join(args))

        if (tag in self.noContent):
            closeTag = ''
        else:
            closeTag = sprintf('</%s>',tag)
        #end if
        return (openTag,content,closeTag)
    #end def

    def openTag( self, tag, *args, **kwds ):
        "Write openTag, content; NO closeTag"
        openTag, content, dummyCloseTag = self.tag( tag, *args, **kwds )
        return sprintf( '%s%s%s\n', '' + '\t' * self.indent, openTag, content )
    #end def

    def closeTag( self, tag, *args, **kwds ):
        "Write closeTag *args"
        dummyOpenTag, content, closeTag = self.tag( tag, *args, **kwds )
        return sprintf( '%s%s%s\n', '' + '\t' * self.indent, closeTag, content )
    #end def

    def relativePath(self):
        ''' Description: return relative path between htmlObj and project
            directory.
            Inputs: htmlObj
            Output: relative path to project html location
            Example: htmlObj molecule: Ccpn_1brv
                     project.molecule.html.fileName (1brvV1.cing/Ccpn_1brv/HTML/Molecule/index.html)
                     returns: '../../'
        '''
        fileName = self.fileName
        sep = os.path.sep
        #pardir = os.path.pardir
        pardirSep = '../' #pardir + sep # '../' is standard for html, no matter if Windows OS.
        upSep   = fileName.count(sep)
        htmlPath = self.project.htmlPath()
#        nTdebug("htmlPath: ["+htmlPath+"]" )
        downSep = htmlPath.count(sep)
        return (upSep-downSep-1) * pardirSep

#    def findHtmlLocationResidueIndex(self, source, destinationResidue, id=None ):
#        if not hasattr(source,'htmlLocation'):
#            nTerror('findHtmlLocationResidue: No htmlLocation attribute associated to object %s', source)
#            return None

    def findHtmlLocation(self, source, destination, id=None ):
        '''Description: given 2 Cing objects returns the relative path between them.
           Inputs: Cing objects souce, destination
           Output: string path or None or error

           E.g. input: source.htmlLocation[0]     : test_HTMLfile.cing/index.html
                       destination.htmlLocation[0]: test_HTMLfile.cing/moleculeName/HTML/indexMolecule.html
                output                            : moleculeName/HTML/indexMolecule.html
        '''
        # Debugger perspecitive put at source (me)
        # Destination is the target.
        for item in [source, destination]:
            if not hasattr(item,'htmlLocation'):
#                nTerror('HTMLfile.findHtmlLocation: No htmlLocation attribute associated to object %s', item)
                return None

        # Strip leading dot for rest of algorithm.
        # Normalize path, eliminating double slashes, etc.
        sourcePath = os.path.normpath(     source.htmlLocation[0])
        destPath   = os.path.normpath(destination.htmlLocation[0])
        # Get default id. It may be None.
        destId     = destination.htmlLocation[1]
        # Or override.
        if id:
            destId = '#' + id

        listSourcePath = sourcePath.split('/')
        listDestPath   = destPath.split('/')

        # JFD next code is disabled because the comparison might shortcircuit
        # when identical names are matched 'by accident'.
#        for index in range(lenSP):
#            if listSourcePath[index] != listDestPath[index]:
#                #location = index * ['..'] + listDestPath
#                break
#        i = lenSP - 1 - index
#        locationList = (index + i) * ['..'] + listDestPath
#        loc = ''
#        for item in location:
#            loc = os.path.join(loc,item)
#        loc = os.path.join( *locationList )

        # How far away (in dir changes) am I from the first (left/cing) dir?
        # The list will look like:  list: ['test_HTMLfile.cing', 'index.html']
        # One jump is one directory.
        # E.g. 1brv/1brv/index.html has 2 jumps.

        toLeftNumberOfJumpsSource = len(listSourcePath) - 1
        toLeftNumberOfJumpsDest   = len(listDestPath)   - 1

        # Any same leading directories may be ommited.
        # using the fact that they are rooted in the same starting dir (curdir)
        toLeftNumberOfJumpsSourceNew = toLeftNumberOfJumpsSource
        i = 0
        while i < toLeftNumberOfJumpsDest and i < toLeftNumberOfJumpsSource:
            if listSourcePath[i] == listDestPath[i]:
                toLeftNumberOfJumpsSourceNew -= 1
            else:
                break
            i += 1
        jumpsToRemove = toLeftNumberOfJumpsSource - toLeftNumberOfJumpsSourceNew
        listDestPathNew = listDestPath[jumpsToRemove:]
        locationList = toLeftNumberOfJumpsSourceNew * ['..']
        locationList += listDestPathNew
        loc = os.path.join( *locationList )
        loc = os.path.normpath(loc) # I don't think it's needed anymore but can't hurt either.
        if destId == None:
            return loc
        return loc + destId

    def insertHtmlLink( self, section, source, destination, text=None, id=None, **kwds ):
        '''Description: create the html command for linking Cing objects.
           Inputs: section (main, header, left etc.), source obj., destination
                   obj., html text, id.
           Output: <a class="red" href="link">text</a> inside section

           Example call: project.html.insertHtmlLink( main, project, item, text=item.name )

           And the funny thing is that if the destination has an attribute:
               'rogScore.colorLabel' then it will be used to define an html class with
               which through the cing.css can be used for defining coloring
               schemes.
        '''

        if not section:
            nTerror("No HTML section defined here")
            return None

        if not source:
            # Happens for 2k0e
#            nTdebug("No Cing object source in insertHtmlLink( self, section, source, destination, text=None, id=None, **kwds ):")
#            nTdebug("[%s, %s, %s, %s, %s, %s, %s]" % ( self, section, source, destination, text, id, kwds ))
            return None

        if not destination:
            # Happens for 2k0e and all projects with missing topology
#            nTdebug("No Cing object destination in insertHtmlLink( self, section, source, destination, text=None, id=None, **kwds ):")
#            nTdebug("[%s, %s, %s, %s, %s, %s, %s]" % ( self, section, source, destination, text, id, kwds ))
            return None

        link = self.findHtmlLocation( source, destination, id )
#        nTdebug('From source: %s to destination: %s, id=%s using relative link: %s' ,
#                 source.htmlLocation, destination.htmlLocation, id,link)

        kw = {'href':link}
        #if not destination.has_key('colorLabel'):
        if hasattr(destination, 'rogScore'):
#            destination.colorLabel = COLOR_GREEN
            if destination.rogScore.isCritiqued():
                # solution for avoiding python 'class' command with html syntax
                kw['class'] = destination.rogScore.colorLabel
                destination.rogScore.addHTMLkeywords( kw )
        #end if
        kw.update(kwds)
        section('a', text, **kw)
    #end def

    def insertHtmlLinkInTag( self, tag, section, source, destination, text=None, id=None, **kwds):
        '''Description: create the html command for linking Cing objs inside a tag.
           Inputs: tag, section (main, header, left etc.), source obj.,
                   destination obj., html text, id.
           Output: <h1><a class="red" href="link">text</a></h1> inside section

        Example call:
                    project.html.insertHtmlLinkInTag( 'li', main, project, item, text=item.name )

        '''
        section(tag, closeTag=False)
        self.insertHtmlLink(section, source, destination, text=text, id=id, **kwds)
        section(tag, openTag=False)

    def escape(self, s, quote=None): # TODO: fall back to cgi.escape() when possible.
        '''Replace special characters "&", "<" and ">" to HTML-safe sequences.
        If the optional flag quote is true, the quotation mark character (")
        is also translated.'''
        s = s.replace("&", "&amp;") # Must be done first!
        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        if quote:
            s = s.replace('"', "&quot;")
        return s

#end class

class ProjectHTMLfile( HTMLfile ):
    """
    Class to generate HTML files for Project instance
    """

    def __init__(self, project ):
        # Create the HTML directory for this project

        fileName = project.htmlPath('index.html') # resides in HTML directory
        title = 'Project ' + project.name
        HTMLfile.__init__(self, fileName, title = title, project=project)
        project.htmlLocation = ( fileName, HTMLfile.top )

        if project.has_key('html'):    # delete any old instances
            del(project['html'])
        project.html = self
        copyCingHtmlJsAndCssToDirectory(project.htmlPath())
        #css and javascript now in HTML dir
        htmlPath = os.path.join(cingRoot,cingPaths.html) # copy needed css and other files/directories.

#        nTdebug("Listing: [%s]" % htmlPath )
        for f in os.listdir( htmlPath ):
#            nTdebug("Listing item: [%s]" % f)
            htmlFile = os.path.join(htmlPath,f)
            if os.path.isfile(htmlFile):
                shutil.copy( htmlFile, project.htmlPath() )
            elif os.path.isdir(htmlFile):
#                nTdebug("Listing dir: [%s]" % f)
                if f.find('.svn') >= 0:
                    continue
                dst = os.path.join( project.htmlPath(), f)
#                nTdebug("Copying dir: [%s] to [%s]" % (htmlFile, dst))
                if os.path.exists(dst):
#                    nTdebug("Removing directory: %s" % dst)
                    shutil.rmtree(dst)
                shutil.copytree(htmlFile,  dst )
                # TODO: exclude .svn items within subdir
                svnDirectoryList = find2(".svn", startdir=dst) # don't use the one from pylab.
                for f2 in svnDirectoryList:
#                    nTdebug("Considering removing directory: %s" % (f2))
                    if os.path.exists(f2):
#                        nTdebug("Removing directory: %s" % f2)
                        shutil.rmtree(f2)

            # end elif
        #end for

        # create an redirect index page in top of project
        # Changed time to 1 second so that the user at least knows she is redirected and
        # the browser back functionality is maintained.
        timeToWait = '1'
        fmt = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>%s
</title>
<meta http-equiv="Refresh" content="%s; url=%s">
</head>
<body>
<H1>Redirecting to %s in %s seconds.</H1>
</body>
</html>
'''
        f = open(project.path('index.html'),'w')
        path = os.path.join(self.project.molecule.name, moleculeDirectories['html'], 'index.html')
        fprintf(f, fmt, title, timeToWait, path, path, timeToWait)
        f.close()
    #end def

    def _generateSummaryHtml( self ):
        """
        Generate summary in Html format
        """
        fileName = self.project.htmlPath( 'summary.html' )
        html = HTMLfile( fileName, title = 'Project summary', project=self.project )
        html.htmlLocation = (fileName, HTMLfile.top) # Fake an object location; see below

        html.header('h1', 'Summary: ' + self.project.name )
        html.insertHtmlLink(html.header, html, self.project, text='Home' )

#        htmlsum = HTMLfile( self.project.htmlPath( 'summary.html' ),title = 'Project summary' )
#        htmlsum.htmlLocation = (self.project.htmlPath('summary.html'), '#_top') # Fake an object location; see below
#        htmlsum.header('h1', 'Summary project ' + self.project.name )
#        htmlsum.header('a', 'Home', href='../../index.html' )    #TODO: fix explicitly coded path

        s = self.project.summaryForProject( toFile = False).split('\n' )

        # Create a two-state machinery.
        summaryLineCount = len(s)
        i = 0
        while i < summaryLineCount:
            line = s[i]
            if line[0:5] == '-----':
                html.main('h3', line )
            elif line.startswith('<PRE>'): # should occur alone on line!
                preLineList = []
                while True:
                    i += 1
                    if i >= summaryLineCount:
                        nTcodeerror("Failed to find </PRE> all the way to the end")
                        break
                    line = s[i]
                    if line.startswith('</PRE>'): # should occur alone on line!
                        break
                    preLineList.append( line )
                subStr = '\n'.join(preLineList)
                html.main('pre', subStr)
            else:
                html.main('br', line )
            i += 1
        #end while
        html.render()
        return html
    #end def

    def _generateHistoryHtml( self ):
        fileName = self.project.htmlPath( 'history.html' )
        html = HTMLfile( fileName, title = 'Project history', project=self.project )
        html.htmlLocation = (fileName, HTMLfile.top) # Fake an object location; see below

        html.header('h1', 'History project ' + self.project.name )
        html.insertHtmlLink(html.header, html, self.project, text='Home' )

        for date,content in self.project.history:
            html.main('h3',date)
            for line in content.split('\n'):
                html.main(None, line)
            #end for
        #end for

        html.render()
        return html
    #end def

    def _generateLogsHtml( self ):
        """
        Match code to classes#addLog etc.
        """
        fileName = self.project.htmlPath( 'logs.html' )
        html = HTMLfile( fileName, title = 'Project logs', project=self.project )
        html.htmlLocation = (fileName, HTMLfile.top) # Fake an object location; see below

        html.header('h1', 'Logs project ' + self.project.name )
        html.insertHtmlLink(html.header, html, self.project, text='Home' )

        html.main('h3', 'Logs')
#        html.main('ul', closeTag=False)
        logsDir = self.project.path(directories.logs)
        logFileList = glob1(logsDir, '*.txt')
        if logFileList:
            logFileList.sort()
            logFileList.reverse() # Important to have latest on top because they might get long. Use p.removeOlderLogs() then.
        n = len(logFileList)
        for i, logFile in enumerate(logFileList):
            idx = n - i
            # Create a link to the actual HTML log file.
            html.main('p', str(idx), closeTag=0)
            html.main('a', logFile, href="../../Logs/%s" % logFile)
            html.main('P', openTag=0)
        #end for
#        html.main('ul', openTag=False)
        html.render()
        return html
    #end def

    def generateHtml( self, htmlOnly = False ):
        """Generate all html for the project page.
        """

        self._resetCingContent()
        self.header('h1', 'Project: ' + self.project.name)

        htmlMain = self.main
        # devide Page using Table; TODO: should be in css???
        htmlMain('table', closeTag=False)
        htmlMain('tr', closeTag=False)
        htmlMain('td', closeTag=False)

        # General section
        self.main('h1', 'Project')
        self.main('ul', closeTag=False)
        if hasattr(self, 'summary'):
            del(self.summary)
        self.summary = self._generateSummaryHtml()
        self.insertHtmlLinkInTag( 'li', self.main, self.project, self.summary, text='Summary')

        #Use a dummy object for referencing the text-files for now
        flatFiles = NTdict()
#        flatFiles.htmlLocation = (self.project.moleculePath('analysis'), HTMLfile.top )
        flatFiles.htmlLocation = (self.project.moleculePath('analysis'), None )
        self.insertHtmlLinkInTag('li',self.main, self.project, flatFiles, text="Details (flat)")

        #Use a dummy object for referencing the text-files for now
        progFiles = NTdict()
#        progFiles.htmlLocation = (self.project.moleculePath(), HTMLfile.top )
        progFiles.htmlLocation = (self.project.moleculePath(), None )
        self.insertHtmlLinkInTag('li',self.main, self.project, progFiles, text="Programs (flat)")

        if hasattr(self, 'history'):
            del(self.history)
        self.history = self._generateHistoryHtml()
        self.insertHtmlLinkInTag( 'li', self.main, self.project, self.history, text='History')

        if hasattr(self, 'logs'):
            del(self.logs)
        self.logs = self._generateLogsHtml()
        self.insertHtmlLinkInTag( 'li', self.main, self.project, self.logs, text='Logs')
        self.main('ul', openTag=False)

        # Molecule page and assignment links
        htmlMain('h1', 'Molecule ')
        htmlMain('ul', closeTag=False)
        self.insertHtmlLinkInTag( 'li', htmlMain, self.project, self.project.molecule,
                                        text=self.project.molecule.name
                                )

        if hasattr(self.project.molecule, 'atomList'):
            self.insertHtmlLinkInTag( 'li', htmlMain, self.project, self.project.molecule.atomList, text='Assignments' )

        self.insertHtmlLinkInTag( 'li', htmlMain, self.project, self.project.dihedralByProjectList, text='Dihedrals' )
        self.insertHtmlLinkInTag( 'li', htmlMain, self.project, self.project.dihedralByResidue, text='Dihedrals by Residue' )

        htmlMain('ul', openTag=False)

        # peaks
        if len(self.project.peaks):
            htmlMain('h1', 'Peaks')
            htmlMain('ul', closeTag=False)
            for pl in self.project.peaks:
                if hasattr(pl,'html'):
#                    nTdebug("Doing peaks [%s] " % (pl.name))
                    self.insertHtmlLinkInTag( 'li', htmlMain, self.project, pl, text=pl.name)
            htmlMain('ul', openTag=False)
        #end if

        # restraints
        rlists = self.project.allRestraintLists()
        if len(rlists) > 0:
            htmlMain('h1', 'Restraints')
            htmlMain('ul', closeTag=False)
            for rl in rlists:
                if hasattr( rl, 'html'):
                    self.insertHtmlLinkInTag( 'li', htmlMain, self.project, rl, text=rl.name)
            htmlMain('ul', openTag=False)
        #end if

        # Credits
        htmlMain('h1', 'Other')
        htmlMain('ul', closeTag=False)
        htmlMain('a',  'Credits', href = 'credits.html' )
        htmlMain('ul', openTag=False)

        # Try to put nice gif of first page
        molGifFileName = "mol.gif"
        pathMolGif     = self.project.htmlPath(molGifFileName)
        if not htmlOnly:
            if hasattr(plugins, MOLGRAP_STR) and plugins[ MOLGRAP_STR ].isInstalled:
                nTdebug("ProjectHtmlFile.generateHtml: trying to create : " + pathMolGif)
                if self.project.molecule.export2gif(pathMolGif, project=self.project):
                    nTwarning("Failed to get the molecular image but using a default image instead")
                # end if
#                which convert TODO:
#            else:
#                nTdebug("Skipping self.project.molecule.export2gif because Molgrap Module is not available.")

        #end if
        if os.path.exists( pathMolGif ):
            htmlMain('td', openTag=False)
            htmlMain('td', closeTag=False)
            htmlMain('img', src = 'mol.gif')
            htmlMain('td', openTag=False)
            htmlMain('tr', openTag=False)
        #end if

        htmlMain('table', openTag=False)
        self.render()
    #end def
#end class

class DihedralByProjectHTMLfile( HTMLfile ):
    """
    Class to generate HTML files for combined Dihedral instance
    """
    ncols = 5

    def __init__(self, project, dihedralByProject ):
        # Create the HTML directory for this dihedral
        fileName = project.htmlPath( htmlDirectories.dihedrals, dihedralByProject.name + '.html' )
        dihedralByProject.htmlLocation = ( fileName, HTMLfile.top )
#        nTdebug("dihedralByProject.htmlLocation[0]: %s" % dihedralByProject.htmlLocation[0])
        HTMLfile.__init__(self, fileName, title='Dihedral by Project' , project=project)
        if hasattr(dihedralByProject, 'html'):
            del(dihedralByProject.html)
        dihedralByProject.html = self
        self.dihedralByProject = dihedralByProject
#        nTdebug("self.dihedralByProject.htmlLocation[0]: %s" % self.dihedralByProject.htmlLocation[0])
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate the HTML code and/or Figs depending htmlOnly
        """
        # Reset CING content
        self._resetCingContent()
        self.header('h1', 'Dihedral '+self.dihedralByProject.name)
        self.insertMinimalHeader(self.dihedralByProject)
        self.insertHtmlLink( self.header, self.dihedralByProject, self.project.dihedralByProjectList, text = 'Dihedrals by project')

#        self.main('h1','Residue-based analysis')
        mol = self.project.molecule
        for chain in mol.allChains():
#            print '>>',mol, chain
            self.insertHtmlLinkInTag( 'h1', self.main, mol, chain, text='Chain %s' % chain.name )
            _makeDihedralByProjectTableHtml( self.dihedralByProject, residues=chain.allResidues(), ncols=self.ncols,
                    pictureBaseName = self.dihedralByProject.name,
#                    imageWidth = imageSmall2DdihedralWidth)#,
                    imageHeight = imageSmall2Ddihedralheight)
#            alternativeMain = self.main,
        #end for
        self.render()
    #end def
#end class

class DihedralByResidueHTMLfile( HTMLfile ):
    """
    Class to generate HTML files for all dihedrals in one page.
    Dihedral by Residue
    """
    def __init__(self, project, dihedralByResidue ):
        # Create the HTML directory for this dihedral
        fileName = project.htmlPath( htmlDirectories.dihedrals, dihedralByResidue.name + '.html' )
        dihedralByResidue.htmlLocation = ( fileName, HTMLfile.top )
#        nTdebug("dihedralByResidue.htmlLocation[0]: %s" % dihedralByResidue.htmlLocation[0])
        HTMLfile.__init__(self, fileName, title="Dihedral plots by Residue", project=project)
        if hasattr(dihedralByResidue, 'html'):
            del(dihedralByResidue.html)
        dihedralByResidue.html = self
#        project.dihedralByResidue = dihedralByResidue # done in Project.__init__
        self.dihedralByResidue = dihedralByResidue
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate the HTML code and/or Figs depending htmlOnly
        """
        # Reset CING content
        self._resetCingContent()
        self.header('h1', self.dihedralByResidue.name)
        self.insertMinimalHeader(self.dihedralByResidue)
        self.insertHtmlLink( self.header, self.dihedralByResidue, self.project.dihedralByProjectList, text = 'Dihedrals by Project')

        self.main('h3', "Dihedral plots by Residue")

        mol = self.project.molecule
        for chain in mol.allChains():
            self.insertHtmlLinkInTag( 'h1', self.main, mol, chain, text='Chain %s' % chain.name )
            _makeDihedralByResidueTableHtml( self.dihedralByResidue, residues=chain.allResidues(),
#                    imageWidth = imageSmall2DdihedralWidth,
                    imageHeight = imageSmall2Ddihedralheight)
        self.render()
    #end def
#end class

class DihedralByProjectListHTMLfile( HTMLfile ):
    """
    Class to generate HTML file for ALL combined Dihedral instance.

    Hangs off the project but is really only used for the HTML generation and
    has no real representation in molecular system description of CING.
    """
    def __init__(self, project ):
        # Create the HTML directory for this dihedral
        title='Dihedrals by Project List'
        fileName = project.htmlPath( htmlDirectories.dihedrals, 'index.html' )
        dihedralByProjectList = project.dihedralByProjectList
        dihedralByProjectList.htmlLocation = ( fileName, HTMLfile.top )
#        nTdebug("dihedralByProject.htmlLocation[0]: %s" % dihedralByProject.htmlLocation[0])
        HTMLfile.__init__(self, fileName, project, title=title)
        if hasattr(dihedralByProjectList, 'html'):
#            del(dihedralByProject.html) #GV thinks this was an error as it throws an error when regenerating html
            del(dihedralByProjectList.html) #
        dihedralByProjectList.html = self
        self.dihedralByProjectList = dihedralByProjectList
        self.title=title
        self.molecule = project.molecule
#        nTdebug("self.dihedralByProject.htmlLocation[0]: %s" % self.dihedralByProject.htmlLocation[0])
        self.dihedralByResidueHTMLfile = DihedralByResidueHTMLfile(self.project, self.project.dihedralByResidue)

    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate the HTML code and/or Figs depending htmlOnly
        """
        # Reset CING content
        self._resetCingContent()
        self.header('h1', self.title)
        self.insertMinimalHeader(self.dihedralByProjectList)

        ncols = 6 # Needs to be 6 or adjust the formatting below in dihedralList with BOGUS inserted.

        main = self.main
        molecule = self.molecule

#        if not htmlOnly:
#            nTmessage("Creating dihedrals combined for all residues html")
#                if project.createHtmlWhatif():
#                    nTerror('Failed to createHtmlWhatif')
#                    return True

        bOGUS_DIHEDRAL_ID = 'BOGUS'
        # USE THE BOGUS for alignment within the table.
        # The LB dihedral is from a pseudo residue; probably of little use.
        dihedralList = """      Ramachandran Janin D1D2 BOGUS BOGUS BOGUS
                                PHI PSI OMEGA BOGUS BOGUS BOGUS
                                CHI1 CHI2 CHI3 CHI4 CHI5 CHI6
                                CHI32 CHI42 BOGUS BOGUS BOGUS BOGUS
                                ALPHA BETA GAMMA DELTA EPSILON ZETA
                                NU0 NU1 NU2 NU3 NU4 CHI
                                LB  BOGUS BOGUS BOGUS BOGUS BOGUS
                        """.split()


        dihedralPresentMap = {}
        moleculeDir = os.path.join(self.project.moleculePath(), moleculeDirectories.html, htmlDirectories.molecule)
        for residue in molecule.allResidues():
#            nTdebug("_generateDihedralByProjectHtml for %s" % residue)
            resDir =  os.path.join(moleculeDir, residue.chain.name, residue.name )
#            nTdebug("resDir: %s" % resDir)
            if not os.path.exists(resDir):
                nTerror("Failed to find resDir: %s" % resDir)
            for dihed in dihedralList:
                tmpPath = os.path.join(resDir, dihed + '.png') #@UnusedVariable
#                print 'tmpPath:', tmpPath, os.path.exists(tmpPath)
                if os.path.exists(tmpPath):
#                if True:
                    dihedralPresentMap[ dihed ] = None

        dihList = dihedralPresentMap.keys()


        self.dihedralByResidueHTMLfile.generateHtml(htmlOnly) # delay until full list is created.
        # only now available.
        self.insertHtmlLink( self.header, self.dihedralByProjectList, self.project.dihedralByResidue, text = 'Dihedrals by Residue') 
        self.header('a', 'Help', href = self.relativePath()+HTMLfile.help_html, title='goto page with help')


        main('h1','Dihedrals by Project')
#        main('h1','Dihedrals by Project',  closeTag=False)

        if dihList:
#            self.insertHtmlLink(main, dihedralByResidueHTMLfile, dihedralByResidue, text='('+dihedralByResidue.name+')')
#            main('h1', openTag=False)
            main('table',  closeTag=False)
            plotCount = 0 # The number of actual plots shown in the table
            for dihed in dihedralList:
                if plotCount % ncols == 0:
                    if plotCount:
                        main('tr',  openTag=False)
                    main('tr',  closeTag=False)
                main('td',  closeTag=False)
                if dihed != bOGUS_DIHEDRAL_ID and dihedralPresentMap.has_key(dihed):
                    dihedralByProject = NTtree( dihed )
                    self.dihedralByProjectList.append( dihedralByProject )
                    dihedralHTMLfile = DihedralByProjectHTMLfile(self.project, dihedralByProject)
                    dihedralHTMLfile.generateHtml(htmlOnly) # delay until full list is created.
                    self.insertHtmlLink(main, self.dihedralByProjectList, dihedralByProject, text=dihed)
                else:
                    main(bOGUS_DIHEDRAL_ID)
                main('td',  openTag=False)
                plotCount += 1
            #end for plot

            if plotCount: # close any started rows.
                main('tr',  openTag=False)
            main('table',  openTag=False) # close table
        else:
#            main('h1', openTag=False) # Close the main header even if there are no dihedrals.
            main('h2', "No plots available")

        self.render()

        # Rendering done after complete list is compiled?
#        i = 0
#        for dihed in dihedralList:
#            if dihed != bOGUS_DIHEDRAL_ID and dihedralPresentMap.has_key(dihed):
#                dihedralByProject = self.dihedralByProjectList[i]
#                dihedralHTMLfile = dihedralByProject.html
#                i += 1
#                dihedralHTMLfile.generateHtml(htmlOnly)
    #end def

#end class

class MoleculeHTMLfile( HTMLfile ):
    """
    Class to generate HTML files for Molecule instance
    """

    def __init__(self, project, molecule ):
        # Create the HTML directory for this molecule
        fileName = project.htmlPath( htmlDirectories.molecule, 'index.html')
        HTMLfile.__init__(self, fileName, project, title='Molecule ' + molecule.name)
        self.molecule = molecule        
        molecule.htmlLocation = ( fileName, HTMLfile.top )

        if molecule.has_key('html'):
            del(molecule['html'])
        molecule.html = self
    #end def

    def _generateHeader(self):
        """generate header html for this Molecule"""
        self.header('h1', 'Molecule '+self.molecule.cName(-1) )
        _navigateHtml( self.molecule )
    #end def

    def _generateProcheckHtml(self, htmlOnly = False):
        """Generate html code for Procheck output"""
        main = self.main
        project = self.project
        molecule = self.molecule

        nTmessage("Creating Procheck html")
        main('h1','Procheck_NMR')
        anyProcheckPlotsGenerated = False
        pcPlotList = [
             ('_01_ramachand','Ramachandran (all)'),
             ('_02_allramach','Ramachandran (type)'),
             ('_03_chi1_chi2','chi1-chi2'),
             ('_04_ch1distrb','chi1'),
             ('_05_ch2distrb','chi2'),
             ('_06_ensramach','Ramachandran (sequence)'),
             ('_07_ensch1ch2','Ensemble chi1-chi2'),
             ('_08_residprop','Residue properties'),
             ('_09_equivresl','Equivalent resolution'),
             ('_10_modelsecs','By-model sec. structures'),
             ('_11_rstraints','Distance restraints'),
             ('_12_restdiffs','Restraint differences'),
             ('_13_restrnsum','Numbers of restraints'),
             ('_14_resdifsum','Difference summary'),
             ('_15_resvifreq','Violation frequency'),
             ('_16_restatist','Restraint statistics'),
             ('_17_restrviol','By-residue violations'),
             ('_18_modelcomp','By-model violations')
            ]
        ncols = 6
        main('table',  closeTag=False)
        plotCount = 0
        for p,d in NTprogressIndicator(pcPlotList):
            procheckLink = os.path.join('../..',
                        project.moleculeDirectories.procheck, molecule.name + p + ".ps")
            procheckLinkReal = os.path.join( project.rootPath( project.name )[0], molecule.name,
                        project.moleculeDirectories.procheck, molecule.name + p + ".ps")
#            nTdebug('procheck real path: ' + procheckLinkReal)
            if not os.path.exists( procheckLinkReal ):
                continue # Skip their inclusion.

            if not htmlOnly and not convert2Web( procheckLinkReal, doMontage=True ):
                nTerror( "Failed to convert2Web input file: " + procheckLinkReal)
                continue

#            _pinupPath, _fullPath, _printPath = fileList
            pinupLink = os.path.join('../..',
                        project.moleculeDirectories.procheck, molecule.name + p + "_pin.gif" )
            fullLink = os.path.join('../..',
                        project.moleculeDirectories.procheck, molecule.name + p + ".png" )
            printLink = os.path.join('../..',
                        project.moleculeDirectories.procheck, molecule.name + p + ".pdf" )
            anyProcheckPlotsGenerated = True
            # plotCount is numbered starting at zero.
            if plotCount % ncols == 0:
                if plotCount: # Only close rows that were started
                    main('tr',  openTag=False)
                main('tr',  closeTag=False)
            main('td',  closeTag=False)
            main('a',   "",         href = fullLink, closeTag=False )
            main('img', "",         src=pinupLink ) # enclosed by _A_ tag.
            main('a',   "",         openTag=False )
            main('br')
            main('a',   d,          href = procheckLink )
            main('br')
            main('a',   "pdf",      href = printLink )
            main('td',  openTag=False)
            plotCount += 1
        #end for

        if plotCount: # close any started rows.
            main('tr',  openTag=False)
        main('table',  openTag=False) # close table
        if not anyProcheckPlotsGenerated:
            main('h2', "No procheck plots found at all")
    #end def


    def _generateCingHtml(self, htmlOnly=False):
        """Generate the html code for the CING based plots.
        """
        main = self.main
        project = self.project
        molecule = self.molecule

        if not htmlOnly:
            nTmessage("Creating CING html")
            if createHtmlCing(project):
                nTerror('Failed to createHtmlCing')
                return True
            #end if
        #end if

        anyCINGPlotsGenerated = False
        main('h1','CING')
        ncols = 6
        main('table',  closeTag=False)
        plotCount = 0 # The number of actual plots shown in the table
        for p,d in NTprogressIndicator(cingPlotList):
            cingLink = os.path.join('../..',
                        project.moleculeDirectories.analysis, molecule.name + p + ".pdf")
            cingLinkReal = os.path.join( project.rootPath( project.name )[0], molecule.name,
                        project.moleculeDirectories.analysis, molecule.name + p + ".pdf")

#            nTdebug('cingLinkReal: ' + cingLinkReal)
            if not os.path.exists( cingLinkReal ):
#                nTwarning('Failed to find expected cingLinkReal: ' + cingLinkReal) # normal when whatif wasn't run.
                continue # Skip their inclusion.

            pinupLink = os.path.join('../..',
                        project.moleculeDirectories.analysis, molecule.name + p + "_pin.gif" )
            fullLink = os.path.join('../..',
                        project.moleculeDirectories.analysis, molecule.name + p + ".png" )
            anyCINGPlotsGenerated = True
            if plotCount % ncols == 0:
                if plotCount:
                    main('tr',  openTag=False)
                main('tr',  closeTag=False)
            main('td',  closeTag=False)
            main('a',   "",         href = fullLink, closeTag=False )
            main(    'img', "",     src=pinupLink ) # enclosed by _A_ tag.
            main('a',   "",         openTag=False )
            main('br')
            main('a',   d,          href = cingLink )
            main('td',  openTag=False)
            plotCount += 1
        #end for plot

        if plotCount: # close any started rows.
            main('tr',  openTag=False)
        main('table',  openTag=False) # close table
        if not anyCINGPlotsGenerated:
            main('h2', "No CING plots found at all")
        #end for doWhatif check.
    #end def

    def _generateWhatifHtml(self, htmlOnly=False):
        """Generate the Whatif html code
        """
        main = self.main
        project = self.project
        molecule = self.molecule

        if not htmlOnly:
            nTmessage("Creating Whatif html")
            if hasattr(plugins, WHATIF_STR) and plugins[ WHATIF_STR ].isInstalled:
                if project.createHtmlWhatif():
                    nTerror('Failed to createHtmlWhatif')
                    return True
                #end if
            #end if
        #end if

        anyWIPlotsGenerated = False

        main('h1','What If')
        ncols = 6
        main('table',  closeTag=False)
        plotCount = 0 # The number of actual plots shown in the table
        for p,d in NTprogressIndicator(wiPlotList):
            wiLink = os.path.join('../..',
                        project.moleculeDirectories.whatif, molecule.name + p + ".pdf")
            wiLinkReal = os.path.join( project.rootPath( project.name )[0], molecule.name,
                        project.moleculeDirectories.whatif, molecule.name + p + ".pdf")
#            nTdebug('wiLinkReal: ' + wiLinkReal)
            if not os.path.exists( wiLinkReal ):
#                nTwarning('Failed to find expected wiLinkReal: ' + wiLinkReal) # normal when whatif wasn't run.
                continue # Skip their inclusion.

            pinupLink = os.path.join('../..',
                        project.moleculeDirectories.whatif, molecule.name + p + "_pin.gif" )
            fullLink = os.path.join('../..',
                        project.moleculeDirectories.whatif, molecule.name + p + ".png" )
            anyWIPlotsGenerated = True
            if plotCount % ncols == 0:
                if plotCount:
                    main('tr',  openTag=False)
                main('tr',  closeTag=False)
            main('td',  closeTag=False)
            main('a',   "",         href = fullLink, closeTag=False )
            main(    'img', "",     src=pinupLink ) # enclosed by _A_ tag.
            main('a',   "",         openTag=False )
            main('br')
            main('a',   d,          href = wiLink )
            main('td',  openTag=False)
            plotCount += 1
        #end for plot

        if plotCount: # close any started rows.
            main('tr',  openTag=False)
        main('table',  openTag=False) # close table
        if not anyWIPlotsGenerated:
            main('h2', "No What If plots found at all")
        #end for doWhatif check.
    #end def

    def _generateWattosHtml(self, htmlOnly=False):
        """Generate the Wattos html code
        """
        main = self.main
        project = self.project
        molecule = self.molecule

        nTmessage("Creating Wattos html")
        if not htmlOnly:
            if hasattr(plugins, WATTOS_STR) and plugins[ WATTOS_STR ].isInstalled:
                if project.createHtmlWattos():
                    nTerror('Failed to createHtmlWattos')
                    return True
                #end if
            #end if
        #end if

        anyWattosPlotsGenerated = False

        main('h1','Wattos')
        ncols = 6
        main('table',  closeTag=False)
        plotCount = -1
        for p,d in NTprogressIndicator(wattosPlotList):
            plotCount += 1
            wattosLink = os.path.join('../..',
                        project.moleculeDirectories.wattos, molecule.name + p + ".pdf")
            wattosLinkReal = os.path.join( project.rootPath( project.name )[0], molecule.name,
                        project.moleculeDirectories.wattos, molecule.name + p + ".pdf")
#            nTdebug('wiLinkReal: ' + wiLinkReal)
            if not os.path.exists( wattosLinkReal ):
#                nTwarning('Failed to find expected wiLinkReal: ' + wiLinkReal) # normal when whatif wasn't run.
                continue # Skip their inclusion.

            pinupLink = os.path.join('../..',
                        project.moleculeDirectories.wattos, molecule.name + p + "_pin.gif" )
            fullLink = os.path.join('../..',
                        project.moleculeDirectories.wattos, molecule.name + p + ".png" )
            anyWattosPlotsGenerated = True
            if plotCount % ncols == 0:
                if plotCount:
                    main('tr',  openTag=False)
                main('tr',  closeTag=False)
            main('td',  closeTag=False)
            main('a',   "",         href = fullLink, closeTag=False )
            main(    'img', "",     src=pinupLink ) # enclosed by _A_ tag.
            main('a',   "",         openTag=False )
            main('br')
            main('a',   d,          href = wattosLink )
            main('td',  openTag=False)
        #end for plot

        if plotCount: # close any started rows.
            main('tr',  openTag=False)
        main('table',  openTag=False) # close table
        if not anyWattosPlotsGenerated:
            main('h2', "No Wattos plots found at all")
        #end for doWhatif check.
    #end def

    def _generateX3dnaHtml(self, htmlOnly=False):
        """Generate the X3dna html code
        """
        main = self.main
        project = self.project
        molecule = self.molecule

        nTmessage("Creating X3dna html")
        if not htmlOnly:
            if hasattr(plugins, X3DNA_STR) and plugins[ X3DNA_STR ].isInstalled:
                if project.createHtmlX3dna():
                    nTerror('Failed to createHtmlX3dna')
                    return True
                #end if
            #end if
        #end if

        anyPlotsGenerated = False

        main('h1','X3DNA') # TODO: check capitalization
        ncols = 6
        main('table',  closeTag=False)
        plotCount = -1
        for p,d in NTprogressIndicator(wattosPlotList):
            plotCount += 1
            link = os.path.join('../..',
                        project.moleculeDirectories[X3DNA_STR], molecule.name + p + ".pdf")
            linkReal = os.path.join( project.rootPath( project.name )[0], molecule.name,
                        project.moleculeDirectories[X3DNA_STR], molecule.name + p + ".pdf")
            if not os.path.exists( linkReal ):
                continue # Skip their inclusion.

            pinupLink = os.path.join('../..',
                        project.moleculeDirectories[X3DNA_STR], molecule.name + p + "_pin.gif" )
            fullLink = os.path.join('../..',
                        project.moleculeDirectories[X3DNA_STR], molecule.name + p + ".png" )
            anyPlotsGenerated = True
            if plotCount % ncols == 0:
                if plotCount:
                    main('tr',  openTag=False)
                main('tr',  closeTag=False)
            main('td',  closeTag=False)
            main('a',   "",         href = fullLink, closeTag=False )
            main(    'img', "",     src=pinupLink ) # enclosed by _A_ tag.
            main('a',   "",         openTag=False )
            main('br')
            main('a',   d,          href = link )
            main('td',  openTag=False)
        #end for plot

        if plotCount: # close any started rows.
            main('tr',  openTag=False)
        main('table',  openTag=False) # close table
        if not anyPlotsGenerated:
            main('h2', "No X3DNA plots found at all")
        #end
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate the HTML code and/or Figs depending htmlOnly
        """
        # Reset CING content
        self._resetCingContent()
        self._generateHeader()

        self.main('h1','Residue-based analysis')
        for chain in self.molecule.allChains():
            #print '>>',self.molecule, chain
            self.insertHtmlLinkInTag( 'h1', self.main, self.molecule, chain,
                                       text='Chain %s' % chain.name
                                     )
            _makeDihedralByProjectTableHtml( self.molecule, chain.allResidues(), None )
        #end for

        if hasattr(self.molecule, 'ensemble'):
            self.main('h1', 'Model-based analysis')
            self.insertHtmlLink(self.main, self.molecule, self.molecule.ensemble, text='Models page')

        self.main('h1', 'Structure-based analysis')
        #Use a dummy object for referencing the salt-bridges text-file for now
        _dummy = NTdict()
        _dummy.htmlLocation = (self.project.moleculePath('analysis')+'/saltbridges.txt', HTMLfile.top )
        self.insertHtmlLink(self.main, self.molecule, _dummy, text='Salt bridges')

        if True: # default is True; disable for speedy debugging
            self._generateCingHtml(htmlOnly=htmlOnly)
            self._generateWhatifHtml(htmlOnly=htmlOnly)
            self._generateProcheckHtml(htmlOnly=htmlOnly)
            self._generateWattosHtml(htmlOnly=htmlOnly)

        #footer code is inserted upon rendering
        # render
        self.render()
    #end def
#end class

class ChainHTMLfile( HTMLfile ):
    """
    Class to generate HTML files for chain instance
    """

    def __init__(self, project, chain ):
        # Create the HTML directory for this residue
        fileName = project.htmlPath(htmlDirectories.molecule, chain.name, 'index.html')
        HTMLfile.__init__(self, fileName, project, title=chain.name)
        self.chain = chain        
        chain.htmlLocation = ( fileName, HTMLfile.top )

        if chain.has_key('html'):
            del(chain['html'])
        chain.html = self
    #end def

    def _generateHeader(self):
        # generate header html for this residue
        self.header('h1', self.chain.cName(-1) )
        _navigateHtml( self.chain )
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate the HTML code and/or Figs depending htmlOnly
        """
        # Reset CING content
        self._resetCingContent()
        self._generateHeader()

        _makeDihedralByProjectTableHtml( self.chain, self.chain.allResidues(), 'Residues' )

        #footer code is inserted upon rendering
        # render
        self.render()
    #end def
#end class

class ResidueHTMLfile( HTMLfile ):
    """
    Class to generate HTML files for residue instance
    """

    def __init__(self, project, residue ):
        # Create the HTML directory for this residue
        fileName = project.htmlPath(htmlDirectories.molecule, residue.chain.name, residue.name, 'index.html')
        HTMLfile.__init__(self, fileName, project, title=residue.name)
        self.residue = residue

        residue.htmlLocation = ( fileName, HTMLfile.top )

        if residue.has_key('html'):
            del(residue['html'])
        residue.html = self
        self.tableKwds = {"cellpadding":"0", "cellspacing":"0", "border":"0"}

    def _generateHeader(self, plottedList):
        # generate header html for this residue
        self.header('h1', self.residue.cName(-1) )
        _navigateHtml( self.residue )

        self.header('a', 'Help', href = self.relativePath()+HTMLfile.help_html, title='goto page with help')

        #TODO: Remove styling from below, should be in css
        self.header( 'br' )
        self.header( 'br' )
        for plot in plottedList:
            kw = {'href':'#'+plot}
            #style="font-size: 0.91em",  removed
            self.header('a', plot, title=sprintf('goto %s plot on this page',plot), **kw)
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate the HTML code and/or Figs depending htmlOnly
        """
        residue = self.residue
        project = self.project
#        resNum  = residue.resNum
        resdir, _tmp, _tmp = nTpath( self.fileName )

        # Reset CING content
        self._resetCingContent()
        # 0: angle 1 name
        # 1: angle 2 name
        # 2: Angle combination name
        # 3: Tuple of arbitrary number of keys to value to show
        # 4: Name of value to show (eg QUACHK)
        plotDihedral2dList = [
                    [PHI_STR,  PSI_STR,  'Ramachandran', [
                        (WHATIF_STR, RAMCHK_STR, VALUE_LIST_STR),
                        (CHK_STR, RAMACHANDRAN_CHK_STR, VALUE_LIST_STR)
                         ]],
                    [CHI1_STR, CHI2_STR, 'Janin',        [
                        (WHATIF_STR, C12CHK_STR, VALUE_LIST_STR),
                        (CHK_STR, CHI1CHI2_CHK_STR, VALUE_LIST_STR)
                        ]],
                    [DIHEDRAL_NAME_Cb4N, DIHEDRAL_NAME_Cb4C, 'D1D2', [
                        (CHK_STR, D1D2_CHK_STR, VALUE_LIST_STR)
                        ]]
                   ]

        graphicsFormatExtension = 'png'
        plottedList = []
#        nTdebug("in generateHtml htmlOnly: %s",htmlOnly)
#        if not htmlOnly:
#            nTdebug("Residue %s: generating dihedral plots", self.residue )

        if not getDeepByKeysOrAttributes(plugins, MATPLIB_STR, IS_INSTALLED_STR):
#            nTdebug('Skipping actual plots in html#generateHtml() because no matplib installed.')
            pass
        else:
            from cing.PluginCode.matplib import NTplotSet #@UnresolvedImport
            from cing.PluginCode.matplib import makeDihedralHistogramPlot #@UnresolvedImport

            for plotDihedralName1,plotDihedralName2,plotDihedralComboName,_keyLoL in plotDihedral2dList:
    #                nTdebug("Residue %s: generating %s plot", self.residue, plotDihedralComboName)
                ps = makeDihedralPlot( project, [residue], plotDihedralName1, plotDihedralName2, htmlOnly=htmlOnly)
                if ps: # Can be None for error, True for success (will create on next pass if not htmlOnly)
                    plottedList.append(plotDihedralComboName)
                    if isinstance(ps, NTplotSet): # actually created.
                        tmpPath = os.path.join(resdir, plotDihedralComboName + '.' + graphicsFormatExtension)
                        ps.hardcopy( fileName = tmpPath )
            #end for

            # Dihedral plots
            for dihed in residue.db.dihedrals.zap('name'):
                if dihed in residue and residue[dihed]:
                    d = residue[dihed] # List of values with outliers etc attached.
    #                    nTdebug("Residue %s: generating dihedral %s plot", self.residue, dihed )
                    ps = makeDihedralHistogramPlot( project, residue, dihed, htmlOnly=htmlOnly )
                    tmpPath = os.path.join(resdir,dihed + '.' + graphicsFormatExtension)
                    if ps:
                        plottedList.append(dihed)
                        if isinstance(ps, NTplotSet): # actually created.
                            ps.hardcopy( fileName = tmpPath )
                    #end if
            #end for
        #end if matplib

        # Generate HTML
        self._generateHeader(plottedList)


        # Left side page

        # summary also to file
        fp = open( os.path.join( resdir, 'summary.txt' ), 'w' )
        fprintf(fp, '----- %5s -----\n', residue)

        # Critique
        if residue.rogScore.isCritiqued():
            residue.html.left( 'h2', 'Critiques', id='Critiques')
            residue.rogScore.createHtmlForComments(residue.html.left)
        #end if


#        residue.html.left( 'h2', 'Dihedrals', id='Plots')
#        for plot in plottedList:
#            kw = {'href':'#'+plot}
#            residue.html.left('a' , plot, **kw)
#        residue.html.left( 'h2', openTag=False)

        # 2D plots
        for plotDihedralName1,plotDihedralName2,plotDihedralComboName,keyLoL in plotDihedral2dList:
            plotFileNameDihedral2D = plotDihedralComboName + '.' + graphicsFormatExtension
            if not plotDihedralComboName in plottedList: # failed on first attempt already. No sense in trying again.
                continue

            tailLink = os.path.join( htmlDirectories.dihedrals, plotDihedralComboName + '.html' )
            # up from Molecule/A/ala181 to tailLink
            relLink = os.path.join('../../..', tailLink)
#            absLink = os.path.join( project.moleculePath(), moleculeDirectories.html, tailLink )
#            print "all: tailLink, relLink, absLink", tailLink, relLink, absLink

            residue.html.left('a',   "",      href = relLink, closeTag=False )
            residue.html.left( 'h2', plotDihedralComboName, id=plotDihedralComboName)
            residue.html.left('a',   "",         openTag=False )

            tmpPath2D = os.path.join(resdir, plotFileNameDihedral2D)
            if os.path.exists(tmpPath2D):
                residue.html.left( 'img', src = plotFileNameDihedral2D )
            else:
                residue.html.left( 'i', 'No plot available')
            for keys in keyLoL:
                # Try to show a What If average Z-score like: 'whatif.QUACHK.valueList 0.054 (+/- 0.012'
                strToShow = '.'.join( keys )
                av = getDeepByKeys(residue,*keys)
                if av == None:
                    continue
                sd = None
                if isinstance(av, NTlist):
                    ( av, sd, _n ) = av.average()
                pointNTvalueStr = "%s"  % NTvalue(value=av, error=sd, fmt='%.2f (+- %.2f)', fmt2='%.2f' )
                strToShow += ': %s' % pointNTvalueStr
                residue.html.left( 'p', strToShow ) # The a tag is not filled yet. Might link to NTmoleculePlot?
                #end if
            #end for
        #end for

        # Dihedrals
        for dihed in residue.db.dihedrals.zap('name'):
            if dihed in residue and residue[dihed]:
                if not dihed in plottedList: # failed on first attempt already. No sense in trying again.
                    continue
    #                            nTdebug( '------>>>>> ' + dihed + repr(res) + repr(res[dihed]) )
                d = residue[dihed] # List of values with outliers etc attached.

                # summarize the results
                lenOutliers = '.' # JFD adds: Indicating None
                outlierList = '.'
                if d.__dict__.has_key('outliers'):
    #                            nTwarning("Found no outliers; code wasn't prepared to deal with that or is JFD wrong?")
                    lenOutliers = str(len(d.outliers))
                    outlierList = d.outliers.zap(0)
    #                            -180.1 is longest: 6.1f
                summary = '%-6s: average: %6.1f   cv: %6.3f  ||  outliers: %3s (models %s)' % (
                           dihed, d.cav, d.cv, lenOutliers, outlierList )
                fprintf( fp, '%s\n', summary )
                #generate HTML code for plot and text
                residue.html.left( 'h2', dihed, id=dihed)
                plotFileNameDihedral1D = dihed + '.' + graphicsFormatExtension
                tmpPath1D = os.path.join(resdir, plotFileNameDihedral1D)
                if os.path.exists(tmpPath1D):
                    residue.html.left( 'img', src = plotFileNameDihedral1D, alt=""  )
                else:
                    residue.html.left( 'i', 'No plot available')

                residue.html.left( 'p', summary )
            #end if
        #end for

        # Right side
        # Distance Restraints
        self._generateRestraintsHtml( type = 'Distance' )
        # Dihedral Restraints
        self._generateRestraintsHtml( type = 'Dihedral')

        #footer code is inserted upon rendering
        # render
        self.render()
    #end def

    def _generateDistanceRestraintCode(self, drl, k):


        columnFormats = [
                            ('#',           {'title':'Restraint number. Only ambiguous restraints show a dot.'} ),

                            ('atom 1',      {'title':'First atom with links to chain, residue and atom entities.'} ),
                            ('atom 2',      {'title':'Second atom with links to chain, residue and atom entities.'} ),

                            ('low',         {'title':'Lower bound'}),
                            ('upp' ,        {'title':'Upper bound'}),
                            ('act' ,        {'title':'Actual value average and standard deviation over ensemble'}),

                            ('viol'   ,     {'title':'Violation averagee and standard deviation over ensemble,'}),
                            ('max' ,        {'title':'Maximum violation in ensemble'}),

                            ('c3'    ,      {'title':'Column for initially sorting. Count of violations above threshold of 0.3 Ang.'}),
                            ('Critique'  ,  {'title':'Any number of remarks to consider.'})
                        ]
        t = MakeHtmlTable( self.right, columnFormats=columnFormats, classId="display", id="dataTables-resDRList" , **self.tableKwds )

        for dr in t.rows(drl):
            t.nextColumn()

            isAmbi = len(dr.atomPairs) > 1
            drId = "%s" % dr.id
            if isAmbi:
                drId = "%s.00" % dr.id
            self.insertHtmlLink(self.right, self.residue, dr, text=drId, title=sprintf('goto distance restraint %d', dr.id))

            if len(dr.atomPairs):
                pair = dr.atomPairs[0]
                for atom in pair:
                    residue = atom.residue
                    chain   = atom.residue.chain
                    t.nextColumn()
                    # not including the . anymore since there will already be a ' ' space that can't be removed.
                    chName = NaNstring
                    titleStr = NO_CHAIN_TO_GO_TO
                    if chain:
                        chName = chain.name
                        titleStr = sprintf('goto chain %s', chain.cName(-1))
                    self.insertHtmlLink( self.right, self.residue, chain,   text = chName,   title = titleStr )
                    if residue == self.residue:
                        self.right( 'i', residue.name )
                    else:
                        self.insertHtmlLink( self.right, self.residue, residue, text = residue.name, 
                                             title = sprintf('goto residue %s', residue.cName(-1)) )
                    self.insertHtmlLink( self.right, self.residue, atom,    text = atom.name,    title = 
                                         sprintf('goto atom %s', atom.cName(-1)) )
                # end for
                if isAmbi:
                    t(None,'etc.')
            #end for

            t.nextColumn(val2Str(dr.lower,'%.1f'))
            t.nextColumn(val2Str(dr.upper,'%.1f'))
            t.nextColumn(sprintf('%s+-%s', val2Str(dr.av,'%.1f'), val2Str(dr.sd,'%.1f')) )

            t.nextColumn(sprintf('%s+-%s', val2Str(dr.violAv,'%.1f'), val2Str(dr.violSd,'%.1f')) )
            t.nextColumn(val2Str(dr.violMax,'%.1f'))
            t.nextColumn(val2Str(dr.violCount3,'%d'))

            t.nextColumn()
            dr.rogScore.createHtmlForComments(self.right)
        #end for

#        if i >= toShow:
#        t('tbody', openTag=False)
    #end def

    def _generateDihedralRestraintCode(self, drl, k):

        columnFormats = [

                            ('#',           {'title':'Restraint number.'} ),

                            ('name',        {'title':'Name of this specific dihedral'} ),

                            ('low',         {'title':'Lower bound'}),
                            ('upp' ,        {'title':'Upper bound'}),
                            ('act' ,        {'title':'Actual value averaged over ensemble'}),
                            ('cv' ,         {'title':'Actual value circular variance over ensemble'}),

                            ('vAv'   ,     {'title':'Violation averagee  over ensemble,'}),
                            ('vSd'   ,     {'title':'Violation standard deviation over ensemble,'}),
                            ('max' ,        {'title':'Maximum violation in ensemble'}),

                            ('c3'    ,      {'title':'Column for initially sorting. Count of violations above threshold of 3 degrees.'}),
                            ('Critique'  ,  {'title':'Any number of remarks to consider.'})
                    ]
        t = MakeHtmlTable( self.right, columnFormats=columnFormats, classId="display", id="dataTables-resACList" , **self.tableKwds )

        for dr in t.rows(drl):
            t.nextColumn()
            self.insertHtmlLink(self.right, self.residue, dr, text=val2Str(dr.id,'%d'), title=sprintf('goto dihedral restraint %d', dr.id))
            dihedralName = dr.getDihedralName()
            if not dihedralName: # For entry 1kos, issue 198
                dihedralName = "Unknown dihedral name"
            t.nextColumn(dihedralName)

            t.nextColumn(val2Str(dr.lower,'%.1f'))
            t.nextColumn(val2Str(dr.upper,'%.1f'))
            t.nextColumn(val2Str(dr.cav,'%.1f'))
            t.nextColumn(val2Str(dr.cv,'%.4f'))

            t.nextColumn(val2Str(dr.violAv,'%.1f'))
            t.nextColumn(val2Str(dr.violSd,'%.1f'))
            t.nextColumn(val2Str(dr.violMax,'%.1f'))
            t.nextColumn(val2Str(dr.violCount3,'%d'))

            t.nextColumn()
            dr.rogScore.createHtmlForComments(self.right)
        #end for
    #end def

    def _generateRestraintsHtml( self, type = None ):
        '''Description: internal routine to generate the Html content for restraints
                   linked to a particular residue.
           Inputs: Cing.Residue, string type of restraint: 'Distance', 'Dihedral',
                   'RDC' (?).
           Output:
        '''
        # Just provide the:
#            form name,  (DR_LEVEL)
#            checkbox name, and (DR_LEVEL)
#            id of the tag to work on (DR_LEVEL).

        residue = self.residue
        project = self.project

        if type == 'Distance':
            restraintList = residue.distanceRestraints
        elif type == 'Dihedral':
            restraintList = residue.dihedralRestraints
        else:
            return
        #end if

        if len(restraintList) == 0: 
            return

        resRight = residue.html.right
        resRight('h2','%s Restraints' % type)


        tmpDict = NTdict()
        for restraint in restraintList:
            rLname = os.path.basename(restraint.htmlLocation[0]).split('.')[0]
            if tmpDict.has_key(rLname):
                tmpDict[rLname].append(restraint)
            else:
                tmpDict[rLname] = NTlist(restraint)
            #end if
        #end for
        rLists = tmpDict.keys()
        # display Restraint list
        for k in rLists:
            rLobj = project[k]
            resRight('h3', closeTag=False)
            residue.html.insertHtmlLink(resRight, residue, rLobj, text=k)

            resRL = tmpDict[k]
#            n = len(resRL)
#            if n > toShow:
#                nameStr = "'%s'" % k
#                onclickStr = "javascript:showHideByCheckBox('%s', this)" % k
#                resRight("input", "show all", type="checkbox", name=nameStr, onclick=onclickStr)

            resRight('h3', openTag=False)
            resRight('p', closeTag=False)
            #resRight('br')
            # sort list by 'violCount3' reverse order (higher to lower values)
            resRL = sortListByRogAndKey(resRL, 'violCount3' )

            # display restraint by number, in line, sorted by violCount3 reverse
            #for dr in resRL:
            #    residue.html.insertHtmlLink(resRight, residue, dr, text=str(dr.id))
            #end for
            # display restraint by line

            if type == 'Distance':
                self._generateDistanceRestraintCode(resRL,k)
            elif type == 'Dihedral':
                self._generateDihedralRestraintCode(resRL,k)
            resRight('p', openTag=False)
        #end for
    #end def
#end class

#class DihedralByProject(NTtree):
#    """Collection of plots per dihedral type.
#    """
#    def __init__(self, name):
#        NTtree.__init__(self, __CLASS__ = DIHEDRAL_BY_PROJECT_LEVEL)
#        self.name = name
    #end def
# end class

class DihedralByProjectList( NTlist ):
    """
    Class based on NTlist that holds all dihedrals with a certain name for all occurences in the project.
    Compare with
    """
    def __init__( self, molecule ):
        NTlist.__init__( self )
        self.name       = molecule.name + '.dihedralByProjectList'
        self.molecule = molecule
#        self.status     = status      # Status of the list; 'keep' indicates storage required
        self.currentId  = 0           # Id for each element of list
    #end def

    def append( self, obj ): # pylint: disable=W0221
        obj.id = self.currentId
        NTlist.append( self, obj )
        self.currentId += 1

    def __str__( self ):
        return sprintf( '<DihedralByProjectList "%s" (%d)>',self.name, len(self) )
    #end def

    def format( self ):  # pylint: disable=W0221
        return str(self)
    #end def
#end class

class AtomsHTMLfile( HTMLfile ):
    """Generate an Atoms html file for listing resonances.

    When resonanceListIdx = None as per default. Then the first existing resonance value will be shown.
    This list will be the main target for an atom.

    For a valid resonanceListIdx the specific list's values (but no invalid resonance values) will be shown.
    """

    def __init__(self, project, atomList, resonanceListIdx = None):

        self.project = project
        self.atomList = atomList
        self.resonanceListIdx = resonanceListIdx
        self.relatedAtomsHTMLfileList = NTlist()

        fname = self._getFileName(resonanceListIdx)
        atomListTitlePostFix = self._getAtomListTitlePostFix(resonanceListIdx)
        fileName = self.project.htmlPath( htmlDirectories.molecule, fname)

#        nTdebug("Now initing AtomsHTMLfile %s %s %s", resonanceListIdx, fname, atomListTitlePostFix )
        HTMLfile.__init__( self, fileName, title = 'Atom List ' + atomListTitlePostFix, project=project )

        if resonanceListIdx == None:
            atomList.htmlLocation = ( fileName, HTMLfile.top )
            if hasattr(atomList, 'html'):
                del(atomList.html)
            atomList.html = self
            # set the fileName and tags to locate each atom
            for atom in self.atomList:
                tag = '_o'+str(atom.__OBJECTID__)
                atom.htmlLocation = ( self.fileName, '#' + tag )
            #end for
            for i in range( len(self.project.molecule.resonanceSources)):
                relatedAtomsHTMLfile = AtomsHTMLfile( self.project, self.project.molecule.atomList, i )
                self.relatedAtomsHTMLfileList.append(relatedAtomsHTMLfile)
            #end for
        else:
            pass
        #end if
    #end def

    def _getFileName(self, resonanceListIdx):
        fname = 'atoms.html'
        if resonanceListIdx != None:
            fname = 'atoms_%s.html' % resonanceListIdx
        return fname

    def _getAtomListTitlePostFix(self, resonanceListIdx):
        atomListTitlePostFix = self.atomList.name
        if resonanceListIdx != None:
            resonanceList = self.project.molecule.resonanceSources[resonanceListIdx]
            atomListTitlePostFix = resonanceList.name
        return atomListTitlePostFix

    def _getResonanceCollapsed(self, atom):
        atomResonanceCollapsed = None
        if self.resonanceListIdx == None:
            idx = getIndexRealResList(atom.resonances)
            if idx >= 0:
                atomResonanceCollapsed = atom.resonances[idx]
            # end if
        else:
            atomResonanceCollapsed = atom.resonances[self.resonanceListIdx]
        return atomResonanceCollapsed

    def _hasResonanceValue(self, atom):
        atomResonanceCollapsed = self._getResonanceCollapsed(atom)
        if atomResonanceCollapsed == None:
            return False
        return not isNoneorNaN(atomResonanceCollapsed.value)

    def _atomRow(self, atom, table):
        """Generate one row in table for atom.
        Return True on error.
        """

        sav     = None
        ssd     = None
        delta   = None
        ddelta  = None
        dav     = None
        dsd     = None
        value   = None
        error   = None

#        nTdebug('resonances: %s' % str(atom.resonances))
        atomResonanceCollapsed = self._getResonanceCollapsed(atom)
        if atomResonanceCollapsed != None:
            value   = atomResonanceCollapsed.value
            error   = atomResonanceCollapsed.error

#        nTdebug("Looking at the resonances: %s using last: %s" % (atom.resonances, atomResonanceCollapsed))
        if self.resonanceListIdx != None and isNoneorNaN(value):
            nTcodeerror("Found 'empty' resonance value for specific resonance list %s. This should have been checked before" % 
                        self.resonanceListIdx)
            return

        if atom.has_key('shiftx') and len(atom.shiftx):
            sav = atom.shiftx.av
            ssd = atom.shiftx.sd

        if atom.db.shift:
            dav = atom.db.shift.average
            dsd = atom.db.shift.sd

        if not isNoneorNaN(value):
            if sav:
                delta = value - sav
            if dav:
                ddelta = value - dav


        savStr     = val2Str(sav,   '%6.2f', useNanString=False )
        ssdStr     = val2Str(ssd,   '%6.2f', useNanString=False )
        deltaStr   = val2Str(delta, '%6.2f', useNanString=False )
        ddeltaStr  = val2Str(ddelta,'%6.2f', useNanString=False )
        davStr     = val2Str(dav,   '%6.2f', useNanString=False )
        dsdStr     = val2Str(dsd,   '%6.2f', useNanString=False )
        valueStr   = val2Str(value, '%6.2f', useNanString=False )
        if valueStr==NaNstring:
            error=None
        if error < 0.001: # Error are often missing and we don't want to bother users with the zeros.
            error = None
        errorStr   = val2Str(error, '%6.2f', useNanString=False )

        chain   = atom.residue.chain
        residue = atom.residue


        table.nextColumn()
        # reference label of atom; insert a dummy character
        if self.resonanceListIdx == None:
            self.main( 'i', '', id=atom.htmlLocation[1][1:])

        chName = NaNstring
        titleStr = NO_CHAIN_TO_GO_TO
        if chain:
            chName = chain.name
            titleStr = sprintf('goto chain %s', chain.cName(-1))

        self.insertHtmlLink( self.main, self.atomList, chain,   text =       chName,   title = titleStr)

        table.nextColumn(str(residue.resNum))

        table.nextColumn()
        self.insertHtmlLink( self.main, self.atomList, residue, text = residue.resName, title = 
                             sprintf('goto residue %s', residue.cName(-1)) )

        table.nextColumn(atom.name)
        spinTypeStr = getDeepByKeys(atom, 'db', 'spinType')
        if not spinTypeStr:
            spinTypeStr = ''
        table.nextColumn(spinTypeStr)
#        self.insertHtmlLink( self.main, self.atomList, atom,    text = atom.name)
        if atom.isStereoAssigned():
            table.nextColumn('S')
        else:
            table.nextColumn('')

        table.nextColumn(valueStr)
        table.nextColumn(errorStr)

        for val,err,d in [(savStr,   ssdStr, deltaStr),
                          (davStr,   dsdStr, ddeltaStr)]:
            table.nextColumn(val)
            table.nextColumn(err)
            table.nextColumn(d)
        # end for

        table.nextColumn()
        atom.rogScore.createHtmlForComments(self.main)
    #end def

    def generateHtml(self, htmlOnly=False):
        """Generate html for atoms listing.

        First division contains single table with critiqued;
        second division contains one table per residue with all.

        Checkbox will toggle between showing either first or second division.
        """

        self._resetCingContent()

        atomListTitlePostFix = self._getAtomListTitlePostFix(self.resonanceListIdx)
        self.header('h1', 'Atom List '+ atomListTitlePostFix)
        self.insertMinimalHeader( self.atomList )

            # Add links to specific lists
        if self.resonanceListIdx == None: # MAIN list
#            hasVascoCorrections = False
            openedVascoList = False
            for i in range( len(self.project.molecule.resonanceSources)):
#                relatedAtomsHTMLfile = self.relatedAtomsHTMLfileList[ i ]
                fn = self._getFileName(i)
                atomListTitlePostFix = self._getAtomListTitlePostFix(i)
                self.header('a', 'Atom List ' + atomListTitlePostFix, href = fn, title='Specific Atom List')
                resonanceList = self.project.molecule.resonanceSources[i]
                if resonanceList.hasVascoCorrectionsApplied():
#                    hasVascoCorrections = True
                    if not openedVascoList:
                        self.main('', 'Vasco rereferencing information: ')
#                        self.main('ol', closeTag=False)
                        openedVascoList = True
                    self.main('a', resonanceList.name, href = self._getFileName(i))
                # end if
            # end for
            for i in range( len(self.project.molecule.resonanceSources)):
                relatedAtomsHTMLfile = self.relatedAtomsHTMLfileList[ i ]
                relatedAtomsHTMLfile.generateHtml()
            #end for
        else: # SPECIFIC list
            # Add link to main list
            i = None
            fn = self._getFileName(i)
            atomListTitlePostFix = self._getAtomListTitlePostFix(i)
            self.header('a', 'Atom List ' + atomListTitlePostFix, href = fn, title='Main Atom List')
            # Add specific Vasco info
            resonanceList = self.project.molecule.resonanceSources[self.resonanceListIdx]
            if resonanceList.hasVascoCorrectionsApplied():
                k1 = 'togglable-element-vasco' # key to division unique within page.
                onclickStr = "showHideByCheckBox('%s', this)" % (k1)
                boxStr = "Vasco rereferencing information"
                self.main("h3", '', closeTag = False)
                self.main("input", boxStr, type="checkbox", onclick=onclickStr, **checkBoxClassAttr)
                self.main("h3", openTag = False)
                styleDisplayStr =  'display:none'
                self.main("div", closeTag=False, id=k1, style=styleDisplayStr)
                self.main('', resonanceList.toVascoHtmlList())
                self.main("div", openTag=False)
            # end if
        # end if

#        refItem = os.path.join( self.project.moleculePath('analysis'),'validateAssignments.txt')
#        abstractResource = NTdict()        # mimic an object
#        abstractResource.htmlLocation = ( refItem, HTMLfile.top )
#        if os.path.exists(refItem):
#            self.insertHtmlLink( self.header, self.atomList, abstractResource, text = 'Text file' )

        columnFormats = [   ('ch',   {'title':'Chain identifier of atom'} ),
                            ('resi', {'title':'Residue number of atom'} ),
                            ('resn', {'title':'Residue type (links to specific residue) of atom'} ),
                            ('atom', {'title':'Name of atom'} ),
                            ('iso',  {'title':'NMR isotope.'} ),
                            ('s' , {'title':'S indicates the atom is stereospecifically assigned.'}),

                            ('obs.',    {'title':'Observed chemical shift.'}),
                            ('error' ,  {'title':'Error estimate of observed chemical shift.'}),

                            ('shiftx',  {'title':'Shiftx predicted chemical shift'}),
                            ('error' ,  {'title':'Error estimate in Shiftx prediction.'}),
                            ('delta'  , {'title':'Observed minus predicted chemical shift.'}),

                            ('dbase'  , {'title':'CING database chemical shift.'}),
                            ('error'    ,  {'title':'CING database chemical shift variation.'}),
                            ('delta',   {'title':'Observed minus database chemical shift.'}),

                            ('Critique'  , {'title':'Any number of remarks to consider.'})
                       ]
        tableKwds = {"cellpadding":"0", "cellspacing":"0", "border":"0"}
        # Make table with only critigued atoms if needed
        atomListCritiqued = []
        atomListShown = []
        for atom in self.atomList:
            if not self.showAtom(atom):
                continue
            # end if
            if self.resonanceListIdx != None:
                if not self._hasResonanceValue(atom):
                    continue
                # end if
            # end if
            atomListShown.append(atom)
            if atom.rogScore.isCritiqued():
                atomListCritiqued.append(atom)

        # reenable after testing is done.
        atomCritiquedPresent = len(atomListCritiqued) > 0
        k1 = 'togglable-element-short' # key to division unique within page.
        k2 = 'togglable-element-long'

        if atomCritiquedPresent:
            onclickStr = "toggleShowHideByCheckBox('%s', '%s', this)" % (k1, k2)
            boxStr = "Only critiqued atoms"
            self.main('h3', '', closeTag=False)
            self.main("input", boxStr, type="checkbox", onclick=onclickStr, **checkBoxClassAttr)
            self.main('h3', openTag=False)
            # Make short hidden table.
#            styleDisplayStr =  'display:' # Means item will be shown.
#            if atomCritiquedPresent:
            styleDisplayStr =  'display:none'
            self.main("div", closeTag=False, id=k1, style=styleDisplayStr)
#            self.main("h1", "Critiqued atoms")
            table = MakeHtmlTable( self.main, columnFormats=columnFormats, classId="display", id="dataTables-atomList-short" , **tableKwds )
            for atom in table.rows( atomListCritiqued ):
                self._atomRow( atom, table )
            self.main("div", openTag=False)


        self.main("div", closeTag=False, id=k2)
#        self.main("h1", "All atoms")
        table = MakeHtmlTable( self.main, columnFormats=columnFormats, classId="display", id="dataTables-atomList-long", **tableKwds )
        for atom in table.rows(atomListShown): # TODO select all when done debugging.
            self._atomRow( atom, table )
        self.main("div", openTag=False)
        self.render()
    #end def


    def showAtom(self, atom):
        if atom.isSulfur() or atom.isOxygen() or atom.isMethylProtonButNotPseudo():
#                        nTdebug("Skipping sulfur, oxygen or methylProtonButNotPseudo: %s" % atom)
            return False
        if atom.isIsopropylOrGuanidinium():
#                        nTdebug("Skipping isIsopropylOrGuanidinium: %s" % atom)
            return False
        aName = atom.name
        if aName == 'H1' or aName == 'H2' or aName == 'H3':
#                        nTdebug("Skipping N terminal proton: %s" % atom)
            return False
        return True

#end class


class RestraintListHTMLfile( HTMLfile ):
    """Generate an DihedralRestraintList html file for listing restraints
    """
    def __init__(self, project, restraintList):

        fileName = project.htmlPath( htmlDirectories.restraints, restraintList.name+'.html' )
        restraintList.htmlLocation = ( fileName, HTMLfile.top )
        HTMLfile.__init__( self, fileName, title = 'Restraints List ' + restraintList.name, project=project )

        if hasattr(restraintList, 'html'):
            del(restraintList.html)
        restraintList.html = self

        self.restraintList = restraintList
        self.restraintListSorted = sortListByRogAndKey(self.restraintList, sortKey='violMax')

        # set the fileName and tags to locate each atom
        for restraint in self.restraintList:
            tag = '_o'+str(restraint.__OBJECTID__)
            restraint.htmlLocation = ( self.fileName, '#' + tag )
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate HTML code for this restraint list
        """

        self._resetCingContent()

        # GV. local vars for easy adaptation from Alan's code
        restraintList = self.restraintList
        allRestraintLists = self.project.allRestraintLists()

        # header
        self.header('h1', 'Restraints List: '+ restraintList.name)
        self.insertHtmlLink( self.header, restraintList, self.project, text = 'Home' )
        index = allRestraintLists.index(restraintList)
        if index > 0:
            try:
                previous = allRestraintLists[index-1]
                self.insertHtmlLink( self.header, restraintList, previous, text = previous.name)
            except:
                pass
        self.insertHtmlLink( self.header, restraintList, self.project, text = 'UP' )
        try:
            next = allRestraintLists[index+1]
            self.insertHtmlLink( self.header, restraintList, next, text = next.name )
        except:
            pass

#        self.main('h3',closeTag=False)
#        for l in restraintList.format().split('\n')[:-1]:
#        self.main(None, restraintList.formatHtml())
#        self.main('h3',openTag=False)

        if restraintList.__CLASS__ == 'DistanceRestraintList':
            self._generateDistanceRestraintHtml(htmlOnly=htmlOnly)
        elif restraintList.__CLASS__ == 'DihedralRestraintList':
            self.main(None, restraintList.formatHtml())
            self._generateDihedralRestraintHtml(htmlOnly=htmlOnly)
        elif restraintList.__CLASS__ == 'RDCRestraintList':
            pass
        else:
            nTerror('RestraintListHTMLfile.generateHtml: invalid restraint list class')
        #end if

        self.render()
    #end def


    def _rowDr(self, restraint, idx, table, isSourceForAtom=True):
        """Generate one row in table for restraint.
        Id will be set to first atomPair
        If isSourceForAtom is not set then the row will not be labelled as a the source for only one can be
        and we're inserting 2 of these tables into the HTML DOM tree.
        """

        # A restraint with just one pair can be identified by not adding a sub id for the first pair!
        # Follows the logic of keeping it simple.
        restraintRowStr = "%s" % ( restraint.id)
        if len(restraint.atomPairs) > 1:
            restraintRowStr = "%s.%02d" % ( restraint.id, idx)

        table.nextColumn(restraintRowStr)
        # Would have like to color code it but then the html isn't numerically sortable.
#        restraint.rogScore.createHtmlColorForString(self.main, restraintRowStr)

        atomPair = restraint.atomPairs[idx]
#        nTdebug("Working on restraint.idx: "+restraintRowStr)

        if len(atomPair) == 0:
#            nTdebug("Found a restraint without any content in atomPair")
            for _i in range(4*2):
                table.nextColumn()
        else:
            i = 0
            for atom in atomPair:
#                fill Atom In 4 Columns
                chain   = atom.residue.chain
                residue = atom.residue

                table.nextColumn()
                # reference label of DR; insert a dummy tag
                if i == 0 and idx==0 and isSourceForAtom:
                    self.main( 'i', '', id=restraint.htmlLocation[1][1:])


                chName = NaNstring
                titleStr = NO_CHAIN_TO_GO_TO
                if chain:
                    chName = chain.name
                    titleStr = sprintf('goto chain %s', chain.cName(-1))
                self.insertHtmlLink( self.main, self.restraintList, chain,   text =       chName,   title = titleStr)
                table.nextColumn(str(residue.resNum))
                table.nextColumn()
                self.insertHtmlLink( self.main, self.restraintList, residue, text = residue.resName, title = 
                                     sprintf('goto residue %s', residue.cName(-1)) )
                table.nextColumn()
                self.insertHtmlLink( self.main, self.restraintList, atom,    text = atom.name)
                i += 1
            # end for
        # end if

        table.nextColumn(val2Str(restraint.lower, '%.2f',useNanString=False),)
#        table.nextColumn(val2Str(restraint.target, '%.2f'),)
        table.nextColumn(val2Str(restraint.upper, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.av, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.sd, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.min, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.max, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.violAv, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.violSd, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.violMax, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.violCount1, '%i'),)
        table.nextColumn(val2Str(restraint.violCount3, '%i'),)
        table.nextColumn(val2Str(restraint.violCount5, '%i'),)

#        restrMain('li', 'Restraint:: Lower | Upper: %s | %s' % (
#                            val2Str(restraint.lower, '%.2f'),
#                            val2Str(restraint.upper, '%.2f')))
#        restrMain('li', 'Actual:: Av +- Sd | Min | Max:  %s +- %s | %s | %s'
#                         % (val2Str(restraint.av,  '%.2f'),
#                            val2Str(restraint.sd,  '%.2f'),
#                            val2Str(restraint.min, '%.2f'),
#                            val2Str(restraint.max, '%.2f')))
#
#        restrMain('li', 'Violations:: Av +- Sd | Max: %s +- %s | %s' %
#                (       val2Str(restraint.violAv,  "%.2f"),
#                        val2Str(restraint.violSd,  "%.2f"),
#                        val2Str(restraint.violMax, "%.2f") ))
#
#        restrMain('li', 'Counts:: > 0.1 | 0.3 | 0.5 A: %i | %i | %i' %
#                         (restraint.violCount1,restraint.violCount3,restraint.violCount5)
#                 )

#        if idx==0:
        if restraint.rogScore.isCritiqued():
            table.nextColumn()
            restraint.rogScore.createHtmlForComments(self.main)
        else:
            table.nextColumn('.')
    #end def


    def _rowAc(self, restraint, table, isSourceForAtom=True):
        table.nextColumn(repr(restraint.id))
        # Would have like to color code it but then the html isn't numerically sortable.
#        restraint.rogScore.createHtmlColorForString(self.main, restraintRowStr)

#        nTdebug("Working on restraint.idx: %s" % restraint.id)

        # Set chn, resi, resn for first atom if preesent.
        if len(restraint.atoms) == 0:
#            nTdebug("Found a restraint without any atoms")
            for _i in range(3):
                table.nextColumn('.')
        else:
            atom = restraint.atoms[0]
            if len(restraint.atoms)>1: # Fixes issue 238.
                atom = restraint.atoms[1] # this is taking Alan's trick in classes.py
            chain   = atom.residue.chain
            residue = atom.residue
            table.nextColumn()
            if isSourceForAtom:
                self.main( 'i', '', id=restraint.htmlLocation[1][1:])
            chName = NaNstring
            titleStr = NO_CHAIN_TO_GO_TO
            if chain:
                chName = chain.name
                titleStr = sprintf('goto chain %s', chain.cName(-1))

            self.insertHtmlLink( self.main, self.restraintList, chain,   text =       chName,   title = titleStr)
            table.nextColumn(str(residue.resNum))
            table.nextColumn()
            self.insertHtmlLink( self.main, self.restraintList, residue, text = residue.resName, title = 
                                 sprintf('goto residue %s', residue.cName(-1)) )
        # end if

        nameStr = restraint.getDihedralName()
        if not nameStr:
            nameStr = '.'
        table.nextColumn(nameStr.lower())

        for i in range(4):
            if len(restraint.atoms) <= i: # can be optimized by compiler?
                table.nextColumn('.')
            else:
                atom = restraint.atoms[i]
                table.nextColumn()
                self.insertHtmlLink( self.main, self.restraintList, atom,    text = atom.name,
                    title = sprintf('goto atom %s', atom.cName(-1)) )
            # end if
        # end for

        table.nextColumn(val2Str(restraint.lower, '%.2f'),)
#        table.nextColumn(val2Str(restraint.target, '%.2f'),)
        table.nextColumn(val2Str(restraint.upper, '%.2f'),)
        table.nextColumn(val2Str(restraint.cav, '%.2f'),)
        table.nextColumn(val2Str(restraint.cv, '%.4f'),)
        table.nextColumn(val2Str(restraint.violCount3, '%i'),)
        table.nextColumn(val2Str(restraint.violAv, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.violSd, '%.2f',useNanString=False),)
        table.nextColumn(val2Str(restraint.violMax, '%.2f',useNanString=False),)

        if restraint.rogScore.isCritiqued():
            table.nextColumn()
            restraint.rogScore.createHtmlForComments(self.main)
        else:
            table.nextColumn('.')
    #end def


    def _genDrFilterHighViolCorHtml(self, htmlOnly=False):
        """Generate html for filtered highly violating restraints.

        Return True on error.
        """
        p = self.project
        fileName = p.path(p.molecule.name, p.moleculeDirectories.analysis, DISTANCE_RESTRAINT_LIST_HIGH_VIOLATIONS_FILTERED_STR)
        if not os.path.exists(fileName):
            return
        k1 = 'togglable-element-filter_high_violation' # key to division unique within page.
        onclickStr = "showHideByCheckBox('%s', this)" % (k1)
        boxStr = "Filtered severe violations"
        titleStr = 'Show the few restraints that were filtered out because they were violated severely.'
        self.main("h3", '', title=titleStr, closeTag = False)
        self.main("input", boxStr, type="checkbox", onclick=onclickStr, **checkBoxClassAttr)
        self.main("h3", openTag = False)

        styleDisplayStr =  'display:none'
        self.main("div", closeTag=False, id=k1, style=styleDisplayStr)
        txt = readTextFromFile(fileName)
        if not txt:
            nTerror("Failed to read: " + fileName)
            return True
        self.main("pre", txt)
        self.main("div", openTag=False)
    #end def

    def _generateDrSsaCorrectionsHtml(self, htmlOnly=False):
        """Generate html for stereoAssignmentCorrectionsStar listing from STAR txt.

        Return True on error.
        """
        saveFrameAssign = self.project.getSaveFrameAssign()
        if not saveFrameAssign:
#            nTdebug("No SSA saveframe embedded.")
            return
        tagTableAssignHeader = saveFrameAssign.tagtables[0]
        gS = tagTableAssignHeader.getString
#        gF = tagTableAssignHeader.getFloat
#        gI = tagTableAssignHeader.getInt

        tagNameListSize = len(tagNameListSsaHeader)

#        tagTypeIidxList = [0,1,3,5] # integers
        valueList = [ gS("_Stereo_assign_list."+tagNameListSsaHeader[i]) for i in range(tagNameListSize)]
        columnFormatsHeader = [   ('Property', {'title':'Parameter of stereospecific assignment check'} ),
                                  ('Value',    {'title':'Plain value'} ),
                                  ]
#        tableKwdsHeader = {"cellpadding":"0", "cellspacing":"0", "border":"0", "float":"left", "clear": "both"}
#        tableKwdsHeader = {"cellpadding":"0", "cellspacing":"0", "border":"0" }

        k1 = 'togglable-element-ssa' # key to division unique within page.
        onclickStr = "showHideByCheckBox('%s', this)" % (k1)
        boxStr = "Stereospecific assignment corrections"
        titleStr = 'Show the stereospecific assignment corrections made to the distance restraints if any.'
#        boxStr += " " + time.asctime() # for debugging labelled with timestamp
        self.main("h3", '', title=titleStr, closeTag = False)
        self.main("input", boxStr, type="checkbox", onclick=onclickStr, **checkBoxClassAttr)
        self.main("h3", openTag = False)
#        styleDisplayStr =  'display:' # Means item will be shown.
        styleDisplayStr =  'display:none'
        self.main("div", closeTag=False, id=k1, style=styleDisplayStr)
#        tableHeader = MakeHtmlTable( self.main, showHeader=False, columnFormats=columnFormatsHeader, classId="display", 
#            id="dataTables-DRSsaHeader", **tableKwdsHeader )
        tableHeader = MakeHtmlTable( self.main, showHeader=False, columnFormats=columnFormatsHeader)
        for rowIdx in tableHeader.rows(range(tagNameListSize)): # count the abov
            humanTagName = getHumanTagName(tagNameListSsaHeader[rowIdx])
            cellKwds = {'title': tagNameDescriptionListSsaHeader[rowIdx]}
            tableHeader.nextColumn(humanTagName, **cellKwds )
            tableHeader.nextColumn(str(valueList[rowIdx]))
        # end for

        columnFormats = [   
('#',           {'title':'Triplet number. Only ambiguous restraints show a dot'} ),
('ch',          {'title':'Chain identifier'} ),
('ri',          {'title':'Residue number'} ),
('rn',          {'title':'Residue name'} ),
('at',          {'title':'Name of pseudoatom representing the triplet'} ),
('Num',         {'title':'Ordinal number of assignment (1 is assigned first)'} ),
('Swapped',     {'title':'yes; if assignment state is swapped with respect to restraint file'} ),
('Mdls Fav %',  {'title':'Percentage of models in which the assignment with the lowest overall energy is favored'} ),
('Nrg Dif %',   {'title':'Percentage of difference between lowest and highest overall energy with respect to the highest overall energy'} ),
('Nrg Dif',     {'title':'Difference between lowest and highest overall energy ensemble averaged'} ),
('Nrg +',       {'title':'Energy of the highest overall energy state (Ang.**2) ensemble averaged'} ),
('Nrg -',       {'title':'Energy of the lowest overall energy state (Ang.**2) ensemble averaged'} ),
('Cnstr #',     {'title':'Number of restraints for this triplet. The highest ranking triplet on this number is assigned first (optional)'}),
('Cnstr Amb #', {'title':'Number of restraints for this triplet that are ambiguous besides the ambiguity from this triplet'} ),
('Deass',       {'title':'yes; if restraints included in this triplet are deassigned'} ),
('Viol Max',    {'title':'Maximum unaveraged violation before deassignment (Ang.)'} ),
('Sngl Crit #', {'title':'Number of violations above threshold for a single model before deassignment (given by Single_mdl_crit_count)'} ),
('Mlt Crit #',  {'title':'Number of violations above threshold for a multiple models before deassignment (given by Multi_mdl_crit_count)'}),
                       ]
        tableKwds = {"cellpadding":"0", "cellspacing":"0", "border":"0"}
#        self.main("h3", "Info per atom group %s" % time.asctime())
        tagTableAssign = saveFrameAssign.tagtables[1]

#        self.main("br", '')
        table = MakeHtmlTable( self.main, columnFormats=columnFormats, classId="display", id="dataTables-DRSsaMain", **tableKwds )
        colCount = len(columnFormats)
        rowCount = tagTableAssign.getRowCount()
        colCount2 = tagTableAssign.getColCount()
        if colCount2 != (colCount-1):
            nTerror("Failed to get correct columns %s but found %s from tagtable" % ( colCount, (colCount+1)))
            return True
        for rowIdx in table.rows(range(rowCount)): # count the above
            atom = None
            if 0: # this fails because of issue 294
                chainName       = tagTableAssign.getString(rowIdx=rowIdx, colIdx=0)
                resNum          = tagTableAssign.getInt(   rowIdx=rowIdx, colIdx=1)
                pseudoAtomName  = tagTableAssign.getString(rowIdx=rowIdx, colIdx=3)
                nameTuple = ( IUPAC, chainName, resNum, pseudoAtomName )
                for item in nameTuple:
                    if item == None:
                        nTdebug("Failed to get valid item from nameTuple: " + str(nameTuple))
                        nameTuple = None
                        continue
                    # end if
                # end for
                atom = self.project.molecule.decodeNameTuple( nameTuple ) # may be None input and output.
                if not atom:
                    pass
    #                nTdebug('In %s failed to map nameTuple %s', getCallerName(), str(nameTuple))

            table.nextColumn(str(rowIdx+1))
            startIdxDefaults = 1
#            fill Atom In 4 Columns
            if atom: # TODO: reuse next time this code comes up
                startIdxDefaults = 5
                residue = atom.residue
                chain   = atom.residue.chain
                chName = NaNstring
                titleStr = NO_CHAIN_TO_GO_TO
                if chain:
                    chName = chain.name
                    titleStr = sprintf('goto chain %s', chain.cName(-1))
                table.nextColumn()
                self.insertHtmlLink( self.main, self.restraintList, chain,   text =       chName,   title = titleStr)
                table.nextColumn(str(residue.resNum))
                table.nextColumn()
                self.insertHtmlLink( self.main, self.restraintList, residue, text = residue.resName, title = 
                                     sprintf('goto residue %s', residue.cName(-1)) )
                table.nextColumn()
                self.insertHtmlLink( self.main, self.restraintList, atom,    text = atom.name)
            # end if

            for colIdx in range(startIdxDefaults,colCount):
                v = tagTableAssign.getString(columnName=None, rowIdx=rowIdx, colIdx=colIdx-1)
                table.nextColumn(v)
            # end for
        # end for
        self.main("div", openTag=False)
    #end def


    def  _generateDrMetaHtml(self, htmlOnly=False):

        header = self.restraintList.name
        if hasattr(self.restraintList, 'rogScore'):
            if self.restraintList.rogScore.isCritiqued():
                header = '<font color="%s">%s</font>' % (self.restraintList.rogScore.colorLabel, header)
#        header = '<h3>DistanceRestraintList %s</h3>' % header

        msg = '''
<table>
<TR><TD>intra-residual</TD><TD align="right">%4d</TD></TR>
<TR><TD>sequential    </TD><TD align="right">%4d</TD></TR>
<TR><TD>medium-range  </TD><TD align="right">%4d</TD></TR>
<TR><TD>long-range    </TD><TD align="right">%4d</TD></TR>
<TR><TD>ambiguous     </TD><TD align="right">%4d</TD></TR>
<TR><TD>sum           </TD><TD align="right">%4d</TD></TR>
</table>

<table>
<TR><TD>rmsd</TD>               <TD> %s +- %s                    </TD></TR>
<TR><TD>violations <-0.1 A (lower-bound violations)</TD><TD align="right"> %4d </TD></TR>
<TR><TD>violations > 0.1 A </TD><TD align="right"> %4d                          </TD></TR>
<TR><TD>violations > 0.3 A </TD><TD align="right"> %4d                          </TD></TR>
<TR><TD>violations > 0.5 A </TD><TD align="right"> %4d                          </TD></TR>
</table>
''' % (
            len(self.restraintList.intraResidual),
            len(self.restraintList.sequential),
            len(self.restraintList.mediumRange),
            len(self.restraintList.longRange),
            len(self.restraintList.ambiguous),
            len(self.restraintList),
            val2Str(self.restraintList.rmsdAv, "%7.3f", 7), val2Str(self.restraintList.rmsdSd, "%6.3f", 6),
            self.restraintList.violCountLower,
            self.restraintList.violCount1,
            self.restraintList.violCount3,
            self.restraintList.violCount5
          )
        k1 = 'togglable-element-metadata-dr' # key to division unique within page.
        onclickStr = "showHideByCheckBox('%s', this)" % (k1)
        boxStr = "Summary"
#        boxStr += " " + time.asctime() # for debugging labelled with timestamp
        self.main("h3", '', closeTag = False)
        self.main("input", boxStr, type="checkbox", onclick=onclickStr, **checkBoxClassAttr)
        self.main("h3", openTag = False)
#        styleDisplayStr =  'display:' # Means item will be shown.
        styleDisplayStr =  'display:none'
        self.main("div", closeTag=False, id=k1, style=styleDisplayStr)
        self.main("", msg)
        self.main("div", openTag=False)
    #end def

    def _generateDistanceRestraintHtml(self, htmlOnly=False):
        """Generate html for DR listing.

        First division contains single table with critiqued;
        second division contains one table per residue with all.

        Checkbox will toggle between showing either first or second division.
        """
        if self._generateDrMetaHtml():
            nTerror("Failed _generateDrMetaHtml")

        if self._generateDrSsaCorrectionsHtml(htmlOnly=htmlOnly):
            nTerror("Failed _generateDrSsaCorrectionsHtml")
        if self._genDrFilterHighViolCorHtml(htmlOnly=htmlOnly):
            nTerror("Failed _genDrFilterHighViolCorHtml")
        columnFormats = [   ('#', {'title':'Restraint number. Only ambiguous restraints show a dot'} ),

                            ('ch1', {'title':'Chain identifier of first atom'} ),
                            ('ri1', {'title':'Residue number of first atom'} ),
                            ('rn1', {'title':'Residue type (links to specific residue) of first atom'} ),
                            ('at1', {'title':'First atom name in pair'} ),

                            ('ch2', {'title':'Chain identifier of second atom'} ),
                            ('ri2', {'title':'Residue number of second atom'} ),
                            ('rn2', {'title':'Residue type (links to specific residue) of second atom'} ),
                            ('at2', {'title':'Second atom name in pair'} ),

                            ('low', {'title':'Lower bound'}),
                            ('upp' , {'title':'Upper bound'}),
                            ('av' , {'title':'Actual value averaged over ensemble'}),
                            ('sd', {'title':'Standard deviation of actual value over ensemble'}),

                            ('min' , {'title':'Minimum actual value in ensemble'}),
                            ('max' , {'title':'Maximum actual value in ensemble'}),

                            ('vAv'   , {'title':'Violation averaged over ensemble,'}),
                            ('vSd'   , {'title':'Violation standard deviation.'}),
                            ('vMx'    , {'title':'Violation maximum value in any one model.'}),

#                            ('c1'    , {'title':'Count of violations between 0.1 and 0.3 Ang.'}),
#                            ('c3'    , {'title':'Count of violations between 0.3 and 0.5 Ang.'}),
#                            ('c5'    , {'title':'Count of violations over 0.5 Ang.'}),

                            ('c1'    , {'title':'Count of violations over 0.1 Ang.'}),
                            ('c3'    , {'title':'Count of violations over 0.3 Ang.'}),
                            ('c5'    , {'title':'Count of violations over 0.5 Ang.'}),

                            ('Critique'  , {'title':'Any number of remarks to consider.'})
                       ]
        tableKwds = {"cellpadding":"0", "cellspacing":"0", "border":"0"}
        # Make table with only critigued atoms if needed
        itemListCritiqued = []

        mapRowIdx2RestraintAtomPair = {}
        mapRowIdx2RestApCritiqued = {}
        rowIdx = 0
        rowIdxCritiqued = 0
        for restraint in self.restraintList:
            for idx, _atomPair in enumerate(restraint.atomPairs):
                mapRowIdx2RestraintAtomPair[rowIdx] = ( restraint, idx)
                rowIdx +=1
                if restraint.rogScore.isCritiqued():
                    mapRowIdx2RestApCritiqued[rowIdxCritiqued] = ( restraint, idx)
                    rowIdxCritiqued += 1
            if restraint.rogScore.isCritiqued():
                itemListCritiqued.append(restraint)
#                pairListCritiquedCount += pairCount
        pairListCount = rowIdx # determines row cound
        pairListCritiquedCount = rowIdxCritiqued # determines row cound

        # reenable after testing is done.
        itemCritiquedPresent = len(itemListCritiqued) > 0
#        itemCritiquedPresent =  False

        k1 = 'togglable-element-short' # key to division unique within page.
        k2 = 'togglable-element-long'

        onclickStr = "toggleShowHideByCheckBox('%s', '%s', this)" % (k1, k2)
        boxStr = "Only critiqued restraints"
        if itemCritiquedPresent:
#           checked="false"
            self.main("h3", '', closeTag = False)
            self.main("input", boxStr, type="checkbox", onclick=onclickStr, **checkBoxClassAttr)
            self.main("h3", openTag = False)
            # Make short hidden table.
#            styleDisplayStr =  'display:' # Means item will be shown.
#            if atomCritiquedPresent:
            styleDisplayStr =  'display:none'
            self.main("div", closeTag=False, id=k1, style=styleDisplayStr)
#            self.main("h3", "Critiqued restraints")
            table = MakeHtmlTable( self.main, columnFormats=columnFormats, classId="display", id="dataTables-DRList-short" , **tableKwds )


            for rowIdx in table.rows(range(pairListCritiquedCount)):
                restraint, idx = mapRowIdx2RestApCritiqued[rowIdx]
                self._rowDr( restraint, idx, table, isSourceForAtom=False )
            self.main("div", openTag=False)


        self.main("div", closeTag=False, id=k2)
#        self.main("h3", "All restraints")
        table = MakeHtmlTable( self.main, columnFormats=columnFormats, classId="display", id="dataTables-DRList-long", **tableKwds )
        table.rows(range(pairListCount)) # set the rows
#        for restraint in self.restraintList:
#        for item in table.rows( self.restraintList[0:10] ):
#            idx = 0 # index of atomPair within restraint
        for rowIdx in table.rows(range(pairListCount)):
            restraint, idx = mapRowIdx2RestraintAtomPair[rowIdx]
            self._rowDr( restraint, idx, table )
#            idx += 1
        self.main("div", openTag=False)
        self.render()
    #end def


    def _generateDihedralRestraintHtml(self, htmlOnly=False):
        """Generate html for AC listing.
        """

        columnFormats = [
                            ('#', {'title':'Restraint number'} ),

                            ('ch', {'title':'Chain identifier'} ),
                            ('rsi', {'title':'Residue number'} ),
                            ('rsn', {'title':'Residue type (links to specific residue)'} ),
                            ('nam', {'title':'Dihedral angle name'} ),
                            ('at1', {'title':'First atom name in given residue defining dihedral angle'} ),
                            ('at2', {'title':'Second atom name defining dihedral angle (perhaps in other residue)'} ),
                            ('at3', {'title':'Third atom name defining dihedral angle (perhaps in other residue)'} ),
                            ('at4', {'title':'Fourth atom name defining dihedral angle (perhaps in other residue)'} ),

                            ('low', {'title':'Lower bound'}),
                            ('upp' , {'title':'Upper bound'}),
                            ('av' , {'title':'Actual value averaged over ensemble'}),
                            ('cv', {'title':'Circular variance of actual value over ensemble'}),

                            ('c3'    , {'title':'Count of violations above threshold.'}),
                            ('vAv'   , {'title':'Violation averaged over ensemble,'}),
                            ('vSd'   , {'title':'Violation standard deviation.'}),
                            ('vMx'    , {'title':'Violation maximum value in any one model.'}),
                            ('Critique'  , {'title':'Any number of remarks to consider.'})
                       ]
        tableKwds = {"cellpadding":"0", "cellspacing":"0", "border":"0"}
        # Make table with only critigued atoms if needed
        itemListCritiqued = []
        for item in self.restraintList:
            if item.rogScore.isCritiqued():
                itemListCritiqued.append(item)

        # reenable after testing is done.
        itemCritiquedPresent = len(itemListCritiqued) > 0
#        itemCritiquedPresent =  False

        k1 = 'togglable-element-short' # key to division unique within page.
        k2 = 'togglable-element-long'

        onclickStr = "toggleShowHideByCheckBox('%s', '%s', this)" % (k1, k2)
        boxStr = "Only critiqued restraints"
        if itemCritiquedPresent:
#           checked="false"
            self.main("h3", "", closeTag = False)
            self.main("input", boxStr, type="checkbox", onclick=onclickStr, **checkBoxClassAttr)
            self.main("h3", openTag = False)

        if itemCritiquedPresent:
            # Make short hidden table.
#            styleDisplayStr =  'display:' # Means item will be shown.
#            if atomCritiquedPresent:
            styleDisplayStr =  'display:none'
            self.main("div", closeTag=False, id=k1, style=styleDisplayStr)
#            self.main("h1", "Critiqued restraints")
            table = MakeHtmlTable( self.main, columnFormats=columnFormats, classId="display", id="dataTables-ACList-short" , **tableKwds )

            for item in table.rows( itemListCritiqued ):
                self._rowAc( item, table, isSourceForAtom=False )
            self.main("div", openTag=False)


        self.main("div", closeTag=False, id=k2)
#        self.main("h1", "All atoms")
        table = MakeHtmlTable( self.main, columnFormats=columnFormats, classId="display", id="dataTables-ACList-long", **tableKwds )
        for item in table.rows( self.restraintList ):
            self._rowAc( item, table )
        self.main("div", openTag=False)
        self.render()
    #end def


#end class


class PeakListHTMLfile( HTMLfile ):
    """Generate an PeakList html file for listing peaks
    """
    def __init__(self, project, peakList):

        fileName = project.htmlPath( htmlDirectories.peaks, peakList.name+'.html' )
        peakList.htmlLocation = ( fileName, HTMLfile.top )
        HTMLfile.__init__( self, fileName, title = 'Peak List ' + peakList.name, project=project )

        if hasattr(peakList, 'html'):
            del(peakList.html)
        peakList.html = self
        self.peakList = peakList

        # set the fileName and tags to locate each atom
        for peak in self.peakList:
            tag = '_o'+str(peak.__OBJECTID__)
            peak.htmlLocation = ( self.fileName, '#' + tag )
        # Get true max dim for all peaks together.
        _minD, self.dimPeakList = self.peakList.minMaxDimension()
        if not self.dimPeakList:
            self.dimPeakList = 1

    #end def

    def _rowPeak(self, peak, table):
        table.nextColumn(str(peak.peakIndex))
# POSITION
        for i in range(self.dimPeakList):
            if len(peak.positions) <= i: # can be optimized by compiler?
                table.nextColumn('.')
            else:
                pos = peak.positions[i]
                if not pos:
                    pos = '.'
                else:
                    pos = "%.3f" % pos
                table.nextColumn(pos)
            # end if
        # end for
# HEIGHT & VOLUME
        fmt = '%.2e'
        table.nextColumn(val2Str(peak.height.value, fmt,useNanString=False))
        table.nextColumn(val2Str(peak.height.error, fmt,useNanString=False))
        table.nextColumn(val2Str(peak.volume.value, fmt,useNanString=False))
        table.nextColumn(val2Str(peak.volume.error, fmt,useNanString=False))
# ATOM(S)
        for i in range(self.dimPeakList):
            atom = None
            if len(peak.resonances) > i: # can be optimized by compiler?
                resonance = peak.resonances[i]
                if resonance:
                    atom = resonance.atom
            # end if
            if not atom:
                for _j in range(4):
                    table.nextColumn('')
                # end for
                continue
            # end if
            chain   = atom.residue.chain
            residue = atom.residue
            table.nextColumn()
            if i == 0:
                self.main( 'i', '', id=peak.htmlLocation[1][1:])

            chName = NaNstring
            titleStr = NO_CHAIN_TO_GO_TO
            if chain:
                chName = chain.name
                titleStr = sprintf('goto chain %s', chain.cName(-1))

            self.insertHtmlLink( self.main, self.peakList, chain,   text =       chName,   title = titleStr)
            table.nextColumn(str(residue.resNum))
            table.nextColumn()
            self.insertHtmlLink( self.main, self.peakList, residue, text = residue.resName, title = 
                                 sprintf('goto residue %s', residue.cName(-1)) )
            table.nextColumn()
            self.insertHtmlLink( self.main, self.peakList, atom,    text = atom.name
                                 , title = sprintf('goto atom %s', atom.cName(-1)))
        # end for
# CRITIQUE
        if peak.rogScore.isCritiqued():
            table.nextColumn()
            peak.rogScore.createHtmlForComments(self.main)
        else:
            table.nextColumn('.')
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate HTML code for this peak list
        """

        self._resetCingContent()

        #peakList = self.peakList
        self.header('h1', 'Peak List: ' + self.peakList.name)
        self.insertHtmlLink( self.header, self.peakList, self.project, text = 'Home' )

        index = self.project.peaks.index(self.peakList)
        if index > 0:
            try:
                previous = self.project.peaks[index-1]
                self.insertHtmlLink( self.header, self.peakList, previous, text = previous.name)
            except: 
                pass
        self.insertHtmlLink( self.header, self.peakList, self.project, text = 'UP')
        try:
            next = self.project.peaks[index+1]
            self.insertHtmlLink( self.header, self.peakList, next, text = next.name)
        except: 
            pass

        ordinalNameList = [ "first", "second", "third", "fourth", "fifth", "sixth", "seventh" ]
        columnFormats = [   ('#', {'title':'Peak number'}  ) ]
        for i in range(self.dimPeakList):
            iPlusOne = i + 1
            csId = "cs%d" % iPlusOne
            title = 'Chemical shift of %s dimension' % ordinalNameList[i]
            columnFormats.append( (csId, {'title':title}  ) )
        columnFormats.append( ("hght", {'title':'Height of the peak'} ) )
        columnFormats.append( ("hErr", {'title':'Height error of the peak'} ) )
        columnFormats.append( ('volume',  {'title':'Volume of the peak'} ) )
        columnFormats.append( ('vErr', {'title':'Volume error of the peak'} ) )
        for i in range(self.dimPeakList):
            iPlusOne = i + 1
            columnList = "%dc %di %dr %da" % ( iPlusOne,iPlusOne,iPlusOne,iPlusOne )
            titleList = [
                         "Chain identifier of %s dimension resonance" %  ordinalNameList[i],
                         "Residue numberof %s dimension resonance" %  ordinalNameList[i],
                         "Residue type of %s dimension resonance (links to specific residue)" %  ordinalNameList[i],
                         "Atom name of %s dimension resonance" %  ordinalNameList[i]
            ]
            for c,column in enumerate(columnList.split()):
                columnFormats.append( (column, {'title': titleList[c]} ) )
        columnFormats.append( ('Critique', {'title':'Any number of remarks to consider.'}))

        tableKwds = {"cellpadding":"0", "cellspacing":"0", "border":"0"}
        # Make table with only critigued atoms if needed
        itemListCritiqued = []
        for item in self.peakList:
            if item.rogScore.isCritiqued():
                itemListCritiqued.append(item)

        # reenable after testing is done.
        itemCritiquedPresent = len(itemListCritiqued) > 0
#        itemCritiquedPresent =  False

        k1 = 'togglable-element-short' # key to division unique within page.
        k2 = 'togglable-element-long'

        onclickStr = "toggleShowHideByCheckBox('%s', '%s', this)" % (k1, k2)
#        boxStr = "show critiqued or all"
        boxStr = "Only critiqued peaks"

        if itemCritiquedPresent:
#           checked="false"
            self.main("h3", "", closeTag = False)
            self.main("input", boxStr, type="checkbox", onclick=onclickStr, **checkBoxClassAttr)
            self.main("h3", openTag = False)

        if itemCritiquedPresent:
            # Make short hidden table.
#            styleDisplayStr =  'display:' # Means item will be shown.
#            if atomCritiquedPresent:
            styleDisplayStr =  'display:none'
            self.main("div", closeTag=False, id=k1, style=styleDisplayStr)
            self.main("h1", "Critiqued peaks")
            id = "dataTables-%ddPeakList-short" % self.dimPeakList
            table = MakeHtmlTable( self.main, columnFormats=columnFormats, classId="display", id=id , **tableKwds )

            for item in table.rows( itemListCritiqued ):
                self._rowPeak( item, table )
            self.main("div", openTag=False)


        self.main("div", closeTag=False, id=k2)
        self.main("h1", "All peaks")
        id = "dataTables-%ddPeakList-long" % self.dimPeakList
        table = MakeHtmlTable( self.main, columnFormats=columnFormats, classId="display", id=id, **tableKwds )
        for item in table.rows( self.peakList ):
            self._rowPeak( item, table )
        self.main("div", openTag=False)
        self.render()
    #end def
#end class

class EnsembleHTMLfile( HTMLfile ):
    """Generate an ensemble html file
    """
    def __init__(self, project, ensemble ):

        fileName = project.htmlPath( htmlDirectories.models, 'index.html' )
        ensemble.htmlLocation = ( fileName, HTMLfile.top )
        HTMLfile.__init__( self, fileName, title = 'Models page', project=project )

        if hasattr(ensemble, 'html'):
            del(ensemble.html)
        ensemble.html = self
        self.ensemble = ensemble
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate HTML code for this peak list
        """

        self._resetCingContent()

        self.header('h1', 'Models page')
        self.insertHtmlLink( self.header, self.ensemble, self.project, text = 'Home' )

        self.main('h3',closeTag=False)
        for line in self.project.molecule.rmsd.format().split('\n')[:-1]:
            self.main('br', line )
        self.main('h3',openTag=False)

        if not getDeepByKeysOrAttributes(plugins, MATPLIB_STR, IS_INSTALLED_STR):
            nTdebug('Skipping plots in html#makeDihedralPlot() because no matplib installed.')
        else:
            from cing.PluginCode.matplib import NTplot #@UnresolvedImport
            from cing.PluginCode.matplib import NTplotSet #@UnresolvedImport

            plotFile = self.project.htmlPath(htmlDirectories.models,'outliers')
            graphicsOutputFormat = 'png'
            if not htmlOnly:
                ps = NTplotSet() # closes any previous plots
                ps.hardcopySize = (600,369)
                plot = NTplot( xLabel = 'Model', yLabel = 'Outliers',
                               xRange = (0, self.project.molecule.modelCount+1)
                             )
                ps.addPlot(plot)
        #        self.project.models[i] holds the number of outliers for model i.
        #        models is a NTdict containing per model a list of outliers.
                outliers = [self.project.models[i] for i in range(len(self.ensemble))]
    #            nTdebug( '>> Number of outliers per model: ' + repr(outliers))
                plot.barChart( self.project.models.items(), 0.05, 0.95,
                               attributes = boxAttributes( fillColor='green' )
                             )

                plot.autoScaleYByValueList(outliers, startAtZero=True,
                                           useIntegerTickLabels=True )
                ps.hardcopy( plotFile )
            #end if
            self.main('img', src = 'outliers.'+graphicsOutputFormat)
        # end if matplib present
        self.render()
    #end def
#end class


def removePreTagLines(msg):
    """Removes lines that start with a pre tag"""
    resultList = []
    msgList = msg.split('\n')
    for line in msgList:
        if line.startswith(HTML_TAG_PRE) or line.startswith(HTML_TAG_PRE2):
            continue
        resultList.append(line)
    result = '\n'.join(resultList)
    return result

def addPreTagLines(msg):
    """Add pre tag lines."""
    return '\n'.join( [HTML_TAG_PRE, msg, HTML_TAG_PRE2 ])

def sortListByRogAndKey(theList, sortKey=None, descending=True):
    if sortKey!=None:
        NTsort(theList, sortKey, inplace=False)
        if descending:
            theList.reverse()
    # sort by color: 1st red, 2nd orange, then green and by violCount3 reverse order
    listRed, listOrange, listGreen = [], [], []
    for item in theList:
        if item.rogScore.isRed():
            listRed.append(item)
        elif item.rogScore.isOrange():
            listOrange.append(item)
        else:
            listGreen.append(item)
    theList = listRed + listOrange + listGreen
    return theList
# end def

def copyCingHtmlJsAndCssToDirectory(dstDir):
    """
    css and javascript now in HTML dir
    """
    nTdebug("Starting %s" % getCallerName())
    if not os.path.exists(dstDir):
        nTdebug("Creating new HTML dir: dstDir")
        os.mkdir(dstDir)
    # end if
    htmlPath = os.path.join(cingRoot,cingPaths.html) # copy needed css and other files/directories.

    nTdebug("Listing: [%s]" % htmlPath )
    for f in os.listdir( htmlPath ):
        nTdebug("Listing item: [%s]" % f)
        htmlFile = os.path.join(htmlPath,f)
        if os.path.isfile(htmlFile):
            shutil.copy( htmlFile, dstDir )
            continue
        # end if        
        if os.path.isdir(htmlFile):
#            nTdebug("Listing dir: [%s]" % f)
            if f.find('.svn') >= 0:
                continue
            # end if
            dst = os.path.join( dstDir, f)
#            nTdebug("Copying dir: [%s] to [%s]" % (htmlFile, dst))
            if os.path.exists(dst):
#                nTdebug("Removing directory: %s" % dst)
                shutil.rmtree(dst)
            # end if
            shutil.copytree(htmlFile,  dst )
            # TODO: exclude .svn items within subdir
            svnDirectoryList = find2(".svn", startdir=dst) # don't use the one from pylab.
            for f2 in svnDirectoryList:
#                nTdebug("Considering removing directory: %s" % (f2))
                if os.path.exists(f2):
#                    nTdebug("Removing directory: %s" % f2)
                    shutil.rmtree(f2)
                # end if
            # end for
        # end if
    #end for
    base_dir = os.path.join(cingPythonCingDir, "NRG")    
    data_dir = os.path.join (base_dir, "data" )
#    base_data_dir = os.path.join (data_dir, self.results_base )
    
#    fileListToCopy = [ 'direct.php' ]
    fileListToCopy = []
    nTmessage("Copy the php scripts: %s" % fileListToCopy)
    for fileNameToCopy in fileListToCopy:
        org_file = os.path.join(data_dir, fileNameToCopy)
        new_file = os.path.join(dstDir, '..', fileNameToCopy)
        nTdebug('Copy from %s to %s' % ( org_file, new_file))
        shutil.copy(org_file, new_file)
    # end for
    nTmessage("Copy the overall index")
    org_file = os.path.join(data_dir, 'redirect.html')
    new_file = os.path.join(dstDir, '..', 'index.html')
    nTdebug('Copy from %s to %s' % ( org_file, new_file))
    shutil.copy(org_file, new_file)    
# end def
