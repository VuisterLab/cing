from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NThistogram
from cing.Libs.NTutils import printError
from pylab import * # preferred importing. Includes nx imports. #@UnusedWildImport
from copy import deepcopy
from cing.Libs.NTutils import NTsort
from matplotlib.collections import LineCollection
from cing.Libs.NTutils import printCodeError

# NOTE WELL: use only 1 NTplot instance at a time.
haveBiggles = False
try:
    import biggles
    haveBiggles = True
except ImportError:
    printError("Failed to import biggles; please check installation")
    
#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Plotting attributes
#-----------------------------------------------------------------------------

def NTplotAttributes( **kwds ):
    a = NTdict()

    a.__FORMAT__ =    '=== plotting attributes ===\n' +\
                      'lineType:   %(lineType)s\n' +\
                      'lineWidth:  %(lineWidth).1f\n' +\
                      'lineColor:  %(lineColor)s\n' +\
                      'fill:       %(fill)s\n' +\
                      'line:       %(line)s\n' +\
                      'fillColor:  %(fillColor)s\n' +\
                      'pointType:  %(pointType)s\n' +\
                      'pointSize:  %(pointSize).1f\n' +\
                      'pointColor: %(pointColor)s\n' +\
                      'font:       %(font)s\n' +\
                      'fontSize:   %(fontSize)d\n' +\
                      'fontColor:  %(fontColor)s\n' +\
                      'textAlign:  %(textAlign)s\n'

    # line defaults
    a.lineType   = 'solid'
    a.lineColor  = 'black'
    a.lineWidth  = 1.0

    # box
    a.fill       = True
    a.fillColor  = 'black'
    a.line       = False

    # points
    a.pointType  = None # Changed to have no point as this is more common for all.
    a.pointSize  = 2.0
    a.pointColor = 'blue'

    # fonts
    a.font       = 'Helvetica'
    a.fontSize   = 12
    a.fontColor  = 'black'

    # text
    a.textAlign  = 'left'
    
    a.alpha = 1. # Takes a value in range [0,1] for transparency/blending.

    # update
    a.update( kwds )

    return a
#end def

def lineAttributes( type='solid', width=1.0, color='black', alpha=1. ):
    return NTplotAttributes( lineType=type, lineWidth=width, lineColor=color, alpha=alpha )
#end def

def boxAttributes( fill=True, fillColor='black', line=False, lineColor='black', alpha=1. ):
    return NTplotAttributes( lineType='solid', lineColor=lineColor, line=line,
                             fill=fill, fillColor=fillColor, alpha=alpha
                           )
#end def

def fontAttributes( font='Helvetica', size=12, color='black', alpha=1. ):
    return NTplotAttributes( font=font, fontSize=size, fontColor=color, alpha=alpha )
#end def

def pointAttributes( type='circle', size=2.0, color='black', alpha=1. ):
    return NTplotAttributes( pointType=type, pointSize=size, pointColor=color, alpha=alpha )
#end def

# Some default attributes
defaultAttributes  = NTplotAttributes()

solidLine          = lineAttributes( type='solid',      width=1.0, color='black' )
dottedLine         = lineAttributes( type='dotted',     width=1.0, color='black' )
dashedline         = lineAttributes( type='longdashed', width=1.0, color='black' )
redLine            = lineAttributes( type='solid',      width=1.0, color='red' )
blueLine           = lineAttributes( type='solid',      width=1.0, color='blue' )
greenLine          = lineAttributes( type='solid',      width=1.0, color='green' )

blackBox           = boxAttributes( fill=True,  fillColor='black' )
redBox             = boxAttributes( fill=True,  fillColor='red' )
greenBox           = boxAttributes( fill=True,  fillColor='green' )
openBox            = boxAttributes( fill=False, fillColor='black', line=True, lineColor='black' )

plusPoint          = pointAttributes( type='plus',          size=2.0, color='blue' )
circlePoint        = pointAttributes( type='circle',        size=2.0, color='blue' )

#Biggles symbol types:
#        "none"                : 0,
#        "dot"                : 1,
#        "plus"                : 2,
#        "asterisk"            : 3, 
#        "circle"            : 4,
#        "cross"                : 5,
#        "square"            : 6,
#        "triangle"            : 7,
#        "diamond"            : 8,
#        "star"                : 9, 
#        "inverted triangle"        : 10, 
#        "starburst"            : 11,
#        "fancy plus"            : 12,
#        "fancy cross"            : 13, 
#        "fancy square"            : 14, 
#        "fancy diamond"            : 15,
#        "filled circle"            : 16,
#        "filled square"            : 17,
#        "filled triangle"        : 18, 
#        "filled diamond"        : 19,
#        "filled inverted triangle"    : 20,
#        "filled fancy square"        : 21,
#        "filled fancy diamond"        : 22,
#        "half filled circle"        : 23,
#        "half filled square"        : 24,
#        "half filled triangle"        : 25,
#        "half filled diamond"        : 26,
#        "half filled inverted triangle" : 27,
#        "half filled fancy square"    : 28,
#        "half filled fancy diamond"    : 29,
#        "octagon"            : 30,
#        "filled octagon"        : 31,
mappingPointType2MatLibPlot = { 
    'none': 'None', 
    'plus': '+', 
    'circle': 'o', 
    'filled circle': 'o',
     }
"""          linestyle or ls: [ '-' | '--' | '-.' | ':' | 'steps' | 'None' | ' ' | '' ] """
mappingLineType2MatLibPlot = { 'solid': None, 'dotted': ':', 'longdashed': '--'}

dpi=72.27 # Latex definition
inches_per_pt = 1.0/dpi
golden_mean = (sqrt(5.)-1.0)/2.0     # Aesthetic ratio where possible.

#-----------------------------------------------------------------------------
# Color conversions
# These functions, when given a magnitude mag between cmin and cmax, return
# a colour tuple (red, green, blue). Light blue is cold (low magnitude)
# and yellow is hot (high magnitude).
#
# GV: Adapted from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52273
#
#-----------------------------------------------------------------------------

def floatRgb(mag, cmin, cmax):
        """
        Return a tuple of floats between 0 and 1 for the red, green and
        blue amplitudes.
        """
        mag  = float(mag)
        cmin = float(cmin)
        cmax = float(cmax)
        try:
            # normalize to [0,1]
            x = float(mag-cmin)/float(cmax-cmin)
        except:
            # cmax = cmin
            x = 0.5
        blue = min((max((4*(0.75-x), 0.)), 1.))
        red  = min((max((4*(x-0.25), 0.)), 1.))
        green= min((max((4*math.fabs(x-0.5)-1., 0.)), 1.))
        return (red, green, blue)

def strRgb(mag, cmin, cmax):
        """
        Return a tuple of strings to be used in Tk plots.
        """

        red, green, blue = floatRgb(mag, cmin, cmax)
        return "#%02x%02x%02x" % (red*255, green*255, blue*255)

def rgb(mag, cmin, cmax):
        """
        Return a tuple of integers to be used in AWT/Java plots.
        """

        red, green, blue = floatRgb(mag, cmin, cmax)
        return (int(red*255), int(green*255), int(blue*255))

def htmlRgb(mag, cmin, cmax):
        """
        Return a tuple of strings to be used in HTML documents.
        """
        return "#%02x%02x%02x"%rgb(mag, cmin, cmax)


class NTplot( NTdict ):
    """
    Base plotting class
    """
    
    def __init__( self, **kwds ):
        NTdict.__init__( self )
        self.__CLASS__    = 'NTplot'
        self.useMatPlotLib= True # Wherever possible transition away from Biggles.

        self.hardcopySize = (400,400)
        self.font         = 'Helvetica'
        self.graphicsOutputFormat = 'png'
        
        self.title        = None
        self.xLabel       = None
        self.yLabel       = None

        self.aspectRatio  = 1.0    # Aspect ratio
        self.xRange       = None   # x-axis (min,max) tuple, None is autoscale
        self.yRange       = None   # y-axis (min,max) tuple, None is autoscale

        self.xTicks       = None   # x-axis tics-list, None is autotics
        self.yTicks       = None   # y-axis tics-list, None is autotics
        self.xmTicks       = None  
        self.ymTicks       = None   

        self.xAxis        = True
        self.yAxis        = True

        self.xGrid        = True   # x-axis grid toggle
        self.yGrid        = True   # y-axis grid toggle

        self.update( kwds )

        if self.useMatPlotLib:
            fig_width_pt  = self.hardcopySize[0]
            if self.hardcopySize[1]:
                fig_height_pt = self.hardcopySize[1]
            else:
                fig_height_pt = int(fig_width_pt*golden_mean)  
#            fig_size_pt   = [fig_width_pt,fig_height_pt]
#            print fig_size_pt
            fig_width     = fig_width_pt*inches_per_pt  # width in inches
            fig_height    = fig_height_pt*inches_per_pt # height in inches
            fig_size      = [fig_width,fig_height]
            
#            printDebug("Getting hardcopySize: "+`self.hardcopySize`)
#            printDebug("Setting sizeInches:   "+`fig_size`)

            params = {'backend':          self.graphicsOutputFormat, 
                      'figure.dpi':       dpi, 
                      'figure.figsize':   fig_size, 
                      'savefig.dpi':      dpi,
                      'savefig.figsize':  fig_size,
                       }
            rcParams.update(params)
            
            close() # Close any left over figures to start a new one.
            self.figure = Figure( frameon=False, 
                                  dpi=dpi,
                                  figsize=fig_size,
                                  facecolor='white',
                                  edgecolor='white',
                                   )
            
        else:
            if not haveBiggles:
                NTerror("NTplot.__init__: No biggles\n")
            else:
                #initialise the biggles plot
                biggles.configure('persistent','no')
                self.b = biggles.FramedPlot()
                self.move( (0.0, 0.0) )
        #endif
    #end def

    def move( self, point ):
        self.currentPoint = point
    #end def

    def draw( self, endPoint, attributes=defaultAttributes ):
        if not attributes:
            attributes=defaultAttributes
        xdata=(self.currentPoint[0], endPoint[0])
        ydata=(self.currentPoint[1], endPoint[1])
#        printDebug("xdata: " + `xdata`)
#        printDebug("ydata: " + `ydata`)
        if self.useMatPlotLib:
            ax = gca()
            line2D = Line2D(xdata, ydata)
            attributesMatLibPlot = self.mapAttributes2MatLibPlotLine2D(attributes)
            self.setMatLibPlotLine2DPropsPoint(line2D, attributesMatLibPlot)
            ax.add_artist(line2D)
        else:
            self.b.add(
                biggles.Curve( xdata, ydata,
                               linetype  = attributes.lineType,
                               linewidth = attributes.lineWidth,
                               linecolor = attributes.lineColor
                             )
            )
        self.currentPoint = endPoint
    #end def

    def line( self, startPoint, endPoint, attributes=defaultAttributes):
        if not attributes:
            attributes=defaultAttributes
        self.move( startPoint )
        self.draw( endPoint=endPoint, attributes=attributes )
    #end def

    def lines( self, points, attributes=None ):
        if not attributes:
            attributes=defaultAttributes
        if len(points) == 0: 
            return
        self.move( points[0] )
        for p in points[1:]:
            self.draw( endPoint=p, attributes=attributes )
        #end for
    #end def

    def box( self, point, sizes, attributes=None ):
        if not attributes:
            attributes=defaultAttributes
        
        if self.useMatPlotLib:
            attributesMatLibPlot = self.mapAttributes2MatLibPatches(attributes)            
            ax = gca()
            rectangle = Rectangle(point, 
                width=sizes[0], 
                height=sizes[1],
                **attributesMatLibPlot )            
            ax.add_artist(rectangle)
        else:
            self.move(  point )
            # clockwise
            #  p2---p3
            #   |   |
            #  p1---p4
            p1 = point
            p2 = (point[0],          point[1]+sizes[1])
            p3 = (point[0]+sizes[0], point[1]+sizes[1])
            p4 = (point[0]+sizes[0], point[1])
    
    #        self.closedObject( [p1,p2,p3,p4], attributes )
            if attributes.fill:
                self.b.add(
                    biggles.FillBetween( [p1[0], p2[0], p3[0]],
                                         [p1[1], p2[1], p3[1]],
                                         [p1[0], p4[0], p3[0]],
                                         [p1[1], p4[1], p3[1]],
                                         fillcolor = attributes.fillColor
                                       )
                )
            #end if
            if attributes.line:
                self.draw( p2, attributes )
                self.draw( p3, attributes )
                self.draw( p4, attributes )
                self.draw( p1, attributes )
            #end if
        #end def

    def mapAttributes2MatLibPlotLine2D(self, attributes=defaultAttributes):
        if not attributes:
            attributes=defaultAttributes
        result = NTdict()
        result.color  = None
        result.marker = 'None'
#            'linewidth'      : None, # all Nones default to rc
#            'linestyle'      : None,
#            'color'          : None,
#            'marker'         : None,
#            'markersize'     : None,
#            'markeredgewidth': None,
#            'markeredgecolor': None,
#            'markerfacecolor': None,
#            'antialiased'    : None,
#            'dash_capstyle'  : None,
#            'solid_capstyle' : None,
#            'dash_joinstyle' : None,
#            'solid_joinstyle': None,
#        }        
        keys = attributes.keys()
        # input:
#        ['fill', 'fillColor', 'font', 'fontColor', 'fontSize', 'line', 'lineColor', 'lineType', 'lineWidth', 
#         'pointColor', 'pointSize', 'pointType', 'textAlign']
        
#        printDebug("attributes: " + attributes.format())
        if 'pointType' in keys:
            if attributes.pointType:                    
                if mappingPointType2MatLibPlot.has_key(attributes.pointType):
#                    print "doing pointType"
                    result.marker =  mappingPointType2MatLibPlot[attributes.pointType]
                else:
                    printCodeError("Failed to map point type ["+`attributes.pointType`+"]to mat lib plot's marker id)")
                    return True
        if 'pointColor' in keys:
#            print "doing pointColor"
            result.markeredgecolor =  attributes.pointColor
            result.markerfacecolor =  attributes.pointColor
            result.color           =  attributes.pointColor
        if 'lineColor' in keys:
#            print "doing lineColor"
            result.color           =  attributes.lineColor
        if 'color' in keys:
#            print "doing color"
            result.color           =  attributes.color
        if 'fill' in keys:
#            print "doing fill"
            markerColor = result.color
            if 'pointColor' in keys:
                markerColor = attributes.pointColor
            elif 'lineColor' in keys:
                markerColor = attributes.lineColor
            result.markeredgecolor =  markerColor
            result.markerfacecolor =  markerColor
        if 'alpha' in keys:
#            print "doing alpha"
            result.alpha           =  attributes.alpha
#        printDebug("result attributes: " + `result`)
        return result

    def mapAttributes2MatLibPatches(self, attributes=defaultAttributes):
        if not attributes:
            attributes=defaultAttributes
        result = {}
        # Patch attributes.
#                 edgecolor=None,
#                 facecolor=None,
#                 linewidth=None,
#                 antialiased = None,
#                 hatch = None,
#                 fill=1,
        # Input
#                facecolor=attributes.fillColor,
#                edgecolor=attributes.lineColor,
#                fill=attributes.fill,
        
        keys = attributes.keys()
        if 'alpha' in keys:
            result['alpha']                =  attributes.alpha
        if 'fill' in keys:
            result['fill']                =  attributes.fill
        if 'fillColor' in keys:
            result['facecolor']           =  attributes.fillColor
        if 'lineColor' in keys:
            result['edgecolor']           =  attributes.lineColor
#        printDebug("input  mapAttributes2MatLibPatches: " + `attributes`)
#        printDebug("result mapAttributes2MatLibPatches: " + `result`)
        return result


    def setMatLibPlotLine2DPropsPoint( self,line2D, attributesMatLibPlot):
        line2D.set_color(attributesMatLibPlot['color'])
        if isinstance(line2D,LineCollection): # Limited set of possibilities.
            return
        if attributesMatLibPlot.has_key('marker'):
            if attributesMatLibPlot.marker == 'None':
                return
            line2D.set_marker(attributesMatLibPlot['marker'])
            line2D.set_markeredgecolor(attributesMatLibPlot['markeredgecolor'])
            line2D.set_markerfacecolor(attributesMatLibPlot['markerfacecolor'])

    def removeMarkerAttributes( self, attributesMatLibPlot):
        del(attributesMatLibPlot['marker'])
        del(attributesMatLibPlot['markeredgecolor'])
        del(attributesMatLibPlot['markerfacecolor'])
            
    def setMatLibPlotLine2DListPropsPoint( self, line2DList, attributesMatLibPlot):
        for line2D in line2DList:
            self.setMatLibPlotLine2DPropsPoint( line2D, attributesMatLibPlot)

    def point( self, point, attributes=defaultAttributes ):
        """
            Add a point
            add xErrorBar if len(points)>2
            add yErrorBar if len(points)>3
        """
        if not attributes:
            attributes=defaultAttributes
        if attributes.has_key('pointType'):
            if not attributes.pointType:
                attributes.pointType= 'none' # Changed to have no point as this is more common for all.
        
        if self.useMatPlotLib:
            attributesMatLibPlot = self.mapAttributes2MatLibPlotLine2D(attributes)
#            print attributesMatLibPlot['marker']
            x = point[0]
            y = point[1]            
            line2D, = plot( [x], [y] )
            self.setMatLibPlotLine2DPropsPoint( line2D, attributesMatLibPlot)
            xerror=None
            yerror=None
            if len(point) >2:
                xerror=point[2]
                if len(point) >3:
                    yerror=point[3]
#            (l0, caplines, barcols) = errorbar([x], [y], xerr=xerror, yerr=yerror, ecolor=attributesMatLibPlot['color'])
            errorbar([x], [y], xerr=xerror, yerr=yerror, ecolor=attributesMatLibPlot['color'])
#            line2Dlist = NTlist() # Allow appending of lists.
#            line2Dlist.append(l0)
#            line2Dlist.addList(caplines)
#            line2Dlist.addList(barcols)
#            attributesMatLibPlotNoMarker = self.removeMarkerAttributes(attributesMatLibPlot)
#            self.setMatLibPlotLine2DListPropsPoint( line2Dlist, attributesMatLibPlotNoMarker)
        else:            
            self.move(  (point[0],point[1]) )
            self.b.add(
               biggles.Point( point[0], point[1],
                              symboltype = attributes.pointType,
                              symbolsize = attributes.pointSize,
                              color      = attributes.pointColor
                            )
            )
            if (len(point) > 2 and point[2] >= 0.0):
                self.b.add(
                    biggles.SymmetricErrorBarsX( [point[0]], [point[1]], [point[2]],
                                                 color = attributes.pointColor
                                               )
                )
            #end if
            if (len(point) > 3 and point[3] >= 0.0):
                self.b.add(
                   biggles.SymmetricErrorBarsY( [point[0]], [point[1]], [point[3]],
                                                 color = attributes.pointColor
                                              )
                )
            #end if
    #end def

    def points( self, points, attributes=defaultAttributes ):
        if not attributes:
            attributes=defaultAttributes
        if len(points) == 0: 
            return
        for p in points:
            self.point( p, attributes )
        #end for
    #end def

    def label( self, point, text, attributes=defaultAttributes ):
        if not attributes:
            attributes=defaultAttributes
        if self.useMatPlotLib:
            xy=(point[0], point[1])
            annotate(text,                                
                        xy=xy,                       # in data coordinate system; assuming only one occurrence.
                        xytext=xy,    
                        xycoords='data', # default: use the axes data coordinate system
                        textcoords='data', 
                        horizontalalignment=attributes.textAlign,
#                        verticalalignment='bottom',
                        )            
        else:
            self.b.add(
                biggles.DataLabel( point[0], point[1], text,
                                   fontface = attributes.font,
                                   fontsize = float(attributes.fontSize)/4.0,
                                   texthalign = attributes.textAlign,
                                   color = attributes.fontColor
                                 )
            )
    #end def

    def labeledPoint( self, point, text, attributes=defaultAttributes ):
        if not attributes:
            attributes=defaultAttributes
        self.point( point, attributes )
        self.label( point, text, attributes )
    #end def

    def autoScale( self, x=True, y=True ):
        if x: 
            self.xRange = None
        if y: 
            self.yRange = None
    #end def

    def updateSettings( self ):
        if self.useMatPlotLib:
            if self.title:
                title( self.title )
            if self.xLabel:
                xlabel(self.xLabel)
            if self.yLabel:
                ylabel(self.yLabel)

            if self.xTicks:
                xticks(self.xTicks)# A list with actual values like 0,60,120...
            if self.yTicks:
                yticks(self.yTicks)# A list with actual values like 0,60,120...
            
            if self.xRange:
                xlim(self.xRange)
            if self.yRange:
                ylim(self.yRange)
            if self.xGrid:
                grid(True)
            else:
                grid(False)
#            biggles.configure('fontface', self.font)
            
        else:
            #update settings
            self.b.title         = self.title
            self.b.xlabel        = self.xLabel
            self.b.ylabel        = self.yLabel
    
            self.b.x.draw_axis   = self.xAxis
            self.b.y.draw_axis   = self.yAxis
            self.b.x2.draw_ticks = 0
            self.b.y2.draw_ticks = 0
            self.b.x.tickdir     = 1
            self.b.y.tickdir     = 1
    
            self.b.x.ticks       = self.xTicks
            self.b.y.ticks       = self.yTicks
    
            self.b.aspect_ratio  = self.aspectRatio
            self.b.xrange        = self.xRange
            self.b.yrange        = self.yRange
    
            self.b.x.draw_grid   = self.xGrid
            self.b.y.draw_grid   = self.yGrid
    
            biggles.configure('width',    self.hardcopySize[0] )
            biggles.configure('height',   self.hardcopySize[1] )
            biggles.configure('fontface', self.font)

    #end def

    def show( self ):
        self.updateSettings()
        if self.useMatPlotLib:
            show()
        else:
            self.b.show()

    def close( self ):
        "Attempts to close a window but fails so far. TODO: fix."
        if self.useMatPlotLib:
            close('all')
#        else:
#            self.b.close() #?

    def hardcopy( self, fileName, graphicsFormat = 'png' ):
        self.updateSettings()
        if self.useMatPlotLib:
            savefig(fileName, format=graphicsFormat)
        else:       
            self.b.write_img( graphicsFormat, self.hardcopySize[0], self.hardcopySize[1], fileName )
    #end def


    def histogram( self, theList, low, high, bins, leftMargin=0.05, rightMargin=0.05, attributes=defaultAttributes, valueIndexPairList=None ):
        if not attributes:
            attributes=defaultAttributes
#        printDebug("Creating number of bins: " + `bins`)
#        printDebug("theList: " + `theList`)
        if not theList:
#            printDebug("empty input not adding histogram")
            return # Nothing to add.
        his = NThistogram( theList, low, high, bins ) # A NTlist
        self.maxY = max(his)
        if self.useMatPlotLib:
            step = (high-low)/bins            
            ind = arange(low,high,step)  # the x locations for the groups
#            printDebug("Creating x coor for bins: " + `ind`)
            gcf() # should not be needed.
            bar(ind, his, step, 
                color    =attributes.fillColor,
                edgecolor=attributes.fillColor)
            ax = gca()

            if valueIndexPairList: # Were dealing with outliers.                
#                printDebug("Annotating the outliers with a arrow and string")
                tmpValueIndexPairList = deepcopy(valueIndexPairList)
                tmpValueIndexPairList = NTsort(tmpValueIndexPairList, 1)
                
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                _ylim_min, ylim_max = ylim
#                printDebug("xlim: " + `xlim`)
#                printDebug("ylim: " + `ylim`)
                outlierLocHeight = ylim_max # In data coordinate system
                outlierLocHeightMin = ylim_max*.1 # In data coordinate system
#                printDebug("tmpValueIndexPairList: " + `tmpValueIndexPairList`)
                for item in tmpValueIndexPairList:                    
                    value = item[1]
                    modelNum = item[0] + 1
                    if not value: # Don't annotate zero values.
                        continue
                    outlierLocHeight -= 0.1*ylim_max # Cascade from top left to bottom right.
                    if outlierLocHeight < outlierLocHeightMin:
                        outlierLocHeight = outlierLocHeightMin
#                    printDebug("Setting data point to: " + `value` +", 1")
#                    printDebug("Setting text point to: " + `value` +", "+ `outlierLocHeight`)
                    ax.plot([value], [1], 'o',color=attributes.fillColor,markeredgecolor=attributes.fillColor,markersize=3)
                    ax.annotate("model "+`modelNum`,                                
#                                xy=(0.05, 1),                       # in data coordinate system; assuming only one occurrence.
                                xy=(value+0.01, 1),                       # in data coordinate system; assuming only one occurrence.
                                xytext=(value, outlierLocHeight),    
                                xycoords='data', # default: use the axes data coordinate system
                                textcoords='data', 
                                arrowprops=dict(facecolor=attributes.fillColor,
                                                edgecolor=attributes.fillColor, 
                                                shrink=0.05,
                                                width=1, # Width of arrow
                                                headwidth=4
                                                ),
                                horizontalalignment='left',
                                verticalalignment='bottom',
                                )
                # Do at the end because the plot command resets the boundaries?
                ax.set_ylim(ymax = ylim_max+1) # get some clearance at the top
            
        else:
            for bin in range( bins ):
                if his[bin] > 0:
                    self.box( point = ( his.low+(bin+leftMargin)*his.binSize, 0.0 ),
                              sizes = ( his.binSize*(1.0-(leftMargin+rightMargin)), float(his[bin]) ),
                              attributes = attributes
                            )
            #end if
        #end for
    #end def

    def barChart( self, barList, leftMargin=-0.5, rightMargin=0.5, attributes=defaultAttributes ):
        """
        Plot a bars at x-leftMargin to x+rightMargin, y height

        barList: list of (x, y) tuples
        """
        if not attributes:
            attributes=defaultAttributes

        for x,y in barList:
#            if y != 0.0: # JFD: Why inserted? It causes biggles to complain when nothing gets added.
                self.box( point = ( x+leftMargin, 0.0 ),
                          sizes = ( rightMargin-leftMargin, float(y) ),
                          attributes = attributes
                        )
            #end if
        #end for
    #end def
    
    def get_ylim(self):
        if self.useMatPlotLib:
            ax = gca()
            ylim = ax.get_ylim()
            return ylim
        else:
            return None
        
    def get_ticklines(self):
        'Return the ticklines lines as a list of Line2D instance; overcoming a lack of "feature" in api'
        figure=gcf()
        ax=figure.get_axes()[0]
#        print ax
        lines = []
        xaxis = ax.get_xaxis()
        yaxis = ax.get_yaxis()
        axisLIst = [ xaxis, yaxis ]
        for axis in axisLIst:
            for tick in axis.majorTicks:
                lines.append(tick.tick1line)
                lines.append(tick.tick2line)
            for tick in axis.minorTicks:
                lines.append(tick.tick1line)
                lines.append(tick.tick2line)
        return silent_list('Line2D ticklines', lines)
    
    def setTickLineWidth(self, size=1):
        tlList = self.get_ticklines()
        for tl in tlList:
            tl.set_markeredgewidth(size) # Unreported feature.
    
    def setMinorTicks(self, space):
        ax=gca()
        minorLocator   = MultipleLocator(space)
        ax.xaxis.set_minor_locator(minorLocator)
        self.setTickLineWidth()
    
#end class

