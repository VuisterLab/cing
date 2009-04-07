"""
Adds html generation methods
"""
from cing import NaNstring
from cing import authorList
from cing import cingPythonCingDir
from cing import cingRoot
from cing import programName
from cing import versionStr
from cing.Libs.Imagery import convert2Web
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import boxAttributes
from cing.Libs.NTplot import lineAttributes
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTmessageNoEOL
from cing.Libs.NTutils import NTmkdir
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTprogressIndicator
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import NTvalue
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import NTzap
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import getDeepByKeys #@UnresolvedImport
from cing.Libs.NTutils import getDeepByKeysOrDefault
from cing.Libs.NTutils import list2asci #@UnusedImport
from cing.Libs.NTutils import sprintf
from cing.Libs.NTutils import val2Str
from cing.PluginCode.required.reqMolgrap import MOLGRAP_STR
from cing.PluginCode.required.reqWattos import WATTOS_STR
from cing.PluginCode.required.reqWattos import wattosPlotList
from cing.PluginCode.required.reqWhatif import C12CHK_STR
from cing.PluginCode.required.reqWhatif import RAMCHK_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.PluginCode.required.reqWhatif import histJaninBySsAndCombinedResType
from cing.PluginCode.required.reqWhatif import histJaninBySsAndResType
from cing.PluginCode.required.reqWhatif import histRamaBySsAndCombinedResType
from cing.PluginCode.required.reqWhatif import histRamaBySsAndResType
from cing.PluginCode.required.reqWhatif import wiPlotList
from cing.core.constants import CHARS_PER_LINE_OF_PROGRESS
from cing.core.constants import PDB
from cing.core.parameters import cingPaths
from cing.core.parameters import htmlDirectories
from cing.core.parameters import moleculeDirectories
from cing.core.parameters import plugins
import os
import shelve
import shutil


dbaseFileName = os.path.join( cingPythonCingDir,'PluginCode','data', 'phipsi_wi_db.dat' )
dbase = shelve.open( dbaseFileName )
#        histCombined               = dbase[ 'histCombined' ]
#histRamaBySsAndResType         = dbase[ 'histRamaBySsAndResType' ]
#    histBySsAndCombinedResType = dbase[ 'histBySsAndCombinedResType' ]
dbase.close()

HTML_TAG_PRE = "<PRE>"
HTML_TAG_PRE2 = "</PRE>"


def makeDihedralHistogramPlot( project, residue, dihedralName, binsize = 5, htmlOnly=False ):
    '''
    Return NTplot instance with histogram of dihedralName
    or None on error.
    Return True if it could be created if htmlOnly is not set.
    '''
    if project == None:
        return None
    if dihedralName not in residue:
        return None
    if residue[dihedralName] == None:
        return None

    if htmlOnly:
        return True

    bins       = 360/binsize
    plotparams = project.plotParameters.getdefault(dihedralName,'dihedralDefault')
#    NTdebug( 'residue: '+`residue`)
    angle = residue[dihedralName] # A NTlist
#    NTdebug( 'angle: ' + `angle`)
    ps = NTplotSet() # closes any previous plots
    ps.hardcopySize = (600,369)
    plot = NTplot( title  = residue._Cname(1),
      xRange = (plotparams.min, plotparams.max),
      xTicks = range(int(plotparams.min), int(plotparams.max+1), plotparams.ticksize),
      xLabel = dihedralName,
      yLabel = 'Occurence')
    ps.addPlot(plot)

#    Note that the good and outliers come from:
#    d.good, d.outliers = peirceTest( d )
    if not angle.__dict__.has_key('good'):
        NTcodeerror("No angle.good plots added. Skipping makeDihedralHistogramPlot for %s %s." % (
                    residue, dihedralName))
        return None
#    NTdebug( 'angle.good: ' + `angle.good`)
    plot.histogram( angle.good.zap(1),
                    plotparams.min, plotparams.max, bins,
                    attributes = boxAttributes( fillColor=plotparams.color ))
    if not angle.__dict__.has_key('outliers'):
        NTcodeerror("No angle.outliers plots added. Skipping makeDihedralHistogramPlot for %s %s." % (
                    residue, dihedralName))
        return None
#    NTdebug( 'angle.outliers: ' + `angle.outliers`)
    plot.histogram( angle.outliers.zap(1),
                plotparams.min, plotparams.max, bins,
                attributes = boxAttributes( fillColor=plotparams.outlier )
                  )
    ylim = plot.get_ylim()
    ylimMax = 5.0 # Just assume.
    if ylim is not None:
        ylimMax = ylim[1]

    # AWSS
    # Let's check if for this 'angle' there is a dihedral restraint
    aAv  = angle.cav
    width = 4.0
    dr = _matchDihedrals(residue, dihedralName)
    alpha=0.3
    if dr:
#        NTdebug("dr: " + dr.format())
        bounds = NTlist(dr.lower, dr.upper)
        bounds.limit(plotparams.min, plotparams.max)
        if bounds[0] < bounds[1]: # single box
            point = (bounds[0], 0) # lower left corner of only box.
            sizes = (bounds[1]-bounds[0],ylimMax)
            plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))
        else: # two boxes
            # right box
            point = (bounds[0], 0) # lower left corner of first box.
            sizes = (plotparams.max-bounds[0],ylimMax)
            plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))
            point = (plotparams.min, 0) # lower left corner of second box.
            sizes = (bounds[1]-plotparams.min,ylimMax)
            plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))


    # Always plot the cav line
    plot.line( (aAv, 0), (aAv, ylimMax),
               lineAttributes(color=plotparams.average, width=width) )
    return ps
#end def


def makeDihedralPlot( project, residueList, dihedralName1, dihedralName2,
                      plotTitle = None, htmlOnly=False ):
    '''Return NTplotSet instance with plot of dihedralName1 vrs dihedralName2 or
       None on error
       Called with: eg ['PHI',  'PSI',  'Ramachandran', 'PHI_PSI']

       Note that residue can also be a list of residues. A single plot will
       be created for all together were the appropriate background histograms
       will be picked.

       Return None on error or ps on success.
    '''

    if not project:
        NTerror( 'in makeDihedralPlot called without project' )
        return None
    if not residueList:
        NTerror( 'makeDihedralPlot called without residues in list' )
        return None

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
#        NTdebug( 'in makeDihedralPlot not in residue dihedral 1: '+dihedralName1 )
        return None

    if dihedralName2 not in residue or residue[dihedralName2] == None:
#        NTdebug( 'in makeDihedralPlot not in residue dihedral 2: '+dihedralName2 )
        return None
    if htmlOnly:
        return True # indicating success

    isSingleResiduePlot = len(residueList) == 1

    if not plotTitle:
        if isSingleResiduePlot:
            plotTitle = residue._Cname(1)
        else:
            plotTitle = '%d residues'



#    NTdebug("Creating a 2D dihedral angle plot for plotItem: %s %s %s", residue, dihedralName1, dihedralName2)

    plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
    plotparams2 = project.plotParameters.getdefault(dihedralName2,'dihedralDefault')

    ps =NTplotSet() # closes any previous plots
    ps.hardcopySize = (500,500)
    plot = NTplot( title  = plotTitle,
      xRange = (plotparams1.min, plotparams1.max),
      xTicks = range(int(plotparams1.min), int(plotparams1.max+1), plotparams1.ticksize),
      xLabel = dihedralName1,
      yRange = (plotparams2.min, plotparams2.max),
      yTicks = range(int(plotparams2.min), int(plotparams2.max+1), plotparams2.ticksize),
      yLabel = dihedralName2)
    ps.addPlot(plot)

    if dihedralName1=='PHI' and dihedralName2=='PSI':
        histBySsAndCombinedResType = histRamaBySsAndCombinedResType
        histBySsAndResType         = histRamaBySsAndResType
    elif dihedralName1=='CHI1' and dihedralName2=='CHI2':
        histBySsAndCombinedResType = histJaninBySsAndCombinedResType
        histBySsAndResType         = histJaninBySsAndResType
    else:
        NTcodeerror("makeDihedralPlot called for non Rama/Janin")
        return None

    histList = []
    ssTypeList = histBySsAndResType.keys() #@UndefinedVariable
    ssTypeList.sort()
    # The assumption is that the derived residues can be represented by the regular.
    resNamePdb = getDeepByKeysOrDefault(residue, residue.resName, 'nameDict', PDB)
    if len( resNamePdb ) > 3: # The above line doesn't work. Manual correction works 95% of the time.
        resNamePdb = resNamePdb[:3]  # .pdb files have a max of 3 chars in their residue name.
#    NTdebug('Looked up residue.resName %s to resNamePdb %s' % ( residue.resName,resNamePdb ))

    for ssType in ssTypeList:
        hist = getDeepByKeys(histBySsAndCombinedResType,ssType)
        if isSingleResiduePlot:
            hist = getDeepByKeys(histBySsAndResType,ssType,resNamePdb)
        if hist != None:
#            NTdebug('Appending for ssType %s and resNamePdb %s' % ( ssType,resNamePdb ))
            histList.append(hist)
    if histList:
#        NTdebug('Will do dihedralComboPlot')
        plot.dihedralComboPlot(histList)



    # Plot restraint ranges for single residue plots.
    for res in residueList:
        if isSingleResiduePlot:
            # res is equal to residue
            dr1 = _matchDihedrals(res, dihedralName1)
            dr2 = _matchDihedrals(res, dihedralName2)

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
                plot.plotDihedralRestraintRanges2D(lower1, upper1,lower2, upper2)

        d1 = res[dihedralName1]
        d2 = res[dihedralName2]

        if not (len(d1) and len(d2)):
#            NTdebug( 'in makeDihedralPlot dihedrals had no defining atoms for 1: %s or', dihedralName1 )
#            NTdebug( 'in makeDihedralPlot dihedrals had no defining atoms for 2: %s'   , dihedralName2 )
            return None
        d1cav = d1.cav
        d2cav = d2.cav

        # Plot data points on top for painters algorithm without alpha blending.
        myPoint = plusPoint.copy()
        myPoint.pointColor = 'green'
        myPoint.pointSize = 6.0
        myPoint.pointEdgeWidth = 1.0
        if res.resName == 'GLY':
            myPoint.pointType = 'triangle'
        if res.resName == 'PRO':
            myPoint.pointType = 'square'

        plot.points( zip( d1, d2 ), attributes=myPoint )

        # Plot the cav point for single residue plots.
        if isSingleResiduePlot:
            myPoint = myPoint.copy()
            myPoint.pointSize = 8.0
            myPoint.pointType = 'circle'
            myPoint.pointColor = 'blue'
            myPoint.fill = False
            plot.point( (d1cav, d2cav),myPoint )

    return ps
#end def



def _matchDihedrals(residue, dihedralName):
    for dr in residue.dihedralRestraints:
        if dr.angle == '%s_%i' % (dihedralName, residue.resNum):
            return dr
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
        NTerror('setupHtml: no molecule defined')
        return True
    #end if

    NTmessage('==> Initializing HTML objects')
    HTMLfile.killHtmlObjects()

    molecule = project.molecule

    ProjectHTMLfile( project )
    MoleculeHTMLfile( project, molecule )
    for chain in molecule.allChains():
        ChainHTMLfile( project, chain )
    for res in molecule.allResidues():
        ResidueHTMLfile( project, res )

#    atomList = AtomList(project) # instantiated only for this purpose locally; TODO: should be in molecule section updateAll
#    project.molecule.atoms = atomList
#    atomList.molecule = project.molecule
    if hasattr(molecule, 'atomList'):
        AtomsHTMLfile( project, molecule.atomList )
    else:
        # reduced verbosity here because gets tested in test_NTutils3.py.
        NTwarning("Failed to create AtomsHTMLfile because no molecule.atomList")

    if hasattr(molecule, 'ensemble'):
        EnsembleHTMLfile( project, molecule.ensemble )
    else:
        NTdebug("Not creating EnsembleHTMLfile because no ensemble")

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
        NTerror('generateHtml: no molecule defined')
        return True
    #end if

    NTmessageNoEOL('==> Generating CING HTML code')
    if htmlOnly:
        NTmessage('.')
    else:
        NTmessage(' and images.')

    project.html.generateHtml(htmlOnly=htmlOnly)
    project.molecule.html.generateHtml(htmlOnly=htmlOnly)
    for chain in project.molecule.allChains():
        chain.html.generateHtml(htmlOnly=htmlOnly)
        NTmessage("Html for chain %s and its residues", chain.name)
        for res in NTprogressIndicator(chain.allResidues(), CHARS_PER_LINE_OF_PROGRESS):
            res.html.generateHtml(htmlOnly=htmlOnly)
    #end for
    NTmessage("Html for atoms and models")
    if hasattr(project.molecule, 'atomList'):
        project.molecule.atomList.html.generateHtml(htmlOnly=htmlOnly)
    if hasattr(project.molecule, 'ensemble'):
        project.molecule.ensemble.html.generateHtml(htmlOnly=htmlOnly)

    NTmessage('Html for peaks and restraints')
    for l in NTprogressIndicator(project.peaks+project.allRestraintLists(), CHARS_PER_LINE_OF_PROGRESS):
        if hasattr(l,'html'):
            l.html.generateHtml(htmlOnly=htmlOnly)
    #end for
#end def

def renderHtml(project):
    '''Description: render HTML content for a Cing.Molecule or for just a
               Cing.Chain, Cing.Residue or Cing.Atom.
       Inputs: a Cing.Molecule, Cing.Chain, Cing.Residue or Cing.Atom.
       Output: return None for success is standard.
    '''
    NTmessage('==> Rendering HTML pages')
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
        name = previous._Cname(-1)
        obj.html.insertHtmlLink( obj.html.header, obj, previous, text = name, id=HTMLfile.headerSectionId,
                                 title = sprintf('goto %s', name)
                               )

    if obj._parent:
        name = obj._parent._Cname(-1)
        obj.html.insertHtmlLink( obj.html.header, obj, obj._parent, text = 'UP',
                                 title = sprintf('goto %s', name)
                               )

    next = obj.sibling(1)
    if next:
        name = next._Cname(-1)
        obj.html.insertHtmlLink( obj.html.header, obj, next, text = next._Cname(-1), id=HTMLfile.headerSectionId,
                                 title = sprintf('goto %s', name)
                               )
#end def

class MakeHtmlTable:
    """Iterative class that generates rows of html Table
        columnFormats:     a list of (header, dict()) tuples describing the column
                             header can be None for no header above column

    Using co statements do format columns did not render properly for align=right

h = HTMLfile('test.html')
t = MakeHtmlTable(h.main,[('row1', dict(width="30px", align="right")),
                          ('row2', dict(width="20px")),
                          ( None, dict(width="40px")), # empty
                          ('row3', dict(width="30px")),
                          ('row4', dict(width="30px"))
                         ],
                 )

for row in t.rows(range(5)):
    t.nextColumn()
    t(None, str(row)+"."+str(1) )
    t.nextColumn()
    t('a', str(row)+"."+str(2) )

    t.nextColumn()  # empty one

    t.nextColumn()
    t(None, str(row)+"."+str(3) )
    # or for oneliners
    t.nextColumn(None, str(row)+"."+str(4) )

#end for
h.render()

    """
    def __init__(self, html, columnFormats=[]):
        self.html = html
        self.columnFormats = columnFormats

        self._rows = None
        self._iter = -1
        self._columnOpen    = False
        self._currentColumn = -1
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
        """
#        print 'iter>', self._rows, self._iter
        if self._rows == None: return None

        self._iter = 0
        self._len  = len(self._rows)
        self._columnOpen    = False
        self._currentColumn = -1

        self.html('table',closeTag=False)
# Using the col statements, the align did not work, at least not using safari
# Now these attributed are explicitly coded for each TD tag
#        for _tmp, kwds in self.columnFormats:
#            self.html('col', **kwds)
        self._mkColumnHeaders()
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
            return None

        self.html('tr', closeTag=False)
        s = self._rows[self._iter]
        self._iter += 1
        self._currentColumn = -1
        self._columnOpen    = False
        return s
    #end def

    def openColumn(self, columnIndex=-1, *args, **kwds):
        """<td> statements with redefined collumn formats
        kwds can override/expand
        """
        if columnIndex >=0 and columnIndex < len(self.columnFormats):
            _tmp,formats = self.columnFormats[columnIndex]
            formats.update(kwds)
            self.html('td',closeTag=False, *args, **formats)
        else:
            self.html('td',closeTag=False, *args, **kwds)
#        self.html('td',closeTag=False)
        self._columnOpen = True
    #end def

    def closeColumn(self):
        self.html('td',openTag=False)
        self._columnOpen = False
    #end def

    def nextColumn(self, *args, **kwds):
        if self._currentColumn >= 0:
            self.closeColumn()
        self.openColumn(self._currentColumn+1, *args, **kwds)
        self._currentColumn += 1
#        if len(args)>0:
#            self.html(*args)
    #end def

    def _mkColumnHeaders(self):
        """Make column headers if any defined
        """
        headers = NTzap(self.columnFormats, 0)
        #print "headers>", headers
        doHeaders = False
        for h in headers:
            if h != None:
                doHeaders = True
                break
        #end for
        if not doHeaders: return

        self.html('tr', closeTag=False)
        for i,h in enumerate(headers):
            self.openColumn(i)
            if h:
                self.html('i', h)
#                self.html(None, h)
            self.closeColumn()
        #end for
        self.html('tr', openTag=False)
    #end def
#end class


def _makeResidueTableHtml( obj, residues, text=None ):
    """
    Make a table with links to residues in html.main of obj
    Return True on error.
    """
    #TODO: use makHtmlTable class
    ncols = 10
    width = '75px' # reserve some space per residue in chain table

    if text:
        obj.html.main('h1',text)
    if not residues:
        NTerror("Failed to _makeResidueTableHtml")
        return True

    r0 = residues[0]
    r1 = r0.resNum
    r2 = r0.resNum/ncols *ncols + ncols-1
    obj.html.main('table', closeTag=False)
    obj.html.main('tr', closeTag=False)
    obj.html.main( 'td',sprintf('%d-%d',r1,r2), style="width: %s" % width )
    for _emptyCell in range( r0.resNum%ncols ):
        obj.html.main('td', style="width: %s" % width)

    prevRes = None
    for res in residues:
        chainBreakDetected = (prevRes!=None) and (prevRes.resNum != (res.resNum - 1))
        if chainBreakDetected or res.resNum%ncols == 0:
            r1 = res.resNum/ncols *ncols
            r2 = r1+ncols-1
            obj.html.main('tr', openTag=False)
            obj.html.main('tr', closeTag=False)
            obj.html.main('td',sprintf('%d-%d',r1,r2), style="width: %s" % width )
            for _emptyCell in range( res.resNum%ncols ):
                obj.html.main('td', style="width: %s" % width)

        # add residue to table
        obj.html.main('td', style="width: %s" % width, closeTag=False)
        obj.html.insertHtmlLink(obj.html.main, obj, res, text=res.name)
        obj.html.main('td', openTag=False)
        prevRes = res
    #end for over res in residues

    obj.html.main('tr', openTag=False)
    obj.html.main('table', openTag=False)
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
           Output: an instanciated HTMLfile obj.

           GV Not any longer as I do not see the need: The file is immidiately tested by a quick open for writing and closing.
        '''

        self.fileName = NTmkdir( fileName )
#        self.rootPath, _tmp, _tmp = NTpath( fileName )
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

    def render(self):
        '''Description: write container to file Html.
           Inputs: a HTMLfile obj.
           Output: written lines and closed file.

           JFD notes it is simpler to code this as constructing the whole content
           first and then writing. It would be just as fast for the size
           of html files we render.
        '''

        self.stream = open( self.fileName, 'w' )
#        NTdebug('writing to file: %s' % self.fileName)
        self.indent = 0
        # JFD proposes to drop the below tags because they hinder javascript beyond my knowledge.
        # AWSS updated it: it should work fine with javascript
        self.stream.write(self.openTag('!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'))
        self.stream.write(self.openTag('html'))
        self.stream.write(self.openTag('head'))
        if self.title:
            self.stream.write( self._generateTag( 'title', self.title ))

        relativePath = self.relativePath()
        cssLink = os.path.join(relativePath, cingPaths.css)
        jsMultiLineLink = os.path.join(relativePath, cingPaths.jsMultiLine)
        self.stream.write(self._generateTag( 'link',
            rel="stylesheet", type="text/css", media="screen", href=cssLink))
        self.stream.write(self._generateTag( 'script', # Not needed for all but always nice.
            type="text/javascript", src=jsMultiLineLink))

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
        self._appendTag( defaultFooter, None, sprintf( ' %s  version %s ', programName, versionStr) )
        n = len(authorList)-1
        for i,author in enumerate(authorList):
            self._appendTag( defaultFooter, 'a', author[0], href=sprintf("mailto:%s", author[1]))
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
#        NTdebug("htmlPath: ["+htmlPath+"]" )
        downSep = htmlPath.count(sep)
        return (upSep-downSep-1) * pardirSep

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
                NTerror('HTMLfile.findHtmlLocation: No htmlLocation attribute associated to object %s', item)
                return None

        # Strip leading dot for rest of algorithm.
        # Normalize path, eliminating double slashes, etc.
        sourcePath = os.path.normpath(     source.htmlLocation[0])
        destPath   = os.path.normpath(destination.htmlLocation[0])
        # Get default id.
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
            NTerror("No HTML section defined here")
            return None

        if not source:
            # Happens for 2k0e
            NTwarning("No Cing object source defined here")
            return None

        if not destination:
            # Happens for 2k0e
            NTwarning("No Cing object destination defined here")
            return None

        link = self.findHtmlLocation( source, destination, id )
#        NTdebug('From source: %s to destination: %s, id=%s using relative link: %s' ,
#                 source.htmlLocation, destination.htmlLocation, id,link
#               )


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

        #css and javascript now in HTML dir
        htmlPath = os.path.join(cingRoot,cingPaths.html) # copy needed css and other files
        for f in os.listdir( htmlPath ):
            htmlFile = os.path.join(htmlPath,f)
            if os.path.isfile(htmlFile):
                shutil.copy( htmlFile, project.htmlPath() )
        #end for

        # create an redirect index page in top of project
        fmt = '''
<html>
<head>
<title>%s/title>
<meta http-equiv="Refresh" content="0; url=%s">
</head>
<body>
Redirecting to %s
</body>
</html>
'''
        f = open(project.path('index.html'),'w')
        path = os.path.join(self.project.molecule.name, moleculeDirectories['html'], 'index.html')
        fprintf(f, fmt, title, path, path)
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

        s = self.project.summary(toFile = False).split('\n')

        # Create a two-state machinery.
        summaryLineCount = len(s)
        i = 0
        while i < summaryLineCount:
            l = s[i]
            if l[0:5] == '-----':
                html.main('h3', l )
            elif l.startswith('<PRE>'): # should occur alone on line!
                preLineList = []
                while True:
                    i += 1
                    if i >= summaryLineCount:
                        NTcodeerror("Failed to find </PRE> all the way to the end")
                        break
                    l = s[i]
                    if l.startswith('</PRE>'): # should occur alone on line!
                        break
                    preLineList.append( l )
                subStr = '\n'.join(preLineList)
                html.main('pre', subStr)
            else:
                html.main('br', l )
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
        flatFiles.htmlLocation = (self.project.moleculePath('analysis'), HTMLfile.top )
        self.insertHtmlLinkInTag('li',self.main, self.project, flatFiles, text="Details (flat)")

        #Use a dummy object for referencing the text-files for now
        progFiles = NTdict()
        progFiles.htmlLocation = (self.project.moleculePath(), HTMLfile.top )
        self.insertHtmlLinkInTag('li',self.main, self.project, progFiles, text="Programs (flat)")

        if hasattr(self, 'history'):
            del(self.history)
        self.history = self._generateHistoryHtml()
        self.insertHtmlLinkInTag( 'li', self.main, self.project, self.history, text='History')
        self.main('ul', openTag=False)

        # Molecule page and assignment links
        htmlMain('h1', 'Molecule ')
        htmlMain('ul', closeTag=False)
        self.insertHtmlLinkInTag( 'li', htmlMain, self.project, self.project.molecule,
                                        text=self.project.molecule.name
                                )

        if hasattr(self.project.molecule, 'atomList'):
            self.insertHtmlLinkInTag( 'li', htmlMain, self.project, self.project.molecule.atomList, text='Assignments' )
        htmlMain('ul', openTag=False)

        # peaks
        if len(self.project.peaks) > 0:
            htmlMain('h1', 'Peaks')
            htmlMain('ul', closeTag=False)
            for pl in self.project.peaks:
                if hasattr(pl,'html'):
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
                NTdebug("ProjectHtmlFile.generateHtml: Trying to create : " + pathMolGif)
                self.project.molecule.export2gif(pathMolGif, project=self.project)
            else:
                NTdebug("Skipping self.project.molecule.export2gif because Molgrap Module is not available.")

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

class MoleculeHTMLfile( HTMLfile ):
    """
    Class to generate HTML files for Molecule instance
    """

    def __init__(self, project, molecule ):
        # Create the HTML directory for this molecule
        fileName = project.htmlPath( htmlDirectories.molecule, 'index.html')
        HTMLfile.__init__(self, fileName, title='Molecule ' + molecule.name, molecule=molecule, project=project)
        molecule.htmlLocation = ( fileName, HTMLfile.top )

        if molecule.has_key('html'):
            del(molecule['html'])
        molecule.html = self
    #end def

    def _generateHeader(self):
        """generate header html for this Molecule"""
        self.header('h1', 'Molecule '+self.molecule._Cname(-1) )
        _navigateHtml( self.molecule )
    #end def

    def _generateProcheckHtml(self, htmlOnly = False):
        """Generate html code for Procheck output"""
        main = self.main
        project = self.project
        molecule = self.molecule

        NTmessage("Creating Procheck html")
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
        plotCount = -1
        for p,d in NTprogressIndicator(pcPlotList):
            plotCount += 1
            procheckLink = os.path.join('../..',
                        project.moleculeDirectories.procheck, molecule.name + p + ".ps")
            procheckLinkReal = os.path.join( project.rootPath( project.name )[0], molecule.name,
                        project.moleculeDirectories.procheck, molecule.name + p + ".ps")
#            NTdebug('procheck real path: ' + procheckLinkReal)
            if not os.path.exists( procheckLinkReal ):
                continue # Skip their inclusion.

            if not htmlOnly and not convert2Web( procheckLinkReal, doMontage=True ):
                NTerror( "Failed to convert2Web input file: " + procheckLinkReal)
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
        #end for

        if plotCount: # close any started rows.
            main('tr',  openTag=False)
        main('table',  openTag=False) # close table
        if not anyProcheckPlotsGenerated:
            main('h2', "No procheck plots found at all")
    #end def

    def _generateWhatifHtml(self, htmlOnly=False):
        """Generate the Whatif html code
        """
        main = self.main
        project = self.project
        molecule = self.molecule

        if not htmlOnly:
            NTmessage("Creating Whatif html")
            if hasattr(plugins, WHATIF_STR) and plugins[ WHATIF_STR ].isInstalled:
                if project.createHtmlWhatif():
                    NTerror('Failed to createHtmlWhatif')
                    return True
                #end if
            #end if
        #end if

        anyWIPlotsGenerated = False

        main('h1','What If')
        ncols = 6
        main('table',  closeTag=False)
        plotCount = -1
        for p,d in NTprogressIndicator(wiPlotList):
            plotCount += 1
            wiLink = os.path.join('../..',
                        project.moleculeDirectories.whatif, molecule.name + p + ".pdf")
            wiLinkReal = os.path.join( project.rootPath( project.name )[0], molecule.name,
                        project.moleculeDirectories.whatif, molecule.name + p + ".pdf")
#            NTdebug('wiLinkReal: ' + wiLinkReal)
            if not os.path.exists( wiLinkReal ):
#                NTwarning('Failed to find expected wiLinkReal: ' + wiLinkReal) # normal when whatif wasn't run.
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

        NTmessage("Creating Wattos html")
        if not htmlOnly:
            if hasattr(plugins, WATTOS_STR) and plugins[ WATTOS_STR ].isInstalled:
                if project.createHtmlWattos():
                    NTerror('Failed to createHtmlWattos')
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
#            NTdebug('wiLinkReal: ' + wiLinkReal)
            if not os.path.exists( wattosLinkReal ):
#                NTwarning('Failed to find expected wiLinkReal: ' + wiLinkReal) # normal when whatif wasn't run.
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
            _makeResidueTableHtml( self.molecule, chain.allResidues(), None )
        #end for

        if hasattr(self.molecule, 'ensemble'):
            self.main('h1', 'Model-based analysis')
            self.insertHtmlLink(self.main, self.molecule, self.molecule.ensemble, text='Models page')

        self.main('h1', 'Structure-based analysis')
        #Use a dummy object for referencing the salt-bridges text-file for now
        _dummy = NTdict()
        _dummy.htmlLocation = (self.project.moleculePath('analysis')+'/saltbridges.txt', HTMLfile.top )
        self.insertHtmlLink(self.main, self.molecule, _dummy, text='Salt bridges')

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
        HTMLfile.__init__(self, fileName, title=chain.name, chain=chain, project=project)
        chain.htmlLocation = ( fileName, HTMLfile.top )

        if chain.has_key('html'):
            del(chain['html'])
        chain.html = self
    #end def

    def _generateHeader(self):
        # generate header html for this residue
        self.header('h1', self.chain._Cname(-1) )
        _navigateHtml( self.chain )
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate the HTML code and/or Figs depending htmlOnly
        """
        # Reset CING content
        self._resetCingContent()
        self._generateHeader()

        _makeResidueTableHtml( self.chain, self.chain.allResidues(), 'Residues' )

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
        HTMLfile.__init__(self, fileName, title=residue.name, residue=residue, project=project)
        residue.htmlLocation = ( fileName, HTMLfile.top )

        if residue.has_key('html'):
            del(residue['html'])
        residue.html = self
#        self.resdir = self.rootPath
        self._mkDistanceTableTemplate()
        self._mkDihedralTableTemplate()

    def _generateHeader(self, plottedList):
        # generate header html for this residue
        self.header('h1', self.residue._Cname(-1) )
        _navigateHtml( self.residue )

        self.header('a', 'Help', href = self.relativePath()+HTMLfile.help_html, title='goto page with help')

        #TODO: Remove styling from below, should be in css
        self.header( 'br' )
        self.header( 'br' )
        for plot in plottedList:
            kw = {'href':'#'+plot}
            self.header('a' , plot, style="font-size: 10px", title=sprintf('goto %s plot on this page',plot), **kw)
    #end def

    def generateHtml(self, htmlOnly=False):
        """
        Generate the HTML code and/or Figs depending htmlOnly
        """
        residue = self.residue
        project = self.project
#        resNum  = residue.resNum
        resdir, _tmp, _tmp = NTpath( self.fileName )

        # Reset CING content
        self._resetCingContent()

        # 0: angle 1 name
        # 1: angle 2 name
        # 2: Angle combination name
        # 3: Tuple of arbitrary number of keys to value to show
        # 4: Name of value to show (eg QUACHK)
        plotList = [['PHI',  'PSI',  'Ramachandran', (WHATIF_STR, RAMCHK_STR, VALUE_LIST_STR), RAMCHK_STR ],
                    ['CHI1', 'CHI2', 'Janin',        (WHATIF_STR, C12CHK_STR, VALUE_LIST_STR), C12CHK_STR]
                   ]
        graphicsFormatExtension = 'png'
        plottedList = []
#        NTdebug("in generateHtml htmlOnly: %s",htmlOnly)
#        if not htmlOnly:
#            NTdebug("Residue %s: generating dihedral plots", self.residue )

        for plotDihedralName1,plotDihedralName2,plotDihedralComboName,keys,_tmp in plotList:
#                NTdebug("Residue %s: generating %s plot", self.residue, plotDihedralComboName)
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
#                    NTdebug("Residue %s: generating dihedral %s plot", self.residue, dihed )
                ps = makeDihedralHistogramPlot( project, residue, dihed, htmlOnly=htmlOnly )
                tmpPath = os.path.join(resdir,dihed + '.' + graphicsFormatExtension)
                if ps:
                    plottedList.append(dihed)
                    if isinstance(ps, NTplotSet): # actually created.
                        ps.hardcopy( fileName = tmpPath )
                #end if
        #end for
        #end if htmlOnly:

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
        for plotDihedralName1,plotDihedralName2,plotDihedralComboName,keys,_tmp in plotList:
            plotFileNameDihedral2D = plotDihedralComboName + '.' + graphicsFormatExtension
            if not plotDihedralComboName in plottedList: # failed on first attempt already. No sense in trying again.
                continue
            tmpPath = os.path.join(resdir, plotDihedralComboName + '.' + graphicsFormatExtension)
            residue.html.left( 'h2', plotDihedralComboName, id=plotDihedralComboName)
            residue.html.left( 'img', src = plotFileNameDihedral2D )
            # Try to show a What If average Z-score like: 'whatif.QUACHK.valueList 0.054 (+/- 0.012'
            strToShow = '.'.join( keys )
            av = getDeepByKeys(residue,*keys)
            if av != None:
                sd = None
                if isinstance(av, NTlist):
                    ( av, sd, _n ) = av.average()
                pointNTvalueStr = "%s"  % NTvalue(value=av, error=sd, fmt='%.2f (+- %.2f)', fmt2='%.2f' )
                strToShow += ': %s' % pointNTvalueStr
                residue.html.left( 'p', strToShow ) # The a tag is not filled yet. Might link to NTmoleculePlot?
            #end if
        #end for

        # Dihedrals
        for dihed in residue.db.dihedrals.zap('name'):
            if dihed in residue and residue[dihed]:
                if not dihed in plottedList: # failed on first attempt already. No sense in trying again.
                    continue
    #                            NTdebug( '------>>>>> ' + dihed + `res` + `res[dihed]` )
                d = residue[dihed] # List of values with outliers etc attached.

                # summarize the results
                lenOutliers = '.' # JFD adds: Indicating None
                outlierList = '.'
                if d.__dict__.has_key('outliers'):
    #                            NTwarning("Found no outliers; code wasn't prepared to deal with that or is JFD wrong?")
                    lenOutliers = `len(d.outliers)`
                    outlierList = d.outliers.zap(0)
    #                            -180.1 is longest: 6.1f
                summary = '%-6s: average: %6.1f   cv: %6.3f  ||  outliers: %3s (models %s)' % (
                           dihed, d.cav, d.cv, lenOutliers, outlierList )
                fprintf( fp, '%s\n', summary )
                #generate HTML code for plot and text
                residue.html.left( 'h2', dihed, id=dihed),
                residue.html.left( 'img', src = dihed + '.' + graphicsFormatExtension, alt=""  )
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

    def _mkDistanceTableTemplate(self):

        self.distanceTable =   MakeHtmlTable( self.right,
                                       columnFormats = [('id',        dict(width= "20px", align="left",  valign="top", style="font-size: 10px") ),
                                                        ('atoms',     dict(width="180px", align="left", valign="top", style="font-size: 10px" ) ),
                                                        #nb align="char", char="." does not work
                                                        ('lower',     dict(width= "25px", align="right",  valign="top", style="font-size: 10px") ),
                                                        ('upper',     dict(width= "25px", align="right",  valign="top", style="font-size: 10px") ),
                                                        ('actual',    dict(width= "55px", align="right",  valign="top", style="font-size: 10px") ),

                                                        ('violations',dict(width= "55px", align="right",  valign="top", style="font-size: 10px") ),
                                                        ('Max',       dict(width= "25px", align="right",  valign="top", style="font-size: 10px") ),
                                                        ('>threshold',     dict(width= "25px", align="center",    valign="top", style="font-size: 10px") ),

                                                        ('Critique',  dict(align="left",  valign="top", style="font-size: 10px") )
                                                       ],
                              )
    #end def

    def _generateDistanceRestraintCode(self, drl):

        t = self.distanceTable
        for dr in t.rows(drl):
            t.nextColumn()
            self.insertHtmlLink(self.right, self.residue, dr, text=val2Str(dr.id,'%d'), title=sprintf('goto distance restraint %d', dr.id))

            t.nextColumn()
            count = 0
            for atm1,atm2 in dr.atomPairs:
#                t(None,sprintf('(%s,%s)', atm1._Cname(2), atm2._Cname(2)))
#                t(None,'(')
                _generateAtomLink( self.residue, atm1, self.right)
                t(None,',')
                _generateAtomLink( self.residue, atm2, self.right)
#                t(None,')')
                t('br')
                count += 1
                if count == 3:
                    t(None,'etc, etc. ')
                    self.insertHtmlLink(self.right, self.residue, dr, text='(full list)')
                    break
                #end if
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
    #end def

    def _mkDihedralTableTemplate(self):

        self.dihedralTable =   MakeHtmlTable( self.right,
                                       columnFormats = [('id',        dict(width= "20px", align="left",  valign="top", style="font-size: 10px") ),
                                                        ('dihedral',  dict(width= "80px", align="left", valign="top", style="font-size: 10px" ) ),
                                                        #nb align="char", char="." does not work
                                                        ('lower',     dict(width= "40px", align="right",  valign="top", style="font-size: 10px") ),
                                                        ('upper',     dict(width= "40px", align="right",  valign="top", style="font-size: 10px") ),
                                                        ('actual',    dict(width= "80px", align="right",  valign="top", style="font-size: 10px") ),

                                                        ('violations',dict(width= "80px", align="right",  valign="top", style="font-size: 10px") ),
                                                        ('Max',       dict(width= "40px", align="right",  valign="top", style="font-size: 10px") ),
                                                        ('>threshold',dict(width= "25px", align="center",    valign="top", style="font-size: 10px") ),

                                                        ('Critique',  dict(align="left",  valign="top", style="font-size: 10px") )
                                                       ],
                              )
    #end def

    def _generateDihedralRestraintCode(self, drl):

        t = self.dihedralTable
        for dr in t.rows(drl):
            t.nextColumn()
            self.insertHtmlLink(self.right, self.residue, dr, text=val2Str(dr.id,'%d'), title=sprintf('goto dihedral restraint %d', dr.id))

            t.nextColumn(dr.getName())

            t.nextColumn(val2Str(dr.lower,'%.1f'))
            t.nextColumn(val2Str(dr.upper,'%.1f'))
            t.nextColumn(sprintf('%s+-%s', val2Str(dr.cav,'%.1f'), val2Str(dr.cv,'%.1f')) )

            t.nextColumn(sprintf('%s+-%s', val2Str(dr.violAv,'%.1f'), val2Str(dr.violSd,'%.1f')) )
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
        residue = self.residue
        project = self.project

        if type == 'Distance':
            restraintList = residue.distanceRestraints
        elif type == 'Dihedral':
            restraintList = residue.dihedralRestraints
        else:
            return
        #end if

        if len(restraintList) == 0: return

        resRight = residue.html.right
        resRight('h2','%s Restraints' % type)


        tmpDict = NTdict()
        for restraint in restraintList:
            RLname = os.path.basename(restraint.htmlLocation[0]).split('.')[0]
            if tmpDict.has_key(RLname):
                tmpDict[RLname].append(restraint)
            else:
                tmpDict[RLname] = NTlist(restraint)
            #end if
        #end for
        RLists = tmpDict.keys()
        # display Restraint list
        for k in RLists:
            RLobj = project[k]
            resRight('h3', closeTag=False)
            residue.html.insertHtmlLink(resRight, residue, RLobj, text=k)
            resRight('h3', openTag=False)
            resRight('p', closeTag=False)
            #resRight('br')
            resRL = tmpDict[k]
            # sort list by 'violCount3' reverse order (higher to lower values)
            resRL = sortListByRogAndKey(resRL, 'violCount3' )

            # display restraint by number, in line, sorted by violCount3 reverse
            #for dr in resRL:
            #    residue.html.insertHtmlLink(resRight, residue, dr, text=str(dr.id))
            #end for
            # display restraint by line
            toShow = 5 # number of restraints to show on the right side of Residue page

            if type == 'Distance':
                self._generateDistanceRestraintCode(resRL[0:toShow])
            elif type == 'Dihedral':
                self._generateDihedralRestraintCode(resRL[0:toShow])
#                for dr in resRL:
#                    text = '%s:' % (str(dr.id))
#                    residue.html.insertHtmlLink(resRight, residue, dr, text=text)
#                    #resRight('ul', closeTag=False)
#                    if type == 'Distance':
#                        av = dr.av
#                        for atomPair in dr.atomPairs:
#                            res1 = atomPair[0]._parent
#                            res2 = atomPair[1]._parent
#                            atomName1 = "(" + atomPair[0].toString() +','
#                            atomName2 =       atomPair[1].toString() +')'
#        #                    atomName1 = "(%s.%s," % ( res1.name, atomPair[0].name )
#        #                    atomName2 = "%s.%s)" % ( res2.name, atomPair[1].name )
#                            residue.html.insertHtmlLink( resRight, residue, res1,
#                                                         text = atomName1 )
#                            residue.html.insertHtmlLink( resRight, residue, res2,
#                                                         text = atomName2 )
#                        #end for
#                    #end if
#                    if type == 'Dihedral':
#                        av = dr.cav
#                        #resRight( 'a', '%s' % dr.angle)
#                        #angleName = dr.angle.split('_')[0]
#                        angleName = dr.getName()
#                        residue.html.insertHtmlLink( resRight, residue, residue,
#                                                     text=angleName, id=angleName )
#                    #end if
#                    resRight('br')
#                    resRight( 'a', type + ': Lower/Av/Upper: %s/ %s / %s' %
#                              (val2Str(dr.lower, "%.2f"),
#                               val2Str(av,       "%.2f"),
#                               val2Str(dr.upper, "%.2f") ))
#                    resRight('br')
#                    #resRight('li', 'Average (Min/Max):  %.3e (%.3e / %.3e)'
#                    #                 % (restraint.av, restraint.min, restraint.max))
#                    resRight( 'a', 'Violations: violCount3 / Average / SD / Max: %d / %s / %s / %s' %
#                                (       dr.violCount3,
#                                        val2Str(dr.violAv,  "%.2f"),
#                                        val2Str(dr.violSd,  "%.2f"),
#                                        val2Str(dr.violMax, "%.2f") ))
#                    resRight('br')
#                    dr.rogScore.createHtmlForComments(resRight)
#
#                    #resRight('ul', openTag=False)
#                    resRight('br')
#                    if resRL.index(dr) + 1 == toShow:
#                        if len(resRL) > toShow :
#                            resRight('a','More: ')
#                            for dr in resRL[toShow:]:
#                                residue.html.insertHtmlLink( resRight, residue, dr,
#                                                         text=str(dr.id) )
#                                #end for
#                            resRight('br')
#                        break
#                    #end if
#                #end for
#            #end if
            resRight('p', openTag=False)
        #end for
    #end def
#end class

def _generateAtomLink( refObj, atom, section):

    residue = atom.residue
    chain   = atom.residue.chain
    refObj.html.insertHtmlLink( section, refObj, chain,   text =       chain.name,   title = sprintf('goto chain %s', chain._Cname(-1)) )
    refObj.html.insertHtmlLink( section, refObj, residue, text = '.' + residue.name, title = sprintf('goto residue %s', residue._Cname(-1)) )
    refObj.html.insertHtmlLink( section, refObj, atom,    text = '.' + atom.name,    title = sprintf('goto atom %s', atom._Cname(-1)) )
#end def

class AtomsHTMLfile( HTMLfile ):
    """Generate an Atoms html file for listing resonances
    """
    def __init__(self, project, atomList):

        fileName = project.htmlPath( htmlDirectories.molecule, 'atoms.html' )
        atomList.htmlLocation = ( fileName, HTMLfile.top )
        HTMLfile.__init__( self, fileName, title = 'Atom List ' + atomList.name, project=project )
        if hasattr(atomList, 'html'):
            del(atomList.html)
        atomList.html = self
        self.atomList = atomList

        # set the fileName and tags to locate each atom
        for atom in self.atomList:
            tag = '_o'+str(atom.__OBJECTID__)
            atom.htmlLocation = ( self.fileName, '#' + tag )
    #end def

    def _atomRow(self, atom, table):
        """Generate one row in table for atom
        """
        #TODO: this code also appears in validateAssignments
        sav     = None
        ssd     = None
        delta   = None
        rdelta  = None
        dav     = None
        dsd     = None
        value   = None
        error   = None

        if atom.has_key('shiftx') and len(atom.shiftx) > 0:
            sav = atom.shiftx.av
            ssd = atom.shiftx.sd
        if atom.isAssigned() and sav:
            delta = atom.resonances().value - sav
            rdelta = 1.0
            if ssd > 0.0:
                rdelta = sav/ssd
        if atom.db.shift:
            dav = atom.db.shift.average
            dsd = atom.db.shift.sd
        if atom.resonances():
            value = atom.resonances().value
            error = atom.resonances().error

        savStr     = val2Str(sav,   '%6.2f', 6 )
        ssdStr     = val2Str(ssd,   '%6.2f', 6 )
        deltaStr   = val2Str(delta, '%6.2f', 6 )
        rdeltaStr  = val2Str(rdelta,'%6.2f', 6 )
        davStr     = val2Str(dav,   '%6.2f', 6 )
        dsdStr     = val2Str(dsd,   '%6.2f', 6 )
        valueStr   = val2Str(value, '%6.2f', 6 ) # was sometimes set to a NOSHIFT
        if valueStr==NaNstring:
            error=None
        errorStr   = val2Str(error, '%6.2f', 6 )

        # start of html

        chain   = atom.residue.chain
        residue = atom.residue
        table.nextColumn()
        self.insertHtmlLink( self.main, self.atomList, chain,   text =       chain.name,   title = sprintf('goto chain %s', chain._Cname(-1)) )
        self.insertHtmlLink( self.main, self.atomList, residue, text = '.' + residue.name, title = sprintf('goto residue %s', residue._Cname(-1)) )
        self.insertHtmlLink( self.main, self.atomList, atom,    text = '.' + atom.name,    title = sprintf('goto atom %s', atom._Cname(-1)) )

        table.nextColumn(valueStr)
        table.nextColumn(errorStr)
        if atom.isStereoAssigned():
            table.nextColumn('S')
        else:
            table.nextColumn('.')


        for val,err in [(savStr,   ssdStr),
                        (deltaStr, rdeltaStr),
                        (davStr,   dsdStr)
                       ]:
            table.nextColumn(val)
            table.nextColumn(err)
        #end for

        table.nextColumn() # empty

        table.nextColumn()
        atom.rogScore.createHtmlForComments(self.main)
    #end def

    def generateHtml(self, htmlOnly=False):
        """Generate html for atoms listing
        """

        self._resetCingContent()

        self.header('h1', 'Atom List '+ self.atomList.name)
        self.insertHtmlLink( self.header, self.atomList, self.project, text = 'Home' )
        self.insertHtmlLink( self.header, self.atomList, self.project.molecule, text = 'Molecule' )

        atomMain = self.main

#        atomMain('h3', closeTag=False)
        refItem = os.path.join( self.project.moleculePath('analysis'),'validateAssignments.txt')
        abstractResource = NTdict()        # mimic an object
        abstractResource.htmlLocation = ( refItem, HTMLfile.top )
        if os.path.exists(refItem):
            self.insertHtmlLink( self.header, self.atomList, abstractResource, text = 'Text file' )

        # generate the html table template
        table = MakeHtmlTable( self.main,
                               columnFormats = [('atom',      dict(width="150px", valign="top" ) ),
                                                #nb align="char", char="." does not work
                                                ('obs.',      dict(width= "50px", align="right",  valign="top") ),
                                                ('error',     dict(width= "50px", align="right",  valign="top") ),
                                                ('stereo',    dict(width= "75px", align="center", valign="top") ),

                                                ('shiftx',    dict(width= "50px", align="right",  valign="top") ),
                                                ('error',     dict(width= "50px", align="right",  valign="top") ),

                                                ('delta',     dict(width= "50px", align="right",  valign="top") ),
                                                ('error',     dict(width= "50px", align="right",  valign="top") ),

                                                ('dbase',     dict(width= "50px", align="right",  valign="top") ),
                                                ('sd',        dict(width= "50px", align="right",  valign="top") ),

                                                ( None,       dict(width="50px")), # empty

                                                ('Critique',  dict(align="left") )
                                               ],
                            )
        # Make table with only critigued atoms
#        critiqued = []
#        for atom in self.atomList:
#            if atom.rogScore.isCritiqued():
#                critiqued.append(atom)
#        #end for
#        tableSelection = table.rows(critiqued)
#        if len(tableSelection.getRows()):
#            atomMain('h1', 'Critiqued')
#            for atom in tableSelection:
#                self._atomRow( atom, tableSelection )

        atomMain('h1', 'Atoms')
        for res in self.atomList.molecule.allResidues():
            for atom in table.rows(res.allAtoms()):
                if not atom.isSulfur() and not atom.isOxygen():
                    # reference label of atom; insert a dummy character
                    self.main('i', '', id=atom.htmlLocation[1][1:] )
                    # table entry for this atom
                    self._atomRow( atom, table )
                #end if
            #end for
            atomMain(None,'# ')
            atomMain('a', 'goto top of page', href=HTMLfile.top, rel="self")
            atomMain('p')
        #end for

        self.render()
    #end def
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
            except: pass
        self.insertHtmlLink( self.header, restraintList, self.project, text = 'UP' )
        try:
            next = allRestraintLists[index+1]
            self.insertHtmlLink( self.header, restraintList, next, text = next.name )
        except: pass

        # main section html
#        restrMain = self.main
        self.main('h3',closeTag=False)
        for l in restraintList.format().split('\n')[:-1]:
            self.main('br', l )
        self.main('h3',openTag=False)

        if restraintList.__CLASS__ == 'DistanceRestraintList':
            self._generateDistanceRestraintHtml(htmlOnly=htmlOnly)
        elif restraintList.__CLASS__ == 'DihedralRestraintList':
            self._generateDihedralRestraintHtml(htmlOnly=htmlOnly)
        elif restraintList.__CLASS__ == 'RDCRestraintList':
            pass
        else:
            NTerror('RestraintListHTMLfile.generateHtml: invalid restraint list class')
        #end if

        self.render()
    #end def

    def _generateDistanceRestraintHtml(self, htmlOnly):
        """Generate html code for distance restraints
        """
        restrMain = self.main

        for restraint in self.restraintListSorted:
            restrMain('h2', 'Restraint ', id = restraint.htmlLocation[1][1:], closeTag=False)
            # Strangely JFD doesn't know how to get the coloring into the next text
            # without creating a html link. So just put in a self reference.
            self.insertHtmlLink(restrMain,self.restraintList,restraint,'%i'%restraint.id)
            restrMain('h2', openTag=False)

            restrMain('ul', closeTag=False)
            restrMain('li', 'Atoms::', closeTag=False)
            if len(restraint.atomPairs) < 1:
                restrMain('b', 'None')

            for atomPair in restraint.atomPairs:
                res1 = atomPair[0]._parent
                res2 = atomPair[1]._parent
#                    atomName1 = "(%s.%s.%s," % ( chn1.name, res1.name, atomPair[0].name )
                atomName1 = "(" + atomPair[0].toString() +','
                atomName2 =       atomPair[1].toString() +')'

                self.insertHtmlLink( restrMain, self.restraintList, res1, text = atomName1 )
                self.insertHtmlLink( restrMain, self.restraintList, res2, text = atomName2 )
            #end for
            restrMain('li', 'Restraint:: Lower | Upper: %s | %s' % (
                                val2Str(restraint.lower, '%.2f'),
                                val2Str(restraint.upper, '%.2f')))
            restrMain('li', 'Actual:: Av +- Sd | Min | Max:  %s +- %s | %s | %s'
                             % (val2Str(restraint.av,  '%.2f'),
                                val2Str(restraint.sd,  '%.2f'),
                                val2Str(restraint.min, '%.2f'),
                                val2Str(restraint.max, '%.2f')))

            restrMain('li', 'Violations:: Av +- Sd | Max: %s +- %s | %s' %
                    (       val2Str(restraint.violAv,  "%.2f"),
                            val2Str(restraint.violSd,  "%.2f"),
                            val2Str(restraint.violMax, "%.2f") ))

            restrMain('li', 'Counts:: > 0.1 | 0.3 | 0.5 A: %i | %i | %i' %
                             (restraint.violCount1,restraint.violCount3,restraint.violCount5)
                     )

            restraint.rogScore.createHtmlForComments(restrMain)
            #restrMain('li', openTag=False)
            restrMain('ul', openTag=False)
        #end for
    #end def

    def _generateDihedralRestraintHtml(self, htmlOnly):
        """Generate html code for dihedral restraints
        """
        restrMain = self.main
        for restraint in self.restraintListSorted:

            restrMain('h2', '', id = restraint.htmlLocation[1][1:], closeTag=False)
            self.insertHtmlLink( restrMain,self.restraintList,restraint, str(restraint)[1:-1] )
            restrMain('h2', openTag=False)

            restrMain('ul', closeTag=False)
            restrMain( 'li', 'Torsional Angle Atoms:', closeTag=False )
            if len(restraint.atoms) < 1:
                restrMain('b','None')
            ind = 0
            for atom in restraint.atoms:
                res = atom._parent
                atomName = atom.toString() +','
#                    atomName = "%s.%s," % ( res.name, atom.name )
                if ind == 0:
                    atomName = '(' + atomName
                if ind == 3:
                    atomName = atomName[:-1] + ')'
                self.insertHtmlLink( restrMain, self.restraintList, res, text = atomName )
                ind += 1
            #end for
            restrMain('li', openTag=False)
            restrMain('li', 'Lower | Upper: %s | %s' % (
                                val2Str(restraint.lower, '%.2f'),
                                val2Str(restraint.upper, '%.2f')))
            restrMain('li', 'Average (CV):  %s (%s)'
                             % (val2Str(restraint.cav, '%.2f'),
                                val2Str(restraint.cv, '%.2f')))
            restrMain('li', 'ViolCount3: %i' % restraint.violCount3)
            restrMain('li', 'Viol Average | SD | Max: %s | %s | %s' % (
                             val2Str(restraint.violAv,  "%.2f"),
                             val2Str(restraint.violSd,  "%.2f"),
                             val2Str(restraint.violMax, "%.2f") )
                     )

#                 val1, val2, _val3 = restraint.retrieveDefinition()
#                 restraint.residue = val1
#                 restraint.angle = '%s_%i' % (val2, val1.resNum)

#            residue, angleName, _tmp = restraint.retrieveDefinition()
#
#            if residue:
#                restrMain('li', 'Angle name:', closeTag=False)
#                self.insertHtmlLink( restrMain, self.restraintList, residue, text=residue.name + '.' +  angleName)
#                restrMain('li', openTag=False)
#                restraint.rogScore.createHtmlForComments(restrMain)
#            else:
#                restrMain('li', 'Angle atoms:', closeTag=False)
#                for i in restraint.atoms:
#                    self.insertHtmlLink( restrMain, self.restraintList, atom.residue, text=atom.name )
#                restrMain('li', openTag=False)
#                restraint.rogScore.createHtmlForComments(restrMain)
#            #end if
            restrMain('ul', openTag=False)

        #end for
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
            except: pass
        self.insertHtmlLink( self.header, self.peakList, self.project, text = 'UP')
        try:
            next = self.project.peaks[index+1]
            self.insertHtmlLink( self.header, self.peakList, next, text = next.name)
        except: pass

        for peak in self.peakList:
            peakMain = self.main
            peakMain( 'h2', 'Peak %i' % peak.peakIndex, id = peak.htmlLocation[1][1:] )

            peakMain('ul', closeTag=False)
            peakMain('li', 'Positions: %s' % peak.positions.__str__())

            fmt = '%.3e'
            if peak.hasHeight():
                peakMain('li', 'Height: %s (%s)' % ( val2Str(peak.height.value, fmt), val2Str(peak.height.error, fmt)))
            if peak.hasVolume():
                peakMain('li', 'Volume: %s (%s)' % ( val2Str(peak.volume.value, fmt), val2Str(peak.volume.error, fmt)))
            peakMain('li', 'Atoms:', closeTag=False)
            for resonance in peak.resonances:
                if resonance:
                    residue = resonance.atom._parent
                    resonanceAtomName = "%s.%s" % ( residue.name, resonance.atom.name )
                    self.insertHtmlLink( peakMain, self.peakList, residue, text = resonanceAtomName )
                else:
                    peakMain('b', 'None')
                #end if
            #end for
            peakMain('li', openTag=False)
            peakMain('ul', openTag=False)
        #end for
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
        for l in self.project.molecule.rmsd.format().split('\n')[:-1]:
            self.main('br', l )
        self.main('h3',openTag=False)


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
            NTdebug( '>> Number of outliers per model: ' + `outliers`)
            plot.barChart( self.project.models.items(), 0.05, 0.95,
                           attributes = boxAttributes( fillColor='green' )
                         )

            plot.autoScaleYByValueList(outliers, startAtZero=True,
                                       useIntegerTickLabels=True )
            ps.hardcopy( plotFile )
        #end if
        self.main('img', src = 'outliers.'+graphicsOutputFormat)
        self.render()
    #end def
#end class


def removePreTagLines(msg):
    """Removes lines that start with a pre tag"""
    resultList = []
    msgList = msg.split('\n')
    for l in msgList:
        
        if l.startswith(HTML_TAG_PRE) or l.startswith(HTML_TAG_PRE2):
            continue 
        resultList.append(l)
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


# register the functions
methods  = [(setupHtml, None),
            (generateHtml, None),
            (renderHtml, None)
           ]
#saves    = []
#restores = [
#           ]
#exports  = []
